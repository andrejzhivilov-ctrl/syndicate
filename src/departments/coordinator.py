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

    def __init__(self, config: Optional[Dict[str, Any]] = None, vault_client: Any = None):
        self.config = config or {}
        self._vault = vault_client
        self.video_producer = VideoProducer()
        self.video_engine_v2 = VideoEngineV2()
        self.script_director = ScriptDirector(vault_client=vault_client)
        self.broll_scout = BRollScout(vault_client=vault_client)
        self.caption_engine = CaptionEngine()
        self.publisher = ContentPublisher(vault_client=vault_client)
        self.grok_writer = GrokWriter(vault_client=vault_client)
        self.mockup_studio = MockupStudio()
        self.affiliate_scout = AffiliateScout()
        self.pod_analyzer = PODAnalyzer()
        self.growth_analyst = GrowthAnalyst()
        self.policy_sentinel = PolicySentinel()
        self._action_map = self._build_action_map()

    async def _act_render_short_video(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        broll = payload.get("broll_video", "media/templates/abstract_loop.mp4")
        script = payload.get("script_text", "Ось топ-3 інструменти для автоматизації бізнесу у 2026 році.")
        filename = payload.get("output_filename", "short_render.mp4")
        voice = payload.get("voice")
        return await self.video_producer.render_video(broll, script, filename, voice=voice)

    async def _act_create_viral_short(self, payload: Dict[str, Any]) -> Dict[str, Any]:
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

    async def _act_direct_short_script(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", "Автоматизація бізнесу без SaaS витрат")
        niche = payload.get("niche", "ai_holding")
        duration = payload.get("duration_sec", 30)
        return await self.script_director.generate_short_script(topic, niche, target_duration_sec=duration)

    async def _act_source_broll_batch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        scenes = payload.get("scenes", [])
        return {"status": "ok", "clips": await self.broll_scout.fetch_broll_batch(scenes)}

    async def _act_generate_karaoke_captions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "")
        duration = payload.get("duration_sec", 30.0)
        timed_words = self.caption_engine.generate_word_timestamps(text, duration)
        style = payload.get("style", "hormozi_cyan")
        ass_path = self.caption_engine.create_ass_karaoke_file(timed_words, style_preset=style)
        return {"status": "ok", "ass_path": ass_path, "timed_words_count": len(timed_words)}

    async def _act_publish_content_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        video_path = payload.get("video_path", "")
        metadata = payload.get("seo_metadata", {})
        return await self.publisher.dispatch_full_campaign(video_path, metadata)

    async def _act_generate_viral_thread(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", "Lean AI holding automation")
        niche = payload.get("niche", "saas_affiliate")
        cta = payload.get("target_cta")
        return await self.grok_writer.generate_thread(topic, niche, target_cta=cta)

    async def _act_generate_pod_mockup(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        artwork = payload.get("artwork_path", "media/art/cyber_skull.png")
        preset = payload.get("preset", "tshirt_front")
        # Compliance check first!
        safe, violations = self.policy_sentinel.check_design_compliance(artwork, [preset])
        if not safe:
            return {"status": "veto_blocked", "reason": violations}
        return self.mockup_studio.composite_artwork(artwork, preset=preset)

    async def _act_scout_affiliate_offers(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        category = payload.get("category")
        return {"status": "ok", "offers": self.affiliate_scout.scout_top_offers(category)}

    async def _act_analyze_pod_trends(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok", "niches": self.pod_analyzer.scan_niches()}

    async def _act_aggregate_growth_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # No fabricated defaults: channel counters come from the caller and
        # revenue/costs must come from the ledger. Defaulting them produced
        # a RESTRICTED_EXECUTIVE_FINANCE dossier with invented money.
        perf = self.growth_analyst.aggregate_channel_performance(
            channels=payload.get("channels"),
            period=payload.get("period", "Last 7 Days"),
        )
        cfo_dossier = self.growth_analyst.formulate_cfo_dossier(
            payload.get("revenue"), payload.get("costs")
        )
        return {"status": "ok", "performance": perf, "cfo_dossier": cfo_dossier}

    async def _act_setup_antidetect_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Policy: no anti-detection / fingerprint-evasion tooling. Accounts the holding
        # operates must be openly its own and comply with platform rules; AI-generated
        # publications carry a disclosure. The profile manager is intentionally not wired.
        return {
            "status": "refused",
            "reason": "antidetect_profiles_not_permitted_by_policy",
            "alternative": "Use the platform's official API / business account with a disclosed AI label.",
        }

    def _build_action_map(self) -> Dict[str, Any]:
        """Action -> handler. Replaces a 12-branch if/elif chain."""
        return {
            "render_short_video": self._act_render_short_video,
            "create_viral_short": self._act_create_viral_short,
            "direct_short_script": self._act_direct_short_script,
            "source_broll_batch": self._act_source_broll_batch,
            "generate_karaoke_captions": self._act_generate_karaoke_captions,
            "publish_content_campaign": self._act_publish_content_campaign,
            "generate_viral_thread": self._act_generate_viral_thread,
            "generate_pod_mockup": self._act_generate_pod_mockup,
            "scout_affiliate_offers": self._act_scout_affiliate_offers,
            "analyze_pod_trends": self._act_analyze_pod_trends,
            "aggregate_growth_metrics": self._act_aggregate_growth_metrics,
            "setup_antidetect_profile": self._act_setup_antidetect_profile,
        }

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task based on action."""
        action = payload.get("action", "")
        logger.info("floor2_dispatch", action=action)

        handler = self._action_map.get(action)
        if handler is None:
            return {
                "status": "error",
                "message": f"Unknown floor2 action: '{action}'",
                "available_actions": sorted(self._action_map),
            }
        return await handler(payload)

