# ===============================================================
# EVA SYNDICATE — Local Faster-Whisper STT Service
# Optimized for CPU int8 quantization
# ===============================================================

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    faster-whisper==1.0.3 \
    fastapi==0.115.0 \
    uvicorn==0.32.0 \
    python-multipart==0.0.12

COPY deploy/runtime/whisper_service.py /app/main.py

ENV ASR_MODEL=large-v3
ENV ASR_QUANTIZATION=int8
ENV ASR_THREADS=2
ENV PORT=9000

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

CMD ["python", "main.py"]
