import importlib.util
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _vault_policies():
    spec = importlib.util.spec_from_file_location("vault_policies_least_privilege_test", ROOT / "tools/vault_policies.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_acl_capabilities_are_read_only_except_token_self_renewal():
    policies = _vault_policies().build_policies()
    block_pattern = re.compile(
        r'path "([^"]+)"\s*\{\s*capabilities = \[([^\]]*)\]\s*\}', re.MULTILINE
    )

    for policy_name, policy_text in policies.items():
        blocks = {path: {cap.strip().strip('"') for cap in caps.split(",")} for path, caps in block_pattern.findall(policy_text)}
        if policy_name == "eva-operator":
            continue  # covered by test_operator_policy_is_write_only_for_secret_data
        assert "auth/token/lookup-self" in blocks
        assert "auth/token/renew-self" in blocks
        assert blocks["auth/token/lookup-self"] == {"read"}
        assert blocks["auth/token/renew-self"] == {"update"}
        for path, capabilities in blocks.items():
            if path in {"auth/token/lookup-self", "auth/token/renew-self"}:
                continue
            assert capabilities <= {"read", "list"}, f"{policy_name} grants write access to {path}"
            assert "read" in capabilities
            if "/metadata/" in path:
                assert "list" in capabilities
            else:
                assert capabilities == {"read"}


def test_operator_policy_is_write_only_for_secret_data():
    """The human operator token may store secrets — and administer nothing else."""
    text = _vault_policies().build_policies()["eva-operator"]
    block_pattern = re.compile(r'path "([^"]+)"\s*\{\s*capabilities = \[([^\]]*)\]\s*\}', re.MULTILINE)
    blocks = {p: {c.strip().strip('"') for c in caps.split(",")} for p, caps in block_pattern.findall(text)}
    for path, caps in blocks.items():
        if path.startswith("auth/token/"):
            continue
        assert path.startswith("secret/"), f"operator reaches outside the secret mount: {path}"
        assert "delete" not in caps and "sudo" not in caps
        assert "/eva-syndicate/" not in path, "operator must not write the retired legacy namespace"
    # No AppRole, policy or auth-method administration, no wildcard over the mount.
    assert not any(p.startswith(("auth/approle", "sys/")) for p in blocks)
    assert "secret/*" not in blocks and "secret/data/*" not in blocks
    # Must be able to do its one job.
    assert {"create", "update"} <= blocks["secret/data/syndicate/api-keys"]
    assert {"create", "update"} <= blocks["secret/data/syndicate/telegram/*"]


def test_every_director_has_a_policy_and_workers_stay_isolated():
    vault_policies = _vault_policies()
    policies = vault_policies.build_policies()
    from src import vault_paths

    for agent in vault_paths.DIRECTOR_IDS:
        if agent == "eva":
            assert "eva-agent" in policies
        else:
            assert f"eva-{agent}" in policies, f"no Vault policy for director {agent}"
    for worker in vault_paths.ISOLATED_WORKERS:
        for path in vault_paths.agent_policy_paths(worker):
            assert f"/agents/{worker}/" in path, f"{worker} reaches {path}"
