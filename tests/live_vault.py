"""A fake Vault HTTP API for tests, plus a helper to run ``vault_init.sh``.

There is no Vault binary and no Docker in CI, so ``deploy/scripts/vault_init.sh``
would otherwise never be executed — and it is the one script that *must* work on
a fresh server, because it is what turns an uninitialised Vault into the tokens
the agent needs to boot.

The fake mirrors the real envelopes (``sys/init``, ``sys/unseal``, ``sys/mounts``,
``sys/audit``, ``sys/policies/acl/<name>``, ``auth/approle/role/<name>`` and its
``/role-id`` + ``/secret-id`` children, ``secret/data/<path>``,
``auth/token/revoke-self``) and the HTTP methods the script uses. It is not a
security tool and not a Vault emulator: it exists to prove the script's
*sequence*, guards and file handling.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_TOKEN = "mock-root-token"

PLACEHOLDER_MARKERS = ("CHANGE_ME", "PLACEHOLDER", "REPLACE_ME", "UPDATE_ME", "FIXME", "TODO")

#: Paths that only need a 204 (audit device, mount, auth method, token revoke).
_NO_CONTENT_PATHS = (
    "/v1/sys/audit/file",
    "/v1/sys/mounts/secret",
    "/v1/auth/approle",
    "/v1/auth/token/revoke-self",
)


def _is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    upper = text.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


class FakeVault:
    """In-memory Vault API, threaded so the script's curl calls can block on it."""

    def __init__(self) -> None:
        self.initialized = False
        self.sealed = True
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self.policies: Dict[str, str] = {}
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.requests: List[Tuple[str, str, Optional[str]]] = []  # (method, path, token)
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self.port = 0

    # ── server lifecycle ────────────────────────────────────────────────────
    def start(self) -> "FakeVault":
        self._httpd = _VaultServer(("127.0.0.1", 0), _FakeVaultHandler)
        self._httpd.state = self
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def __enter__(self) -> "FakeVault":
        return self.start()

    def __exit__(self, *exc: Any) -> None:
        self.stop()

    @property
    def address(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    # ── assertion helpers ───────────────────────────────────────────────────
    def paths_written(self) -> List[str]:
        return [p for m, p, _t in self.requests if m in ("PUT", "POST") and "/secret/data/" in p]

    def tokens_used(self) -> List[Optional[str]]:
        return [t for _m, _p, t in self.requests]

    def placeholder_secrets(self) -> Dict[str, List[str]]:
        """Secrets holding a fill-me-in marker — the thing this work removes."""
        offenders: Dict[str, List[str]] = {}
        for path, data in self.secrets.items():
            bad = sorted(k for k, v in data.items() if _is_placeholder(v))
            if bad:
                offenders[path] = bad
        return offenders


class _VaultServer(ThreadingHTTPServer):
    """HTTP server carrying the shared :class:`FakeVault` state."""

    state: FakeVault

    def handle_error(self, request: Any, client_address: Any) -> None:
        """curl's ``-f`` abandons a 4xx connection early; that is not a failure."""
        pass


class _FakeVaultHandler(BaseHTTPRequestHandler):
    """One handler class for every fake Vault; state lives on the server."""

    protocol_version = "HTTP/1.0"

    #: Exact paths handled by a single method that only needs to answer 204.
    _NO_CONTENT = _NO_CONTENT_PATHS

    #: Prefix → handler name, checked in order.
    _PREFIX_ROUTES: Tuple[Tuple[str, str], ...] = (
        ("/v1/sys/policies/acl/", "_handle_policy"),
        ("/v1/auth/approle/role/", "_handle_approle"),
        ("/v1/secret/data/", "_handle_kv"),
    )

    # ── plumbing ────────────────────────────────────────────────────────────
    @property
    def state(self) -> FakeVault:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, *args: Any) -> None:  # silence access logs
        pass

    def _send(self, code: int, body: Optional[Dict[str, Any]] = None) -> None:
        blob = json.dumps(body or {}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def _json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    def _path(self) -> str:
        return self.path.split("?", 1)[0]

    def _token(self) -> Optional[str]:
        return self.headers.get("X-Vault-Token")

    def _record(self, method: str) -> str:
        path = self._path()
        self.state.requests.append((method, path, self._token()))
        return path

    def _require_root(self) -> bool:
        """Only the root token may write secrets/policies — like real Vault ACLs."""
        if self._token() == ROOT_TOKEN:
            return True
        self._send(403, {"errors": ["permission denied"]})
        return False

    # ── GET ─────────────────────────────────────────────────────────────────
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = self._record("GET")
        if path == "/v1/sys/health":
            self._send(200, {"initialized": self.state.initialized, "sealed": self.state.sealed})
        elif path == "/v1/sys/init":
            self._send(200, {"initialized": self.state.initialized})
        elif path.startswith("/v1/secret/data/"):
            self._get_kv(path)
        elif path.startswith("/v1/auth/approle/role/") and path.endswith("/role-id"):
            self._get_role_id(path)
        else:
            self._send(404, {"errors": ["unsupported path"]})

    def _get_kv(self, path: str) -> None:
        if not self._require_root():
            return
        key = path[len("/v1/secret/data/"):]
        if key not in self.state.secrets:
            self._send(404, {"errors": []})
            return
        self._send(200, {"data": {"data": self.state.secrets[key]}})

    def _get_role_id(self, path: str) -> None:
        name = path[len("/v1/auth/approle/role/"):-len("/role-id")]
        if name not in self.state.roles:
            self._send(404, {"errors": []})
            return
        self._send(200, {"data": {"role_id": f"role-id-{name}"}})

    # ── PUT / POST ──────────────────────────────────────────────────────────
    def do_PUT(self) -> None:  # noqa: N802
        self._route_mutation("PUT")

    def do_POST(self) -> None:  # noqa: N802
        self._route_mutation("POST")

    def _route_mutation(self, method: str) -> None:
        path = self._record(method)
        exact: Dict[str, Callable[[str], None]] = {
            "/v1/sys/init": self._handle_init,
            "/v1/sys/unseal": self._handle_unseal,
        }
        if path in exact:
            exact[path](path)
            return
        if path in self._NO_CONTENT:
            self._send(204)
            return
        for prefix, handler_name in self._PREFIX_ROUTES:
            if path.startswith(prefix):
                getattr(self, handler_name)(path)
                return
        self._send(404, {"errors": ["unsupported path"]})

    def _handle_init(self, _path: str) -> None:
        body = self._json_body()
        if not body.get("secret_shares"):
            self._send(400, {"errors": ["missing secret_shares"]})
            return
        if self.state.initialized:
            self._send(400, {"errors": ["vault is already initialized"]})
            return
        self.state.initialized = True
        shares = int(body["secret_shares"])
        self._send(200, {
            "keys": [f"key-{i}" for i in range(shares)],
            "keys_base64": [f"share-{i}" for i in range(shares)],
            "root_token": ROOT_TOKEN,
        })

    def _handle_unseal(self, _path: str) -> None:
        if self._json_body().get("key") not in [f"share-{i}" for i in range(5)]:
            self._send(400, {"errors": ["invalid key"]})
            return
        self.state.sealed = False
        self._send(200, {"sealed": False})

    def _handle_policy(self, path: str) -> None:
        if not self._require_root():
            return
        self.state.policies[path.rsplit("/", 1)[-1]] = self._json_body().get("policy", "")
        self._send(204)

    def _handle_approle(self, path: str) -> None:
        if not self._require_root():
            return
        name = path[len("/v1/auth/approle/role/"):]
        if name.endswith("/secret-id"):
            name = name[: -len("/secret-id")]
            if name not in self.state.roles:
                self._send(404, {"errors": []})
                return
            self._send(200, {"data": {"secret_id": f"secret-id-{name}"}})
            return
        self.state.roles[name] = self._json_body()
        self._send(204)

    def _handle_kv(self, path: str) -> None:
        if not self._require_root():
            return
        self.state.secrets[path[len("/v1/secret/data/"):]] = self._json_body().get("data", {})
        self._send(204)


def run_vault_init(
    vault: FakeVault,
    secrets_dir: Path,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Run ``deploy/scripts/vault_init.sh`` against ``vault``.

    ``env`` is merged over a deterministic, non-placeholder baseline so the
    guards in the script pass unless a test deliberately breaks one.
    """
    mingit_usr = r"C:\Users\Admin\.gemini\antigravity\brain\3212bbb7-eaa9-42ef-8dd7-47ab843f1594\scratch\mingit\usr\bin"
    mingit_w64 = r"C:\Users\Admin\.gemini\antigravity\brain\3212bbb7-eaa9-42ef-8dd7-47ab843f1594\scratch\mingit\mingw64\bin"
    venv_bin = str(Path(sys.executable).parent)
    extra_path = os.pathsep.join([venv_bin, mingit_usr, mingit_w64, os.environ.get("PATH", "/usr/bin:/bin")])
    bash_bin = shutil.which("bash", path=extra_path) or "bash"
    base_env = {
        "PATH": extra_path,
        "VAULT_ADDR": vault.address,
        "SECRETS_DIR": str(secrets_dir),
        "POSTGRES_PASSWORD": "db-pass-for-tests",
        "REDIS_PASSWORD": "redis-pass-for-tests",
    }
    base_env.update(env or {})
    return subprocess.run(
        [bash_bin, str(REPO_ROOT / "deploy" / "scripts" / "vault_init.sh")],
        capture_output=True,
        text=True,
        env=base_env,
        timeout=120,
        check=False,
    )
