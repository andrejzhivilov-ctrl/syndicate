"""
Embeddings service — serves the self-hosted vector model to the syndicate.

Runs as its own container on the internal ``backend`` network (no published
ports), so memory text never leaves the server. Called by
``src/embeddings.py`` via ``EMBEDDINGS_URL``.

Model: ``BAAI/bge-m3`` — multilingual (100+ languages, strong on Ukrainian),
1024 dense dimensions. It is downloaded on first start into ``/app/model_cache``
(a volume, so a restart does not re-download) rather than baked into the image.

Honesty rules (``AGENTS.md`` §1):

* If the model is not loaded, ``/embed`` answers **503 with a reason** — it never
  returns zeros or a shorter vector, because a zero vector would compare
  "successfully" against the HNSW index and quietly poison retrieval.
* ``/health`` returns 503 while the model is missing, so ``docker compose ps``
  shows ``unhealthy`` instead of pretending the service is fine.

Endpoints
---------
``GET  /health``  → model, dimensions, device, whether it is loaded.
``POST /embed``   → ``{"texts": [...]}`` → ``{"vectors": [[...]], "dimensions": 1024}``

Model files are large: the first start needs internet access and can take a few
minutes on CPU. Pre-fetch them with:

    docker compose run --rm embeddings python -c \\
      "from sentence_transformers import SentenceTransformer as S; S('BAAI/bge-m3')"
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import structlog
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

MODEL_NAME = os.getenv("EMBEDDINGS_MODEL", "BAAI/bge-m3")
EXPECTED_DIM = int(os.getenv("EMBEDDINGS_EXPECTED_DIM", "1024"))
MAX_BATCH = int(os.getenv("EMBEDDINGS_MAX_BATCH", "64"))
# Optional shared secret. The service sits on the internal network, but n8n shares
# that network, so a defence-in-depth token is cheap.
REQUIRED_TOKEN = (os.getenv("EMBEDDINGS_TOKEN") or "").strip()

_state: Dict[str, Any] = {"model": None, "dimensions": None, "error": None}


def _load_model() -> None:
    """Load the model; a failure is recorded, never raised into a fake success."""
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(MODEL_NAME, device="cpu")
        dimensions = int(model.get_sentence_embedding_dimension() or 0)
        if dimensions != EXPECTED_DIM:
            # Not fatal for the service, but the client validates dimensions too;
            # saying it out loud beats serving vectors nobody can compare.
            logger.warning(
                "embeddings_dimension_mismatch",
                model=MODEL_NAME, reported=dimensions, expected=EXPECTED_DIM,
            )
        _state.update({"model": model, "dimensions": dimensions, "error": None})
        logger.info("embeddings_model_loaded", model=MODEL_NAME, dimensions=dimensions)
    except Exception as exc:  # noqa: BLE001
        _state.update({"model": None, "dimensions": None, "error": str(exc)})
        logger.error("embeddings_model_load_failed", model=MODEL_NAME, error=str(exc))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Loading in-process rather than lazily on first request: the healthcheck then
    # reflects reality from the first second, instead of reporting "ok" while the
    # very first real call times out.
    _load_model()
    yield


app = FastAPI(title="EVA SYNDICATE Embeddings", version="1.0.0", lifespan=lifespan)


class EmbedRequest(BaseModel):
    texts: List[str] = Field(default_factory=list)
    model: Optional[str] = None


def _check_token(token: Optional[str]) -> None:
    if REQUIRED_TOKEN and token != REQUIRED_TOKEN:
        raise HTTPException(status_code=401, detail="invalid or missing X-Embeddings-Token")


@app.get("/health")
async def health() -> Dict[str, Any]:
    if _state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "value": None,
                "model": MODEL_NAME,
                "warning": _state["error"] or "model not loaded",
            },
        )
    return {
        "status": "ok",
        "value": {"loaded": True, "device": "cpu"},
        "model": MODEL_NAME,
        "dimensions": _state["dimensions"],
        "warning": None,
    }


@app.post("/embed")
async def embed(request: EmbedRequest, x_embeddings_token: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _check_token(x_embeddings_token)

    if _state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "value": None,
                "model": MODEL_NAME,
                "warning": _state["error"] or "model not loaded",
            },
        )

    texts = [str(text) for text in request.texts]
    if not texts:
        return {"vectors": [], "dimensions": _state["dimensions"], "model": MODEL_NAME}
    if len(texts) > MAX_BATCH:
        raise HTTPException(
            status_code=400,
            detail=f"batch of {len(texts)} exceeds EMBEDDINGS_MAX_BATCH={MAX_BATCH}",
        )

    model = _state["model"]
    vectors = model.encode(
        texts,
        normalize_embeddings=True,  # cosine distance via the HNSW index
        batch_size=len(texts),
        show_progress_bar=False,
    )
    return {
        "vectors": [[float(value) for value in vector] for vector in vectors],
        "dimensions": _state["dimensions"],
        "model": MODEL_NAME,
    }
