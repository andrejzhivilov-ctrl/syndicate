---
name: firecrawl-scraper
description: >-
  Deep web scraping and crawling using Firecrawl API / MCP. Bypasses JavaScript rendering,
  Cloudflare, anti-bot protections, and converts any web page directly into clean LLM-ready Markdown.
  Use when normal fetch/curl fails, or when deep crawling an entire documentation site is required.
---

# Firecrawl Scraper & Web Researcher

Extract clean Markdown from modern Single Page Applications (SPA), protected sites, and full domains.

## Python Usage (Installed via firecrawl-py)

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-YOUR_API_KEY")

# Scrape a single URL to Markdown
scrape_result = app.scrape_url('https://example.com', params={'formats': ['markdown']})
print(scrape_result['markdown'])

# Crawl an entire documentation site
crawl_result = app.crawl_url('https://example.com/docs', params={'limit': 10, 'scrapeOptions': {'formats': ['markdown']}})
```

## CLI / Direct Scrape Helper
Use Python script in `execution/scrape_url.py` for deterministic execution.
