"""Code sandbox for the agents (19.11.2026).

Andrii chose a sandbox over a terminal: an agent runs Python for numbers, tables, charts and backtests,
but the code has no secrets, no Vault, no internet and no server around it. The container sits only on
the internal ``hermes_net`` (no route out), runs read-only as an unprivileged user, and each run is a
fresh process in a fresh temporary folder with time, memory and output caps.

POST /run  {"code": "...", "files": {"name.csv": "text", ...}, "timeout": 60}
-> {"status": "ok"|"error"|"timeout", "stdout": "...", "stderr": "...", "files": {"chart.png": "<base64>", ...}}
GET /health -> {"status": "ok"}
"""
from __future__ import annotations

import base64
import json
import os
import resource
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 20 * 1024 * 1024
MAX_TIMEOUT = 300
DEFAULT_TIMEOUT = 60
MAX_OUTPUT = 20_000
MAX_FILE_OUT = 2 * 1024 * 1024
MAX_FILES_OUT = 10
MEMORY_BYTES = 1024 * 1024 * 1024
SAFE_NAME = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")


def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
    os.setsid()


def _safe(name: str) -> bool:
    return bool(name) and len(name) <= 80 and set(name) <= SAFE_NAME and not name.startswith(".")


def run(code: str, files: dict, timeout: int) -> dict:
    with tempfile.TemporaryDirectory(dir="/tmp") as work:
        root = Path(work)
        for name, text in (files or {}).items():
            if not _safe(name):
                return {"status": "error", "error": f"bad_file_name: {name[:40]}"}
            (root / name).write_text(str(text), encoding="utf-8")
        before = {path.name for path in root.iterdir()}
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": work, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8",
               "MPLCONFIGDIR": work}
        try:
            done = subprocess.run([sys.executable, "-I", "-c", code], cwd=work, env=env, capture_output=True,
                                  text=True, timeout=timeout, preexec_fn=_limits)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": f"more than {timeout} s"}
        made = {}
        for path in sorted(root.iterdir()):
            if path.name in before or not path.is_file() or len(made) >= MAX_FILES_OUT:
                continue
            if path.stat().st_size <= MAX_FILE_OUT:
                made[path.name] = base64.b64encode(path.read_bytes()).decode("ascii")
        return {"status": "ok" if done.returncode == 0 else "error", "exit_code": done.returncode,
                "stdout": done.stdout[-MAX_OUTPUT:], "stderr": done.stderr[-MAX_OUTPUT:], "files": made}


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        self._reply(200 if self.path == "/health" else 404, {"status": "ok"} if self.path == "/health" else {})

    def do_POST(self) -> None:  # noqa: N802 - http.server API
        if self.path != "/run":
            return self._reply(404, {"status": "error", "error": "not_found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self._reply(413, {"status": "error", "error": "body_too_large_or_empty"})
        try:
            body = json.loads(self.rfile.read(length))
            code = str(body["code"])
        except (ValueError, KeyError, TypeError):
            return self._reply(400, {"status": "error", "error": "bad_request"})
        timeout = max(1, min(int(body.get("timeout") or DEFAULT_TIMEOUT), MAX_TIMEOUT))
        files = body.get("files") if isinstance(body.get("files"), dict) else {}
        return self._reply(200, run(code, files, timeout))

    def log_message(self, *_args) -> None:  # no request bodies in logs
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
