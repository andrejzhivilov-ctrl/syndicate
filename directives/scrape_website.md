# Directive: Scrape a Public Website to Markdown

## Goal and authorization

Fetch one public, static HTML page and convert it to Markdown. Use this only for pages the operator is authorized to access and where automated retrieval is permitted. Do not scrape private/account-only content, submit forms, evade paywalls, defeat rate limits, or bypass Cloudflare or other access controls.

## Inputs

- `target_url`: an `http` or `https` URL on a publicly routable host, using port 80 or 443. URLs with embedded credentials and local/private destinations are rejected.
- `output_file`: optional Markdown filename. It must be a single filename and is written only under ignored `scratch/scraper/`; arbitrary paths are rejected.

## Execution

Run:

```text
python execution/scrape_single_site.py --confirm-authorized <url> [output_file.md]
```

The required `--confirm-authorized` flag is an operator attestation that access is authorized and automated retrieval is permitted; it is not a permission check or a way around a site's controls. The script uses a bounded direct HTTP(S) request with IP pinning, public-address checks for DNS and every redirect, a redirect limit, timeouts, and a 2 MiB response cap. It accepts HTML/XHTML only and converts the fetched bytes locally with MarkItDown. It does not execute JavaScript, use a browser, use ambient proxies, or invoke a cloud scraping service.

## Access-control and rendering limits

- If the page requires login, authorization, JavaScript execution, a CAPTCHA, or presents a bot/access-control challenge, stop. Request an approved API/export or operator-authorized access path; do not switch to Firecrawl, Playwright, proxy rotation, stealth mode, or another bypass.
- Respect the site's published terms, robots guidance, rate limits, and applicable law. Do not repeatedly retry a denied request.
- Dynamic content may be absent. Report that limitation as unavailable rather than attempting to evade the site's controls.

## Output

Markdown is stored in `scratch/scraper/` with private file permissions. Do not copy scraped personal, confidential, or access-controlled data into Git, logs, chat, or deliverables.
