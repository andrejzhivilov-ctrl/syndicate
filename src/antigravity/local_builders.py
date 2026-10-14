"""Deterministic offline builders, not generative AI or a code execution sandbox."""

from __future__ import annotations

import html
import io
import os
import shutil
import subprocess
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from src.antigravity.studio import reviewed_text
from src.antigravity.workspace import StudioError, Workspace


def landing(ws: Workspace, title: str, description: str) -> str:
    title = html.escape(reviewed_text(title, 160))
    description = html.escape(reviewed_text(description, 4000))
    content = f'''<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; form-action 'none'; base-uri 'none'">
<title>{title}</title><style>
body{{margin:0;background:#101628;color:#eef3ff;font:20px system-ui}}
main{{max-width:900px;margin:15vh auto;padding:32px}}h1{{font-size:clamp(32px,7vw,76px)}}
p{{line-height:1.7;white-space:pre-wrap}}small{{color:#abb7d4}}
</style></head><body><main><small>SYNDICATE / LOCAL STATIC DRAFT</small>
<h1>{title}</h1><p>{description}</p>
<small>Локальна чернетка. Немає бекенду, платежів, збору даних або публікації.</small>
</main></body></html>'''
    relative = f"artifacts/landing-{uuid4().hex}.html"
    ws.write(relative, content.encode())
    ws.audit("static_landing_created", relative.split("/")[-1])
    return relative


def poster(ws: Workspace, title: str) -> str:
    text = reviewed_text(title, 160)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 52)
    except OSError as exc:
        raise StudioError("dejavu_font_unavailable") from exc
    image = Image.new("RGB", (1280, 720), "#101628")
    draw = ImageDraw.Draw(image)
    draw.rectangle((52, 52, 1228, 668), outline="#5ed9c1", width=3)
    # Wrap by measured pixels, including long unbroken text.
    lines, line = [], ""
    for char in text.replace("\n", " "):
        if draw.textlength(line + char, font=font) > 1080:
            lines.append(line)
            line = ""
        line += char
    lines.append(line)
    draw.multiline_text((90, 200), "\n".join(lines[:5]), fill="#eef3ff", font=font, spacing=16)
    output = io.BytesIO()
    image.save(output, format="PNG")
    relative = f"artifacts/poster-{uuid4().hex}.png"
    ws.write(relative, output.getvalue())
    ws.audit("deterministic_poster_created", relative.split("/")[-1])
    return relative


def video(ws: Workspace, frame: str, *, seconds: int = 5) -> dict:
    """Render one local PNG into MP4. No shell, remote URLs, codecs chosen by user, or audio."""
    if type(seconds) is not int or not 1 <= seconds <= 30:
        raise StudioError("duration_must_be_1_to_30_seconds")
    if not frame.startswith("artifacts/") or not frame.endswith(".png"):
        raise StudioError("local_png_artifact_required")
    content = ws.read(frame)
    # Decode and re-encode locally before ffmpeg: no untrusted playlist/protocol input.
    with Image.open(io.BytesIO(content)) as image:
        if image.width * image.height > 10_000_000:
            raise StudioError("image_too_large")
        clean = io.BytesIO()
        image.convert("RGB").resize((1280, 720)).save(clean, format="PNG")
    executable = shutil.which("ffmpeg")
    if not executable:
        return {"status": "unavailable", "reason": "ffmpeg_not_installed", "value": None}
    # All files have unique names, and writes never replace operator files.
    source = f"artifacts/frame-{uuid4().hex}.png"
    target = f"artifacts/video-{uuid4().hex}.mp4"
    ws.write(source, clean.getvalue())
    output = ws.write(target, b"")
    command = [
        executable, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-threads", "1", "-protocol_whitelist", "file,pipe", "-loop", "1",
        "-i", str(ws.path(source)), "-t", str(seconds), "-an", "-r", "24",
        "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-fs", "16777216", str(output),
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, timeout=90, check=False,
            env={"PATH": os.defpath, "LANG": "C.UTF-8"},
        )
    except (OSError, subprocess.TimeoutExpired):
        ws.audit("video_render_failed", output.name)
        return {"status": "unavailable", "reason": "ffmpeg_failed", "value": None}
    if result.returncode or output.stat().st_size == 0:
        ws.audit("video_render_failed", output.name)
        return {"status": "unavailable", "reason": "ffmpeg_failed", "value": None}
    ws.audit("video_rendered", output.name)
    return {"status": "ok", "path": target, "audio": False, "generative_ai": False}
