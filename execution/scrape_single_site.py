"""Fetch one public HTML page and convert it to Markdown safely.

The network client deliberately bypasses environment-configured proxies and pins
connections to the public IPs validated for each URL/redirect. It has no browser,
JavaScript, Cloudflare-bypass, or arbitrary file-write capability.
"""

from __future__ import annotations

import argparse
import http.client
import io
import ipaddress
import os
import re
import socket
import ssl
import sys
import tempfile
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRAPER_OUTPUT_ROOT = REPO_ROOT / "scratch" / "scraper"
MAX_URL_LENGTH = 2_048
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_MARKDOWN_CHARS = 200_000
MAX_REDIRECTS = 4
REQUEST_TIMEOUT_SECONDS = 8.0
TOTAL_TIMEOUT_SECONDS = 20.0
READ_CHUNK_BYTES = 64 * 1024
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
    ".test",
    ".invalid",
    ".example",
    ".onion",
)
BLOCKED_IPV6_NETWORKS = (
    ipaddress.ip_network("64:ff9b::/96"),  # well-known NAT64 can translate to private IPv4
    ipaddress.ip_network("64:ff9b:1::/48"),  # local-use NAT64 translation prefix
)


class ScrapeError(Exception):
    """A safe, non-sensitive error code suitable for CLI output."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ParsedURL:
    scheme: str
    host: str
    port: int
    host_header: str
    request_target: str


@dataclass(frozen=True)
class FetchResponse:
    status: int
    headers: dict[str, str]
    body: bytes = b""


def _is_public_address(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    if isinstance(parsed, ipaddress.IPv6Address):
        if parsed.ipv4_mapped is not None:
            parsed = parsed.ipv4_mapped
        elif parsed.sixtofour is not None or parsed.teredo is not None or any(parsed in network for network in BLOCKED_IPV6_NETWORKS):
            return False
    return parsed.is_global


def parse_and_validate_url(raw_url: str) -> ParsedURL:
    """Parse an HTTP(S) URL and reject credentials, private hosts and odd ports."""
    if not isinstance(raw_url, str) or not raw_url or len(raw_url) > MAX_URL_LENGTH:
        raise ScrapeError("invalid_url")
    if raw_url != raw_url.strip() or any(ord(char) < 0x20 or ord(char) == 0x7F for char in raw_url):
        raise ScrapeError("invalid_url")

    try:
        parts = urlsplit(raw_url)
        scheme = parts.scheme.lower()
        hostname = parts.hostname
        explicit_port = parts.port
    except ValueError as exc:
        raise ScrapeError("invalid_url") from exc

    if scheme not in {"http", "https"} or not hostname:
        raise ScrapeError("invalid_url")
    if parts.username is not None or parts.password is not None or "\\" in parts.netloc:
        raise ScrapeError("unsafe_url")
    if "%" in hostname:
        # In particular, do not accept IPv6 zone identifiers.
        raise ScrapeError("unsafe_host")

    default_port = 443 if scheme == "https" else 80
    port = default_port if explicit_port is None else explicit_port
    if port != default_port:
        raise ScrapeError("unsafe_port")

    host = hostname.rstrip(".").lower()
    if not host or len(host) > 253:
        raise ScrapeError("unsafe_host")

    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not _is_public_address(str(literal_ip)):
            raise ScrapeError("unsafe_host")
        host = str(literal_ip)
        host_for_header = f"[{host}]" if literal_ip.version == 6 else host
    else:
        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ScrapeError("unsafe_host") from exc
        labels = host.split(".")
        if len(labels) < 2 or any(
            not label
            or len(label) > 63
            or label.startswith("-")
            or label.endswith("-")
            or re.fullmatch(r"[a-z0-9-]+", label) is None
            for label in labels
        ):
            raise ScrapeError("unsafe_host")
        if any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in BLOCKED_HOST_SUFFIXES):
            raise ScrapeError("unsafe_host")
        # Some system resolvers accept non-standard numeric IPv4 spellings
        # (octal, hexadecimal, or a single integer) as if they were IP literals.
        try:
            alternate_ip = ipaddress.IPv4Address(socket.inet_aton(host))
        except (OSError, ValueError):
            alternate_ip = None
        if alternate_ip is not None:
            if not alternate_ip.is_global:
                raise ScrapeError("unsafe_host")
            host = str(alternate_ip)
        host_for_header = host

    # Encode Unicode path/query octets before passing them to http.client.
    path = quote(parts.path or "/", safe="/%:@!$&'()*+,;=-._~")
    query = quote(parts.query, safe="/%?:@!$&'()*+,;=-._~")
    request_target = path + (f"?{query}" if query else "")
    if not request_target.startswith("/") or any(ord(char) < 0x20 or ord(char) == 0x7F for char in request_target):
        raise ScrapeError("invalid_url")

    if explicit_port is not None:
        host_for_header = f"{host_for_header}:{port}"
    return ParsedURL(
        scheme=scheme,
        host=host,
        port=port,
        host_header=host_for_header,
        request_target=request_target,
    )


def resolve_public_addresses(host: str) -> list[str]:
    """Resolve once and reject the whole host if any answer is non-public."""
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if not _is_public_address(str(literal)):
            raise ScrapeError("unsafe_host")
        return [str(literal)]

    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (OSError, socket.gaierror) as exc:
        raise ScrapeError("dns_resolution_failed") from exc

    addresses = set()
    for record in records:
        address = record[4][0]
        if not isinstance(address, str) or "%" in address or not _is_public_address(address):
            raise ScrapeError("unsafe_host")
        addresses.add(str(ipaddress.ip_address(address)))
    if not addresses:
        raise ScrapeError("dns_resolution_failed")
    return sorted(addresses)


class _PinnedHTTPConnection(http.client.HTTPConnection):
    """HTTP connection that cannot re-resolve the checked hostname."""

    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float) -> None:
        super().__init__(host, port=port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self._tunnel()


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection pinned to a validated IP while retaining host SNI/TLS checks."""

    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float) -> None:
        super().__init__(host, port=port, timeout=timeout, context=ssl.create_default_context())
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self._tunnel()
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


def _header_value(headers: Any, name: str) -> str | None:
    getter = getattr(headers, "get", None)
    if callable(getter):
        value = getter(name)
        if value is not None:
            return str(value)
    lowered = name.lower()
    if isinstance(headers, dict):
        for key, value in headers.items():
            if str(key).lower() == lowered:
                return str(value)
    return None


def _read_bounded_body(response: Any, connection: Any, max_bytes: int, deadline: float) -> bytes:
    declared_length = _header_value(response.headers, "Content-Length")
    expected_length: int | None = None
    if declared_length is not None:
        try:
            expected_length = int(declared_length)
        except ValueError as exc:
            raise ScrapeError("invalid_content_length") from exc
        if expected_length < 0:
            raise ScrapeError("invalid_content_length")
        if expected_length > max_bytes:
            raise ScrapeError("response_too_large")

    content_encoding = (_header_value(response.headers, "Content-Encoding") or "identity").strip().lower()
    if content_encoding not in {"", "identity"}:
        raise ScrapeError("unsupported_content_encoding")

    chunks: list[bytes] = []
    total = 0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ScrapeError("timeout")
        if connection.sock is not None:
            connection.sock.settimeout(remaining)
        chunk = response.read(min(READ_CHUNK_BYTES, max_bytes + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ScrapeError("response_too_large")
        chunks.append(chunk)
    if expected_length is not None and total != expected_length:
        raise ScrapeError("incomplete_response")
    return b"".join(chunks)


def _request_once(
    parsed_url: ParsedURL,
    pinned_ip: str,
    *,
    max_bytes: int,
    deadline: float,
) -> FetchResponse:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ScrapeError("timeout")
    timeout = min(REQUEST_TIMEOUT_SECONDS, remaining)
    connection_type = _PinnedHTTPSConnection if parsed_url.scheme == "https" else _PinnedHTTPConnection
    connection = connection_type(parsed_url.host, parsed_url.port, pinned_ip, timeout)
    try:
        connection.putrequest("GET", parsed_url.request_target, skip_accept_encoding=True)
        connection.putheader("Host", parsed_url.host_header)
        connection.putheader("User-Agent", "SYNDICATE-Scraper/1.0")
        connection.putheader("Accept", "text/html, application/xhtml+xml")
        connection.putheader("Accept-Encoding", "identity")
        connection.putheader("Connection", "close")
        connection.endheaders()
        response = connection.getresponse()
        headers = {str(key): str(value) for key, value in response.getheaders()}

        if response.status in REDIRECT_STATUSES:
            return FetchResponse(status=response.status, headers=headers)
        if response.status != 200:
            return FetchResponse(status=response.status, headers=headers)
        body = _read_bounded_body(response, connection, max_bytes, deadline)
        return FetchResponse(status=response.status, headers=headers, body=body)
    except ScrapeError:
        raise
    except TimeoutError as exc:
        raise ScrapeError("timeout") from exc
    except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
        raise ScrapeError("connection_failed") from exc
    finally:
        connection.close()


def _require_authorization_confirmation(confirmed: bool) -> None:
    if confirmed is not True:
        raise ScrapeError("authorization_confirmation_required")


def fetch_html(
    raw_url: str,
    *,
    authorization_confirmed: bool = False,
    max_bytes: int = MAX_RESPONSE_BYTES,
    resolver: Callable[[str], list[str]] = resolve_public_addresses,
    requester: Callable[..., FetchResponse] = _request_once,
) -> bytes:
    """Fetch bounded HTML through validated, IP-pinned HTTP(S) connections."""
    _require_authorization_confirmation(authorization_confirmed)
    if max_bytes <= 0:
        raise ScrapeError("invalid_size_limit")
    deadline = time.monotonic() + TOTAL_TIMEOUT_SECONDS
    current_url = raw_url

    for redirect_count in range(MAX_REDIRECTS + 1):
        parsed = parse_and_validate_url(current_url)
        addresses = resolver(parsed.host)
        response: FetchResponse | None = None
        last_error: ScrapeError | None = None
        for address in addresses:
            if not _is_public_address(address):
                raise ScrapeError("unsafe_host")
            try:
                response = requester(parsed, address, max_bytes=max_bytes, deadline=deadline)
                break
            except ScrapeError as exc:
                if exc.code == "timeout":
                    raise
                last_error = exc
        if response is None:
            raise last_error or ScrapeError("connection_failed")

        if response.status in REDIRECT_STATUSES:
            if redirect_count >= MAX_REDIRECTS:
                raise ScrapeError("redirect_limit")
            location = _header_value(response.headers, "Location")
            if not location:
                raise ScrapeError("redirect_location_missing")
            next_url = urljoin(current_url, location)
            next_parsed = parse_and_validate_url(next_url)
            if parsed.scheme == "https" and next_parsed.scheme != "https":
                raise ScrapeError("https_downgrade_redirect")
            current_url = next_url
            continue
        if response.status != 200:
            raise ScrapeError("http_status_not_ok")

        content_type = (_header_value(response.headers, "Content-Type") or "").split(";", 1)[0].strip().lower()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ScrapeError("unsupported_content_type")
        if not response.body:
            raise ScrapeError("empty_response")
        if len(response.body) > max_bytes:
            raise ScrapeError("response_too_large")
        return response.body

    raise ScrapeError("redirect_limit")


def convert_html_to_markdown(html_bytes: bytes) -> str:
    """Convert bounded HTML without executing scripts or making secondary requests."""
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise ScrapeError("converter_unavailable") from exc

    try:
        result = MarkItDown().convert_stream(io.BytesIO(html_bytes), file_extension=".html")
        content = result.text_content
    except Exception as exc:
        raise ScrapeError("conversion_failed") from exc
    if not isinstance(content, str) or not content.strip():
        raise ScrapeError("empty_conversion")
    if len(content) > MAX_MARKDOWN_CHARS:
        raise ScrapeError("markdown_too_large")
    return content


def resolve_output_path(output_arg: str | None, output_root: Path = SCRAPER_OUTPUT_ROOT) -> Path:
    """Allow a Markdown filename only, anchored inside the ignored scratch directory."""
    root = Path(output_root)
    if root == SCRAPER_OUTPUT_ROOT and (REPO_ROOT / "scratch").is_symlink():
        raise ScrapeError("unsafe_output_path")
    if root.is_symlink():
        raise ScrapeError("unsafe_output_path")
    try:
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as exc:
        raise ScrapeError("output_directory_unavailable") from exc
    if root.is_symlink():
        raise ScrapeError("unsafe_output_path")

    root = root.resolve()
    raw_name = output_arg or "scraped_content.md"
    if not isinstance(raw_name, str) or not raw_name or "\x00" in raw_name:
        raise ScrapeError("unsafe_output_path")
    candidate = Path(raw_name)
    if candidate.is_absolute():
        if candidate.parent.resolve() != root:
            raise ScrapeError("unsafe_output_path")
        filename = candidate.name
    else:
        if len(candidate.parts) != 1 or candidate.name in {"", ".", ".."}:
            raise ScrapeError("unsafe_output_path")
        filename = candidate.name

    if (
        len(filename) > 128
        or filename in {".", ".."}
        or ":" in filename
        or any(ord(char) < 0x20 or ord(char) == 0x7F for char in filename)
        or Path(filename).suffix.lower() != ".md"
    ):
        raise ScrapeError("unsafe_output_path")

    target = root / filename
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ScrapeError("unsafe_output_path")
    return target


def write_markdown(markdown: str, output_arg: str | None, output_root: Path = SCRAPER_OUTPUT_ROOT) -> Path:
    if not isinstance(markdown, str) or len(markdown) > MAX_MARKDOWN_CHARS:
        raise ScrapeError("markdown_too_large")
    target = resolve_output_path(output_arg, output_root)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=".scrape-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(markdown)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, target)
        temporary_name = None
    except OSError as exc:
        raise ScrapeError("output_write_failed") from exc
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
    return target


def main(argv: Iterable[str] | None = None, *, output_root: Path = SCRAPER_OUTPUT_ROOT) -> int:
    parser = argparse.ArgumentParser(description="Fetch one authorized public HTML page into Markdown.")
    parser.add_argument(
        "--confirm-authorized",
        action="store_true",
        required=True,
        help="confirm access is authorized and automated retrieval is permitted",
    )
    parser.add_argument("url", help="public HTTP(S) URL")
    parser.add_argument("output_file", nargs="?", help="Markdown filename under scratch/scraper")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        html_bytes = fetch_html(
            args.url, authorization_confirmed=args.confirm_authorized
        )
        markdown = convert_html_to_markdown(html_bytes)
        write_markdown(markdown, args.output_file, output_root)
    except ScrapeError as exc:
        print(f"[Execution Error] {exc.code}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - keep URLs, paths, and response data out of logs
        print(f"[Execution Error] unexpected_{type(exc).__name__}", file=sys.stderr)
        return 1

    print(f"[Execution Success] Saved Markdown output ({len(markdown)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
