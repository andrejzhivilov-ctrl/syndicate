# Directive: Scrape Website to Markdown

## Goal
Scrape any given target URL and extract clean, token-efficient Markdown content without ads, navbars, or cookie notices.

## Inputs
- `target_url`: The URL to scrape.
- `output_format`: Defaults to markdown.

## Tools & Execution Scripts
- Use `execution/scrape_single_site.py <url> [output_file.md]`
- Script uses MarkItDown or Firecrawl (if installed / API provided) or requests + BeautifulSoup.

## Output
- Clean `.md` file in `.tmp/` or designated deliverables path.
- Extracted title, headings, and core body text.

## Edge Cases & Annealing Notes
- If Cloudflare challenge detected: Switch from basic fetch to Firecrawl API or Playwright scraper.
- If content is empty: Check for client-side JavaScript rendering requirement.
