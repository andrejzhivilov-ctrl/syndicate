# -*- coding: utf-8 -*-
"""
Execution script: scrape_single_site.py
Deterministic layer 3 script for scraping web pages into clean Markdown.
Supports: MarkItDown (local) & Firecrawl (cloud fallback).
"""

import sys
import os
import urllib.request
from markitdown import MarkItDown

def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_single_site.py <url> [output_file.md]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(".tmp", "scraped_content.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"[Execution] Scraping {url}...")
    
    # 1. Fetch HTML
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_bytes = resp.read()
    except Exception as e:
        print(f"[Execution Error] Failed to fetch URL: {e}")
        sys.exit(1)

    # 2. Convert to Markdown using MarkItDown
    import io
    md = MarkItDown()
    result = md.convert_stream(io.BytesIO(html_bytes), file_extension='.html')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.text_content)

    print(f"[Execution Success] Saved to {output_file} ({len(result.text_content)} chars)")

if __name__ == "__main__":
    main()
