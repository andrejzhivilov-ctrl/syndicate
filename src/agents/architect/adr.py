"""Architecture Decision Records (ADR) generation.

Implements the GitOps duty from ARCHITECT_CTO_SPEC.md §6 — every key change
produces a versioned ADR in ``/docs/adr/ADR-XXXX.md`` and a conventional-commit
message (e.g. ``feat(arch): ADR-0012 Implement Telnyx fallback gateway``).
Pure string/formatting helpers — no I/O — so the agent can decide whether to
write locally or push through the GitHub connector.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional


def format_adr(
    *,
    number: int,
    title: str,
    status: str = "Proposed",
    context: str = "",
    decision: str = "",
    consequences: str = "",
    alternatives: Optional[List[str]] = None,
    author: str = "Architect",
    when: Optional[str] = None,
) -> str:
    """Render a Markdown ADR following the standard Nygard template."""
    day = when or date.today().isoformat()
    alt_block = ""
    if alternatives:
        alt_block = "\n## Розглянуті альтернативи\n\n" + "\n".join(
            f"- {a}" for a in alternatives
        ) + "\n"
    num = f"{number:04d}"
    return (
        f"# ADR-{num}: {title}\n\n"
        f"- **Статус:** {status}\n"
        f"- **Дата:** {day}\n"
        f"- **Автор:** {author}\n\n"
        f"## Контекст\n\n{context or 'TBD'}\n\n"
        f"## Рішення\n\n{decision or 'TBD'}\n\n"
        f"## Наслідки\n\n{consequences or 'TBD'}\n"
        f"{alt_block}"
    )


def adr_filename(number: int, title: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title).strip("-")
    slug = "-".join(filter(None, slug.split("-")))[:60]
    return f"docs/adr/ADR-{number:04d}-{slug}.md"


def commit_message(number: int, title: str, kind: str = "feat", scope: str = "arch") -> str:
    return f"{kind}({scope}): ADR-{number:04d} {title}"


def build_adr_bundle(
    number: int, title: str, **kwargs: Any
) -> Dict[str, Any]:
    """Return the full artefact set for one architectural decision."""
    # ``kind`` only affects the commit message, not the document body — pop it
    # once, up front, so it can never leak into format_adr().
    kind = kwargs.pop("kind", "feat")
    return {
        "number": number,
        "path": adr_filename(number, title),
        "commit_message": commit_message(number, title, kind=kind),
        "content": format_adr(number=number, title=title, **kwargs),
    }
