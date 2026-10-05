"""
SYNDIKATE Content Factory — Viral Script & Scene Director.
Transforms high-level topics into production-ready, scene-by-scene blueprints
optimized for 9:16 vertical retention (TikTok, YouTube Shorts, Instagram Reels).
Implements the Hook-Retain-Reward structure with B-roll cues and SFX triggers.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)

# Deterministic six-scene template (Ukrainian). Durations are scaled to the
# requested length at render time; see ``_generate_fallback_template``.
TEMPLATE_SCENES = [
    {
        "scene_id": 1,
        "duration_sec": 3.0,
        "narration": "90% підприємців зливають гроші на непотрібний софт.",
        "broll_keywords": ["money burning", "laptop stress person"],
        "visual_action": "Rapid zoom on falling currency or frustrated founder",
        "sfx": "whoosh",
        "emphasis_words": ["90%", "зливають"]
    },
    {
        "scene_id": 2,
        "duration_sec": 3.5,
        "narration": "Ось як наш автономний холдинг SYNDICATE закриває операційку в нуль витрат:",
        "broll_keywords": ["cyberpunk server", "data analytics"],
        "visual_action": "Sleek dark server infrastructure with cyan neon lights",
        "sfx": "sub_bass",
        "emphasis_words": ["SYNDICATE", "нуль"]
    },
    {
        "scene_id": 3,
        "duration_sec": 4.0,
        "narration": "Замість підписок на 10 SaaS сервісів — власні локальні AI-агенти на одному сервері.",
        "broll_keywords": ["artificial intelligence brain", "code matrix"],
        "visual_action": "Multi-agent node graph connecting autonomously",
        "sfx": "pop",
        "emphasis_words": ["10 SaaS", "локальні"]
    },
    {
        "scene_id": 4,
        "duration_sec": 3.5,
        "narration": "Контент рендериться за секунди, фінанси рахуються без бухгалтера.",
        "broll_keywords": ["video timeline render", "fast digital clock"],
        "visual_action": "Accelerated timeline showing automated video assembly",
        "sfx": "ding",
        "emphasis_words": ["секунди", "без бухгалтера"]
    },
    {
        "scene_id": 5,
        "duration_sec": 4.0,
        "narration": "Перестань годувати чужі платформи. Будуй власну незалежну екосистему.",
        "broll_keywords": ["futuristic skyscraper", "city skyline night"],
        "visual_action": "Majestic drone shot of cyberpunk high-rise",
        "sfx": "impact",
        "emphasis_words": ["незалежну", "екосистему"]
    },
    {
        "scene_id": 6,
        "duration_sec": 3.0,
        "narration": "Повна схема архітектури холдингу вже у нашому каналі. Посилання в шапці.",
        "broll_keywords": ["smartphone telegram screen", "tap click screen"],
        "visual_action": "Close up of finger tapping join button",
        "sfx": "cash_register",
        "emphasis_words": ["архітектури", "в шапці"]
    }
]



class ScriptDirector:
    """Automated director for short-form video scripting and visual choreography."""

    def __init__(self, api_key: Optional[str] = None, model: str = "grok-beta"):
        self.api_key = api_key or os.getenv("XAI_API_KEY", "")
        self.model = model
        self.base_url = "https://api.x.ai/v1"

    async def generate_short_script(
        self,
        topic: str,
        niche: str = "ai_holding",
        target_duration_sec: int = 30,
        style: str = "hormozi",
        language: str = "uk"
    ) -> Dict[str, Any]:
        """
        Generate a high-retention vertical video script broken into 2.5-3.5 second scenes.
        Calculates optimal speech density (approx 2.3 - 2.5 words per second).
        """
        target_words = int(target_duration_sec * 2.4)

        system_prompt = (
            "You are an elite short-form video director and viral scriptwriter for TikTok, Reels, and YouTube Shorts. "
            "Your videos achieve >85% completion rates by following ruthless dopamine pacing:\n"
            "1. THE HOOK (0-3s): Stop the scroll immediately with a contrarian statement, shock metric, or visual paradox.\n"
            "2. RETENTION CHOREOGRAPHY: Scene cut every 2.0 to 3.5 seconds. No scene stays static.\n"
            "3. B-ROLL CUES: For every single scene, provide 2-3 specific English search keywords for stock footage.\n"
            "4. SOUND DESIGN: Trigger sound effects (whoosh, pop, ding, bass_drop, cash) on psychological transition points.\n"
            "5. NO AI FLUFF: Never say 'in this video', 'let's dive in', 'unleash', 'transform'. Use visceral, punchy phrasing.\n"
            "Return ONLY valid JSON matching the requested schema."
        )

        user_prompt = (
            f"Topic: {topic}\n"
            f"Niche: {niche}\n"
            f"Target Duration: {target_duration_sec} seconds (~{target_words} words)\n"
            f"Language: {language} (natural modern Ukrainian phrasing)\n"
            f"Style: {style} (high-energy, authoritative, Alex Hormozi punchiness)\n\n"
            "Output JSON format exactly:\n"
            "{\n"
            '  "title": "Viral Hook Title",\n'
            '  "hook_text": "First 3 seconds spoken text",\n'
            '  "target_duration_sec": 30,\n'
            '  "scenes": [\n'
            '    {\n'
            '      "scene_id": 1,\n'
            '      "duration_sec": 3.0,\n'
            '      "narration": "Text spoken in this exact scene",\n'
            '      "broll_keywords": ["server datacenter", "neon lights"],\n'
            '      "visual_action": "Fast push-in on glowing server rack",\n'
            '      "sfx": "whoosh",\n'
            '      "emphasis_words": ["80%", "бюджету"]\n'
            '    }\n'
            '  ],\n'
            '  "full_narration": "Complete voiceover text assembled",\n'
            '  "cta": "Call to action sentence",\n'
            '  "seo": {\n'
            '    "youtube_title": "SEO Optimized Title for Shorts",\n'
            '    "hashtags": ["#ai", "#automation", "#бізнес"],\n'
            '    "description": "Short video description with hook and link placeholder"\n'
            '  }\n'
            "}"
        )

        if not self.api_key or self.api_key == "PLACEHOLDER_UPDATE_ME":
            logger.info("script_director_fallback_template", topic=topic)
            return self._generate_fallback_template(
                topic, niche, target_duration_sec, language,
                reason="XAI_API_KEY is not configured",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.72,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            raw_json = data["choices"][0]["message"]["content"]
            try:
                parsed = json.loads(raw_json)
            except (json.JSONDecodeError, TypeError) as exc:
                logger.warning("grok_director_unparsable", error=str(exc))
                return self._generate_fallback_template(
                    topic, niche, target_duration_sec, language,
                    reason=f"grok returned unparsable script: {exc}",
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("grok_director_failed_using_fallback", error=str(exc))
            return self._generate_fallback_template(
                topic, niche, target_duration_sec, language,
                reason=f"grok request failed: {exc}",
            )

        if not isinstance(parsed.get("scenes"), list) or not parsed["scenes"]:
            return self._generate_fallback_template(
                topic, niche, target_duration_sec, language,
                reason="grok returned no scenes",
            )

        logger.info("viral_script_generated", title=parsed.get("title"), scenes=len(parsed["scenes"]))
        return {"status": "ok", "script": parsed, "model": self.model, "synthetic": False}

    def _generate_fallback_template(
        self,
        topic: str,
        niche: str,
        duration: int,
        lang: str,
        reason: str = "fallback template"
    ) -> Dict[str, Any]:
        """Deterministic blueprint used when Grok is unavailable.

        The template used to be returned with ``status: "ok"`` and no marker at
        all, and its six scenes always summed to 21s regardless of the
        requested duration — a 15s brief silently produced a 21s narration and
        the voiceover overran the video. Durations are now scaled to the
        requested length and the result is tagged ``synthetic: True``.
        """
        import copy

        scenes = copy.deepcopy(TEMPLATE_SCENES)
        total = sum(float(scene["duration_sec"]) for scene in scenes) or 1.0
        factor = max(0.1, float(duration) / total)
        for scene in scenes:
            scene["duration_sec"] = round(float(scene["duration_sec"]) * factor, 2)

        full_narration = " ".join(scene["narration"] for scene in scenes)

        script_data = {
            "title": f"Як заощадити 80% бюджету: Архітектура {topic}",
            "hook_text": scenes[0]["narration"],
            "target_duration_sec": duration,
            "scenes": scenes,
            "full_narration": full_narration,
            "cta": "Посилання на інфраструктурний шаблон у шапці профілю.",
            "seo": {
                "youtube_title": "Як AI-агенти замінюють 10 SaaS сервісів | Автономний Холдинг",
                "hashtags": ["#ai", "#автоматизація", "#syndicate", "#бізнес2026", "#saas", "#shorts"],
                "description": (
                    f"Розбір архітектури автономного контент-заводу та AI-холдингу SYNDICATE.\n"
                    f"Тема: {topic} | Ніша: {niche}\n"
                    "Деталі та відкритий код — у нашому Telegram."
                ),
            },
        }

        warnings = [f"script_not_generated_by_llm: {reason}"]
        if (lang or "uk").lower() not in ("uk", "ua", "ukrainian"):
            warnings.append("template_script_is_ukrainian_only")

        return {
            "status": "ok",
            "script": script_data,
            "model": "template-engine-v2",
            "synthetic": True,
            "warnings": warnings,
        }
