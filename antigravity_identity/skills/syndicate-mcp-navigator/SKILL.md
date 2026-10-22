---
name: syndicate-mcp-navigator
description: Practical catalog, selector, and configuration builder over SYNDICATE's 18,789 MCP servers across 70 categories (mcp_servers/) and the governed MCP Server Pool (mcp_servers/pool/registry.json). Use when selecting, reviewing, or configuring MCP servers for Antigravity or Syndicate directors.
---

# Syndicate MCP Navigator & Practical Arsenal (`syndicate-mcp-navigator`)

## 1. Repository MCP Architecture
The Syndicate repository contains a complete indexed snapshot of **18,789 MCP servers across 70 categories** in `mcp_servers/`:
- **Governed Pool Manifest:** `mcp_servers/pool/registry.json`
- **Category Catalogs:** `mcp_servers/categories/01_Development.md` through `70_Identity.md`
- **Full JSON Registry:** `mcp_servers/mcp_servers_registry.json`

## 2. Core Practical MCP Arsenal for Antigravity (VM Super-Agent) & Directors
When configuring MCP servers on the 24/7 VM or local workstation, prioritize these vetted, high-utility servers:

| MCP Server | Category | Primary Use in SYNDICATE | Target Agents |
|---|---|---|---|
| `mcp-server-time` | `02_Productivity` |Pinned IANA timezone & UTC/Kyiv conversion (`2026.10.10`) | All Directors, Eva, Kodex |
| `mcp-server-filesystem` | `24_File_System` | Sandboxed read/write access to Obsidian Vault & workspace | Antigravity, Kodex, Architect |
| `mcp-server-git` / `github` | `21_Version_Control` | Git tree inspection, branch management, PR & diff review | Antigravity, Architect |
| `mcp-server-postgres` | `09_Database` | Read-only schema inspection & pgvector telemetry queries | Antigravity, Architect, Fin, Sam |
| `mcp-server-playwright` | `25_Browser_Automation` | Headless UI testing, screenshot capture, web app verification | Antigravity, Oscar, Tyler, Jack |
| `firecrawl-mcp` | `11_Web_Scraping` | Clean LLM-ready Markdown extraction from docs & web pages | Antigravity, Kodex, Kira |
| `mcp-obsidian` | `13_Knowledge___Memory` | Direct graph/backlink traversal & frontmatter search in Obsidian | Kodex, Eva, Kira, All Directors |
| `mcp-server-docker` | `20_Cloud_Platforms` | Container health inspection, log streaming, compose verification | Antigravity, Architect, Marshal |

## 3. Zero-Trust Governance Rules for MCP (`Marshal` & `Architect`)
1. **Catalog != Approval:** Entries in `mcp_servers/categories/*.md` are discovery metadata only.
2. **Pinning & Hash Verification:** Before enabling any MCP server in production, pin its package version and artifact SHA-256 in `mcp_servers/pool/registry.json`.
3. **Least Privilege:** Bind each MCP server to explicit tool allowlists and pass credentials exclusively via environment variables / HashiCorp Vault (`secret/data/syndicate/mcp`).
