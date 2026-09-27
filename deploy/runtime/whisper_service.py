import os
import io
import logging
from fastapi import FastAPI, UploadFile, File
import uvicorn
from faster_whisper import WhisperModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whisper_service")

app = FastAPI(title="Faster Whisper STT Service")

MODEL_NAME = os.getenv("ASR_MODEL", "large-v3")
QUANTIZATION = os.getenv("ASR_QUANTIZATION", "int8")
THREADS = int(os.getenv("ASR_THREADS", "2"))

logger.info(f"Loading Whisper model: {MODEL_NAME} (quantization: {QUANTIZATION}, cpu_threads: {THREADS})")
model = WhisperModel(MODEL_NAME, device="cpu", compute_type=QUANTIZATION, cpu_threads=THREADS)
logger.info("Model loaded and ready.")

@app.get("/health")
def health():
    return {"status": "ready", "model": MODEL_NAME, "quantization": QUANTIZATION}

@app.post("/asr")
async def transcribe(audio_file: UploadFile = File(...), language: str = "uk"):
    contents = await audio_file.read()
    audio_stream = io.BytesIO(contents)
    
    segments, info = model.transcribe(audio_stream, language=language, beam_size=5)
    text = " ".join([segment.text for segment in segments]).strip()
    
    return {"text": text, "language": info.language, "duration": info.duration}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "9000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
