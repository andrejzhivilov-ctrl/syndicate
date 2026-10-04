"""
Video Prompt Enhancer — turns a rough idea into a cinematic, model-ready prompt
(Veo 3 / Kling / generic) with camera, lens, lighting, mood, audio and negatives.
Deterministic and provider-agnostic; the actual video API call lives elsewhere.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

STYLES: Dict[str, Dict[str, str]] = {
    "cinematic": {"lens": "35mm anamorphic", "lighting": "soft key light with warm rim light", "grade": "teal-orange film grade, subtle grain", "mood": "dramatic, immersive"},
    "documentary": {"lens": "50mm prime, handheld", "lighting": "natural available light", "grade": "neutral realistic color", "mood": "authentic, observational"},
    "tech_neon": {"lens": "24mm wide", "lighting": "cyan and violet neon, high contrast", "grade": "cool saturated cyberpunk grade", "mood": "futuristic, energetic"},
    "luxury_minimal": {"lens": "85mm macro, shallow depth of field", "lighting": "diffused studio softbox", "grade": "clean high-key, platinum highlights", "mood": "calm, premium"},
}
CAMERA_MOVES = {
    "push_in": "slow dolly push-in", "orbit": "smooth 180-degree orbit", "tracking": "steady tracking shot",
    "crane": "rising crane shot", "static": "locked-off tripod shot", "whip": "fast whip-pan transition",
}
NEGATIVES = ["text overlays", "watermark", "distorted hands", "extra fingers", "flicker", "jitter", "low resolution", "morphing faces"]
ASPECTS = {"9:16": "vertical 9:16 (Shorts/Reels)", "16:9": "horizontal 16:9", "1:1": "square 1:1"}


class VideoPromptEnhancer:
    def enhance(
        self,
        idea: str,
        style: str = "cinematic",
        camera: str = "push_in",
        duration_s: int = 8,
        aspect: str = "9:16",
        provider: str = "generic",
        dialogue: Optional[str] = None,
        subject: Optional[str] = None,
        camera_move: Optional[str] = None,
        lighting: Optional[str] = None,
        lens: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        idea = " ".join(idea.split())
        if len(idea) < 8:
            return {"status": "needs_more_detail", "missing": ["idea (at least a short sentence)"]}
        st = dict(STYLES.get(style, STYLES["cinematic"]))
        if lighting:
            st["lighting"] = lighting
        if lens:
            st["lens"] = lens
        camera = camera_move or camera
        move = CAMERA_MOVES.get(camera, camera)
        duration_s = max(2, min(int(duration_s), 30))
        aspect_desc = ASPECTS.get(aspect, ASPECTS["9:16"])

        parts = [
            f"{subject or idea}",
            f"Action: {idea}" if subject else "",
            f"Camera: {move}, {st['lens']}",
            f"Lighting: {st['lighting']}",
            f"Look: {st['grade']}",
            f"Mood: {st['mood']}",
            f"Format: {aspect_desc}, {duration_s} seconds, 24fps, 4K detail",
        ]
        if dialogue:
            parts.append(f'Audio: natural ambience; character says: "{dialogue}"')
        else:
            parts.append("Audio: subtle cinematic ambience, no speech")
        positive = ". ".join(p for p in parts if p) + "."

        warnings: List[str] = []
        if len(idea.split()) < 4:
            warnings.append("Ідея дуже коротка — модель домалює деталі сама.")
        if duration_s > 12 and provider == "veo3":
            warnings.append("Veo 3 стабільніший на кліпах до ~8–10 с; розбийте сцену на шоти.")

        payload: Dict[str, Any] = {"prompt": positive, "negative_prompt": ", ".join(NEGATIVES)}
        if provider == "veo3":
            payload.update({"aspect_ratio": aspect, "duration_seconds": min(duration_s, 10), "generate_audio": True})
        elif provider == "kling":
            payload.update({"aspect_ratio": aspect, "duration": "10" if duration_s > 5 else "5", "cfg_scale": 0.6})
        return {
            "status": "ok", "provider": provider, "style": style, "camera": camera,
            "prompt": positive, "negative_prompt": payload["negative_prompt"],
            "api_payload": payload, "warnings": warnings,
        }

    def shot_list(self, idea: str, shots: int = 3, **kw: Any) -> List[Dict[str, Any]]:
        """Split one idea into establishing / action / payoff shots."""
        roles = [("establishing", "static"), ("action", "tracking"), ("payoff", "push_in"), ("cutaway", "orbit")]
        out = []
        for i in range(max(1, min(shots, len(roles)))):
            role, cam = roles[i]
            out.append({"shot": i + 1, "role": role, **self.enhance(f"{role} shot: {idea}", camera=cam, **kw)})
        return out
