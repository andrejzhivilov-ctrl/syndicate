"""Local typography preview and 300 DPI print artwork, never a fake photo mockup."""
from __future__ import annotations

import uuid

from PIL import Image, ImageDraw, ImageFont

from src.data_paths import ensure_dir


def _load_font(size: int):
    for candidate in ("DejaVuSans.ttf", "arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def render_personalization(caption: str) -> dict:
    folder = ensure_dir("tyler", "data/tyler") / "assets"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    artifact_id = uuid.uuid4().hex
    font_size = 150
    font = _load_font(font_size)
    artwork = Image.new("RGBA", (3600, 4500), (255, 255, 255, 0))
    draw = ImageDraw.Draw(artwork)
    # A bounded caption is fitted, rather than clipped or silently truncated.
    while draw.textbbox((0, 0), caption, font=font)[2] > 3200 and font_size > 12:
        font_size -= 2
        font = _load_font(font_size)
    draw.text((1800, 1600), caption, font=font, fill="#111111", anchor="mm")
    print_path = folder / f"{artifact_id}-print.png"
    artwork.save(print_path, dpi=(300, 300))
    preview = Image.new("RGB", (900, 1100), "#e9e9e9")
    painter = ImageDraw.Draw(preview)
    painter.polygon([(230, 160), (340, 110), (560, 110), (670, 160), (800, 350),
                     (670, 430), (630, 330), (630, 960), (270, 960), (270, 330),
                     (230, 430), (100, 350)], fill="#fafafa", outline="#888888")
    artwork.thumbnail((380, 480))
    preview.paste(artwork, (260, 330), artwork)
    preview_path = folder / f"{artifact_id}-preview.png"
    preview.save(preview_path)
    print_path.chmod(0o600)
    preview_path.chmod(0o600)
    return {"print_artwork": str(print_path), "preview": str(preview_path), "dpi": 300,
            "preview_type": "schematic_typography", "print_size_inches": [12, 15],
            "production_review_required": True,
            "warning": "Schematic preview, not a product photograph; review color, placement and font licensing"}
