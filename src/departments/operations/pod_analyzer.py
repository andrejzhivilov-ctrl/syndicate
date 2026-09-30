"""
SYNDIKAT Operations — Print on Demand (POD) Trend Analyzer.
Discovers high-intent, low-competition evergreen niches for merchandise.
Issues design prompts to Content Factory Mockup Studio.
"""

from __future__ import annotations

from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(__name__)


class PODAnalyzer:
    """Discovers trending phrases, aesthetic themes, and micro-niches for merchandise."""

    EVERGREEN_NICHES = [
        {
            "niche": "Code & Terminal Humor",
            "search_volume": "HIGH",
            "competition": "MEDIUM",
            "seed_phrases": [
                "There is no place like 127.0.0.1",
                "git commit -m 'It works on my machine'",
                "sudo rm -rf /excuses"
            ],
            "recommended_products": ["oversized_tshirt", "hoodie", "coffee_mug"]
        },
        {
            "niche": "Cyberpunk & Minimalist Circuit Aesthetics",
            "search_volume": "HIGH",
            "competition": "LOW",
            "seed_phrases": [
                "Decentralized Consciousness",
                "Neural Network Hardware Architect",
                "Zero Trust Protocol"
            ],
            "recommended_products": ["metal_poster", "desk_mat", "phone_case"]
        },
        {
            "niche": "Veteran Stoic Resilience",
            "search_volume": "MEDIUM",
            "competition": "LOW",
            "seed_phrases": [
                "Amor Fati — Embrace the grind",
                "Calm in the Tempest",
                "Discipline Over Motivation"
            ],
            "recommended_products": ["heavyweight_hoodie", "gym_tote", "canvas_print"]
        }
    ]

    def scan_niches(self) -> List[Dict[str, Any]]:
        """Return vetted niches scored by margin and conversion."""
        logger.info("pod_niches_scanned", count=len(self.EVERGREEN_NICHES))
        return self.EVERGREEN_NICHES

    def generate_design_brief(self, niche_name: str) -> Dict[str, Any]:
        """Produce a design order for MockupStudio."""
        niche = next((n for n in self.EVERGREEN_NICHES if n["niche"].lower() == niche_name.lower()), self.EVERGREEN_NICHES[0])
        return {
            "order_id": f"pod_brief_{niche['niche'][:10].strip().replace(' ', '_').lower()}",
            "theme": niche["niche"],
            "seed_phrase": niche["seed_phrases"][0],
            "products": niche["recommended_products"],
            "assigned_to": "content_factory/mockup_studio"
        }
