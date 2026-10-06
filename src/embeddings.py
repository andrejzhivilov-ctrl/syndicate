"""
Embedding provider — the vector half of semantic memory search.

The syndicate's memory is personal: health records, finances, private
conversations. Vectors are therefore produced by a self-hosted model rather than
a third-party API, which buys three things at once:

* nothing leaves the server, so PII never has to be masked before embedding —
  and masking would be self-defeating here, because it removes exactly the
  identifiers (names, IBANs, phone numbers) an operator later searches for;
* no per-token bill: embedding every episode is free once the model is resident;
* a multilingual model that is genuinely strong on Ukrainian, unlike the
  English-first APIs.

Default model: ``BAAI/bge-m3`` (dense, 1024 dimensions), served by the
``embeddings`` container — see ``deploy/runtime/embeddings_server.py``.

Honesty rules (``AGENTS.md`` §1), because a poisoned index is worse than a
missing one:

* A vector is either produced correctly or not produced at all. This module never
  returns zeros, never pads or truncates a vector, and never substitutes a
  different model's output.
* A dimension mismatch is an error, not something to coerce — it means the
  provider and the database schema disagree, and every similarity score computed
  afterwards would be meaningless while looking perfectly normal.
* ``EmbeddingUnavailable`` carries the reason so callers can report
  ``unavailable`` instead of pretending a search happened.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logger = structlog.get_logger(__name__)

# BGE-M3 dense output. This number is not free to change: it must match
# ``vector(N)`` in config/postgres/*.sql, which is guarded by
# tests/test_regressions.py::TestEmbeddingContract. Changing the model means
# changing the schema (see config/postgres/migration_v5_embeddings_1024.sql).
EMBEDDING_DIM = 1024
DEFAULT_MODEL = "bge-m3"
# Cyrillic tokenises at roughly 2-3 characters per token, so 6000 characters stay
# well inside BGE-M3's 8192-token window while bounding request size.
MAX_INPUT_CHARS = 6000


class EmbeddingUnavailable(RuntimeError):
    """No trustworthy vector could be produced (provider down, bad payload)."""


class _TransientProviderError(EmbeddingUnavailable):
    """A provider hiccup worth retrying once; still an ``EmbeddingUnavailable``."""


def _validate_vector(vector: Any, expected: int, index: int) -> List[float]:
    """Return ``vector`` as a list of finite floats, or raise.

    Every check here exists because the alternative is silent corruption: a
    wrong-length or zero vector compares fine against the HNSW index and simply
    returns nonsense, which looks like a working search.
    """
    if not isinstance(vector, (list, tuple)):
        raise EmbeddingUnavailable(f"vector #{index} is {type(vector).__name__}, expected a list")
    if len(vector) != expected:
        raise EmbeddingUnavailable(
            f"vector #{index} has {len(vector)} dimensions, expected {expected} — the provider "
            "model and the config/postgres schema disagree; refusing to index it"
        )
    values: List[float] = []
    for value in vector:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise EmbeddingUnavailable(f"vector #{index} contains a non-numeric value") from exc
        if not math.isfinite(number):
            raise EmbeddingUnavailable(f"vector #{index} contains NaN or infinity")
        values.append(number)
    if not any(values):
        raise EmbeddingUnavailable(
            f"vector #{index} is all zeros — that is what a broken provider returns instead of "
            "failing, and it would make every search look successful"
        )
    return values


class HttpEmbeddingProvider:
    """Embedding provider backed by the local ``embeddings`` service.

    ``client`` may be injected so tests can drive the exact HTTP contract with
    ``httpx.MockTransport`` — the model itself cannot be exercised in CI, but the
    validation rules above can.
    """

    def __init__(
        self,
        base_url: str,
        model: str = DEFAULT_MODEL,
        dimensions: int = EMBEDDING_DIM,
        timeout: float = 30.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.base_url = str(base_url).rstrip("/")
        self.model = model
        self.dimensions = int(dimensions)
        self._timeout = float(timeout)
        self._client = client

    @property
    def name(self) -> str:
        return f"{self.model}@{self.base_url}"

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def health(self) -> Dict[str, Any]:
        """Probe the service; ``unavailable`` is a real answer, not an exception."""
        try:
            response = await self._http().get("/health")
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "unavailable",
                "value": None,
                "provider": self.name,
                "warning": f"embeddings service unreachable: {exc}",
            }

        reported = payload.get("dimensions")
        if reported is not None and int(reported) != self.dimensions:
            return {
                "status": "unavailable",
                "value": payload,
                "provider": self.name,
                "warning": (
                    f"embeddings service reports {reported} dimensions, this deployment expects "
                    f"{self.dimensions} — semantic search stays off until they agree"
                ),
            }
        return {"status": "ok", "value": payload, "provider": self.name, "warning": None}

    async def embed(self, texts: Sequence[str]) -> List[List[float]]:
        """Embed a batch. Raises :class:`EmbeddingUnavailable` rather than guessing."""
        prepared = [str(text)[:MAX_INPUT_CHARS] for text in texts]
        if not prepared:
            return []

        payload = await self._post({"texts": prepared, "model": self.model})
        vectors = payload.get("vectors")
        if not isinstance(vectors, list) or len(vectors) != len(prepared):
            returned = len(vectors) if isinstance(vectors, list) else "no"
            raise EmbeddingUnavailable(
                f"embeddings service returned {returned} vectors for {len(prepared)} inputs"
            )
        return [_validate_vector(vector, self.dimensions, index) for index, vector in enumerate(vectors)]

    async def embed_one(self, text: str) -> List[float]:
        vectors = await self.embed([text])
        return vectors[0]

    @retry(
        retry=retry_if_exception_type(_TransientProviderError),
        stop=stop_after_attempt(2),
        wait=wait_fixed(0.2),
        reraise=True,
    )
    async def _post(self, body: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = await self._http().post("/embed", json=body)
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            # One retry: a cold model or a brief network blip is worth it, and it
            # is bounded so a dead service cannot stall the write path.
            raise _TransientProviderError(f"embeddings service unreachable: {exc}") from exc

        if response.status_code >= 500:
            raise _TransientProviderError(
                f"embeddings service returned {response.status_code}: {response.text[:200]}"
            )
        if response.status_code >= 400:
            raise EmbeddingUnavailable(
                f"embeddings service rejected the request ({response.status_code}): "
                f"{response.text[:200]}"
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise EmbeddingUnavailable("embeddings service returned a non-JSON body") from exc
        if not isinstance(payload, dict):
            raise EmbeddingUnavailable("embeddings service returned a non-object payload")
        return payload


def build_embedding_provider(env: Optional[Dict[str, str]] = None) -> Optional[HttpEmbeddingProvider]:
    """Build the provider from the environment, or ``None`` when it is disabled.

    ``EMBEDDINGS_URL`` unset or empty means "this deployment has no vector
    search": episodic memory keeps working and semantic search reports
    ``disabled``. That is a supported mode (a cache outage must cost recall
    quality, never availability), not a misconfiguration.
    """
    import os

    source = env if env is not None else os.environ
    url = (source.get("EMBEDDINGS_URL") or "").strip()
    if not url:
        logger.warning(
            "embeddings_disabled",
            reason="EMBEDDINGS_URL is not set",
            impact="semantic search is off; episodic memory still works",
        )
        return None

    dimensions_raw = (source.get("EMBEDDINGS_DIM") or "").strip()
    try:
        dimensions = int(dimensions_raw) if dimensions_raw else EMBEDDING_DIM
    except ValueError:
        logger.warning("embeddings_bad_dim", value=dimensions_raw, fallback=EMBEDDING_DIM)
        dimensions = EMBEDDING_DIM

    timeout_raw = (source.get("EMBEDDINGS_TIMEOUT") or "").strip()
    try:
        timeout = float(timeout_raw) if timeout_raw else 30.0
    except ValueError:
        timeout = 30.0

    return HttpEmbeddingProvider(
        base_url=url,
        model=(source.get("EMBEDDINGS_MODEL") or DEFAULT_MODEL).strip() or DEFAULT_MODEL,
        dimensions=dimensions,
        timeout=timeout,
    )
