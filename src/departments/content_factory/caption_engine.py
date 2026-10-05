"""
SYNDIKATE Content Factory — Dynamic Word-Level Caption & Karaoke Engine.
Generates Advanced SubStation Alpha (.ass) animated subtitles featuring
Alex Hormozi-style active word pop, glowing strokes, and multi-color emphasis.
Renders natively in FFmpeg at 200+ FPS without frame-by-frame Python re-encoding.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class CaptionEngine:
    """Specialized subtitle generator for high-retention vertical short-form videos."""

    # Presets for subtitle aesthetics
    STYLES = {
        "hormozi_cyan": {
            "fontname": "Montserrat",
            "fontsize": 68,
            "primary_color": "&H00FFFFFF",     # White (inactive words)
            "active_color": "&H00FFFF00",      # Vibrant Cyan BGR (&H00FFFF00 in ASS format)
            "outline_color": "&H00000000",     # Deep Black Outline
            "back_color": "&H80000000",        # Semi-transparent shadow
            "bold": 1,
            "outline": 5.0,
            "shadow": 3.0,
            "alignment": 2,                    # Bottom-center
            "margin_v": 480,                   # Safe zone above TikTok/Reels navigation UI
        },
        "hormozi_yellow": {
            "fontname": "Impact",
            "fontsize": 72,
            "primary_color": "&H00FFFFFF",
            "active_color": "&H0000FFFF",      # Vibrant Gold / Yellow
            "outline_color": "&H00000000",
            "back_color": "&H80000000",
            "bold": 1,
            "outline": 5.0,
            "shadow": 3.0,
            "alignment": 2,
            "margin_v": 480,
        },
        "minimal_cyber": {
            "fontname": "Arial",
            "fontsize": 60,
            "primary_color": "&H00E2E8F0",
            "active_color": "&H00FF3B30",      # Electric Blue / Neon
            "outline_color": "&H000F172A",
            "back_color": "&H60000000",
            "bold": 1,
            "outline": 4.0,
            "shadow": 2.0,
            "alignment": 2,
            "margin_v": 460,
        }
    }

    def __init__(self, output_dir: Optional[str] = None):
        from src.data_paths import ensure_dir

        self.output_dir = ensure_dir("captions", output_dir)

    def generate_word_timestamps(
        self,
        full_text: str,
        total_audio_duration_sec: float
    ) -> List[Dict[str, Any]]:
        """
        Estimate high-accuracy word-level timestamps based on phonetic length
        and punctuation pauses when local Whisper model is not loaded.
        """
        words = full_text.strip().split()
        if not words:
            return []

        # Weigh each word by character count + punctuation pause
        weights = []
        for w in words:
            weight = max(1, len(w))
            if w.endswith((".", "!", "?")):
                weight += 4.5  # Sentence pause
            elif w.endswith((",", ";", ":", "—", "-")):
                weight += 2.5  # Clause pause
            weights.append(weight)

        total_weight = sum(weights)
        time_per_weight = total_audio_duration_sec / total_weight

        timed_words = []
        current_time = 0.0

        for w, weight in zip(words, weights, strict=False):
            duration = weight * time_per_weight
            start_time = current_time
            end_time = current_time + (duration * 0.92)  # Slight gap between words
            timed_words.append({
                "word": w,
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "duration": round(end_time - start_time, 2)
            })
            current_time += duration

        return timed_words

    def group_words_into_lines(
        self,
        word_timestamps: List[Dict[str, Any]],
        words_per_line: int = 3
    ) -> List[Dict[str, Any]]:
        """Group word timestamps into punchy, readable phrases (2-4 words per display)."""
        lines = []
        words_per_line = max(1, int(words_per_line))
        for i in range(0, len(word_timestamps), words_per_line):
            chunk = word_timestamps[i:i + words_per_line]
            if not chunk:
                continue
            line_start = chunk[0]["start"]
            line_end = chunk[-1]["end"]
            lines.append({
                "start": line_start,
                "end": line_end,
                "words": chunk,
                "text": " ".join(c["word"] for c in chunk)
            })
        return lines

    def create_ass_karaoke_file(
        self,
        word_timestamps: List[Dict[str, Any]],
        output_filename: str = "styled_captions.ass",
        style_preset: str = "hormozi_cyan",
        words_per_phrase: int = 3
    ) -> str:
        """
        Build production-grade .ass subtitle file with karaoke color transitions.
        FFmpeg burns this directly with: -vf "ass=styled_captions.ass"
        """
        # Only the bare filename is honoured: a caller-supplied path separator
        # would write outside the captions directory.
        out_path = self.output_dir / Path(output_filename).name
        if style_preset in self.STYLES:
            style = self.STYLES[style_preset]
        else:
            logger.warning("ass_unknown_style_preset", preset=style_preset, fallback="hormozi_cyan")
            style = self.STYLES["hormozi_cyan"]

        def sec_to_ass_time(sec: float) -> str:
            """Seconds -> ``H:MM:SS.cc``.

            The old version computed the centiseconds from the fractional part
            alone, so 1.999s rounded up to ``0:00:01.100`` — an invalid ASS
            timestamp that libass/FFmpeg rejects.
            """
            total_cs = max(0, int(round(float(sec) * 100)))
            hrs, rem = divmod(total_cs, 3_600_00)
            mins, rem = divmod(rem, 6_000)
            secs, centisecs = divmod(rem, 100)
            return f"{hrs:d}:{mins:02d}:{secs:02d}.{centisecs:02d}"

        # Header for 1080x1920 vertical canvas
        header = f"""[Script Info]
Title: SYNDIKATE Dynamic Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['fontname']},{style['fontsize']},{style['primary_color']},{style['active_color']},{style['outline_color']},{style['back_color']},{style['bold']},0,0,0,100,100,0,0,1,{style['outline']},{style['shadow']},{style['alignment']},80,80,{style['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        phrases = self.group_words_into_lines(word_timestamps, words_per_line=max(1, int(words_per_phrase)))
        events = []

        for phrase in phrases:
            start_str = sec_to_ass_time(phrase["start"])
            end_str = sec_to_ass_time(phrase["end"])

            # Build karaoke timing tags: {\k<duration_in_centiseconds>}Word
            # Active word receives bright color pop
            karaoke_parts = []
            for w in phrase["words"]:
                centisecs = max(10, int(w["duration"] * 100))
                clean_word = w["word"].upper()
                karaoke_parts.append(f"{{\\k{centisecs}}}{clean_word}")

            karaoke_text = " ".join(karaoke_parts)
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{karaoke_text}")

        full_ass = header + "\n".join(events) + "\n"
        out_path.write_text(full_ass, encoding="utf-8")
        logger.info("ass_karaoke_captions_created", path=str(out_path), phrases=len(phrases))
        return str(out_path)
