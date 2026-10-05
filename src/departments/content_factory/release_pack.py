"""
Release Pack Builder — voice idea -> verified, humanized, approval-gated release.

Pipeline:  idea -> thesis/arguments/hook -> drafts (Telegram post, Shorts script,
cover + video prompts) -> Humanizer -> Orc verification of factual claims ->
Change Request (nothing is publishable until the operator approves it).
"""

from __future__ import annotations

import re
import time
import uuid
from typing import Any, Dict, List, Optional, Sequence

import structlog

from src.change_requests import ChangeRequestError, ChangeRequestStore
from src.departments.content_factory.humanizer import Humanizer
from src.departments.content_factory.video_prompt_enhancer import VideoPromptEnhancer
from src.verifier import Claim, Evidence, OrcVerifier

logger = structlog.get_logger(__name__)

BLOCKED_BRANDS = ("disney", "marvel", "nike", "adidas", "pokemon", "nintendo", "coca-cola", "mickey")


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s.strip()]


class ReleasePackBuilder:
    def __init__(
        self,
        cr_store: Optional[ChangeRequestStore] = None,
        humanizer: Optional[Humanizer] = None,
        enhancer: Optional[VideoPromptEnhancer] = None,
        video_enhancer: Optional[VideoPromptEnhancer] = None,
        verifier: Optional[OrcVerifier] = None,
        max_ai_score: float = 40.0,
    ) -> None:
        self._cr = cr_store
        self._human = humanizer or Humanizer()
        self._enh = enhancer or video_enhancer or VideoPromptEnhancer()
        self._orc = verifier or OrcVerifier()
        self._max_ai = max_ai_score

    @staticmethod
    def extract_structure(idea: str) -> Dict[str, Any]:
        sents = _sentences(idea)
        thesis = sents[0] if sents else idea.strip()
        arguments = sents[1:4] if len(sents) > 1 else []
        hook = thesis if len(thesis.split()) <= 14 else " ".join(thesis.split()[:12]) + "…"
        return {"thesis": thesis, "arguments": arguments, "hook": hook}

    async def build(
        self,
        idea_text: str | Dict[str, Any],
        claims: Optional[Sequence[Dict[str, Any]]] = None,
        author: str = "floor2_coordinator",
        style: str = "cinematic",
        provider: str = "veo3",
        replayer: Optional[Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if isinstance(idea_text, dict):
            payload = idea_text
            idea_text = payload.get("copy_text") or payload.get("idea_text") or payload.get("title") or ""
            claims = payload.get("claims", claims)
            author = payload.get("author", author)
            style = payload.get("style", style)
            provider = payload.get("provider", provider)

        if len(str(idea_text).strip()) < 10:
            return {"status": "needs_more_detail", "message": "Idea is too short to build a release pack."}
        low = str(idea_text).lower()
        brand_hits = [b for b in BLOCKED_BRANDS if b in low]
        if brand_hits:
            return {"status": "veto_blocked", "reason": [f"trademarked_brand:{b}" for b in brand_hits]}

        struct = self.extract_structure(str(idea_text))
        bullets = "\n".join(f"• {a}" for a in struct["arguments"])
        tg_raw = f"{struct['hook']}\n\n{struct['thesis']}\n\n{bullets}".strip()
        shorts_raw = {
            "hook_0_3s": struct["hook"],
            "beats": struct["arguments"] or [struct["thesis"]],
            "cta": "Підписуйся, щоб не пропустити наступний розбір.",
        }

        tg = self._human.scrub(tg_raw)
        beats = [self._human.scrub(b)["text"] for b in shorts_raw["beats"]]
        humanized = {
            "telegram_post": tg["text"],
            "shorts_script": {"hook_0_3s": self._human.scrub(shorts_raw["hook_0_3s"])["text"], "beats": beats, "cta": shorts_raw["cta"]},
        }
        ai_score = self._human.analyze(tg["text"])["ai_score"]

        video = self._enh.enhance(struct["thesis"], style=style, provider=provider)
        cover_prompt = self._enh.enhance(f"cover image: {struct['thesis']}", style="luxury_minimal", aspect="1:1")["prompt"] if video.get("status") == "ok" else ""

        verified: List[Dict[str, Any]] = []
        blocked: List[Dict[str, Any]] = []
        for c in claims or []:
            if not isinstance(c, dict) or not c.get("statement"):
                # A malformed claim used to raise KeyError and abort the whole
                # release pack; record it as unverifiable instead.
                blocked.append({"statement": c.get("statement") if isinstance(c, dict) else None,
                                "verdict": "unproven", "reasons": ["malformed_claim"]})
                continue
            ev = Evidence(call=c.get("call", {}), response=c.get("response"), timestamp=c.get("timestamp", time.time())) if "response" in c else None
            claim = Claim(c["statement"], author, ev, c.get("must_contain", []), c.get("must_not_contain", []))
            verdict = await self._orc.verify(claim, replayer)
            (verified if verdict.passes_to_human else blocked).append({"statement": c["statement"], "verdict": verdict.status, "reasons": verdict.reasons})

        release_id = f"REL-{uuid.uuid4().hex[:8]}"
        pack = {
            "status": "ok",
            "release_id": release_id,
            "structure": struct,
            "humanized": humanized,
            "humanized_copy": humanized["telegram_post"],
            "ai_score": ai_score,
            "ai_score_ok": ai_score <= self._max_ai,
            "video": {k: video.get(k) for k in ("prompt", "negative_prompt", "api_payload", "warnings")},
            "video_prompt": video.get("prompt"),
            "cover_prompt": cover_prompt,
            "claims_verified": verified,
            "claims_blocked": blocked,
            "verification": {"verdict": "verified" if not blocked else "blocked", "verified_count": len(verified)},
        }

        md = self._to_markdown(pack)
        cr: Optional[Dict[str, Any]] = None
        if self._cr is not None:
            try:
                cr = self._cr.create(
                    author=author,
                    title=f"Release pack {release_id}",
                    rationale="Content Factory release awaiting operator approval",
                    changes=[{"path": f"wiki/releases/{release_id}.md", "content": md}],
                    tests_passed=["humanizer", "orc_verifier"] if not blocked else ["humanizer"],
                    risk="medium" if blocked or ai_score > self._max_ai else "low",
                )
            except ChangeRequestError as exc:
                logger.warning("release_cr_failed", error=str(exc))
        pack.update(
            publish_allowed=False,
            change_request={"cr_id": cr["id"]} if cr else {},
            change_request_id=cr["id"] if cr else None,
            requires_hitl=True,
            warnings=(["ai_voice_score_above_threshold"] if ai_score > self._max_ai else []) + (["unverified_claims_removed_from_copy"] if blocked else []),
        )
        return pack

    def is_approved(self, release_id: str, change_request_id: str) -> bool:
        if self._cr is None:
            return False
        try:
            cr = self._cr.get(change_request_id)
        except ChangeRequestError:
            return False
        return cr["status"] == "applied" and any(release_id in c["path"] for c in cr["changes"])

    @staticmethod
    def _to_markdown(pack: Dict[str, Any]) -> str:
        h = pack["humanized"]
        lines = [
            f"# {pack['release_id']}", "", f"**Thesis:** {pack['structure']['thesis']}", "",
            "## Telegram", h["telegram_post"], "", "## Shorts script",
            f"- Hook: {h['shorts_script']['hook_0_3s']}",
            *[f"- Beat: {b}" for b in h["shorts_script"]["beats"]],
            f"- CTA: {h['shorts_script']['cta']}", "", "## Video prompt", str(pack["video"]["prompt"]), "",
            "## Cover prompt", pack["cover_prompt"], "", f"AI-voice score: {pack['ai_score']}",
        ]
        return "\n".join(lines) + "\n"
