#!/usr/bin/env python3
"""
SYNDICATE Holding — Vault Key & Fleet Management Tool.
Handles LLM Provider API Keys and 18-Agent Telegram Bot Tokens.
"""

import sys
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

VAULT_INIT_PATH = "/opt/eva/vault-secrets/vault-init.json"
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")

ALL_18_AGENTS = [
    "eva", "alice", "sonar", "architect", "kodex", "marshal",
    "fin", "sam", "jack", "scout", "oscar", "tyler",
    "ray", "dex", "doc", "trainer", "kira", "atlas"
]

def get_root_token() -> str:
    if not os.path.exists(VAULT_INIT_PATH):
        raise RuntimeError(f"Vault init file not found at {VAULT_INIT_PATH}")
    with open(VAULT_INIT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["root_token"]

def vault_request(method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    token = get_root_token()
    url = f"{VAULT_ADDR}/v1/{path.lstrip('/')}"
    headers = {
        "X-Vault-Token": token,
        "Content-Type": "application/json"
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if e.fp else str(e)
        if e.code == 404:
            return {}
        raise RuntimeError(f"Vault error {e.code} for {path}: {err_msg}")

def get_secret(path: str) -> Dict[str, Any]:
    res = vault_request("GET", f"secret/data/syndicate/{path}")
    return res.get("data", {}).get("data", {})

def put_secret(path: str, data: Dict[str, Any]) -> None:
    vault_request("POST", f"secret/data/syndicate/{path}", {"data": data})

def mask_key(k: str) -> str:
    if not k or len(k) < 8:
        return "***"
    return f"{k[:4]}...{k[-4:]}"

def cmd_status():
    print("=== SYNDICATE Vault Status ===")
    health = vault_request("GET", "sys/health")
    print(f"Vault Initialized: {health.get('initialized')}, Sealed: {health.get('sealed')}, Version: {health.get('version')}")
    
    # Check API keys
    api_keys = get_secret("api-keys")
    print(f"\n--- LLM Provider Keys ({len(api_keys)} configured) ---")
    for provider, val in sorted(api_keys.items()):
        print(f"  [{provider:16s}]: {mask_key(str(val))}")
        
    # Check master auth
    auth = get_secret("auth")
    print(f"\n--- Master API Key ---")
    print(f"  configured: {'YES' if auth.get('api_key') else 'NO'}")
    if auth.get('api_key'):
        print(f"  key: {mask_key(auth['api_key'])}")

    # Check Telegram Bots
    fleet = get_secret("telegram_bots")
    print(f"\n--- 18 Telegram Bots ({len(fleet)} / 18 configured) ---")
    for agent in ALL_18_AGENTS:
        status = mask_key(fleet[agent]) if agent in fleet else "MISSING"
        print(f"  {agent:12s}: {status}")

def cmd_get_auth():
    auth = get_secret("auth")
    key = auth.get("api_key", "")
    print(f"Master API Key: {key}")
    print(f"\nCockpit Direct URL:")
    print(f"https://syndicateholding.com/cockpit?token={key}")

def cmd_set_key(provider: str, key_val: str):
    provider = provider.strip().lower()
    mapping = {
        "openrouter": "openrouter_api_key",
        "gemini": "gemini_api_key",
        "google": "gemini_api_key",
        "anthropic": "anthropic_api_key",
        "claude": "anthropic_api_key",
        "openai": "openai_api_key",
        "perplexity": "perplexity_api_key",
        "sonar": "perplexity_api_key",
        "grok": "grok_api_key",
        "xai": "grok_api_key",
        "deepseek": "deepseek_api_key"
    }
    canonical = mapping.get(provider, f"{provider}_api_key")
    current = get_secret("api-keys")
    current[canonical] = key_val.strip()
    current[provider] = key_val.strip()  # also save short name
    put_secret("api-keys", current)
    print(f"[OK] Stored key for provider '{provider}' (canonical: '{canonical}') in Vault.")

def cmd_set_bot(agent_id: str, token: str):
    agent_id = agent_id.strip().lower()
    if agent_id not in ALL_18_AGENTS:
        print(f"[ERROR] Unknown agent '{agent_id}'. Must be one of: {', '.join(ALL_18_AGENTS)}")
        sys.exit(1)
    token = token.strip()
    
    fleet = get_secret("telegram_bots")
    fleet[agent_id] = token
    put_secret("telegram_bots", fleet)
    
    put_secret(f"telegram/{agent_id}", {"bot_token": token, "agent_id": agent_id})
    
    if agent_id == "eva":
        put_secret("telegram", {"bot_token": token})
        
    print(f"[OK] Telegram Bot for Agent '{agent_id}' stored successfully: {mask_key(token)}")

def cmd_bulk_bots(filepath_or_data: str):
    text = filepath_or_data
    if os.path.exists(filepath_or_data):
        with open(filepath_or_data, "r", encoding="utf-8") as f:
            text = f.read()
    
    count = 0
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        parts = line.split(":", 1)
        agent_id = parts[0].strip().lower()
        token = parts[1].strip()
        if agent_id in ALL_18_AGENTS and token:
            cmd_set_bot(agent_id, token)
            count += 1
    print(f"[BULK COMPLETE] Configured {count} Telegram bots.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: syndicate_vault.py <status|get-auth|set-key|set-bot|bulk-bots> [args...]")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "status":
        cmd_status()
    elif cmd == "get-auth":
        cmd_get_auth()
    elif cmd == "set-key":
        if len(sys.argv) < 4:
            print("Usage: syndicate_vault.py set-key <provider> <api_key>")
            sys.exit(1)
        cmd_set_key(sys.argv[2], sys.argv[3])
    elif cmd == "set-bot":
        if len(sys.argv) < 4:
            print("Usage: syndicate_vault.py set-bot <agent_id> <bot_token>")
            sys.exit(1)
        cmd_set_bot(sys.argv[2], sys.argv[3])
    elif cmd == "bulk-bots":
        if len(sys.argv) < 3:
            print("Usage: syndicate_vault.py bulk-bots <file_or_string>")
            sys.exit(1)
        cmd_bulk_bots(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
