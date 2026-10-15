"""Local editorial assets with escaped text and generated filesystem names."""
from __future__ import annotations

import uuid
from html import escape

from PIL import Image, ImageDraw, ImageFont

from src.data_paths import ensure_dir
from src.agents.director_base import text


def thumbnail(title: str, brand: str) -> dict:
    folder = ensure_dir("oscar", "data/oscar") / "assets"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    image = Image.new("RGB", (1280, 720), "#122033")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("DejaVuSans.ttf", 66)
    # Wrap by measured pixels rather than character count.
    lines, current = [], ""
    for word in title.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) > 1120:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    if len(lines) > 5 or any(draw.textlength(line, font=font) > 1120 for line in lines):
        raise ValueError("thumbnail_title_too_long")
    draw.multiline_text((80, 100), "\n".join(lines), font=font, fill="white", spacing=18)
    draw.text((80, 630), brand, font=ImageFont.truetype("DejaVuSans.ttf", 30), fill="#57e8bc")
    path = folder / f"{uuid.uuid4().hex}-thumbnail.png"
    image.save(path)
    path.chmod(0o600)
    return {"path": str(path), "dimensions": [1280, 720], "kind": "typographic_editorial_draft",
            "ctr": None, "warning": "CTR cannot be predicted without an experiment"}


def diagram(payload: dict) -> dict:
    nodes = payload["nodes"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 12:
        raise ValueError("diagram_node_count")
    labels = [escape(text(label, "node_label", 80)) for label in nodes]
    width, height = 900, 60 + 100 * len(labels)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>']
    for i, label in enumerate(labels):
        y = 30 + i * 100
        if i:
            parts.append(f'<path d="M450 {y-30} V{y}" stroke="#334155" stroke-width="3"/>')
        parts += [f'<rect x="50" y="{y}" width="800" height="70" rx="12" fill="#e2e8f0"/>',
                  f'<text x="450" y="{y+43}" text-anchor="middle" font-family="sans-serif" font-size="18">{label}</text>']
    parts.append('</svg>')
    folder = ensure_dir("oscar", "data/oscar") / "assets"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = folder / f"{uuid.uuid4().hex}-diagram.svg"
    path.write_text("".join(parts))
    path.chmod(0o600)
    return {"path": str(path), "format": "svg", "nodes": len(labels)}
