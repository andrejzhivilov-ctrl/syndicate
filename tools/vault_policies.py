#!/usr/bin/env python3
"""Generate the Vault ACL policies from ``src/vault_paths.py``.

Why this exists
---------------
The policies used to be heredocs inside ``deploy/scripts/vault_init.sh``. Two
problems followed: they drifted from the paths the code actually reads, and the
runtime policy was a wildcard (``secret/data/eva-syndicate/*``) that granted
every secret to one token — including other agents' provider keys and anything
added later.

Now the grants are derived from one source of truth (``src/vault_paths.py``) and
written to ``config/vault/policies/``. ``deploy/scripts/vault_init.sh`` only
uploads files; it no longer invents policy text.

Usage::

    python tools/vault_policies.py --write   # regenerate the files
    python tools/vault_policies.py --check   # fail if files drift (CI gate)

Exit codes: 0 ok, 1 drift/coverage failure.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src import vault_paths  # noqa: E402

POLICY_DIR = REPO_ROOT / "config" / "vault" / "policies"

#: Capabilities every agent token needs to keep itself alive.
TOKEN_SELF_PATHS: Tuple[Tuple[str, str], ...] = (
    ("auth/token/renew-self", "update"),
    ("auth/token/lookup-self", "read"),
)

HEADER = """# GENERATED FILE — do not edit by hand.
# Regenerate with: python tools/vault_policies.py --write
# Source of truth: src/vault_paths.py
#
# {title}
"""


def _policy_text(title: str, paths: List[Tuple[str, str]]) -> str:
    """Render one policy. Metadata paths get ``list,read`` in a single block."""
    merged: Dict[str, List[str]] = {}
    for path, capabilities in paths:
        caps = [c.strip() for c in capabilities.strip("[]").split(",") if c.strip()]
        if "/metadata/" in path and "list" not in caps:
            caps = ["list"] + caps
        merged[path] = sorted(set(merged.get(path, []) + caps))

    lines = [HEADER.format(title=title).rstrip("\n"), ""]
    for path, caps in merged.items():
        rendered = ", ".join(f'"{c}"' for c in caps)
        lines.append(f'path "{path}" {{')
        lines.append(f"  capabilities = [{rendered}]")
        lines.append("}")
        lines.append("")
    # Exactly one trailing newline.
    return "\n".join(lines).rstrip("\n") + "\n"


#: The runtime container (server + orchestrator). Named ``eva-agent`` because
#: that is the service ``docker-compose.yml`` and ``.env.example`` already
#: refer to; Eva's orchestrator *is* the server process, so she has no separate
#: per-agent policy.
RUNTIME_POLICY_NAME = "eva-agent"


def runtime_policy() -> Tuple[str, str]:
    """The container that runs today: every floor in one process."""
    title = (
        "Runtime policy (server + all floors in one container).\n"
        "# Holds exactly the secrets the running code reads — see\n"
        "# vault_paths.INFRA_SERVICES / CONNECTOR_SERVICES / VOICE_SERVICES.\n"
        "# Replace with the per-agent policies once each floor gets its own\n"
        "# container: this token can read every floor's secrets by design."
    )
    paths = [(p, '["read"]') for p in vault_paths.policy_paths()]
    paths += [(p, '["list", "read"]') for p in vault_paths.policy_paths() if "/metadata/" in p]
    paths += list(TOKEN_SELF_PATHS)
    return RUNTIME_POLICY_NAME, _policy_text(title, paths)


def agent_policy(agent_id: str) -> Tuple[str, str]:
    """One agent's own policy (used when floors get their own containers)."""
    services = vault_paths.AGENT_SERVICES.get(agent_id, ())
    title = (
        f"Agent policy: {agent_id}.\n"
        f"# Infrastructure: {', '.join(vault_paths.INFRA_SERVICES)}.\n"
        f"# Own subtree: {vault_paths.agent_secret_path(agent_id, '<name>')}.\n"
        f"# Extra services: {', '.join(services) if services else 'none (default deny)'}.\n"
        "# Cannot read other agents' subtrees or the server's own API key."
    )
    paths = [(p, '["read"]') for p in vault_paths.agent_policy_paths(agent_id)]
    paths += [(p, '["list", "read"]') for p in vault_paths.agent_policy_paths(agent_id) if "/metadata/" in p]
    paths += list(TOKEN_SELF_PATHS)
    return f"eva-{agent_id}", _policy_text(title, paths)


def container_agents() -> Tuple[str, ...]:
    """Agents that will get their own container (all of them except Eva)."""
    return tuple(a for a in vault_paths.AGENTS_IDS if a != "eva")


def build_policies() -> Dict[str, str]:
    """Return ``{policy_name: hcl_text}`` for every policy the deployment needs."""
    policies = dict([runtime_policy()])
    for agent_id in container_agents():
        name, text = agent_policy(agent_id)
        policies[name] = text
    return policies


# ── verification ────────────────────────────────────────────────────────────
#: Literal reads of the form ``secret_path("telegram")``.
_LITERAL_READ = re.compile(r'secret_path\(\s*"([\w./-]+)"')
#: ``agent_secret_path("sam", ...)`` — reported as the ``agents/sam`` subtree.
_AGENT_READ = re.compile(r'agent_secret_path\(\s*"([\w-]+)"')
#: ``BaseConnector.SERVICE_NAME = "telegram"`` — read via ``self.SERVICE_NAME``.
_SERVICE_NAME = re.compile(r'^\s*SERVICE_NAME(?::\s*str)?\s*=\s*"([\w-]+)"')
#: ``read_vault_secret(self._vault, "elevenlabs", ...)`` — voice providers.
_VOICE_READ = re.compile(r'read_vault_secret\(\s*self\._vault\s*,\s*"([\w-]+)"')


def services_in_code() -> Dict[str, List[str]]:
    """Every Vault service the code reads, with locations.

    Three shapes have to be covered, or the check gives false confidence:
    literal ``secret_path("x")``, connectors (`SERVICE_NAME = "x"`, read via
    ``self.SERVICE_NAME``) and voice providers (``read_vault_secret(..., "x")``).
    """
    # Skip the module that only *defines* the helpers: its docstring contains
    # example calls (`agent_secret_path("sam", "broker")`) that are not reads.
    skip = {REPO_ROOT / "src" / "vault_paths.py", Path(__file__).resolve()}
    found: Dict[str, List[str]] = {}
    for base in ("src", "deploy", "tools"):
        for path in (REPO_ROOT / base).rglob("*.py"):
            if path.resolve() in skip:
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                where = f"{path.relative_to(REPO_ROOT)}:{lineno}"
                for match in _LITERAL_READ.finditer(line):
                    found.setdefault(match.group(1), []).append(where)
                for match in _AGENT_READ.finditer(line):
                    found.setdefault(f"{vault_paths.AGENTS}/{match.group(1)}", []).append(where)
                for match in _SERVICE_NAME.finditer(line):
                    if match.group(1) != "base":  # the abstract connector itself
                        found.setdefault(match.group(1), []).append(where)
                for match in _VOICE_READ.finditer(line):
                    found.setdefault(match.group(1), []).append(where)
    return found


def declared_vs_discovered() -> List[str]:
    """Services the code uses that the curated lists in vault_paths miss."""
    discovered = set(services_in_code())
    declared = set(vault_paths.INFRA_SERVICES) | set(vault_paths.CONNECTOR_SERVICES)
    declared |= set(vault_paths.VOICE_SERVICES) | {vault_paths.AUTH}
    declared |= {s for s in discovered if s.startswith(f"{vault_paths.AGENTS}/")}
    return sorted(discovered - declared)


def coverage_gaps(runtime_hcl: str) -> Dict[str, List[str]]:
    """Services the code reads but the runtime policy does not grant."""
    gaps: Dict[str, List[str]] = {}
    for service, locations in services_in_code().items():
        if service.startswith(f"{vault_paths.AGENTS}/"):
            # Whole agent subtree is granted by the agents/* glob.
            needed = [f"{vault_paths.MOUNT}/data/{vault_paths.PREFIX}/{vault_paths.AGENTS}/*"]
        else:
            needed = vault_paths.policy_paths_for_service(service)
        missing = [p for p in needed if f'path "{p}"' not in runtime_hcl]
        if missing:
            gaps[service] = locations
    return gaps


def wildcard_grants(hcl: str) -> List[str]:
    """Any grant that would cover the whole secret store or a whole prefix."""
    offenders = []
    for line in hcl.splitlines():
        if not line.startswith('path "'):
            continue
        target = line.split('"')[1]
        # A trailing ``*`` directly after the prefix (i.e. ``<prefix>/*``)
        # hands over everything: services, agents, future secrets alike.
        if target.rstrip("*").rstrip("/").endswith(vault_paths.PREFIX):
            offenders.append(target)
    return offenders


def _filesystem_failures(policies: Dict[str, str]) -> List[str]:
    """Policy files that are missing, stale, or no longer generated."""
    failures: List[str] = []
    for name, text in sorted(policies.items()):
        path = POLICY_DIR / f"{name}.hcl"
        if not path.exists():
            failures.append(f"missing policy file: {path.relative_to(REPO_ROOT)}")
        elif path.read_text(encoding="utf-8") != text:
            failures.append(f"policy out of date: {path.relative_to(REPO_ROOT)} (run --write)")
    stale = sorted({p.stem for p in POLICY_DIR.glob("*.hcl")} - set(policies))
    if stale:
        failures.append(f"policy files with no generator: {stale}")
    return failures


def _coverage_failures(policies: Dict[str, str]) -> List[str]:
    """Services read by the code but not declared, or not granted."""
    failures: List[str] = []
    for service in declared_vs_discovered():
        failures.append(
            f"code reads '{service}' but src/vault_paths.py does not declare it "
            "(add it to CONNECTOR_SERVICES/VOICE_SERVICES or the per-agent map)"
        )
    for service, locations in sorted(coverage_gaps(policies[RUNTIME_POLICY_NAME]).items()):
        failures.append(f"runtime policy does not grant '{service}' read by {', '.join(locations)}")
    return failures


def _privilege_failures(policies: Dict[str, str]) -> List[str]:
    """Wildcards and cross-agent reads — the two ways least privilege breaks."""
    failures: List[str] = []
    for name, text in policies.items():
        for target in wildcard_grants(text):
            failures.append(f"policy {name} grants a whole-prefix wildcard: {target}")

    for agent_id in container_agents():
        agent_hcl = policies[f"eva-{agent_id}"]
        for other in vault_paths.AGENTS_IDS:
            if other != agent_id and f"{vault_paths.AGENTS}/{other}/" in agent_hcl:
                failures.append(f"policy eva-{agent_id} can read {other}'s subtree")
        # The server's own API key is not an agent secret.
        if f'path "{vault_paths.secret_path(vault_paths.AUTH)}"' in agent_hcl:
            failures.append(f"policy eva-{agent_id} can read the server auth secret")
    return failures


def check() -> int:
    """Return a shell exit code; prints a human-readable report."""
    policies = build_policies()
    failures = _filesystem_failures(policies) + _coverage_failures(policies) + _privilege_failures(policies)

    if failures:
        print("Vault policy check FAILED:")
        for line in failures:
            print(f"  ✗ {line}")
        return 1
    print(
        f"Vault policies OK: {len(policies)} policies, "
        f"{len(services_in_code())} Vault services read by code."
    )
    return 0


def write() -> int:
    policies = build_policies()
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    for stale in POLICY_DIR.glob("*.hcl"):
        if stale.stem not in policies:
            stale.unlink()
            print(f"removed {stale.relative_to(REPO_ROOT)}")
    for name, text in sorted(policies.items()):
        path = POLICY_DIR / f"{name}.hcl"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="regenerate config/vault/policies/*.hcl")
    group.add_argument("--check", action="store_true", help="verify policies match the code")
    args = parser.parse_args(argv)
    return write() if args.write else check()


if __name__ == "__main__":
    raise SystemExit(main())
