FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.30.6 \
    python-multipart==0.0.12 \
    faster-whisper==1.0.3 \
    structlog==24.4.0

COPY deploy/docker/whisper_server.py /app/whisper_server.py

ENV PORT=9000 \
    ASR_MODEL=large-v3 \
    ASR_QUANTIZATION=int8 \
    ASR_THREADS=2 \
    HF_HOME=/app/model_cache

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=120s \
    CMD curl -f http://localhost:9000/health || exit 1

CMD ["python", "-m", "uvicorn", "whisper_server:app", "--host", "0.0.0.0", "--port", "9000"]
