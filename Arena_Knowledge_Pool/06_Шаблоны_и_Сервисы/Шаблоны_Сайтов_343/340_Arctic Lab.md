---
title: "Arctic Lab"
template_id: "aff0e95a-3272-4f1c-82e4-645f688f2bed"
section: "sites"
category_slug: "portfolio"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/07f910ce-219d-4a92-89d8-90f70946bb4a.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Arctic Lab

> **Секція:** `SITES` | **Категорія:** `portfolio`  
> **ID шаблону:** `aff0e95a-3272-4f1c-82e4-645f688f2bed`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Portfolio

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/07f910ce-219d-4a92-89d8-90f70946bb4a.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
|Build a single-page "IGLOO" concept site using Vite + React 18 + TypeScript + Tailwind CSS 3 + framer-motion + lucide-react. Recreate it EXACTLY as specified below.

## 1. FONTS (load in index.html <head>, in this exact order)

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
<link href="https://db.onlinewebfonts.com/c/6464eb173643efcc64e904b96201d0cc?family=Dimensions+W03+300R" rel="stylesheet" />
```

Font usage rules:
- Display headlines ("IGLOO" hero text and "WITH A VIEW"): `font-family: 'Dimensions W03 300R', 'Anton', sans-serif` — Dimensions W03 300R is the primary display face (a tall condensed stencil-style font loaded from onlinewebfonts.com); **Anton (Google Fonts) is the explicit fallback for headlines only**, so if the onlinewebfonts stylesheet fails or is blocked in any browser, headlines render in Anton, never in a default sans.
- Body/UI text: `font-family: 'Inter', sans-serif` (weights 300/400/500/600), set globally on `body`.
- Hero description paragraph: `font-family: 'Courier New', monospace`.
- Page `<title>`: IGLOO.

Global CSS (index.css); body has Inter, `-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`, `overflow-x: hidden`.

## 2. ASSETS (exact URLs)

Page background (shared, spans both sections):
`https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260723_224514_a4f5778c-5a68-4e60-b9f8-74aeec2ef48b.png&w=1920&q=85`

Overlay image (iceberg cutout, sits in front of background but behind ALL UI, spans both sections, pointer-events-none):
`https://soft-zoom-63098134.figma.site/_assets/v11/7e3b4feb333e9a78d12d5afc7d48730615390ec2.png`

Left-side thumbnails (top to bottom, 4 images):
1. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094505_c14a7566-ec38-46cf-b298-b641815acbdc.png&w=1280&q=85`
2. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094527_33af18d8-e52c-49a6-8b9b-4706b0c0a85a.png&w=1280&q=85`
3. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094546_3f85bc04-8e66-4d82-aa27-fcf40742a384.png&w=1280&q=85`
4. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094606_79a7fc4d-cf64-48bc-a2d3-52dd5ad6ffe3.png&w=1280&q=85`

"With A View" cards (3 cards, in order, with titles):
1. "Cliffside Retreat" — `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101354_a5a857b7-b9ce-4e3f-9cc1-27424c9e4c8d.png&w=1280&q=85`
2. "Island Escape" — `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101420_1c0cbb04-a7b5-41f1-9d21-fcf3976f6be6.png&w=1280&q=85`
3. "Coastal Haven" — `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101434_83163d4d-1639-4812-8753-e679652939ff.png&w=1280&q=85`

## 3. PAGE STRUCTURE

Root `<div style="background-color:#D6D7DD">` containing:
(a) a MobileMenu overlay component, and (b) a `relative overflow-hidden` wrapper that spans BOTH full-screen sections and holds two absolutely-positioned full-bleed images:
- Background `<img>`: `absolute inset-0 w-full h-full object-cover`, dynamic `objectPosition: center {focalY}%` and `transform: scale({scrollScale})` with `transformOrigin: top center` (see animation #2).
- Overlay `<img>`: identical positioning/animation, plus `z-[10] pointer-events-none`.

### SECTION 1 — Hero (`relative w-full h-screen overflow-hidden`)

1. **Giant "IGLOO" headline**: absolutely centered container `inset-0 flex items-start justify-center pt-[13vh] pointer-events-none z-[2]`. Text rendered with a per-letter animation component (see animation #1). Classes: `text-[36vw] md:text-[35vw] leading-[0.85] text-white/80 tracking-[0.01em] select-none`, font: Dimensions W03 300R → Anton fallback. It sits BEHIND the iceberg overlay (z-2 < z-10) so the iceberg visually cuts through the wordmark.

2. **Fixed navbar** (`fixed top-0 z-[40] flex items-center justify-between px-5 md:px-8 py-4 md:py-5`):
   - Left (desktop only, `hidden md:flex gap-10`): links PORTFOLIO, ABOUT, LAB — `text-xs font-semibold tracking-widest uppercase text-neutral-700 hover:text-neutral-900 transition-colors`, href="#".
   - Left (mobile only): hamburger Menu icon (lucide, size 22, strokeWidth 1.5) that opens the mobile menu.
   - Center: wordmark "IGLOO" — `text-sm tracking-[0.35em] text-neutral-600 uppercase`, font Inter.
   - Right (`flex gap-4 md:gap-5`): Instagram icon (desktop only) and Search icon, lucide size 18, strokeWidth 1.5, `text-neutral-700 hover:text-neutral-900`.

3. **Left thumbnail rail** (desktop only): `absolute left-4 md:left-6 top-1/2 -translate-y-1/2 z-[30] flex-col gap-3`; each thumb `w-12 md:w-16 h-12 md:h-16 rounded-lg overflow-hidden cursor-pointer hover:scale-105 transition-transform shadow-md` with object-cover image.

4. **Right scroll line** (desktop only): `absolute right-8 top-1/2 z-[30]`, a `w-px h-32 bg-neutral-500/60` vertical rule, vertically centered via translateY(-50%).

5. **Bottom caption**: `absolute bottom-8 md:bottom-12 left-1/2 -translate-x-1/2 z-[30] flex flex-col items-center gap-3 text-center px-6`:
   - Paragraph in 'Courier New', monospace: `text-[10px] md:text-xs tracking-widest text-white max-w-xs md:max-w-sm leading-relaxed`, text: "A conceptual vision of an igloo, afloat in the Arctic. Where minimalism, nature, and imagination converge."
   - Below it a lucide ChevronDown (size 16, white) with Tailwind `animate-bounce`.

### SECTION 2 — "With A View" (`relative z-[20] w-full h-screen overflow-hidden -mt-[20px]`)

Inner column `relative z-10 h-screen flex flex-col justify-between p-6 md:p-10 lg:p-16`:

1. Top block (`flex flex-col gap-4 pt-16`):
   - Heading row (`flex items-start`): per-letter animated text "With A View" rendered uppercase — `text-[18vw] md:text-[16vw] leading-[0.85] text-white tracking-[0.01em] uppercase`, font Dimensions W03 300R → Anton fallback, left-aligned; to its right (desktop only) a horizontal rule `flex-1 mt-[0.42em] ml-4` containing `w-full h-px bg-white/70`.
   - Subtext row (`flex md:justify-end`): paragraph `text-white text-sm md:text-base max-w-xs leading-relaxed md:text-right`: "Elevated sanctuaries perched above the clouds, where architecture meets the infinite horizon."

2. Bottom card grid: `grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 pb-4 max-w-4xl mx-auto mt-8 md:mt-0`. Each card: `group relative rounded-xl overflow-hidden aspect-[3/4] cursor-pointer max-h-[28vh]`; the 3rd card additionally `col-span-2 md:col-span-1 max-w-[50%] md:max-w-full mx-auto md:mx-0` (so on mobile it spans both columns but is half-width and centered). Image: `w-full h-full object-cover transition-transform duration-500 group-hover:scale-110`. Title overlaid `absolute bottom-3 left-3 right-3` as `text-white text-xs md:text-sm font-medium tracking-wide`.

### Mobile menu (z-[100] fixed overlay)
- Backdrop: `bg-black/60 backdrop-blur-sm`, fades opacity over 500ms, click closes.
- Panel: right-anchored drawer `w-[75vw] max-w-xs h-full bg-white/95 backdrop-blur-xl shadow-2xl`, slides in from `translate-x-full` over 500ms with easing `cubic-bezier(0.16,1,0.3,1)`. Contains an X close button (top-right, lucide size 24), the three nav links stacked (`text-lg font-semibold tracking-widest uppercase`, each fading/sliding in from `translate-x-8` with delays 150ms/230ms/310ms when open), and bottom-left Instagram + Search icons (size 20) fading up with 400ms delay. Opening sets `document.body.style.overflow = 'hidden'`; closing restores it.

## 4. ANIMATIONS (implement exactly)

1. **LettersPullUp** (framer-motion, used for both big headlines): split text into characters; each char is a `motion.span` with variants `initial: { y: 20, opacity: 0 }` → `animate: { y: 0, opacity: 1, transition: { delay: i * 0.05 } }` (i = char index), triggered once when the element scrolls into view (`useInView(ref, { once: true })`). Spaces render as `&nbsp;`. Wrapper is `flex flex-wrap` with justify-center by default, justify-start for the "With A View" heading.

2. **Scroll-driven background zoom/pan** (custom hook, applied to BOTH the background and overlay images): on scroll (rAF-throttled, passive listener), compute `progress = min(scrollY / window.innerHeight, 1)`; set `scale = 1 + progress * 0.12` (i.e. 1 → 1.12) and `focalY = progress * 100` (objectPosition drifts from `center 0%` to `center 100%`). Transform origin `top center`.

3. **Staggered reveal on scroll** (custom hook, IntersectionObserver, fires once): container observed at threshold 0.1 (hero) / 0.15 (view section); when intersecting, each indexed child transitions from `opacity: 0; translateY(24px)` to visible over `0.7s cubic-bezier(0.16,1,0.3,1)` with per-index delay — hero uses 150ms steps (headline=index 0, nav=2, thumbnails=3–6, right line=7, bottom caption=8), view section uses 200ms steps (heading=0, subtext=1, cards=2–4). For elements that also carry a centering transform (right line, bottom caption), compose it: e.g. hidden state `translateX(-50%) translateY(24px)` → visible `translateX(-50%)`.

4. **Micro-interactions**: thumbnail `hover:scale-105`; card image `group-hover:scale-110` (500ms); chevron `animate-bounce`; all link color transitions via `transition-colors`.

## 5. DEPENDENCIES

package.json deps: react ^18.3.1, react-dom ^18.3.1, framer-motion ^12, lucide-react ^0.344.0, @vitejs/plugin-react, tailwindcss ^3.4, typescript ^5.5, vite ^5.4. Tailwind config: default, content `./index.html` + `./src/**/*.{js,ts,jsx,tsx}`. Vite config: react plugin, `optimizeDeps.exclude: ['lucide-react']`.

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>IGLOO</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <link href="https://db.onlinewebfonts.com/c/6464eb173643efcc64e904b96201d0cc?family=Dimensions+W03+300R" rel="stylesheet" />
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
      background: #D6D7DD;
    }

    /* ===== LAYOUT ===== */
    .page-wrapper { background-color: #D6D7DD; }
    .shared-container { position: relative; overflow: hidden; }
    .shared-bg, .overlay-img {
      position: absolute; inset: 0; width: 100%; height: 100%;
      object-fit: cover; transform-origin: top center;
    }
    .overlay-img { z-index: 10; pointer-events: none; }
    .hero-section { position: relative; width: 100%; height: 100vh; overflow: hidden; }
    .view-section {
      position: relative; z-index: 20; width: 100%; height: 100vh;
      overflow: hidden; margin-top: -20px;
    }

    /* ===== HEADING ===== */
    .hero-heading-wrapper {
      position: absolute; inset: 0; display: flex; align-items: flex-start;
      justify-content: center; padding-top: 13vh; pointer-events: none; z-index: 2;
    }
    .hero-heading {
      display: flex; flex-wrap: wrap; justify-content: center;
    }
    .hero-heading .letter {
      font-family: 'Dimensions W03 300R', sans-serif;
      font-size: 35vw; line-height: 0.85; color: rgba(255,255,255,0.8);
      letter-spacing: 0.01em; user-select: none;
      opacity: 0; transform: translateY(20px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }
    .hero-heading.revealed .letter {
      opacity: 1; transform: translateY(0);
    }

    /* ===== NAV ===== */
    .main-nav {
      position: fixed; top: 0; left: 0; right: 0; z-index: 40;
      display: flex; align-items: center; justify-content: space-between;
      padding: 16px 20px;
      opacity: 0; transform: translateY(24px);
      transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1) 300ms, transform 0.7s cubic-bezier(0.16,1,0.3,1) 300ms;
    }
    .main-nav.revealed { opacity: 1; transform: translateY(0); }
    .nav-links { display: none; align-items: center; gap: 40px; }
    .nav-links a {
      font-size: 12px; font-weight: 600; letter-spacing: 0.1em;
      color: #404040; text-decoration: none; text-transform: uppercase;
      transition: color 0.3s;
    }
    .nav-links a:hover { color: #171717; }
    .nav-brand {
      font-size: 14px; letter-spacing: 0.35em; color: #525252;
      font-weight: 400; text-transform: uppercase; font-family: 'Inter', sans-serif;
    }
    .nav-right { display: flex; align-items: center; gap: 16px; }
    .nav-right a, .hamburger { color: #404040; transition: color 0.3s; cursor: pointer; background: none; border: none; }
    .nav-right a:hover, .hamburger:hover { color: #171717; }
    .nav-right .desktop-only { display: none; }
    .hamburger { display: block; }

    /* ===== SIDE THUMBNAILS ===== */
    .side-thumbnails {
      position: absolute; left: 24px; top: 50%; transform: translateY(-50%);
      z-index: 30; display: none; flex-direction: column; gap: 12px;
    }
    .side-thumbnails .thumb {
      width: 64px; height: 64px; border-radius: 8px; overflow: hidden;
      cursor: pointer; transition: transform 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.15);
      opacity: 0; transform: translateY(24px);
      transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1);
    }
    .side-thumbnails .thumb:hover { transform: scale(1.05) !important; }
    .side-thumbnails .thumb img { width: 100%; height: 100%; object-fit: cover; }
    .side-thumbnails.revealed .thumb { opacity: 1; transform: translateY(0); }

    /* ===== RIGHT SCROLL LINE ===== */
    .right-line {
      position: absolute; right: 32px; top: 50%; transform: translateY(-50%);
      z-index: 30; display: none; flex-direction: column; align-items: center; gap: 8px;
      opacity: 0; transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1) 1050ms;
    }
    .right-line.revealed { opacity: 1; }
    .right-line div { width: 1px; height: 128px; background: rgba(115,115,115,0.6); }

    /* ===== BOTTOM TEXT ===== */
    .bottom-text {
      position: absolute; bottom: 48px; left: 50%; transform: translateX(-50%) translateY(24px);
      z-index: 30; display: flex; flex-direction: column; align-items: center;
      gap: 12px; text-align: center; padding: 0 24px;
      opacity: 0; transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1) 1200ms, transform 0.7s cubic-bezier(0.16,1,0.3,1) 1200ms;
    }
    .bottom-text.revealed { opacity: 1; transform: translateX(-50%) translateY(0); }
    .bottom-text p {
      font-family: 'Courier New', monospace; font-size: 10px;
      letter-spacing: 0.1em; color: white; max-width: 256px; line-height: 1.625;
    }
    .bounce-arrow {
      color: white; animation: bounce 1s infinite;
    }
    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-25%); }
    }

    /* ===== VIEW SECTION ===== */
    .view-inner {
      position: relative; z-index: 10; height: 100vh;
      display: flex; flex-direction: column; justify-content: space-between;
      padding: 24px;
    }
    .view-top { display: flex; flex-direction: column; gap: 16px; padding-top: 64px; }
    .view-heading-row { display: flex; align-items: flex-start; }
    .view-heading { display: flex; flex-wrap: wrap; justify-content: flex-start; }
    .view-heading .letter {
      font-family: 'Dimensions W03 300R', sans-serif;
      font-size: 18vw; line-height: 0.85; color: white;
      letter-spacing: 0.01em; text-transform: uppercase;
      opacity: 0; transform: translateY(20px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }
    .view-heading.revealed .letter { opacity: 1; transform: translateY(0); }
    .view-line {
      display: none; flex: 1; margin-top: 0.42em; margin-left: 16px;
    }
    .view-line div { width: 100%; height: 1px; background: rgba(255,255,255,0.7); }
    .view-subtext-row {
      display: flex; opacity: 0; transform: translateY(24px);
      transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1) 200ms, transform 0.7s cubic-bezier(0.16,1,0.3,1) 200ms;
    }
    .view-subtext-row.revealed { opacity: 1; transform: translateY(0); }
    .view-subtext {
      color: white; font-size: 14px; max-width: 320px; line-height: 1.625;
    }
    .view-cards {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
      max-width: 896px; margin: 32px auto 16px; padding-bottom: 16px;
    }
    .view-card {
      position: relative; border-radius: 12px; overflow: hidden;
      aspect-ratio: 3/4; cursor: pointer; max-height: 28vh;
      opacity: 0; transform: translateY(24px);
      transition: opacity 0.7s cubic-bezier(0.16,1,0.3,1), transform 0.7s cubic-bezier(0.16,1,0.3,1);
    }
    .view-card.revealed { opacity: 1; transform: translateY(0); }
    .view-card:nth-child(3) {
      grid-column: span 2; max-width: 50%; margin: 0 auto;
    }
    .view-card img {
      width: 100%; height: 100%; object-fit: cover;
      transition: transform 0.5s;
    }
    .view-card:hover img { transform: scale(1.1); }
    .view-card .card-title {
      position: absolute; bottom: 12px; left: 12px; right: 12px;
      color: white; font-size: 12px; font-weight: 500; letter-spacing: 0.025em;
    }

    /* ===== MOBILE MENU ===== */
    .mobile-overlay {
      position: fixed; inset: 0; z-index: 100; visibility: hidden;
      transition: visibility 0s 0.5s;
    }
    .mobile-overlay.open { visibility: visible; transition-delay: 0s; }
    .mobile-overlay-bg {
      position: absolute; inset: 0; background: rgba(0,0,0,0.6);
      backdrop-filter: blur(4px); opacity: 0; transition: opacity 0.5s;
    }
    .mobile-overlay.open .mobile-overlay-bg { opacity: 1; }
    .mobile-drawer {
      position: absolute; top: 0; right: 0; height: 100%;
      width: 75vw; max-width: 320px;
      background: rgba(255,255,255,0.95); backdrop-filter: blur(16px);
      box-shadow: -10px 0 40px rgba(0,0,0,0.15);
      transform: translateX(100%);
      transition: transform 0.5s cubic-bezier(0.16,1,0.3,1);
    }
    .mobile-overlay.open .mobile-drawer { transform: translateX(0); }
    .drawer-close {
      position: absolute; top: 20px; right: 20px; background: none; border: none;
      color: #404040; cursor: pointer; transition: color 0.3s;
    }
    .drawer-close:hover { color: #171717; }
    .drawer-nav { display: flex; flex-direction: column; gap: 32px; padding: 96px 32px 0; }
    .drawer-nav a {
      font-size: 18px; font-weight: 600; letter-spacing: 0.1em;
      color: #404040; text-decoration: none; text-transform: uppercase;
      opacity: 0; transform: translateX(32px);
      transition: opacity 0.5s, transform 0.5s, color 0.3s;
    }
    .mobile-overlay.open .drawer-nav a { opacity: 1; transform: translateX(0); }
    .drawer-nav a:hover { color: #171717; }
    .drawer-bottom {
      position: absolute; bottom: 40px; left: 32px;
      display: flex; align-items: center; gap: 20px;
      opacity: 0; transform: translateY(16px);
      transition: opacity 0.5s 400ms, transform 0.5s 400ms;
    }
    .mobile-overlay.open .drawer-bottom { opacity: 1; transform: translateY(0); }
    .drawer-bottom a { color: #404040; transition: color 0.3s; }
    .drawer-bottom a:hover { color: #171717; }

    /* ===== SVG ICONS ===== */
    .icon { display: inline-block; vertical-align: middle; }

    /* ===== DESKTOP ===== */
    @media (min-width: 768px) {
      .main-nav { padding: 20px 32px; }
      .nav-links { display: flex; }
      .hamburger { display: none; }
      .nav-right { gap: 20px; }
      .nav-right .desktop-only { display: block; }
      .side-thumbnails { display: flex; }
      .right-line { display: flex; }
      .bottom-text { bottom: 48px; }
      .bottom-text p { font-size: 12px; max-width: 384px; }
      .hero-heading .letter { font-size: 35vw; }
      .view-inner { padding: 40px; }
      .view-top { padding-top: 64px; }
      .view-heading .letter { font-size: 16vw; }
      .view-line { display: block; }
      .view-subtext-row { justify-content: flex-end; }
      .view-subtext { font-size: 16px; text-align: right; }
      .view-cards { grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 0; }
      .view-card:nth-child(3) { grid-column: span 1; max-width: 100%; margin: 0; }
      .view-card .card-title { font-size: 14px; }
    }
    @media (min-width: 1024px) {
      .view-inner { padding: 64px; }
    }
  </style>
</head>
<body>
  <div class="page-wrapper">

    <!-- MOBILE MENU -->
    <div class="mobile-overlay" id="mobileMenu">
      <div class="mobile-overlay-bg" onclick="closeMenu()"></div>
      <div class="mobile-drawer">
        <button class="drawer-close" onclick="closeMenu()" aria-label="Close menu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
        <nav class="drawer-nav">
          <a href="#" style="transition-delay: 150ms" onclick="closeMenu()">Portfolio</a>
          <a href="#" style="transition-delay: 230ms" onclick="closeMenu()">About</a>
          <a href="#" style="transition-delay: 310ms" onclick="closeMenu()">Lab</a>
        </nav>
        <div class="drawer-bottom">
          <a href="#"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg></a>
          <a href="#"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></a>
        </div>
      </div>
    </div>

    <!-- SHARED CONTAINER -->
    <div class="shared-container">
      <!-- Background -->
      <img class="shared-bg" id="sharedBg"
        src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260723_224514_a4f5778c-5a68-4e60-b9f8-74aeec2ef48b.png&w=1920&q=85"
        alt="" />
      <!-- Overlay -->
      <img class="overlay-img" id="overlayImg"
        src="https://soft-zoom-63098134.figma.site/_assets/v11/7e3b4feb333e9a78d12d5afc7d48730615390ec2.png"
        alt="" />

      <!-- HERO SECTION -->
      <section class="hero-section" id="heroSection">
        <!-- Heading -->
        <div class="hero-heading-wrapper">
          <div class="hero-heading" id="heroHeading"></div>
        </div>

        <!-- Nav -->
        <nav class="main-nav" id="mainNav">
          <div class="nav-links">
            <a href="#">Portfolio</a>
            <a href="#">About</a>
            <a href="#">Lab</a>
          </div>
          <button class="hamburger" onclick="openMenu()" aria-label="Open menu">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
          <span class="nav-brand">IGLOO</span>
          <div class="nav-right">
            <a href="#" class="desktop-only"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg></a>
            <a href="#"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></a>
          </div>
        </nav>

        <!-- Side Thumbnails -->
        <div class="side-thumbnails" id="sideThumbs">
          <div class="thumb" style="transition-delay: 450ms"><img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094505_c14a7566-ec38-46cf-b298-b641815acbdc.png&w=1280&q=85" alt="Thumbnail 1" /></div>
          <div class="thumb" style="transition-delay: 600ms"><img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094527_33af18d8-e52c-49a6-8b9b-4706b0c0a85a.png&w=1280&q=85" alt="Thumbnail 2" /></div>
          <div class="thumb" style="transition-delay: 750ms"><img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094546_3f85bc04-8e66-4d82-aa27-fcf40742a384.png&w=1280&q=85" alt="Thumbnail 3" /></div>
          <div class="thumb" style="transition-delay: 900ms"><img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_094606_79a7fc4d-cf64-48bc-a2d3-52dd5ad6ffe3.png&w=1280&q=85" alt="Thumbnail 4" /></div>
        </div>

        <!-- Right Scroll Line -->
        <div class="right-line" id="rightLine"><div></div></div>

        <!-- Bottom Text -->
        <div class="bottom-text" id="bottomText">
          <p>A conceptual vision of an igloo, afloat in the Arctic. Where minimalism, nature, and imagination converge.</p>
          <svg class="bounce-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </section>

      <!-- VIEW SECTION -->
      <section class="view-section" id="viewSection">
        <div class="view-inner">
          <div class="view-top">
            <div class="view-heading-row">
              <div class="view-heading" id="viewHeading"></div>
              <div class="view-line"><div></div></div>
            </div>
            <div class="view-subtext-row" id="viewSubtext">
              <p class="view-subtext">Elevated sanctuaries perched above the clouds, where architecture meets the infinite horizon.</p>
            </div>
          </div>

          <div class="view-cards" id="viewCards">
            <div class="view-card" style="transition-delay: 400ms">
              <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101354_a5a857b7-b9ce-4e3f-9cc1-27424c9e4c8d.png&w=1280&q=85" alt="Cliffside Retreat" />
              <span class="card-title">Cliffside Retreat</span>
            </div>
            <div class="view-card" style="transition-delay: 600ms">
              <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101420_1c0cbb04-a7b5-41f1-9d21-fcf3976f6be6.png&w=1280&q=85" alt="Island Escape" />
              <span class="card-title">Island Escape</span>
            </div>
            <div class="view-card" style="transition-delay: 800ms">
              <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260718_101434_83163d4d-1639-4812-8753-e679652939ff.png&w=1280&q=85" alt="Coastal Haven" />
              <span class="card-title">Coastal Haven</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <script>
    // ===== LETTER PULL-UP =====
    function createLetters(container, text, staggerMs) {
      text.split('').forEach((char, i) => {
        const span = document.createElement('span');
        span.className = 'letter';
        span.style.transitionDelay = (i * staggerMs) + 'ms';
        span.innerHTML = char === ' ' ? '&nbsp;' : char;
        container.appendChild(span);
      });
    }
    createLetters(document.getElementById('heroHeading'), 'IGLOO', 50);
    createLetters(document.getElementById('viewHeading'), 'With A View', 50);

    // ===== SCROLL PARALLAX =====
    const sharedBg = document.getElementById('sharedBg');
    const overlayImg = document.getElementById('overlayImg');
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(() => {
          const progress = Math.min(window.scrollY / window.innerHeight, 1);
          const scale = 1 + progress * 0.12;
          const focalY = progress * 100;
          const transform = 'scale(' + scale + ')';
          const objPos = 'center ' + focalY + '%';
          sharedBg.style.transform = transform;
          sharedBg.style.objectPosition = objPos;
          overlayImg.style.transform = transform;
          overlayImg.style.objectPosition = objPos;
          ticking = false;
        });
      }
    }, { passive: true });

    // ===== INTERSECTION OBSERVERS =====
    function observeReveal(el, cls, threshold) {
      const obs = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) { el.classList.add(cls); obs.disconnect(); }
      }, { threshold: threshold || 0.1 });
      obs.observe(el);
    }

    // Hero reveals
    const heroSection = document.getElementById('heroSection');
    const heroObs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        document.getElementById('heroHeading').classList.add('revealed');
        document.getElementById('mainNav').classList.add('revealed');
        document.getElementById('sideThumbs').classList.add('revealed');
        document.getElementById('rightLine').classList.add('revealed');
        document.getElementById('bottomText').classList.add('revealed');
        heroObs.disconnect();
      }
    }, { threshold: 0.1 });
    heroObs.observe(heroSection);

    // View section reveals
    const viewSection = document.getElementById('viewSection');
    const viewObs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        document.getElementById('viewHeading').classList.add('revealed');
        document.getElementById('viewSubtext').classList.add('revealed');
        document.querySelectorAll('.view-card').forEach(c => c.classList.add('revealed'));
        viewObs.disconnect();
      }
    }, { threshold: 0.15 });
    viewObs.observe(viewSection);

    // ===== MOBILE MENU =====
    function openMenu() {
      document.getElementById('mobileMenu').classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeMenu() {
      document.getElementById('mobileMenu').classList.remove('open');
      document.body.style.overflow = '';
    }
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*