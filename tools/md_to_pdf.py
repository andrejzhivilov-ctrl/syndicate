#!/usr/bin/env python
"""Render a (GitHub-flavoured) Markdown file to PDF with Cyrillic support.

Reportlab's built-in Type-1 fonts carry no Cyrillic glyphs, so the text is set
in DejaVu (present on any Debian/Ubuntu base image and in the agent image).
Everything the audit reports use is supported: ATX headings, fenced code
blocks, pipe tables, bullet / ordered lists, bold and inline code.

Usage:
    python tools/md_to_pdf.py docs/FIX_REPORT.md [output.pdf]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

FONT_DIRS = (
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/dejavu"),
    Path("/usr/share/fonts/TTF"),
)

_FONT_CACHE: dict = {}


def register_fonts() -> Tuple[str, str]:
    """Register DejaVu and return ``(body_font, mono_font)`` names."""
    if _FONT_CACHE:
        return _FONT_CACHE["body"], _FONT_CACHE["mono"]

    wanted = {
        "DejaVuSans": "DejaVuSans.ttf",
        "DejaVuSans-Bold": "DejaVuSans-Bold.ttf",
        "DejaVuSans-Oblique": "DejaVuSans-Oblique.ttf",
        "DejaVuSansMono": "DejaVuSansMono.ttf",
        "DejaVuSansMono-Bold": "DejaVuSansMono-Bold.ttf",
    }
    registered = {}
    for name, filename in wanted.items():
        for directory in FONT_DIRS:
            candidate = directory / filename
            if candidate.exists():
                pdfmetrics.registerFont(TTFont(name, str(candidate)))
                registered[name] = True
                break

    if "DejaVuSans" not in registered:
        raise SystemExit(
            "DejaVu fonts not found in any of: " + ", ".join(str(d) for d in FONT_DIRS)
        )

    family = pdfmetrics.registerFontFamily(
        "DejaVuSans",
        normal="DejaVuSans",
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Oblique",
        boldItalic="DejaVuSans-Bold",
    )
    del family

    _FONT_CACHE["body"] = "DejaVuSans"
    _FONT_CACHE["mono"] = "DejaVuSansMono" if registered.get("DejaVuSansMono") else "Courier"
    return _FONT_CACHE["body"], _FONT_CACHE["mono"]


# --------------------------------------------------------------------- styles
def build_styles(body: str, mono: str) -> dict:
    base = getSampleStyleSheet()
    ss = {}

    ss["body"] = ParagraphStyle(
        "Body", parent=base["BodyText"], fontName=body, fontSize=9.5, leading=13.5,
        alignment=TA_LEFT, spaceAfter=5,
    )
    ss["h1"] = ParagraphStyle(
        "H1", parent=ss["body"], fontSize=19, leading=24, spaceBefore=4, spaceAfter=10,
        textColor=colors.HexColor("#0f172a"),
    )
    ss["h2"] = ParagraphStyle(
        "H2", parent=ss["body"], fontSize=13.5, leading=18, spaceBefore=13, spaceAfter=6,
        textColor=colors.HexColor("#0f172a"),
    )
    ss["h3"] = ParagraphStyle(
        "H3", parent=ss["body"], fontSize=11, leading=15, spaceBefore=9, spaceAfter=4,
        textColor=colors.HexColor("#1e293b"),
    )
    ss["h4"] = ParagraphStyle(
        "H4", parent=ss["body"], fontSize=10, leading=13, spaceBefore=7, spaceAfter=3,
        textColor=colors.HexColor("#334155"),
    )
    ss["code"] = ParagraphStyle(
        "Code", parent=base["Code"], fontName=mono, fontSize=8, leading=10.5,
        backColor=colors.HexColor("#f1f5f9"), borderPadding=5,
        textColor=colors.HexColor("#0f172a"), spaceBefore=4, spaceAfter=8,
    )
    ss["cell"] = ParagraphStyle(
        "Cell", parent=ss["body"], fontSize=8.2, leading=11, spaceAfter=0,
    )
    ss["cell_head"] = ParagraphStyle(
        "CellHead", parent=ss["cell"], fontName=body,
        textColor=colors.HexColor("#0f172a"),
    )
    ss["bullet"] = ParagraphStyle(
        "Bullet", parent=ss["body"], leftIndent=0, spaceAfter=2,
    )
    ss["rule"] = ParagraphStyle("Rule", parent=ss["body"], fontSize=1, leading=2, spaceAfter=6)
    return ss


# ------------------------------------------------------------------- markdown
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")


# DejaVu carries no colour emoji; reportlab would emit a blank box for them.
_EMOJI = re.compile(
    "["
    "\U0001f000-\U0001faff"      # pictographs, emoticons, symbols
    "\U00002190-\U000021ff"      # arrows
    "\U00002460-\U000027bf"      # enclosed alphanumerics, dingbats
    "\ufe0f\ufe0e\u200d"        # variation selectors, ZWJ
    "]+"
)


def strip_emoji(text: str) -> str:
    return _EMOJI.sub("", text)


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str, mono: str) -> str:
    """Escape, then re-apply the inline markup we support."""
    text = strip_emoji(text)
    placeholders: List[str] = []

    def stash(rendered: str) -> str:
        placeholders.append(rendered)
        return f"\x00{len(placeholders) - 1}\x00"

    def link_sub(match: re.Match) -> str:
        label = escape(strip_emoji(match.group(1)))
        href = escape(match.group(2)).replace('"', "&quot;")
        return stash(f'<link href="{href}" color="#2563eb">{label}</link>')

    def code_sub(match: re.Match) -> str:
        return stash(f'<font face="{mono}" size="8.6">{escape(match.group(1))}</font>')

    text = _LINK.sub(link_sub, text)
    text = _INLINE_CODE.sub(code_sub, text)
    text = _BOLD.sub(lambda m: stash(f"<b>{escape(m.group(1))}</b>"), text)
    text = _ITALIC.sub(lambda m: stash(f"<i>{escape(m.group(1))}</i>"), text)
    text = escape(text)
    for index, rendered in enumerate(placeholders):
        text = text.replace(f"\x00{index}\x00", rendered)
    return text


def split_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line and "|" in line


def _read_fence(lines: List[str], index: int) -> Tuple[int, str]:
    """Consume a ``` fenced block. Returns ``(next_index, code)``."""
    code: List[str] = []
    index += 1
    while index < len(lines) and not lines[index].strip().startswith("```"):
        code.append(lines[index])
        index += 1
    return index + 1, "\n".join(code)


def _read_table(lines: List[str], index: int) -> Tuple[int, List[List[str]]]:
    """Consume a pipe table (header + separator + body)."""
    rows = [split_row(lines[index])]
    index += 2
    while index < len(lines) and lines[index].strip().startswith("|"):
        rows.append(split_row(lines[index]))
        index += 1
    return index, rows


def _is_list_start(line: str) -> bool:
    return bool(re.match(r"^[-*]\s+", line))


def _is_ordered_start(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", line))


def _is_paragraph_end(line: str) -> bool:
    return (
        not line
        or line.startswith("```")
        or line.startswith("|")
        or line in ("---", "***", "___")
        or bool(re.match(r"^#{1,6}\s+", line))
        or _is_list_start(line)
        or _is_ordered_start(line)
    )


def _read_list(lines: List[str], index: int, ordered: bool) -> Tuple[int, List[str]]:
    """Consume a list, folding wrapped continuation lines into their item."""
    matcher = _is_ordered_start if ordered else _is_list_start
    strip = (lambda s: re.sub(r"^\d+\.\s+", "", s)) if ordered else (lambda s: re.sub(r"^[-*]\s+", "", s))
    items: List[str] = []
    while index < len(lines) and matcher(lines[index].strip()):
        items.append(strip(lines[index].strip()))
        index += 1
        # Continuation: an indented (or simply non-block) line belongs to the
        # item above it — otherwise a wrapped item silently starts a new list.
        while index < len(lines):
            nxt = lines[index].strip()
            if not nxt or matcher(nxt) or nxt.startswith(("```", "|", "#")) or nxt in ("---", "***", "___"):
                break
            if lines[index][:1] in (" ", "\t") or not _is_paragraph_end(nxt):
                items[-1] += " " + nxt
                index += 1
            else:
                break
    return index, items


def parse(markdown: str) -> List[List]:
    """Split the document into typed blocks: ``(kind, payload)``."""
    lines = markdown.splitlines()
    blocks: List[List] = []
    index = 0
    total = len(lines)

    while index < total:
        line = lines[index].strip()

        if not line:
            index += 1
        elif line.startswith("```"):
            index, code = _read_fence(lines, index)
            blocks.append(["code", code])
        elif line.startswith("|") and index + 1 < total and is_separator(lines[index + 1]):
            index, rows = _read_table(lines, index)
            blocks.append(["table", rows])
        elif line in ("---", "***", "___"):
            blocks.append(["rule", ""])
            index += 1
        elif re.match(r"^#{1,6}\s+", line):
            level, text = re.match(r"^(#{1,6})\s+(.*)$", line).groups()
            blocks.append([f"h{min(len(level), 4)}", text.strip()])
            index += 1
        elif _is_list_start(line):
            index, items = _read_list(lines, index, ordered=False)
            blocks.append(["ul", items])
        elif _is_ordered_start(line):
            index, items = _read_list(lines, index, ordered=True)
            blocks.append(["ol", items])
        else:
            paragraph: List[str] = []
            while index < total and not _is_paragraph_end(lines[index].strip()):
                paragraph.append(lines[index].strip())
                index += 1
            blocks.append(["p", " ".join(paragraph)])
    return blocks


# ------------------------------------------------------------------- rendering
def render(blocks: List[List], styles: dict, body: str, mono: str,
           title: str, usable_width: float) -> List:
    story: List = []
    first_heading = True

    for kind, payload in blocks:
        if kind == "rule":
            story.append(Spacer(1, 3))
            story.append(_hr(usable_width))
            story.append(Spacer(1, 5))
        elif kind == "code":
            story.append(Preformatted(payload, styles["code"]))
        elif kind.startswith("h"):
            text = inline(payload, mono)
            if kind == "h1" and first_heading:
                first_heading = False
            story.append(Paragraph(text, styles[kind]))
        elif kind == "p":
            story.append(Paragraph(inline(payload, mono), styles["body"]))
        elif kind in ("ul", "ol"):
            flowables = [
                ListItem(Paragraph(inline(item, mono), styles["bullet"]), leftIndent=14)
                for item in payload
            ]
            story.append(
                ListFlowable(
                    flowables,
                    bulletType="bullet" if kind == "ul" else "1",
                    bulletFontSize=7,
                    leftIndent=12,
                    spaceAfter=6,
                )
            )
        elif kind == "table":
            story.extend(_table(payload, styles, mono, usable_width))
        else:  # pragma: no cover - defensive
            raise ValueError(f"unknown block kind: {kind}")

    del title, body
    return story


def _hr(width: float) -> Table:
    table = Table([[""]], colWidths=[width], rowHeights=[0.7])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def _table(rows: List[List[str]], styles: dict, mono: str, usable_width: float) -> List:
    if not rows:
        return []

    header = rows[0]
    body_rows = rows[1:]
    columns = max(len(r) for r in rows)

    data = [[Paragraph(inline(c, mono), styles["cell_head"]) for c in _pad(header, columns)]]
    for row in body_rows:
        data.append([Paragraph(inline(c, mono), styles["cell"]) for c in _pad(row, columns)])

    # Equal columns keep wide tables readable; very wide tables compress instead
    # of overflowing the frame.
    col_width = usable_width / columns
    table = Table(data, colWidths=[col_width] * columns, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    return [Spacer(1, 4), table, Spacer(1, 8)]


def _pad(row: List[str], columns: int) -> List[str]:
    return row + [""] * (columns - len(row))


# ------------------------------------------------------------------------ main
def convert(source: Path, target: Optional[Path] = None) -> Path:
    body, mono = register_fonts()
    styles = build_styles(body, mono)

    markdown = source.read_text(encoding="utf-8")
    title = next(
        (line.lstrip("# ").strip() for line in markdown.splitlines() if line.startswith("# ")),
        source.stem,
    )

    target = target or source.with_suffix(".pdf")
    target.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(target),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=15 * mm,
        topMargin=17 * mm,
        bottomMargin=16 * mm,
        title=title,
        author="SYNDICATE audit",
        subject=title,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

    def decorate(canvas, document) -> None:
        canvas.saveState()
        canvas.setFont(body, 7.5)
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.drawString(doc.leftMargin, 10 * mm, title)
        canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"Стор. {document.page}")
        canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
        canvas.setLineWidth(0.4)
        canvas.line(doc.leftMargin, 12.5 * mm, A4[0] - doc.rightMargin, 12.5 * mm)
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=decorate)])

    story = render(parse(markdown), styles, body, mono, title, doc.width)
    doc.build(story)
    return target


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    source = Path(argv[1])
    target = Path(argv[2]) if len(argv) > 2 else None
    if not source.exists():
        print(f"no such file: {source}", file=sys.stderr)
        return 1
    out = convert(source, target)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
