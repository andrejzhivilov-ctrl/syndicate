"""Alex reads books from the vault in parts: PDF, EPUB, DOCX, text; nothing guessed."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from src import material_reader as reader


def _pdf_with_text(lines):
    """A minimal real PDF: one page per line, Helvetica text."""
    objects = ["<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(len(lines)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(lines)} >>")
    font = 3 + 2 * len(lines)
    for i, line in enumerate(lines):
        stream = f"BT /F1 12 Tf 72 720 Td ({line}) Tj ET"
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                       f"/Resources << /Font << /F1 {font} 0 R >> >> /Contents {4 + 2 * i} 0 R >>")
        objects.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1"))
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        out.write(f"{offset:010d} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


def _blank_pdf():
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def _epub(chapters):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml",
                         '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                         '<rootfile full-path="OEBPS/content.opf"/></rootfiles></container>')
        items = "".join(f'<item id="c{i}" href="c{i}.xhtml"/>' for i in range(len(chapters)))
        # Spine order is deliberately the reverse of the manifest: reading follows the spine.
        spine = "".join(f'<itemref idref="c{i}"/>' for i in reversed(range(len(chapters))))
        archive.writestr("OEBPS/content.opf",
                         f'<package xmlns="http://www.idpf.org/2007/opf"><manifest>{items}</manifest>'
                         f"<spine>{spine}</spine></package>")
        for i, text in enumerate(chapters):
            archive.writestr(f"OEBPS/c{i}.xhtml", f"<html><head><style>x{{}}</style></head>"
                                                   f"<body><h1>Розділ</h1><p>{text}</p></body></html>")
    return out.getvalue()


def _docx(paragraphs):
    import docx

    document = docx.Document()
    for text in paragraphs:
        document.add_paragraph(text)
    out = io.BytesIO()
    document.save(out)
    return out.getvalue()


@pytest.fixture()
def vault(tmp_path):
    root = tmp_path / "vault"
    (root / "Health_Coach" / "Матеріали").mkdir(parents=True)
    (root / ".obsidian").mkdir()
    return root


def test_each_format_reads_as_text_with_pdf_page_marks(vault, tmp_path):
    folder = vault / "Health_Coach" / "Матеріали"
    (folder / "Hypertrophy.pdf").write_bytes(_pdf_with_text(["Volume drives growth", "Rest two minutes"]))
    (folder / "Харчування.epub").write_bytes(_epub(["Білок 1.6 г на кг", "Вступ"]))
    (folder / "Курс.docx").write_bytes(_docx(["Тиждень 1: техніка", "Тиждень 2: обсяг"]))
    cache = tmp_path / "cache"

    pdf = reader.read_material(vault, "Health_Coach/Матеріали/Hypertrophy.pdf", cache_dir=cache)
    assert pdf["status"] == "ok" and "[стор. 2]" in pdf["text"] and "Rest two minutes" in pdf["text"]
    epub = reader.read_material(vault, "Health_Coach/Матеріали/Харчування.epub", cache_dir=cache)
    assert epub["text"].index("Вступ") < epub["text"].index("Білок")  # spine order
    assert "x{}" not in epub["text"]
    docx_part = reader.read_material(vault, "Health_Coach/Матеріали/Курс.docx", cache_dir=cache)
    assert "Тиждень 2: обсяг" in docx_part["text"]
    assert list(cache.glob("*.txt")), "extracted text is cached outside the vault"


def test_a_long_book_is_read_part_by_part(vault, tmp_path):
    (vault / "book.txt").write_text("а" * (reader.PART_CHARS * 2 + 10), encoding="utf-8")
    first = reader.read_material(vault, "book.txt", 1, cache_dir=tmp_path / "c")
    last = reader.read_material(vault, "book.txt", 3, cache_dir=tmp_path / "c")
    assert first["parts"] == 3 and len(first["text"]) == reader.PART_CHARS and len(last["text"]) == 10
    assert reader.read_material(vault, "book.txt", 4, cache_dir=tmp_path / "c")["error"] == "part_out_of_range"


def test_a_scan_or_a_bad_file_is_reported_never_guessed(vault, tmp_path, monkeypatch):
    (vault / "scan.pdf").write_bytes(_blank_pdf())
    (vault / "broken.epub").write_bytes(b"not a zip")
    (vault / "notes.xlsx").write_bytes(b"x")
    cache = tmp_path / "c"
    assert reader.read_material(vault, "scan.pdf", cache_dir=cache)["reason"] == "no_text_layer"
    assert reader.read_material(vault, "broken.epub", cache_dir=cache)["reason"] == "damaged_file"
    assert reader.read_material(vault, "notes.xlsx", cache_dir=cache)["reason"] == "unsupported_format"
    (vault / "big.epub").write_bytes(_epub(["x" * 5000]))
    monkeypatch.setattr(reader, "MAX_UNZIPPED_BYTES", 1000)
    assert reader.read_material(vault, "big.epub", cache_dir=cache)["reason"] == "too_large_unpacked"


def test_nothing_outside_the_vault_is_readable(vault, tmp_path):
    (tmp_path / "secret.txt").write_text("outside", encoding="utf-8")
    for path in ("../secret.txt", str(tmp_path / "secret.txt"), "Health_Coach/../../secret.txt"):
        assert reader.read_material(vault, path, cache_dir=tmp_path / "c")["reason"] == "not_found", path


def test_list_finds_books_but_skips_notes_and_hidden_folders(vault):
    (vault / "Health_Coach" / "Матеріали" / "Hypertrophy.pdf").write_bytes(b"%PDF")
    (vault / "Health_Coach" / "План.md").write_text("нотатка", encoding="utf-8")
    (vault / ".obsidian" / "cache.txt").write_text("x", encoding="utf-8")
    found = reader.list_materials(vault, "матеріали")
    assert [item["path"] for item in found["items"]] == ["Health_Coach/Матеріали/Hypertrophy.pdf"]
    assert reader.list_materials(vault, "")["found"] == 1


def test_the_gateway_masks_material_text_and_counts_parts(vault, tmp_path, monkeypatch):
    from src import hermes_tools as tools

    (vault / "card.txt").write_text("Телефон тренера +380671234567", encoding="utf-8")
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", str(vault))
    monkeypatch.setenv("EVA_DATA_DIR", str(tmp_path / "data"))
    result = tools.material_read("card.txt", "1")
    assert result["status"] == "ok" and "671234" not in result["text"]
    assert tools.material_read("card.txt", "two")["error"] == "part_not_a_number"
    assert Path(tmp_path / "data" / "materials_text_cache").is_dir()
