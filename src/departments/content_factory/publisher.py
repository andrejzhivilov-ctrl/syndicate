"""
SYNDIKATE Content Factory — Multi-Channel Social Media Publisher.
Dispatches completed vertical video assets to YouTube Shorts, TikTok,
and the SYNDIKATE Telegram Broadcast Channel.
Enforces Sentinel safety checks and rate limits.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)


class ContentPublisher:
    """Dispatches media to video sharing platforms and broadcast channels."""

    def __init__(
        self,
        telegram_bot_token: Optional[str] = None,
        telegram_channel_id: Optional[str] = None,
        youtube_credentials_path: Optional[str] = None
    ):
        self.tg_token = telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.tg_channel = telegram_channel_id or os.getenv("TELEGRAM_CHANNEL_ID", "@syndicate_holding")
        self.yt_creds = youtube_credentials_path or os.getenv("YOUTUBE_CREDENTIALS_PATH", "credentials/youtube.json")

    async def publish_to_telegram(
        self,
        video_path: str,
        caption: str,
        parse_mode: str = "Markdown"
    ) -> Dict[str, Any]:
        """Post short video directly to official Telegram channel."""
        v_file = Path(video_path)
        if not v_file.exists():
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        if not self.tg_token or self.tg_token == "PLACEHOLDER_UPDATE_ME":
            # Nothing was sent. The old code returned "mock_success", so the
            # campaign log recorded a published post that never left the box.
            logger.info("telegram_publish_skipped_no_token", channel=self.tg_channel, video=str(v_file))
            return {
                "status": "not_published",
                "published": False,
                "platform": "telegram",
                "channel": self.tg_channel,
                "video": str(v_file),
                "reason": "TELEGRAM_BOT_TOKEN is not configured",
                "message": "Telegram post skipped: no active bot token",
            }

        url = f"https://api.telegram.org/bot{self.tg_token}/sendVideo"
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                with open(str(v_file), "rb") as f:
                    files = {"video": (v_file.name, f, "video/mp4")}
                    data = {
                        "chat_id": self.tg_channel,
                        "caption": caption[:1024],  # Telegram max caption limit
                        "parse_mode": parse_mode,
                        "supports_streaming": True
                    }
                    resp = await client.post(url, data=data, files=files)
                    resp.raise_for_status()
                    res_data = resp.json()
                    message_id = res_data.get("result", {}).get("message_id")
                    logger.info("telegram_video_published", message_id=message_id, channel=self.tg_channel)
                    return {
                        "status": "ok",
                        "published": True,
                        "platform": "telegram",
                        "message_id": message_id,
                        "channel": self.tg_channel
                    }
            except Exception as e:
                logger.error("telegram_publish_failed", error=str(e))
                return {"status": "error", "published": False, "platform": "telegram", "message": str(e)}

    async def schedule_youtube_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Upload vertical video to YouTube Shorts using YouTube Data API v3.
        Appends #Shorts to title and description for mandatory algorithmic routing.
        """
        safe_title = title if "#Shorts" in title else f"{title} #Shorts"
        safe_tags = list(set(tags + ["Shorts", "YouTubeShorts", "Syndicate"]))

        if not Path(self.yt_creds).exists():
            logger.info("youtube_shorts_mock_schedule", title=safe_title)
            return {
                "status": "not_published",
                "published": False,
                "platform": "youtube_shorts",
                "title": safe_title,
                "tags": safe_tags,
                "video_path": video_path,
                "reason": "YOUTUBE_CREDENTIALS_PATH not found",
                "message": "YouTube upload skipped: no OAuth credentials token",
            }

        # Credentials are present but the resumable Data API v3 upload is not
        # implemented yet. The old code returned status "ok" with a fabricated
        # "MOCK_YT_ID_1048", so the campaign log claimed a video had been
        # published when nothing was ever sent to YouTube.
        logger.warning("youtube_shorts_upload_not_implemented", title=safe_title)
        return {
            "status": "not_implemented",
            "published": False,
            "platform": "youtube_shorts",
            "title": safe_title,
            "video_id": None,
            "message": (
                "YouTube Data API v3 resumable upload is not implemented yet; "
                "the video was NOT published."
            ),
        }

    async def dispatch_full_campaign(
        self,
        video_path: str,
        seo_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Broadcast video across all configured channels."""
        title = seo_metadata.get("youtube_title", "SYNDIKATE Autonomous System")
        desc = seo_metadata.get("description", "Automated holding insights.")
        tags = seo_metadata.get("hashtags", ["#ai", "#syndicate"])

        tg_caption = f"🎬 *{title}*\n\n{desc}\n\n{' '.join(tags)}"

        results = {}
        # 1. Telegram
        results["telegram"] = await self.publish_to_telegram(video_path, caption=tg_caption)
        # 2. YouTube Shorts
        results["youtube_shorts"] = await self.schedule_youtube_short(video_path, title, desc, tags)

        # The old code always reported "ok", so a campaign where every channel
        # failed looked identical to a successful one.
        statuses = {r.get("status") for r in results.values()}
        if statuses and statuses <= {"ok"}:
            campaign_status = "ok"
        elif "ok" in statuses:
            campaign_status = "partial"
        elif statuses <= {"not_implemented", "not_published"}:
            # Channels were skipped or unimplemented — nothing was published,
            # and that is not a failure of the pipeline either.
            campaign_status = "not_published"
        else:
            campaign_status = "error"

        return {
            "status": campaign_status,
            "campaign_results": results,
            "published_platforms": [k for k, r in results.items() if r.get("published")],
            "published": any(r.get("published") for r in results.values()),
        }
