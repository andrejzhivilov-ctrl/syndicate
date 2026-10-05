"""
SYNDIKAT Content Factory — Local Video Producer.
Renders 9:16 vertical short-form videos (TikTok, YouTube Shorts, Reels)
using local Edge-TTS (free natural voiceover) and local multi-threaded FFmpeg.
Runs at $0 marginal cost on Contabo 16-core VPS.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("edge_tts not installed. Voice synthesis fallback will be used.")


class VideoProducer:
    """Automated video production worker for short-form content."""

    DEFAULT_VOICES = {
        "uk": "uk-UA-PolinaNeural",
        "uk_male": "uk-UA-OstapNeural",
        "en": "en-US-ChristopherNeural",
        "en_female": "en-US-JennyNeural",
        "es": "es-ES-AlvaroNeural",
        "de": "de-DE-ConradNeural",
    }

    def __init__(self, output_dir: Optional[str] = None, font_path: Optional[str] = None):
        # ``EVA_DATA_DIR`` keeps renders writable when the container root fs is read-only.
        from src.data_paths import ensure_dir

        self.output_dir = ensure_dir("videos", output_dir)
        self.font_path = font_path
        self.ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"

    async def generate_voiceover(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        volume: str = "+0%"
    ) -> Dict[str, Any]:
        """Generate high-quality natural voiceover using free Microsoft Edge-TTS."""
        if not EDGE_TTS_AVAILABLE:
            return {"status": "error", "message": "edge-tts library not available"}

        if not text or not text.strip():
            return {"status": "error", "message": "Empty script: nothing to synthesise."}

        selected_voice = voice or self.DEFAULT_VOICES.get("uk", "uk-UA-PolinaNeural")
        audio_path = Path(output_audio_path)
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Edge-TTS is a network service (speech.platform.bing.com). An unreachable
        # endpoint used to propagate out of Floor 2 and fail the whole task;
        # degrade to a structured error so the coordinator can fall back.
        try:
            communicate = edge_tts.Communicate(text, selected_voice, rate=rate, volume=volume)
            await communicate.save(str(audio_path))
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "voiceover_synthesis_failed",
                path=str(audio_path),
                voice=selected_voice,
                error=f"{type(exc).__name__}: {exc}",
            )
            return {
                "status": "error",
                "message": f"Edge-TTS synthesis unavailable: {type(exc).__name__}: {exc}",
            }

        logger.info("voiceover_generated", path=str(audio_path), voice=selected_voice, length=len(text))
        return {
            "status": "ok",
            "audio_path": str(audio_path),
            "voice": selected_voice,
            "text_length": len(text)
        }

    def generate_srt(self, segments: List[Dict[str, Any]], output_srt_path: str) -> str:
        """
        Generate SubRip (.srt) subtitle file.
        segments format: [{"start": 0.0, "end": 2.5, "text": "Привіт, друзі!"}, ...]
        """
        srt_path = Path(output_srt_path)
        srt_path.parent.mkdir(parents=True, exist_ok=True)

        def format_time(seconds: float) -> str:
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

        lines = []
        for idx, seg in enumerate(segments, start=1):
            start_str = format_time(seg.get("start", 0.0))
            end_str = format_time(seg.get("end", 2.0))
            text = seg.get("text", "")
            lines.append(f"{idx}\n{start_str} --> {end_str}\n{text}\n")

        content = "\n".join(lines)
        srt_path.write_text(content, encoding="utf-8")
        return str(srt_path)

    def build_ffmpeg_command(
        self,
        broll_video: str,
        voiceover_audio: str,
        output_mp4: str,
        srt_subtitles: Optional[str] = None,
        bg_music: Optional[str] = None,
        duration: Optional[float] = None,
        target_resolution: str = "1080x1920"
    ) -> List[str]:
        """
        Construct optimal multi-threaded FFmpeg command for 9:16 vertical video.
        Uses 16 CPU threads for maximum throughput on Contabo VPS.
        """
        width, height = target_resolution.split("x")
        cmd = [
            self.ffmpeg_bin, "-y",
            "-threads", "16",
            "-stream_loop", "-1",
            "-i", str(broll_video),
            "-i", str(voiceover_audio),
        ]

        if bg_music and Path(bg_music).exists():
            cmd.extend(["-stream_loop", "-1", "-i", str(bg_music)])
            # Filter complex with audio mixing: duck bg music by -18dB under voiceover
            filter_complex = (
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1[v];"
                f"[2:a]volume=0.15[bgm];"
                f"[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
            )
            cmd.extend(["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]"])
        else:
            filter_str = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1"
            )
            if srt_subtitles and Path(srt_subtitles).exists():
                escaped_srt = str(srt_subtitles).replace("\\", "/").replace(":", "\\:")
                filter_str += f",subtitles='{escaped_srt}':force_style='FontSize=22,FontName=Impact,Outline=2,PrimaryColour=&H0000FFFF'"
            cmd.extend(["-vf", filter_str, "-map", "0:v", "-map", "1:a"])

        cmd.extend([
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
        ])

        if duration:
            cmd.extend(["-t", str(duration)])

        cmd.append(str(output_mp4))
        return cmd

    async def render_video(
        self,
        broll_video: str,
        script_text: str,
        output_filename: str,
        voice: Optional[str] = None,
        bg_music: Optional[str] = None
    ) -> Dict[str, Any]:
        """End-to-end video synthesis pipeline."""
        output_mp4 = self.output_dir / output_filename
        temp_audio = self.output_dir / f"temp_vo_{output_mp4.stem}.mp3"

        # 1. Synthesize voiceover
        vo_res = await self.generate_voiceover(script_text, str(temp_audio), voice=voice)
        if vo_res.get("status") != "ok":
            return vo_res

        # 2. Build FFmpeg command
        cmd = self.build_ffmpeg_command(
            broll_video=broll_video,
            voiceover_audio=str(temp_audio),
            output_mp4=str(output_mp4),
            bg_music=bg_music
        )

        logger.info("executing_ffmpeg_render", output=str(output_mp4), cmd=" ".join(cmd[:10]) + "...")

        # 3. Execute or mock if dry run
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logger.warning("ffmpeg_render_error", stderr=stderr.decode(errors="ignore")[:300])
                return {
                    "status": "warning",
                    "message": "FFmpeg completed with errors or mock environment",
                    "command": " ".join(cmd),
                    "output_file": str(output_mp4)
                }
        except FileNotFoundError:
            logger.info("ffmpeg_not_in_system_path_dryrun", command=" ".join(cmd))
            return {
                "status": "dry_run",
                "message": "FFmpeg command constructed successfully (binary not installed in local dev)",
                "command": " ".join(cmd),
                "audio_ready": str(temp_audio),
                "output_file": str(output_mp4)
            }

        return {
            "status": "ok",
            "video_path": str(output_mp4),
            "audio_path": str(temp_audio)
        }
