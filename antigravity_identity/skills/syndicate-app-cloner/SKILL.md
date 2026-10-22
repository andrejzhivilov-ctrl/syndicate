---
name: syndicate-app-cloner
description: Practical end-to-end pipeline for analyzing, reverse-engineering, and cloning mobile (Google Play / Android APK / iOS) and desktop/web applications into the SYNDICATE ecosystem. Combines replica-recon, replica-test, rea-reverse-engineering, and Syndicate NeuroFlow dark-glass UI design. Use whenever Andrii provides Google Play links, APKs, screenshots, or app references to clone or adapt for the Syndicate PC/Smartphone apps.
---

# Syndicate App Cloner & Feature Extractor (`syndicate-app-cloner`)

## Purpose
Transform external reference applications (Google Play apps, desktop tools, dashboards, fintech/health/productivity trackers) into clean-room, production-ready modules and UI screens inside the **SYNDICATE** PC & Smartphone ecosystem.

## 5-Step Practical Pipeline

### 1. Reconnaissance & Feature Matrix (`replica-recon` + `rea-reverse-engineering`)
- **Input Sources:** Google Play URLs, APK/AAB packages, screenshots, walkthrough videos, or public API docs.
- **Deliverables:**
  - `Screen Inventory (S01..Sxx)`: Every screen, route, state (`empty`, `loading`, `filled`, `error`, `offline`), and navigation transition.
  - `User Flows (F01..Fxx)`: Happy path click count + edge cases.
  - `Inferred Data Model`: Entities, fields, types, and relationships mapped to Syndicate's PostgreSQL / pgvector / SQLite local-first schema.
  - `Feature Matrix`: `must / should / could / skip` priorities.

### 2. Syndicate Architectural Mapping (Radial Boardroom Integration)
Map extracted app features directly to the responsible **Syndicate Director**:
- **Command & Briefing UI** -> `eva` (Chief of Staff, Morning/Evening Briefing, Voice switch)
- **Finance, Ledger, Subscriptions & Crypto/FOP** -> `fin` (CFO)
- **Trading, Charts & Orderflow** -> `sam` (Quant & Markets)
- **Sports Betting, Odds & Value Calculator** -> `jack` (Betting Quant — PariMatch, Vbet, Pinnacle, Kelly sizing)
- **Clinical Biomarkers, HRV & Medical ID** -> `doc` (Chief Medical Officer)
- **Workouts, RPE, Periodization & KBJU/Nutrition** -> `trainer` (Physical Performance Director)
- **Knowledge Graph, Second Brain & Media Archive** -> `kodex` (Chief Archivist — NotebookLM ↔ Obsidian Task Web)
- **Academy, Flashcards & Socratic Code/Language Tutor** -> `kira` (Dean of Academy)
- **Creative Studio & Viral Media** -> `oscar`
- **E-Commerce & Price/Supplier Scout** -> `tyler`
- **Zero-Trust Security & Audit** -> `marshal`
- **Code, n8n Workflows & VM Contractor Bridge** -> `architect` + `antigravity`

### 3. Visual & UX Adaptation (Syndicate NeuroFlow Design System)
Apply our signature **NeuroFlow Dark Glass** aesthetic:
- **Backgrounds:** Deep obsidian (`#0a0b10`, `#12141d`) with `backdrop-filter: blur(20px)` glassmorphism panels.
- **Accents:** High-contrast tactical orange (`#ff5500`), cyber emerald (`#00e676`), electric cyan (`#00e5ff`), and warning amber (`#ffb300`).
- **Layout:** Bento-grid telemetry cards, radial Boardroom selector (no legacy floors!), tactile micro-interactions, and responsive Desktop (Electron/Tauri/Web) + Mobile (PWA/React Native/Flutter) viewports.

### 4. Clean-Room Implementation
- Write modular, self-contained frontend + FastAPI/WebSocket backend handlers.
- Never copy proprietary assets, trademarks, or hardcoded third-party tokens.
- Ensure offline/degraded resilience (explicit `unavailable` status when sensors or APIs are offline, never fake metrics).

### 5. E2E Verification (`replica-test` + `webapp-testing`)
- Verify every cloned screen and flow against the feature matrix (`empty`, `populated`, `error`, and `unauthorized` states).
- Run automated pytest / Playwright checks before committing to `main`.
