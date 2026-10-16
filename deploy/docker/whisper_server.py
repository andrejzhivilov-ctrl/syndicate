import os
import tempfile
from typing import Optional
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from faster_whisper import WhisperModel
import structlog

logger = structlog.get_logger(__name__)

app = FastAPI(title="SYNDICATE Faster-Whisper ASR Service", version="1.0.0")

MODEL_SIZE = os.getenv("ASR_MODEL", "large-v3")
QUANTIZATION = os.getenv("ASR_QUANTIZATION", "int8")
NUM_THREADS = int(os.getenv("ASR_THREADS", "2"))
MODEL_DIR = os.getenv("HF_HOME", "/app/model_cache")

_model: Optional[WhisperModel] = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info("loading_whisper_model", model=MODEL_SIZE, quant=QUANTIZATION)
        _model = WhisperModel(
            MODEL_SIZE,
            device="cpu",
            compute_type=QUANTIZATION,
            cpu_threads=NUM_THREADS,
            download_root=MODEL_DIR,
        )
    return _model


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "whisper_asr", "model": MODEL_SIZE}


@app.post("/asr")
async def transcribe(
    audio_file: UploadFile = File(...),
    language: str = Query(default="uk"),
):
    try:
        model = get_model()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(
                tmp_path,
                language=language if language != "auto" else None,
                beam_size=5,
            )
            text = " ".join([seg.text.strip() for seg in segments])
            return {
                "text": text,
                "language": info.language,
                "duration": round(info.duration, 2),
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as exc:
        logger.error("transcription_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
