"""Private, operator-reviewed local full-text index. No embeddings or external calls.

One owner, one index. This does not provide multi-user ACLs or semantic RAG.
Do not ingest a medical archive or an unreviewed complete chat export.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from contextlib import contextmanager

from src.antigravity.studio import reviewed_text
from src.antigravity.workspace import StudioError, Workspace


class HistoryIndex:
    def __init__(self, workspace: Workspace) -> None:
        self.ws = workspace

    @contextmanager
    def _connection(self):
        relative = "history/reviewed.sqlite3"
        path = self.ws.path(relative)
        if not path.exists():
            try:
                self.ws.write(relative, b"")
            except StudioError as exc:
                if str(exc) != "output_already_exists":
                    raise
        path.chmod(0o600)
        conn = sqlite3.connect(path, timeout=10)
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS sources (hash TEXT PRIMARY KEY, chunks INTEGER NOT NULL)")
            conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
                source_hash UNINDEXED, ordinal UNINDEXED, content, tokenize='unicode61'
            )""")
            yield conn
        finally:
            conn.close()

    def ingest(self, inbox_file: str, *, operator_reviewed: bool = False) -> dict:
        if operator_reviewed is not True:
            raise StudioError("reviewed_private_copy_required")
        if not inbox_file.startswith("inbox/") or not inbox_file.endswith(".txt"):
            raise StudioError("reviewed_inbox_txt_required")
        raw = self.ws.read(inbox_file).decode("utf-8")
        # Scan the entire document BEFORE inserting any rows; never partial import.
        clean = reviewed_text(raw, 5 * 1024 * 1024)
        fingerprint = hashlib.sha256(clean.encode()).hexdigest()
        pieces = [clean[start:start + 1600] for start in range(0, len(clean), 1400)]
        with self._connection() as conn, conn:
            previous = conn.execute("SELECT chunks FROM sources WHERE hash = ?", (fingerprint,)).fetchone()
            if previous:
                return {"status": "already_indexed", "source_hash": fingerprint, "chunks": previous[0]}
            conn.executemany(
                "INSERT INTO chunks(source_hash, ordinal, content) VALUES (?, ?, ?)",
                [(fingerprint, i, piece) for i, piece in enumerate(pieces)],
            )
            conn.execute("INSERT INTO sources VALUES (?, ?)", (fingerprint, len(pieces)))
        self.ws.audit("reviewed_local_history_indexed", fingerprint)
        return {"status": "indexed_local_fts", "source_hash": fingerprint, "chunks": len(pieces)}

    def search(self, query: str, limit: int = 5) -> dict:
        query = reviewed_text(query, 1000)
        if type(limit) is not int or not 1 <= limit <= 10:
            raise StudioError("limit_must_be_1_to_10")
        terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)[:20]
        if not terms:
            raise StudioError("search_terms_required")
        if not self.ws.path("history/reviewed.sqlite3").exists():
            return {"status": "unavailable", "reason": "history_not_indexed", "matches": []}
        expression = " OR ".join(f'"{term}"' for term in terms)
        with self._connection() as conn:
            rows = conn.execute(
                """SELECT source_hash, ordinal, snippet(chunks, 2, '', '', ' … ', 40)
                   FROM chunks WHERE chunks MATCH ? ORDER BY rank LIMIT ?""", (expression, limit),
            ).fetchall()
        return {
            "status": "ok" if rows else "no_matches", "engine": "local_fts_not_semantic",
            "matches": [{"source_hash": r[0], "chunk": r[1], "excerpt": r[2]} for r in rows],
        }
