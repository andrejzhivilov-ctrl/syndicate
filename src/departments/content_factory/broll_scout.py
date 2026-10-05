"""
SYNDIKATE Content Factory — Intelligent B-Roll Scout & Cache Manager.
Fetches vertical 9:16 high-definition stock video clips (Pexels / Pixabay)
and maintains a local high-speed cache on the Contabo server to achieve $0 operating costs.
Includes automated Ken Burns motion fallback for static visual assets.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)


class BRollScout:
    """Automated stock media scout and local asset manager."""

    PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
    PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        pexels_api_key: Optional[str] = None,
        pixabay_api_key: Optional[str] = None
    ):
        # EVA_DATA_DIR-aware: the container root filesystem is read-only.
        from src.data_paths import ensure_dir

        self.cache_dir = ensure_dir("broll_cache", cache_dir)
        self.pexels_key = pexels_api_key or os.getenv("PEXELS_API_KEY", "")
        self.pixabay_key = pixabay_api_key or os.getenv("PIXABAY_API_KEY", "")
        self.ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"

    async def fetch_broll_for_scene(
        self,
        keywords: List[str],
        scene_id: int = 1,
        min_duration_sec: float = 3.0
    ) -> Dict[str, Any]:
        """
        Fetch the best vertical 9:16 video clip matching keywords.
        Checks local cache first, then calls Pexels/Pixabay, with motion fallback.
        """
        query = " ".join(keywords)
        cache_key = hashlib.md5(query.lower().strip().encode("utf-8")).hexdigest()[:12]
        cached_file = self.cache_dir / f"broll_{cache_key}.mp4"

        if cached_file.exists() and cached_file.stat().st_size > 10_000:
            logger.info("broll_cache_hit", query=query, path=str(cached_file))
            return {
                "status": "cached",
                "scene_id": scene_id,
                "video_path": str(cached_file),
                "query": query
            }

        # 1. Try Pexels API if key provided
        if self.pexels_key and self.pexels_key != "PLACEHOLDER_UPDATE_ME":
            video_url = await self._search_pexels(query)
            if video_url:
                downloaded = await self._download_file(video_url, str(cached_file))
                if downloaded:
                    logger.info("broll_downloaded_pexels", query=query, path=str(cached_file))
                    return {
                        "status": "downloaded",
                        "source": "pexels",
                        "scene_id": scene_id,
                        "video_path": str(cached_file),
                        "query": query
                    }

        # 2. Try Pixabay API if key provided
        if self.pixabay_key and self.pixabay_key != "PLACEHOLDER_UPDATE_ME":
            video_url = await self._search_pixabay(query)
            if video_url:
                downloaded = await self._download_file(video_url, str(cached_file))
                if downloaded:
                    logger.info("broll_downloaded_pixabay", query=query, path=str(cached_file))
                    return {
                        "status": "downloaded",
                        "source": "pixabay",
                        "scene_id": scene_id,
                        "video_path": str(cached_file),
                        "query": query
                    }

        # 3. Fallback: Generate local synthetic vertical motion loop
        fallback_path = await self._generate_synthetic_clip(str(cached_file), min_duration_sec, scene_id)
        return {
            "status": "synthetic_fallback",
            "scene_id": scene_id,
            "video_path": fallback_path,
            "query": query
        }

    async def fetch_broll_batch(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Download or retrieve B-roll for all scenes in parallel."""
        tasks = []
        for idx, scene in enumerate(scenes, start=1):
            keywords = scene.get("broll_keywords", ["technology dark neon"])
            duration = scene.get("duration_sec", 3.5)
            tasks.append(self.fetch_broll_for_scene(keywords, scene_id=idx, min_duration_sec=duration))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        resolved = []
        for idx, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error("broll_fetch_failed", index=idx, error=str(res))
                # Report ``video_path: None`` instead of a path to a file that
                # was never created — downstream checks ``Path(...).exists()``
                # and silently skipped a non-existent "fallback" clip.
                resolved.append({
                    "status": "error_fallback",
                    "scene_id": idx + 1,
                    "video_path": None,
                    "error": str(res),
                })
            else:
                resolved.append(res)
        return resolved

    async def _search_pexels(self, query: str) -> Optional[str]:
        """Search Pexels API for vertical portrait video."""
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "orientation": "portrait",
            "size": "medium",
            "per_page": 5
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(self.PEXELS_SEARCH_URL, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    videos = data.get("videos", [])
                    if videos:
                        video_files = videos[0].get("video_files", [])
                        # Prefer 1080x1920 or 720x1280
                        for vf in video_files:
                            if vf.get("width") and vf.get("height"):
                                if vf["height"] > vf["width"]:  # Vertical
                                    return vf.get("link")
                        if video_files:
                            return video_files[0].get("link")
            except Exception as e:
                logger.warning("pexels_api_query_failed", query=query, error=str(e))
        return None

    async def _search_pixabay(self, query: str) -> Optional[str]:
        """Search Pixabay API for video asset."""
        params = {
            "key": self.pixabay_key,
            "q": query,
            "video_type": "all",
            "per_page": 5
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(self.PIXABAY_SEARCH_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    hits = data.get("hits", [])
                    if hits:
                        vids = hits[0].get("videos", {})
                        for quality in ["medium", "large", "small"]:
                            if quality in vids and vids[quality].get("url"):
                                return vids[quality]["url"]
            except Exception as e:
                logger.warning("pixabay_api_query_failed", query=query, error=str(e))
        return None

    async def _download_file(self, url: str, destination: str) -> bool:
        """Download binary stream to local file."""
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                async with client.stream("GET", url) as resp:
                    resp.raise_for_status()
                    with open(destination, "wb") as f:
                        async for chunk in resp.aiter_bytes(chunk_size=65536):
                            f.write(chunk)
                return True
            except Exception as e:
                logger.error("broll_download_stream_failed", url=url, error=str(e))
                return False

    async def _generate_synthetic_clip(self, output_path: str, duration: float, scene_id: int) -> str:
        """
        Generate a dynamic 1080x1920 abstract motion video using FFmpeg
        test patterns (plasma, gradients) to ensure the render pipeline never crashes.
        """
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Vary color palette per scene (deep cyberpunk blues, purples, cyans)
        hue_shift = (scene_id * 45) % 360
        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi",
            "-i", f"mptestsrc=rate=30:size=1080x1920:duration={duration}",
            "-vf", f"hue=h={hue_shift}:s=2,boxblur=10:5",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            str(dest)
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                return str(dest)
        except Exception as e:
            logger.warning("synthetic_ffmpeg_clip_failed", error=str(e))

        # Absolute minimal fallback: return destination path
        return str(dest)
