"""
SYNDIKATE Content Factory — Video Engine v2.0 (Autonomous Production Line).
Assembles multi-scene vertical short-form videos with dynamic B-roll cuts every 2.5-3.5s,
word-level animated karaoke captions, audio ducking, and sound effects.
Optimized for 16 vCPU threads on Contabo VPS with zero external SaaS fees.
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

from src.departments.content_factory.broll_scout import BRollScout
from src.departments.content_factory.caption_engine import CaptionEngine
from src.departments.content_factory.script_director import ScriptDirector

logger = structlog.get_logger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


class VideoEngineV2:
    """High-throughput multi-scene automated video producer."""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        broll_cache_dir: Optional[str] = None,
        captions_dir: Optional[str] = None,
        threads: int = 16
    ):
        from src.data_paths import data_dir, ensure_dir

        self.output_dir = ensure_dir("videos", output_dir)
        self.threads = threads
        self.ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe_bin = shutil.which("ffprobe") or "ffprobe"

        self.director = ScriptDirector()
        self.broll_scout = BRollScout(cache_dir=str(data_dir("broll_cache", broll_cache_dir)))
        self.caption_engine = CaptionEngine(output_dir=str(data_dir("captions", captions_dir)))

    async def _synthesize_voiceover(
        self,
        full_text: str,
        voice: str,
        temp_audio: Path,
        default_duration: float,
    ) -> "tuple[float, Optional[str]]":
        """Step 2 — Edge-TTS voiceover.

        Edge-TTS is a network service (speech.platform.bing.com). An unreachable
        endpoint used to propagate out of Floor 2 and fail the whole pipeline;
        fall back to a silent track so the render can continue without audio.
        Returns ``(audio_duration, tts_error)``.
        """
        audio_duration = float(default_duration)
        if not EDGE_TTS_AVAILABLE or not full_text.strip():
            logger.warning("edge_tts_unavailable_mocking_audio")
            self._create_dummy_audio(str(temp_audio), duration=audio_duration)
            return audio_duration, "edge_tts_not_installed" if not EDGE_TTS_AVAILABLE else None
        try:
            communicate = edge_tts.Communicate(full_text, voice, rate="+4%")
            await communicate.save(str(temp_audio))
            audio_duration = self._get_audio_duration(str(temp_audio)) or audio_duration
            return audio_duration, None
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "edge_tts_synthesis_unavailable",
                voice=voice,
                error=f"{type(exc).__name__}: {exc}",
            )
            self._create_dummy_audio(str(temp_audio), duration=audio_duration)
            return audio_duration, f"{type(exc).__name__}: {exc}"

    @staticmethod
    def _write_concat_file(broll_clips: List[Dict[str, Any]], concat_list_file: Path) -> List[str]:
        """Step 5 — build the FFmpeg concat list. Returns the warnings raised."""
        warnings: List[str] = []
        concat_lines = []
        for b_item in broll_clips:
            v_path = b_item.get("video_path")
            if v_path and Path(v_path).exists():
                # A literal quote in a path used to escape the concat line.
                safe_path = str(v_path).replace("\\", "/").replace("'", "'\\''")
                concat_lines.append(f"file '{safe_path}'")

        if not concat_lines:
            warnings.append("no_broll_footage")
        concat_list_file.write_text("\n".join(concat_lines), encoding="utf-8")
        return warnings

    def _build_ffmpeg_cmd(
        self,
        concat_list_file: Path,
        temp_audio: Path,
        ass_path: str,
        final_video_path: Path,
        audio_duration: float,
        bg_music: Optional[str],
    ) -> List[str]:
        """Step 6 — assemble the FFmpeg composite command."""
        escaped_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")
        ffmpeg_cmd = [
            self.ffmpeg_bin, "-y",
            "-threads", str(self.threads),
            "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
            "-i", str(temp_audio),
        ]

        if bg_music and Path(bg_music).exists():
            ffmpeg_cmd.extend(["-stream_loop", "-1", "-i", str(bg_music)])
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,setsar=1,ass='{escaped_ass}'[v];"
                f"[2:a]volume=0.14[bgm];"
                f"[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
            )
            ffmpeg_cmd.extend(["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]"])
        else:
            filter_str = (
                f"scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,setsar=1,ass='{escaped_ass}'"
            )
            ffmpeg_cmd.extend(["-vf", filter_str, "-map", "0:v", "-map", "1:a"])

        ffmpeg_cmd.extend([
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(audio_duration),
            str(final_video_path),
        ])
        return ffmpeg_cmd

    async def _run_ffmpeg(self, ffmpeg_cmd: List[str], warnings: List[str]) -> None:
        try:
            proc = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                warnings.append(f"ffmpeg_exit_{proc.returncode}")
                logger.warning("ffmpeg_render_finished_with_warnings", stderr=stderr.decode(errors="ignore")[:300])
        except FileNotFoundError:
            warnings.append("ffmpeg_not_installed")
            logger.info("ffmpeg_dry_run_environment")

    async def render_complete_short(
        self,
        topic: str,
        niche: str = "ai_holding",
        duration_sec: int = 30,
        voice: str = "uk-UA-PolinaNeural",
        output_filename: Optional[str] = None,
        bg_music: Optional[str] = None,
        caption_style: str = "hormozi_cyan"
    ) -> Dict[str, Any]:
        """
        Autonomous End-to-End Pipeline:
        1. Script & Scene Blueprint (Hook + 4-6 scenes + SFX + B-roll cues)
        2. Voiceover Synthesis (Edge-TTS)
        3. Word-Level Timestamp Extraction & Karaoke ASS Generation
        4. B-roll Stock Sourcing (Parallel Pexels/Cache fetch)
        5. FFmpeg Multi-Cut Assembly & Subtitle Burning
        """
        target_name = output_filename or f"short_{int(asyncio.get_event_loop().time())}.mp4"
        final_video_path = self.output_dir / target_name
        temp_audio = self.output_dir / f"vo_{final_video_path.stem}.mp3"
        concat_list_file = self.output_dir / f"concat_{final_video_path.stem}.txt"

        logger.info("content_pipeline_started", topic=topic, target=str(final_video_path))

        # --- STEP 1: Generate Viral Script Blueprint ---
        script_res = await self.director.generate_short_script(
            topic=topic,
            niche=niche,
            target_duration_sec=duration_sec
        )
        script_data = script_res.get("script", {})
        scenes = script_data.get("scenes", [])
        full_text = script_data.get("full_narration", "")

        # --- STEP 2: Synthesize Voiceover ---
        audio_duration, tts_error = await self._synthesize_voiceover(
            full_text, voice, temp_audio, duration_sec
        )

        # --- STEP 3: Generate Dynamic Word-Level Captions ---
        timed_words = self.caption_engine.generate_word_timestamps(full_text, audio_duration)
        ass_path = self.caption_engine.create_ass_karaoke_file(
            word_timestamps=timed_words,
            output_filename=f"captions_{final_video_path.stem}.ass",
            style_preset=caption_style
        )

        # --- STEP 4: Source Multi-Scene B-Roll Footage ---
        broll_clips = await self.broll_scout.fetch_broll_batch(scenes)

        # --- STEP 5 + 6: Concat list and FFmpeg composite ---
        warnings: List[str] = []
        if tts_error:
            warnings.append(f"voiceover_unavailable: {tts_error}")
        warnings.extend(self._write_concat_file(broll_clips, concat_list_file))

        ffmpeg_cmd = self._build_ffmpeg_cmd(
            concat_list_file, temp_audio, ass_path, final_video_path, audio_duration, bg_music
        )
        logger.info("ffmpeg_assembly_launched", threads=self.threads, duration=audio_duration)

        # An empty concat list would make FFmpeg concatenate nothing and exit
        # non-zero with a confusing error; skip straight to the honest status.
        if concat_list_file.read_text(encoding="utf-8").strip():
            await self._run_ffmpeg(ffmpeg_cmd, warnings)
        else:
            warnings.append("ffmpeg_skipped_no_input")

        # Only claim success when the artefact really exists. The old code
        # returned status "ok" even in a dry-run environment with no output.
        rendered = final_video_path.exists() and final_video_path.stat().st_size > 0
        if not rendered:
            warnings.append("output_file_missing")

        return {
            "status": "ok" if rendered else "error",
            "video_path": str(final_video_path),
            "audio_path": str(temp_audio),
            "captions_path": str(ass_path),
            "duration_sec": audio_duration,
            "scene_count": len(scenes),
            "script_title": script_data.get("title"),
            "seo_metadata": script_data.get("seo", {}),
            "warnings": warnings,
            "message": None if rendered else ("Video was not produced: " + "; ".join(warnings)),
        }

    def _get_audio_duration(self, audio_file: str) -> Optional[float]:
        """Probe exact audio duration in seconds using ffprobe."""
        cmd = [
            self.ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_file)
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
            return float(out)
        except Exception:
            return None

    def _create_dummy_audio(self, output_path: str, duration: float = 30.0) -> None:
        """Create silent placeholder MP3 if TTS is unavailable."""
        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", str(duration),
            "-c:a", "libmp3lame",
            str(output_path)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
