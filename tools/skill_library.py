#!/usr/bin/env python3
"""Inspect installed project skills; never execute their commands or scripts."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent_platform.skill_library import SkillLibrary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--agent')
    parser.add_argument('--skill')
    parser.add_argument('--resource', default='SKILL.md')
    args = parser.parse_args()
    if not args.verify and not args.agent:
        parser.error('--agent or --verify is required')
    try:
        library = SkillLibrary()
        if args.verify:
            result = library.verify()
        elif args.skill:
            result = library.read(args.agent, args.skill, args.resource)
        else:
            result = library.for_agent(args.agent)
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({'status': 'unavailable', 'value': None,
                          'warning': 'skill_missing_invalid_or_unassigned'}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
