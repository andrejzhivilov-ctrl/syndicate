---
name: markitdown
description: >-
  Universal file conversion tool by Microsoft. Converts PDF, DOCX, PPTX, XLSX, HTML, images (OCR),
  audio (transcription), ZIP, and YouTube URLs into clean, token-efficient Markdown for LLM analysis.
  Use whenever the user provides documents or asks to parse, extract, or convert office files or media into Markdown.
---

# MarkItDown Skill (Microsoft)

Convert office documents, PDFs, presentations, spreadsheets, and media files to Markdown.

## Capabilities

MarkItDown supports converting:
- **PDFs**: Text, headers, tables, structure.
- **PowerPoint (.pptx)**: Slides, notes, shapes, text hierarchy.
- **Word (.docx)**: Headings, bullet points, formatted text, tables.
- **Excel (.xlsx, .xls)**: Spreadsheets into clean Markdown tables.
- **HTML**: Web pages into clean Markdown without DOM junk.
- **Images**: OCR and EXIF metadata extraction.
- **Audio**: Speech transcription and audio metadata.
- **ZIP files**: Iterates through nested archives.

## Usage in Python

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("path/to/document.pdf")
print(result.text_content)
```

## CLI Usage

Run via the Python environment:
```powershell
scratch\uv\venv\Scripts\python.exe -m markitdown input.pdf -o output.md
```

Or convert directly using the helper script `scripts/convert.py`:
```powershell
python scripts/convert.py <input_file> [output_file]
```
