"""Static deploy-config invariants (docker is not available in CI, so check the YAML)."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_FILES = [ROOT / "deploy" / n for n in (
    "docker-compose.yml", "docker-compose.directors.yml", "docker-compose.voice.yml",
    "docker-compose.alice.yml", "docker-compose.integrations.yml")]
# Ports that are intentionally reachable from the internet (UFW also allows exactly these).
PUBLIC_PORTS = {"80:80", "443:443", "7881:7881/tcp", "7882:7882/udp"}


def test_root_and_deploy_compose_are_identical():
    assert (ROOT / "docker-compose.yml").read_text() == (ROOT / "deploy" / "docker-compose.yml").read_text()


def test_only_the_documented_ports_are_published_publicly():
    for path in COMPOSE_FILES:
        doc = yaml.safe_load(path.read_text())
        for name, svc in (doc.get("services") or {}).items():
            for port in svc.get("ports") or []:
                spec = str(port)
                if spec.startswith("127.0.0.1:") or "SYNCTHING_BIND_IP" in spec:
                    continue
                assert spec in PUBLIC_PORTS, f"{path.name}:{name} publishes {spec} on all interfaces"


def test_every_director_overlay_secret_id_name_is_written_by_vault_init():
    overlay = (ROOT / "deploy" / "docker-compose.directors.yml").read_text()
    names = set(re.findall(r"\$\{([A-Z]+)_VAULT_ROLE_ID", overlay))
    init = (ROOT / "deploy" / "scripts" / "vault_init.sh").read_text()
    assert names and "${agent_key^^}_VAULT_ROLE_ID" in init
    from src.vault_paths import AGENTS_IDS
    assert {n.lower() for n in names} <= set(AGENTS_IDS)


def test_bootstrap_keeps_token_out_of_argv_and_remote():
    text = (ROOT / "deploy" / "server_bootstrap.sh").read_text()
    assert "${1:-}" not in text and "https://${GITHUB_TOKEN}@" not in text
    assert "ufw allow in 7880" not in text and "ufw allow in 22000" not in text


def test_secret_dumps_are_not_tracked():
    ignore = (ROOT / ".gitignore").read_text()
    for needle in ("EVA_SYNDICATE_FULL_DIALOGUE", "vault-init.json", "directors.env"):
        assert needle in ignore
    assert not (ROOT / "EVA_SYNDICATE_FULL_DIALOGUE.txt").exists()


def test_livekit_joins_the_network_nginx_proxies_it_on():
    # nginx reaches syndicate-livekit:7880 via syndicate_frontend; a recreate
    # without this declaration left voice.<domain> unreachable and nginx -t red.
    voice = yaml.safe_load((ROOT / "deploy" / "docker-compose.voice.yml").read_text())
    assert "syndicate_frontend" in voice["services"]["livekit-server"]["networks"]
    assert voice["networks"]["syndicate_frontend"]["external"] is True
    nginx = (ROOT / "config" / "nginx" / "nginx.conf").read_text()
    assert "syndicate-livekit:7880" in nginx


def test_vault_init_raises_the_approle_mount_ttl_cap():
    # SecretID TTL is capped by the approle mount's max_lease_ttl; without the
    # tune the "90-day" SecretIDs died after 24h (hand-tuned) or 32 days (default).
    init = (ROOT / "deploy" / "scripts" / "vault_init.sh").read_text()
    assert 'sys/auth/approle/tune' in init
    assert '\\"max_lease_ttl\\": \\"${SECRET_ID_TTL}\\"' in init
