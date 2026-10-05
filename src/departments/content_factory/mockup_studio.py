"""
SYNDIKAT Content Factory — Mockup Studio for Print On Demand (POD).
Composites generated artwork onto apparel, posters, mugs, and phone cases
using local Pillow (PIL) pipeline at $0 software cost.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog
from PIL import Image, ImageEnhance

logger = structlog.get_logger(__name__)


class MockupStudio:
    """Automated compositor for ecommerce mockups and social media product visuals."""

    # Default mockup placement coordinates: (x, y, target_width, target_height)
    PLACEMENT_PRESETS = {
        "tshirt_front": (350, 420, 500, 650),
        "hoodie_chest": (380, 400, 450, 550),
        "poster_frame": (200, 180, 800, 1100),
        "mug_wrap": (300, 350, 400, 400),
    }

    def __init__(self, output_dir: Optional[str] = None):
        from src.data_paths import ensure_dir

        self.output_dir = ensure_dir("mockups", output_dir)

    def composite_artwork(
        self,
        artwork_path: str,
        template_path: Optional[str] = None,
        preset: str = "tshirt_front",
        output_filename: str = "mockup_result.webp",
        opacity: float = 0.95
    ) -> Dict[str, Any]:
        """Composite PNG artwork onto a base mockup template.

        Missing inputs used to be papered over with a synthetic cyan square
        while the response still said ``status: "ok"`` — a real-looking mockup
        with no real artwork behind it. Such renders are now tagged
        ``synthetic: True`` and carry a warning.
        """
        from PIL import UnidentifiedImageError

        art_p = Path(artwork_path)
        out_p = self.output_dir / output_filename
        warnings: List[str] = []
        synthetic = False

        if not art_p.exists():
            logger.info("artwork_missing_creating_synthetic", path=str(art_p))
            artwork = Image.new("RGBA", (800, 800), (0, 240, 255, 200))
            synthetic = True
            warnings.append(f"artwork_not_found:{art_p} — placeholder artwork composited")
        else:
            try:
                artwork = Image.open(art_p).convert("RGBA")
            except (UnidentifiedImageError, OSError) as exc:
                return {
                    "status": "error",
                    "error": f"artwork_unreadable: {exc}",
                    "mockup_path": None,
                    "preset": preset,
                    "synthetic": False,
                }

        # Base template or solid dark luxury backdrop
        if template_path:
            tpl_p = Path(template_path)
            if tpl_p.exists():
                try:
                    base = Image.open(tpl_p).convert("RGBA")
                except (UnidentifiedImageError, OSError) as exc:
                    warnings.append(f"template_unreadable:{exc}")
                    base = Image.new("RGBA", (1200, 1600), (15, 23, 42, 255))
            else:
                warnings.append(f"template_not_found:{template_path}")
                base = Image.new("RGBA", (1200, 1600), (15, 23, 42, 255))
        else:
            base = Image.new("RGBA", (1200, 1600), (15, 23, 42, 255))

        if preset not in self.PLACEMENT_PRESETS:
            warnings.append(f"unknown_preset:{preset} — falling back to tshirt_front placement")
        placement = self.PLACEMENT_PRESETS.get(preset, self.PLACEMENT_PRESETS["tshirt_front"])
        x, y, max_w, max_h = placement

        # Maintain aspect ratio of artwork
        artwork.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

        # Apply slight texture blend (fade alpha slightly to blend with garment)
        opacity = max(0.0, min(1.0, float(opacity)))
        if opacity < 1.0:
            alpha = artwork.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            artwork.putalpha(alpha)

        # Center within the bounding box
        paste_x = x + (max_w - artwork.width) // 2
        paste_y = y + (max_h - artwork.height) // 2

        base.paste(artwork, (paste_x, paste_y), mask=artwork)

        # Export as lightweight WebP / JPEG
        final_rgb = base.convert("RGB")
        try:
            final_rgb.save(str(out_p), format="WEBP", quality=88)
        except (OSError, ValueError) as exc:
            return {
                "status": "error",
                "error": f"mockup_export_failed: {exc}",
                "mockup_path": None,
                "preset": preset,
                "synthetic": synthetic,
                "warnings": warnings,
            }

        logger.info("mockup_created", output=str(out_p), preset=preset, synthetic=synthetic)
        return {
            "status": "ok",
            "mockup_path": str(out_p),
            "preset": preset,
            "dimensions": f"{final_rgb.width}x{final_rgb.height}",
            "synthetic": synthetic,
            "warnings": warnings,
        }
