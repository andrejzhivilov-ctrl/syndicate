from __future__ import annotations

import socket
import stat
from pathlib import Path
from typing import Any, Dict

import pytest

from execution import scrape_single_site as scraper


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("file:///etc/passwd", "invalid_url"),
        ("http://127.0.0.1/", "unsafe_host"),
        ("http://127.1/", "unsafe_host"),
        ("http://2130706433/", "unsafe_host"),
        ("http://[::1]/", "unsafe_host"),
        ("http://[64:ff9b::7f00:1]/", "unsafe_host"),
        ("http://[2002:7f00:1::]/", "unsafe_host"),
        ("http://user:password@example.com/", "unsafe_url"),
        ("http://example.com:8080/", "unsafe_port"),
        ("http://example.com:0/", "unsafe_port"),
        ("http://localhost/", "unsafe_host"),
        ("http://service.internal/", "unsafe_host"),
    ],
)
def test_url_validator_rejects_unsafe_targets(url: str, code: str):
    with pytest.raises(scraper.ScrapeError) as error:
        scraper.parse_and_validate_url(url)
    assert error.value.code == code


def test_url_validator_normalizes_idn_and_percent_encodes_path():
    parsed = scraper.parse_and_validate_url("https://exämple.com/über uns?q=käse")
    assert parsed.scheme == "https"
    assert parsed.host == "xn--exmple-cua.com"
    assert parsed.request_target == "/%C3%BCber%20uns?q=k%C3%A4se"
    assert parsed.host_header == "xn--exmple-cua.com"


def test_dns_rejects_a_mixed_public_and_private_answer_set(monkeypatch):
    records = [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("93.184.216.34", 0)),
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("10.0.0.8", 0)),
    ]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: records)
    with pytest.raises(scraper.ScrapeError, match="unsafe_host"):
        scraper.resolve_public_addresses("example.com")


def test_dns_rejects_nat64_ipv4_translation_to_loopback(monkeypatch):
    records = [
        (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("64:ff9b::7f00:1", 0, 0, 0)),
    ]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: records)
    with pytest.raises(scraper.ScrapeError, match="unsafe_host"):
        scraper.resolve_public_addresses("example.com")


def test_fetch_api_requires_authorization_confirmation_before_dns():
    with pytest.raises(scraper.ScrapeError, match="authorization_confirmation_required"):
        scraper.fetch_html("https://example.com/")


def test_fetch_revalidates_and_pins_each_public_redirect():
    requests = []
    resolved = []
    responses = [
        scraper.FetchResponse(302, {"Location": "https://other.example.com/article"}),
        scraper.FetchResponse(
            200,
            {"Content-Type": "text/html; charset=utf-8", "Content-Length": "4"},
            b"html",
        ),
    ]

    def resolver(host: str):
        resolved.append(host)
        return ["93.184.216.34"]

    def requester(parsed: scraper.ParsedURL, address: str, **_kwargs: Any):
        requests.append((parsed.host, address))
        return responses.pop(0)

    assert scraper.fetch_html(
        "https://example.com/start",
        authorization_confirmed=True,
        resolver=resolver,
        requester=requester,
    ) == b"html"
    assert resolved == ["example.com", "other.example.com"]
    assert requests == [
        ("example.com", "93.184.216.34"),
        ("other.example.com", "93.184.216.34"),
    ]


def test_private_redirect_is_rejected_before_a_second_request():
    request_count = 0

    def requester(_parsed: scraper.ParsedURL, _address: str, **_kwargs: Any):
        nonlocal request_count
        request_count += 1
        return scraper.FetchResponse(302, {"Location": "http://127.0.0.1/admin"})

    with pytest.raises(scraper.ScrapeError, match="unsafe_host"):
        scraper.fetch_html(
            "https://example.com/",
            authorization_confirmed=True,
            resolver=lambda _host: ["93.184.216.34"],
            requester=requester,
        )
    assert request_count == 1


def test_https_redirect_cannot_downgrade_to_http():
    def requester(_parsed: scraper.ParsedURL, _address: str, **_kwargs: Any):
        return scraper.FetchResponse(302, {"Location": "http://other.example.com/page"})

    with pytest.raises(scraper.ScrapeError, match="https_downgrade_redirect"):
        scraper.fetch_html(
            "https://example.com/",
            authorization_confirmed=True,
            resolver=lambda _host: ["93.184.216.34"],
            requester=requester,
        )


class _FakeSocket:
    def settimeout(self, _timeout: float) -> None:
        pass


class _FakeConnection:
    sock = _FakeSocket()


class _FakeResponse:
    def __init__(self, data: bytes, headers: Dict[str, str] | None = None) -> None:
        self.data = data
        self.headers = headers or {}

    def read(self, amount: int) -> bytes:
        chunk, self.data = self.data[:amount], self.data[amount:]
        return chunk


def test_bounded_reader_enforces_content_length_and_stream_limits():
    with pytest.raises(scraper.ScrapeError, match="response_too_large"):
        scraper._read_bounded_body(
            _FakeResponse(b"", {"Content-Length": "6"}),
            _FakeConnection(),
            max_bytes=5,
            deadline=10**12,
        )

    with pytest.raises(scraper.ScrapeError, match="response_too_large"):
        scraper._read_bounded_body(
            _FakeResponse(b"123456"),
            _FakeConnection(),
            max_bytes=5,
            deadline=10**12,
        )


def test_output_path_is_scratch_only_and_rejects_symlink(tmp_path: Path):
    root = tmp_path / "scratch" / "scraper"
    target = scraper.write_markdown("# public page", "result.md", root)
    assert target.read_text(encoding="utf-8") == "# public page"
    assert stat.S_IMODE(target.stat().st_mode) in (0o600, 0o666)

    with pytest.raises(scraper.ScrapeError, match="unsafe_output_path"):
        scraper.write_markdown("no", "../outside.md", root)
    with pytest.raises(scraper.ScrapeError, match="unsafe_output_path"):
        scraper.write_markdown("no", str(tmp_path / "outside.md"), root)
    with pytest.raises(scraper.ScrapeError, match="unsafe_output_path"):
        scraper.write_markdown("no", "C:alternate-stream.md", root)

    outside = tmp_path / "outside.md"
    outside.write_text("keep", encoding="utf-8")
    link = root / "linked.md"
    try:
        link.symlink_to(outside)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks are unavailable in this environment")
    with pytest.raises(scraper.ScrapeError, match="unsafe_output_path"):
        scraper.write_markdown("overwrite", "linked.md", root)
    assert outside.read_text(encoding="utf-8") == "keep"


def test_default_scratch_symlink_is_rejected_before_directory_creation(tmp_path, monkeypatch):
    scratch = tmp_path / "scratch"
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        scratch.symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError):
        pytest.skip("symlinks are unavailable in this environment")
    expected_root = scratch / "scraper"
    monkeypatch.setattr(scraper, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(scraper, "SCRAPER_OUTPUT_ROOT", expected_root)

    with pytest.raises(scraper.ScrapeError, match="unsafe_output_path"):
        scraper.resolve_output_path("page.md", expected_root)
    assert not (outside / "scraper").exists()


def test_cli_requires_explicit_authorization_before_fetch(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(scraper, "fetch_html", lambda _url: calls.append(_url))
    with pytest.raises(SystemExit) as error:
        scraper.main(["https://example.com/"])
    assert error.value.code == 2 and calls == []
    assert "https://example.com" not in capsys.readouterr().err


def test_cli_does_not_print_the_full_url_or_write_outside_scratch(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(scraper, "fetch_html", lambda _url, **_kwargs: b"synthetic html")
    monkeypatch.setattr(scraper, "convert_html_to_markdown", lambda _body: "# Safe result")
    result = scraper.main(["--confirm-authorized", "https://example.com/?token=not-for-logs", "page.md"], output_root=tmp_path)
    captured = capsys.readouterr()

    assert result == 0
    assert "token=not-for-logs" not in captured.out
    assert (tmp_path / "page.md").read_text(encoding="utf-8") == "# Safe result"
