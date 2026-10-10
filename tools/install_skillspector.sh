#!/usr/bin/env bash
# Install NVIDIA SkillSpector into .tools/skillspector for Marshal proposal scans.
# Does NOT add a Marshal capability, does NOT enable LLM pass, does NOT install agent skills.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="$REPO_ROOT/.tools/skillspector"
SOURCE="${SKILLSPECTOR_SOURCE:-git+https://github.com/NVIDIA/skillspector.git}"

echo "Marshal SkillSpector installer"
echo "  prefix: $PREFIX"
echo "  this is a host scanner, not a grant"

if ! command -v python3 >/dev/null; then
  echo "python3 not found" >&2
  exit 1
fi

PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
PY_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)')"
if [ "$(python3 -c 'import sys; print(sys.version_info.major)')" -lt 3 ] || [ "$PY_MINOR" -lt 12 ]; then
  echo "SkillSpector requires Python 3.12+. This host has $PY_VER." >&2
  echo "Install 3.12+, then re-run. Marshal wrapper stays fail-closed (scan_unavailable)." >&2
  exit 2
fi

mkdir -p "$REPO_ROOT/.tools"
python3 -m venv "$PREFIX"
"$PREFIX/bin/pip" install -U pip
"$PREFIX/bin/pip" install "$SOURCE"
if [ ! -x "$PREFIX/bin/skillspector" ]; then
  echo "skillspector binary missing after install" >&2
  exit 1
fi

echo "installed: $PREFIX/bin/skillspector"
echo "scan: python tools/marshal_skill_scan.py <local-skill-path>"
echo "never: skillspector without --no-llm; never remote GitHub URLs through Marshal wrapper"
