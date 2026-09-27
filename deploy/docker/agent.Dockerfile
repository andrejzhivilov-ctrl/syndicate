# ===============================================================
# EVA SYNDICATE — Production Universal Agent Dockerfile
# Multi-stage, hardened, non-root Python 3.11 agent runtime
# ===============================================================

FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Base Python dependencies for all Syndicate agents
COPY deploy/docker/requirements-agent.txt .
RUN pip install --no-cache-dir --user -r requirements-agent.txt

# ── FINAL PRODUCTION STAGE ─────────────────────────────────────
FROM python:3.11-slim

ARG AGENT_UID=1001
ARG AGENT_GID=1001
ARG AGENT_NAME=agent

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed wheels from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user matching the container uid/gid
RUN groupadd -g ${AGENT_GID} syndicate && \
    useradd -u ${AGENT_UID} -g syndicate -m -s /bin/bash syndicate && \
    mkdir -p /app /data/workspace /data/audit && \
    chown -R syndicate:syndicate /app /data

# Copy runtime entrypoint & agent runner
COPY deploy/runtime /app/runtime
RUN chmod +x /app/runtime/*.py

USER syndicate

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "/app/runtime/agent_runner.py"]
