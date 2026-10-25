#!/usr/bin/env python3
"""Release the emergency lockdown. Run on the server, inside the eva-agent container:

    docker exec -it syndicate-eva-agent-1 python -m tools.unlock_lockdown

Asks for the master API key (hidden) and compares it, in constant time, with the
key the running process holds (``EVA_API_KEY`` in its environment). There is no
HTTP endpoint for this on purpose (manifest §11.2.4).
"""
from __future__ import annotations

import getpass
import hmac
import os
import sys

from src.lockdown import Lockdown


def main() -> int:
    expected = os.getenv("EVA_API_KEY", "")
    if not expected:
        print("EVA_API_KEY is not set in this environment; cannot verify the master key.", file=sys.stderr)
        return 2
    lock = Lockdown()
    if not lock.is_locked():
        print("Not locked down.")
        return 0
    info = lock.info() or {}
    print(f"Lockdown engaged at {info.get('engaged_at')} by {info.get('actor')}: {info.get('reason')}")
    presented = getpass.getpass("Master key: ")
    if not hmac.compare_digest(presented.encode("utf-8"), expected.encode("utf-8")):
        print("Wrong key. Still locked.", file=sys.stderr)
        return 1
    lock.path.unlink()
    print("Lockdown released.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
