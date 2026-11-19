#!/bin/bash
# syndicate-ro — the only root command the `codex` user may run (via sudo). Read only.
# Install from the root-owned deploy copy, never from codex's own clone (docs/CODEX_SERVER.md):
#   install -m 755 -o root -g root /opt/syndicate/tools/server/syndicate_ro.sh /usr/local/bin/syndicate-ro
# Vault and LiveKit are deliberately not listed; there is no exec, restart or file access.
set -euo pipefail

ALLOWED="syndicate-syndicate-agent-1 deploy-sam-hermes-1 deploy-trainer-hermes-1 deploy-code-sandbox-1 \
syndicate-nginx-1 syndicate-embeddings-1 syndicate-whisper-1 syndicate-redis-1 syndicate-postgres-1 \
syndicate-garage-1 syndicate-kokoro-tts"

usage() {
  echo "usage: syndicate-ro status | version | logs <container> [lines<=2000]" >&2
  echo "containers: $ALLOWED" >&2
  exit 2
}

case "${1:-}" in
  status)
    docker ps --format '{{.Names}}\t{{.Status}}\t{{.Image}}'
    ;;
  version)
    git -C /opt/syndicate log -1 --format='%h %ad %s' --date=iso
    ;;
  logs)
    name="${2:-}"
    lines="${3:-200}"
    [[ " $ALLOWED " == *" $name "* ]] || usage
    [[ "$lines" =~ ^[0-9]{1,4}$ ]] && (( lines >= 1 && lines <= 2000 )) || usage
    docker logs --tail "$lines" "$name" 2>&1
    ;;
  *)
    usage
    ;;
esac
