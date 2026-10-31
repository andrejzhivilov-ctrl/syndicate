#!/usr/bin/env python3
"""SYNDICATE — Vault key & fleet management (provider keys, 18 Telegram bots).

Security properties (this replaces a version that used the root token from
``vault-init.json``, took secrets as command-line arguments and printed a
``?token=`` URL):

* uses the restricted ``eva-operator`` token (``VAULT_TOKEN`` env, or the file
  ``/opt/eva/vault-secrets/operator.token``) — never the root token;
* secrets are read from a hidden prompt / stdin / a 0600 file, never from argv,
  so they do not land in shell history or ``ps``;
* secrets are never printed in full; the master key is shown only with an
  explicit ``--reveal`` on an interactive terminal, and never as a URL.

Usage:
    scripts/syndicate_vault.py status
    scripts/syndicate_vault.py set-key <provider>            # prompts for the key
    scripts/syndicate_vault.py set-bot <agent_id>            # prompts for the token
    scripts/syndicate_vault.py bulk-bots <file> [--shred]    # file lines: agent_id:token
    scripts/syndicate_vault.py distribute-keys                # pool -> each worker's own subtree
    scripts/syndicate_vault.py verify-bots                   # Telegram getMe per bot
    scripts/syndicate_vault.py set-owner <telegram_user_id>  # who may talk to the bots
    scripts/syndicate_vault.py set-location                  # prompts: fixed point for Eva's weather
    scripts/syndicate_vault.py rotate-master [--reveal]
    scripts/syndicate_vault.py show-master --reveal
    scripts/syndicate_vault.py obsidian-webdav --reveal [--rotate]  # Remotely Save (WebDAV) login for PC/phone
"""
from __future__ import annotations

import getpass
import json
import os
import re
import secrets
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.vault_paths import DIRECTOR_IDS  # noqa: E402

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
OPERATOR_TOKEN_FILE = Path(os.getenv("VAULT_OPERATOR_TOKEN_FILE", "/opt/eva/vault-secrets/operator.token"))
ALL_18_AGENTS = list(DIRECTOR_IDS)
BOT_TOKEN_RE = re.compile(r"^\d{6,12}:[A-Za-z0-9_-]{30,50}$")

#: Which provider keys each isolated worker may hold (manifest §3.3 tier routing).
#: Names are the ones ``director_providers.build_provider`` understands:
#: openrouter | gemini | grok | haiku | youtube | odds.
WORKER_PROVIDERS = {
    "oscar": ("grok", "gemini", "haiku"),
    "tyler": ("grok", "openrouter", "haiku"),
    "jack": ("openrouter", "gemini", "odds"),
    "sonar": ("gemini", "openrouter"),
    "scout": ("gemini", "grok", "youtube"),
    "dex": ("gemini", "openrouter"),
    "ray": ("gemini", "openrouter"),
    "atlas": ("gemini", "openrouter"),
}
#: Pool entry (``api-keys``) each worker-side provider name is copied from.
POOL_SOURCE = {
    "openrouter": "openrouter_api_key",
    "gemini": "gemini_api_key",
    "grok": "grok_api_key",
    "haiku": "anthropic_api_key",
    "youtube": "youtube_api_key",
    "odds": "odds_api_key",
}

PROVIDER_KEYS = {
    "youtube": ("youtube_api_key",),
    "odds": ("odds_api_key",),
    "openrouter": ("openrouter_api_key",),
    "gemini": ("gemini_api_key", "google_api_key"),
    "google": ("gemini_api_key", "google_api_key"),
    "anthropic": ("anthropic_api_key",),
    "claude": ("anthropic_api_key",),
    "openai": ("openai_api_key",),
    "perplexity": ("perplexity_api_key",),
    "sonar": ("perplexity_api_key",),
    "grok": ("grok_api_key", "xai_api_key"),
    "xai": ("grok_api_key", "xai_api_key"),
    "deepseek": ("deepseek_api_key",),
    "groq": ("groq_api_key",),
    # Voice replies in the director bots (src/voice_reply.py).
    "respeecher": ("respeecher_api_key",),
    "elevenlabs": ("elevenlabs_api_key",),
    # Air-raid alerts for Eva's briefings (src/integrations/public_data.py).
    "alerts": ("alerts_in_ua_token",),
    # Sam's macro sources (src/integrations/macro_data.py). EDGAR takes no key but
    # a "Name email" User-Agent, stored the same way so it never lands in code.
    "fred": ("fred_api_key",),
    "eia": ("eia_api_key",),
    "edgar": ("sec_user_agent",),
    # n8n public API key: Eva and the architect build and read workflows through it.
    "n8n": ("n8n_api_key",),
}


def _token() -> str:
    token = os.getenv("VAULT_TOKEN", "").strip()
    if token:
        return token
    if OPERATOR_TOKEN_FILE.is_file():
        mode = OPERATOR_TOKEN_FILE.stat().st_mode
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            raise SystemExit(f"{OPERATOR_TOKEN_FILE} must be mode 0600 (is {oct(mode & 0o777)})")
        return OPERATOR_TOKEN_FILE.read_text(encoding="utf-8").strip()
    raise SystemExit(
        "No operator token. Set VAULT_TOKEN or create /opt/eva/vault-secrets/operator.token "
        "(written by deploy/scripts/vault_init.sh)."
    )


def vault_request(method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{VAULT_ADDR}/v1/{path.lstrip('/')}"
    headers = {"X-Vault-Token": _token(), "Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310 - fixed VAULT_ADDR
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        detail = exc.read().decode("utf-8", "replace") if exc.fp else str(exc)
        raise SystemExit(f"Vault error {exc.code} for {path}: {detail[:300]}") from None


def get_secret(path: str) -> Dict[str, Any]:
    return vault_request("GET", f"secret/data/syndicate/{path}").get("data", {}).get("data", {}) or {}


def put_secret(path: str, data: Dict[str, Any]) -> None:
    vault_request("POST", f"secret/data/syndicate/{path}", {"data": data})


def mask(value: str) -> str:
    return "***" if not value or len(value) < 12 else f"{value[:3]}…{value[-3:]}"


def read_secret_value(prompt: str) -> str:
    """Hidden prompt on a TTY, otherwise the first line of stdin. Never argv."""
    if sys.stdin.isatty():
        value = getpass.getpass(prompt)
    else:
        value = sys.stdin.readline()
    value = value.strip()
    if not value:
        raise SystemExit("empty value — nothing stored")
    return value


def cmd_status() -> None:
    health = vault_request("GET", "sys/health")
    print(f"Vault initialized={health.get('initialized')} sealed={health.get('sealed')} version={health.get('version')}")
    keys = get_secret("api-keys")
    print(f"\nProvider keys ({len(keys)} stored):")
    for name in sorted(keys):
        print(f"  {name:24s} {mask(str(keys[name]))}")
    print(f"\nMaster API key: {'configured' if get_secret('auth').get('api_key') else 'MISSING'}")
    owner = get_secret("telegram").get("owner_user_id")
    print(f"Telegram owner id: {owner if owner else 'MISSING (gateway will reject every message)'}")
    present = 0
    print("\nTelegram bots:")
    for agent in ALL_18_AGENTS:
        token = get_secret(f"telegram/{agent}").get("bot_token", "")
        present += 1 if token else 0
        print(f"  {agent:10s} {mask(token) if token else 'MISSING'}")
    print(f"\n{present}/18 bots configured.")


def cmd_set_key(provider: str) -> None:
    provider = provider.strip().lower()
    names = PROVIDER_KEYS.get(provider, (f"{provider}_api_key",))
    if not re.fullmatch(r"[a-z0-9_]{2,40}", provider):
        raise SystemExit("invalid provider name")
    if provider == "edgar":  # SEC wants a contact, not a key: "Company Name email@domain"
        value = read_secret_value("SEC EDGAR User-Agent, 'Name email@domain' (hidden): ")
        if "@" not in value or " " not in value.strip():
            raise SystemExit("EDGAR needs 'Name email@domain', e.g. 'Syndicate Research you@example.com'")
    else:
        value = read_secret_value(f"{provider} API key (hidden): ")
    current = get_secret("api-keys")
    for name in names:
        current[name] = value
    put_secret("api-keys", current)
    print(f"[OK] stored {', '.join(names)} ({mask(value)})")


def cmd_distribute_keys() -> None:
    """Copy pool keys into each worker's own subtree (least privilege per worker)."""
    pool = get_secret("api-keys")
    copied = skipped = 0
    for agent, providers in WORKER_PROVIDERS.items():
        for provider in providers:
            value = pool.get(POOL_SOURCE[provider])
            if not value:
                print(f"  {agent:8s} {provider:11s} SKIP (pool has no {POOL_SOURCE[provider]})")
                skipped += 1
                continue
            put_secret(f"agents/{agent}/{provider}", {"api_key": value, "provider": provider})
            print(f"  {agent:8s} {provider:11s} copied")
            copied += 1
    print(f"\n{copied} copied, {skipped} skipped. Re-run after adding or rotating a provider key.")


def cmd_set_bot(agent_id: str, token: Optional[str] = None) -> None:
    agent_id = agent_id.strip().lower()
    if agent_id not in ALL_18_AGENTS:
        raise SystemExit(f"unknown agent '{agent_id}'. Valid: {', '.join(ALL_18_AGENTS)}")
    token = (token or read_secret_value(f"Telegram bot token for {agent_id} (hidden): ")).strip()
    if not BOT_TOKEN_RE.fullmatch(token):
        raise SystemExit("that does not look like a Telegram bot token (<digits>:<35 chars>)")
    put_secret(f"telegram/{agent_id}", {"bot_token": token, "agent_id": agent_id})
    print(f"[OK] bot for '{agent_id}' stored ({mask(token)})")


def cmd_bulk_bots(path: str, shred: bool) -> None:
    file = Path(path)
    if not file.is_file():
        raise SystemExit(f"{path} not found")
    mode = file.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise SystemExit(f"{path} must be mode 0600 before it may hold tokens (chmod 600 {path})")
    count = 0
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        agent_id, token = line.split(":", 1)
        cmd_set_bot(agent_id.strip(), token.strip())
        count += 1
    print(f"[BULK] stored {count} bot tokens")
    if shred:
        try:
            size = file.stat().st_size
            file.write_bytes(b"\0" * size)
        finally:
            file.unlink()
        print(f"[BULK] {path} overwritten and removed")


def cmd_verify_bots() -> None:
    ok = 0
    for agent in ALL_18_AGENTS:
        token = get_secret(f"telegram/{agent}").get("bot_token", "")
        if not token:
            print(f"  {agent:10s} MISSING")
            continue
        try:
            with urllib.request.urlopen(  # noqa: S310 - fixed host
                f"https://api.telegram.org/bot{token}/getMe", timeout=10
            ) as resp:
                info = json.loads(resp.read().decode("utf-8")).get("result", {})
            print(f"  {agent:10s} OK  @{info.get('username')}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  {agent:10s} FAIL {type(exc).__name__}")
    print(f"\n{ok}/18 bots answered getMe.")


def cmd_set_owner(user_id: str) -> None:
    if not re.fullmatch(r"\d{4,15}", user_id.strip()):
        raise SystemExit("Telegram user id is a number (ask @userinfobot or your own bot)")
    current = get_secret("telegram")
    current["owner_user_id"] = user_id.strip()
    put_secret("telegram", current)
    print("[OK] owner id stored; the gateway now accepts messages only from this user")


def cmd_set_location() -> None:
    """Fixed point for Eva's weather (not GPS): prompted, so it stays out of shell history."""
    latitude = float(input("Latitude (e.g. 50.45): ").strip().replace(",", "."))
    longitude = float(input("Longitude (e.g. 30.52): ").strip().replace(",", "."))
    label = input("Label shown in the bot (optional, e.g. a city): ").strip()
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise SystemExit("latitude must be -90..90 and longitude -180..180")
    put_secret("agents/eva/briefing", {"latitude": round(latitude, 2), "longitude": round(longitude, 2),
                                       "label": label[:60]})
    print("[OK] weather point stored (rounded to ~1 km)")


def cmd_rotate_master(reveal: bool) -> None:
    auth = get_secret("auth")
    new_key = secrets.token_urlsafe(48)
    auth["api_key"] = new_key
    put_secret("auth", auth)
    print("[OK] master API key rotated. Restart eva-agent so it picks up the new key.")
    print("     Every device token stays valid; the old master key stops working.")
    if reveal:
        _print_master(new_key)


def _print_master(key: str) -> None:
    if not sys.stdout.isatty():
        raise SystemExit("refusing to print the master key to a non-interactive stream")
    print(f"\nMASTER KEY (shown once, store it in your password manager):\n{key}\n")


def cmd_show_master(reveal: bool) -> None:
    if not reveal:
        raise SystemExit("pass --reveal to display the key (interactive terminal only)")
    key = get_secret("auth").get("api_key", "")
    if not key:
        raise SystemExit("no master key stored")
    _print_master(key)


def cmd_obsidian_webdav(reveal: bool, rotate: bool = False) -> None:
    """WebDAV login for the Remotely Save plugin; created in Vault on the first run."""
    if not reveal:
        raise SystemExit("pass --reveal to display the Obsidian WebDAV login (interactive terminal only)")
    # Checked before any write: a rotated password nobody saw would lock out every device.
    if not sys.stdout.isatty():
        raise SystemExit("refusing to print the login to a non-interactive stream")
    data = get_secret("agents/eva/obsidian")
    if rotate or not data.get("webdav_password"):
        data = {**data, "webdav_user": "andrii", "webdav_password": secrets.token_urlsafe(24)}
        put_secret("agents/eva/obsidian", data)
        print("New login stored in Vault: restart eva-agent so the WebDAV server picks it up.")
    print("\nRemotely Save → Remote service: WebDAV")
    print("  Server Address: https://sync.syndicateholding.com")
    print(f"  Username:       {data['webdav_user']}")
    print(f"  Password:       {data['webdav_password']}")
    print("  Auth Type:      basic")
    print("  Change The Remote Base Directory: vault")


def cmd_obsidian_key(reveal: bool) -> None:
    """Settings for the Remotely Save plugin (S3) on Andrii's PC and phone."""
    if not reveal:
        raise SystemExit("pass --reveal to display the Obsidian sync key (interactive terminal only)")
    data = get_secret("agents/eva/obsidian")
    if not data.get("access_key_id"):
        raise SystemExit("no Obsidian sync key yet: run `python3 tools/garage_setup.py --apply` first")
    if not sys.stdout.isatty():
        raise SystemExit("refusing to print the key to a non-interactive stream")
    print("\nRemotely Save → Remote service: S3 or compatible")
    print(f"  Endpoint:          {data.get('endpoint')}")
    print(f"  Region:            {data.get('region', 'garage')}")
    print(f"  Access Key ID:     {data['access_key_id']}")
    print(f"  Secret Access Key: {data['secret_access_key']}")
    print(f"  Bucket Name:       {data.get('bucket')}")
    print("  S3 URL style:      Path-Style;  Bypass CORS: on;  Encryption password: leave empty\n")


def main(argv: list[str]) -> int:  # noqa: C901
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, rest = argv[1].lower(), argv[2:]
    flags = {a for a in rest if a.startswith("--")}
    args = [a for a in rest if not a.startswith("--")]
    if cmd == "status":
        cmd_status()
    elif cmd == "set-key" and args:
        cmd_set_key(args[0])
    elif cmd == "set-bot" and args:
        cmd_set_bot(args[0])
    elif cmd == "bulk-bots" and args:
        cmd_bulk_bots(args[0], "--shred" in flags)
    elif cmd == "distribute-keys":
        cmd_distribute_keys()
    elif cmd == "verify-bots":
        cmd_verify_bots()
    elif cmd == "set-owner" and args:
        cmd_set_owner(args[0])
    elif cmd == "set-location":
        cmd_set_location()
    elif cmd == "rotate-master":
        cmd_rotate_master("--reveal" in flags)
    elif cmd == "obsidian-key":
        cmd_obsidian_key("--reveal" in flags)
    elif cmd == "obsidian-webdav":
        cmd_obsidian_webdav("--reveal" in flags, "--rotate" in flags)
    elif cmd == "show-master":
        cmd_show_master("--reveal" in flags)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
