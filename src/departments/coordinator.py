"""
SYNDIKAT Floor 2 Coordinator.
Orchestrates operations across Content Factory, Operations, and Compliance departments.
Maintains strict domain isolation:
- All financial metrics are routed to Fin (CFO).
- Sam remains strictly isolated in Quant Trading.
- Sentinel and PolicySentinel gate all outbound assets.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import structlog

from src.departments.compliance.antidetect_browser import AntiDetectProfileManager
from src.departments.compliance.policy_sentinel import PolicySentinel
from src.departments.content_factory.broll_scout import BRollScout
from src.departments.content_factory.caption_engine import CaptionEngine
from src.departments.content_factory.grok_writer import GrokWriter
from src.departments.content_factory.mockup_studio import MockupStudio
from src.departments.content_factory.publisher import ContentPublisher
from src.departments.content_factory.script_director import ScriptDirector
from src.departments.content_factory.video_engine_v2 import VideoEngineV2
from src.departments.content_factory.video_producer import VideoProducer
from src.departments.operations.affiliate_scout import AffiliateScout
from src.departments.operations.growth_analyst import GrowthAnalyst
from src.departments.operations.pod_analyzer import PODAnalyzer

logger = structlog.get_logger(__name__)


class Floor2Coordinator:
    """Dispatches work orders across Floor 2 business units and content factory."""

    AGENT_ID = "floor2_coordinator"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.video_producer = VideoProducer()
        self.video_engine_v2 = VideoEngineV2()
        self.script_director = ScriptDirector()
        self.broll_scout = BRollScout()
        self.caption_engine = CaptionEngine()
        self.publisher = ContentPublisher()
        self.grok_writer = GrokWriter()
        self.mockup_studio = MockupStudio()
        self.affiliate_scout = AffiliateScout()
        self.pod_analyzer = PODAnalyzer()
        self.growth_analyst = GrowthAnalyst()
        self.policy_sentinel = PolicySentinel()
        self.antidetect_mgr = AntiDetectProfileManager()

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task based on action."""
        action = payload.get("action", "")
        logger.info("floor2_dispatch", action=action)

        if action == "render_short_video":
            broll = payload.get("broll_video", "media/templates/abstract_loop.mp4")
            script = payload.get("script_text", "Ось топ-3 інструменти для автоматизації бізнесу у 2026 році.")
            filename = payload.get("output_filename", "short_render.mp4")
            voice = payload.get("voice")
            return await self.video_producer.render_video(broll, script, filename, voice=voice)

        elif action == "create_viral_short":
            # Next-Gen End-to-End Pipeline
            topic = payload.get("topic", "Автономний холдинг на одному сервері")
            niche = payload.get("niche", "ai_automation")
            duration = payload.get("duration_sec", 30)
            voice = payload.get("voice", "uk-UA-PolinaNeural")
            filename = payload.get("output_filename")
            bg_music = payload.get("bg_music")
            style = payload.get("caption_style", "hormozi_cyan")
            return await self.video_engine_v2.render_complete_short(
                topic=topic,
                niche=niche,
                duration_sec=duration,
                voice=voice,
                output_filename=filename,
                bg_music=bg_music,
                caption_style=style
            )

        elif action == "direct_short_script":
            topic = payload.get("topic", "Автоматизація бізнесу без SaaS витрат")
            niche = payload.get("niche", "ai_holding")
            duration = payload.get("duration_sec", 30)
            return await self.script_director.generate_short_script(topic, niche, target_duration_sec=duration)

        elif action == "source_broll_batch":
            scenes = payload.get("scenes", [])
            return {"status": "ok", "clips": await self.broll_scout.fetch_broll_batch(scenes)}

        elif action == "generate_karaoke_captions":
            text = payload.get("text", "")
            duration = payload.get("duration_sec", 30.0)
            timed_words = self.caption_engine.generate_word_timestamps(text, duration)
            style = payload.get("style", "hormozi_cyan")
            ass_path = self.caption_engine.create_ass_karaoke_file(timed_words, style_preset=style)
            return {"status": "ok", "ass_path": ass_path, "timed_words_count": len(timed_words)}

        elif action == "publish_content_campaign":
            video_path = payload.get("video_path", "")
            metadata = payload.get("seo_metadata", {})
            return await self.publisher.dispatch_full_campaign(video_path, metadata)

        elif action == "generate_viral_thread":
            topic = payload.get("topic", "Lean AI holding automation")
            niche = payload.get("niche", "saas_affiliate")
            cta = payload.get("target_cta")
            return await self.grok_writer.generate_thread(topic, niche, target_cta=cta)

        elif action == "generate_pod_mockup":
            artwork = payload.get("artwork_path", "media/art/cyber_skull.png")
            preset = payload.get("preset", "tshirt_front")
            # Compliance check first!
            safe, violations = self.policy_sentinel.check_design_compliance(artwork, [preset])
            if not safe:
                return {"status": "veto_blocked", "reason": violations}
            return self.mockup_studio.composite_artwork(artwork, preset=preset)

        elif action == "scout_affiliate_offers":
            category = payload.get("category")
            return {"status": "ok", "offers": self.affiliate_scout.scout_top_offers(category)}

        elif action == "analyze_pod_trends":
            return {"status": "ok", "niches": self.pod_analyzer.scan_niches()}

        elif action == "aggregate_growth_metrics":
            perf = self.growth_analyst.aggregate_channel_performance()
            costs = payload.get("costs", 35.0)
            rev = payload.get("revenue", 210.0)
            cfo_dossier = self.growth_analyst.formulate_cfo_dossier(rev, costs)
            return {"status": "ok", "performance": perf, "cfo_dossier": cfo_dossier}

        elif action == "setup_antidetect_profile":
            acc = payload.get("account_name", "eva_growth_01")
            plat = payload.get("platform", "threads")
            return {"status": "ok", "profile": self.antidetect_mgr.create_isolated_profile(acc, plat)}

        else:
            return {
                "status": "error",
                "message": f"Unknown floor2 action: '{action}'",
                "available_actions": [
                    "create_viral_short",
                    "direct_short_script",
                    "source_broll_batch",
                    "generate_karaoke_captions",
                    "publish_content_campaign",
                    "render_short_video",
                    "generate_viral_thread",
                    "generate_pod_mockup",
                    "scout_affiliate_offers",
                    "analyze_pod_trends",
                    "aggregate_growth_metrics",
                    "setup_antidetect_profile"
                ]
            }
