"""Read-only, default-deny MCP discovery and candidate metadata pool.

This module never imports or launches MCP servers, fetches catalog URLs,
installs packages, or interprets catalog text as instructions. The raw catalog is
untrusted discovery data; only the host-owned ServiceHub grants and reader
allowlist decide whether an agent may search or read it.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
_MANIFEST_PATH = "mcp_servers/pool/registry.json"
_CATALOG_PATH = "mcp_servers/mcp_servers_registry.json"
_AGENT_ID_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_CANDIDATE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_POOL_ITEM_ID_RE = re.compile(r"^candidate:([a-z0-9][a-z0-9-]{0,63})$")
_CATALOG_ITEM_ID_RE = re.compile(r"^catalog:([0-9]{5})$")
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
_INSTALL_TEXT_RE = re.compile(r"\b(?:npx|uvx|uv\s+tool\s+install|pip\s+install|npm\s+install|docker\s+(?:run|pull)|curl|wget)\b", re.I)
_CREDENTIAL_TEXT_RE = re.compile(r"\b(?:api[_ -]?key|token|password|oauth|credential|paid|payment|usdc|wallet)\b", re.I)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)(\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|password|authorization|token)\b\s*[:=]\s*[\"']?)([A-Za-z0-9._~+/=-]{12,})"
)
_SECRET_PREFIX_RE = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[A-Z0-9]{16})\b"
)
_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I)
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")
_MAX_MANIFEST_BYTES = 256 * 1024
_MAX_CATALOG_BYTES = 16 * 1024 * 1024
_MAX_CATALOG_RECORDS = 25_000
_MAX_DESCRIPTION_CHARS = 12_000
_MAX_READ_DESCRIPTION_CHARS = 2_000
_MAX_QUERY_CHARS = 512
_MAX_SEARCH_LIMIT = 5
_POLICY_NOTICE = (
    "Untrusted discovery metadata only: verify the exact upstream source, license, version, tool effects, "
    "credentials, and egress independently. This record does not authorize installation, launch, or grants."
)


class MCPServerPoolError(ValueError):
    """A safe, non-content-bearing MCP-pool error."""


class MCPServerPool:
    """Search/read a hash-pinned catalog under a host-controlled reader allowlist."""

    def __init__(
        self,
        *,
        root: Path | str = ROOT,
        reader_agents: Iterable[str] = (),
    ) -> None:
        supplied_root = Path(root)
        if supplied_root.is_symlink():
            raise MCPServerPoolError("pool_unavailable")
        try:
            self.root = supplied_root.resolve(strict=True)
        except OSError as exc:
            raise MCPServerPoolError("pool_unavailable") from exc
        if not self.root.is_dir():
            raise MCPServerPoolError("pool_unavailable")
        self.reader_agents = self._validated_agent_ids(reader_agents)
        self.manifest = self._read_json(_MANIFEST_PATH, _MAX_MANIFEST_BYTES)
        self._validate_manifest()
        self.catalog = self._read_json(
            _CATALOG_PATH,
            _MAX_CATALOG_BYTES,
            expected_sha256=self.manifest["source_catalog"]["sha256"],
        )
        self.records = self._validate_catalog()
        self.candidates = {item["id"]: item for item in self.manifest["items"]}

    @staticmethod
    def _validated_agent_ids(values: Iterable[str]) -> frozenset[str]:
        if isinstance(values, (str, bytes)):
            raise MCPServerPoolError("invalid_reader_agents")
        try:
            result = frozenset(values)
        except TypeError as exc:
            raise MCPServerPoolError("invalid_reader_agents") from exc
        if len(result) > 64 or any(not isinstance(value, str) or not _AGENT_ID_RE.fullmatch(value) for value in result):
            raise MCPServerPoolError("invalid_reader_agents")
        return result

    def _read_file_bytes(self, relative_path: str, max_bytes: int) -> bytes:
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise MCPServerPoolError("pool_path_invalid")
        path = self.root / relative
        current = self.root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise MCPServerPoolError("pool_unavailable")
        try:
            resolved = path.resolve(strict=True)
            if not resolved.is_relative_to(self.root) or not resolved.is_file():
                raise MCPServerPoolError("pool_unavailable")
            if resolved.stat().st_size > max_bytes:
                raise MCPServerPoolError("pool_file_too_large")
            raw = resolved.read_bytes()
        except OSError as exc:
            raise MCPServerPoolError("pool_unavailable") from exc
        if len(raw) > max_bytes:
            raise MCPServerPoolError("pool_file_too_large")
        return raw

    def _read_json(
        self,
        relative_path: str,
        max_bytes: int,
        *,
        expected_sha256: str | None = None,
    ) -> dict[str, Any]:
        raw = self._read_file_bytes(relative_path, max_bytes)
        if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise MCPServerPoolError("catalog_integrity_failed")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MCPServerPoolError("pool_file_invalid") from exc
        if not isinstance(value, dict):
            raise MCPServerPoolError("pool_file_invalid")
        return value

    def _validate_manifest(self) -> None:
        manifest = self.manifest
        source = manifest.get("source_catalog")
        policy = manifest.get("policy")
        items = manifest.get("items")
        if (
            manifest.get("schema_version") != 1
            or manifest.get("pool_id") != "mcp_server_pool"
            or manifest.get("status") != "prepared_not_enabled"
            or not isinstance(source, dict)
            or not isinstance(policy, dict)
            or source.get("path") != _CATALOG_PATH
            or not isinstance(source.get("sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", source["sha256"])
            or not isinstance(source.get("record_count"), int)
            or isinstance(source.get("record_count"), bool)
            or not isinstance(items, list)
            or len(items) > 256
        ):
            raise MCPServerPoolError("pool_manifest_invalid")
        if (
            policy.get("default_reader_allowlist") != []
            or policy.get("only_read_only_pool_operations") != ["mcp.pool.search", "mcp.pool.read"]
        ):
            raise MCPServerPoolError("pool_manifest_invalid")
        if (
            policy.get("catalog_records_never_create_runtime_servers") is not True
            or policy.get("catalog_records_never_create_agent_grants") is not True
            or policy.get("no_install_or_launch_from_catalog") is not True
        ):
            raise MCPServerPoolError("pool_manifest_invalid")
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                raise MCPServerPoolError("pool_manifest_invalid")
            item_id = item.get("id")
            if (
                not isinstance(item_id, str)
                or not _CANDIDATE_ID_RE.fullmatch(item_id)
                or item_id in seen
                or not isinstance(item.get("name"), str)
                or not item["name"].strip()
                or len(item["name"]) > 256
                or item.get("status") not in {"proposed_not_applied", "review_pending"}
                or item.get("runtime_enabled") is not False
                or item.get("grants_applied") is not False
                or not isinstance(item.get("tools"), list)
                or len(item["tools"]) > 64
            ):
                raise MCPServerPoolError("pool_manifest_invalid")
            seen.add(item_id)
            package = item.get("package")
            upstream_url = item.get("upstream_url")
            parsed_upstream = urlsplit(upstream_url) if isinstance(upstream_url, str) else None
            if (
                not isinstance(package, dict)
                or not isinstance(package.get("name"), str)
                or not package["name"].strip()
                or not isinstance(package.get("version"), str)
                or not package["version"].strip()
                or not isinstance(package.get("artifact_sha256"), str)
                or not re.fullmatch(r"[a-f0-9]{64}", package["artifact_sha256"])
                or parsed_upstream is None
                or parsed_upstream.scheme != "https"
                or not parsed_upstream.hostname
                or parsed_upstream.username
                or parsed_upstream.password
            ):
                raise MCPServerPoolError("pool_manifest_invalid")
            for tool in item["tools"]:
                if (
                    not isinstance(tool, dict)
                    or not isinstance(tool.get("name"), str)
                    or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", tool["name"])
                    or tool.get("effect") not in {"read", "pure_compute"}
                    or not isinstance(tool.get("scope"), str)
                    or len(tool["scope"]) > 512
                    or tool.get("proposed_allowlist") is not True
                ):
                    raise MCPServerPoolError("pool_manifest_invalid")

    def _validate_catalog(self) -> list[dict[str, Any]]:
        servers = self.catalog.get("servers")
        declared_count = self.manifest["source_catalog"]["record_count"]
        if (
            self.catalog.get("version") != "2.0.0"
            or self.catalog.get("total_servers") != declared_count
            or isinstance(self.catalog.get("total_servers"), bool)
            or not isinstance(servers, list)
            or len(servers) != declared_count
            or len(servers) > _MAX_CATALOG_RECORDS
        ):
            raise MCPServerPoolError("catalog_invalid")
        normalized: list[dict[str, Any]] = []
        for server in servers:
            if not isinstance(server, dict):
                raise MCPServerPoolError("catalog_invalid")
            normalized.append(self._normalize_catalog_record(server))
        return normalized

    @staticmethod
    def _catalog_text(server: dict[str, Any], field: str, max_length: int, *, allow_empty: bool = False) -> str:
        default = "" if allow_empty else None
        value = server.get(field, default)
        if (
            not isinstance(value, str)
            or len(value) > max_length
            or (not allow_empty and not value.strip())
        ):
            raise MCPServerPoolError("catalog_invalid")
        return value

    @classmethod
    def _normalize_catalog_record(cls, server: dict[str, Any]) -> dict[str, Any]:
        name = cls._catalog_text(server, "name", 1024).strip()
        url = cls._catalog_text(server, "url", 4096)
        category = cls._catalog_text(server, "category", 256).strip()
        description = cls._catalog_text(server, "description", _MAX_DESCRIPTION_CHARS, allow_empty=True)
        safe_url, query_or_fragment_omitted = cls._safe_catalog_url(url)
        return {
            "name": name,
            "url": safe_url,
            "url_query_or_fragment_omitted": query_or_fragment_omitted,
            "category": category,
            "description": description,
        }

    @staticmethod
    def _safe_catalog_url(url: str) -> tuple[str, bool]:
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise MCPServerPoolError("catalog_invalid")
        if not parsed.hostname or parsed.username or parsed.password:
            raise MCPServerPoolError("catalog_invalid")
        safe_url = urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path, "", ""))
        return safe_url, bool(parsed.query or parsed.fragment)

    @staticmethod
    def _redact_sensitive_text(value: str) -> tuple[str, bool]:
        original = value
        value = _SECRET_ASSIGNMENT_RE.sub(r"\1[REDACTED]", value)
        value = _SECRET_PREFIX_RE.sub("[REDACTED_CREDENTIAL]", value)
        value = _BEARER_RE.sub("Bearer [REDACTED]", value)
        value = _JWT_RE.sub("[REDACTED_JWT]", value)
        return value, value != original

    @staticmethod
    def _normalize(value: str) -> str:
        return unicodedata.normalize("NFKC", value).casefold()

    @classmethod
    def _tokens(cls, value: str) -> set[str]:
        return set(_TOKEN_RE.findall(cls._normalize(value)))

    def _require_reader(self, agent_id: str) -> None:
        if not isinstance(agent_id, str) or not _AGENT_ID_RE.fullmatch(agent_id):
            raise MCPServerPoolError("unknown_agent")
        if agent_id not in self.reader_agents:
            raise MCPServerPoolError("pool_access_denied")

    @staticmethod
    def _validate_query(query: str) -> tuple[set[str], str]:
        if not isinstance(query, str) or not query.strip() or len(query) > _MAX_QUERY_CHARS:
            raise MCPServerPoolError("invalid_query")
        tokens = MCPServerPool._tokens(query)
        if not tokens:
            raise MCPServerPoolError("query_too_short")
        return tokens, MCPServerPool._normalize(query).strip()

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= _MAX_SEARCH_LIMIT:
            raise MCPServerPoolError("invalid_limit")

    @staticmethod
    def _validate_category(category: str | None) -> str | None:
        if category is None:
            return None
        if not isinstance(category, str) or not category.strip() or len(category) > 128:
            raise MCPServerPoolError("invalid_category")
        return MCPServerPool._normalize(category).strip()

    @staticmethod
    def _search_score(query_tokens: set[str], query_text: str, fields: list[str]) -> int:
        all_tokens = MCPServerPool._tokens(" ".join(fields))
        hits = query_tokens & all_tokens
        if not hits:
            return 0
        name_tokens = MCPServerPool._tokens(fields[0])
        category_tokens = MCPServerPool._tokens(fields[1]) if len(fields) > 1 else set()
        score = len(hits) + 2 * len(query_tokens & name_tokens) + len(query_tokens & category_tokens)
        if query_text in MCPServerPool._normalize(" ".join(fields)):
            score += 4
        return score

    def search(
        self,
        agent_id: str,
        query: str,
        *,
        limit: int = 3,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return bounded metadata only; no source descriptions or executable data."""
        self._require_reader(agent_id)
        query_tokens, query_text = self._validate_query(query)
        self._validate_limit(limit)
        normalized_category = self._validate_category(category)
        ranked: list[tuple[int, int, str, dict[str, Any]]] = []

        for item_id, item in self.candidates.items():
            item_category = item.get("service", "MCP candidate")
            if normalized_category and normalized_category not in self._normalize(item_category):
                continue
            fields = [item["name"], item_category, item.get("summary", ""), item.get("upstream_url", "")]
            score = self._search_score(query_tokens, query_text, fields)
            if score:
                result = {
                    "id": f"candidate:{item_id}",
                    "name": item["name"],
                    "category": item_category,
                    "url": item.get("upstream_url"),
                    "status": item["status"],
                    "source_type": "curated_candidate",
                    "trust": "review_metadata_not_runtime_approval",
                    "policy_notice": _POLICY_NOTICE,
                }
                ranked.append((score, 1, item_id, result))

        for index, server in enumerate(self.records, start=1):
            if normalized_category and normalized_category not in self._normalize(server["category"]):
                continue
            fields = [server["name"], server["category"], server["description"], server["url"]]
            score = self._search_score(query_tokens, query_text, fields)
            if score:
                item_id = f"catalog:{index:05d}"
                result = {
                    "id": item_id,
                    "name": server["name"],
                    "category": server["category"],
                    "url": server["url"],
                    "url_query_or_fragment_omitted": server["url_query_or_fragment_omitted"],
                    "status": "discovered_only",
                    "source_type": "untrusted_catalog",
                    "trust": "unverified",
                    "policy_notice": _POLICY_NOTICE,
                }
                ranked.append((score, 0, item_id, result))

        ranked.sort(key=lambda entry: (-entry[0], -entry[1], entry[2]))
        return [result for _score, _priority, _item_id, result in ranked[:limit]]

    def read(self, agent_id: str, item_id: str) -> dict[str, Any]:
        """Read one selected record; raw catalog text remains explicitly untrusted."""
        self._require_reader(agent_id)
        if not isinstance(item_id, str) or len(item_id) > 80:
            raise MCPServerPoolError("invalid_item_id")
        pool_match = _POOL_ITEM_ID_RE.fullmatch(item_id)
        if pool_match:
            candidate_id = pool_match.group(1)
            item = self.candidates.get(candidate_id)
            if item is None:
                raise MCPServerPoolError("item_unavailable")
            return {
                "id": item_id,
                "name": item["name"],
                "service": item.get("service"),
                "upstream_url": item.get("upstream_url"),
                "package": item.get("package"),
                "transport": item.get("transport"),
                "license": item.get("license", "unknown"),
                "status": item["status"],
                "summary": item.get("summary", ""),
                "tools": item["tools"],
                "credentials_required": item.get("credentials_required"),
                "network_egress": item.get("network_egress", []),
                "runtime_state": item.get("runtime_state", {}),
                "review": item.get("review", {}),
                "runtime_enabled": False,
                "grants_applied": False,
                "policy_notice": _POLICY_NOTICE,
            }
        catalog_match = _CATALOG_ITEM_ID_RE.fullmatch(item_id)
        if not catalog_match:
            raise MCPServerPoolError("invalid_item_id")
        index = int(catalog_match.group(1)) - 1
        if index < 0 or index >= len(self.records):
            raise MCPServerPoolError("item_unavailable")
        item = self.records[index]
        description = item["description"]
        safe_description, credential_redacted = self._redact_sensitive_text(description)
        preview = safe_description[:_MAX_READ_DESCRIPTION_CHARS]
        risk_flags = []
        if _INSTALL_TEXT_RE.search(description):
            risk_flags.append("description_mentions_install_or_execution_commands")
        if _CREDENTIAL_TEXT_RE.search(description):
            risk_flags.append("description_mentions_credentials_or_paid_features")
        if credential_redacted:
            risk_flags.append("credential_like_literal_redacted_from_description")
        return {
            "id": item_id,
            "name": item["name"],
            "url": item["url"],
            "url_query_or_fragment_omitted": item["url_query_or_fragment_omitted"],
            "category": item["category"],
            "description": preview,
            "description_truncated": len(safe_description) > len(preview),
            "description_is_untrusted": True,
            "catalog_license": "unknown_not_present_in_source_record",
            "risk_flags": risk_flags,
            "status": "discovered_only",
            "source_type": "untrusted_catalog",
            "source_catalog_sha256": self.manifest["source_catalog"]["sha256"],
            "runtime_enabled": False,
            "grants_applied": False,
            "policy_notice": _POLICY_NOTICE,
        }
