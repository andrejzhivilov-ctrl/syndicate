# SYNDICATE — embeddings service (self-hosted BGE-M3)
#
# Why a separate container instead of a library inside eva-agent:
#   * eva-agent runs read-only with a 3 GB limit; a ~2 GB model does not belong there;
#   * the model loads once and stays warm, so agent restarts stay fast;
#   * it mirrors the existing `whisper` service — one container, one model, one volume.
#
# The model itself is NOT baked in: it downloads on first start into the
# `embeddings_data` volume (see deploy/docker-compose.yml). Build stays fast and
# the image stays small.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/model_cache \
    HF_HUB_DISABLE_TELEMETRY=1

WORKDIR /app

# CPU-only torch from the dedicated index: the default PyPI wheel pulls ~2.5 GB of
# CUDA runtime this server will never use.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.4.1 \
 && pip install --no-cache-dir \
        sentence-transformers==3.0.1 \
        fastapi==0.115.0 \
        "uvicorn[standard]==0.30.6" \
        structlog==24.4.0

COPY deploy/runtime/embeddings_server.py /app/embeddings_server.py

# Non-root, matching the other services. The model cache volume is the only
# writable path — it is created here with the right owner.
RUN mkdir -p /app/model_cache && chown -R 1001:1001 /app
USER 1001

EXPOSE 8000

# No published ports: reachable only from the internal `backend` network.
CMD ["uvicorn", "embeddings_server:app", "--host", "0.0.0.0", "--port", "8000"]
