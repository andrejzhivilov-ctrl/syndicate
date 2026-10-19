---
title: "ARENA POOL: Шаблоны Сайтов и Компонентов React + Tailwind"
pool_id: "pool_site_templates_react"
tags:
  - arena_pool
  - react_templates
  - tailwind_css
  - web_components
---

# 🌐 ARENA KNOWLEDGE POOL: Шаблоны Сайтов и UI-Компонентов (343 шаблона)

> Промпты для генерации полнофункциональных веб-интерфейсов на React, Tailwind CSS, TypeScript и Canvas 3D анимациях.

---

---
title: "Interactive Portfolio"
template_id: "fe2b9ba5-4327-44c1-a06c-930d9d758b49"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Interactive Portfolio

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `fe2b9ba5-4327-44c1-a06c-930d9d758b49`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Interactive Portfolio](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/1b5f35fc-5838-40f9-942a-357119a30019.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-viewport photography portfolio hero section in React (Vite + TypeScript + Tailwind). Use only inline styles (no Tailwind utility classes in JSX). Import the font `Inter` (weights 400, 500, 600) via Google Fonts in `index.css`:

```
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Display:wght@500;600&display=swap');
```

Set `body { margin:0; padding:0; font-family:'Inter',sans-serif; background:white; overflow:hidden; }` and `* { box-sizing: border-box; }`.

---

**LAYOUT (App component):**

The root container is `width:100%; height:100vh; overflow:hidden; position:relative; background:white`.

Inside it, layer these elements (all `position:absolute`):

1. **Background image** -- `inset:0`, uses `backgroundImage` with this URL:
   `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_151236_784929aa-a992-4292-9938-1dd9b5296a29.png&w=1920&q=85`
   `backgroundSize:'cover'`, `backgroundPosition:'center'`.

2. **Gradient overlay** -- `inset:0`, `background:'linear-gradient(180deg, rgba(84,84,84,0) 0%, rgb(0,0,0) 100%)'`, `opacity:0.4`.

3. **Bottom blur layer** -- `bottom:0; left:50%; transform:translateX(-50%); width:100%; height:47.375%`, with `backdropFilter:'blur(10px)'`, `WebkitBackdropFilter:'blur(10px)'`, masked with `maskImage:'linear-gradient(to bottom, transparent 0%, black 40%)'` (also `-webkit-mask-image`). `zIndex:1; pointerEvents:'none'`.

4. **6 draggable ProjectCard components** positioned absolutely at specific anchor percentages.

5. **Dock bar** at `bottom:64px; left:50%; transform:translateX(-50%); zIndex:4`. Flex row, `gap:16px; padding:12px; borderRadius:24px; background:'rgba(255,255,255,0.1)'; border:'1px solid rgba(255,255,255,0.2)'; backdropFilter:'blur(5px)'`.

---

**PROJECT CARDS:**

Each project has `anchorX` and `anchorY` (percentage positions). The card is `position:absolute; left: calc(anchorX% - 52px); top: calc(anchorY% - 64px)`. Uses a custom `useDraggable()` hook to allow drag-repositioning via `transform: translate(pos.x, pos.y)`. `zIndex:2; cursor:pointer; userSelect:none`.

Card structure (flex column, center-aligned, gap 8px):
- **Image wrapper**: `padding:12px; borderRadius:8px`. On hover: `border: 2px solid rgba(255,255,255,0.2)` and `background: rgba(0,0,0,0.16)`. Otherwise transparent border and background. `transition: background 0.18s ease, border-color 0.18s ease`.
  - **Thumbnail image**: `width:80px; height:auto; borderRadius:8px; border: 1px solid rgba(255,255,255,0.2); boxShadow: 0px 1px 6px 0px rgba(0,0,0,0.08)`.
- **Title label**: On hover, `background: rgb(0,102,221); padding: 4px 8px; borderRadius:4px`. Otherwise transparent with `padding: 4px 0`. `transition: background 0.18s ease, padding 0.18s ease`.
  - Text: `fontFamily:"'Inter',sans-serif"; fontWeight:400; fontSize:16px; lineHeight:1.4em; letterSpacing:-0.04em; color:rgb(247,247,247); whiteSpace:nowrap`.

Clicking a card (only if drag distance < 5px) opens that project in a modal window.

**6 Projects data:**

| # | title | anchorX | anchorY | thumbnail |
|---|-------|---------|---------|-----------|
| 1 | "La ou dort l'eau" | 42.75 | 48.5 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260606_153138_ef8b2e9b-3d18-4b75-8df7-5bc6f0f84fca.png&w=1920&q=85` |
| 2 | "Champ Silencieux" | 26 | 29.5 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_092743_5be19a2a-e188-4bca-9ed6-74049aa3d83b.png&w=1920&q=85` |
| 3 | "Lisiere" | 23.33 | 60.88 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260530_012333_aca09e65-227f-4185-a25f-85191cfac44d.png&w=1920&q=85` |
| 4 | "Elan Brut" | 68 | 62.13 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260527_084631_63ecf071-0fd9-42e3-989a-144728ce8ddb.png&w=1920&q=85` |
| 5 | "Les Silences Miroirs" | 66.08 | 19.63 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260525_053312_b4d2b145-7bb2-4755-b7a0-79a8e81b1265.png&w=1920&q=85` |
| 6 | "Revolte douce" | 73.92 | 40.75 | `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260512_012043_9764f2d0-5c6e-4faa-94a6-a8253df08c5e.png&w=1920&q=85` |

---

**useDraggable() HOOK:**

Tracks drag state in a `useRef` (`dragging, sx, sy, ox, oy, cx, cy`). On `mousedown`: records start position and current offset. Attaches `mousemove` and `mouseup` listeners to `window`. On move: calculates delta from start, updates position state. On up: removes listeners. Returns `{ pos: {x, y}, onMouseDown, isDraggingRef }`.

---

**DOCK BAR (5 icons + 1 divider):**

Each DockIcon is a flex column (centered). On hover: shows a tooltip above and scales the icon to 1.12x.

- **Tooltip**: `position:absolute; bottom: calc(100% + 12px); left:50%; transform:translateX(-50%)`. Fades in with `opacity` transition (0.15s). White pill background (`padding:6px 12px; borderRadius:64px; boxShadow:0 4px 16px rgba(0,0,0,0.12)`). Text: Inter 500, 12px, letterSpacing -0.04em, black. Below pill: a white CSS triangle (border trick, 8px).

- **Icon button**: `width:48px; height:48px; borderRadius:28%; overflow:hidden`. On hover: `transform:scale(1.12)` with `transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1)`. Image fills the button with `objectFit:cover`.

Dock contents (left to right):
1. "About Me" icon: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_151824_5f47765e-d133-4a38-b8bc-d968a07881a3.png&w=1920&q=85` -- opens About overlay
2. "Notes" icon: `https://framerusercontent.com/images/4ar8CL6aUtjymV8jTsXrcPzXCM.svg` -- opens Notes overlay
3. **Vertical divider**: `width:1px; height:48px; background:rgba(255,255,255,0.2); borderRadius:64px`
4. "Instagram" icon: `https://framerusercontent.com/images/Q0Z0p8LOZhN2hJ2arLjEtkqQD0.png` -- links to `https://www.instagram.com/`
5. "X" icon: `https://framerusercontent.com/images/vjmmhizcqEgw5ZT5SNFQMpxD00.png` -- links to `https://www.x.com/`
6. "Behance" icon: `https://framerusercontent.com/images/edJkRGfjqjPajyxmEgsUCKVgjE.png` -- links to `https://www.behance.com/`

---

**WINDOW SHELL (shared modal component):**

Centered fixed overlay (`inset:0; display:flex; alignItems:center; justifyContent:center; zIndex:50; pointerEvents:none`). Inner panel: `width:60vw (or 70vw if "wide"); maxWidth:720px (or 840px); maxHeight:70vh; borderRadius:24px; background:white; boxShadow:0 32px 80px rgba(0,0,0,0.28); pointerEvents:all`.

**Spring-in animation**: On mount, transitions from `scale(0.8) opacity:0` to `scale(1) opacity:1` using `transition: transform 0.4s cubic-bezier(0.34,1.28,0.64,1), opacity 0.3s ease`. Uses `requestAnimationFrame` + state toggle.

**Title bar** (draggable): `height:40px; padding:0 16px; borderBottom:1px solid rgb(229,229,234); cursor:grab`. Contains 3 macOS-style traffic light circles (12px diameter, colors: `rgb(253,93,92)`, `rgb(250,201,0)`, `rgb(52,199,90)`) that close the window on click. Title text: Inter 400, 16px, color `rgb(134,134,139)`, letterSpacing -0.04em.

**Scrollable body**: `flex:1; overflowY:auto; padding:16px; gap:16px; flex column`.

---

**CSS in index.css (also include):**

```css
@keyframes springIn {
  0% { opacity:0; transform:scale(0.8); }
  100% { opacity:1; transform:scale(1); }
}
.spring-in { animation: springIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
```
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Neural Interface"
template_id: "07956fe9-0167-42ef-9c82-31e0bab092cf"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Neural Interface

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `07956fe9-0167-42ef-9c82-31e0bab092cf`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Neural Interface](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/cacbc0f7-6c7d-4dee-87e2-7b17a9b073a9.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>SynapseX</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

html, body {
  font-family: "Space Mono", monospace;
  background: #000;
  color: #fff;
  width: 100%;
  height: auto;
  overflow-x: hidden;
  overflow-y: auto;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

html.lenis, html.lenis-under-construction { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
.lenis.lenis-smooth [data-lenis-prevent] { overscroll-behavior: contain; }
.lenis.lenis-stopped { overflow: hidden; }
.lenis.lenis-scrolling iframe { pointer-events: none; }

a { text-decoration: none; color: inherit; }
button { border: none; outline: none; background: none; font-family: inherit; cursor: pointer; }
button:focus { outline: none; }

/* ── Video Layer ── */
#video-layer {
  position: fixed; inset: 0;
  width: 100%; height: 100%;
  overflow: hidden; z-index: 1;
  background: #000;
  user-select: none;
}
#video-layer video {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  pointer-events: none;
  opacity: 0;
  will-change: transform, filter, opacity;
}

/* ── Progressive Bottom Blur ── */
#bottom-blur {
  position: fixed; bottom: 0; left: 0;
  width: 100%; height: 150px;
  z-index: 30;
  pointer-events: none; user-select: none;
  background: linear-gradient(to bottom, transparent, #000);
  -webkit-mask-image: linear-gradient(to top, #000 50%, transparent);
  mask-image: linear-gradient(to top, #000 50%, transparent);
  -webkit-backdrop-filter: blur(4px);
  backdrop-filter: blur(4px);
}

/* ── Header ── */
#main-header {
  position: fixed; top: 0; left: 0; right: 0;
  height: 80px; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem;
  opacity: 0;
  transition: opacity 0.8s ease-out;
  pointer-events: auto;
}
#main-header.visible { opacity: 1; }

.header-left { display: flex; align-items: center; gap: 8px; }

/* Logo Pill */
.logo-pill {
  height: 48px; padding: 0 20px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  display: flex; align-items: center; gap: 10px;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
  user-select: none;
}
.logo-pill:hover { background: rgba(255,255,255,0.22); transform: scale(1.02); }
.logo-pill:active { transform: scale(0.98); }
.logo-pill svg { width: 18px; height: 18px; color: #fff; flex-shrink: 0; }
.logo-pill span {
  font-size: 16px; font-weight: 500;
  letter-spacing: -0.02em; color: #fff; line-height: 1;
  white-space: nowrap;
}

/* Hamburger Menu Pill */
.menu-pill {
  height: 48px; width: 48px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  display: flex; align-items: center;
  overflow: hidden;
  transition: width 0.35s cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
}
.menu-pill.open { width: 290px; }

.hamburger-btn {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative; z-index: 2;
  transition: all 0.2s;
}
.menu-pill.open .hamburger-btn {
  width: 36px; height: 36px;
  border-radius: 11px;
  background: rgba(255,255,255,0.1);
  margin-left: 6px;
}
.menu-pill.open .hamburger-btn:hover { background: rgba(255,255,255,0.2); }

.hamburger-icon {
  width: 18px; height: 12px; position: relative;
}
.hamburger-icon span {
  position: absolute; left: 0;
  width: 18px; height: 1.5px;
  background: #fff; border-radius: 1px;
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s;
  transform-origin: center;
}
.hamburger-icon span:nth-child(1) { top: 0; }
.hamburger-icon span:nth-child(2) { top: 5px; }
.hamburger-icon span:nth-child(3) { top: 10px; }
.menu-pill.open .hamburger-icon span:nth-child(1) { transform: translateY(5px) rotate(45deg); }
.menu-pill.open .hamburger-icon span:nth-child(2) { opacity: 0; transform: scale(0); }
.menu-pill.open .hamburger-icon span:nth-child(3) { transform: translateY(-5px) rotate(-45deg); }

.menu-links {
  display: flex; align-items: center; gap: 24px;
  margin-left: auto; padding-right: 24px;
  opacity: 0; transform: translateX(15px);
  transition: opacity 0.15s, transform 0.15s;
  pointer-events: none; flex-shrink: 0;
  white-space: nowrap;
}
.menu-pill.open .menu-links {
  opacity: 1; transform: translateX(0);
  pointer-events: auto;
}
.menu-links span {
  font-size: 16px; font-weight: 400;
  color: rgba(255,255,255,0.85);
  cursor: pointer; transition: color 0.15s; line-height: 1;
}
.menu-links span:hover { color: #fff; }

/* Download Button */
.download-btn {
  height: 48px; padding: 0 24px;
  background: #fff; border-radius: 9999px;
  display: flex; align-items: center; gap: 10px;
  color: #000; transition: background 0.15s, transform 0.15s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.download-btn:hover { background: #e2e2e6; transform: scale(1.03); }
.download-btn:active { transform: scale(0.97); }
.download-btn i { font-size: 16px; color: #000; transform: translateY(-1px); }
.download-btn span { font-size: 16px; font-weight: 500; color: #000; line-height: 1; }

/* ── Main Content ── */
#main-content {
  position: relative; width: 100%;
  display: flex; flex-direction: column;
  padding: 80px 2rem 144px;
  z-index: 10; pointer-events: auto;
  opacity: 0;
  transition: opacity 1s ease-out;
}
#main-content.visible { opacity: 1; }

.dot-grid {
  position: absolute; inset: 0;
  background-image: radial-gradient(#fff 1px, transparent 1px);
  background-size: 24px 24px;
  opacity: 0.05; pointer-events: none;
}

/* ── Hero Section ── */
#hero-section {
  position: relative; width: 100%; max-width: 1280px; margin: 0 auto;
  display: flex; flex-direction: column;
  min-height: 80vh;
  justify-content: space-between;
  padding-top: 32px; padding-bottom: 64px;
  transition: opacity 0.1s linear, transform 0.1s linear;
}

.hero-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 48px; width: 100%;
}
.hero-grid-bottom {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 48px; width: 100%; margin-top: auto; padding-top: 48px;
  align-items: end;
}

.hero-title {
  font-weight: 300;
  font-size: clamp(50px, 8vw, 100px);
  color: #fff; line-height: 0.95;
  letter-spacing: -0.03em;
  display: flex; flex-direction: column;
  user-select: none;
}
.hero-title.right { align-items: flex-end; text-align: right; }

.hero-desc {
  max-width: 380px;
  font-size: 15px; color: rgba(255,255,255,0.6);
  line-height: 1.625;
  transition: opacity 0.1s linear, transform 0.1s linear;
}

/* ── Cinematic Paragraph ── */
#cinematic-section {
  position: relative; width: 100%; max-width: 1024px; margin: 0 auto;
  padding: 96px 24px 128px;
  perspective: 400px;
  pointer-events: none;
}
#cinematic-inner {
  transform-style: preserve-3d;
  text-align: center;
  transition: opacity 0.05s linear;
}
#cinematic-inner h2 {
  font-weight: 400;
  font-size: clamp(22px, 3.5vw, 42px);
  color: #fff; line-height: 1.35;
  letter-spacing: -0.02em;
  user-select: none;
  padding: 0 24px;
}

/* ── Stats Section ── */
#stats-section {
  width: 100vw; position: relative;
  margin-left: calc(-50vw + 50%);
  margin-top: 64px;
  overflow: hidden;
  opacity: 0; transform: translateY(40px) scale(0.98);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
#stats-section.revealed { opacity: 1; transform: translateY(0) scale(1); }

.swiper { width: 100%; height: 520px; padding-bottom: 20px !important; overflow: visible !important; }
.swiper-slide { width: 380px; max-width: 85%; height: 480px; background-position: center; background-size: cover; }

.stat-card-outer {
  padding: 6px; border-radius: 28px;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  display: flex; flex-direction: column;
  justify-content: space-between; height: 480px;
}
.stat-card-inner {
  background: rgba(0,0,0,0.45);
  border: 1px solid rgba(255,255,255,0.05);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 23px; padding: 32px;
  display: flex; flex-direction: column;
  justify-content: space-between; flex: 1;
}
.stat-title {
  font-family: "Space Mono", monospace;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  color: #fff; opacity: 0.8;
}
.stat-value {
  font-size: clamp(60px, 6vw, 76px);
  font-weight: 400; letter-spacing: -0.04em;
  color: #fff; line-height: 1;
  margin-top: 24px;
}
.stat-details { display: flex; flex-direction: column; gap: 8px; padding-top: 16px; }
.stat-detail {
  display: flex; align-items: flex-start; gap: 8px;
  font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 500;
}
.stat-detail .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255,255,255,0.3);
  margin-top: 4px; flex-shrink: 0;
}
.stat-footer {
  padding: 12px 24px 10px;
  font-family: "Space Mono", monospace;
  font-size: 10px; font-weight: 500;
  color: rgba(255,255,255,0.55);
  text-transform: uppercase; letter-spacing: 0.1em;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* ── Mobile ── */
@media (max-width: 639px) {
  #main-header { padding: 0 16px; }
  .desktop-header { display: none !important; }
  .mobile-header { display: flex !important; }
  #main-content { padding: 80px 16px 144px; }
  .hero-grid, .hero-grid-bottom { grid-template-columns: 1fr; }
  .hero-title.right { align-items: flex-start; text-align: left; }
  .hero-desc { font-size: 14px; }
  #cinematic-section { padding: 64px 16px 96px; }
}
@media (min-width: 640px) {
  .mobile-header { display: none !important; }
  .desktop-header { display: flex !important; }
}

/* Mobile header */
.mobile-header {
  align-items: center; justify-content: space-between;
  width: 100%; height: 100%; gap: 8px;
}
.mobile-left {
  display: flex; align-items: center; height: 36px;
  flex-grow: 1; min-width: 0; margin-right: 16px; position: relative;
}

.logo-pill-m {
  height: 36px; padding: 0 12px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 10px;
  display: flex; align-items: center; gap: 6px;
  cursor: pointer; flex-shrink: 0;
  overflow: hidden; white-space: nowrap;
  transition: width 0.35s cubic-bezier(0.22,1,0.36,1), opacity 0.35s, margin-right 0.35s, padding 0.35s;
  width: 108px; margin-right: 6px;
}
.logo-pill-m.collapsed {
  width: 0; opacity: 0; margin-right: 0;
  padding: 0; pointer-events: none;
}
.logo-pill-m svg { width: 14px; height: 14px; color: #fff; flex-shrink: 0; }
.logo-pill-m span { font-size: 13px; font-weight: 500; letter-spacing: -0.02em; color: #fff; line-height: 1; flex-shrink: 0; }

.menu-pill-m {
  height: 36px; width: 36px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 10px;
  display: flex; align-items: center;
  overflow: hidden; flex-shrink: 0;
  transition: width 0.35s cubic-bezier(0.22,1,0.36,1);
}
.menu-pill-m.open { width: 100%; }

.hamburger-btn-m {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; z-index: 2; transition: all 0.2s;
}
.menu-pill-m.open .hamburger-btn-m {
  width: 28px; height: 28px;
  border-radius: 8px; background: rgba(255,255,255,0.1);
  margin-left: 4px;
}

.hamburger-icon-m { width: 15px; height: 10px; position: relative; }
.hamburger-icon-m span {
  position: absolute; left: 0; width: 15px; height: 1.2px;
  background: #fff; border-radius: 1px;
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), opacity 0.3s;
  transform-origin: center;
}
.hamburger-icon-m span:nth-child(1) { top: 0; }
.hamburger-icon-m span:nth-child(2) { top: 4px; }
.hamburger-icon-m span:nth-child(3) { top: 8px; }
.menu-pill-m.open .hamburger-icon-m span:nth-child(1) { transform: translateY(4px) rotate(45deg); }
.menu-pill-m.open .hamburger-icon-m span:nth-child(2) { opacity: 0; transform: scale(0); }
.menu-pill-m.open .hamburger-icon-m span:nth-child(3) { transform: translateY(-4px) rotate(-45deg); }

.menu-links-m {
  display: flex; align-items: center; gap: 14px;
  margin-left: auto; padding-right: 14px;
  opacity: 0; transform: translateX(10px);
  transition: opacity 0.15s, transform 0.15s;
  pointer-events: none; flex-shrink: 0; white-space: nowrap;
}
.menu-pill-m.open .menu-links-m { opacity: 1; transform: translateX(0); pointer-events: auto; }
.menu-links-m span { font-size: 13px; font-weight: 400; color: rgba(255,255,255,0.85); cursor: pointer; transition: color 0.15s; line-height: 1; }
.menu-links-m span:hover { color: #fff; }

.download-btn-m {
  height: 36px; padding: 0 14px;
  background: #fff; border-radius: 9999px;
  display: flex; align-items: center; gap: 6px;
  color: #000; flex-shrink: 0;
  transition: background 0.15s, transform 0.15s;
}
.download-btn-m:hover { background: #e2e2e6; transform: scale(1.03); }
.download-btn-m:active { transform: scale(0.97); }
.download-btn-m i { font-size: 13px; color: #000; transform: translateY(-0.5px); }
.download-btn-m span { font-size: 13px; font-weight: 500; color: #000; line-height: 1; }

/* Scramble text helper */
.scramble-line { display: inline-block; }
</style>
</head>
<body>

<!-- LAYER 0: Background Video -->
<div id="video-layer">
  <video id="bg-video" loop muted playsinline preload="auto"
    src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260613_120544_a609e0c2-e52d-4bd5-b10f-b66ac51f1965.mp4">
  </video>
</div>

<!-- LAYER 1: Bottom Blur -->
<div id="bottom-blur"></div>

<!-- HEADER -->
<header id="main-header">
  <!-- Desktop -->
  <div class="desktop-header" style="display:flex;align-items:center;justify-content:space-between;width:100%;height:100%;">
    <div class="header-left">
      <div class="logo-pill" id="logo-pill" onclick="window.scrollTo({top:0,behavior:'smooth'})">
        <svg viewBox="-50 -50 100 100"><g fill="currentColor"><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(90)"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(180)"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(270)"/></g></svg>
        <span>SynapseX</span>
      </div>
      <div class="menu-pill" id="menu-pill">
        <button class="hamburger-btn" id="hamburger-btn" aria-label="Toggle Menu">
          <div class="hamburger-icon"><span></span><span></span><span></span></div>
        </button>
        <div class="menu-links">
          <span onclick="window.scrollTo({top:window.innerHeight,behavior:'smooth'});document.getElementById('menu-pill').classList.remove('open')">About</span>
          <span onclick="window.scrollTo({top:window.innerHeight*2,behavior:'smooth'});document.getElementById('menu-pill').classList.remove('open')">Metrics</span>
        </div>
      </div>
    </div>
    <a class="download-btn" href="https://www.instagram.com/dmitriyinin" target="_blank" rel="noopener noreferrer">
      <i class="bi bi-apple"></i>
      <span>Download</span>
    </a>
  </div>

  <!-- Mobile -->
  <div class="mobile-header">
    <div class="mobile-left">
      <div class="logo-pill-m" id="logo-pill-m" onclick="window.scrollTo({top:0,behavior:'smooth'})">
        <svg viewBox="-50 -50 100 100"><g fill="currentColor"><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(90)"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(180)"/><path d="M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z" transform="rotate(270)"/></g></svg>
        <span>SynapseX</span>
      </div>
      <div class="menu-pill-m" id="menu-pill-m">
        <button class="hamburger-btn-m" id="hamburger-btn-m" aria-label="Toggle Menu Mobile">
          <div class="hamburger-icon-m"><span></span><span></span><span></span></div>
        </button>
        <div class="menu-links-m">
          <span onclick="window.scrollTo({top:window.innerHeight,behavior:'smooth'});closeMobileMenu()">About</span>
          <span onclick="window.scrollTo({top:window.innerHeight*2,behavior:'smooth'});closeMobileMenu()">Metrics</span>
        </div>
      </div>
    </div>
    <a class="download-btn-m" href="https://www.instagram.com/dmitriyinin" target="_blank" rel="noopener noreferrer">
      <i class="bi bi-apple"></i>
      <span>Download</span>
    </a>
  </div>
</header>

<!-- MAIN CONTENT -->
<main id="main-content">
  <div class="dot-grid"></div>

  <!-- SECTION 1: Hero -->
  <div id="hero-section">
    <div style="width:100%;flex:1;display:flex;flex-direction:column;justify-content:space-between;gap:48px;">
      <div class="hero-grid">
        <div style="text-align:left;">
          <div class="hero-title">
            <span class="scramble-line" data-scramble-in data-text="Brain" data-delay="100">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
            <span class="scramble-line" data-scramble-in data-text="And Body" data-delay="300">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
          </div>
        </div>
        <div></div>
      </div>

      <div class="hero-grid-bottom">
        <div class="hero-desc" id="hero-desc">
          <p>Built at the intersection of neuroscience and artificial intelligence. SynapseX continuously maps neural pathways, cognitive load, and physiological states into a single adaptive intelligence layer.</p>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;text-align:right;">
          <div class="hero-title right">
            <span class="scramble-line" data-scramble-in data-text="One" data-delay="200">&nbsp;&nbsp;&nbsp;</span>
            <span class="scramble-line" data-scramble-in data-text="Network" data-delay="400">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 1.5: Cinematic Parallax Paragraph -->
  <div id="cinematic-section">
    <div id="cinematic-inner">
      <h2>A neural-AI interface built on the architecture of the human nervous system. SynapseX translates synaptic activity into computational intelligence. Every signal becomes measurable, structured, and visible. It continuously reconstructs internal state as a dynamic neural map. Biological noise is filtered into actionable cognitive patterns.</h2>
    </div>
  </div>

  <!-- SECTION 2: Stats Carousel -->
  <div id="stats-section">
    <div class="swiper" id="stats-swiper">
      <div class="swiper-wrapper" id="swiper-wrapper"></div>
    </div>
  </div>
</main>

<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
<script>
(function() {
  "use strict";

  // ── Constants ──
  const GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+~|}{[]:;?><";
  const VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260613_120544_a609e0c2-e52d-4bd5-b10f-b66ac51f1965.mp4";

  const statsData = [
    { title: "NEURAL ACTIVITY", value: "7.2M", footer: "LIVE SIGNALS INTERPRETED", details: ["Continuous temporal synapsing","1024 parallel telemetry streams","Dynamic feed classification active"] },
    { title: "PREDICTIVE MODEL", value: "93%", footer: "FORECAST ACCURACY RATE", details: ["Reinforced gradient mapping","Low latency neural resolution","Adaptive signal feedback system"] },
    { title: "EPOCH LATENCY", value: "0.4ms", footer: "CYCLE RESPONSE SPEED", details: ["Hardware accelerated pipeline","Direct metal shader execution","Temporal synchronization loop"] },
    { title: "COGNITIVE STREAMS", value: "14.8M", footer: "REAL-TIME MODEL COHERENCE", details: ["Distributed synapse projection","High-fidelity entropy filtering","Sub-millisecond state coherence"] },
    { title: "SYNAPSE DEPTH", value: "128L", footer: "MODEL RESOLUTION DEPTH", details: ["Deep feed-forward mapping","Transformer-based neural routing","Multi-dimensional pattern projection"] },
    { title: "SIGNAL INTEGRITY", value: "99.9%", footer: "NOISE REDUCTION RATIO", details: ["Advanced wave-let filtering","Dynamic heuristic balancing","Contextual signal amplification"] }
  ];

  // ── State ──
  let scrollProgress = 0;
  let smoothScrollProgress = 0;
  let entrancePhase = "loading"; // loading | animating | complete
  let entranceStart = 0;
  let videoReady = false;

  // ── Elements ──
  const video = document.getElementById("bg-video");
  const header = document.getElementById("main-header");
  const mainContent = document.getElementById("main-content");
  const heroSection = document.getElementById("hero-section");
  const heroDesc = document.getElementById("hero-desc");
  const cinematicInner = document.getElementById("cinematic-inner");
  const statsSection = document.getElementById("stats-section");

  // ── Build Stats Cards ──
  const wrapper = document.getElementById("swiper-wrapper");
  statsData.forEach(card => {
    const slide = document.createElement("div");
    slide.className = "swiper-slide";
    slide.innerHTML = `
      <div class="stat-card-outer">
        <div class="stat-card-inner">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span class="stat-title">${card.title}</span>
            </div>
            <div class="stat-value">${card.value}</div>
          </div>
          <div class="stat-details">
            ${card.details.map(d => `<div class="stat-detail"><span class="dot"></span><span>${d}</span></div>`).join("")}
          </div>
        </div>
        <div class="stat-footer">${card.footer}</div>
      </div>`;
    wrapper.appendChild(slide);
  });

  // ── Swiper Init ──
  new Swiper("#stats-swiper", {
    effect: "coverflow",
    grabCursor: true,
    slidesPerView: "auto",
    centeredSlides: true,
    loop: true,
    spaceBetween: 32,
    coverflowEffect: { rotate: 30, stretch: 0, depth: 100, modifier: 1, slideShadows: false },
    observer: true,
    observeParents: true
  });

  // ── Hamburger Menus ──
  document.getElementById("hamburger-btn").addEventListener("click", () => {
    document.getElementById("menu-pill").classList.toggle("open");
  });
  document.getElementById("hamburger-btn-m").addEventListener("click", () => {
    const pill = document.getElementById("menu-pill-m");
    const logo = document.getElementById("logo-pill-m");
    pill.classList.toggle("open");
    logo.classList.toggle("collapsed", pill.classList.contains("open"));
  });
  window.closeMobileMenu = function() {
    document.getElementById("menu-pill-m").classList.remove("open");
    document.getElementById("logo-pill-m").classList.remove("collapsed");
  };

  // ── Scroll Tracking ──
  function updateScrollProgress() {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    if (scrollHeight <= 0) return;
    scrollProgress = scrollTop / scrollHeight;
  }
  window.addEventListener("scroll", updateScrollProgress, { passive: true });
  updateScrollProgress();

  // ── Lenis (Desktop only) ──
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;

  if (!isMobile) {
    const lenisScript = document.createElement("script");
    lenisScript.src = "https://unpkg.com/lenis@1.1.18/dist/lenis.min.js";
    lenisScript.onload = function() {
      const lenis = new Lenis({
        duration: 1.2,
        easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
        smoothWheel: true,
        wheelMultiplier: 1.0,
        touchMultiplier: 1.5
      });
      lenis.on("scroll", updateScrollProgress);
      function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
      requestAnimationFrame(raf);
    };
    document.head.appendChild(lenisScript);
  }

  // ── ScrambleIn System ──
  const scrambleEls = document.querySelectorAll("[data-scramble-in]");
  const scrambleStates = [];

  scrambleEls.forEach(el => {
    const text = el.getAttribute("data-text");
    const delay = parseInt(el.getAttribute("data-delay") || "0", 10);
    scrambleStates.push({
      el, text, delay,
      phase: "idle", // idle | scrambling-in | revealed | scrambling-out | hidden
      progress: 0, lastTime: 0, started: false
    });
  });

  function updateScrambles(now) {
    const scrollActive = scrollProgress > 0.015;

    scrambleStates.forEach(s => {
      if (!videoReady && s.phase === "idle") return;

      if (videoReady && s.phase === "idle" && !scrollActive && !s.started) {
        s.started = true;
        setTimeout(() => {
          s.phase = "scrambling-in";
          s.progress = 0;
          s.lastTime = now;
        }, s.delay);
        return;
      }

      if (scrollActive && (s.phase === "revealed" || s.phase === "scrambling-in")) {
        s.phase = "scrambling-out";
        s.progress = 0;
        s.lastTime = now;
      } else if (!scrollActive && (s.phase === "hidden" || s.phase === "scrambling-out")) {
        s.phase = "scrambling-in";
        s.progress = 0;
        s.lastTime = now;
      }

      if (s.phase === "scrambling-in") {
        const duration = 900;
        s.progress = Math.min(1, s.progress + (now - s.lastTime) / duration);
        s.lastTime = now;
        const t = s.progress;

        let result = "";
        for (let i = 0; i < s.text.length; i++) {
          if (s.text[i] === " ") { result += " "; continue; }
          const threshold = i / s.text.length;
          if (t >= threshold + 0.15) result += s.text[i];
          else if (t >= threshold - 0.1) result += GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          else result += "\u00A0";
        }
        s.el.textContent = result;
        s.el.style.opacity = "1";

        if (t >= 1) { s.phase = "revealed"; s.el.textContent = s.text; }
      } else if (s.phase === "scrambling-out") {
        const duration = 700;
        s.progress = Math.min(1, s.progress + (now - s.lastTime) / duration);
        s.lastTime = now;
        const t = s.progress;

        let result = "";
        for (let i = 0; i < s.text.length; i++) {
          if (s.text[i] === " ") { result += " "; continue; }
          const threshold = i / s.text.length;
          if (t >= threshold + 0.2) result += "\u00A0";
          else if (t >= threshold - 0.05) result += GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          else result += s.text[i];
        }
        s.el.textContent = result;
        s.el.style.opacity = String(Math.max(0, 1 - t * 1.5));

        if (t >= 1) {
          s.phase = "hidden";
          s.el.textContent = s.text.replace(/\S/g, "\u00A0");
          s.el.style.opacity = "0";
        }
      }
    });
  }

  // ── Stats Reveal on Scroll ──
  let statsRevealed = false;
  function checkStatsReveal() {
    if (statsRevealed) return;
    const rect = statsSection.getBoundingClientRect();
    if (rect.top < window.innerHeight * 0.9) {
      statsRevealed = true;
      statsSection.classList.add("revealed");
    }
  }
  window.addEventListener("scroll", checkStatsReveal, { passive: true });

  // ── Main Animation Loop ──
  let isSeeking = false;
  let nextSeekTime = null;

  video.addEventListener("seeking", () => { isSeeking = true; });
  video.addEventListener("seeked", () => {
    isSeeking = false;
    if (nextSeekTime !== null) {
      const t = nextSeekTime; nextSeekTime = null;
      if (video.readyState >= 1 && video.duration > 0) { isSeeking = true; video.currentTime = t; }
    }
  });
  video.addEventListener("loadedmetadata", () => { video.autoplay = false; video.pause(); });
  video.autoplay = false;
  video.pause();

  // Safety timeout
  setTimeout(() => {
    if (entrancePhase === "loading") {
      entrancePhase = "animating";
      entranceStart = performance.now();
    }
  }, 3500);

  function tick(now) {
    // ── Smooth scroll interpolation ──
    smoothScrollProgress += (scrollProgress - smoothScrollProgress) * 0.12;
    if (Math.abs(scrollProgress - smoothScrollProgress) < 0.0001) smoothScrollProgress = scrollProgress;

    // ── Video blur + scale ──
    const subtleBase = Math.max(0, Math.min(1, (smoothScrollProgress - 0.1) / 0.45));
    const progressive = Math.max(0, Math.min(1, (smoothScrollProgress - 0.55) / 0.4));
    const blurVal = subtleBase * 5 + progressive * 50;
    const scaleVal = 1.03 + Math.max(0, Math.min(1, (smoothScrollProgress - 0.1) / 0.9)) * 0.08;

    // ── Video entrance ──
    let entranceZoom = 1.0;
    let entranceOpacity = 1.0;

    if (entrancePhase === "loading") {
      entranceZoom = 1.12;
      entranceOpacity = 0;
      if (video.readyState >= 3) {
        entrancePhase = "animating";
        entranceStart = performance.now();
      }
    }

    if (entrancePhase === "animating") {
      const elapsed = now - entranceStart;
      const progress = Math.min(1, elapsed / 1400);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      entranceZoom = 1.12 - 0.12 * easeOut;
      entranceOpacity = Math.min(1.0, elapsed / 500);

      if (progress >= 1) {
        entrancePhase = "complete";
        videoReady = true;
        header.classList.add("visible");
        mainContent.classList.add("visible");
      }
    }

    if (entrancePhase === "complete" && !videoReady) {
      videoReady = true;
      header.classList.add("visible");
      mainContent.classList.add("visible");
    }

    // Apply video styles
    video.style.filter = `blur(${blurVal}px)`;
    video.style.transform = `scale(${scaleVal * entranceZoom})`;
    video.style.opacity = String(entranceOpacity);

    // ── Video seek ──
    if (video.readyState >= 1 && video.duration > 0) {
      const targetTime = Math.max(0, Math.min(video.duration, smoothScrollProgress * video.duration));
      if (Math.abs(video.currentTime - targetTime) > 0.008) {
        if (!isSeeking && !video.seeking) { isSeeking = true; video.currentTime = targetTime; }
        else { nextSeekTime = targetTime; }
      }
    }

    // ── Hero section parallax ──
    const scrollH = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollYNorm = scrollH > 0 ? (window.scrollY / scrollH) : 0;

    // Hero fade
    const heroOp = Math.max(0, Math.min(1, 1 - scrollYNorm / 0.26));
    const heroSc = 1 - (1 - 0.96) * Math.min(1, scrollYNorm / 0.26);
    heroSection.style.opacity = String(heroOp);
    heroSection.style.transform = `scale(${heroSc})`;

    // Desc fade
    const descOp = Math.max(0, Math.min(1, 1 - scrollYNorm / 0.12));
    const descYval = -30 * Math.min(1, scrollYNorm / 0.12);
    heroDesc.style.opacity = String(descOp);
    heroDesc.style.transform = `translateY(${descYval}px)`;

    // ── Cinematic paragraph ──
    const scrollPx = window.scrollY;
    const yVal = -120 * Math.min(1, scrollPx / 1000);

    // Opacity keyframes: [0.08, 0.22, 0.42, 0.65] -> [0, 1, 1, 0]
    let cinOp = 0;
    if (scrollYNorm <= 0.08) cinOp = 0;
    else if (scrollYNorm <= 0.22) cinOp = (scrollYNorm - 0.08) / (0.22 - 0.08);
    else if (scrollYNorm <= 0.42) cinOp = 1;
    else if (scrollYNorm <= 0.65) cinOp = 1 - (scrollYNorm - 0.42) / (0.65 - 0.42);
    else cinOp = 0;

    cinematicInner.style.transform = `rotateX(24deg) translateY(${yVal}px) translateZ(15px)`;
    cinematicInner.style.opacity = String(Math.max(0, Math.min(1, cinOp)));

    // ── ScrambleIn updates ──
    updateScrambles(now);

    // ── Hero desc entrance ──
    if (videoReady && !heroDesc._entered) {
      heroDesc._entered = true;
      heroDesc.style.transition = "opacity 0.9s cubic-bezier(0.215,0.61,0.355,1) 0.2s, transform 0.9s cubic-bezier(0.215,0.61,0.355,1) 0.2s";
      heroDesc.style.opacity = "1";
      heroDesc.style.transform = "translateY(0)";
    }

    requestAnimationFrame(tick);
  }

  // Set initial desc state
  heroDesc.style.opacity = "0";
  heroDesc.style.transform = "translateY(25px)";

  requestAnimationFrame(tick);
  checkStatsReveal();
})();
</script>
</body>
</html>

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Wellness Hero"
template_id: "0a497cc8-4d72-4c49-aff5-45e8de4cfe44"
section: "sites"
category_slug: "general"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/512543ac-d6b6-4dad-be3f-5475ac866f70.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Wellness Hero

> **Секція:** `SITES` | **Категорія:** `general`  
> **ID шаблону:** `0a497cc8-4d72-4c49-aff5-45e8de4cfe44`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/512543ac-d6b6-4dad-be3f-5475ac866f70.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-screen hero section landing page for "Aurai" - an always-on AI wellness companion. The page is a single viewport-height section with a looping background video and overlaid content.

## Video Background

- Full-screen `<video>` element with `autoPlay`, `loop`, `muted`, `playsInline` attributes
- Video URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260618_174853_aac61aa2-0f3f-4cf1-bc78-7f657dd11164.mp4`
- Video covers entire viewport with `object-cover`
- Focal point positioning:
  - Mobile (default): `object-position: 80% center`
  - Tablet (md breakpoint): `object-position: right center`
  - Desktop (lg breakpoint): `object-position: center center`

## Fonts

- **Askan Light** loaded from: `https://db.onlinewebfonts.com/c/304a6edcec9f8858eeaafc2ac18243f4?family=Askan+Light` - used for the brand name and heading
- **Inter** (weights 300, 400, 500, 600) from Google Fonts - used as the body/UI font
- Tailwind config extends fontFamily with `askan: ['"Askan Light"', 'serif']` and `inter: ['Inter', 'sans-serif']`

## Layout Structure

The content is layered on top of the video using `absolute inset-0 z-10` with a flex column layout. Padding: `px-4 sm:px-10 lg:px-12 py-4 sm:py-8`.

## Navigation (Top)

A `<nav>` with `flex items-center justify-between`:

**Left nav pill (glassmorphism):**
- `bg-black/20 backdrop-blur-md rounded-2xl border border-white/10`
- Padding: `px-4 py-2.5 sm:px-6 sm:py-4`
- Contains:
  - A custom SVG logo (4-petal pinwheel shape, `w-5 h-5 sm:w-7 sm:h-7`, white)
  - Brand text "Aurai" in `font-askan text-white text-base sm:text-xl tracking-wide`
  - Hamburger menu icon (lucide-react `Menu`/`X`) with left margin: `ml-4 sm:ml-32 md:ml-64 lg:ml-96`

**Right button (desktop only):**
- `hidden sm:block bg-white text-gray-900 font-medium text-sm px-6 py-3 rounded-full`
- Text: "Join the list"

## Mobile Menu (shown on toggle)

- `sm:hidden`, positioned `absolute top-[4.5rem] left-4 right-4`
- `bg-black/30 backdrop-blur-xl rounded-2xl p-5 border border-white/10`
- Contains links: "Story", "Benefits", "Connect" (white text) and a full-width "Join the list" button

## Main Content (Bottom-aligned)

On mobile: a spacer `flex-1 sm:hidden` pushes content to the bottom.

The content container: `flex flex-col sm:flex-1 sm:flex-row sm:items-end pb-4 sm:pb-12 lg:pb-16 sm:mt-auto`

**Left column:**

1. **Heading:** `font-askan text-white text-[2rem] sm:text-[3.5rem] md:text-[4.5rem] lg:text-[5.5rem] leading-[1.05] tracking-tight max-w-[700px]`
   - Text: "Your calm is always within."

2. **Subtitle:** `text-white/70 text-xs sm:text-base md:text-lg max-w-[520px] leading-relaxed`
   - Text: "Aurai is your always-on wellness companion. Built by leading therapists, it brings you the care and clarity right when you need it."

3. **Email form:** A rounded pill input with inline submit button
   - Container: `bg-black/30 backdrop-blur-md rounded-full border border-white/10`
   - Input: transparent background, white text, placeholder "Your email address", `px-4 sm:px-6 py-3 sm:py-4 text-sm`
   - Submit button (absolute right-1.5): `bg-white text-gray-900 text-xs sm:text-sm font-medium px-3 sm:px-6 py-2 sm:py-3 rounded-full`
   - Text: "Join the list"
   - On submit: shows alert with entered email

4. **Feature pills (mobile only):** `flex sm:hidden flex-wrap gap-2 mt-2`
   - Three pills with `bg-black/30 backdrop-blur-md text-white text-xs px-3 py-1.5 rounded-full border border-white/10`
   - Labels: "Smart Therapy", "Real-time Healing", "Insights into outcomes"

**Right column (desktop only):**
- `hidden sm:flex flex-col items-end gap-2 self-end`
- Same three feature pills as mobile but with `text-xs sm:text-sm px-4 py-2`

## Custom SVG Logo

A pinwheel/4-quadrant shape with this path:
```
M 228 0 C 172.772 0 128 44.772 128 100 L 128 0 L 0 0 L 0 28 C 0 83.228 44.772 128 100 128 L 0 128 L 0 256 L 28 256 C 83.228 256 128 211.228 128 156 L 128 256 L 256 256 L 256 228 C 256 172.772 211.228 128 156 128 L 256 128 L 256 0 Z
```
ViewBox: `0 0 256 256`, fill: `currentColor`

## Global CSS

```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
```

## Key Design Principles

- No dark overlay on the video - content relies on glassmorphism pills and text contrast
- All interactive glass elements use `bg-black/20` or `bg-black/30` with `backdrop-blur-md` or `backdrop-blur-xl`
- Borders are `border-white/10` throughout
- White text with `/70` opacity for secondary text
- Rounded-full for buttons and inputs, rounded-2xl for containers
- Page title: "Aurai - Always-On Wellness Companion"
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Glitch Pulse"
template_id: "8bdde778-2a17-4245-9bea-5ef14477e677"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Glitch Pulse

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `8bdde778-2a17-4245-9bea-5ef14477e677`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Glitch Pulse](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/4f64eddb-e3a3-49a1-93d3-01719ed1e3e4.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
## Overview

Build a single-page React + TypeScript + Vite + Tailwind CSS v4 landing page. The page is extremely tall (1200vh) but all visual content is position-fixed to the viewport. Scrolling drives two scroll-scrubbed HLS videos, a typewriter text deletion effect, a vertically-scrolling manifesto, mouse-trail stickers, and a scroll-triggered feedback form. The aesthetic is brutalist/retro-digital with a pixel font, lime green on near-black with electric blue accents.

---

## TECH STACK (exact versions)

```json
{
  "dependencies": {
    "@tailwindcss/vite": "^4.1.14",
    "@vitejs/plugin-react": "^5.0.4",
    "express": "^4.21.2",
    "hls.js": "^1.6.16",
    "react": "^19.0.1",
    "react-dom": "^19.0.1",
    "vite": "^6.2.3"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^22.14.0",
    "esbuild": "^0.25.0",
    "tailwindcss": "^4.1.14",
    "tsx": "^4.21.0",
    "typescript": "~5.8.2"
  }
}
```

---

## ALL ASSET URLs

### HLS Videos (Mux streams):
```
VIDEO_URL_1 = "https://stream.mux.com/W2NRcV6MrewS7QyWWqAWZvJR9jrnPU5rxymlPg01gRzk.m3u8"
VIDEO_URL_2 = "https://stream.mux.com/aypDi1exkKgYKEbWme9Csi47zxIim0101hw3ghmSzQIyw.m3u8"
```

### Static Stickers (Figma CDN):
```
STICKER1 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/d9a6de619b1e7bf4b31b22e6d29324306ee68ad9.d9a6de61.png"
STICKER2 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/7d1d8f4421fc4780ec85b4153ca6605a4b90dd65.7d1d8f44.png"
STICKER3 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/80809d23ccb460d0db21f77bb3afef67d3ad1d9a.80809d23.png"
STICKER4 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/50d6c27f67bc10d6859cf37d2f017bc406ad3a0d.50d6c27f.png"
```

### Mouse Trail Stickers (Figma CDN):
```
TRAIL_STICKER1 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/b77ef81dabfca9ce4a4d1af5d553e17019a0d229.b77ef81d.png"
TRAIL_STICKER2 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/9ece3a6bf6c5cecf6c0078d022a171bc93baf9c5.9ece3a6b.png"
TRAIL_STICKER3 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/41b9f0bffb2c0b2e1d3fbe26c124ed1378970c35.41b9f0bf.png"
TRAIL_STICKER4 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/0edc0785a3e3bf26be7a494886999c4a6f1dc14c.0edc0785.png"
TRAIL_STICKER5 = "https://crow-peanut-06457083.figma.site/_components/v2/4c2b061456bbff22b92923348791b501874ded3f/d12ddf42fe4c8437df4414c883fe60fb77b20cbe.d12ddf42.png"
```

---

## FONT

Google Font: **"Press Start 2P"** -- imported via CSS `@import url(...)`. Registered as a Tailwind v4 theme token:

```css
@theme {
  --font-press-start: "Press Start 2P", system-ui, sans-serif;
}
```

Applied everywhere via class `font-press-start`.

---

## COLOR SYSTEM

| Token | Value | Usage |
|-------|-------|-------|
| Background | `slate-950` | Page bg, form bg |
| Primary text/accent | `#85D743` | All headings, buttons, cursor, manifesto text |
| Secondary accent | `#0033FF` | Marquee bg, form border, button shadows |
| Button hover | `#9eff5c` / `#9bfb4e` | Submit/reset button hover states |
| Form bg | `slate-950/95` | 95% opacity dark overlay |
| Input bg | `slate-900` | Form input fields |
| Input border | `slate-700` | Default border, `#85D743` on focus |
| Nav text | white | Navigation links |
| Selection | `emerald-500/20` | Text selection highlight |

---

## HTML SHELL (`index.html`)

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Scroll Video</title>
  </head>
  <body class="bg-slate-950 overflow-x-hidden m-0 p-0 selection:bg-emerald-500/20">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## CSS (`src/index.css`) -- EXACT

```css
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
@import "tailwindcss";

@theme {
  --font-press-start: "Press Start 2P", system-ui, sans-serif;
}

@keyframes marquee {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-50%, 0, 0); }
}

@keyframes sticker-fade-out {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(0);
  }
  20% {
    opacity: 1;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(1.05);
  }
  30% {
    opacity: 1;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(1.0);
  }
  85% {
    opacity: 1;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(1.0);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(0.8);
  }
}

.animate-marquee {
  display: flex;
  width: max-content;
  animation: marquee 10s linear infinite;
}
```

---

## PAGE LAYOUT

Root container: `relative w-full bg-slate-950 min-h-[1200vh] select-none`

All visual content is `position: fixed`. The 1200vh height exists solely to create scroll distance that drives the animations.

---

## ELEMENT-BY-ELEMENT BREAKDOWN

### 1. FULL-SCREEN VIDEO BACKGROUND (fixed, z-auto)

Container: `fixed inset-0 w-full h-full overflow-hidden`

Two `<video>` elements stacked:
- Both: `absolute inset-0 w-full h-full object-cover pointer-events-none transition-opacity duration-300`
- Both: `muted playsInline autoPlay={false} preload="auto" crossOrigin="anonymous"`
- Video 1 starts at `opacity: 1`, Video 2 starts at `opacity: 0`

**HLS Setup:**
- Use `hls.js` with `{ maxBufferLength: 60 }`
- On `MANIFEST_PARSED`: call `video.play().then(() => video.pause())` to warm decoder
- Fallback: native HLS for Safari via `canPlayType("application/vnd.apple.mpegurl")`

**Scroll-Scrub Logic (requestAnimationFrame lerp loop):**
- Calculate `progress = scrollY / (documentHeight - windowHeight)` [0 to 1]
- Video 1 maps progress [0, 0.5] to its full duration
- Video 2 maps progress [0.5, 1.0] to its full duration
- Lerp factor: 0.3 (smooth interpolation per frame)
- Guard: Only update `video.currentTime` when `!video.seeking`
- Snap immediately at scroll boundaries (scrollY <= 10 for v1, at bottom for v2)

**Crossfade (no dim):**
- Progress 0-0.45: v1 opacity 1, v2 opacity 0
- Progress 0.45-0.5: v1 stays at opacity 1, v2 fades from 0 to 1 (overlaid on top)
- Progress 0.5+: v1 opacity 0 (GPU savings), v2 opacity 1

---

### 2. DIAGONAL MARQUEE BANNER (fixed, z-50)

Container: `fixed top-14 left-[-170px] w-[650px] -rotate-[30deg] z-50 bg-[#0033FF] py-[18px] overflow-hidden select-none pointer-events-none shadow-2xl`

Inner: `.animate-marquee flex whitespace-nowrap`

Two identical `<span>` elements for seamless loop:
```
font-press-start text-[16px] text-[#85D743] tracking-widest px-4
```
Content: `WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!&nbsp;` (repeated twice)

Animation: `marquee 10s linear infinite` (translates X from 0 to -50%)

---

### 3. FLOATING STICKER - TOP LEFT (fixed, z-40)

Container: `fixed z-40 select-none pointer-events-none transition-transform duration-300`
- Inline style: `top: 232px`, `left: 120px`, `transform: rotate(32deg)`
- Image: STICKER1, `w-[100px] h-auto object-contain`, `referrerPolicy="no-referrer"`

---

### 4. FLOATING STICKER - BOTTOM RIGHT (fixed, z-40)

Container: `fixed bottom-8 right-8 z-40 select-none pointer-events-none transition-transform duration-300`
- Image: STICKER2, `w-[110px] sm:w-[150px] h-auto object-contain`, `referrerPolicy="no-referrer"`

---

### 5. NAVIGATION (fixed, z-50)

```
fixed top-10 right-8 md:right-16 z-50 flex gap-6 md:gap-10 font-press-start text-[10px] sm:text-xs md:text-sm text-white select-auto
```

Links: Projects, Expertise, About, Contact
- Each: `hover:text-[#85D743] transition-colors duration-200`
- Contact link: `onClick` prevents default, calls `window.scrollTo({ top: documentElement.scrollHeight, behavior: "smooth" })`

---

### 6. HERO TEXT - TYPEWRITER DELETION (fixed, z-30)

Container: `fixed top-0 left-0 w-full h-screen z-30 pointer-events-none flex flex-col justify-end p-8 md:p-16 pb-16 sm:pb-24`

H1: `font-press-start text-[#85D743] text-3xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl leading-[1.2] tracking-tight uppercase select-none max-w-5xl`

**Three lines:**

**Line 1: "PROBLEM"** -- 7 individual `<span className="inline-block relative">` characters (indices 1-7)

**Line 2: "WITH" + 2 stickers** -- wrapped in `inline-flex items-center gap-3 sm:gap-5 md:gap-7 align-middle`
- Letters W-I-T-H in nested `inline-flex items-center gap-[0.06em] sm:gap-[0.08em] md:gap-[0.1em]` (indices 8-11)
- STICKER4 image at index 12: `h-[0.85em] w-auto object-contain`, rotated `-8deg`
- STICKER3 image at index 13: `h-[0.85em] w-auto object-contain`, rotated `6deg`

**Line 3: "CREATIVE?"** -- 9 characters (indices 14-22)

**Total character count: 22**

**Cursor:** After the last visible character: `inline-block w-[0.14em] h-[0.8em] bg-[#85D743] ml-1 select-none animate-pulse align-middle`

**Deletion logic:**
- During scroll progress 0 to 0.25, characters are removed right-to-left
- `visibleCount = Math.round((1 - activeProgress) * 22)` where `activeProgress = min(progress, 0.25) / 0.25`

---

### 7. MANIFESTO - ROLLING CREDITS (fixed, z-25)

Container: `fixed top-0 left-0 w-full md:w-[70%] h-screen z-25 pointer-events-none flex flex-col justify-start p-8 md:p-16 pt-[12vh] pb-16 select-none`
- Initial inline style: `opacity: 0`, `transform: translateY(100vh)`

Text div: `font-press-start text-[#85D743] text-[20px] sm:text-[26px] md:text-[32px] leading-[1.35] tracking-tight uppercase text-left whitespace-pre-line select-none`

**Scroll behavior:**
- Begins after progress 0.25 + (200px / maxScroll) delay
- `alpha = (progress - startProgress) / (1 - startProgress)` [0 to 1]
- `opacity = min(1, alpha / 0.05)` (fast fade-in)
- `translateY = 100 - (alpha * 450)` in vh (scrolls from +100vh to -350vh)

**Exact manifesto text:**
```
LIMITLESS INPUTS OR
STANDARD LAYOUT
TEMPLATE
CONSUMERS. THIS IS
A HIGHLY SELECTIVE
ENVIRONMENT
ENGINEERED FOR
HYPER-PRODUCTIVE
CREATORS, UI/UX
VISIONARIES, AND
AI PROMPT
ARCHITECTS WHO
OPERATE AT THE
ABSOLUTE LIMITS OF
DIGITAL PRODUCT
CREATION. OUR
FRAMEWORK IS

---

WHY CHOOSE US?
1. ZERO MOCKUPS,
   ONLY REAL CODE.
2. SPEED RUNS -
   ZERO WASTED TIME.
3. DIGITAL EDGE -
   AESTHETIC
   DOMINANCE.
4. SYSTEM STATE -
   INTELLIGENT
   INTERACTION.

---

WE REJECT
THE BORING.
WE REJECT
THE STANDARD.

CHOOSE ABSOLUTE
CREATIVE EDGE.

THE FUTURE IS
NOW SECURED.
```

---

### 8. MOUSE TRAIL STICKERS (fixed, z-[60])

Container: `fixed inset-0 pointer-events-none z-[60] overflow-hidden`

**Behavior:**
- Track mouse position via `window.addEventListener("mousemove", ..., { passive: true })`
- Spawn new sticker when cursor moves > 150px from last spawn point
- 5 sticker types cycle sequentially (not randomly): trail_sticker1 through trail_sticker5
- Random rotation: `Math.random() * 40 - 20` degrees
- Max 4 stickers visible: `[...prev.slice(-3), newSticker]`
- Auto-remove after 2200ms via `setTimeout`

**Each sticker element:**
- `absolute select-none pointer-events-none flex items-center justify-center -translate-x-1/2 -translate-y-1/2`
- Inline style: `left: x`, `top: y`, `transform: translate(-50%, -50%) rotate(Xdeg)`, `--rot: Xdeg`
- `animation: sticker-fade-out 2.2s forwards cubic-bezier(0.16, 1, 0.3, 1)`
- Images: `w-[110px] sm:w-[150px] md:w-[180px] h-auto object-contain`, `referrerPolicy="no-referrer"`

---

### 9. FEEDBACK FORM (fixed, z-[55])

Container: `fixed left-1/2 z-[55] w-[92%] max-w-[460px] p-6 sm:p-8 bg-slate-950/95 border-4 border-[#0033FF] shadow-[10px_10px_0px_#85D743] select-auto transition-all duration-[900ms] pointer-events-auto`

**Position/Animation:**
- `bottom: 50%`
- When visible: `transform: translate(-50%, 50%) rotate(0deg)`
- When hidden: `transform: translate(-50%, 150vh) rotate(15deg)`
- `transitionTimingFunction: cubic-bezier(0.16, 1, 0.3, 1)`

**Triggers at:** scroll progress >= 0.95

**Close button:** `absolute top-4 right-4 font-press-start text-[14px] text-slate-500 hover:text-red-500 hover:scale-110 active:scale-95 transition-all cursor-pointer select-none border-none bg-transparent` -- content: `[X]`

**Form (default state):**
- Title: "FEEDBACK SYSTEM" -- `font-press-start text-xs sm:text-sm text-[#85D743] tracking-widest uppercase text-center mb-1`
- Name input: `type="text" required placeholder="YOUR NAME"` -- `font-mono text-xs text-white bg-slate-900 border-2 border-slate-700 focus:border-[#85D743] hover:border-slate-500 focus:outline-none p-2.5 w-full uppercase transition-all placeholder-slate-600`
- Email input: `type="email" required placeholder="NAME@DOMAIN.COM"` -- same styles minus `uppercase`
- Textarea: `required rows={3} placeholder="FEEDBACK / ARCHITECTURE IDEAS..."` -- same styles plus `resize-none`
- Submit button: "LAUNCH TRANSMISSION" -- `font-press-start text-[8px] sm:text-[9px] text-black bg-[#85D743] hover:bg-[#9bfb4e] active:translate-y-0.5 active:shadow-none border-2 border-black py-3 px-6 shadow-[4px_4px_0px_#0033FF] w-full font-bold uppercase tracking-widest cursor-pointer select-none transition-all mt-1`
- Form gap: `flex flex-col gap-4 sm:gap-5`

**Success state:**
- Symbol: `font-press-start text-[32px] text-[#85D743] mb-4 animate-bounce` -- content: `✦`
- Heading: "TRANSMISSION SUCCESS" -- `font-press-start text-xs sm:text-sm text-[#85D743] mb-3 tracking-widest uppercase`
- Subtext: "Your feedback is secured in our neural network database." -- `font-mono text-[10px] sm:text-xs text-slate-400 max-w-sm mb-6 uppercase leading-relaxed`
- Reset button: "[ NEW TRANSMISSION ]" -- `font-press-start text-[8px] sm:text-[10px] text-black bg-[#85D743] hover:bg-[#9eff5c] border-2 border-black py-2.5 px-5 font-bold uppercase tracking-wider shadow-[3px_3px_0px_#0033FF] active:translate-y-0.5 active:shadow-none transition-all cursor-pointer`

---

## SERVER (`server.ts`)

Express server on port 3000. In development: Vite middleware mode (SPA). In production: serves static `dist/` directory.

```typescript
import express from "express";
import path from "path";
import fs from "fs";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;
  const publicDir = path.join(process.cwd(), "public");
  if (!fs.existsSync(publicDir)) fs.mkdirSync(publicDir, { recursive: true });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({ server: { middlewareMode: true }, appType: "spa" });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => res.sendFile(path.join(distPath, "index.html")));
  }

  app.listen(PORT, "0.0.0.0", () => console.log(`Server running on http://localhost:${PORT}`));
}
startServer();
```

---

## VITE CONFIG (`vite.config.ts`)

```typescript
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig(() => ({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(__dirname, '.') } },
}));
```

---

## CRITICAL IMPLEMENTATION DETAILS

1. **No auto-play videos** -- videos are paused immediately after a play() call to warm up the decoder. Scroll scrubbing sets `currentTime` directly.
2. **Seeking guard** -- `if (!video.seeking)` prevents setting new frames while browser is still rendering the previous seek.
3. **No dim on crossfade** -- Video 1 stays at full opacity while video 2 fades in on top. Only after transition completes does video 1 go to opacity 0.
4. **All images use `referrerPolicy="no-referrer"`** to avoid Figma CDN blocking.
5. **State updates use equality check** -- `setX((prev) => prev !== newVal ? newVal : prev)` to avoid unnecessary re-renders during scroll.
6. **The manifesto translates a total of 450vh** (from +100vh to -350vh) to ensure it fully scrolls off screen.
7. **Mouse trail uses sequential cycling** (`typeCounter % 5`), not random selection.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "OYLA"
template_id: "32c5e8f7-2316-44b2-a156-f91b9d80bb3f"
section: "sites"
category_slug: "ecommerce"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 OYLA

> **Секція:** `SITES` | **Категорія:** `ecommerce`  
> **ID шаблону:** `32c5e8f7-2316-44b2-a156-f91b9d80bb3f`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Ecommerce

### 🖼 Прев'ю:
![OYLA](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/a669a7a4-184b-4bed-8c30-bc8b16df6e9d.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
**Build a luxury handcrafted jewelry brand landing page for "OYLA" — a single-page app using Vite + Express with an `index.html` entry point served through Vite's SPA middleware in development and Express static serving in production. The page features scroll-driven video scrubbing, horizontal product carousel with video reveal, a two-column stats section, and a fixed footer reveal. Use GSAP + ScrollTrigger for all scroll-driven animations.**

---

### BUILD & SERVING ARCHITECTURE

- **Dev:** Express server (`tsx server.ts`) on port 3000 with Vite mounted as middleware (`createViteServer({ server: { middlewareMode: true }, appType: "spa" })`)
- **Build:** `vite build` compiles the frontend into `dist/`, then `esbuild` bundles `server.ts` into `dist/server.cjs` (Node CJS, external packages)
- **Production:** Express serves the `dist/` folder as static, with a catch-all route serving `index.html`
- The main page content lives in `index.html` at the project root (Vite entry point) with inline `<style>` and `<script>` tags
- Express provides an API proxy endpoint at `GET /api/higgsfield-video` that extracts direct MP4 URLs from Higgsfield share pages

---

### BRAND & DESIGN SYSTEM

- **Brand name:** OYLA (handcrafted rings studio, based in Berlin, est. 2019)
- **Brand color:** `#A3111E` (deep crimson red) used for header text, logo, and navigation only
- **Background:** Pure white `#ffffff`
- **Text:** Pure black `#000000` for all body and heading text
- **Dividers:** `#000000` solid 1px lines
- **Color palette:** Strictly black and white with the single crimson accent for the header/nav only

### FONTS (Google Fonts)

Load these exact fonts:
- **Instrument Serif** (weights: 400, italic 400) — used for all large display headings (hero title, stat numbers, left column heading)
- **Inter Tight** (weights: 300–700, italic 300–700) — used for body text, buttons, navigation, footer, and all UI elements
- **Cormorant Garamond** (weights: 300–700, italic) — loaded but not actively used (available for future use)

CSS font stacks:
- Headings: `'Instrument Serif', Georgia, serif`
- Body/UI: `'Inter Tight', 'Inter', Arial, sans-serif`

### CSS VARIABLES

```css
:root {
  --color-bg: #ffffff;
  --color-primary-text: #000000;
  --color-demoted-text: #000000;
  --color-divider: #000000;
  --font-stack: 'Inter Tight', 'Inter', Arial, sans-serif;
}
```

---

### STRUCTURE (TOP TO BOTTOM)

---

#### 1. FIXED HEADER

- **Position:** Fixed, `top: 32px`, `left: 32px`, `right: 32px`, `height: 30px`, `z-index: 100`
- **Layout:** Flexbox row, space-between, center aligned
- **Left:** OYLA logo as inline SVG (112x60px viewBox), all paths filled `#A3111E`. The logo contains the letters "OYLA" in a custom serif typeface with a distinctive "O" made of two concentric ellipses
- **Right:** Navigation group containing:
  - "ABOUT" link — `font-size: 15px`, `font-weight: 500`, uppercase, `color: #A3111E`, `gap: 194px` from the cart/menu group
  - Cart/Menu group (`gap: 50px`):
    - Hamburger button: 2 horizontal lines, each `30px` wide, `2.2px` height, `#A3111E`, `5px` gap between them
    - "[ BAG ]" button text — same 15px/500 style as ABOUT, `color: #A3111E`
- **Hover states:** `opacity: 0.7` on all interactive header elements

---

#### 2. SCROLL-DRIVEN VIDEO HERO SECTION

- **Container:** `height: 500vh` (creates the scroll distance for video scrubbing), `background: #000000`, `z-index: 10`
- **Sticky viewport:** `position: sticky; top: 0; height: 100vh`, black background, flex column, content pinned to bottom-left with `padding: 48px`
- **Video element:** Absolutely positioned, full-cover (`object-fit: cover`), `z-index: 1`, playsinline, muted, preload="auto"
  - **Primary video URL:** `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260627_212146_743b92b3-40a3-46cb-988d-7bf716564ec3.mp4`
- **Hero content overlay** (`z-index: 3`, `max-width: 700px`, left-aligned):
  - **Title:** "MEASURED" on line 1, "PURITY" on line 2
    - Font: Instrument Serif, `clamp(36px, 6vw, 72px)`, weight 400, `line-height: 1.05`, `letter-spacing: -1px`, `color: #000000`
    - Each line wrapped in `<span class="hero-title-line"><span class="hero-title-line-inner">...</span></span>`
  - **DISCOVER button** (below title, `margin-top: 10px`):
    - Capsule shape: white background, `border: 1px solid rgba(0,0,0,0.08)`, `border-radius: 100px`, `padding: 4px 4px 4px 18px`
    - Text "DISCOVER" — 13px, weight 500, uppercase
    - Circle icon: `28px` diameter, `#2e2e2e` background, white `+` cross made with `::before`/`::after` pseudo-elements (10px x 1.5px horizontal, 1.5px x 10px vertical)
    - Hover: background flips to `#000000`, text becomes white, circle becomes white with black cross
    - Click action: smooth scrolls to the footer

---

### CRITICAL VIDEO SCRUBBING TECHNIQUE

The video scrubbing uses a `requestAnimationFrame` loop with a **seeking guard** — this is the most important performance pattern:

```js
if (!video.seeking && Math.abs(video.currentTime - currentTime) > 0.01) {
  video.currentTime = currentTime;
}
```

**The `!video.seeking` check is essential.** We tell the browser: "Update the video frame ONLY when you have completely finished rendering the previous one." (Оновлюй кадр відео ТІЛЬКИ тоді, коли ти повністю закінчив малювати попередній.) Without this guard, the browser's video decoder gets flooded with seek requests, causing freezing, black frames, and stuttering. The smooth interpolation (`currentTime += (targetTime - currentTime) * 0.08`) combined with this seeking guard creates a buttery-smooth cinematic scrubbing experience.

**Full scrubbing behavior:**
- Video is paused; `currentTime` is driven by scroll position within the 500vh container
- Smooth interpolation: `currentTime += (targetTime - currentTime) * 0.08` in a `requestAnimationFrame` loop
- Only updates `currentTime` when `!video.seeking` AND delta > 0.01
- At 80%+ scroll progress, hero text characters individually fade out, blur, and shift upward (per-character staggered animation using cubic easing)
- The DISCOVER button also fades/shifts up with `pow(progress, 4)` easing

**Text splitting:** On DOMContentLoaded, each `.hero-title-line-inner` text is split into individual `<span class="hero-char">` elements for per-character animation.

---

#### 3. HORIZONTAL PRODUCT CAROUSEL (Awards Section)

- **Section:** Full viewport height (`100vh`), `overflow: hidden`, `border-top` and `border-bottom: 1px solid #000`, `z-index: 10`
- **Grid:** Flexbox row, `width: max-content`, containing 6 product cards
- **Each card:** `width: 33.333vw`, `border-right: 1px solid #000`, white background, centered content with `padding: clamp(40px, 8vh, 80px) 48px`, `gap: clamp(24px, 4vh, 48px)`
  - Image container: `height: 280px`, centered, `max-width: 85%`, `object-fit: contain`
  - Product name: 18px, weight 400, `letter-spacing: -0.2px`
  - Price: 16px, weight 500, `opacity: 0.6`

**Products (with exact CloudFront image URLs):**

1. **Obsidian Coil** — $480
   - Image: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144408_92b74dc4-ca69-412a-acfd-304f9b29eb5e_min.webp`

2. **Void Arc** — $560
   - Image: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_145142_ed02063b-d983-47d2-b60b-4b4a5a3448bd_min.webp`

3. **Onyx Hex** — $620
   - Image: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144747_f21bc119-e460-45be-a071-851291bd71c5_min.webp`

4. **Shadow Sigil** — $740
   - Image: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260627_215521_100b78bd-d24a-4225-b2e8-5bb30d44af73_min.webp`

5. **Eclipse Band** — $820
   - Image: (same as Obsidian Coil) `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144408_92b74dc4-ca69-412a-acfd-304f9b29eb5e_min.webp`

6. **Matte Skull** — $950
   - Image: (same as Void Arc) `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_145142_ed02063b-d983-47d2-b60b-4b4a5a3448bd_min.webp`

**GSAP ScrollTrigger animation:**
- Section is pinned (`pin: true`, `start: "top top"`)
- Phase 1: Grid scrolls horizontally (translateX from 0 to negative overflow distance), `scrub: true`, `ease: "none"`
- Phase 2: After horizontal scroll completes, a `.video-scaling-wrapper` element symmetrically expands from `width: 0%` to `width: 100%` centered (`left: 50%; transform: translateX(-50%)`) revealing a second scroll-scrubbed video beneath

**Second video:**
- URL: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_122130_8b16d300-75cb-49f5-82ce-afd6b79c2d79.mp4`
- Positioned `absolute`, centered with `transform: translate(-50%, -50%)`, `width: 100vw`, `height: 100vh`, `object-fit: cover`
- Uses the same `!video.seeking` guard pattern for smooth scrubbing
- Scrubbed in sync with the expansion progress using the same smooth interpolation technique (0.08 lerp factor)

---

#### 4. TWO-COLUMN STATS & COPY SECTION

- **Layout:** CSS Grid `50% 50%`, `border-bottom: 1px solid #000`
- **Left column:** `position: sticky; top: 0; height: 100vh`, flex column, `justify-content: space-between`, `padding: 48px 96px 48px 48px`
  - **Heading:** "Made Without Compromise" — Instrument Serif, `clamp(32px, 4vw, 42px)`, weight 400, `line-height: 1.15`
  - **3 paragraphs** (Inter Tight, 24px, weight 400, `line-height: 1.1`, `letter-spacing: -0.2px`, `gap: 32px`):
    1. "Each ring is forged by a single pair of hands — no factory floor, no assembly line. The material is chosen first; the form follows its nature."
    2. "We work in oxidized silver, blackened bronze, and raw brass. Weights are deliberate. Edges are left where they fall. Nothing is smoothed for comfort."
    3. "OYLA exists for those who wear jewelry that means something. Not decoration — declaration. One piece at a time, made to last a lifetime."
  - **VIEW COLLECTION button** (same capsule style as DISCOVER button)
  - All left-column elements have `data-fade-slide-in` attribute for scroll-triggered fade+slide animation (autoAlpha 0->1, y 20->0, stagger 0.15, duration 0.8, power2.out)

- **Right column:** `border-left: 1px solid #000`, scrollable, contains 4 stat cards:
  - Each card: `padding: 48px`, `min-height: 45vh`, `border-bottom: 1px solid #000` (except last)
  - Each card has a "stomp-wrapper" with two "stomp-stack" divs (stack-a and stack-b), each containing duplicate h1 headings (first is hidden via CSS `:first-child { display: none }`)
  - Heading font: Instrument Serif, `clamp(46px, 5.5vw, 70px)`, `letter-spacing: -1.5px`, `line-height: 0.95`
  - Detail paragraph below: 24px, `padding-top: 42px`, `line-height: 1.2`

**Stat cards content:**

| Stack A | Stack B | Detail |
|---------|---------|--------|
| 100% | Handmade | Every ring crafted by a single artisan, start to finish |
| 14-92g | Per piece | Deliberate weight — each ring is a physical presence you feel |
| Sterling | & Silver | Oxidized metals only — no plating, no compromise |
| Lifetime | Guarantee | We stand behind every piece we make, forever |

Card 4 also has: `<p class="card-subtext">Est. OYLA Studio, 2019.</p>` (13px, `margin-top: 12px`)

**Text splitting for stats:** Each visible `.heading-style-h1:last-child` is split into `<span class="stat-char">` elements. Each `.detail-paragraph` is split into `<span class="detail-word">` elements.

---

#### 5. FOOTER (Fixed Reveal Pattern)

- **Position:** `position: fixed; bottom: 0; left: 0; z-index: 1` — revealed as main content scrolls past
- **A `.footer-spacer` div** (transparent, pointer-events none) sits in the normal flow with its height dynamically set to match the footer's height, creating the reveal effect
- **Layout:** CSS Grid `1.2fr 1fr 1.5fr`, `gap: 48px`, `padding: 80px 48px`, white background

**Column 1 — Sign in & Credits:**
- Header: "Sign in" link (18px, weight 400, `letter-spacing: -0.2px`)
- Credits block (18px, `line-height: 1.35`):
  ```
  Handcrafted in small batches
  OYLA Studio
  [blank line]
  Based in Berlin
  (c) OYLA 2026
  All pieces are original designs.
  ```

**Column 2 — Links:**
- Header: "Instagram" link
- Links list (`gap: 12px`): Refund Policy, Privacy Policy, Terms of Service
- All links: 18px, weight 400, hover `opacity: 0.6`

**Column 3 — Newsletter:**
- Header: "Newsletter" (h3, 18px, weight 400)
- Description: "Join our list. Be first to know new drops. 10% off your first order." (18px, `line-height: 1.35`, `max-width: 380px`, `margin-bottom: 24px`)
- Form: Capsule input (`background: #f7f7f5`, `border-radius: 100px`, `padding: 6px 6px 6px 24px`, `max-width: 440px`)
  - Input: placeholder "Email", 14px, transparent background
  - Focus state: `box-shadow: 0 0 0 1px #000000`
  - Submit button: same capsule button pattern with "SUBSCRIBE" text and `+` circle
  - On submit: `alert('You're on the list. Welcome.')`

---

### RESPONSIVE BREAKPOINTS

**Tablet (769px - 1199px):**
- Header: 24px safe zone, nav gap 100px, cart/menu gap 32px
- Left column: padding 40px 32px
- Hero title: 48px fixed
- Stat headings: 44px !important
- Left heading: 30px
- Body text: 18px
- Award cards: 50vw width
- Footer: 2-column grid (last col spans 2)

**Mobile (<=768px):**
- Header: 16px safe zone, 44px touch targets
- Grid collapses to 1 column
- Left column: no longer sticky, auto height
- Hero title: 38px
- Stat headings: 34px !important
- Body text: 15px
- Award cards: 85vw width
- Footer: 1 column, 48px 16px padding
- All buttons: min-height 44px, full-width where appropriate

---

### JAVASCRIPT ANIMATION SYSTEM

Uses GSAP 3.12.5 + ScrollTrigger (loaded from CDN):
```
https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js
https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js
```

Key behaviors:
1. **Video scrub loop** — requestAnimationFrame loop reads scroll position, lerps to target time, uses `!video.seeking` guard to prevent decoder flooding
2. **Hero text exit** — per-character opacity/blur/translateY driven by scroll progress > 80%
3. **Awards horizontal scroll + video reveal** — GSAP timeline with ScrollTrigger pin
4. **Left panel fade-in** — staggered autoAlpha/y animation on scroll
5. **Footer spacer** — dynamically matches footer height for reveal effect
6. **Resize handling** — debounced (200ms), kills all ScrollTriggers and rebuilds on width change
7. **Font-ready init** — animations initialize on `document.fonts.ready` (not window.load) to avoid waiting for slow CDN video downloads

---

### SERVER (Express + Vite)

- Express server on port 3000
- API endpoint `GET /api/higgsfield-video` — proxy that fetches a Higgsfield share page, extracts the direct MP4 URL from HTML source (via regex matching for .mp4 URLs and og:video meta tags), returns JSON `{ success: true, url: "..." }`
- Default share URL: `https://higgsfield.ai/s/keldUFnImRA`
- Second video fetched with query param: `?url=https://higgsfield.ai/s/iK6bYyCxd0I`
- In dev mode: mounts Vite middleware (`middlewareMode: true`, `appType: "spa"`) for HMR
- In production: serves static dist folder with catch-all to `index.html`

---

### KEY IMPLEMENTATION NOTES

- The page content lives in `index.html` with inline CSS and JS (Vite processes it as the SPA entry point)
- Videos have hardcoded CloudFront CDN fallback URLs and also attempt dynamic refresh from the Higgsfield proxy API on page load
- The `.video-overlay` div exists but is fully disabled (`display: none`, transparent)
- Duplicate h1 headings in stomp-stacks: first child hidden by CSS `:first-child { display: none }`, second child is the visible/animated one
- `will-change: width` on video-scaling-wrapper, `will-change: transform` on awards-grid
- `pointer-events: none` on video-scaling-wrapper when width is 0%
- The `!video.seeking` guard is used on BOTH video elements to prevent decoder overload — this is the single most important performance detail for scroll-scrubbed video

SOURCE CODE:
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OYLA — Handcrafted Rings</title>
    
    <!-- Load Inter Tight Font from Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700&family=Instrument+Serif:ital,wght@0,400;1,400&family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet">

    <!-- CSS Styling -->
    <style>
      :root {
        --color-bg: #ffffff;
        --color-primary-text: #000000;
        --color-demoted-text: #000000;
        --color-divider: #000000;
        --font-stack: 'Inter Tight', 'Inter', Arial, sans-serif;
      }

      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      body {
        background-color: var(--color-bg);
        color: var(--color-primary-text);
        font-family: var(--font-stack);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        overflow-x: hidden;
      }

      /* SCROLL-DRIVEN VIDEO HERO */
      .scroll-video-container {
        position: relative;
        height: 500vh; /* Smooth, luxurious scrubbing distance */
        background-color: #000000;
        width: 100%;
        z-index: 10;
      }

      .video-hero-sticky {
        position: sticky;
        top: 0;
        height: 100vh;
        width: 100%;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-end; /* Pin to the bottom of the screen */
        align-items: flex-start;
        background-color: #000000;
        padding: 48px;
        box-sizing: border-box;
      }

      #scroll-video {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: 1;
      }

      /* SECOND SCROLL-DRIVEN VIDEO IN PINNED SECTION */
      .video-scaling-wrapper {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 0%; /* Initial state, expanded via GSAP */
        height: 100%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #000000;
        z-index: 50; /* Place on top of horizontal cards */
        will-change: width;
        pointer-events: none; /* Let clicks pass when width is 0% */
      }

      #scroll-video-second {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: 1;
      }

      .video-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: transparent; /* No darkening */
        z-index: 2;
        pointer-events: none;
        display: none; /* Fully disabled */
      }

      .hero-content {
        position: relative;
        z-index: 3;
        max-width: 700px;
        width: 100%;
        text-align: left;
      }

      .hero-tag {
        font-size: 11px;
        letter-spacing: 0.15em;
        color: #000000; /* Pure black */
        text-transform: uppercase;
        margin-bottom: 20px;
        display: inline-block;
        font-weight: 400;
      }

      .hero-title {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: clamp(36px, 6vw, 72px);
        font-weight: 400;
        color: #000000; /* Pure black */
        line-height: 1.05;
        letter-spacing: -1px;
        margin-bottom: 24px;
      }

      .hero-title-line {
        display: block;
      }

      .hero-title-line-inner {
        display: block;
        will-change: transform;
      }

      .hero-subtitle {
        font-size: 18px;
        line-height: 1.4;
        color: #000000; /* Pure black */
        font-weight: 400;
      }

      .scroll-indicator {
        margin-top: 48px;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #000000; /* Pure black */
        font-weight: 400;
        display: inline-block;
        transition: opacity 0.3s ease;
      }

      .scroll-indicator .arrow {
        margin-top: 8px;
        animation: bounce 2s infinite;
      }

      @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
          transform: translateY(0);
        }
        40% {
          transform: translateY(-8px);
        }
        60% {
          transform: translateY(-4px);
        }
      }

      /* MAIN OUTER SECTION */
      .outer-section {
        width: 100%;
        background-color: var(--color-bg);
        position: relative;
        z-index: 10;
        border-bottom: 1px solid var(--color-divider);
      }

      /* TWO-COLUMN GRID Layout */
      .grid-container {
        display: grid;
        grid-template-columns: 50% 50%;
        width: 100%;
        position: relative;
      }

      /* LEFT COLUMN - Sticky */
      .left-column {
        position: sticky;
        top: 0;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 48px 96px 48px 48px;
        box-sizing: border-box;
      }

      .left-heading {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: clamp(32px, 4vw, 42px);
        font-weight: 400;
        color: var(--color-primary-text);
        margin: 0;
        line-height: 1.15;
      }

      .left-middle {
        display: flex;
        flex-direction: column;
        gap: 32px;
        margin-top: 40px;
        margin-bottom: 40px;
      }

      .left-p {
        color: var(--color-demoted-text);
        font-size: 24px;
        line-height: 1.1;
        letter-spacing: -0.2px;
        margin: 0;
        font-weight: 400;
      }

      .left-bottom {
        display: block;
      }

      .explore-btn {
        text-transform: uppercase;
        font-size: 13px;
        letter-spacing: 0.1em;
        border: 1px solid var(--color-primary-text);
        color: var(--color-primary-text);
        border-radius: 100px;
        padding: 12px 24px;
        background: transparent;
        cursor: pointer;
        font-weight: 400;
        transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
        outline: none;
      }

      .explore-btn:hover {
        background-color: var(--color-primary-text);
        color: var(--color-bg);
      }

      .explore-btn:active {
        transform: scale(0.97);
      }

      /* RIGHT COLUMN - Scrolling flow */
      .right-column {
        border-left: 1px solid var(--color-divider);
        width: 100%;
        box-sizing: border-box;
      }

      /* 4 STAT CARDS */
      .right-card {
        width: 100%;
        padding: 48px;
        border-bottom: 1px solid var(--color-divider);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 45vh;
        box-sizing: border-box;
      }

      /* Remove border bottom on the last card */
      .right-card:last-child {
        border-bottom: none;
      }

      /* Stomp slots structure */
      .stomp-wrapper {
        display: flex;
        flex-direction: column;
      }

      .stomp-stack {
        position: relative;
        width: 100%;
        overflow: hidden;
      }

      .stomp-track {
        display: flex;
        flex-direction: column;
        width: 100%;
      }

      .heading-style-h1 {
        font-family: 'Instrument Serif', Georgia, serif;
        font-size: clamp(46px, 5.5vw, 70px);
        letter-spacing: -1.5px;
        line-height: 0.95;
        margin: 0;
        padding: 0;
        white-space: nowrap;
        font-weight: 400;
      }

      /* Hide structural duplicate h1s — CSS-level, no GSAP timing dependency */
      .stomp-stack .heading-style-h1:first-child {
        display: none;
      }

      /* Color pairings for stacks */
      .stack-a .heading-style-h1 {
        color: var(--color-primary-text);
      }

      .stack-b .heading-style-h1 {
        color: var(--color-demoted-text);
      }

      /* Detail paragraphs & subtexts */
      .detail-paragraph {
        font-size: 24px;
        color: var(--color-demoted-text);
        padding-top: 42px;
        line-height: 1.2;
        margin: 0;
        letter-spacing: -0.2px;
        font-weight: 400;
      }

      .card-subtext {
        font-size: 13px;
        color: var(--color-demoted-text);
        margin-top: 12px;
        font-weight: 400;
      }

      /* REPLICA FOOTER STYLING */
      .replica-footer {
        background-color: #ffffff;
        color: #000000;
        padding: 80px 48px;
        font-family: var(--font-stack);
        display: grid;
        grid-template-columns: 1.2fr 1fr 1.5fr;
        gap: 48px;
        box-sizing: border-box;
        width: 100%;
        position: fixed;
        bottom: 0;
        left: 0;
        z-index: 1;
      }

      .footer-col {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
      }

      .footer-header-item {
        height: 24px; /* Align row 1 elements to a single line */
        margin-bottom: 48px; /* Consistent margin before row 2 elements start */
        display: flex;
        align-items: center;
      }

      .footer-header-link {
        font-size: 18px;
        font-weight: 400;
        color: #000000;
        text-decoration: none;
        letter-spacing: -0.2px;
        line-height: 1.2;
        transition: opacity 0.25s ease;
      }

      .footer-header-link:hover {
        opacity: 0.6;
      }

      .footer-header-text {
        font-size: 18px;
        font-weight: 400;
        color: #000000;
        letter-spacing: -0.2px;
        line-height: 1.2;
        margin: 0;
      }

      .footer-content-item {
        display: flex;
        flex-direction: column;
      }

      .footer-links-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .footer-link {
        font-size: 18px;
        font-weight: 400;
        color: #000000;
        text-decoration: none;
        transition: opacity 0.25s ease;
        letter-spacing: -0.2px;
        width: fit-content;
      }

      .footer-link:hover {
        opacity: 0.6;
      }

      .footer-credits {
        font-size: 18px;
        line-height: 1.35;
        color: #000000;
        margin-top: 0; /* Align directly to the header container bottom */
        letter-spacing: -0.2px;
      }

      .footer-credits p {
        margin-bottom: 2px;
      }
      
      .footer-credits p:last-child {
        margin-bottom: 0;
      }

      .newsletter-desc {
        font-size: 18px;
        line-height: 1.35;
        color: #000000;
        letter-spacing: -0.2px;
        margin-top: 0; /* Align directly to the header container bottom */
        margin-bottom: 24px;
        max-width: 380px;
      }

      .newsletter-form {
        position: relative;
        display: flex;
        align-items: center;
        background-color: #f7f7f5; /* Elegant warm off-white capsule */
        border-radius: 100px;
        padding: 6px 6px 6px 24px;
        width: 100%;
        max-width: 440px;
        box-sizing: border-box;
        transition: box-shadow 0.25s ease;
      }

      .newsletter-form:focus-within {
        box-shadow: 0 0 0 1px #000000;
      }

      .newsletter-input {
        border: none;
        background: transparent;
        color: #000000;
        font-family: var(--font-stack);
        font-size: 14px;
        width: 100%;
        outline: none;
        padding: 10px 0;
      }

      .newsletter-input::placeholder {
        color: #000000;
        opacity: 0.4;
      }

      .newsletter-btn-wrapper {
        display: flex;
        align-items: center;
        background-color: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 100px;
        padding: 4px 4px 4px 18px;
        cursor: pointer;
        transition: background-color 0.25s ease, transform 0.25s ease;
        margin-left: 12px;
        flex-shrink: 0;
      }

      .newsletter-btn-wrapper:hover {
        background-color: #000000;
        color: #ffffff;
      }

      .newsletter-btn-text {
        font-size: 13px;
        font-weight: 500;
        letter-spacing: -0.1px;
        margin-right: 8px;
        user-select: none;
        text-transform: uppercase;
      }

      .newsletter-btn-circle {
        width: 28px;
        height: 28px;
        background-color: #2e2e2e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0;
        position: relative;
        flex-shrink: 0;
        transition: background-color 0.25s ease;
      }

      .newsletter-btn-circle::before,
      .newsletter-btn-circle::after {
        content: '';
        position: absolute;
        background-color: #ffffff;
        top: 50%;
        left: 50%;
        border-radius: 1px;
        transition: background-color 0.25s ease;
      }

      .newsletter-btn-circle::before {
        width: 10px;
        height: 1.5px;
        transform: translate(-50%, -50%);
      }

      .newsletter-btn-circle::after {
        width: 1.5px;
        height: 10px;
        transform: translate(-50%, -50%);
      }

      .newsletter-btn-wrapper:hover .newsletter-btn-circle {
        background-color: #ffffff;
      }

      .newsletter-btn-wrapper:hover .newsletter-btn-circle::before,
      .newsletter-btn-wrapper:hover .newsletter-btn-circle::after {
        background-color: #000000;
      }

      /* AWARDS SECTION STYLING */
      .awards-section {
        width: 100%;
        height: 100vh;
        background-color: var(--color-bg);
        border-top: 1px solid var(--color-divider);
        border-bottom: 1px solid var(--color-divider);
        box-sizing: border-box;
        overflow: hidden;
        position: relative;
        z-index: 10;
      }

      .awards-grid {
        display: flex;
        flex-direction: row;
        width: max-content;
        height: 100%;
        box-sizing: border-box;
        will-change: transform;
      }

      .award-card {
        padding: clamp(40px, 8vh, 80px) 48px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: clamp(24px, 4vh, 48px);
        height: 100%;
        width: 33.333vw;
        box-sizing: border-box;
        border-right: 1px solid var(--color-divider);
        background-color: #ffffff;
        flex-shrink: 0;
      }

      .award-card:last-child {
        border-right: none;
      }

      .award-image-container {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 280px;
        flex: none;
      }

      .award-img {
        max-width: 85%;
        max-height: 100%;
        object-fit: contain;
      }

      .award-text-container {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        width: 100%;
      }

      .award-title {
        font-size: 18px;
        font-weight: 400;
        color: #000000;
        letter-spacing: -0.2px;
        line-height: 1.3;
        margin: 0;
      }

      .award-price {
        font-size: 16px;
        font-weight: 500;
        color: #000000;
        opacity: 0.6;
        margin: 0;
      }

      /* OYLA HEADER STYLING */
      .oyla-header {
        position: fixed;
        left: 32px;
        right: 32px;
        top: 32px;
        height: 30px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 0;
        z-index: 100;
        box-sizing: border-box;
        background: transparent;
      }

      /* OYLA Logo */
      .oyla-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        height: 60px;
        width: 112px;
      }

      /* Header Nav */
      .oyla-header-nav {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 0px;
        gap: 194px;
        width: auto;
        height: 30px;
      }

      /* About */
      .oyla-about-link {
        width: 50px;
        height: 18px;
        font-family: 'Inter Tight', 'Inter', sans-serif;
        font-style: normal;
        font-weight: 500;
        font-size: 15px;
        line-height: 18px;
        text-transform: uppercase;
        color: #A3111E;
        text-decoration: none;
        mix-blend-mode: normal;
        display: inline-block;
        transition: opacity 0.2s ease;
      }

      .oyla-about-link:hover {
        opacity: 0.7;
      }

      /* Cart + Menu */
      .oyla-cart-menu {
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0px;
        gap: 50px;
        width: 126px;
        height: 30px;
      }

      /* Burger */
      .oyla-burger-btn {
        width: 30px;
        height: 30px;
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 5px;
        position: relative;
        transition: opacity 0.2s ease;
      }

      .oyla-burger-btn:hover {
        opacity: 0.7;
      }

      .burger-line {
        width: 30px;
        height: 2.2px;
        background-color: #A3111E;
        display: block;
        transition: transform 0.3s ease, opacity 0.3s ease;
      }

      /* [ BAG ] */
      .oyla-bag-btn {
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        width: 46px;
        height: 18px;
        font-family: 'Inter Tight', 'Inter', sans-serif;
        font-style: normal;
        font-weight: 500;
        font-size: 15px;
        line-height: 18px;
        color: #A3111E;
        text-transform: uppercase;
        transition: opacity 0.2s ease;
      }

      .oyla-bag-btn:hover {
        opacity: 0.7;
      }

      /* ==========================================================================
         TABLET STYLES (769px – 1199px)
         ========================================================================== */
      @media (min-width: 769px) and (max-width: 1199px) {
        /* Container and spacing overrides (Safe zone min 24px) */
        .oyla-header {
          left: 24px;
          right: 24px;
          top: 24px;
        }

        .oyla-header-nav {
          gap: 100px;
          width: auto;
        }

        .oyla-cart-menu {
          gap: 32px;
          width: auto;
        }

        .left-column {
          padding: 40px 32px;
        }

        .left-middle {
          gap: 24px;
          margin-top: 28px;
          margin-bottom: 28px;
        }

        .right-card {
          padding: 32px;
          min-height: 40vh;
        }

        /* Typography scale (preserves strict hierarchy: h1 > h2 > h3 > body-large) */
        .hero-title {
          font-size: 48px;
          line-height: 1.1;
          margin-bottom: 20px;
        }

        .heading-style-h1 {
          font-size: 44px !important;
          line-height: 1.05;
          letter-spacing: -1px;
        }

        .left-heading {
          font-size: 30px;
          line-height: 1.2;
        }

        .left-p,
        .detail-paragraph {
          font-size: 18px;
          line-height: 1.35;
        }

        .card-subtext {
          font-size: 12px;
          margin-top: 10px;
        }

        /* Awards section */
        .award-card {
          width: 50vw;
          padding: 40px 32px;
          gap: 24px;
        }

        .award-image-container {
          height: 220px !important;
        }

        .award-title {
          font-size: 16px;
          line-height: 1.3;
        }

        .award-price {
          font-size: 14px;
        }

        /* Footer overrides */
        .replica-footer {
          grid-template-columns: 1fr 1fr;
          padding: 60px 32px;
          gap: 32px;
        }

        .footer-col:last-child {
          grid-column: span 2;
          min-height: auto;
          margin-top: 24px;
        }

        .footer-header-item {
          margin-bottom: 32px;
        }

        .footer-header-link,
        .footer-header-text,
        .footer-link,
        .footer-credits,
        .newsletter-desc {
          font-size: 15px;
          line-height: 1.35;
        }

        .newsletter-form {
          padding: 6px 6px 6px 20px;
          max-width: 400px;
        }

        .newsletter-input {
          font-size: 13px;
        }
      }

      /* ==========================================================================
         MOBILE STYLES (≤ 768px)
         ========================================================================== */
      @media (max-width: 768px) {
        /* Container and safe zone (min 16px safe zone) */
        .oyla-header {
          left: 16px;
          right: 16px;
          top: 16px;
          height: 44px;
          display: flex;
          align-items: center;
        }

        .oyla-header-nav {
          gap: 16px;
          width: auto;
          height: 44px;
        }

        .oyla-cart-menu {
          gap: 16px;
          width: auto;
          height: 44px;
        }

        /* Expand header targets to minimum touch size (44px) */
        .oyla-about-link {
          font-size: 14px;
          height: 44px;
          display: inline-flex;
          align-items: center;
          padding: 0;
          min-width: 44px;
        }

        .oyla-bag-btn {
          font-size: 14px;
          height: 44px;
          display: inline-flex;
          align-items: center;
          padding: 0;
          min-width: 44px;
        }

        .oyla-burger-btn {
          width: 44px;
          height: 44px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
        }

        .burger-line {
          width: 24px;
        }

        /* Grid collapse & layout switch */
        .grid-container {
          grid-template-columns: 1fr;
        }

        .left-column {
          position: relative;
          height: auto;
          top: auto;
          padding: 48px 16px;
        }

        .right-column {
          border-left: none;
        }

        .left-middle {
          gap: 20px;
          margin-top: 24px;
          margin-bottom: 24px;
        }

        .right-card {
          padding: 40px 16px;
          min-height: auto;
        }

        /* Typography fluid scale & strict hierarchy (h1 > h2 > h3 > body-large) */
        .hero-title {
          font-size: 38px;
          line-height: 1.1;
          margin-bottom: 16px;
        }

        .heading-style-h1 {
          font-size: 34px !important;
          line-height: 1.1;
          letter-spacing: -0.5px;
        }

        .left-heading {
          font-size: 26px;
          line-height: 1.2;
        }

        .left-p,
        .detail-paragraph {
          font-size: 15px;
          line-height: 1.4;
        }

        .card-subtext {
          font-size: 11px;
          margin-top: 8px;
        }

        /* Video hero padding & layout constraints */
        .video-hero-sticky {
          padding: 32px 16px;
        }

        /* Buttons & interactive elements touch target & alignment */
        .explore-btn {
          width: 100%;
          text-align: center;
          display: block;
          padding: 14px 28px;
          min-height: 44px;
          font-size: 13px;
          letter-spacing: 0.1em;
          box-sizing: border-box;
        }

        .newsletter-btn-wrapper {
          min-height: 44px;
          padding: 6px 6px 6px 18px;
          box-sizing: border-box;
        }

        /* Awards section horizontal scrolling card proportions */
        .award-card {
          width: 85vw;
          padding: 32px 16px;
          gap: 20px;
        }

        .award-image-container {
          height: 180px !important;
        }

        .award-title {
          font-size: 14px;
          line-height: 1.3;
        }

        .award-price {
          font-size: 13px;
        }

        /* Footer 1-column collapse and spacing alignment */
        .replica-footer {
          grid-template-columns: 1fr;
          padding: 48px 16px;
          gap: 32px;
        }

        .footer-col {
          min-height: auto;
        }

        .footer-col:last-child {
          grid-column: span 1;
          margin-top: 0;
        }

        .footer-header-item {
          margin-bottom: 24px;
        }

        .footer-header-link,
        .footer-header-text,
        .footer-link,
        .newsletter-desc {
          font-size: 14px;
          line-height: 1.4;
        }

        .footer-credits {
          margin-top: 24px;
          font-size: 13px;
          line-height: 1.4;
        }

        .footer-links-list {
          gap: 8px;
        }

        .newsletter-form {
          padding: 6px 6px 6px 16px;
          width: 100%;
          max-width: 100%;
        }

        .newsletter-input {
          font-size: 13px;
        }
      }
    </style>
  </head>
  <body>

    <!-- OYLA HEADER -->
    <header class="oyla-header">
      <a href="#" class="oyla-logo" aria-label="OYLA">
        <svg width="112" height="60" viewBox="0 0 112 60" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M63.243 44.6164C62.8166 44.6164 62.6034 44.4601 62.6034 44.1475C62.6034 43.8349 62.7882 43.6644 63.1577 43.636L65.0765 43.3376C65.645 43.2524 66.0288 43.1103 66.2278 42.9114C66.4268 42.684 66.5263 42.272 66.5263 41.6752V31.6157C66.5263 30.9905 66.3841 30.3796 66.0999 29.7828L59.8319 16.6543C59.6329 16.1712 59.4055 15.8018 59.1496 15.546C58.8938 15.2903 58.5242 15.1055 58.041 14.9919L57.6572 14.9066C57.2593 14.8214 57.0603 14.6367 57.0603 14.3525C57.0603 14.0683 57.2735 13.9263 57.6999 13.9263H64.9912C65.3892 13.9263 65.5882 14.0825 65.5882 14.3951C65.5882 14.7077 65.3466 14.8782 64.8633 14.9066L64.0532 14.9919C63.5699 15.0203 63.2288 15.1766 63.0298 15.4608C62.8308 15.7449 62.8735 16.1854 63.1577 16.7821L68.4024 27.9499C68.5161 28.1488 68.6582 28.2483 68.8288 28.2483C68.9994 28.2483 69.1415 28.1488 69.2552 27.9499L74.2867 17.6773C74.6562 16.9384 74.7415 16.3417 74.5425 15.887C74.3719 15.4039 73.9598 15.1198 73.306 15.0345L72.3679 14.9066C71.8846 14.8214 71.643 14.6509 71.643 14.3951C71.643 14.0825 71.842 13.9263 72.24 13.9263H78.2948C78.7212 13.9263 78.9344 14.0683 78.9344 14.3525C78.9344 14.6367 78.7354 14.8214 78.3374 14.9066L77.911 14.9919C77.5131 15.0771 77.1577 15.3187 76.845 15.7165C76.5608 16.1143 76.177 16.7821 75.6938 17.7199L70.108 28.9303C69.909 29.3281 69.7669 29.7118 69.6816 30.0812C69.5963 30.4222 69.5537 30.82 69.5537 31.2747V41.6752C69.5537 42.272 69.6532 42.684 69.8521 42.9114C70.0796 43.1103 70.4633 43.2524 71.0034 43.3376L72.9222 43.636C73.2917 43.6644 73.4765 43.8349 73.4765 44.1475C73.4765 44.4601 73.2633 44.6164 72.8369 44.6164H63.243Z" fill="#A3111E"/>
<path d="M76.8614 44.6164C76.435 44.6164 76.2218 44.4601 76.2218 44.1475C76.2218 43.8917 76.4065 43.7212 76.7761 43.636L77.7568 43.4655C78.3537 43.3518 78.7375 43.1955 78.9081 42.9966C79.107 42.7977 79.2065 42.3999 79.2065 41.8031V16.7395C79.2065 16.1428 79.107 15.7449 78.9081 15.546C78.7375 15.3471 78.3537 15.1908 77.7568 15.0771L76.7761 14.9066C76.4065 14.8214 76.2218 14.6509 76.2218 14.3951C76.2218 14.0825 76.435 13.9263 76.8614 13.9263H84.6644C85.0908 13.9263 85.304 14.0968 85.304 14.4378C85.304 14.6935 85.1476 14.8498 84.8349 14.9066L83.6837 15.0771C83.0867 15.1624 82.6888 15.3187 82.4898 15.546C82.3192 15.7733 82.2339 16.1854 82.2339 16.7821V40.6522C82.2339 41.6752 82.5182 42.4141 83.0867 42.8687C83.6837 43.3234 84.4228 43.5507 85.304 43.5507C85.9578 43.5507 86.6258 43.4229 87.308 43.1671C88.0187 42.8829 88.6583 42.3714 89.2268 41.6326C89.7954 40.8654 90.2217 39.7571 90.506 38.3078L91.0603 35.452C91.1456 35.0825 91.3588 34.8978 91.6999 34.8978C92.0979 34.8978 92.2684 35.1394 92.2116 35.6225L91.6999 43.636C91.6431 44.2896 91.2877 44.6164 90.6339 44.6164H76.8614Z" fill="#A3111E"/>
<path d="M91.6183 44.6164C91.1919 44.6164 90.9787 44.4743 90.9787 44.1901C90.9787 43.906 91.1777 43.7212 91.5757 43.636L92.2153 43.5081C92.7838 43.3945 93.2102 43.1245 93.4944 42.6982C93.7787 42.2436 94.0203 41.6184 94.2193 40.8227L100.828 14.182C100.885 13.8978 100.971 13.7131 101.084 13.6279C101.226 13.5426 101.354 13.5 101.468 13.5C101.61 13.5 101.738 13.5426 101.852 13.6279C101.994 13.7131 102.093 13.8978 102.15 14.182L108.887 41.2064C109.086 42.002 109.314 42.5562 109.57 42.8687C109.825 43.1813 110.223 43.3945 110.763 43.5081L111.403 43.636C111.801 43.7212 112 43.906 112 44.1901C112 44.4743 111.787 44.6164 111.36 44.6164H104.069C103.671 44.6164 103.472 44.4601 103.472 44.1475C103.472 43.8349 103.714 43.6644 104.197 43.636L105.007 43.5507C105.49 43.4939 105.789 43.3376 105.903 43.0819C106.045 42.8261 106.045 42.3857 105.903 41.7605L104.282 35.1536C104.112 34.4147 103.643 34.0453 102.875 34.0453H98.398C97.6589 34.0453 97.1899 34.4147 96.9909 35.1536L95.5411 40.8654C95.1147 42.4851 95.5411 43.3802 96.8203 43.5507L97.4599 43.636C97.9432 43.7212 98.1848 43.8917 98.1848 44.1475C98.1848 44.4601 97.9858 44.6164 97.5878 44.6164H91.6183ZM98.2701 32.7666H102.96C103.415 32.7666 103.6 32.525 103.515 32.0419L100.786 20.6184H100.573L97.7158 32.0419C97.6305 32.525 97.8152 32.7666 98.2701 32.7666Z" fill="#A3111E"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M29.8667 0C46.3616 0 59.7334 13.4315 59.7334 30C59.7334 46.5685 46.3616 60 29.8667 60C13.3718 60 0 46.5685 0 30C0 13.4315 13.3718 0 29.8667 0ZM29.8653 6.45117C14.2574 6.45146 1.60563 16.9948 1.60563 30C1.60582 43.0051 14.2576 53.5485 29.8653 53.5488C45.4732 53.5488 58.1261 43.0053 58.1263 30C58.1263 16.9946 45.4734 6.45117 29.8653 6.45117Z" fill="#A3111E"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M59.7334 30C59.7334 39.1127 54.0504 46.5 47.0401 46.5C40.0297 46.5 29.8667 39.1939 29.8667 30.0812C29.8667 20.9685 40.0297 13.5 47.0401 13.5C54.0504 13.5 59.7334 20.8873 59.7334 30ZM57.0049 29.9971C57.0049 21.3744 52.5442 14.3835 47.0415 14.3833C41.5388 14.3833 37.0782 21.3743 37.0782 29.9971C37.0784 38.6196 41.5389 45.6094 47.0415 45.6094C52.544 45.6092 57.0047 38.6194 57.0049 29.9971Z" fill="#A3111E"/>
        </svg>
      </a>
      <div class="oyla-header-nav">
        <a href="#" class="oyla-about-link">ABOUT</a>
        <div class="oyla-cart-menu">
          <button class="oyla-burger-btn" aria-label="Menu">
            <span class="burger-line"></span>
            <span class="burger-line"></span>
          </button>
          <button class="oyla-bag-btn">
            [ BAG ]
          </button>
        </div>
      </div>
    </header>

    <!-- SCROLL-DRIVEN VIDEO HERO -->
    <div class="scroll-video-container">
      <div class="video-hero-sticky">
        <video id="scroll-video" playsinline muted preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260627_212146_743b92b3-40a3-46cb-988d-7bf716564ec3.mp4"></video>
        <div class="video-overlay"></div>
        
        <div class="hero-content">
          <h1 class="hero-title">
            <span class="hero-title-line">
              <span class="hero-title-line-inner">MEASURED</span>
            </span>
            <span class="hero-title-line">
              <span class="hero-title-line-inner">PURITY</span>
            </span>
          </h1>
          <button id="hero-confirm-btn" class="newsletter-btn-wrapper" style="margin-left: 0; margin-top: 10px;" onclick="document.querySelector('.replica-footer').scrollIntoView({ behavior: 'smooth' })">
            <span class="newsletter-btn-text">DISCOVER</span>
            <div class="newsletter-btn-circle">+</div>
          </button>
        </div>
      </div>
    </div>

    <!-- AWARDS AND CARDS SECTION -->
    <section class="awards-section">
      <div class="awards-grid">
        <!-- CARD 1 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144408_92b74dc4-ca69-412a-acfd-304f9b29eb5e_min.webp" alt="Obsidian Coil" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Obsidian Coil</h3>
            <span class="award-price">$480</span>
          </div>
        </div>

        <!-- CARD 2 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_145142_ed02063b-d983-47d2-b60b-4b4a5a3448bd_min.webp" alt="Void Arc" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Void Arc</h3>
            <span class="award-price">$560</span>
          </div>
        </div>

        <!-- CARD 3 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144747_f21bc119-e460-45be-a071-851291bd71c5_min.webp" alt="Onyx Hex" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Onyx Hex</h3>
            <span class="award-price">$620</span>
          </div>
        </div>

        <!-- CARD 4 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260627_215521_100b78bd-d24a-4225-b2e8-5bb30d44af73_min.webp" alt="Shadow Sigil" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Shadow Sigil</h3>
            <span class="award-price">$740</span>
          </div>
        </div>

        <!-- CARD 5 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_144408_92b74dc4-ca69-412a-acfd-304f9b29eb5e_min.webp" alt="Eclipse Band" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Eclipse Band</h3>
            <span class="award-price">$820</span>
          </div>
        </div>

        <!-- CARD 6 -->
        <div class="award-card">
          <div class="award-image-container">
            <img src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_145142_ed02063b-d983-47d2-b60b-4b4a5a3448bd_min.webp" alt="Matte Skull" class="award-img" />
          </div>
          <div class="award-text-container">
            <h3 class="award-title">Matte Skull</h3>
            <span class="award-price">$950</span>
          </div>
        </div>
      </div>

      <!-- VIDEO CLIP REVEAL CONTAINER (Clipping Frame inside Pinned Section) -->
      <div class="video-scaling-wrapper">
        <video id="scroll-video-second" playsinline muted preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260628_122130_8b16d300-75cb-49f5-82ce-afd6b79c2d79.mp4"></video>
      </div>

    </section>

    <!-- MAIN OPPORTUNITY SECTION -->
    <section class="outer-section">
      <div class="grid-container">
        
        <!-- LEFT COLUMN -->
        <div class="left-column">
          <!-- Top -->
          <h2 class="left-heading" data-fade-slide-in>Made Without Compromise</h2>
          
          <!-- Middle -->
          <div class="left-middle">
            <p class="left-p" data-fade-slide-in>Each ring is forged by a single pair of hands — no factory floor, no assembly line. The material is chosen first; the form follows its nature.</p>
            <p class="left-p" data-fade-slide-in>We work in oxidized silver, blackened bronze, and raw brass. Weights are deliberate. Edges are left where they fall. Nothing is smoothed for comfort.</p>
            <p class="left-p" data-fade-slide-in>OYLA exists for those who wear jewelry that means something. Not decoration — declaration. One piece at a time, made to last a lifetime.</p>
          </div>
          
          <!-- Bottom -->
          <div class="left-bottom" data-fade-slide-in>
            <button class="newsletter-btn-wrapper" style="margin-left: 0;">
              <span class="newsletter-btn-text">VIEW COLLECTION</span>
              <div class="newsletter-btn-circle">+</div>
            </button>
          </div>
        </div>
        
        <!-- RIGHT COLUMN -->
        <div class="right-column">
          
          <!-- CARD 1 -->
          <div class="right-card">
            <div class="stomp-wrapper">
              <div class="stomp-stack stack-a">
                <h1 class="heading-style-h1">100%</h1>
                <h1 class="heading-style-h1">100%</h1>
              </div>
              <div class="stomp-stack stack-b">
                <h1 class="heading-style-h1">Handmade</h1>
                <h1 class="heading-style-h1">Handmade</h1>
              </div>
            </div>
            <p class="detail-paragraph">Every ring crafted by a single artisan, start to finish</p>
          </div>

          <!-- CARD 2 -->
          <div class="right-card">
            <div class="stomp-wrapper">
              <div class="stomp-stack stack-a">
                <h1 class="heading-style-h1">14–92g</h1>
                <h1 class="heading-style-h1">14–92g</h1>
              </div>
              <div class="stomp-stack stack-b">
                <h1 class="heading-style-h1">Per piece</h1>
                <h1 class="heading-style-h1">Per piece</h1>
              </div>
            </div>
            <p class="detail-paragraph">Deliberate weight — each ring is a physical presence you feel</p>
          </div>

          <!-- CARD 3 -->
          <div class="right-card">
            <div class="stomp-wrapper">
              <div class="stomp-stack stack-a">
                <h1 class="heading-style-h1">Sterling</h1>
                <h1 class="heading-style-h1">Sterling</h1>
              </div>
              <div class="stomp-stack stack-b">
                <h1 class="heading-style-h1">& Silver</h1>
                <h1 class="heading-style-h1">& Silver</h1>
              </div>
            </div>
            <p class="detail-paragraph">Oxidized metals only — no plating, no compromise</p>
          </div>

          <!-- CARD 4 -->
          <div class="right-card">
            <div class="stomp-wrapper">
              <div class="stomp-stack stack-a">
                <h1 class="heading-style-h1">Lifetime</h1>
                <h1 class="heading-style-h1">Lifetime</h1>
              </div>
              <div class="stomp-stack stack-b">
                <h1 class="heading-style-h1">Guarantee</h1>
                <h1 class="heading-style-h1">Guarantee</h1>
              </div>
            </div>
            <p class="detail-paragraph">We stand behind every piece we make, forever</p>
            <p class="card-subtext">Est. OYLA Studio, 2019.</p>
          </div>
          
        </div>
      </div>
    </section>

    <!-- Spacer for the fixed/revealed footer -->
    <div class="footer-spacer" style="pointer-events: none; background: transparent; width: 100%;"></div>

    <!-- REPLICA FOOTER SECTION -->
    <footer class="replica-footer">
      <!-- COLUMN 1: Sign in & Credits -->
      <div class="footer-col">
        <div class="footer-header-item">
          <a href="#" class="footer-header-link">Sign in</a>
        </div>

        <div class="footer-content-item">
          <div class="footer-credits">
            <p>Handcrafted in small batches</p>
            <p>OYLA Studio</p>
            <br>
            <p>Based in Berlin</p>
            <p>© OYLA 2026</p>
            <p>All pieces are original designs.</p>
          </div>
        </div>
      </div>

      <!-- COLUMN 2: Links -->
      <div class="footer-col">
        <div class="footer-header-item">
          <a href="#" class="footer-header-link">Instagram</a>
        </div>

        <div class="footer-content-item">
          <div class="footer-links-list">
            <a href="#" class="footer-link">Refund Policy</a>
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">Terms of Service</a>
          </div>
        </div>
      </div>

      <!-- COLUMN 3: Newsletter -->
      <div class="footer-col">
        <div class="footer-header-item">
          <h3 class="footer-header-text">Newsletter</h3>
        </div>

        <div class="footer-content-item">
          <p class="newsletter-desc">Join our list. Be first to know new drops. 10% off your first order.</p>

          <form class="newsletter-form" onsubmit="event.preventDefault(); alert('You\'re on the list. Welcome.');">
            <input type="email" class="newsletter-input" placeholder="Email" required />
            <button type="submit" class="newsletter-btn-wrapper">
              <span class="newsletter-btn-text">SUBSCRIBE</span>
              <div class="newsletter-btn-circle">+</div>
            </button>
          </form>
        </div>
      </div>
    </footer>

    <!-- GSAP + ScrollTrigger Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>

    <!-- Dynamic Layout & Animation Script -->
    <script>
      // Register ScrollTrigger with GSAP
      gsap.registerPlugin(ScrollTrigger);

      // Smooth Video Scroll Scrubbing Logic
      const videoContainer = document.querySelector('.scroll-video-container');
      const video = document.getElementById('scroll-video');
      const videoIndicator = document.getElementById('video-scroll-indicator');

      if (video && videoContainer) {
        // Keep video paused
        video.pause();

        // Dynamically fetch the freshest direct video URL from server
        fetch("/api/higgsfield-video")
          .then(res => res.json())
          .then(data => {
            if (data && data.success && data.url) {
              console.log("Dynamically loaded video URL from Higgsfield:", data.url);
              // Resolve relative/absolute differences to prevent redundant reloads
              const absoluteTarget = new URL(data.url, window.location.href).href;
              const absoluteCurrent = video.src ? new URL(video.src, window.location.href).href : "";
              
              if (absoluteTarget !== absoluteCurrent) {
                const wasCurrentTime = video.currentTime;
                video.src = data.url;
                video.load();
                video.currentTime = wasCurrentTime;
              }
            }
          })
          .catch(err => {
            console.warn("Failed to dynamically fetch video URL, using robust fallback CDN source.", err);
          });

        let targetTime = 0;
        let currentTime = 0;

        function scrubVideo() {
          const rect = videoContainer.getBoundingClientRect();
          const totalHeight = videoContainer.offsetHeight - window.innerHeight;
          const scrolled = -rect.top;

          let progress = scrolled / totalHeight;
          progress = Math.max(0, Math.min(1, progress));

          // Only calculate if metadata is loaded (readyState >= 1)
          if (video.readyState >= 1 && video.duration) {
            // Keep a tiny margin at the end of the video to avoid looping/stalling issues
            const safeDuration = video.duration - 0.05;
            targetTime = progress * safeDuration;
            targetTime = Math.max(0, Math.min(safeDuration, targetTime));

            // Smoothly interpolate video.currentTime for a luxury cinematic experience
            currentTime += (targetTime - currentTime) * 0.08;
            
            if (Math.abs(currentTime - targetTime) < 0.01) {
              currentTime = targetTime;
            }
            
            // CRITICAL PERFORMANCE GUARD: 
            // Avoid setting currentTime if the video is already busy seeking or the change is negligible.
            // This prevents the browser decoder from being flooded with requests, which causes freezing and black screens.
            if (!video.seeking && Math.abs(video.currentTime - currentTime) > 0.01) {
              video.currentTime = currentTime;
            }
          }

          // Fade out scroll indicator after 10% progress
          if (videoIndicator) {
            if (progress > 0.1) {
              videoIndicator.style.opacity = '0';
              videoIndicator.style.pointerEvents = 'none';
            } else {
              videoIndicator.style.opacity = (1 - (progress / 0.1)).toString();
              videoIndicator.style.pointerEvents = 'auto';
            }
          }

          // Smooth scroll-synchronized transition for Hero Title lines and Button once video progress is >= 80% (progress >= 0.8)
          const titleInners = document.querySelectorAll('.hero-title-line-inner');
          const confirmBtn = document.getElementById('hero-confirm-btn');
          
          let animProgress = 0;
          if (progress >= 0.8) {
            animProgress = (progress - 0.8) / 0.2; // Map 0.8 -> 1.0 range to 0.0 -> 1.0 range
          }
          
          const heroChars = document.querySelectorAll('.hero-char');
          const totalChars = heroChars.length;
          heroChars.forEach((char, i) => {
            const charStart = (i / Math.max(totalChars - 1, 1)) * 0.6;
            let p = (animProgress - charStart) / 0.4;
            p = Math.max(0, Math.min(1, p));
            const eased = p * p * p;
            char.style.opacity = (1 - eased).toString();
            char.style.transform = `translate3d(0, ${-28 * eased}px, 0)`;
            char.style.filter = `blur(${9 * eased}px)`;
          });
          
          if (confirmBtn) {
            // Button fades out and shifts up
            const btnEased = Math.pow(animProgress, 4);
            confirmBtn.style.transform = `translate3d(0, ${-25 * btnEased}px, 0)`;
            confirmBtn.style.opacity = (1 - animProgress).toString();
            if (animProgress >= 0.95) {
              confirmBtn.style.pointerEvents = 'none';
            } else {
              confirmBtn.style.pointerEvents = 'auto';
            }
          }

          requestAnimationFrame(scrubVideo);
        }

        // Start scrubbing loop
        requestAnimationFrame(scrubVideo);

        // Scroll event for instant indicator fade response
        window.addEventListener('scroll', () => {
          const rect = videoContainer.getBoundingClientRect();
          const totalHeight = videoContainer.offsetHeight - window.innerHeight;
          const scrolled = -rect.top;
          let progress = scrolled / totalHeight;
          progress = Math.max(0, Math.min(1, progress));
          
          if (videoIndicator) {
            if (progress > 0.1) {
              videoIndicator.style.opacity = '0';
            } else {
              videoIndicator.style.opacity = (1 - (progress / 0.1)).toString();
            }
          }
        }, { passive: true });
      }

      // Smooth Video Scroll Scrubbing Logic for Second Video
      const secondVideo = document.getElementById('scroll-video-second');

      if (secondVideo) {
        // Keep video paused
        secondVideo.pause();

        // Dynamically fetch the freshest direct video URL from server
        fetch("/api/higgsfield-video?url=https://higgsfield.ai/s/iK6bYyCxd0I")
          .then(res => res.json())
          .then(data => {
            if (data && data.success && data.url) {
              console.log("Dynamically loaded second video URL from Higgsfield:", data.url);
              const absoluteTarget = new URL(data.url, window.location.href).href;
              const absoluteCurrent = secondVideo.src ? new URL(secondVideo.src, window.location.href).href : "";
              
              if (absoluteTarget !== absoluteCurrent) {
                const wasCurrentTime = secondVideo.currentTime;
                secondVideo.src = data.url;
                secondVideo.load();
                secondVideo.currentTime = wasCurrentTime;
              }
            }
          })
          .catch(err => {
            console.warn("Failed to dynamically fetch second video URL, using robust fallback.", err);
          });
      }

      // Shared variables for smooth second video scrubbing driven by GSAP timeline
      let targetTimeSecond = 0;
      let currentTimeSecond = 0;

      function smoothScrubSecond() {
        const secondVideo = document.getElementById('scroll-video-second');
        if (secondVideo && secondVideo.readyState >= 1 && secondVideo.duration) {
          // Smoothly interpolate secondVideo.currentTime
          currentTimeSecond += (targetTimeSecond - currentTimeSecond) * 0.08;
          
          if (Math.abs(currentTimeSecond - targetTimeSecond) < 0.01) {
            currentTimeSecond = targetTimeSecond;
          }
          
          if (!secondVideo.seeking && Math.abs(secondVideo.currentTime - currentTimeSecond) > 0.01) {
            secondVideo.currentTime = currentTimeSecond;
          }
        }
        requestAnimationFrame(smoothScrubSecond);
      }
      requestAnimationFrame(smoothScrubSecond);

      // Track ScrollTriggers to easily clear/rebuild on resize
      let activeTriggers = [];

      function initStompAnimations() {
        // Ensure char/word splits exist before any animation setup
        initTextSplits();

        // Natively kill ALL existing ScrollTrigger instances on the page.
        // This is 100% robust and automatically cleans up all pinning spacers, resets layout,
        // and restores elements to their original state before we rebuild.
        ScrollTrigger.getAll().forEach(t => {
          if (t && typeof t.kill === 'function') {
            t.kill(true);
          }
        });
        activeTriggers = [];

        // Kill active GSAP animations on target elements to prevent conflicts
        gsap.killTweensOf(".heading-style-h1, .stomp-stack, .detail-paragraph, .card-subtext, [data-fade-slide-in], .awards-grid, .video-scaling-wrapper, #scroll-video-second, .hero-char, .stat-char, .detail-word");

        // Reset all animated elements to a clean state
        document.querySelectorAll('.heading-style-h1, .detail-paragraph, .card-subtext, [data-fade-slide-in], .awards-grid, .video-scaling-wrapper, #scroll-video-second').forEach(el => {
          gsap.set(el, { clearProps: "all" });
        });
        document.querySelectorAll('.hero-char, .stat-char, .detail-word').forEach(el => {
          el.style.opacity = '';
          el.style.transform = '';
          el.style.filter = '';
        });
        document.querySelectorAll('.stomp-stack').forEach(s => {
          s.style.overflow = '';
          s.style.height = '';
        });

        // 4. LEFT PANEL FADE & SLIDE-IN ANIMATIONS
        // Only run on desktop screens >= 768px
        if (window.innerWidth >= 768) {
          const fadeAnim = gsap.fromTo("[data-fade-slide-in]", 
            { autoAlpha: 0, y: 20 },
            {
              autoAlpha: 1,
              y: 0,
              stagger: 0.15,
              duration: 0.8,
              ease: "power2.out",
              scrollTrigger: {
                trigger: ".outer-section",
                start: "top 80%",
                toggleActions: "play none none reverse"
              }
            }
          );
          if (fadeAnim.scrollTrigger) {
            activeTriggers.push(fadeAnim.scrollTrigger);
          }
        } else {
          // Clean up fade-slide-in properties for smaller screens so elements are fully visible
          gsap.set("[data-fade-slide-in]", { clearProps: "all" });
        }

        // 5. HORIZONTAL AWARDS SCROLL ON VERTICAL SCROLL & VIDEO REVEAL
        const section = document.querySelector('.awards-section');
        const grid = document.querySelector('.awards-grid');
        const videoScalingWrapper = document.querySelector('.video-scaling-wrapper');
        const secondVideo = document.getElementById('scroll-video-second');

        if (section && grid) {
          gsap.set(grid, { clearProps: "transform" }); // Reset inline transform
          if (videoScalingWrapper) {
            gsap.set(videoScalingWrapper, { clearProps: "all" });
          }
          if (secondVideo) {
            gsap.set(secondVideo, { clearProps: "all" });
          }
          
          const scrollDistance = () => Math.max(0, grid.scrollWidth - window.innerWidth);
          const totalDuration = () => scrollDistance() + window.innerHeight * 1.5;
          
          const carouselTl = gsap.timeline({
            scrollTrigger: {
              trigger: section,
              pin: true,
              start: "top top",
              end: () => `+=${totalDuration()}`,
              scrub: true,
              invalidateOnRefresh: true,
              onUpdate: (self) => {
                // Symmetrical smooth second video scrubbing driven by GSAP timeline progress
                if (secondVideo && secondVideo.duration) {
                  const d1 = scrollDistance();
                  const dTot = totalDuration();
                  let progressSecond = 0;
                  if (dTot > 0) {
                    const startProgress = d1 / dTot;
                    if (self.progress >= startProgress) {
                      progressSecond = (self.progress - startProgress) / (1 - startProgress);
                    }
                  }
                  progressSecond = Math.max(0, Math.min(1, progressSecond));
                  
                  const safeDuration = secondVideo.duration - 0.05;
                  targetTimeSecond = progressSecond * safeDuration;
                  targetTimeSecond = Math.max(0, Math.min(safeDuration, targetTimeSecond));
                }
              }
            }
          });
          
          // Phase 1: Horizontal scroll of the awards grid
          carouselTl.to(grid, {
            x: () => -scrollDistance(),
            ease: "none",
            duration: () => scrollDistance()
          });
          
          // Phase 2: Symmetrically expand the video container from the center (0% to 100%)
          if (videoScalingWrapper) {
            carouselTl.fromTo(videoScalingWrapper, {
              width: "0%"
            }, {
              width: "100%",
              ease: "none",
              duration: () => window.innerHeight * 1.5
            });
          }
          
          if (carouselTl.scrollTrigger) {
            activeTriggers.push(carouselTl.scrollTrigger);
          }
        }

        // 6. DYNAMIC FOOTER REVEAL SPACING
        const footer = document.querySelector('.replica-footer');
        const spacer = document.querySelector('.footer-spacer');
        if (footer && spacer) {
          // Set spacer height to match footer height
          spacer.style.height = `${footer.offsetHeight}px`;
        }
      }

      // Use fonts.ready (not window.load) — fires before user can scroll to the stats section.
      // window.load waits for Higgsfield CDN videos which load slowly; by then the user
      // may already be past the section and the exit scrub would snap mid-progress, hiding text.
      document.fonts.ready.then(() => {
        initStompAnimations();
      });

      // Handle viewport resizing with a debounced wrapper to prevent thrashing
      let lastWidth = window.innerWidth;
      let resizeTimeout;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
          // Always keep the spacer height in sync on resize
          const footer = document.querySelector('.replica-footer');
          const spacer = document.querySelector('.footer-spacer');
          if (footer && spacer) {
            spacer.style.height = `${footer.offsetHeight}px`;
          }

          const currentWidth = window.innerWidth;
          if (currentWidth !== lastWidth) {
            lastWidth = currentWidth;
            initStompAnimations();
          } else {
            // Only update positions/calculations if width didn't change (prevents breaking on mobile address bar scroll toggle)
            ScrollTrigger.refresh();
          }
        }, 200);
      });

      function initTextSplits() {
        document.querySelectorAll('.hero-title-line-inner').forEach(el => {
          if (el.dataset.split) return;
          el.dataset.split = 'true';
          el.innerHTML = el.textContent.split('').map(c =>
            c === ' '
              ? '<span class="hero-char" style="display:inline-block;white-space:pre"> </span>'
              : `<span class="hero-char" style="display:inline-block">${c}</span>`
          ).join('');
        });

        document.querySelectorAll('.right-card .heading-style-h1:last-child').forEach(el => {
          if (el.dataset.split) return;
          el.dataset.split = 'true';
          el.innerHTML = el.textContent.split('').map(c =>
            c === ' '
              ? '<span class="stat-char" style="display:inline-block;white-space:pre"> </span>'
              : `<span class="stat-char" style="display:inline-block">${c}</span>`
          ).join('');
        });

        document.querySelectorAll('.right-card .detail-paragraph').forEach(el => {
          if (el.dataset.split) return;
          el.dataset.split = 'true';
          el.innerHTML = el.textContent.trim().split(/(\s+)/).map(w =>
            w.trim() === '' ? w
              : `<span class="detail-word" style="display:inline-block">${w}</span>`
          ).join('');
        });
      }
      document.addEventListener('DOMContentLoaded', initTextSplits);
    </script>
  </body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Clarity Core"
template_id: "4fb39da5-9997-4469-aa68-ec6ee2bb0771"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Clarity Core

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `4fb39da5-9997-4469-aa68-ec6ee2bb0771`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Clarity Core](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/57f59485-2638-4924-ac7e-a3e3bb677d3e.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Build a premium single-page landing site for "LumiDerm" — a luxury skincare/biotech brand. Use React + TypeScript + Vite + Tailwind CSS. Use lucide-react for icons. Use the font "Helvetica Now Text" loaded from this CDN:
https://db.onlinewebfonts.com/c/08e020de1811ec4489f82d1247a42c09?family=Helvetica+Now+Text

Set the page title to "LumiDerm | Advanced Skin Science".

The site has 3 components: SplashScreen, Navbar, and HeroSection. The entire page is fixed/fullscreen with overflow hidden, no scrollbar. Black background base.

---

### SECTION 1: Splash Screen (SplashScreen.tsx)

A loading intro that plays on first load:
- Full-screen overlay at z-[9999], bg-[#010101].
- Shows a progress bar at the bottom (px-12, bottom-12). Left label says "Loading" in white/40, uppercase, tracking-[0.2em], xs text. Right shows the percentage in white, sm, tabular-nums font-medium.
- The progress bar is 1px tall, bg-white/10 track, with a white fill that animates from 0% to 100% over 2400ms (20ms interval steps).
- Once 100% is reached, wait 300ms, then trigger a "curtain reveal" animation:
  - Two panels (left half and right half) slide apart: left translates -100% X, right translates +100% X.
  - Duration: 1200ms, easing: cubic-bezier(0.76, 0, 0.24, 1).
  - The loader content fades to opacity-0 with duration-300 during reveal.
- After 1200ms of the curtain animation, call onComplete to signal the main content can appear.

---

### SECTION 2: Navbar (Navbar.tsx)

A floating pill-shaped navbar, fixed at the top center:
- Position: fixed top-4 (sm:top-6), centered, z-50, px-4 on the wrapper.
- Nav pill: bg-white/10, backdrop-blur-md, border border-white/15, rounded-full, px-2 py-2.
- On mobile: full-width with justify-between. On sm+: auto width.
- Appears with a transition: opacity and translateY(-4 to 0) over 700ms with 300ms delay, triggered by `isActive` prop.

Contents:
- Logo: text-base font-medium tracking-tight. "Lumi" in font-bold, "Derm" in font-light. Both white.
- Desktop nav links (hidden md:flex): "Science", "Treatments", "Results", "Testimonials", "Connect". Each: text-white/80, text-sm, hover:text-white, hover:bg-white/10, px-4 py-1.5, rounded-full.
- CTA button (hidden sm:flex): "Book Now" with ArrowRight icon. bg-[#5794E2], text-white text-sm, px-5 py-2, rounded-full, hover:bg-[#4a84d0].
- Mobile hamburger (md:hidden): w-9 h-9 rounded-full bg-white/10, toggles between Menu and X icons.
- Mobile overlay: fixed inset-0 z-40, bg-black/90 backdrop-blur-lg. Shows the same 5 links as text-2xl font-light centered vertically with gap-6, plus the "Book Now" button. Transitions opacity over 300ms.

---

### SECTION 3: Hero Section (HeroSection.tsx)

A fullscreen video background hero with scroll-driven crossfade between two states.

**Video backgrounds:** (not looping, plays once then pause)
- Video 1 URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260619_222559_363e35af-d0bc-4650-b3cb-58bf833daa51.mp4`
- Video 2 URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260619_232048_98292efb-9b9c-4089-a587-72f33437c8f8.mp4`
- Both: absolute inset-0, w-full h-full, object-cover, muted, playsInline, preload="auto".
- Video 1 opacity = 1 - progress. Video 2 opacity = progress.


**Scroll-driven progress (0 to 1):**
- Listen to wheel events (passive: false, preventDefault).
- Delta = e.deltaY / 800. Clamp progress between 0 and 1.
- When progress crosses 0.5 threshold, pause one video and play the other from the start.
- Video 1 plays when progress < 0.5. Video 2 plays when progress >= 0.5.

**Hero State 1 (progress near 0) — Bottom Left content:**
- Opacity: max(0, 1 - progress * 2.5). TranslateY: progress * 30px.
- Position: absolute bottom-12 left-6 right-6, sm:bottom-8 sm:left-8 sm:right-auto, md:bottom-16 md:left-12. max-w-2xl.
- H1: "The Future of\nSkin Regeneration". text-3xl sm:text-4xl md:text-6xl lg:text-7xl, font-light, leading-[1.05], tracking-tight, mb-4 md:mb-6.
- P: "Heal with science, not guesswork. LumiDerm merges cellular research and bioactive formulations to unlock your skin's true radiant potential." text-xs sm:text-sm md:text-base, text-white/70, max-w-md, mb-6 md:mb-8.
- Button: "Explore Now". bg-[#5794E2], rounded-full, text-xs sm:text-sm, px-6 sm:px-8, py-3 sm:py-3.5.

**Hero State 1 — White Card (bottom right, hidden on mobile):**
- hidden sm:flex. Position: absolute bottom-8 right-8 md:bottom-16 md:right-12.
- bg-white rounded-2xl p-4 md:p-5, items-center gap-4 md:gap-5, shadow-2xl, max-w-[380px] md:max-w-[460px].
- Same opacity/transform as Hero 1 content.
- Left: thumbnail image (w-20 h-20 md:w-24 md:h-24, rounded-xl, object-cover). URL: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260619_220258_2f77857f-c799-4cce-9818-442542b98f2a.png&w=1280&q=85`
- Right: "LumiDerm" and "BioActive" (text-sm font-medium, text-[#010101]), with a blue circle button (w-9 h-9, bg-[#3b82f6]) containing ArrowRight icon. Below: "CellBoost(TM) 3.0" in text-[#666] text-xs.

**Hero State 2 (progress near 1) — Bottom Center content:**
- Opacity: max(0, (progress - 0.4) * 2.5). TranslateY: max(0, (1 - progress) * 30)px.
- Position: absolute bottom-12 sm:bottom-12 md:bottom-20, left-0 right-0, centered, px-6.
- H2: "Clinically Advanced\nSkin Science". text-2xl sm:text-3xl md:text-5xl lg:text-6xl, font-light, leading-[1.1], tracking-tight, mb-4 md:mb-5.
- P: "Our patented peptide complex penetrates at the cellular level, stimulating natural collagen and restoring youthful elasticity." text-xs sm:text-sm md:text-base, text-white/70, max-w-lg.

**Hero State 2 — Stats (mobile: horizontal below text, desktop: right side vertical):**

Mobile (flex sm:hidden, mt-6, gap-6, horizontal):
- "8M+" / "Skin Transformed"
- "96.4%" / "Visible Renewal"  
- "37" / "Patents Granted"
- Numbers: text-xl font-light. Labels: text-[10px] text-white/50. Dividers: w-[1px] h-8 bg-[#5794E2]/40.

Desktop (hidden sm:flex, absolute right-8 md:right-12, top-1/2, vertical, gap-8):
- Same 3 stats. Numbers: text-3xl md:text-4xl font-light. Labels: text-xs md:text-sm, text-white/50.
- Blue separator lines: w-12 h-[1px] bg-[#5794E2]/60, mt-4 after first two.
- Transform: translateY(calc(-50% + hero2TranslateY px)).

---

### App.tsx

- State: splashComplete (boolean, starts false).
- Renders SplashScreen (only when not complete), Navbar, and HeroSection.
- Both Navbar and HeroSection receive `isActive={splashComplete}`.

### Global CSS (index.css)

- Tailwind directives (@tailwind base/components/utilities).
- Global reset: * { margin:0; padding:0; box-sizing:border-box }
- html, body, #root: width/height 100%, overflow hidden, font-family: 'Helvetica Now Text', Helvetica, Arial, sans-serif.

### Tailwind Config

- Extend fontFamily with: helvetica: ['"Helvetica Now Text"', 'Helvetica', 'Arial', 'sans-serif']

Make everything fully mobile responsive. The site should feel like an Apple-level luxury product page with smooth animations and premium typography.
```

SOUCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LumiDerm | Advanced Skin Science</title>
  <link href="https://db.onlinewebfonts.com/c/08e020de1811ec4489f82d1247a42c09?family=Helvetica+Now+Text" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            helvetica: ['"Helvetica Now Text"', 'Helvetica', 'Arial', 'sans-serif'],
          },
        },
      },
    };
  </script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; overflow: hidden; font-family: 'Helvetica Now Text', Helvetica, Arial, sans-serif; }
  </style>
</head>
<body>

<!-- Splash Screen -->
<div id="splash" class="fixed inset-0 z-[9999] flex items-center justify-center">
  <div id="curtain-left" class="absolute top-0 left-0 w-1/2 h-full bg-[#010101] transition-transform duration-[1200ms] ease-[cubic-bezier(0.76,0,0.24,1)]" style="transform: translateX(0)"></div>
  <div id="curtain-right" class="absolute top-0 right-0 w-1/2 h-full bg-[#010101] transition-transform duration-[1200ms] ease-[cubic-bezier(0.76,0,0.24,1)]" style="transform: translateX(0)"></div>
  <div id="loader-content" class="absolute bottom-12 left-0 right-0 px-12 transition-opacity duration-300 opacity-100">
    <div class="flex items-center justify-between mb-3">
      <span class="text-white/40 text-xs tracking-[0.2em] uppercase font-helvetica">Loading</span>
      <span id="progress-text" class="text-white text-sm font-helvetica tabular-nums font-medium">0%</span>
    </div>
    <div class="w-full h-[1px] bg-white/10 relative overflow-hidden">
      <div id="progress-bar" class="absolute top-0 left-0 h-full bg-white transition-all duration-100 ease-linear" style="width: 0%"></div>
    </div>
  </div>
</div>

<!-- Navbar -->
<div id="navbar-wrapper" class="fixed top-4 sm:top-6 left-0 right-0 z-50 flex justify-center px-4 transition-all duration-700 delay-300 opacity-0 -translate-y-4 pointer-events-none">
  <nav class="flex items-center gap-1 bg-white/10 backdrop-blur-md border border-white/15 rounded-full px-2 py-2 w-full sm:w-auto justify-between sm:justify-start">
    <div class="text-white text-base font-medium tracking-tight font-helvetica px-3 sm:px-4">
      <span class="font-bold">Lumi</span><span class="font-light">Derm</span>
    </div>
    <div class="hidden md:flex items-center gap-1">
      <a href="#" class="text-white/80 text-sm hover:text-white hover:bg-white/10 transition-all px-4 py-1.5 rounded-full font-helvetica">Science</a>
      <a href="#" class="text-white/80 text-sm hover:text-white hover:bg-white/10 transition-all px-4 py-1.5 rounded-full font-helvetica">Treatments</a>
      <a href="#" class="text-white/80 text-sm hover:text-white hover:bg-white/10 transition-all px-4 py-1.5 rounded-full font-helvetica">Results</a>
      <a href="#" class="text-white/80 text-sm hover:text-white hover:bg-white/10 transition-all px-4 py-1.5 rounded-full font-helvetica">Testimonials</a>
      <a href="#" class="text-white/80 text-sm hover:text-white hover:bg-white/10 transition-all px-4 py-1.5 rounded-full font-helvetica">Connect</a>
    </div>
    <button class="hidden sm:flex items-center gap-2 bg-[#5794E2] text-white text-sm px-5 py-2 rounded-full hover:bg-[#4a84d0] transition-all font-helvetica ml-2">
      Book Now
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
    </button>
    <button id="mobile-menu-btn" class="md:hidden flex items-center justify-center w-9 h-9 rounded-full bg-white/10 text-white">
      <svg id="menu-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
      <svg id="close-icon" class="hidden" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
    </button>
  </nav>
</div>

<!-- Mobile Menu Overlay -->
<div id="mobile-overlay" class="fixed inset-0 z-40 bg-black/90 backdrop-blur-lg md:hidden flex flex-col items-center justify-center gap-6 transition-all duration-300 opacity-0 pointer-events-none">
  <a href="#" class="mobile-link text-white text-2xl font-light font-helvetica hover:text-white/70 transition-colors">Science</a>
  <a href="#" class="mobile-link text-white text-2xl font-light font-helvetica hover:text-white/70 transition-colors">Treatments</a>
  <a href="#" class="mobile-link text-white text-2xl font-light font-helvetica hover:text-white/70 transition-colors">Results</a>
  <a href="#" class="mobile-link text-white text-2xl font-light font-helvetica hover:text-white/70 transition-colors">Testimonials</a>
  <a href="#" class="mobile-link text-white text-2xl font-light font-helvetica hover:text-white/70 transition-colors">Connect</a>
  <button class="flex items-center gap-2 bg-[#5794E2] text-white text-sm px-6 py-3 rounded-full hover:bg-[#4a84d0] transition-all font-helvetica mt-4">
    Book Now
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
  </button>
</div>

<!-- Hero Section -->
<div class="fixed inset-0 w-full h-full overflow-hidden bg-black">
  <video id="video1" class="absolute inset-0 w-full h-full object-cover" muted playsinline preload="auto">
    <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260619_222559_363e35af-d0bc-4650-b3cb-58bf833daa51.mp4" type="video/mp4" />
  </video>
  <video id="video2" class="absolute inset-0 w-full h-full object-cover" muted playsinline preload="auto">
    <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260619_232048_98292efb-9b9c-4089-a587-72f33437c8f8.mp4" type="video/mp4" />
  </video>
  <div class="absolute inset-0 bg-black/20"></div>

  <!-- Hero 1 Content - Bottom Left -->
  <div id="hero1-content" class="absolute bottom-12 left-6 right-6 sm:bottom-8 sm:left-8 sm:right-auto md:bottom-16 md:left-12 z-10 max-w-2xl" style="opacity:0; transform:translateY(32px); transition:all 0.7s ease;">
    <h1 class="text-white text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-light leading-[1.05] tracking-tight font-helvetica mb-4 md:mb-6">
      The Future of<br/>Skin Regeneration
    </h1>
    <p class="text-white/70 text-xs sm:text-sm md:text-base leading-relaxed max-w-md mb-6 md:mb-8 font-helvetica">
      Heal with science, not guesswork. LumiDerm merges cellular research and bioactive formulations to unlock your skin's true radiant potential.
    </p>
    <button class="bg-[#5794E2] text-white text-xs sm:text-sm font-medium px-6 sm:px-8 py-3 sm:py-3.5 rounded-full hover:bg-[#4a84d0] transition-all font-helvetica">
      Explore Now
    </button>
  </div>

  <!-- Hero 1 - White Card - Bottom Right -->
  <div id="hero1-card" class="hidden sm:flex absolute bottom-8 right-8 md:bottom-16 md:right-12 bg-white rounded-2xl p-4 md:p-5 items-center gap-4 md:gap-5 shadow-2xl max-w-[380px] md:max-w-[460px] z-10" style="opacity:0; transform:translateY(32px); transition:all 0.7s ease;">
    <div class="w-20 h-20 md:w-24 md:h-24 rounded-xl overflow-hidden flex-shrink-0">
      <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260619_220258_2f77857f-c799-4cce-9818-442542b98f2a.png&w=1280&q=85" alt="Featured" class="w-full h-full object-cover" />
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-4 md:gap-6">
        <div>
          <p class="text-[#010101] text-sm font-medium leading-tight font-helvetica">LumiDerm</p>
          <p class="text-[#010101] text-sm font-medium leading-tight font-helvetica">BioActive</p>
        </div>
        <button class="w-9 h-9 rounded-full bg-[#3b82f6] flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
        </button>
      </div>
      <p class="text-[#666] text-xs mt-3 font-helvetica">CellBoost&#8482; 3.0</p>
    </div>
  </div>

  <!-- Hero 2 Content - Bottom Center -->
  <div id="hero2-content" class="absolute bottom-12 sm:bottom-12 md:bottom-20 left-0 right-0 z-10 flex flex-col items-center text-center px-6" style="opacity:0; transform:translateY(30px); transition:opacity 0.3s ease, transform 0.3s ease; pointer-events:none;">
    <h2 class="text-white text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-light leading-[1.1] tracking-tight font-helvetica mb-4 md:mb-5">
      Clinically Advanced<br/>Skin Science
    </h2>
    <p class="text-white/70 text-xs sm:text-sm md:text-base leading-relaxed max-w-lg font-helvetica">
      Our patented peptide complex penetrates at the cellular level, stimulating natural collagen and restoring youthful elasticity.
    </p>
    <!-- Stats mobile -->
    <div class="flex sm:hidden items-center gap-6 mt-6">
      <div class="flex flex-col items-center">
        <span class="text-white text-xl font-light tracking-tight font-helvetica">8M+</span>
        <span class="text-white/50 text-[10px] mt-0.5 font-helvetica">Skin Transformed</span>
      </div>
      <div class="w-[1px] h-8 bg-[#5794E2]/40"></div>
      <div class="flex flex-col items-center">
        <span class="text-white text-xl font-light tracking-tight font-helvetica">96.4%</span>
        <span class="text-white/50 text-[10px] mt-0.5 font-helvetica">Visible Renewal</span>
      </div>
      <div class="w-[1px] h-8 bg-[#5794E2]/40"></div>
      <div class="flex flex-col items-center">
        <span class="text-white text-xl font-light tracking-tight font-helvetica">37</span>
        <span class="text-white/50 text-[10px] mt-0.5 font-helvetica">Patents Granted</span>
      </div>
    </div>
  </div>

  <!-- Hero 2 Stats - Right Side Desktop -->
  <div id="hero2-stats" class="hidden sm:flex absolute right-8 md:right-12 top-1/2 z-10 flex-col gap-8" style="opacity:0; transform:translateY(calc(-50% + 30px)); transition:opacity 0.3s ease, transform 0.3s ease; pointer-events:none;">
    <div class="flex flex-col items-start">
      <span class="text-white text-3xl md:text-4xl font-light tracking-tight font-helvetica">8M+</span>
      <span class="text-white/50 text-xs md:text-sm mt-1 font-helvetica">Skin Transformed</span>
      <div class="w-12 h-[1px] bg-[#5794E2]/60 mt-4"></div>
    </div>
    <div class="flex flex-col items-start">
      <span class="text-white text-3xl md:text-4xl font-light tracking-tight font-helvetica">96.4%</span>
      <span class="text-white/50 text-xs md:text-sm mt-1 font-helvetica">Visible Renewal</span>
      <div class="w-12 h-[1px] bg-[#5794E2]/60 mt-4"></div>
    </div>
    <div class="flex flex-col items-start">
      <span class="text-white text-3xl md:text-4xl font-light tracking-tight font-helvetica">37</span>
      <span class="text-white/50 text-xs md:text-sm mt-1 font-helvetica">Patents Granted</span>
    </div>
  </div>
</div>

<script>
(function() {
  // --- State ---
  let splashComplete = false;
  let progress = 0;
  let prevSection = 1;
  let mobileOpen = false;
  const mouseTarget = { x: 0, y: 0 };
  const mouseCurrent = { x: 0, y: 0 };
  const MAGNETIC_STRENGTH = 15;

  // --- DOM refs ---
  const splash = document.getElementById('splash');
  const curtainLeft = document.getElementById('curtain-left');
  const curtainRight = document.getElementById('curtain-right');
  const loaderContent = document.getElementById('loader-content');
  const progressText = document.getElementById('progress-text');
  const progressBar = document.getElementById('progress-bar');
  const navbarWrapper = document.getElementById('navbar-wrapper');
  const video1 = document.getElementById('video1');
  const video2 = document.getElementById('video2');
  const hero1Content = document.getElementById('hero1-content');
  const hero1Card = document.getElementById('hero1-card');
  const hero2Content = document.getElementById('hero2-content');
  const hero2Stats = document.getElementById('hero2-stats');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileOverlay = document.getElementById('mobile-overlay');
  const menuIcon = document.getElementById('menu-icon');
  const closeIcon = document.getElementById('close-icon');

  // --- Splash Screen ---
  const duration = 2400;
  const interval = 20;
  const steps = duration / interval;
  const increment = 100 / steps;
  let currentProgress = 0;

  const splashTimer = setInterval(function() {
    currentProgress += increment;
    if (currentProgress >= 100) {
      currentProgress = 100;
      clearInterval(splashTimer);
      setTimeout(function() {
        // Reveal curtains
        curtainLeft.style.transform = 'translateX(-100%)';
        curtainRight.style.transform = 'translateX(100%)';
        loaderContent.style.opacity = '0';
        setTimeout(function() {
          splash.style.display = 'none';
          splashComplete = true;
          activateHero();
        }, 1200);
      }, 300);
    }
    progressText.textContent = Math.round(currentProgress) + '%';
    progressBar.style.width = currentProgress + '%';
  }, interval);

  // --- Activate after splash ---
  function activateHero() {
    navbarWrapper.classList.remove('opacity-0', '-translate-y-4', 'pointer-events-none');
    navbarWrapper.classList.add('opacity-100', 'translate-y-0');
    video1.currentTime = 0;
    video1.play().catch(function(){});
    updateHeroElements();
  }

  // --- Mobile menu ---
  mobileMenuBtn.addEventListener('click', function() {
    mobileOpen = !mobileOpen;
    if (mobileOpen) {
      mobileOverlay.classList.remove('opacity-0', 'pointer-events-none');
      mobileOverlay.classList.add('opacity-100', 'pointer-events-auto');
      menuIcon.classList.add('hidden');
      closeIcon.classList.remove('hidden');
    } else {
      mobileOverlay.classList.add('opacity-0', 'pointer-events-none');
      mobileOverlay.classList.remove('opacity-100', 'pointer-events-auto');
      menuIcon.classList.remove('hidden');
      closeIcon.classList.add('hidden');
    }
  });

  document.querySelectorAll('.mobile-link').forEach(function(link) {
    link.addEventListener('click', function() {
      mobileOpen = false;
      mobileOverlay.classList.add('opacity-0', 'pointer-events-none');
      mobileOverlay.classList.remove('opacity-100', 'pointer-events-auto');
      menuIcon.classList.remove('hidden');
      closeIcon.classList.add('hidden');
    });
  });

  // --- Scroll-driven progress ---
  window.addEventListener('wheel', function(e) {
    if (!splashComplete) return;
    e.preventDefault();
    const delta = e.deltaY / 800;
    progress = Math.max(0, Math.min(1, progress + delta));
    handleSectionSwitch();
    updateHeroElements();
  }, { passive: false });

  function handleSectionSwitch() {
    const currentSection = progress < 0.5 ? 1 : 2;
    if (currentSection !== prevSection) {
      prevSection = currentSection;
      if (currentSection === 1) {
        video1.currentTime = 0;
        video1.play().catch(function(){});
        video2.pause();
      } else {
        video2.currentTime = 0;
        video2.play().catch(function(){});
        video1.pause();
      }
    }
  }

  function updateHeroElements() {
    if (!splashComplete) return;

    const hero1Opacity = Math.max(0, 1 - progress * 2.5);
    const hero1TranslateY = progress * 30;
    const hero2Opacity = Math.max(0, (progress - 0.4) * 2.5);
    const hero2TranslateY = Math.max(0, (1 - progress) * 30);

    // Videos
    video1.style.opacity = 1 - progress;
    video2.style.opacity = progress;

    // Hero 1
    hero1Content.style.opacity = hero1Opacity;
    hero1Content.style.transform = 'translateY(' + hero1TranslateY + 'px)';
    hero1Content.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    hero1Content.style.pointerEvents = hero1Opacity > 0.3 ? 'auto' : 'none';

    hero1Card.style.opacity = hero1Opacity;
    hero1Card.style.transform = 'translateY(' + hero1TranslateY + 'px)';
    hero1Card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    hero1Card.style.pointerEvents = hero1Opacity > 0.3 ? 'auto' : 'none';

    // Hero 2
    hero2Content.style.opacity = hero2Opacity;
    hero2Content.style.transform = 'translateY(' + hero2TranslateY + 'px)';
    hero2Content.style.pointerEvents = hero2Opacity > 0.3 ? 'auto' : 'none';

    hero2Stats.style.opacity = hero2Opacity;
    hero2Stats.style.transform = 'translateY(calc(-50% + ' + hero2TranslateY + 'px))';
    hero2Stats.style.pointerEvents = hero2Opacity > 0.3 ? 'auto' : 'none';
  }

  // --- Magnetic mouse parallax on videos ---
  window.addEventListener('mousemove', function(e) {
    mouseTarget.x = (e.clientX / window.innerWidth - 0.5) * -MAGNETIC_STRENGTH;
    mouseTarget.y = (e.clientY / window.innerHeight - 0.5) * -MAGNETIC_STRENGTH;
  });

  function animateMouse() {
    mouseCurrent.x += (mouseTarget.x - mouseCurrent.x) * 0.08;
    mouseCurrent.y += (mouseTarget.y - mouseCurrent.y) * 0.08;
    const transform = 'translate3d(' + mouseCurrent.x + 'px, ' + mouseCurrent.y + 'px, 0) scale(1.05)';
    video1.style.transform = transform;
    video2.style.transform = transform;
    requestAnimationFrame(animateMouse);
  }
  requestAnimationFrame(animateMouse);
})();
</script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "PROMPT"
template_id: "619b1cce-fd72-4233-9013-95150d065413"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 PROMPT

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `619b1cce-fd72-4233-9013-95150d065413`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![PROMPT](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/e9d8b91e-518a-448d-9812-96117520b652.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
### Overview

Build a full-screen, scroll-driven fashion/archive landing page for a brand called "prmpt". The page has two main phases:

1. **Hero phase** (first 100vh of scroll): Full-viewport video background with overlaid UI (logo, nav, product info, custom cursor). A black panel slides up from below covering the video.
2. **Gallery phase** (continues scrolling): The black panel contains a scattered grid of product images that scale in/out as they enter/exit the viewport. At the end, a white overlay fades in with a "view" CTA button.

---

### Tech Stack

- **React 19** + **TypeScript**
- **Vite 6** with `@vitejs/plugin-react`
- **Tailwind CSS v4** via `@tailwindcss/vite` plugin
- **GSAP 3.15** + `@gsap/react` (ScrollTrigger)
- **Motion (Framer Motion) 12** (`motion/react`)
- **Font**: "Inter Tight" (Google Fonts, weight 500) -- loaded via `<link>` or import

---

### Asset URLs

**Videos (CloudFront):**
- LEFT video: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260625_154433_532a85d3-dabf-4265-b8bd-19ac6af31842.mp4`
- RIGHT video: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260625_154401_a664f076-b971-4557-8728-40ef9ea4c49b.mp4`

**Gallery Images (10 total, in order):**
1. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_104530_521b2f85-c0f3-4d0e-9704-b578315b4cb9.png&w=1920&q=85`
2. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103711_76ccdb8b-5043-4f47-9c54-4379713393ea.png&w=1920&q=85`
3. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103728_394f6a1b-85e2-4386-a4f6-408472a0a5b7.png&w=1920&q=85`
4. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103739_86743e0e-16a7-4bee-bf38-dd67985344dc.png&w=1920&q=85`
5. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103748_b2215dc8-a3a7-470d-b19a-5b87fa7d0c37.png&w=1920&q=85`
6. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103758_e919ce72-5c9d-4b87-9be6-d7647b34825c.png&w=1920&q=85`
7. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103808_013583d0-3386-4547-9832-37c7d8edb3ac.png&w=1920&q=85`
8. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103937_a0c49d0a-33eb-4ead-aea6-c1baf241acbc.png&w=1920&q=85`
9. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_103956_d18ed8fd-7b6f-4b86-91f9-20010fe38670.png&w=1920&q=85`
10. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260629_104034_ba5a9963-87ff-4008-a545-6bd686c088b5.png&w=1920&q=85`

---

### SECTION 1: Hero (Video Background + Overlaid UI)

#### Root Container
- `id="scroll-spacer"`, `position: relative`, `user-select: none`, `background: white`
- Height is dynamically calculated (initially `500vh`, then overridden by GSAP to `vh + maxScroll + 2*vh`)
- Custom cursor hidden on desktop (`cursor: none`), default on touch devices

#### 1A. Custom Cursor (Desktop Only)
- Hidden on mobile/tablet (< 1024px)
- A `fixed`, `pointer-events-none`, `z-index: 50` div that follows `mousemove`
- Positioned via direct DOM manipulation (`style.left/top = clientX/clientY`)
- `transform: translate(-50%, -50%)` to center on pointer
- `mix-blend-mode: exclusion`
- Contains a 48x48 SVG: a circle with stroke (r=22.75, strokeWidth=2.5) containing a custom Japanese/decorative glyph path, all filled white

#### 1B. Logo (Top Left)
- `position: fixed`, `pointer-events-none`, `z-index: 20`
- `mix-blend-mode: exclusion`
- Responsive width: 124px (mobile < 640), 266px (tablet 640-1024), 355px (desktop)
- Position: `top: 16px, left: 16px` (mobile), `top: 32px, left: 32px` (desktop)
- Motion animation: fade in + slide up (`opacity: 0->1, y: 12->0`), duration 0.6s, ease `[0.25, 0.1, 0.25, 1]`, delay 0s
- SVG viewBox `0 0 355 110`, contains the "prmpt" wordmark + circled "R" mark, all paths filled white

#### 1C. Caption (Below Logo, Left Side)
- `position: fixed`, `pointer-events-none`, `z-index: 20`
- `mix-blend-mode: exclusion`
- Position: `left: 32px` (desktop), `left: 16px` (mobile)
- Top: 244px (desktop), 180px (tablet), 118px (mobile)
- Width: 692px (desktop), `calc(50vw - 48px)` (tablet), `calc(100vw - 32px)` (mobile)
- Font: Inter Tight, weight 500, size 12px, line-height 140%, letter-spacing -0.04em, color #FFFFFF
- Motion animation: same as logo but delay 0.3s
- Text content: "When switching between videos near the center, do not reset currentTime to 0 abruptly. Add a small dead zone: if cursor is within +/-50px of center, keep both videos at currentTime = 0 and show whichever was last active."

#### 1D. Header Navigation (Top Right)
- `position: fixed`, `z-index: 20`, `pointer-events-none`
- `mix-blend-mode: exclusion`
- Position: `top: 32px, right: 32px` (desktop), `top: 16px, right: 16px` (mobile)
- Width: 330px (desktop), auto (mobile)
- Height: 30px
- Flex row, justify-content: space-between, align-items: center
- Motion animation: same easing, delay 0.15s
- Contains:
  - "ABOUT" text (hidden on mobile): Inter Tight, 500, 15px, uppercase, white
  - A flex row with gap 50px (desktop) / 20px (mobile):
    - Hamburger SVG icon: viewBox `0 0 40 40`, two horizontal lines (`M0 14H40` and `M0 26H40`), stroke white, strokeWidth 2.5. Size: 30x30 (desktop), 24x24 (mobile)
    - "[ CART ]" text: Inter Tight, 500, 15px (desktop) / 13px (mobile), white

#### 1E. Product Info (Bottom Right)
- `id="outro-info"`, `position: fixed`, `pointer-events-none`, `z-index: 20`
- `mix-blend-mode: exclusion`
- **Desktop**: right: 32px, bottom: 80px, width: 330px, flex-column, align center
- **Mobile**: left: 0, right: 0, bottom: 48px, flex-column, align center
- Motion animation: opacity 0->1, delay 0.45s
- `data-outro-offset`: 166 (desktop), 132 (mobile) -- used by scroll animation
- Contains:
  - Top block (flex-column, align flex-start, width 100% desktop / 252px mobile, margin-bottom 32px desktop / 12px mobile):
    - Circle icon: relative div (30x30 desktop, 20x20 mobile) containing:
      - SVG circle (cx=20, cy=20, r=18.75, stroke white, strokeWidth 2.5 desktop / 2 mobile)
      - `<span id="circle-symbol">` centered inside, shows "8" initially, changes to random symbol from `['8', '$', '^^', '%', '/']` on scroll (throttled 80ms)
      - Font: Inter Tight, 500, 15px (desktop) / 10px (mobile), letter-spacing -0.04em, uppercase, white
    - Collection label: Inter Tight, 500, 30px (desktop) / 20px (mobile), line-height 100%, text-align center, letter-spacing -0.04em, uppercase, white. Content: `ARCHIVE COLLECTION` + line break + `"PROMPT"`
  - Price: Inter Tight, 500, 80px (desktop) / 60px (mobile), line-height 100%, text-align center, letter-spacing -0.04em, white. Content: `$97,33`

#### 1F. "View" Button (Bottom Right, Initially Hidden)
- `id="outro-buy"`, `position: fixed`, `pointer-events-none`, `z-index: 20`
- `mix-blend-mode: exclusion`
- **Desktop**: right: 32px, bottom: 32px, width: 330px, height: 174px
- **Mobile**: left: 16px, right: 16px, bottom: 60px, height: 100px
- `transform-origin: right bottom`, `transform: scale(0)` (starts hidden, scales to 1 via scroll)
- Background: #fff, border-radius: 1335px (pill shape)
- Flex center
- Text "view": Inter Tight, 500, 110px (desktop) / 72px (mobile), letter-spacing -0.04em, color #fff, `mix-blend-mode: exclusion`

#### 1G. Video Container
- `id="main-canvas"`, `pointer-events-none`
- **Desktop**: `position: fixed, inset: 0, width: 100%, height: 100%, z-index: 0`
- **Mobile**: `position: fixed, left: 0, top: 220px, width: 100vw, height: calc(100vh - 220px), z-index: 0`
- Opacity transition: 0 -> 1 when both videos loaded (`opacity 0.3s ease`)
- `overflow: hidden`
- Contains two `<video>` elements (muted, playsInline, preload="auto"), absolutely positioned to fill container, `object-fit: cover`
- Left video starts `display: none`, right starts `display: block`


**Desktop (non-touch):**
- Videos are NOT auto-played. They are scrubbed based on cursor X position via `requestAnimationFrame`.
- Dead zone: `Math.max(30, width * 0.05)` pixels from center
- If cursor is in dead zone, keep current video at `currentTime = 0`
- If cursor moves left of dead zone: show RIGHT video, scrub it based on distance from center-left-edge to left edge
- If cursor moves right of dead zone: show LEFT video, scrub it based on distance from center+deadzone to right edge
- `activeSideRef` tracks which side was last active, only changes when cursor exceeds dead zone
- Progress calculation: `(distance from dead zone edge) / (available range)` mapped to `0...video.duration`
CRITICAL: Only update currentTime when !video.seeking -- this prevents jittery playback by waiting for the browser to finish rendering the previous seek before requesting a new one.
#### 1H. Video Interaction Logic

**Mobile/Tablet (touch):**
- Videos auto-play alternately: left plays first, on `ended` event switches to right, on right `ended` switches back to left
- Respects `prefers-reduced-motion`

#### 1I. White Overlay
- `id="outro-overlay"`, `position: fixed, inset: 0`, `pointer-events-none`, `z-index: 12`
- Background: #fff, opacity: 0 (controlled by scroll)

#### 1J. Footer
- `id="outro-footer"`, `position: fixed`, `pointer-events-none`
- Left: 16px, bottom: 32px (desktop) / 24px (mobile)
- `mix-blend-mode: exclusion`, opacity: 0 (controlled by scroll)
- Flex row, gap: 80px (desktop) / space-between (mobile)
- Two spans: "PRMPT (R) 2026" and "PRIVACY POLICY"
- Font: Inter Tight, 500, 13px (desktop) / 11px (mobile), letter-spacing -0.02em, uppercase, white

---

### SECTION 2: Black Panel (Gallery)

#### Container
- `position: fixed, inset: 0`, background: black, `z-index: 10`
- Initially translated `translateY(100vh)` (off-screen below)
- Slides up to `translateY(0)` during first 100vh of scroll via GSAP ScrollTrigger (scrub: true, ease: none)

#### Inner Wrapper
- `width: 100%`, `padding-top: min(400px, 40vh)`

#### Grid Layout Algorithm
- Responsive columns: 2 (< 640px), 3 (640-1024px), 4 (>= 1024px)
- Each cell has `aspect-ratio: 2/3`
- Layout function `buildLayout(count, cols)` creates rows:
  - For each row `r`, compute primary column: `a = (r * 2 + (r % 2)) % cols`
  - Place one image at column `a`
  - Every 3rd row (`r % 3 === 0`), place a second image at `b = (a + 2) % cols` (or `(a+1)%cols` if same as a)
  - Empty cells get `-1` (rendered as empty spacer divs)

#### Card Behavior
- Each card has class `bp-card`, `will-change: transform`
- `transform: scale(0)` initially
- `transform-origin`: cards in left half of grid get `right bottom`, right half get `left bottom`
- Scale is computed per-frame in RAF based on card's vertical position:
  - **Enter**: `Math.min(1, (vh - top) / (vh * 0.6))` -- scales from 0 to 1 as it enters viewport
  - **Exit**: `Math.min(1, bottom / (vh * 0.4))` -- scales from 1 to 0 as it exits top
  - Final scale: `Math.min(enter, exit)`
  - If card is fully off-screen (bottom <= 0 or top >= vh): `scale(0)`

#### Scroll Phases (RAF-based, NOT scroll events)
- **Phase 1** (scrollY 0 to vh): Panel slides up. Cards are computed with panelOffset = `vh - scrollY`
- **Phase 2** (scrollY > vh): Panel is fixed at top. Inner wrapper translates up: `translateY(-(scrollY - vh))`. Cards recomputed with phase2 offset.
- **Outro** (scrollY > vh + maxScroll): White overlay fades in, product info slides up by `outroOffset` px, "view" button scales from 0 to 1, footer fades in. Progress: `(scrollY - vh - maxScroll) / (vh - 100)`

#### Spacer Height Calculation
- Set dynamically: `vh + maxScroll + 2 * vh` where `maxScroll = wrapScrollHeight - vh`

---

### CSS (index.css)

```css
@import "tailwindcss";

.bp-card {
  will-change: transform;
}

@media (prefers-reduced-motion: reduce) {
  .bp-card {
    will-change: auto;
  }
}
```

---

### Responsive Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: >= 1024px

---

### Key Design Principles
- All text overlays use `mix-blend-mode: exclusion` to remain visible against both light and dark backgrounds
- No visible scroll bar interaction -- entirely RAF-driven position tracking
- `pointer-events-none` on all overlaid UI elements
- `user-select: none` on root container
- Videos hidden (`visibility: hidden`) once scroll passes first viewport height
- Circle symbol randomizes on scroll (throttled to 80ms)
- Entry animations staggered: logo (0s), nav (0.15s), caption (0.3s), product info (0.45s)
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Vision Reveal"
template_id: "636f43d2-79be-4288-a0c4-717f77ee4087"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Vision Reveal

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `636f43d2-79be-4288-a0c4-717f77ee4087`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Vision Reveal](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/2b280d32-6b2f-4295-b044-20d0b3855032.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Creative Studio Showcase</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
* { font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }

html, body {
  margin: 0; padding: 0;
  background: #E4E4E4;
  color: #F4F1E8;
  overflow-x: hidden;
  scroll-behavior: smooth;
}

/* ===== SPLASH ===== */
.splash {
  position: fixed; inset: 0;
  width: 100vw; height: 100vh;
  z-index: 9999;
  pointer-events: none;
  overflow: hidden;
  animation: splashHide 0.3s ease forwards;
  animation-delay: 1.35s;
}
.splash-row { display: flex; width: 100%; height: 50%; }
.splash-box { width: 20%; height: 100%; background: #75C5DE; }
.splash-row-top .splash-box { animation: splashTop 1s cubic-bezier(0.96,-0.02,0.38,1.01) forwards; }
.splash-row-bottom .splash-box { animation: splashBottom 1s cubic-bezier(0.96,-0.02,0.38,1.01) forwards; }
.splash-box:nth-child(1) { animation-delay: 0s; }
.splash-box:nth-child(2) { animation-delay: 0.05s; }
.splash-box:nth-child(3) { animation-delay: 0.1s; }
.splash-box:nth-child(4) { animation-delay: 0.15s; }
.splash-box:nth-child(5) { animation-delay: 0.2s; }

@keyframes splashTop { from { transform: translateY(0%); } to { transform: translateY(-100%); } }
@keyframes splashBottom { from { transform: translateY(0%); } to { transform: translateY(100%); } }
@keyframes splashHide { to { opacity: 0; visibility: hidden; } }

/* ===== HERO IMAGE ENTRANCE ===== */
@keyframes heroImageIn {
  from { opacity: 0; transform: scale(1.5) rotate(3deg); }
  to { opacity: 1; transform: scale(1) rotate(0deg); }
}
.hero-image-animate {
  animation: heroImageIn 1.2s cubic-bezier(0.25,0.46,0.45,0.94) forwards;
  animation-delay: 1s;
  opacity: 0;
}

/* ===== WORD REVEAL ===== */
@keyframes wordReveal {
  from { opacity: 0; transform: translateY(10px); filter: blur(10px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
.word-reveal {
  opacity: 0;
  display: inline-block;
  margin-right: 0.3em;
  animation: wordReveal 0.4s ease forwards;
}

/* ===== CTA ENTRANCE ===== */
@keyframes slideUpScale {
  from { opacity: 0; transform: translateY(60px) scale(0.4); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.cta-animate {
  opacity: 0;
  animation: slideUpScale 0.8s cubic-bezier(0.25,0.46,0.45,0.94) forwards;
  animation-delay: 1s;
}

/* ===== CTA BUTTON ===== */
.cta-btn { position: relative; overflow: hidden; display: flex; align-items: center; border: none; background: none; cursor: pointer; border-radius: 9999px; padding: 8px; gap: 12px; }
.cta-btn-bg {
  position: absolute; top: 5px; bottom: 5px; left: 8px;
  width: calc(100% - 8px - 8px - 48px - 12px);
  border-radius: 9999px; background: white; z-index: 0;
  transition: width 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
}
@media (min-width: 768px) { .cta-btn-bg { width: calc(100% - 8px - 8px - 54px - 12px); } }
.cta-btn:hover .cta-btn-bg { width: calc(100% - 16px); }
.cta-btn-text { position: relative; z-index: 1; color: #111111; font-weight: 500; font-size: 16px; padding: 12px 32px; white-space: nowrap; }
@media (min-width: 768px) { .cta-btn-text { font-size: 18px; padding: 16px 40px; } }
.cta-btn-circle {
  position: relative; z-index: 1; display: flex; align-items: center; justify-content: center;
  width: 48px; height: 48px; border-radius: 50%; background: #75C5DE; flex-shrink: 0;
  transition: transform 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
}
@media (min-width: 768px) { .cta-btn-circle { width: 54px; height: 54px; } }
.cta-btn:hover .cta-btn-circle { transform: translateX(-7px); }

/* ===== MENU CTA (smaller) ===== */
.menu-cta-btn { position: relative; overflow: hidden; display: flex; align-items: center; border: none; background: none; cursor: pointer; border-radius: 9999px; padding: 6px; gap: 8px; }
.menu-cta-bg {
  position: absolute; top: 5px; bottom: 5px; left: 8px;
  width: calc(100% - 8px - 8px - 38px - 8px);
  border-radius: 9999px; background: white; z-index: 0;
  transition: width 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
}
.menu-cta-btn:hover .menu-cta-bg { width: calc(100% - 12px); }
.menu-cta-text { position: relative; z-index: 1; color: #111111; font-weight: 500; font-size: 14px; padding: 8px 40px; white-space: nowrap; }
.menu-cta-circle {
  position: relative; z-index: 1; display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 50%; background: #75C5DE; flex-shrink: 0;
  transition: transform 0.3s ease;
}
.menu-cta-btn:hover .menu-cta-circle { transform: translateX(-4px); }

/* ===== CREATOR TEXT ===== */
@keyframes creatorSlideUp { from { transform: translateY(330px); } to { transform: translateY(0); } }
.creator-text-animate {
  transform: translateY(330px);
  animation: creatorSlideUp 1s cubic-bezier(0.16,1,0.3,1) forwards;
  animation-delay: 1.5s;
}

/* ===== NAVIGATION ===== */
.logo-wrapper {
  position: fixed; top: 30px; left: 0; width: 50%; z-index: 10;
  display: flex; justify-content: flex-start; align-items: center; mix-blend-mode: difference;
}
@media (min-width: 768px) { .logo-wrapper { top: 40px; } }
.logo-wrapper .inner { padding-left: 20px; }
@media (min-width: 768px) { .logo-wrapper .inner { padding-left: 40px; } }
.logo-wrapper img { width: 32px; height: 32px; }

.burger-wrapper {
  position: fixed; top: 16px; right: 0; width: 50%; z-index: 10;
  display: flex; justify-content: flex-end; align-items: center;
}
@media (min-width: 768px) { .burger-wrapper { top: 27px; } }
.burger-wrapper .inner { padding-right: 20px; }
@media (min-width: 768px) { .burger-wrapper .inner { padding-right: 40px; } }

.burger-btn {
  width: 59px; height: 59px; border-radius: 50%; border: none; cursor: pointer;
  display: flex; flex-direction: column; gap: 4px; align-items: center; justify-content: center;
  background: #F4F1E8; transition: background 0.4s ease;
}
.burger-btn:hover { background: #0B0B0B; }
.burger-btn .bar {
  display: block; width: 24px; height: 2px; background: #111111;
  transition: all 0.3s ease;
}
.burger-btn:hover .bar { background: #F4F1E8; }
.burger-btn.open { background: #0B0B0B; }
.burger-btn.open .bar { background: #F4F1E8; }
.burger-btn.open .bar:first-child { transform: rotate(45deg) translate(2px, 2px); }
.burger-btn.open .bar:last-child { transform: rotate(-45deg) translate(2px, -2px); }

/* ===== MENU PANEL ===== */
.menu-panel {
  position: fixed; z-index: 9;
  left: 8px; right: 8px;
  border-radius: 20px;
  background: rgba(17,17,17,0.95);
  backdrop-filter: blur(26px); -webkit-backdrop-filter: blur(26px);
  padding: 90px 32px 32px 32px;
  display: flex; flex-direction: column; justify-content: space-between;
  transition: top 0.5s cubic-bezier(0.25,0.46,0.45,0.94), opacity 0.4s ease;
  top: -600px; opacity: 0; pointer-events: none;
}
@media (min-width: 768px) {
  .menu-panel { left: auto; right: 7px; width: 420px; padding: 60px; }
}
.menu-panel.open { top: 0; opacity: 1; pointer-events: auto; }
@media (min-width: 768px) { .menu-panel.open { top: 7px; } }

.menu-panel nav { display: flex; flex-direction: column; gap: 8px; }
.menu-panel nav a {
  color: #F4F1E8; font-size: 36px; font-weight: 500; text-decoration: none;
  line-height: 130%; transition: opacity 0.3s ease;
}
@media (min-width: 768px) { .menu-panel nav a { font-size: 42px; } }
.menu-panel nav a:hover { opacity: 0.7; }

.menu-contact { display: flex; flex-direction: column; gap: 20px; margin-top: 32px; }
.menu-email { color: #9A9590; font-size: 18px; text-decoration: none; transition: color 0.3s ease; }
@media (min-width: 768px) { .menu-email { font-size: 20px; } }
.menu-email:hover { color: #F4F1E8; }
.menu-socials { display: flex; gap: 24px; }
.menu-socials a {
  color: #9A9590; font-size: 14px; text-decoration: underline;
  text-underline-offset: 2px; transition: color 0.3s ease;
}
.menu-socials a:hover { color: #F4F1E8; }

/* ===== HERO ===== */
.hero {
  position: relative; width: 100%; overflow: hidden;
  background: #E4E4E4; min-height: 100vh;
}
@media (min-width: 768px) { .hero { height: 100vh; min-height: 800px; } }

.hero-big-text {
  position: absolute; bottom: -30px; left: 0; right: 0; z-index: 2;
  pointer-events: none; width: 100%; text-align: center;
}
@media (min-width: 768px) { .hero-big-text { bottom: -40px; } }
.hero-big-text h2 {
  font-weight: 500; color: #F4F1E8; line-height: 80%;
  letter-spacing: -0.04em; white-space: nowrap;
  font-size: clamp(180px, 28vw, 560px);
}

.hero-base-img {
  position: absolute; top: 30vh; left: 0; right: 0; bottom: 0;
  background-size: cover; background-repeat: no-repeat;
  background-position: 60% center; z-index: 5;
}
@media (min-width: 768px) { .hero-base-img { top: 0; background-position: center; } }

.hero-reveal-img {
  position: absolute; top: 30vh; left: 0; right: 0; bottom: 0;
  background-size: cover; background-repeat: no-repeat;
  background-position: 60% center; z-index: 7; pointer-events: none;
}
@media (min-width: 768px) { .hero-reveal-img { top: 0; background-position: center; } }

.hero-content {
  position: relative; z-index: 8;
  display: flex; flex-direction: column; justify-content: flex-start; align-items: flex-start;
  width: 100%; max-width: 1600px; margin: 0 auto;
  padding: 110px 16px 24px 16px; pointer-events: none;
}
@media (min-width: 768px) {
  .hero-content {
    position: absolute; inset: 0;
    justify-content: space-between;
    padding: 160px 40px 100px 40px;
  }
}
.hero-content-inner { display: flex; flex-direction: column; align-items: flex-start; gap: 30px; width: 100%; pointer-events: auto; }

.hero-headline {
  font-size: 22px; font-weight: 500; line-height: 120%;
  letter-spacing: -0.02em; color: #111111; max-width: 447px;
}
@media (min-width: 768px) { .hero-headline { font-size: 28px; } }

/* ===== CANVAS (hidden) ===== */
#reveal-canvas { display: none; position: absolute; inset: 0; pointer-events: none; }

/* ===== REDUCED MOTION ===== */
@media (prefers-reduced-motion: reduce) {
  .splash { animation: splashHide 0.01s linear forwards; }
  .splash-box { animation: none !important; }
  .hero-image-animate, .word-reveal, .cta-animate, .creator-text-animate {
    animation: none !important; opacity: 1 !important;
    transform: none !important; filter: none !important; visibility: visible !important;
  }
}
</style>
</head>
<body>

<!-- SPLASH -->
<div class="splash" id="splash">
  <div class="splash-row splash-row-top">
    <div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div>
  </div>
  <div class="splash-row splash-row-bottom">
    <div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div><div class="splash-box"></div>
  </div>
</div>

<!-- LOGO -->
<div class="logo-wrapper">
  <div class="inner">
    <a href="/" aria-label="Home">
      <img src="https://framerusercontent.com/images/VMcS7YYTM5PXfXvlHc9u3hSCMM.svg" alt=""/>
    </a>
  </div>
</div>

<!-- BURGER -->
<div class="burger-wrapper">
  <div class="inner">
    <button class="burger-btn" id="burger-btn" aria-label="Open menu">
      <span class="bar"></span>
      <span class="bar"></span>
    </button>
  </div>
</div>

<!-- MENU PANEL -->
<div class="menu-panel" id="menu-panel">
  <nav>
    <a href="#work">Work</a>
    <a href="#about">About</a>
    <a href="#blog">Blog</a>
  </nav>
  <div class="menu-contact">
    <a href="mailto:studio@norakessler.com" class="menu-email">studio@norakessler.com</a>
    <div class="menu-socials">
      <a href="#">Pinterest</a>
      <a href="#">Behance</a>
      <a href="#">Letterboxd</a>
    </div>
  </div>
  <div style="margin-top:32px;">
    <button class="menu-cta-btn">
      <span class="menu-cta-bg"></span>
      <span class="menu-cta-text">Let's talk</span>
      <span class="menu-cta-circle">
        <svg width="14" height="14" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 13L13 5M13 5H6M13 5V12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
    </button>
  </div>
</div>

<!-- HERO -->
<main class="hero">
  <!-- Big text behind image -->
  <div class="hero-big-text creator-text-animate">
    <h2>Visuals</h2>
  </div>

  <!-- Base image -->
  <div class="hero-base-img hero-image-animate"
       style="background-image:url('https://soft-zoom-63098134.figma.site/_assets/v11/5c9f982199fde1d9b85a20e5396f0fa7bacaf9a3.png?w=2560');">
  </div>

  <!-- Reveal layer -->
  <canvas id="reveal-canvas"></canvas>
  <div class="hero-reveal-img" id="reveal-img"
       style="background-image:url('https://soft-zoom-63098134.figma.site/_assets/v11/6be2165e31648955b4e071f4cf2a50bc572b9bfd.png?w=1536');">
  </div>

  <!-- Content -->
  <div class="hero-content">
    <div class="hero-content-inner">
      <h1 class="hero-headline" id="headline"></h1>
      <button class="cta-btn cta-animate">
        <span class="cta-btn-bg"></span>
        <span class="cta-btn-text">Start a project now</span>
        <span class="cta-btn-circle">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 13L13 5M13 5H6M13 5V12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
      </button>
    </div>
  </div>
</main>

<script>
(function() {
  // Word reveal
  const headline = document.getElementById('headline');
  const text = "I build compelling visual stories & motion that make ideas shine.";
  const words = text.split(' ');
  words.forEach(function(word, i) {
    const span = document.createElement('span');
    span.className = 'word-reveal';
    span.textContent = word;
    span.style.animationDelay = (1 + i * 0.05) + 's';
    headline.appendChild(span);
  });

  // Burger menu toggle
  const burgerBtn = document.getElementById('burger-btn');
  const menuPanel = document.getElementById('menu-panel');
  let menuOpen = false;
  burgerBtn.addEventListener('click', function() {
    menuOpen = !menuOpen;
    if (menuOpen) {
      burgerBtn.classList.add('open');
      menuPanel.classList.add('open');
      burgerBtn.setAttribute('aria-label', 'Close menu');
    } else {
      burgerBtn.classList.remove('open');
      menuPanel.classList.remove('open');
      burgerBtn.setAttribute('aria-label', 'Open menu');
    }
  });
  // Close menu on nav link click
  menuPanel.querySelectorAll('nav a').forEach(function(a) {
    a.addEventListener('click', function() {
      menuOpen = false;
      burgerBtn.classList.remove('open');
      menuPanel.classList.remove('open');
    });
  });

  // Spotlight reveal
  const SPOTLIGHT_R = 260;
  const canvas = document.getElementById('reveal-canvas');
  const imgLayer = document.getElementById('reveal-img');
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  const mouse = { x: -999, y: -999 };
  const smooth = { x: -999, y: -999 };

  window.addEventListener('mousemove', function(e) {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  function loop() {
    smooth.x += (mouse.x - smooth.x) * 0.1;
    smooth.y += (mouse.y - smooth.y) * 0.1;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var grad = ctx.createRadialGradient(smooth.x, smooth.y, 0, smooth.x, smooth.y, SPOTLIGHT_R);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.4, 'rgba(255,255,255,1)');
    grad.addColorStop(0.6, 'rgba(255,255,255,0.75)');
    grad.addColorStop(0.75, 'rgba(255,255,255,0.4)');
    grad.addColorStop(0.88, 'rgba(255,255,255,0.12)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');

    ctx.beginPath();
    ctx.arc(smooth.x, smooth.y, SPOTLIGHT_R, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    var dataUrl = canvas.toDataURL();
    imgLayer.style.webkitMaskImage = 'url(' + dataUrl + ')';
    imgLayer.style.maskImage = 'url(' + dataUrl + ')';
    imgLayer.style.webkitMaskSize = '100% 100%';
    imgLayer.style.maskSize = '100% 100%';

    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
</script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Neon Logic"
template_id: "8942cf17-2544-4794-9a67-177e3c539b3d"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Neon Logic

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `8942cf17-2544-4794-9a67-177e3c539b3d`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Neon Logic](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5cb6071d-165d-4d20-97d0-22f257bba541.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page landing site for "SynapseX" -- a futuristic neural-AI interface product. The entire site uses a black background with white text and full-viewport video backgrounds. The primary font is "Space Mono" (monospace) for all text. Use React + TypeScript + Vite + Tailwind CSS + Framer Motion.

### Fonts & External Assets

- **Primary font:** "Space Mono" (all weights: 400, 700, italic) from Google Fonts
- **Display font (background watermark only):** "Anton SC" from Google Fonts
- **Icons:** Bootstrap Icons CDN (`https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css`) -- used only for the Apple icon (`bi bi-apple`) in the download button
- **All Tailwind `fontFamily` keys** (`sans`, `serif`, `mono`) are overridden to `"Space Mono", monospace`

### Video URLs (CloudFront -- use exactly these)

1. **Hero (mouse-scrubbed, NOT autoplay):**
   `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_083515_290e5a10-0b95-41af-a5e2-32b6389baa4d.mp4`

2. **Second Section (autoplay, muted, loop):**
   `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_092455_089c54f8-3b03-4966-9df1-e9746063d0ef.mp4`

3. **Metrics Section (autoplay, muted, loop):**
   `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_095810_ecea3dd2-fc5e-4e41-8696-4219290b6589.mp4`

4. **Technology Section (autoplay, muted, loop):**
   `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_095750_32a52ce0-2005-45c9-9093-41f03fde9530.mp4`

5. **Footer (autoplay, muted, loop):**
   `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_080203_fd7f4f85-3a86-4837-8192-85e7bfe68e75.mp4`

### Dependencies

```json
"framer-motion": "^12.40.0",
"lucide-react": "^0.344.0",
"react": "^18.3.1",
"react-dom": "^18.3.1"
```

### Global CSS (`index.css`)

- Import Space Mono from Google Fonts
- Import Bootstrap Icons CSS
- Tailwind directives (`@tailwind base/components/utilities`)
- CSS variables: all `--font-*` set to `"Space Mono", monospace`
- Global reset: `* { margin: 0; padding: 0; box-sizing: border-box; }`
- `html, body`: `background: #000; color: #fff; overflow-x: hidden; overflow-y: auto; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;`
- Lenis smooth scroll utility classes (`.lenis.lenis-smooth`, `.lenis.lenis-stopped`, `.lenis.lenis-scrolling iframe`)

### Custom Text Animation Components

#### 1. `ScrambleIn` -- entrance reveal animation
- Props: `text: string`, `delay: number` (ms before start), `triggered: boolean`
- Character set: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+~|}{[]:;?><`
- On trigger (after delay): runs interval every 25ms, revealing characters left-to-right at 0.5 chars/frame
- Characters not yet revealed show random chars (up to 3 ahead of the reveal cursor); characters beyond that are empty
- Spaces always show as spaces
- Before triggered: renders `&nbsp;`

#### 2. `ScrambleText` -- hover-driven scramble
- Props: `text: string`, `isHovered: boolean`, `className?: string`
- On hover: scrambles all chars with random chars, then reveals left-to-right at 4 frames/char, interval 25ms
- On unhover: immediately resets to original text

### Custom SVG Logo (`SynapseXLogo`)

A 4-fold rotationally symmetric abstract shape rendered in an SVG with `viewBox="-50 -50 100 100"`. Each quadrant is the same path rotated 0/90/180/270 degrees:

```
M 1.5,23 L 1.5,33 C 1.5,38.5 6,43 11.5,43 L 16.5,43 C 22,43 26.5,38.5 26.5,33 Q 28,28 33,26.5 C 38.5,26.5 43,22 43,16.5 L 43,11.5 C 43,6 38.5,1.5 33,1.5 L 23,1.5 Q 12,12 1.5,23 Z
```

### Animated Hamburger (`SquashHamburger`)

- 3 horizontal bars (absolute positioned spans)
- Desktop: container 18x12px, bar height 1.5px
- Mobile: container 15x10px, bar height 1.2px
- On open: top bar rotates 45deg + translates down to center; middle bar fades/scales out; bottom bar rotates -45deg + translates up to center
- Spring animation: stiffness 300, damping 20

---

### Page Sections (in order)

---

#### SECTION 1: Hero (full viewport height)

- **Background:** Video #1, `object-cover`, paused on load. Controlled by mouse-scrub: horizontal mouse movement across viewport scrubs the video timeline forward/backward. Sensitivity factor: `0.8`. Uses `seeked` event to chain seeks without dropping frames.
- **Entrance animation:** After 800ms delay, `entranceComplete` state becomes true -- all hero content fades in (opacity 0 -> 1, duration 1s).
- **Dot grid overlay:** `radial-gradient(#ffffff 1px, transparent 1px)` with 24x24px grid, opacity 0.05, pointer-events-none
- **Large background watermark text:** The word "TRANSCENDENCE" in "Anton SC" font, centered vertically (offset +50px from center), `clamp(120px, 30vw, 521px)` font size, uppercase, letter-spacing -4px. Opacity 0.10. Color achieved via `radial-gradient(circle, rgba(142,127,148,0) 0%, #8E7F94 70%)` as `background-clip: text` with transparent fill.
- **Layout:** Flexbox column, padding `px-4 sm:px-6 md:px-8 pt-20 sm:pt-24 pb-8 sm:pb-12`. Content is pushed to the bottom using `flex-1` spacer.
- **Bottom row:** `flex-col gap-6 md:flex-row md:items-end md:justify-between`
  - **Left column** (`flex flex-col gap-4`):
    - **h1** "Brain" / "And Body" (two lines via `<br>`): `text-white font-light leading-[0.95] tracking-[-0.03em] text-[clamp(40px,10vw,100px)]`. Each line uses `ScrambleIn` with delays 200ms and 500ms.
    - **Description paragraph** (motion.p): fade-up animation (y:25->0, opacity 0->1, duration 0.9s, cubic-bezier ease `[0.215, 0.610, 0.355, 1.000]`, delay 0.2s). Text: "Built at the intersection of neuroscience and artificial intelligence. SynapseX continuously maps neural pathways, cognitive load, and physiological states into a single adaptive intelligence layer." Style: `max-w-sm text-[13px] sm:text-[15px] text-white/60 leading-relaxed`
  - **Right h1** "One" / "Network": Same styling as left h1 but with `text-left md:text-right`. ScrambleIn delays: 700ms and 1000ms.

---

#### NAVBAR (fixed, z-50)

- Fixed to top, height 80px (h-20), transparent background, full width
- Fades in with `entranceComplete` (opacity 0->1, duration 0.8s)

**Desktop (hidden below `sm`):**
- Left group: two pills side by side with gap-2
  - **Logo pill:** h-12, px-5, `bg-white/15 backdrop-blur-md rounded-[14px]`. Contains SynapseXLogo (18x18px white) + "SynapseX" text (16px font-medium tracking-tight white). WhileHover: scale 1.02 + bg rgba(255,255,255,0.22). WhileTap: scale 0.98. Hides on `sm` when menu open (`hidden md:flex`), shows normally otherwise.
  - **Expanding menu pill:** Animates width from 48px (closed) to 290px (open) with spring (stiffness 350, damping 28). h-12, `rounded-[14px]`, `bg-white/15 backdrop-blur-md`. Contains:
    - Hamburger button: when closed = 48x48px rounded-[14px]; when open = 36x36px rounded-[11px] with `bg-white/10 hover:bg-white/20 ml-1.5`
    - Nav links (fade in when open, offset x:15->0): "About" and "Metrics" with ScrambleText on hover. 16px font-normal text-white/85 hover:text-white. Smooth-scroll to `window.innerHeight` and `window.innerHeight * 2` respectively.
- Right: **Download button** -- `h-12 px-6 bg-white rounded-full`, black text. Apple icon + "Download" with ScrambleText on hover. WhileHover: scale 1.03 + bg #e2e2e6. WhileTap: scale 0.97.

**Mobile (visible below `sm`):**
- Scaled-down version: h-9 pills, rounded-[10px], smaller text (13px), logo pill animates to width 0 when menu open (spring stiffness 350, damping 28). Menu capsule expands to 100% width when open. Download button: h-9 px-3.5 rounded-full.

---

#### SECTION 2: Cinematic Text (full viewport height)

- **Background:** Video #2, autoplay muted loop, object-cover
- **Top gradient overlay:** 180px height, linear-gradient from `#010103` to transparent, z-10
- **Content:** Centered large paragraph in a `max-w-5xl` container with 3D perspective (400px)
  - Framer Motion: `rotateX(24deg) translateY(${yScaleValue}px) translateZ(15px)` where `yScaleValue` transforms from 60 to -120 based on smooth scroll progress (spring: stiffness 15, damping 32, mass 1.8). Opacity fades in from 0 to 1 between scroll progress 0.3-0.5.
  - Text: "A neural-AI interface built on the architecture of the human nervous system. SynapseX translates synaptic activity into computational intelligence. Every signal becomes measurable, structured, and visible. It continuously reconstructs internal state as a dynamic neural map. Biological noise is filtered into actionable cognitive patterns."
  - Style: `font-sans font-normal text-[22px] sm:text-[30px] md:text-[36px] lg:text-[42px] text-white leading-[1.35] tracking-[-0.02em] select-none px-6 sm:px-12 text-center`

---

#### SECTION 3: Metrics (min-h-screen)

- **Background:** Video #3, autoplay muted loop, object-cover
- **Layout:** Centered content, `pt-32 pb-32 px-6`, max-w-6xl
- **Subtitle:** "Performance Metrics" -- `text-white/40 text-[13px] sm:text-[14px] tracking-[0.2em] uppercase mb-20 text-center`. Fades in on scroll (whileInView, duration 1.2s, once, amount 0.3).
- **Metrics grid:** 3 columns on md, 1 on mobile, gap-16 md:gap-8. Each metric fades up (y:30->0, opacity, duration 0.8s, staggered 0.15s delay per item):
  - "2.4ms" -- Synaptic Latency
  - "99.7%" -- Signal Accuracy
  - "140B" -- Neural Parameters
  - Value: `text-white text-[clamp(48px,10vw,96px)] font-light tracking-[-0.04em] leading-none`
  - Label: `text-white/40 text-[13px] sm:text-[15px] mt-4 tracking-wide`

---

#### SECTION 4: Technology / Adaptive Intelligence (full viewport height)

- **Background:** Video #4, autoplay muted loop, object-cover
- **Layout:** Flexbox column, `px-8 sm:px-12 md:px-16 py-12 sm:py-16`
- **Top area:** flex-col md:flex-row md:justify-between md:items-start gap-6
  - **Left heading:** "Adaptive / Intelligence" (two lines), `text-white font-light text-[clamp(36px,8vw,72px)] leading-[0.95] tracking-[-0.03em]`. Fades up (y:40->0, duration 1.0s, whileInView once amount 0.3).
  - **Right paragraph:** "The system learns your neural baseline within 72 hours. From there, every cognitive state is mapped, predicted, and optimized in real time." `text-white/50 text-[13px] sm:text-[15px] leading-relaxed max-w-xs md:text-right md:pt-2`. Fades up (y:20->0, duration 1.0s, delay 0.2s).
- **Spacer** (`flex-1`)
- **Bottom grid:** 2 cols on mobile, 4 cols on md, gap-8 md:gap-6. Fades in on scroll (duration 1.0s, delay 0.3s). Each item staggered (y:20->0, duration 0.7s, delay i*0.1):
  1. "Cortical Mapping" -- "Real-time spatial reconstruction of active neural regions."
  2. "Signal Isolation" -- "Separates cognitive intent from biological noise."
  3. "State Prediction" -- "Anticipates cognitive transitions before they occur."
  4. "Loop Feedback" -- "Closed-loop adjustment based on outcome correlation."
  - Title: `text-white text-[14px] sm:text-[16px] font-normal mb-2`
  - Desc: `text-white/40 text-[12px] sm:text-[14px] leading-relaxed`

---

#### SECTION 5: Architecture (min-h-screen, pure black background, no video)

- Centered content, max-w-3xl, `px-6 py-32`
- **Heading block** (fades up y:30->0, duration 1.0s, whileInView once amount 0.4):
  - Subtitle: "Architecture" -- `text-white/40 text-[13px] sm:text-[14px] tracking-[0.2em] uppercase mb-8`
  - Heading: "Three layers. Zero friction." -- `text-white font-light text-[clamp(28px,6vw,56px)] leading-[1.15] tracking-[-0.02em] mb-10`
  - Description: "Sensor layer captures raw bioelectric signals. Processing layer isolates intent. Interface layer delivers structured output to any connected system." -- `text-white/45 text-[15px] sm:text-[17px] leading-relaxed max-w-xl mx-auto`
- **Layer cards** (fade in, duration 1.2s, delay 0.4s, whileInView once amount 0.4): 3 stacked cards, `mt-20 flex-col items-center gap-4`. Each card: `max-w-md h-[72px] border border-white/10 rounded-lg flex items-center justify-between px-6`
  - Left: "Layer 1/2/3" -- `text-white/30 text-[12px] tracking-[0.15em] uppercase`
  - Right: "Capture" / "Process" / "Interface" -- `text-white text-[16px] sm:text-[18px] font-light`

---

#### FOOTER

- Black background, overflow hidden
- Two-column layout (stacked on mobile): `flex-col md:flex-row min-h-[400px]`
- **Left:** Video #5, `object-cover`, fills half width (h-[300px] on mobile, auto height on md)
- **Right:** Flex column justify-between, `p-10 sm:p-16`
  - Top: SynapseXLogo (18x18px, text-white/70) + "SynapseX" text (15px font-medium text-white/70 tracking-tight), mb-8. Below: "The next evolution of human-machine interaction. Built for those who refuse to be limited by biology alone." `text-white/40 text-[14px] sm:text-[15px] leading-relaxed max-w-sm`
  - Bottom: "(c) 2026 SynapseX Labs. All rights reserved." `text-white/25 text-[12px] mt-12`

---

### Key Technical Details

- The entire app wrapper has inline style: `fontFamily: '"Space Mono", monospace'`
- All `h-screen` elements also have `h-[100dvh]` for mobile viewport compatibility
- The hero video is NOT autoplay -- it starts paused at time 0 and is scrubbed by horizontal mouse movement (delta-based, not absolute position). The seek logic chains via `seeked` event to avoid frame-dropping.
- Framer Motion `useScroll` tracks the second section with offset `["start end", "end start"]`, piped through `useSpring` (stiffness 15, damping 32, mass 1.8) then `useTransform` and `useMotionTemplate` for the 3D text rotation effect.
- No external state management, no routing, no database -- pure single-page React app.

---
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Bio-Age Dashboard"
template_id: "8c71df27-098c-4f99-8102-a32c813deda2"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Bio-Age Dashboard

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `8c71df27-098c-4f99-8102-a32c813deda2`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Bio-Age Dashboard](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/463a4c89-b026-48e5-a038-6d46d1ee7802.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
**Tech Stack:** Vite + React + TypeScript + Tailwind CSS + Lucide React icons. Font: Inter (imported from Google Fonts with weights 300-900).

---

### Background Video

Full-screen background video covering the entire viewport, auto-playing, looping, muted, inline. Fades in over 1500ms on load.

```
URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_044635_8daabe05-1a5c-491c-920f-4b0bd8f04812.mp4
```

Positioned `absolute inset-0 w-full h-full object-cover z-0`.

---

### Navigation Bar

Positioned at top with `px-5 sm:px-8 lg:px-12 pt-6 sm:pt-8 relative z-10`, using `flex items-start justify-between`.

**Left:** Logo SVG image:
```
https://polo-pecan-73837341.figma.site/_assets/v11/f73360d8fc2d33f2b5a4bfb1fa4935fca355946f.svg
```
Size: 160x40px.

**Center:** A help button (HelpCircle icon, 18px, strokeWidth 1.5) in a 36-40px round button with `bg-black/20`, absolutely positioned `left-1/2 top-8 sm:top-10 -translate-x-1/2`.

**Right:** User name "Benjamin Carter" (text-xl sm:text-3xl lg:text-[42px] font-bold, right-aligned, hidden on mobile `hidden md:block`) + a circular profile avatar (44px / 64px / 72px responsive) with image:
```
https://polo-pecan-73837341.figma.site/_assets/v11/745de561b3ebfa8634a3483efc95f21feedd96c9.png
```

---

### Layout (Content Wrapper)

`flex flex-col xl:flex-row xl:items-end xl:justify-between` positioned at bottom on XL screens (`xl:absolute xl:bottom-0 xl:left-0 xl:right-0`), with padding `px-5 sm:px-8 lg:px-12 pb-6 sm:pb-8 lg:pb-12`.

---

### Left Side: Main Age Card

**Card container:** `rounded-[24px] sm:rounded-[32px] lg:rounded-[40px]`, size `w-full sm:w-[520px] lg:w-[620px] h-[420px] sm:h-[500px] lg:h-[550px]`, centered content, `relative overflow-hidden`.

**Rotating background:** An inner div with `absolute inset-[-5%]` (overflows slightly for seamless rotation) with CSS animation `spin-slow 30s linear infinite` (full 360deg rotation). Background image:
```
https://polo-pecan-73837341.figma.site/_assets/v11/d8d9bd498347ea96ca4d675a624c8d90e06786e7.png
```
`background-size: cover; background-position: center;`

**Text overlay (z-10, centered):**
- "Estimated" + "Biological Age" - `text-gray-200 text-base sm:text-lg md:text-[22px] font-medium`
- Large count-up number starting at 0, animating to 28 over 1.8 seconds (40 steps), then incrementing by 1 every 6 seconds indefinitely. Font: `text-[72px] sm:text-[100px] lg:text-[132px] font-semibold leading-[0.85] tracking-tight font-['Inter'] tabular-nums`

---

### Below Age Card: Badge + Ruler Ticker

**Badge:** `"3 Years Younger"` in a pill shape with `border border-[#EFCE96]/50 bg-[#EFCE96]/20 text-white text-xs sm:text-sm font-medium tracking-wide px-4 sm:px-6 py-2 rounded-full`.

**Ruler Ticker:** Infinite horizontal scrolling ruler with gold-colored ticks:
- 61 ticks per set (duplicated for seamless loop)
- Every 10th tick: 26px tall. Every 5th tick: 26px tall. Others: 18px tall.
- Tick color: `rgba(239, 206, 150, 0.5)`, width 1px, rounded.
- Static center indicator tick: 40px tall, 2px wide, color `#EFCE96`, absolutely centered.
- Edge fade mask: `linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%)`
- Animation: `ticker 12s linear infinite` (translateX 0 to -50%)
- Container: `max-w-[620px] h-[40px] mt-2`

---

### Right Side: 4 Info Cards (2x2 grid)

Layout: `flex flex-col gap-4 sm:gap-[20px]`. On mobile, cards stack in pairs (2 per row via `flex-col sm:flex-row`). On XL, they stack vertically aligned right.

All cards: `w-full xl:w-[260px] h-[130px] sm:h-[144px] rounded-[16px] sm:rounded-[20px] p-4 sm:p-5 flex flex-col justify-between`.

**1. Upcoming Activities** - `bg-[#2F2F2F]/60 backdrop-blur-[52px]`, hover: `bg-[#2F2F2F]/70`.
- Title: "Upcoming Activities" (white, text-base sm:text-lg, font-semibold)
- Bottom: "4 events" (text-white/55, text-[11px] sm:text-[12px]) + black circle with ArrowRight icon

**2. Your Insights** - Background image card:
```
https://polo-pecan-73837341.figma.site/_assets/v11/94903fdf21e145cd4ba873c15fc03251c0600ee5.png
```
`background-size: cover; background-position: center;` with `hover:brightness-110`.
- Title: "Your Insights" (white)
- Bottom: "8 Risks" pill (white bg, black text, rounded-full, px-3, h-6 sm:h-7, text-[12px] sm:text-[14px]) + white circle with black ArrowRight

**3. Your Health Snapshot** - Expandable card.
- Default state: `bg-[#2F2F2F]/60 backdrop-blur-[52px]`, white text, shows title + "Recommendations" subtitle + ArrowUp in black circle.
- Expanded state (hover on desktop, click on mobile): `bg-white`, black text, height grows to 280px (desktop) or auto (mobile). Shows full recommendation text: "With a biological age of 28, your body is performing like a young, energetic you. Keep fueling it with movement, nourishing food, quality rest, and a calm mind - so you can stay strong, sharp, and unstoppable." + ArrowDown icon in `bg-[#F0F0F0]` circle. Transition: 300ms ease-in-out on all color/size changes.

**4. Action Plan** - Background image card:
```
https://polo-pecan-73837341.figma.site/_assets/v11/0c38fdb8a933b0da384a5a3f8b0d9986bb919838.png
```
`background-size: cover; background-position: center;` with `hover:brightness-110`.
- Title: "Action Plan" (white)
- Bottom: "Details" pill (white bg, black text) + white circle with black ArrowRight

---

### Animations (Intersection Observer based)

Custom `AnimatedElement` component using IntersectionObserver (threshold 0.1). Elements start invisible with a 40px offset in their specified direction (up/down/left/right) or scale(0.9), then animate to final position with:
- Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (spring-like)
- Duration: 0.8s
- Staggered delays: Nav 100-200ms, Age card 300ms, text 600ms, number 800ms, badge 1000ms, cards 500/650/800/950ms

---

### CSS Keyframes (in index.css)

```css
@keyframes ticker {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.animate-ticker { animation: ticker 12s linear infinite; }

@keyframes spin-slow {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-spin-bg { animation: spin-slow 30s linear infinite; }
```

---

### Tailwind Config Additions

```js
colors: {
  surface: { 900: '#0a0a0a', 800: '#1a1a1a', 700: '#2a2a2a', 600: '#3a3a3a' },
  gold: { 400: '#c9a96e', 500: '#b8944d', 600: '#a07d3a' },
},
fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] }
```

---

### Global Styles

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
body { background-color: #0a0a0a; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
```

---

### Dependencies

- `react` ^18.3.1
- `lucide-react` ^0.344.0 (icons used: ArrowDown, ArrowRight, ArrowUp, HelpCircle)
- `tailwindcss` ^3.4.1
- Vite + React plugin
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Apex Pulse"
template_id: "962c24c6-ffe5-4d75-a531-8d56cfa8df42"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Apex Pulse

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `962c24c6-ffe5-4d75-a531-8d56cfa8df42`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Apex Pulse](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/9b62b242-674b-4ca1-b412-b16c49fccfff.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Build a dark, cinematic drone/UAV technology landing page called **"AETHER_X"** using React + Vite + TypeScript + Tailwind CSS. The site has a scroll-driven video background and two content sections with reveal-on-scroll animations. Here is the exact specification:

---

### Font & Global Styles

- Load **Helvetica Neue Regular** via this stylesheet in `index.html`:
  ```
  https://db.onlinewebfonts.com/c/0d49fc455f4a8951a42daf952412a713?family=Helvetica+Neue+Regular
  ```
- Body: `font-family: 'Helvetica Neue Regular', 'Helvetica Neue', Helvetica, Arial, sans-serif`, background `#0a0a0a`, color `#fff`, antialiased.
- In `tailwind.config.js`, set `fontFamily.sans` and `fontFamily.mono` to `'"Flexo Soft Medium"', 'system-ui', 'sans-serif'`.
- Selection highlight: `rgba(255, 255, 255, 0.2)`.
- Page title: `AETHER_X — Where Sky Meets Machine Logic`

---

### Dependencies

Only: `react`, `react-dom`, `lucide-react`, `@supabase/supabase-js`. Tailwind + PostCSS + Autoprefixer + Vite for tooling.

---

### Architecture (5 components)

```
App.tsx
  -> ScrollVideo (fixed fullscreen background)
  -> Navbar (fixed top)
  -> main
       -> SectionOne (hero, bottom-aligned)
       -> spacer div (h-[80vh], aria-hidden)
       -> SectionTwo (full-height, justify-between)
```

---

### Component 1: `Reveal.tsx` (scroll-triggered animation wrapper)

- Props: `children`, `delay` (ms, default 0), `className`, `as` ('div' | 'span', default 'div')
- Uses `IntersectionObserver` with `threshold: 0.15`
- Animates from `translate-y-8 opacity-0` to `translate-y-0 opacity-100`
- Transition: `duration-700 ease-out will-change-transform`
- `transitionDelay` applied via inline style from `delay` prop

---

Component 2: ScrollVideo.tsx (frame-extracted scroll-synced video)
Video URL (CloudFront):

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4
Architecture principle: The <video> element starts visible as a live fallback. The rAF loop starts immediately on mount and seeks the video on scroll. Once frame extraction finishes, the canvas becomes visible and the video is hidden -- seamless handoff with zero blank frames.
Implementation:
1. State: framesReady boolean (default false). framesRef holds extracted ImageBitmap[].
2. First useEffect (frame extraction, runs once):
    * Fetch video as blob, create object URL
    * Extract up to 120 frames at max width 1280px using createImageBitmap + sequential seek-based extraction (derive frame count from video.duration * 24, clamped between 30-120)
    * On success: store frames in framesRef.current, set framesReady = true
    * On failure or cancellation: do nothing -- the video fallback stays visible permanently
    * Cleanup: set cancelled flag, revoke object URL, close all ImageBitmaps
3. Second useEffect (rAF scroll-sync loop, deps: [framesReady]):
    * Starts immediately on mount (when framesReady is still false) -- this is critical
    * Re-runs when framesReady flips to true (cleans up old loop, starts new one with frame drawing)
    * Scroll handler: maps scrollY / (scrollHeight - innerHeight) to 0-1 progress, clamped
    * Resize handler: sets canvas dimensions to clientWidth * dpr x clientHeight * dpr (dpr capped at 2)
    * Tick function (rAF):
        * Smooth interpolation: smoothed += (targetProgress - smoothed) * 0.1
        * If frames exist (frames.length > 1): map smoothed to frame index, draw to canvas with cover-fit math
        * Else if video element exists (fallback): seek video.currentTime to smoothed * duration (with seek-lock to avoid stacking seeks)
    * Cover-fit draw: scale = max(canvasW/frameW, canvasH/frameH), center the scaled frame
4. Render structure:  <div class="fixed inset-0 -z-10 bg-[#0a0a0a]">
5.   {!framesReady && <video ... visible, muted, playsInline, preload="auto", object-cover />}
6.   <canvas ... class includes 'invisible' when !framesReady, removes it when framesReady />
7.   <div class="absolute inset-0 bg-black/20" /> (overlay)
8. </div>
9.   
Key detail: The <video> is conditionally rendered (!framesReady), so it is present and visible during loading. The canvas starts with invisible class and only becomes visible when framesReady flips. This guarantees something is always on screen -- the video during load, the canvas after extraction.



### Component 3: `Navbar.tsx`

- Fixed top, z-50, flex between, responsive padding (`px-5 py-4 sm:px-8 sm:py-5 md:px-12`)
- Left: custom SVG logo (white, 32x32, scales to 36x36 on sm+). SVG path:
  ```
  M 160 88 L 194 34 L 216 0 L 256 0 L 256 40 L 221.5 93.5 L 200 128 L 256 128 L 256 256 L 96 256 L 96 168 L 64.246 220 L 40 256 L 0 256 L 0 216 L 34 162 L 56 128 L 0 128 L 0 0 L 160 0 Z
  ```
- Right: pill button "Join The Fleet" -- `rounded-full bg-white text-black uppercase tracking-wider text-xs (sm:text-sm)`, hover: `bg-white/90 scale-105`
- Both wrapped in `<Reveal>` (logo delay 0, button delay 150)

---

### Component 4: `SectionOne.tsx` (Hero)

- Full viewport height, content at bottom (`flex-col justify-end`)
- 2-column grid on sm+, single column mobile
- **Column 1:** Large heading with 3 stacked `<Reveal as="span">` lines:
  - "Relentless." (delay 100)
  - "Sovereign." (delay 250)
  - "Unyielding." (delay 400)
  - Font size: `clamp(2.5rem, 8vw, 6rem)`, font-medium, leading-[1.05], tracking-tight, drop-shadow-lg
- **Column 2:** 3 stats in a flex-wrap row (right-aligned on sm+), delay 550:
  - `360` + degree symbol + "Sensor Array"
  - `12` + degree symbol + "Thermal Scan"
  - `98` + % + "Precision"
  - Values: `text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums`
  - Labels: `text-[10px] sm:text-xs uppercase tracking-wider text-white/50`

---

### Component 5: `SectionTwo.tsx`

- Full viewport, `flex-col justify-between`, responsive padding
- **Top-right block** (self-end, max-w-sm):
  - Heading (delay 100): "Precision / built into / every line." -- `text-3xl sm:text-4xl md:text-5xl font-semibold leading-[1.1]`
  - Stat row (delay 250, mt-8): 2-column grid `[auto_1fr]`
    - Left: "99.7%" bold + label "Fleet Ready"
    - Right: paragraph "Proven in 14,000+ sorties with unmatched operational readiness and zero downtime." -- `text-xs sm:text-sm text-white/70`

- **Bottom area** (mt-auto pt-16 sm:pt-20, 2-col grid on sm+):
  - Column 1 (delay 400): 3 stats in flex row:
    - `240 km` / "Reach"
    - `85 kg` / "Capacity"
    - `42 km/h` / "Glide Speed"
  - Column 2 (delay 550, sm:ml-auto):
    - 4 stats: `grid-cols-2 sm:flex`. First stat has `border border-white/30 rounded-lg`:
      - `160 km` / "Reach"
      - `5.8 hrs` / "Endurance"
      - `52 km/h` / "Max Pace"
      - `18 kg` / "Carry"
    - 2 pill buttons below:
      - "Schedule a Call" -- outline style (`border border-white/60 rounded-full`), hover: `border-white bg-white/10`
      - "Full Details" -- solid white, text-black, hover: `bg-white/90 scale-105`

---

### Key responsive breakpoints:
- Mobile: single column, smaller text, reduced padding
- `sm` (640px): 2-column grids activate, larger text
- `md` (768px): max padding/text sizes

### Color palette:
- Background: `#0a0a0a`
- Text: white, `white/70`, `white/60`, `white/50`
- Borders: `white/30`, `white/60`
- Overlay: `black/20`

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AETHER_X — Where Sky Meets Machine Logic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://db.onlinewebfonts.com/c/0d49fc455f4a8951a42daf952412a713?family=Helvetica+Neue+Regular" rel="stylesheet" />
  <style>
    body {
      font-family: 'Helvetica Neue Regular', 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: #0a0a0a;
      color: #fff;
      -webkit-font-smoothing: antialiased;
      margin: 0;
    }
    ::selection {
      background-color: rgba(255, 255, 255, 0.2);
    }
    .reveal {
      transition: all 700ms cubic-bezier(0.33, 1, 0.68, 1);
      will-change: transform;
      transform: translateY(2rem);
      opacity: 0;
    }
    .reveal.visible {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <!-- Scroll Video Background -->
  <div id="video-bg" style="position:fixed;inset:0;z-index:-1;background:#0a0a0a;">
    <video
      id="fallback-video"
      src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4"
      muted
      playsinline
      preload="auto"
      style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;"
    ></video>
    <canvas
      id="scroll-canvas"
      style="position:absolute;inset:0;width:100%;height:100%;visibility:hidden;"
    ></canvas>
    <div style="position:absolute;inset:0;background:rgba(0,0,0,0.2);"></div>
  </div>

  <!-- Navbar -->
  <nav class="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-5 py-4 sm:px-8 sm:py-5 md:px-12">
    <div class="reveal">
      <a href="#" class="block" aria-label="Home">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 256 256" class="sm:h-9 sm:w-9">
          <path d="M 160 88 L 194 34 L 216 0 L 256 0 L 256 40 L 221.5 93.5 L 200 128 L 256 128 L 256 256 L 96 256 L 96 168 L 64.246 220 L 40 256 L 0 256 L 0 216 L 34 162 L 56 128 L 0 128 L 0 0 L 160 0 Z" fill="#ffffff"/>
        </svg>
      </a>
    </div>
    <div class="reveal" style="transition-delay:150ms;">
      <a href="#" class="group flex items-center gap-1.5 rounded-full bg-white px-5 py-2 text-xs font-medium uppercase tracking-wider text-black transition-all duration-300 hover:bg-white/90 hover:scale-105 sm:px-6 sm:py-2.5 sm:text-sm">
        Join The Fleet
      </a>
    </div>
  </nav>

  <!-- Main Content -->
  <main>
    <!-- Section One: Hero -->
    <section class="relative flex min-h-screen flex-col justify-end" style="min-height:100svh;">
      <div class="relative px-6 pb-10 sm:px-10 md:px-16 md:pb-16">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 sm:gap-12 items-end">
          <!-- Column 1: Heading -->
          <div>
            <h1 class="max-w-lg font-medium leading-[1.05] tracking-tight text-white drop-shadow-lg" style="font-size:clamp(2.5rem,8vw,6rem);">
              <span class="block reveal" style="transition-delay:100ms;">Relentless.</span>
              <span class="block reveal" style="transition-delay:250ms;">Sovereign.</span>
              <span class="block reveal" style="transition-delay:400ms;">Unyielding.</span>
            </h1>
          </div>
          <!-- Column 2: Stats -->
          <div class="reveal" style="transition-delay:550ms;">
            <div class="flex flex-wrap items-end gap-6 sm:gap-10 md:gap-14 sm:justify-end">
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">360<span class="text-lg text-white/70 sm:text-xl md:text-2xl">&deg;</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Sensor Array</span>
              </div>
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">12<span class="text-lg text-white/70 sm:text-xl md:text-2xl">&deg;</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Thermal Scan</span>
              </div>
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">98<span class="text-lg text-white/70 sm:text-xl md:text-2xl">%</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Precision</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Spacer -->
    <div aria-hidden="true" style="height:80vh;"></div>

    <!-- Section Two -->
    <section class="relative flex min-h-screen flex-col justify-between px-6 py-10 sm:px-10 sm:py-14 md:px-16 md:py-20" style="min-height:100svh;">
      <!-- Top right area -->
      <div class="self-end w-full max-w-sm">
        <div class="reveal" style="transition-delay:100ms;">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold leading-[1.1] tracking-tight text-white">
            Precision<br/>built into<br/>every line.
          </h2>
        </div>
        <div class="reveal mt-8" style="transition-delay:250ms;">
          <div class="grid gap-3" style="grid-template-columns:auto 1fr;">
            <div class="flex flex-col">
              <span class="text-3xl sm:text-4xl font-bold text-white tabular-nums">99.7<span class="text-lg text-white/60">%</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Fleet Ready</span>
            </div>
            <div class="flex flex-col justify-center">
              <p class="text-xs sm:text-sm leading-relaxed text-white/70">Proven in 14,000+ sorties with unmatched operational readiness and zero downtime.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom area -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 sm:gap-12 mt-auto pt-16 sm:pt-20">
        <!-- Column 1: 3 stats -->
        <div class="reveal" style="transition-delay:400ms;">
          <div class="flex items-end gap-6 sm:gap-10">
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">240<span class="ml-0.5 text-sm sm:text-base text-white/60">km</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Reach</span>
            </div>
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">85<span class="ml-0.5 text-sm sm:text-base text-white/60">kg</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Capacity</span>
            </div>
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">42<span class="ml-0.5 text-sm sm:text-base text-white/60">km/h</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Glide Speed</span>
            </div>
          </div>
        </div>

        <!-- Column 2: 4 stats + buttons -->
        <div class="reveal sm:ml-auto" style="transition-delay:550ms;">
          <div class="flex flex-col gap-6">
            <!-- 4 stats -->
            <div class="grid grid-cols-2 sm:flex sm:items-stretch gap-0">
              <div class="flex flex-col px-3 sm:px-4 py-3 border border-white/30 rounded-lg">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">160<span class="ml-0.5 text-xs text-white/60">km</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Reach</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">5.8<span class="ml-0.5 text-xs text-white/60">hrs</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Endurance</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">52<span class="ml-0.5 text-xs text-white/60">km/h</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Max Pace</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">18<span class="ml-0.5 text-xs text-white/60">kg</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Carry</span>
              </div>
            </div>
            <!-- Buttons -->
            <div class="flex items-center gap-3 mt-2">
              <a href="#" class="rounded-full border border-white/60 px-5 sm:px-6 py-2.5 text-[11px] sm:text-xs font-medium uppercase tracking-wider text-white transition-all duration-300 hover:border-white hover:bg-white/10">Schedule a Call</a>
              <a href="#" class="rounded-full bg-white px-5 sm:px-6 py-2.5 text-[11px] sm:text-xs font-medium uppercase tracking-wider text-black transition-all duration-300 hover:bg-white/90 hover:scale-105">Full Details</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    // --- Reveal Animation (IntersectionObserver) ---
    const revealEls = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach((el) => revealObserver.observe(el));

    // --- Scroll-Synced Video with Frame Extraction ---
    (function() {
      const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4';
      const MAX_FRAMES = 120;
      const MAX_FRAME_WIDTH = 1280;

      const video = document.getElementById('fallback-video');
      const canvas = document.getElementById('scroll-canvas');
      const ctx = canvas.getContext('2d');

      let frames = [];
      let framesReady = false;
      let targetProgress = 0;
      let smoothed = 0;
      let lastFrameIndex = -1;
      let videoSeeking = false;

      // Scroll handler
      function onScroll() {
        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        targetProgress = scrollable > 0 ? Math.min(Math.max(window.scrollY / scrollable, 0), 1) : 0;
      }

      // Resize canvas
      function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(canvas.clientWidth * dpr);
        canvas.height = Math.round(canvas.clientHeight * dpr);
        lastFrameIndex = -1;
      }

      // Draw frame with cover-fit
      function drawCover(frame) {
        const cw = canvas.width;
        const ch = canvas.height;
        const s = Math.max(cw / frame.width, ch / frame.height);
        const dw = frame.width * s;
        const dh = frame.height * s;
        ctx.drawImage(frame, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
      }

      // Seek lock
      video.addEventListener('seeked', function() { videoSeeking = false; });

      // rAF loop - starts immediately, uses video fallback until frames ready
      function tick() {
        requestAnimationFrame(tick);
        smoothed += (targetProgress - smoothed) * 0.1;

        if (frames.length > 1) {
          const index = Math.min(Math.round(smoothed * (frames.length - 1)), frames.length - 1);
          if (index !== lastFrameIndex) {
            lastFrameIndex = index;
            drawCover(frames[index]);
          }
        } else if (video && video.duration && !videoSeeking) {
          const t = smoothed * video.duration;
          if (Math.abs(video.currentTime - t) > 0.001) {
            videoSeeking = true;
            video.currentTime = t;
          }
        }
      }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', resize);
      resize();
      onScroll();
      requestAnimationFrame(tick);

      // Frame extraction (async, runs in background)
      async function extractFrames(src) {
        const tempVideo = document.createElement('video');
        tempVideo.src = src;
        tempVideo.muted = true;
        tempVideo.playsInline = true;
        tempVideo.preload = 'auto';

        await new Promise(function(resolve, reject) {
          tempVideo.onloadedmetadata = resolve;
          tempVideo.onerror = function() { reject(new Error('video load failed')); };
        });

        const scale = Math.min(1, MAX_FRAME_WIDTH / tempVideo.videoWidth);
        const w = Math.round(tempVideo.videoWidth * scale);
        const h = Math.round(tempVideo.videoHeight * scale);
        const count = Math.min(Math.max(Math.round(tempVideo.duration * 24), 30), MAX_FRAMES);
        const extracted = [];

        for (let i = 0; i < count; i++) {
          const t = (i / (count - 1)) * Math.max(tempVideo.duration - 0.05, 0);
          await new Promise(function(resolve) {
            tempVideo.onseeked = resolve;
            tempVideo.currentTime = t;
          });
          extracted.push(await createImageBitmap(tempVideo, { resizeWidth: w, resizeHeight: h }));
        }

        tempVideo.removeAttribute('src');
        tempVideo.load();
        return extracted;
      }

      // Start extraction, switch to canvas when ready
      (async function() {
        try {
          const res = await fetch(VIDEO_URL);
          if (!res.ok) return;
          const blob = await res.blob();
          const objectUrl = URL.createObjectURL(blob);
          const extracted = await extractFrames(objectUrl);
          URL.revokeObjectURL(objectUrl);

          if (extracted.length < 2) {
            extracted.forEach(function(f) { f.close(); });
            return;
          }

          frames = extracted;
          framesReady = true;
          // Switch display: show canvas, hide video
          canvas.style.visibility = 'visible';
          video.style.display = 'none';
        } catch(e) {
          // Video fallback stays visible permanently
        }
      })();
    })();
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Obsidian Hero"
template_id: "9813340a-c8f4-44e8-a5a9-d61af1c280d9"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Obsidian Hero

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `9813340a-c8f4-44e8-a5a9-d61af1c280d9`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero



### 🖼 Прев'ю:
![Obsidian Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/f09c875f-1312-4452-a2cf-668df547df05.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a single-page architecture / design studio landing page using React, Vite, TypeScript, and Tailwind CSS. The page is a fullscreen hero with a looping background video, overlaid navigation, headline, and two staggered project cards.

---

**TECH STACK:**
- React 18 + TypeScript + Vite
- Tailwind CSS 3
- lucide-react (icons: Grid3X3, Menu, X)
- No other dependencies

---

**FONT:**
- Load "Lexend" from `https://db.onlinewebfonts.com/c/42dbf00de1681d38477679d3eadad56a?family=Lexend` via a `<link>` in index.html
- In tailwind.config.js, extend fontFamily with: `vilsuve: ['Lexend', 'sans-serif']`

---

**LOGO (inline SVG, white, 24x24):**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor">
  <path d="M 156 0 C 211.228 0 256 44.772 256 100 L 256 256 L 100 256 C 44.772 256 0 211.228 0 156 L 0 0 Z M 80 80 C 80 133.019 122.981 176 176 176 C 176 122.981 133.019 80 80 80 Z" />
</svg>
```
Use this as a React component `<Logo className="w-6 h-6 text-white" />` (uses `fill="currentColor"`).

---

**BACKGROUND VIDEO:**
- URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_054830_07627566-fd88-4b82-9ee8-b5d78b1c4f36.mp4`
- Attributes: autoPlay, muted, loop, playsInline
- Positioned: absolute inset-0, w-full h-full, object-cover
- Parent container: relative h-screen w-full overflow-hidden bg-black

---

**LAYOUT STRUCTURE (all within the fullscreen container):**

1. **Navigation bar** (z-10, relative):
   - Left: Logo + desktop nav links ("Work" active/white, "Studio" and "Connect" white/70 with hover:white)
   - Right: "Enter" text (desktop only) + hamburger Menu icon
   - Padding: px-5 sm:px-6 md:px-12, py-5 md:py-6
   - Desktop nav links hidden on mobile; hamburger shows on mobile (md:hidden), also visible on desktop

2. **Main content area** (flex-1, relative, same horizontal padding):
   - **Hero text block** (top-left, pt-4 sm:pt-8 md:pt-16, max-w-lg):
     - H1: "Shape your\nbold spaces" - font-vilsuve, text-3xl sm:text-4xl md:text-6xl lg:text-7xl, text-white, leading-[0.95], tracking-tight
     - Paragraph: "Designing bold forms, sculpting purposeful structures, and building a timeless legacy for all." - text-white/60, text-xs sm:text-sm md:text-base, max-w-xs, leading-relaxed
     - Button: "Our Projects" with Grid3X3 icon - border border-white/30, rounded-full, px-5 sm:px-6 py-2.5 sm:py-3, hover:bg-white/10

   - **Two staggered cards** (absolute bottom-right):
     - Container: absolute bottom-6 sm:bottom-8 md:bottom-12 right-5 sm:right-6 md:right-12
     - Grid: grid grid-cols-2 gap-3 sm:gap-4 md:gap-5
     - Card 1: col-start-1 row-start-1, self-end, w-36 sm:w-44 md:w-52 lg:w-60
       - Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_052633_1cc62234-04fe-4fb5-905e-66254dd3c5db.png&w=1280&q=85`
       - Label: "CRAFT" (uppercase, text-white/60, text-[10px] sm:text-xs)
       - Title: "Spaces shaped with intention." (text-sm sm:text-base md:text-lg, font-semibold)
       - Grid3X3 icon bottom-right (text-white/70)
     - Card 2: col-start-2 row-start-2, w-36 sm:w-44 md:w-52 lg:w-60
       - Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_052653_54120660-1330-4f38-92ab-a6ba7ac15397.png&w=1280&q=85`
       - Label: "ARCVAULT" (same style)
       - Title: "Form in Stone" (text-base sm:text-xl md:text-2xl, font-semibold)
       - Grid3X3 icon bottom-right
     - Both cards: rounded-xl sm:rounded-2xl, aspect-square, gradient overlay (bg-gradient-to-t from-black/60 via-black/20 to-transparent), content justified to bottom

   - **Floating labels** (lg only, absolute positioned on background):
     - "Concrete Atrium / 282 M" at top-[25%] right-[30%] - small white dot + text-xs
     - "Brutalist Arc / 67%" at top-[45%] right-[15%] - same style

   - **Scroll indicator** (absolute bottom-8 left-1/2, hidden md:flex):
     - Text "Scroll" - text-white/40, text-[10px], uppercase, tracking-[0.3em], vertical writing mode (writingMode: 'vertical-rl'), rotated 180deg

3. **Mobile menu overlay** (fixed inset-0 z-50):
   - Toggled by `menuOpen` state
   - Backdrop: bg-black/90 backdrop-blur-xl, opacity transition 500ms
   - Content slides in from top (-translate-y-8 to translate-y-0), 500ms ease-out
   - Header: Logo left, X close button right
   - Links: "Work", "Studio", "Connect", "Enter" - text-4xl, font-vilsuve, font-light, staggered entrance (each link delayed 75ms apart starting at 150ms), border-b border-white/10
   - Footer: "Crafting bold spaces for an intentional world." - text-white/40 text-xs, delayed 450ms
   - pointer-events-none when closed, pointer-events-auto when open

---

**CSS (index.css):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

No additional custom CSS needed.

---

**KEY DESIGN DETAILS:**
- Entire page is black with the video covering the background
- All text is white with various opacity levels (white, white/70, white/60, white/50, white/40)
- Fully responsive: mobile-first breakpoints at sm, md, lg
- Cards use a CSS grid stagger pattern (not absolute positioning relative to each other)
- Transitions on hover states and menu animations
- No scrolling on the page (h-screen overflow-hidden)

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Shape Your Bold Spaces</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://db.onlinewebfonts.com/c/42dbf00de1681d38477679d3eadad56a?family=Lexend" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            vilsuve: ['Lexend', 'sans-serif'],
          },
        },
      },
    }
  </script>
</head>
<body class="m-0 p-0">
  <div id="app" class="relative h-screen w-full overflow-hidden bg-black">
    <!-- Background Video -->
    <video autoplay muted loop playsinline class="absolute inset-0 w-full h-full object-cover">
      <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_054830_07627566-fd88-4b82-9ee8-b5d78b1c4f36.mp4" type="video/mp4" />
    </video>

    <!-- Mobile Menu Overlay -->
    <div id="mobile-menu" class="fixed inset-0 z-50 pointer-events-none transition-all duration-500 ease-in-out">
      <!-- Backdrop -->
      <div id="menu-backdrop" class="absolute inset-0 bg-black/90 backdrop-blur-xl opacity-0 transition-opacity duration-500" onclick="closeMenu()"></div>
      <!-- Menu Content -->
      <div id="menu-content" class="relative z-10 flex flex-col h-full opacity-0 -translate-y-8 transition-all duration-500 ease-out">
        <!-- Menu Header -->
        <div class="flex items-center justify-between px-6 py-6">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor" class="w-6 h-6 text-white">
            <path d="M 156 0 C 211.228 0 256 44.772 256 100 L 256 256 L 100 256 C 44.772 256 0 211.228 0 156 L 0 0 Z M 80 80 C 80 133.019 122.981 176 176 176 C 176 122.981 133.019 80 80 80 Z" />
          </svg>
          <button onclick="closeMenu()" class="text-white hover:opacity-80 transition-opacity">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <!-- Menu Links -->
        <div class="flex-1 flex flex-col justify-center px-8 gap-2">
          <a href="#" class="menu-link text-white text-4xl font-vilsuve font-light py-3 border-b border-white/10 opacity-0 -translate-x-8 transition-all duration-500 ease-out" style="transition-delay: 0ms" onclick="closeMenu()">Work</a>
          <a href="#" class="menu-link text-white text-4xl font-vilsuve font-light py-3 border-b border-white/10 opacity-0 -translate-x-8 transition-all duration-500 ease-out" style="transition-delay: 0ms" onclick="closeMenu()">Studio</a>
          <a href="#" class="menu-link text-white text-4xl font-vilsuve font-light py-3 border-b border-white/10 opacity-0 -translate-x-8 transition-all duration-500 ease-out" style="transition-delay: 0ms" onclick="closeMenu()">Connect</a>
          <a href="#" class="menu-link text-white text-4xl font-vilsuve font-light py-3 border-b border-white/10 opacity-0 -translate-x-8 transition-all duration-500 ease-out" style="transition-delay: 0ms" onclick="closeMenu()">Enter</a>
        </div>
        <!-- Menu Footer -->
        <div id="menu-footer" class="px-8 pb-10 opacity-0 translate-y-4 transition-all duration-500 ease-out" style="transition-delay: 0ms">
          <p class="text-white/40 text-xs">Crafting bold spaces for an intentional world.</p>
        </div>
      </div>
    </div>

    <!-- Content Layer -->
    <div class="relative z-10 flex flex-col h-full">
      <!-- Navigation -->
      <nav class="flex items-center justify-between px-5 sm:px-6 md:px-12 py-5 md:py-6">
        <div class="flex items-center gap-8 md:gap-12">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor" class="w-6 h-6 text-white">
            <path d="M 156 0 C 211.228 0 256 44.772 256 100 L 256 256 L 100 256 C 44.772 256 0 211.228 0 156 L 0 0 Z M 80 80 C 80 133.019 122.981 176 176 176 C 176 122.981 133.019 80 80 80 Z" />
          </svg>
          <div class="hidden md:flex items-center gap-8">
            <a href="#" class="text-white text-sm font-medium hover:opacity-80 transition-opacity">Work</a>
            <a href="#" class="text-white/70 text-sm hover:text-white transition-colors">Studio</a>
            <a href="#" class="text-white/70 text-sm hover:text-white transition-colors">Connect</a>
          </div>
        </div>
        <div class="flex items-center gap-6">
          <span class="text-white text-sm hidden md:block">Enter</span>
          <button onclick="openMenu()" class="text-white hover:opacity-80 transition-opacity md:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
          <button onclick="openMenu()" class="text-white hover:opacity-80 transition-opacity hidden md:block">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
        </div>
      </nav>

      <!-- Main Content -->
      <div class="flex-1 relative px-5 sm:px-6 md:px-12">
        <!-- Heading and subtext -->
        <div class="pt-4 sm:pt-8 md:pt-16">
          <div class="flex flex-col gap-4 sm:gap-6 md:gap-8 max-w-lg">
            <h1 class="font-vilsuve text-3xl sm:text-4xl md:text-6xl lg:text-7xl text-white leading-[0.95] tracking-tight">
              Shape your<br>bold spaces
            </h1>
            <p class="text-white/60 text-xs sm:text-sm md:text-base max-w-xs leading-relaxed">
              Designing bold forms, sculpting purposeful structures, and building a timeless legacy for all.
            </p>
            <button class="flex items-center gap-3 border border-white/30 rounded-full px-5 sm:px-6 py-2.5 sm:py-3 w-fit text-white text-xs sm:text-sm hover:bg-white/10 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
              Our Projects
            </button>
          </div>
        </div>

        <!-- Stacked cards - grid layout -->
        <div class="absolute bottom-6 sm:bottom-8 md:bottom-12 right-5 sm:right-6 md:right-12">
          <div class="grid grid-cols-2 gap-3 sm:gap-4 md:gap-5">
            <!-- Card 1 -->
            <div class="col-start-1 row-start-1 w-36 sm:w-44 md:w-52 lg:w-60 self-end">
              <div class="relative rounded-xl sm:rounded-2xl overflow-hidden aspect-square">
                <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_052633_1cc62234-04fe-4fb5-905e-66254dd3c5db.png&w=1280&q=85" alt="Nature" class="absolute inset-0 w-full h-full object-cover" />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                <div class="relative z-10 flex flex-col justify-end h-full p-3 sm:p-4 md:p-5">
                  <span class="text-white/60 text-[10px] sm:text-xs uppercase tracking-wider">Craft</span>
                  <h3 class="text-white text-sm sm:text-base md:text-lg font-semibold mt-1 leading-tight">Spaces shaped with intention.</h3>
                  <div class="mt-2 sm:mt-3 flex justify-end">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:w-5 sm:h-5 text-white/70"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
                  </div>
                </div>
              </div>
            </div>
            <!-- Card 2 -->
            <div class="col-start-2 row-start-2 w-36 sm:w-44 md:w-52 lg:w-60">
              <div class="relative rounded-xl sm:rounded-2xl overflow-hidden aspect-square">
                <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_052653_54120660-1330-4f38-92ab-a6ba7ac15397.png&w=1280&q=85" alt="EcoStove" class="absolute inset-0 w-full h-full object-cover" />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                <div class="relative z-10 flex flex-col justify-end h-full p-3 sm:p-4 md:p-5">
                  <span class="text-white/60 text-[10px] sm:text-xs uppercase tracking-wider">ArcVault</span>
                  <h3 class="text-white text-base sm:text-xl md:text-2xl font-semibold mt-1">Form in Stone</h3>
                  <div class="mt-2 sm:mt-3 flex justify-end">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:w-5 sm:h-5 text-white/70"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating labels -->
        <div class="hidden lg:block absolute top-[25%] right-[30%]">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-white/60"></div>
            <div>
              <p class="text-white text-xs font-medium">Concrete Atrium</p>
              <p class="text-white/50 text-xs">282 M</p>
            </div>
          </div>
        </div>
        <div class="hidden lg:block absolute top-[45%] right-[15%]">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-white/60"></div>
            <div>
              <p class="text-white text-xs font-medium">Brutalist Arc</p>
              <p class="text-white/50 text-xs">67%</p>
            </div>
          </div>
        </div>

        <!-- Scroll indicator -->
        <div class="absolute bottom-8 left-1/2 -translate-x-1/2 hidden md:flex flex-col items-center gap-2">
          <span class="text-white/40 text-[10px] uppercase tracking-[0.3em] rotate-180" style="writing-mode: vertical-rl;">Scroll</span>
        </div>
      </div>
    </div>
  </div>

  <script>
    function openMenu() {
      const menu = document.getElementById('mobile-menu');
      const backdrop = document.getElementById('menu-backdrop');
      const content = document.getElementById('menu-content');
      const links = document.querySelectorAll('.menu-link');
      const footer = document.getElementById('menu-footer');

      menu.classList.remove('pointer-events-none');
      menu.classList.add('pointer-events-auto');
      backdrop.classList.remove('opacity-0');
      backdrop.classList.add('opacity-100');
      content.classList.remove('opacity-0', '-translate-y-8');
      content.classList.add('opacity-100', 'translate-y-0');

      links.forEach((link, i) => {
        link.style.transitionDelay = (150 + i * 75) + 'ms';
        setTimeout(() => {
          link.classList.remove('opacity-0', '-translate-x-8');
          link.classList.add('opacity-100', 'translate-x-0');
        }, 10);
      });

      footer.style.transitionDelay = '450ms';
      setTimeout(() => {
        footer.classList.remove('opacity-0', 'translate-y-4');
        footer.classList.add('opacity-100', 'translate-y-0');
      }, 10);
    }

    function closeMenu() {
      const menu = document.getElementById('mobile-menu');
      const backdrop = document.getElementById('menu-backdrop');
      const content = document.getElementById('menu-content');
      const links = document.querySelectorAll('.menu-link');
      const footer = document.getElementById('menu-footer');

      menu.classList.remove('pointer-events-auto');
      menu.classList.add('pointer-events-none');
      backdrop.classList.remove('opacity-100');
      backdrop.classList.add('opacity-0');
      content.classList.remove('opacity-100', 'translate-y-0');
      content.classList.add('opacity-0', '-translate-y-8');

      links.forEach((link) => {
        link.style.transitionDelay = '0ms';
        link.classList.remove('opacity-100', 'translate-x-0');
        link.classList.add('opacity-0', '-translate-x-8');
      });

      footer.style.transitionDelay = '0ms';
      footer.classList.remove('opacity-100', 'translate-y-0');
      footer.classList.add('opacity-0', 'translate-y-4');
    }
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Investment Gate"
template_id: "a68d437b-7292-4c07-a94b-3aa63748dcd5"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Investment Gate

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `a68d437b-7292-4c07-a94b-3aa63748dcd5`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Investment Gate](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/ba31559e-726e-4a5c-b156-70a2f93271af.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a luxury real estate landing page called "VELORA" using React, TypeScript, Vite, and Tailwind CSS. The page has 3 main parts: a Splash Screen, a Hero Section with a morphing bottom navbar and popup menu, and a Scroll-Driven Gallery Overlay. Use `lucide-react` for icons. No other UI libraries.

---

### FONTS

Load these two fonts in `index.html` `<head>`:

1. **Haboro Norm Regular** (serif, used for brand name and headings):
   ```html
   <link href="https://db.onlinewebfonts.com/c/cc69fe194f7ed41628d4628f37a10a21?family=Haboro+Norm+Regular" rel="stylesheet">
   ```

2. **Geist** (sans-serif, weights 300/400/500/600, used for body text and UI elements):
   ```html
   <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap" rel="stylesheet">
   ```

Register them in `tailwind.config.js`:
```js
fontFamily: {
  haboro: ['"Haboro Norm Regular"', 'serif'],
  geist: ['Geist', 'sans-serif'],
}
```

---

### GLOBAL CSS (`index.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Geist', sans-serif;
  overflow-x: hidden;
}

@keyframes menuSlideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

@keyframes menuSlideDown {
  from {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(40px) scale(0.95);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes menuItemSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-open {
  animation: menuSlideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.menu-close {
  animation: menuSlideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.menu-overlay-open {
  animation: fadeIn 0.3s ease forwards;
}

.menu-overlay-close {
  animation: fadeOut 0.3s ease forwards;
}

.menu-item-enter {
  animation: menuItemSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
```

---

### SECTION 1: SPLASH SCREEN (`SplashScreen.tsx`)

A fixed full-screen black overlay (`z-[9999]`) that plays a video once. When the video ends, the screen fades out over 700ms and then unmounts.

- **Container**: `fixed inset-0 z-[9999] bg-black flex items-center`, with a `transition-opacity duration-700` that goes to `opacity-0` when fading.
- **Video**: Absolutely positioned at `top-[20%] left-[30%]` on mobile, `md:left-[55%] md:-translate-x-1/2` on desktop. Sizes: `w-[320px]` mobile, `sm:w-[390px]`, `md:w-[750px]`. `aspect-video object-contain`. Autoplay, muted, playsInline. No loop.
- **Video URL**: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_205729_0e6fae4e-5fc0-42d0-b49a-b88d85ede0b2.mp4`
- **Behavior**: On `onEnded`, set fading state to true. After 800ms timeout, call `onComplete` to remove the splash.

---

### SECTION 2: HERO SECTION (in `App.tsx`)

The entire hero is a `<section>` with `fixed inset-0 h-screen w-full overflow-hidden z-0`.

#### 2A. Video Background
- Full-screen looping video: `absolute inset-0 w-full h-full object-cover`
- **Video URL**: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_210218_173f8eba-17ff-4e27-972b-d128af25bf49.mp4`
- autoPlay, muted, loop, playsInline

#### 2B. Top Navbar
- `relative z-10 flex items-center justify-between px-4 sm:px-6 md:px-12 pt-4 sm:pt-6 md:pt-8`
- Left: empty spacer `w-8 sm:w-32 md:w-40`
- Center: Brand name "VELORA" in `font-haboro text-white text-lg sm:text-xl md:text-2xl tracking-[0.2em] uppercase`
- Right: spacer same width containing a "GET IN TOUCH" button (`hidden sm:block bg-white text-black px-4 md:px-6 py-2 md:py-2.5 text-xs md:text-sm font-geist font-medium tracking-wide hover:bg-white/90 transition-colors duration-200`)

#### 2C. Hero Heading (centered)
- Container: `flex-1 flex items-center justify-center px-4 sm:px-6`
- Text: `font-haboro text-white text-center text-2xl sm:text-3xl md:text-5xl lg:text-6xl xl:text-7xl leading-[1.1] tracking-wide uppercase max-w-5xl`
- Content:
  ```
  PREMIUM REAL ESTATE FOR
  INVESTORS BEYOND OWNERSHIP
  ```
  (line break between the two lines)

#### 2D. Bottom Morphing Navbar
- Centered at the bottom: `flex justify-center pb-4 sm:pb-6 md:pb-10`
- The bar is a black rectangle that morphs between two states:
  - **Expanded** (menu closed): width `280px`, max-width `85vw`. Contains:
    - Left: `Home` icon from lucide-react (`w-5 h-5 text-amber-500`)
    - Center: "HOME" text (`font-geist text-white text-sm tracking-[0.15em] uppercase font-medium`)
    - Right: Hamburger button (two horizontal white lines, `w-6 h-[1.5px] bg-white`, one at `top-[8px]` and one at `top-[15px]`)
  - **Collapsed** (menu open): morphs to `56px` square showing an X close button (two `w-5 h-[1.5px] bg-white` lines rotated 45deg and -45deg)
- Transition: `transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]`

#### 2E. Menu Popup
- Triggered by hamburger click.
- **Overlay**: `fixed inset-0 z-20`, with `menu-overlay-open`/`menu-overlay-close` CSS animation classes.
- **Menu panel**: `fixed z-30 left-1/2 bottom-[80px] sm:bottom-[100px] md:bottom-[120px] w-[92vw] max-w-[480px] bg-black rounded-lg p-6 sm:p-8 md:p-10`
  - Uses `menu-open`/`menu-close` CSS classes (translateX(-50%) centered via those animations).
  - Header: "MENU" label (`font-geist text-neutral-400 text-xs tracking-[0.2em] uppercase mb-6`)
  - Menu items list (`space-y-1`): `['About', 'Properties', 'Work', 'Partnership', 'Contact']`
    - Each item: `font-haboro text-white text-2xl md:text-3xl lg:text-4xl hover:text-neutral-300 transition-colors duration-200 block py-1`
    - Each `<li>` has class `menu-item-enter` with staggered `animationDelay: ${i * 60 + 100}ms` and initial `opacity: 0`
  - Footer section: `mt-8 pt-6 border-t border-neutral-700/50 space-y-3`
    - "Private line" row: label `font-geist text-neutral-400 text-sm`, value `font-geist text-white text-sm` showing `+44 020 8156 7290`
    - "Email" row: same style, showing `hello@velora.com`
  - CTA button: `w-full mt-6 bg-white text-black py-3 font-geist text-sm font-medium tracking-wide hover:bg-neutral-100 transition-colors duration-200` with text "GET IN TOUCH"
- **Close behavior**: Sets `isClosing` to true, waits 300ms, then unmounts menu.

---

### SECTION 3: SCROLL-DRIVEN GALLERY (`ScrollGallery.tsx`)

The entire app container has `bg-black h-[900vh]` to create scroll space. The gallery is a `fixed inset-0 z-10 pointer-events-none` overlay that animates based on scroll progress (0 to 1).

#### Scroll Phase Breakdown:

| Progress Range | What Happens |
|---|---|
| 0.00 - 0.06 | A thin black vertical line appears at center, grows from 0px to 50px wide, full height |
| 0.06 - 0.16 | The line expands width to fill the entire viewport (cubic ease-in-out) |
| 0.16 - 0.34 | Image 1 scales from center (scale 0.2 to 1.0, opacity fades in quickly) |
| 0.34 - 0.50 | Image 2 scales from center (same animation, stacked on top) |
| 0.50 - 0.64 | Image 3 scales from center (same animation, stacked on top) |
| 0.64 - 0.78 | Black text screen scales from center (same scale animation). Shows text: "Access exceptional real estate opportunities **worldwide.**" (worldwide in amber-500) |
| 0.78 - 0.90 | Background morphs from black to white (RGB interpolation). The black text fades out. |
| 0.90 - 1.00 | White screen with text: "Built on trust and **expertise.**" (expertise in amber-500) fades in |

#### Image Scale Animation Formula:
- `scale = 0.2 + progress * 0.8`
- `opacity = Math.min(1, progress * 4)` (quick fade-in)

#### Image Styling:
- Mobile: `w-[85vw] h-auto max-w-[900px] aspect-[16/10]` with `rounded-lg`
- Desktop (`sm:`): `w-full h-full max-w-none aspect-auto` with no rounding (`rounded-none`)
- All images: `object-cover`

#### Image URLs (in order):
1. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_211418_dbb8d807-3cfb-4c26-b1df-02fb0c23cc7d.png&w=1280&q=85`
2. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_211445_ba965dcd-97d6-4644-b390-d4744078ec6c.png&w=1280&q=85`
3. `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_212326_f5e78786-d7bb-40c5-abac-cd3c0be37d90.png&w=1280&q=85`

#### Text Screens Typography:
- Both text screens: `font-geist font-light text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-center leading-[1.3] max-w-3xl px-6`
- Black screen text color: `text-white`
- White screen text color: `text-neutral-800`
- Accent word color: `text-amber-500`

#### Width Expansion Easing (Phase 2):
```js
const eased = expandProgress < 0.5
  ? 4 * expandProgress * expandProgress * expandProgress
  : 1 - Math.pow(-2 * expandProgress + 2, 3) / 2;
```

#### Morph (black to white) formula:
```js
backgroundColor: `rgb(${Math.round(morphProgress * 255)}, ${Math.round(morphProgress * 255)}, ${Math.round(morphProgress * 255)})`
```

---

### PAGE STRUCTURE

```
App.tsx
  - bg-black h-[900vh]
  - SplashScreen (conditional, unmounts after video ends)
  - Hero Section (fixed, z-0)
    - Video background (looping)
    - Navbar + Heading + Bottom bar
    - Menu popup (conditional)
  - ScrollGallery (fixed, z-10, pointer-events-none)
```

---

### TECH STACK
- Vite + React 18 + TypeScript
- Tailwind CSS 3.4
- lucide-react (only the `Home` icon)
- No other dependencies needed

---

### PAGE TITLE
`VELORA - Premium Real Estate`

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VELORA - Premium Real Estate</title>
  <link href="https://db.onlinewebfonts.com/c/cc69fe194f7ed41628d4628f37a10a21?family=Haboro+Norm+Regular" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Geist', sans-serif; overflow-x: hidden; background: #000; }
    .font-haboro { font-family: 'Haboro Norm Regular', serif; }
    .font-geist { font-family: 'Geist', sans-serif; }

    /* Splash Screen */
    #splash {
      position: fixed; inset: 0; z-index: 9999; background: #000;
      display: flex; align-items: center;
      transition: opacity 0.7s ease;
    }
    #splash.fading { opacity: 0; }
    #splash video {
      position: absolute; top: 20%; left: 30%;
      width: 320px; aspect-ratio: 16/9; object-fit: contain;
    }
    @media (min-width: 640px) {
      #splash video { width: 390px; }
    }
    @media (min-width: 768px) {
      #splash video { left: 55%; transform: translateX(-50%); width: 750px; }
    }

    /* Hero Section */
    #hero {
      position: fixed; inset: 0; height: 100vh; width: 100%; overflow: hidden; z-index: 0;
    }
    #hero-video {
      position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
    }
    #hero-content {
      position: relative; z-index: 10; display: flex; flex-direction: column; height: 100%;
    }

    /* Navbar */
    #navbar {
      display: flex; align-items: center; justify-content: space-between;
      padding: 1rem 1rem 0;
    }
    @media (min-width: 640px) { #navbar { padding: 1.5rem 1.5rem 0; } }
    @media (min-width: 768px) { #navbar { padding: 2rem 3rem 0; } }

    .nav-spacer { width: 2rem; }
    @media (min-width: 640px) { .nav-spacer { width: 8rem; } }
    @media (min-width: 768px) { .nav-spacer { width: 10rem; } }

    #brand-name {
      color: #fff; letter-spacing: 0.2em; text-transform: uppercase;
      font-size: 1.125rem;
    }
    @media (min-width: 640px) { #brand-name { font-size: 1.25rem; } }
    @media (min-width: 768px) { #brand-name { font-size: 1.5rem; } }

    #cta-btn {
      display: none; background: #fff; color: #000;
      padding: 0.5rem 1rem; font-size: 0.75rem;
      font-weight: 500; letter-spacing: 0.05em; border: none; cursor: pointer;
      transition: background 0.2s;
    }
    #cta-btn:hover { background: rgba(255,255,255,0.9); }
    @media (min-width: 640px) { #cta-btn { display: block; } }
    @media (min-width: 768px) { #cta-btn { padding: 0.625rem 1.5rem; font-size: 0.875rem; } }

    /* Hero Heading */
    #hero-heading-wrap {
      flex: 1; display: flex; align-items: center; justify-content: center; padding: 0 1rem;
    }
    #hero-heading {
      color: #fff; text-align: center; text-transform: uppercase;
      line-height: 1.1; letter-spacing: 0.025em; max-width: 64rem;
      font-size: 1.5rem;
    }
    @media (min-width: 640px) { #hero-heading { font-size: 1.875rem; } }
    @media (min-width: 768px) { #hero-heading { font-size: 3rem; } }
    @media (min-width: 1024px) { #hero-heading { font-size: 3.75rem; } }
    @media (min-width: 1280px) { #hero-heading { font-size: 4.5rem; } }

    /* Bottom Bar */
    #bottom-bar-wrap {
      display: flex; justify-content: center; padding-bottom: 1rem;
    }
    @media (min-width: 640px) { #bottom-bar-wrap { padding-bottom: 1.5rem; } }
    @media (min-width: 768px) { #bottom-bar-wrap { padding-bottom: 2.5rem; } }

    #bottom-bar {
      background: #000; display: flex; align-items: center; justify-content: center;
      overflow: hidden; position: relative;
      transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
      width: 280px; max-width: 85vw; height: 56px;
    }
    #bottom-bar.collapsed { width: 56px; max-width: 56px; }

    #bar-content {
      display: flex; align-items: center; justify-content: space-between;
      width: 100%; padding: 0.75rem 1rem;
      transition: opacity 0.2s;
    }
    @media (min-width: 768px) { #bar-content { padding: 1rem 1.5rem; } }
    #bar-content.hidden-content { opacity: 0; pointer-events: none; }

    .bar-icon-wrap { width: 2.5rem; height: 2.5rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

    #home-icon { width: 20px; height: 20px; color: #f59e0b; }

    #bar-label {
      color: #fff; font-size: 0.875rem; letter-spacing: 0.15em;
      text-transform: uppercase; font-weight: 500; white-space: nowrap;
    }

    #hamburger { width: 2.5rem; height: 2.5rem; display: flex; align-items: center; justify-content: center; cursor: pointer; background: none; border: none; flex-shrink: 0; position: relative; }
    .ham-line { position: absolute; left: 7px; width: 24px; height: 1.5px; background: #fff; }
    .ham-line:first-child { top: 15px; }
    .ham-line:last-child { top: 22px; }

    #close-btn {
      position: absolute; width: 56px; height: 56px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; background: none; border: none;
      transition: opacity 0.3s; opacity: 0; pointer-events: none;
    }
    #close-btn.visible { opacity: 1; pointer-events: auto; }
    .close-line { position: absolute; left: 18px; top: 27px; width: 20px; height: 1.5px; background: #fff; }
    .close-line:first-child { transform: rotate(45deg); }
    .close-line:last-child { transform: rotate(-45deg); }

    /* Menu Popup */
    #menu-overlay {
      position: fixed; inset: 0; z-index: 20; display: none;
    }
    #menu-overlay.open { display: block; animation: fadeIn 0.3s ease forwards; }
    #menu-overlay.closing { display: block; animation: fadeOut 0.3s ease forwards; }

    #menu-panel {
      position: fixed; z-index: 30;
      left: 50%; bottom: 80px;
      width: 92vw; max-width: 480px;
      background: #000; border-radius: 0.5rem;
      padding: 1.5rem; display: none;
    }
    @media (min-width: 640px) { #menu-panel { bottom: 100px; padding: 2rem; } }
    @media (min-width: 768px) { #menu-panel { bottom: 120px; padding: 2.5rem; } }
    #menu-panel.open { display: block; animation: menuSlideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    #menu-panel.closing { display: block; animation: menuSlideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

    #menu-label {
      color: #a3a3a3; font-size: 0.75rem; letter-spacing: 0.2em;
      text-transform: uppercase; margin-bottom: 1.5rem;
    }

    #menu-list { list-style: none; }
    #menu-list li { margin-bottom: 0.25rem; }
    #menu-list a {
      color: #fff; font-size: 1.5rem; text-decoration: none;
      display: block; padding: 0.25rem 0; transition: color 0.2s;
    }
    #menu-list a:hover { color: #d4d4d4; }
    @media (min-width: 768px) { #menu-list a { font-size: 1.875rem; } }
    @media (min-width: 1024px) { #menu-list a { font-size: 2.25rem; } }

    .menu-item { opacity: 0; animation: menuItemSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

    #menu-footer {
      margin-top: 2rem; padding-top: 1.5rem;
      border-top: 1px solid rgba(64,64,64,0.5);
    }
    .menu-footer-row {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;
    }
    .menu-footer-label { color: #a3a3a3; font-size: 0.875rem; }
    .menu-footer-value { color: #fff; font-size: 0.875rem; }

    #menu-cta {
      width: 100%; margin-top: 1.5rem; background: #fff; color: #000;
      padding: 0.75rem; font-size: 0.875rem; font-weight: 500;
      letter-spacing: 0.05em; border: none; cursor: pointer; transition: background 0.2s;
    }
    #menu-cta:hover { background: #f5f5f5; }

    /* Scroll Gallery */
    #scroll-gallery {
      position: fixed; inset: 0; z-index: 10; pointer-events: none;
    }

    #rect-line {
      position: absolute; top: 0; left: 50%; transform: translateX(-50%);
      height: 100%; background: #000; width: 0px; display: none;
    }

    #fullscreen-content {
      position: absolute; inset: 0; display: none;
    }

    .gallery-img-wrap {
      position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    }
    .gallery-img-inner {
      width: 85vw; max-width: 900px; aspect-ratio: 16/10; overflow: hidden; border-radius: 0.5rem;
    }
    @media (min-width: 640px) {
      .gallery-img-inner { width: 100%; height: 100%; max-width: none; aspect-ratio: auto; border-radius: 0; }
    }
    .gallery-img-inner img { width: 100%; height: 100%; object-fit: cover; }

    #black-text-screen {
      position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 5;
    }
    #black-text-screen .bg { position: absolute; inset: 0; background: #000; }
    #black-text-screen h2 {
      position: relative; color: #fff; text-align: center; font-weight: 300;
      line-height: 1.3; max-width: 48rem; padding: 0 1.5rem;
      font-size: 1.5rem;
    }
    @media (min-width: 640px) { #black-text-screen h2 { font-size: 1.875rem; } }
    @media (min-width: 768px) { #black-text-screen h2 { font-size: 2.25rem; } }
    @media (min-width: 1024px) { #black-text-screen h2 { font-size: 3rem; } }
    #black-text-screen .accent { color: #f59e0b; }

    #white-screen {
      position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 6;
    }
    #white-screen h2 {
      color: #262626; text-align: center; font-weight: 300;
      line-height: 1.3; max-width: 48rem; padding: 0 1.5rem;
      font-size: 1.5rem;
    }
    @media (min-width: 640px) { #white-screen h2 { font-size: 1.875rem; } }
    @media (min-width: 768px) { #white-screen h2 { font-size: 2.25rem; } }
    @media (min-width: 1024px) { #white-screen h2 { font-size: 3rem; } }
    #white-screen .accent { color: #f59e0b; }

    /* Scroll spacer */
    #scroll-spacer { height: 900vh; }

    /* Animations */
    @keyframes menuSlideUp {
      from { opacity: 0; transform: translateX(-50%) translateY(40px) scale(0.95); }
      to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
    }
    @keyframes menuSlideDown {
      from { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
      to { opacity: 0; transform: translateX(-50%) translateY(40px) scale(0.95); }
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
    @keyframes menuItemSlide {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>

<!-- Splash Screen -->
<div id="splash">
  <video
    id="splash-video"
    src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_205729_0e6fae4e-5fc0-42d0-b49a-b88d85ede0b2.mp4"
    autoplay muted playsinline
  ></video>
</div>

<!-- Hero Section -->
<section id="hero">
  <video
    id="hero-video"
    src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_210218_173f8eba-17ff-4e27-972b-d128af25bf49.mp4"
    autoplay muted loop playsinline
  ></video>

  <div id="hero-content">
    <!-- Top Navbar -->
    <nav id="navbar">
      <div class="nav-spacer"></div>
      <h1 id="brand-name" class="font-haboro">VELORA</h1>
      <div class="nav-spacer" style="display:flex;justify-content:flex-end;">
        <button id="cta-btn" class="font-geist">GET IN TOUCH</button>
      </div>
    </nav>

    <!-- Hero Heading -->
    <div id="hero-heading-wrap">
      <h2 id="hero-heading" class="font-haboro">
        PREMIUM REAL ESTATE FOR<br>INVESTORS BEYOND OWNERSHIP
      </h2>
    </div>

    <!-- Bottom Morphing Bar -->
    <div id="bottom-bar-wrap">
      <div id="bottom-bar">
        <div id="bar-content">
          <div class="bar-icon-wrap">
            <svg id="home-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
          <span id="bar-label" class="font-geist">HOME</span>
          <button id="hamburger" aria-label="Open menu">
            <span class="ham-line"></span>
            <span class="ham-line"></span>
          </button>
        </div>
        <button id="close-btn" aria-label="Close menu">
          <span class="close-line"></span>
          <span class="close-line"></span>
        </button>
      </div>
    </div>
  </div>

  <!-- Menu Overlay -->
  <div id="menu-overlay"></div>

  <!-- Menu Panel -->
  <div id="menu-panel">
    <p id="menu-label" class="font-geist">MENU</p>
    <ul id="menu-list" class="font-haboro">
      <li class="menu-item" style="animation-delay:100ms"><a href="#">About</a></li>
      <li class="menu-item" style="animation-delay:160ms"><a href="#">Properties</a></li>
      <li class="menu-item" style="animation-delay:220ms"><a href="#">Work</a></li>
      <li class="menu-item" style="animation-delay:280ms"><a href="#">Partnership</a></li>
      <li class="menu-item" style="animation-delay:340ms"><a href="#">Contact</a></li>
    </ul>
    <div id="menu-footer" class="font-geist">
      <div class="menu-footer-row">
        <span class="menu-footer-label">Private line</span>
        <span class="menu-footer-value">+44 020 8156 7290</span>
      </div>
      <div class="menu-footer-row">
        <span class="menu-footer-label">Email</span>
        <span class="menu-footer-value">hello@velora.com</span>
      </div>
    </div>
    <button id="menu-cta" class="font-geist">GET IN TOUCH</button>
  </div>
</section>

<!-- Scroll Gallery Overlay -->
<div id="scroll-gallery">
  <div id="rect-line"></div>
  <div id="fullscreen-content">
    <div class="absolute inset-0 bg-black" style="position:absolute;inset:0;background:#000;"></div>
    <div class="gallery-img-wrap" id="img-wrap-0" style="z-index:1;display:none;">
      <div class="gallery-img-inner">
        <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_211418_dbb8d807-3cfb-4c26-b1df-02fb0c23cc7d.png&w=1280&q=85" alt="Property 1">
      </div>
    </div>
    <div class="gallery-img-wrap" id="img-wrap-1" style="z-index:2;display:none;">
      <div class="gallery-img-inner">
        <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_211445_ba965dcd-97d6-4644-b390-d4744078ec6c.png&w=1280&q=85" alt="Property 2">
      </div>
    </div>
    <div class="gallery-img-wrap" id="img-wrap-2" style="z-index:3;display:none;">
      <div class="gallery-img-inner">
        <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_212326_f5e78786-d7bb-40c5-abac-cd3c0be37d90.png&w=1280&q=85" alt="Property 3">
      </div>
    </div>
    <div id="black-text-screen" style="display:none;">
      <div class="bg"></div>
      <h2 class="font-geist">Access exceptional real estate<br>opportunities <span class="accent">worldwide.</span></h2>
    </div>
    <div id="white-screen" style="display:none;">
      <h2 class="font-geist">Built on trust and <span class="accent">expertise.</span></h2>
    </div>
  </div>
</div>

<!-- Scroll Spacer -->
<div id="scroll-spacer"></div>

<script>
// Splash Screen
const splash = document.getElementById('splash');
const splashVideo = document.getElementById('splash-video');
splashVideo.addEventListener('ended', () => {
  splash.classList.add('fading');
  setTimeout(() => { splash.style.display = 'none'; }, 800);
});

// Menu
let menuOpen = false;
const bottomBar = document.getElementById('bottom-bar');
const barContent = document.getElementById('bar-content');
const closeBtn = document.getElementById('close-btn');
const menuOverlay = document.getElementById('menu-overlay');
const menuPanel = document.getElementById('menu-panel');
const hamburger = document.getElementById('hamburger');

function openMenu() {
  menuOpen = true;
  bottomBar.classList.add('collapsed');
  barContent.classList.add('hidden-content');
  closeBtn.classList.add('visible');
  menuOverlay.classList.remove('closing');
  menuOverlay.classList.add('open');
  menuPanel.classList.remove('closing');
  menuPanel.classList.add('open');
}

function closeMenu() {
  menuOverlay.classList.add('closing');
  menuOverlay.classList.remove('open');
  menuPanel.classList.add('closing');
  menuPanel.classList.remove('open');
  setTimeout(() => {
    menuOpen = false;
    bottomBar.classList.remove('collapsed');
    barContent.classList.remove('hidden-content');
    closeBtn.classList.remove('visible');
    menuOverlay.classList.remove('closing');
    menuPanel.classList.remove('closing');
  }, 300);
}

hamburger.addEventListener('click', openMenu);
closeBtn.addEventListener('click', closeMenu);
menuOverlay.addEventListener('click', closeMenu);
document.querySelectorAll('#menu-list a').forEach(a => a.addEventListener('click', (e) => { e.preventDefault(); closeMenu(); }));

// Scroll Gallery
const rectLine = document.getElementById('rect-line');
const fullscreenContent = document.getElementById('fullscreen-content');
const imgWraps = [document.getElementById('img-wrap-0'), document.getElementById('img-wrap-1'), document.getElementById('img-wrap-2')];
const blackTextScreen = document.getElementById('black-text-screen');
const whiteScreen = document.getElementById('white-screen');

function handleScroll() {
  const scrollY = window.scrollY;
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
  const progress = maxScroll > 0 ? Math.max(0, Math.min(1, scrollY / maxScroll)) : 0;

  // Phase 1: Line appears (0 - 0.06)
  const lineProgress = Math.max(0, Math.min(1, progress / 0.06));

  // Phase 2: Width expansion (0.06 - 0.16)
  const expandProgress = Math.max(0, Math.min(1, (progress - 0.06) / 0.10));
  const eased = expandProgress < 0.5
    ? 4 * expandProgress * expandProgress * expandProgress
    : 1 - Math.pow(-2 * expandProgress + 2, 3) / 2;

  let rectWidth = '0px';
  if (progress > 0 && progress <= 0.06) {
    rectWidth = (lineProgress * 50) + 'px';
  } else if (progress > 0.06) {
    rectWidth = eased >= 0.95 ? '100vw' : 'calc(50px + ' + (eased * 100) + 'vw)';
  }

  const showRect = progress > 0;
  const rectFullscreen = progress >= 0.16;

  // Show/hide rect line
  if (showRect && !rectFullscreen) {
    rectLine.style.display = 'block';
    rectLine.style.width = rectWidth;
  } else {
    rectLine.style.display = 'none';
  }

  // Fullscreen content
  if (rectFullscreen) {
    fullscreenContent.style.display = 'block';
  } else {
    fullscreenContent.style.display = 'none';
  }

  // Images
  const starts = [0.16, 0.34, 0.50];
  const durations = [0.18, 0.16, 0.14];
  for (let i = 0; i < 3; i++) {
    const imgProgress = Math.max(0, Math.min(1, (progress - starts[i]) / durations[i]));
    if (imgProgress <= 0) {
      imgWraps[i].style.display = 'none';
    } else {
      imgWraps[i].style.display = 'flex';
      const scale = 0.2 + imgProgress * 0.8;
      const opacity = Math.min(1, imgProgress * 4);
      imgWraps[i].querySelector('.gallery-img-inner').style.transform = 'scale(' + scale + ')';
      imgWraps[i].querySelector('.gallery-img-inner').style.opacity = opacity;
    }
  }

  // Black text screen (0.64 - 0.78)
  const blackTextProgress = Math.max(0, Math.min(1, (progress - 0.64) / 0.14));
  const morphProgress = Math.max(0, Math.min(1, (progress - 0.78) / 0.12));

  if (blackTextProgress > 0 && progress < 0.90) {
    blackTextScreen.style.display = 'flex';
    const scale = 0.2 + blackTextProgress * 0.8;
    const opacity = Math.min(1, blackTextProgress * 4);
    blackTextScreen.style.transform = 'scale(' + scale + ')';
    blackTextScreen.style.opacity = opacity;
    const textOpacity = progress >= 0.78 ? Math.max(0, 1 - morphProgress * 3) : 1;
    blackTextScreen.querySelector('h2').style.opacity = textOpacity;
  } else {
    blackTextScreen.style.display = 'none';
  }

  // White screen (0.78+)
  const whiteTextProgress = Math.max(0, Math.min(1, (progress - 0.90) / 0.10));
  if (progress >= 0.78) {
    whiteScreen.style.display = 'flex';
    const r = Math.round(morphProgress * 255);
    whiteScreen.style.backgroundColor = 'rgb(' + r + ',' + r + ',' + r + ')';
    whiteScreen.style.opacity = morphProgress;
    const textOp = whiteTextProgress > 0
      ? Math.min(1, whiteTextProgress * 2.5)
      : Math.max(0, morphProgress * 2 - 1);
    whiteScreen.querySelector('h2').style.opacity = textOp;
  } else {
    whiteScreen.style.display = 'none';
  }
}

window.addEventListener('scroll', handleScroll, { passive: true });
handleScroll();
</script>
</body>
</html>

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Luxury Hero"
template_id: "ab679ee8-8690-4383-b6da-e0c6ffaa3d72"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Luxury Hero

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `ab679ee8-8690-4383-b6da-e0c6ffaa3d72`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Luxury Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/0fa90afe-705d-4b5a-9152-7a119150665a.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Build a luxury real estate landing page called **"Horizon Estates"** using **React + TypeScript + Vite + Tailwind CSS**. Use `lucide-react` for icons. Do NOT reset or remove any padding, margin, or spacing from elements. Every spacing value listed below is intentional and must be preserved exactly.

---

### FONTS (load in index.html `<head>`)

```html
<link href="https://db.onlinewebfonts.com/c/60323b40d418d578b0b2d55837f67ef2?family=Magical+Source+Demo" rel="stylesheet">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap" rel="stylesheet">
```

Tailwind config extends fontFamily:
```js
heading: ['"Magical Source Demo"', 'serif'],
geist: ['Geist', 'sans-serif'],
```

---

### GLOBAL CSS (index.css) - COPY EXACTLY

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Geist', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

.font-heading {
  font-family: 'Magical Source Demo', serif;
}

.font-geist {
  font-family: 'Geist', sans-serif;
}
```

**IMPORTANT**: The `* { margin: 0; padding: 0 }` reset applies globally. All component spacing is then set explicitly via Tailwind classes. Do NOT add additional resets or remove the padding/margin classes on components - they counteract the global reset.

---

### APP ROOT

```tsx
<div className="bg-black">
  <Navbar />
  <Hero />
</div>
```

Nothing else. Background is pure black.

---

### NAVBAR COMPONENT

The navbar is `position: fixed` and overlays the hero. It has real padding that must not be zero.

**Container `<nav>`:**
```
className="fixed top-0 left-0 right-0 z-50 px-5 md:px-12 py-4 md:py-5 flex items-center justify-between"
```
- Horizontal padding: `px-5` (20px) on mobile, `md:px-12` (48px) on desktop
- Vertical padding: `py-4` (16px) on mobile, `md:py-5` (20px) on desktop
- These paddings are CRITICAL - they space the logo, links, and button away from screen edges

**Left - Logo SVG:**
```tsx
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none" className={className}>
  <path d="M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z" fill="currentColor" />
</svg>
```
Classes on the logo in the navbar: `w-7 h-7 md:w-10 md:h-10 text-white relative z-50`

**Center - Nav Links (hidden mobile, visible md+):**
```
className="hidden md:flex items-center gap-8 text-white/90 text-sm font-geist font-light tracking-wide"
```
- `gap-8` (32px) between each link - this is the spacing between nav items
- Links: "Story", "Estates", "Lifestyle", "Views", "Inquire"
- Each link: `hover:text-white transition-colors`

**Right - CTA Button (hidden mobile, visible md+):**
```
className="hidden md:flex group items-center gap-2 bg-white/90 backdrop-blur-sm rounded-full pl-5 pr-1.5 py-1.5 hover:bg-white transition-all shadow-lg"
```
- `pl-5` (20px) left padding for text breathing room
- `pr-1.5` (6px) right padding - tight because the arrow circle sits there
- `py-1.5` (6px) vertical padding
- `gap-2` (8px) between text and arrow circle
- `rounded-full` makes it pill-shaped

Button text span:
```
className="text-gray-800 text-xs md:text-sm font-geist font-medium tracking-wider uppercase"
```

Arrow circle span:
```
className="flex items-center justify-center w-7 h-7 md:w-8 md:h-8 rounded-full bg-rose-200/60 group-hover:bg-rose-300/70 transition-colors"
```
Contains `<ArrowRight className="w-3.5 h-3.5 text-gray-700" />` from lucide-react.

**Mobile Hamburger (visible below md):**
```
className="relative z-50 md:hidden flex flex-col items-center justify-center w-10 h-10"
```
- The button has a tap target of `w-10 h-10` (40px square)
- Two `<span>` lines inside:
```
className="block w-5 h-[1.5px] bg-white rounded-full transition-all duration-300 ease-[cubic-bezier(0.77,0,0.18,1)]"
```
- Closed state: first span `-translate-y-[3px]`, second span `translate-y-[3px]` (6px gap between lines)
- Open state: first span `rotate-45 translate-y-[3px]`, second span `-rotate-45 -translate-y-[0px]`

**Mobile Menu Overlay:**
- Outer: `fixed inset-0 z-40 md:hidden transition-all duration-500 ease-[cubic-bezier(0.77,0,0.18,1)]`
- Background: `absolute inset-0 bg-black/95 backdrop-blur-xl transition-opacity duration-500`
- Content container: `relative h-full flex flex-col items-center justify-center px-8`
  - `px-8` (32px) side padding on the centered content
- Links list: `flex flex-col items-center gap-6`
  - `gap-6` (24px) between each mobile nav link
- Each link: `text-white text-2xl font-heading tracking-wider uppercase hover:text-white/70 transition-colors`
- Staggered animation: each item delays by 60ms starting at 100ms (`100 + i * 60`ms)
- Animation: `opacity-0 translate-y-6` to `opacity-100 translate-y-0`, duration 500ms
- Mobile CTA appears below links with `mt-10` (40px top margin), delayed 420ms
- Mobile CTA button: same styles as desktop but with `w-7 h-7` arrow circle (no md size-up)
- When menu opens: `document.body.style.overflow = 'hidden'` (prevents background scroll)

---

### HERO COMPONENT

**Outer wrapper** - creates scrollable space:
```
className="relative h-[200dvh]"
```
This makes the total height 200% of viewport - the extra 100vh below is empty scroll space.

**Sticky inner section** - stays pinned while you scroll through the outer wrapper:
```
className="sticky top-0 w-full h-[100dvh] overflow-hidden"
```

**VIDEO 1 URL**: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260625_174131_395bc785-bb21-4e65-abf6-27c56f0764b6.mp4`

**VIDEO 2 URL**: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_055914_ee2b3b56-9a58-4885-989e-5b72a68b630d.mp4`

**Video 2 (BEHIND, rendered first in DOM):**
```html
<video ref={video2Ref} muted playsInline preload="auto" src={VIDEO_2}
  className="absolute inset-0 w-full h-full object-cover" />
```
- No autoPlay, no loop
- Always in the DOM, always visible (it just sits behind Video 1)

**Video 1 (ON TOP, rendered second in DOM so it stacks above):**
```html
<video autoPlay muted loop playsInline
  className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ${
    scrolled ? 'opacity-0 pointer-events-none' : 'opacity-100'
  }`}>
  <source src={VIDEO_1} type="video/mp4" />
</video>
```
- Loops forever, auto-plays on load
- Fades to invisible (700ms) when user scrolls, revealing Video 2 behind it

**Scroll logic (JavaScript):**
```ts
const [scrolled, setScrolled] = useState(false);
const video2Ref = useRef<HTMLVideoElement>(null);
const wasScrolled = useRef(false);

useEffect(() => {
  const handleScroll = () => {
    const isScrolled = window.scrollY > 0;
    setScrolled(isScrolled);
    const v = video2Ref.current;
    if (!v) return;
    if (isScrolled && !wasScrolled.current) {
      v.currentTime = 0;
      v.play().catch(() => {});
    } else if (!isScrolled && wasScrolled.current) {
      v.pause();
    }
    wasScrolled.current = isScrolled;
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

**Center Logo with Concentric Circles:**

Positioning container:
```
className="absolute inset-0 flex items-center justify-center pb-[25vh] sm:pb-[30vh]"
```
- `pb-[25vh]` / `sm:pb-[30vh]` pushes the logo upward from center (toward upper-third of screen)

Circle container:
```
className="relative flex items-center justify-center w-[45vw] h-[45vw] max-w-[320px] max-h-[320px] md:w-[30vw] md:h-[30vw] md:max-w-[400px] md:max-h-[400px]"
```

Three elements animate in on mount (a `visible` state flips true after 200ms setTimeout):

1. Outer circle ring:
```
className="absolute inset-0 rounded-full border border-white/35 transition-all duration-[1200ms] ease-out"
// visible: opacity-100 scale-100 | hidden: opacity-0 scale-75
// transitionDelay: 0ms
```

2. Inner circle ring:
```
className="absolute inset-[12%] rounded-full border border-white/25 transition-all duration-[1200ms] ease-out"
// visible: opacity-100 scale-100 | hidden: opacity-0 scale-75
// transitionDelay: 150ms
```

3. Logo SVG (same Logo component from Navbar):
```
className="w-12 h-12 sm:w-16 sm:h-16 md:w-24 md:h-24 text-white"
// wrapper: transition-all duration-[1000ms] ease-out
// visible: opacity-100 scale-100 | hidden: opacity-0 scale-90
// transitionDelay: 350ms
```

**Bottom Text Block:**
```
className="absolute bottom-0 left-0 right-0 pb-10 sm:pb-12 md:pb-16 px-5 sm:px-6 md:px-12 text-center"
```
- Bottom padding: `pb-10` (40px) mobile, `pb-12` (48px) sm, `pb-16` (64px) md
- Side padding: `px-5` (20px) mobile, `px-6` (24px) sm, `px-12` (48px) md

H1:
```
className="font-heading text-white text-2xl sm:text-3xl md:text-5xl lg:text-6xl leading-[1.1] tracking-wide uppercase"
// Animation: opacity-0 translate-y-8 -> opacity-100 translate-y-0
// duration-[1000ms] ease-out, delay 600ms
```
Text: `"Where the horizon meets"` then `<br />` then `"timeless elegance"`

P:
```
className="mt-3 sm:mt-4 md:mt-6 text-white/80 font-geist font-light text-xs sm:text-sm md:text-base max-w-xs sm:max-w-md mx-auto leading-relaxed"
// Animation: opacity-0 translate-y-6 -> opacity-100 translate-y-0
// duration-[1000ms] ease-out, delay 850ms
```
- `mt-3` (12px) / `mt-4` (16px) / `mt-6` (24px) gap between heading and paragraph
- `max-w-xs` (320px) / `sm:max-w-md` (448px) constrains paragraph width
- `mx-auto` centers it

Text: `"Indulge in unparalleled seaside living where sophistication meets the endless shore."`

---

### CRITICAL NOTES TO PREVENT SPACING ISSUES

1. Do NOT use `@layer base` resets that strip button/link padding beyond what is already in the global `*` reset
2. The button `pl-5 pr-1.5 py-1.5` creates asymmetric padding intentionally - the left side has more room for text, the right side is tight against the arrow circle
3. The navbar `px-5 md:px-12` keeps content away from screen edges - never set this to 0
4. `gap-8` on the nav links creates 32px between each item - this is what prevents them from being crammed together
5. The `pb-[25vh]` on the center logo container is what pushes it toward the upper third - without it the logo would be dead center
6. All `transition-all duration-[Xms]` values use Tailwind's arbitrary value syntax with square brackets
7. The `sticky top-0` + `h-[200dvh]` outer div pattern is what makes scroll detection work - without the extra height, `window.scrollY` stays at 0

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Horizon Estates</title>
  <link href="https://db.onlinewebfonts.com/c/60323b40d418d578b0b2d55837f67ef2?family=Magical+Source+Demo" rel="stylesheet">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Geist', sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
      background: #000;
    }

    .font-heading {
      font-family: 'Magical Source Demo', serif;
    }

    /* NAVBAR */
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 50;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    @media (min-width: 768px) {
      .navbar {
        padding: 20px 48px;
      }
    }

    .logo {
      width: 28px;
      height: 28px;
      color: white;
      position: relative;
      z-index: 50;
    }

    @media (min-width: 768px) {
      .logo {
        width: 40px;
        height: 40px;
      }
    }

    .nav-links {
      display: none;
      align-items: center;
      gap: 32px;
      list-style: none;
    }

    @media (min-width: 768px) {
      .nav-links {
        display: flex;
      }
    }

    .nav-links a {
      color: rgba(255, 255, 255, 0.9);
      text-decoration: none;
      font-size: 14px;
      font-weight: 300;
      letter-spacing: 0.025em;
      transition: color 0.2s;
    }

    .nav-links a:hover {
      color: white;
    }

    .cta-btn {
      display: none;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(4px);
      border-radius: 9999px;
      padding: 6px 6px 6px 20px;
      border: none;
      cursor: pointer;
      transition: background 0.2s;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    }

    @media (min-width: 768px) {
      .cta-btn {
        display: flex;
      }
    }

    .cta-btn:hover {
      background: white;
    }

    .cta-btn-text {
      color: #1f2937;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      font-family: 'Geist', sans-serif;
    }

    @media (min-width: 768px) {
      .cta-btn-text {
        font-size: 14px;
      }
    }

    .cta-btn-arrow {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 9999px;
      background: rgba(251, 207, 232, 0.6);
      transition: background 0.2s;
    }

    @media (min-width: 768px) {
      .cta-btn-arrow {
        width: 32px;
        height: 32px;
      }
    }

    .cta-btn:hover .cta-btn-arrow {
      background: rgba(252, 164, 175, 0.7);
    }

    .cta-btn-arrow svg {
      width: 14px;
      height: 14px;
      color: #374151;
    }

    /* HAMBURGER */
    .hamburger {
      position: relative;
      z-index: 50;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      background: none;
      border: none;
      cursor: pointer;
    }

    @media (min-width: 768px) {
      .hamburger {
        display: none;
      }
    }

    .hamburger-line {
      display: block;
      width: 20px;
      height: 1.5px;
      background: white;
      border-radius: 9999px;
      transition: all 0.3s cubic-bezier(0.77, 0, 0.18, 1);
    }

    .hamburger-line:first-child {
      transform: translateY(-3px);
    }

    .hamburger-line:last-child {
      transform: translateY(3px);
    }

    .hamburger.open .hamburger-line:first-child {
      transform: rotate(45deg) translateY(0.75px);
    }

    .hamburger.open .hamburger-line:last-child {
      transform: rotate(-45deg) translateY(-0.75px);
    }

    /* MOBILE MENU */
    .mobile-menu {
      position: fixed;
      inset: 0;
      z-index: 40;
      visibility: hidden;
      transition: all 0.5s cubic-bezier(0.77, 0, 0.18, 1);
    }

    @media (min-width: 768px) {
      .mobile-menu {
        display: none !important;
      }
    }

    .mobile-menu.open {
      visibility: visible;
    }

    .mobile-menu-bg {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.95);
      backdrop-filter: blur(24px);
      opacity: 0;
      transition: opacity 0.5s cubic-bezier(0.77, 0, 0.18, 1);
    }

    .mobile-menu.open .mobile-menu-bg {
      opacity: 1;
    }

    .mobile-menu-content {
      position: relative;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 0 32px;
    }

    .mobile-menu-links {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
      list-style: none;
    }

    .mobile-menu-links li {
      opacity: 0;
      transform: translateY(24px);
      transition: all 0.5s cubic-bezier(0.77, 0, 0.18, 1);
    }

    .mobile-menu.open .mobile-menu-links li {
      opacity: 1;
      transform: translateY(0);
    }

    .mobile-menu.open .mobile-menu-links li:nth-child(1) { transition-delay: 100ms; }
    .mobile-menu.open .mobile-menu-links li:nth-child(2) { transition-delay: 160ms; }
    .mobile-menu.open .mobile-menu-links li:nth-child(3) { transition-delay: 220ms; }
    .mobile-menu.open .mobile-menu-links li:nth-child(4) { transition-delay: 280ms; }
    .mobile-menu.open .mobile-menu-links li:nth-child(5) { transition-delay: 340ms; }

    .mobile-menu-links a {
      color: white;
      text-decoration: none;
      font-size: 24px;
      font-family: 'Magical Source Demo', serif;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      transition: color 0.2s;
    }

    .mobile-menu-links a:hover {
      color: rgba(255, 255, 255, 0.7);
    }

    .mobile-menu-cta {
      margin-top: 40px;
      opacity: 0;
      transform: translateY(24px);
      transition: all 0.5s cubic-bezier(0.77, 0, 0.18, 1);
    }

    .mobile-menu.open .mobile-menu-cta {
      opacity: 1;
      transform: translateY(0);
      transition-delay: 420ms;
    }

    .mobile-cta-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(4px);
      border-radius: 9999px;
      padding: 6px 6px 6px 20px;
      border: none;
      cursor: pointer;
      transition: background 0.2s;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .mobile-cta-btn:hover {
      background: white;
    }

    /* HERO */
    .hero-outer {
      position: relative;
      height: 200dvh;
    }

    .hero-section {
      position: sticky;
      top: 0;
      width: 100%;
      height: 100dvh;
      overflow: hidden;
    }

    .hero-video {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .video-1 {
      transition: opacity 0.7s;
    }

    .video-1.faded {
      opacity: 0;
      pointer-events: none;
    }

    /* CENTER LOGO */
    .center-logo-wrap {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      padding-bottom: 25vh;
    }

    @media (min-width: 640px) {
      .center-logo-wrap {
        padding-bottom: 30vh;
      }
    }

    .center-logo-container {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 45vw;
      height: 45vw;
      max-width: 320px;
      max-height: 320px;
    }

    @media (min-width: 768px) {
      .center-logo-container {
        width: 30vw;
        height: 30vw;
        max-width: 400px;
        max-height: 400px;
      }
    }

    .circle-outer {
      position: absolute;
      inset: 0;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.35);
      opacity: 0;
      transform: scale(0.75);
      transition: all 1200ms ease-out;
      transition-delay: 0ms;
    }

    .circle-inner {
      position: absolute;
      inset: 12%;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.25);
      opacity: 0;
      transform: scale(0.75);
      transition: all 1200ms ease-out;
      transition-delay: 150ms;
    }

    .center-logo-icon {
      opacity: 0;
      transform: scale(0.9);
      transition: all 1000ms ease-out;
      transition-delay: 350ms;
    }

    .center-logo-icon svg {
      width: 48px;
      height: 48px;
      color: white;
    }

    @media (min-width: 640px) {
      .center-logo-icon svg {
        width: 64px;
        height: 64px;
      }
    }

    @media (min-width: 768px) {
      .center-logo-icon svg {
        width: 96px;
        height: 96px;
      }
    }

    /* Visible state */
    .visible .circle-outer,
    .visible .circle-inner {
      opacity: 1;
      transform: scale(1);
    }

    .visible .center-logo-icon {
      opacity: 1;
      transform: scale(1);
    }

    /* BOTTOM TEXT */
    .bottom-text {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 0 20px 40px;
      text-align: center;
    }

    @media (min-width: 640px) {
      .bottom-text {
        padding: 0 24px 48px;
      }
    }

    @media (min-width: 768px) {
      .bottom-text {
        padding: 0 48px 64px;
      }
    }

    .bottom-text h1 {
      font-family: 'Magical Source Demo', serif;
      color: white;
      font-size: 24px;
      line-height: 1.1;
      letter-spacing: 0.025em;
      text-transform: uppercase;
      opacity: 0;
      transform: translateY(32px);
      transition: all 1000ms ease-out;
      transition-delay: 600ms;
    }

    @media (min-width: 640px) {
      .bottom-text h1 {
        font-size: 30px;
      }
    }

    @media (min-width: 768px) {
      .bottom-text h1 {
        font-size: 48px;
      }
    }

    @media (min-width: 1024px) {
      .bottom-text h1 {
        font-size: 60px;
      }
    }

    .bottom-text p {
      margin-top: 12px;
      color: rgba(255, 255, 255, 0.8);
      font-family: 'Geist', sans-serif;
      font-weight: 300;
      font-size: 12px;
      max-width: 320px;
      margin-left: auto;
      margin-right: auto;
      line-height: 1.625;
      opacity: 0;
      transform: translateY(24px);
      transition: all 1000ms ease-out;
      transition-delay: 850ms;
    }

    @media (min-width: 640px) {
      .bottom-text p {
        font-size: 14px;
        max-width: 448px;
        margin-top: 16px;
      }
    }

    @media (min-width: 768px) {
      .bottom-text p {
        font-size: 16px;
        margin-top: 24px;
      }
    }

    .visible .bottom-text h1,
    .visible .bottom-text p {
      opacity: 1;
      transform: translateY(0);
    }
  </style>
</head>
<body>

  <!-- NAVBAR -->
  <nav class="navbar">
    <svg class="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">
      <path d="M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z" fill="currentColor" />
    </svg>

    <ul class="nav-links">
      <li><a href="#">Story</a></li>
      <li><a href="#">Estates</a></li>
      <li><a href="#">Lifestyle</a></li>
      <li><a href="#">Views</a></li>
      <li><a href="#">Inquire</a></li>
    </ul>

    <button class="cta-btn">
      <span class="cta-btn-text">Book a Tour</span>
      <span class="cta-btn-arrow">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
      </span>
    </button>

    <button class="hamburger" id="hamburger" aria-label="Toggle menu">
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
    </button>
  </nav>

  <!-- MOBILE MENU -->
  <div class="mobile-menu" id="mobileMenu">
    <div class="mobile-menu-bg"></div>
    <div class="mobile-menu-content">
      <ul class="mobile-menu-links">
        <li><a href="#">Story</a></li>
        <li><a href="#">Estates</a></li>
        <li><a href="#">Lifestyle</a></li>
        <li><a href="#">Views</a></li>
        <li><a href="#">Inquire</a></li>
      </ul>
      <div class="mobile-menu-cta">
        <button class="mobile-cta-btn">
          <span class="cta-btn-text">Book a Tour</span>
          <span class="cta-btn-arrow">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </span>
        </button>
      </div>
    </div>
  </div>

  <!-- HERO -->
  <div class="hero-outer">
    <section class="hero-section" id="heroSection">
      <video id="video2" class="hero-video" muted playsinline preload="auto"
        src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260624_055914_ee2b3b56-9a58-4885-989e-5b72a68b630d.mp4">
      </video>

      <video id="video1" class="hero-video video-1" autoplay muted loop playsinline>
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260625_174131_395bc785-bb21-4e65-abf6-27c56f0764b6.mp4" type="video/mp4" />
      </video>

      <div class="center-logo-wrap">
        <div class="center-logo-container">
          <div class="circle-outer"></div>
          <div class="circle-inner"></div>
          <div class="center-logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">
              <path d="M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z" fill="currentColor" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bottom-text">
        <h1>Where the horizon meets<br>timeless elegance</h1>
        <p>Indulge in unparalleled seaside living where sophistication meets the endless shore.</p>
      </div>
    </section>
  </div>

  <script>
    // Entrance animation
    setTimeout(() => {
      document.getElementById('heroSection').classList.add('visible');
    }, 200);

    // Scroll logic - video swap
    let wasScrolled = false;
    const video1 = document.getElementById('video1');
    const video2 = document.getElementById('video2');

    window.addEventListener('scroll', () => {
      const isScrolled = window.scrollY > 0;

      if (isScrolled) {
        video1.classList.add('faded');
      } else {
        video1.classList.remove('faded');
      }

      if (isScrolled && !wasScrolled) {
        video2.currentTime = 0;
        video2.play().catch(() => {});
      } else if (!isScrolled && wasScrolled) {
        video2.pause();
      }

      wasScrolled = isScrolled;
    }, { passive: true });

    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobileMenu');

    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.classList.toggle('open');
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close mobile menu on link click
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        hamburger.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "3D Story"
template_id: "adbfe70a-9f35-4c4b-978b-d5d5bdebc813"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 3D Story

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `adbfe70a-9f35-4c4b-978b-d5d5bdebc813`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![3D Story](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/a537e88c-4401-491d-b717-571d0004bb92.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Veldara</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html, body { overflow-x: hidden; }
body { font-family: 'Inter', sans-serif; background: #010101; color: #fff; }

.fixed { position: fixed; }
.absolute { position: absolute; }
.relative { position: relative; }
.inset-0 { top: 0; right: 0; bottom: 0; left: 0; }

/* Scroll Video */
#scroll-video-container {
  position: fixed; inset: 0; z-index: -10;
  background: #0a0a0a; top: -20%;
}
#scroll-video-container canvas,
#scroll-video-container video {
  position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
}
#scroll-video-container .overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.2); }

/* Particles */
#particles-canvas {
  position: fixed; inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 3;
}

/* Nav */
nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 2.5rem;
}
nav .logo { font-weight: 700; font-size: 1.25rem; color: #fff; letter-spacing: -0.025em; }
nav .nav-links { display: flex; align-items: center; gap: 1.5rem; }
nav .nav-links a { font-size: 0.875rem; color: #d1d5db; text-decoration: none; transition: color 0.2s; }
nav .nav-links a:hover { color: #fff; }
nav .social { display: flex; align-items: center; gap: 1rem; }
nav .social a { color: #d1d5db; transition: color 0.2s; }
nav .social a:hover { color: #fff; }
nav .social svg { width: 1.25rem; height: 1.25rem; }

/* Hero */
#hero {
  position: relative; height: 100vh; width: 100%; display: flex; flex-direction: column;
}
#hero .gradient-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.6), transparent, transparent);
}
#hero .content {
  position: relative; z-index: 10; flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end; text-align: center;
  padding: 0 1.5rem 6rem;
}
#hero .subtitle { font-size: 0.875rem; color: #9ca3af; margin-bottom: 1rem; letter-spacing: 0.05em; }
#hero h1 { font-size: clamp(1.5rem, 5vw, 3.75rem); font-weight: 600; line-height: 1.15; max-width: 48rem; }
#hero h1 .underlined {
  position: relative; display: inline-block;
}
#hero h1 .underlined .line {
  position: absolute; bottom: 0.25rem; left: 0; width: 100%; height: 10px;
  background: #2C5C88; border-radius: 2px;
}
#hero h1 .underlined span { position: relative; }
#hero .ctas {
  display: flex; align-items: center; gap: 1rem; margin-top: 2.5rem; flex-wrap: wrap; justify-content: center;
}
#hero .code-box {
  display: flex; align-items: center; gap: 0.5rem;
  background: #1a1a1a; border: 1px solid rgba(55,65,81,0.5);
  border-radius: 0.5rem; padding: 0.875rem 2rem;
}
#hero .code-box .prompt { color: #2C5C88; font-family: monospace; font-size: 0.875rem; }
#hero .code-box code { font-size: 0.875rem; color: #e5e7eb; font-family: monospace; }
#hero .cta-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: #2C5C88; color: #fff; font-weight: 500; border-radius: 0.5rem;
  padding: 0.875rem 2rem; font-size: 0.875rem; text-decoration: none; transition: background 0.2s;
}
#hero .cta-btn:hover { background: #3a7aad; }
#hero .bounce-arrow {
  position: relative; z-index: 10; display: flex; justify-content: center; padding-bottom: 2rem;
}
#hero .bounce-arrow svg { width: 1.5rem; height: 1.5rem; color: #6b7280; animation: bounce 1s infinite; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-25%); }
}

/* Cards */
#fixed-cards {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 4;
  padding: 2rem 2.5rem; opacity: 0; pointer-events: none;
}
#fixed-cards .grid {
  max-width: 72rem; margin: 0 auto;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.5rem;
}
#fixed-cards .card h3 { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 1rem; }
#fixed-cards .card p { color: #d1d5db; font-size: 0.875rem; line-height: 1.6; }

/* Section 3 */
#section-three {
  position: relative; min-height: 100vh; display: flex; align-items: flex-end;
  justify-content: center; padding: 0 2.5rem 8rem;
}
#section-three .inner {
  position: relative; z-index: 10; display: flex; flex-direction: column;
  align-items: center; text-align: center;
  opacity: 0; transform: translateY(32px); filter: blur(8px);
  transition: opacity 1s ease-out, transform 1s ease-out, filter 1s ease-out;
}
#section-three .inner.visible { opacity: 1; transform: translateY(0); filter: blur(0); }
#section-three .inner p { color: #d1d5db; font-size: 1rem; margin-bottom: 0.75rem; }
#section-three .inner h2 { font-size: clamp(1.875rem, 6vw, 4.5rem); font-weight: 700; }

/* Content wrapper */
#content { position: relative; z-index: 2; }

/* Responsive */
@media (max-width: 768px) {
  nav { padding: 1rem 1.5rem; }
  nav .nav-links { display: none; }
  #hero .content { padding-bottom: 5rem; }
  #hero h1 { font-size: 1.5rem; }
  #hero .ctas { flex-direction: column; }
  #fixed-cards .grid { grid-template-columns: 1fr; gap: 1.5rem; }
  #fixed-cards { padding: 1.5rem 1rem; }
  #section-three { padding-bottom: 5rem; }
}
</style>
</head>
<body>

<!-- Scroll Video Background -->
<div id="scroll-video-container">
  <canvas id="video-canvas"></canvas>
  <video id="video-fallback" muted playsinline preload="auto" crossorigin="anonymous"
    src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260616_212935_bbf608da-62d1-4f25-9be4-c346e4d09cc8.mp4"
  ></video>
  <div class="overlay"></div>
</div>

<!-- Particles -->
<canvas id="particles-canvas"></canvas>

<!-- Fixed Cards -->
<div id="fixed-cards">
  <div class="grid">
    <div class="card">
      <h3>Explore Veldara</h3>
      <p>Veldara merges the elegance of Svelte 5 with the depth of Three.js within easy reach. It's crafted to be robust and adaptable while remaining intuitive and simple to grasp.</p>
    </div>
    <div class="card">
      <h3>Unlock Three.js</h3>
      <p>The web is growing increasingly dimensional. At its heart, Veldara offers a composable declarative API for building performant Three.js experiences on the web.</p>
    </div>
    <div class="card">
      <h3>Connect Everything</h3>
      <p>Veldara ships with tooling for physics, XR, animation, layouting, model loading, and extensive utilities to make building compelling 3D apps for the web effortless.</p>
    </div>
  </div>
</div>

<!-- Navigation -->
<nav>
  <div style="display:flex;align-items:center;gap:2rem;">
    <span class="logo">veldara</span>
    <div class="nav-links">
      <a href="#">Guides</a>
      <a href="#">Journal</a>
    </div>
  </div>
  <div class="social">
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286z"/></svg></a>
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg></a>
  </div>
</nav>

<!-- Main Content -->
<div id="content">
  <!-- Section 1: Hero -->
  <section id="hero">
    <div class="gradient-overlay"></div>
    <div class="content">
      <p class="subtitle">Our Purpose:</p>
      <h1>
        Instantly craft immersive
        <span class="underlined"><span class="line"></span><span>3D worlds</span></span>
        on the web.
      </h1>
      <div class="ctas">
        <div class="code-box">
          <span class="prompt">&gt;</span>
          <code>npm i @veldara/core</code>
        </div>
        <a href="#" class="cta-btn">Get Started <span>&rarr;</span></a>
      </div>
    </div>
    <div class="bounce-arrow">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg>
    </div>
  </section>

  <!-- Spacer -->
  <div style="height:150vh;"></div>

  <!-- Cards Trigger Zone -->
  <div id="cards-trigger" style="height:200vh;"></div>

  <!-- Spacer -->
  <div style="height:100vh;"></div>

  <!-- Section 3 -->
  <section id="section-three">
    <div class="inner" id="section-three-inner">
      <p>Presenting</p>
      <h2>Veldara 8</h2>
    </div>
  </section>
</div>

<script>
(function() {
  // ===================== SCROLL VIDEO =====================
  const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260616_212935_bbf608da-62d1-4f25-9be4-c346e4d09cc8.mp4';
  const canvas = document.getElementById('video-canvas');
  const videoEl = document.getElementById('video-fallback');
  const ctx = canvas.getContext('2d');
  let frames = [];
  let framesReady = false;
  let lastFrameIndex = -1;
  let videoSeeking = false;

  function resizeCanvas() {
    const dpr = Math.min(devicePixelRatio, 2);
    const rect = canvas.getBoundingClientRect();
    const w = Math.round(rect.width * dpr);
    const h = Math.round(rect.height * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    lastFrameIndex = -1;
  }

  async function extractFrames() {
    try {
      const response = await fetch(VIDEO_URL, { mode: 'cors' });
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      const video = document.createElement('video');
      video.muted = true;
      video.playsInline = true;
      video.crossOrigin = 'anonymous';
      video.preload = 'auto';
      video.src = objectUrl;

      await new Promise((resolve, reject) => {
        video.onloadedmetadata = () => resolve();
        video.onerror = () => reject();
        setTimeout(() => reject(), 15000);
      });

      const scale = Math.min(1, 1280 / video.videoWidth);
      const scaledWidth = Math.round(video.videoWidth * scale);
      const scaledHeight = Math.round(video.videoHeight * scale);
      const frameCount = Math.max(30, Math.min(120, Math.round(video.duration * 24)));

      for (let i = 0; i < frameCount; i++) {
        const time = (i / (frameCount - 1)) * (video.duration - 0.05);
        video.currentTime = time;
        await new Promise((resolve, reject) => {
          const onSeeked = () => { video.removeEventListener('seeked', onSeeked); resolve(); };
          video.addEventListener('seeked', onSeeked);
          setTimeout(() => { video.removeEventListener('seeked', onSeeked); reject(); }, 3000);
        });
        const bitmap = await createImageBitmap(video, { resizeWidth: scaledWidth, resizeHeight: scaledHeight });
        frames.push(bitmap);
      }

      if (frames.length > 0) {
        framesReady = true;
        canvas.style.visibility = 'visible';
        videoEl.style.display = 'none';
      }
      URL.revokeObjectURL(objectUrl);
    } catch(e) { /* fallback to video seeking */ }
  }

  function getScrollBounds() {
    const vh = window.innerHeight;
    return { start: vh * 0.5, end: document.documentElement.scrollHeight - vh };
  }

  function getProgress() {
    const { start, end } = getScrollBounds();
    const range = end - start;
    if (range <= 0) return 0;
    return Math.max(0, Math.min(1, (window.scrollY - start) / range));
  }

  function drawFrame(frame) {
    const cw = canvas.width, ch = canvas.height;
    const s = Math.max(cw / frame.width, ch / frame.height);
    const dw = frame.width * s, dh = frame.height * s;
    ctx.drawImage(frame, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }

  function videoTick() {
    const progress = getProgress();
    if (framesReady && frames.length > 0) {
      const idx = Math.round(progress * (frames.length - 1));
      if (idx !== lastFrameIndex) {
        lastFrameIndex = idx;
        if (frames[idx]) drawFrame(frames[idx]);
      }
    } else if (videoEl.duration && isFinite(videoEl.duration) && videoEl.readyState >= 1) {
      const target = progress * videoEl.duration;
      if (!videoSeeking && Math.abs(videoEl.currentTime - target) > 0.001) {
        videoSeeking = true;
        videoEl.currentTime = target;
      }
    }
    requestAnimationFrame(videoTick);
  }

  videoEl.addEventListener('seeked', () => { videoSeeking = false; });
  videoEl.addEventListener('stalled', () => { videoSeeking = false; });
  videoEl.addEventListener('loadeddata', () => { videoEl.currentTime = 0; });
  canvas.style.visibility = 'hidden';

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  requestAnimationFrame(videoTick);
  extractFrames();

  // ===================== PARTICLES =====================
  const pCanvas = document.getElementById('particles-canvas');
  const pCtx = pCanvas.getContext('2d');
  let particles = [];

  function resizeParticles() {
    pCanvas.width = window.innerWidth;
    pCanvas.height = window.innerHeight;
    createParticles();
  }

  function createParticles() {
    particles = [];
    const count = Math.floor((pCanvas.width * pCanvas.height) / 12000);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * pCanvas.width,
        y: Math.random() * pCanvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: Math.random() * 1.5 + 0.5,
        opacity: Math.random() * 0.6 + 0.2
      });
    }
  }

  function animateParticles() {
    pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = pCanvas.width;
      if (p.x > pCanvas.width) p.x = 0;
      if (p.y < 0) p.y = pCanvas.height;
      if (p.y > pCanvas.height) p.y = 0;
      pCtx.beginPath();
      pCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      pCtx.fillStyle = `rgba(255,255,255,${p.opacity})`;
      pCtx.fill();
    }
    requestAnimationFrame(animateParticles);
  }

  resizeParticles();
  window.addEventListener('resize', resizeParticles);
  animateParticles();

  // ===================== HERO FADE =====================
  function updateHeroOpacity() {
    const fade = Math.max(0, 1 - window.scrollY / (window.innerHeight * 0.3));
    document.getElementById('hero').style.opacity = fade;
  }
  window.addEventListener('scroll', updateHeroOpacity, { passive: true });

  // ===================== FIXED CARDS =====================
  const fixedCards = document.getElementById('fixed-cards');
  const cardsGrid = fixedCards.querySelector('.grid');

  function tickCards() {
    const trigger = document.getElementById('cards-trigger');
    const rect = trigger.getBoundingClientRect();
    const triggerTop = rect.top + window.scrollY;
    const triggerHeight = rect.height;
    const scrollY = window.scrollY;
    const vh = window.innerHeight;

    const start = triggerTop - vh * 0.5;
    const end = triggerTop + triggerHeight - vh * 0.3;
    const range = end - start;

    let progress = range > 0 ? (scrollY - start) / range : 0;
    progress = Math.max(0, Math.min(1, progress));

    const isActive = scrollY >= start - vh * 0.2 && scrollY <= end + vh * 0.3;
    const fadeIn = Math.min(1, Math.max(0, (scrollY - (start - vh * 0.2)) / (vh * 0.2)));
    const fadeOut = Math.min(1, Math.max(0, (end + vh * 0.3 - scrollY) / (vh * 0.3)));
    const containerOpacity = isActive ? Math.min(fadeIn, fadeOut) : 0;

    fixedCards.style.opacity = containerOpacity;
    fixedCards.style.pointerEvents = containerOpacity > 0.1 ? 'auto' : 'none';

    const isMobile = window.innerWidth < 768;
    const revealPct = progress * 130;
    if (isMobile) {
      cardsGrid.style.maskImage = `linear-gradient(to bottom, black ${revealPct}%, transparent ${revealPct + 20}%)`;
      cardsGrid.style.webkitMaskImage = `linear-gradient(to bottom, black ${revealPct}%, transparent ${revealPct + 20}%)`;
    } else {
      cardsGrid.style.maskImage = `linear-gradient(to right, black ${revealPct}%, transparent ${revealPct + 15}%)`;
      cardsGrid.style.webkitMaskImage = `linear-gradient(to right, black ${revealPct}%, transparent ${revealPct + 15}%)`;
    }

    requestAnimationFrame(tickCards);
  }
  requestAnimationFrame(tickCards);

  // ===================== SECTION 3 INTERSECTION =====================
  const sectionThreeInner = document.getElementById('section-three-inner');
  const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
      sectionThreeInner.classList.add('visible');
      observer.unobserve(sectionThreeInner);
    }
  }, { threshold: 0.15 });
  observer.observe(sectionThreeInner);
})();
</script>
</body>
</html>

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Veldara</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html, body { overflow-x: hidden; }
body { font-family: 'Inter', sans-serif; background: #010101; color: #fff; }

.fixed { position: fixed; }
.absolute { position: absolute; }
.relative { position: relative; }
.inset-0 { top: 0; right: 0; bottom: 0; left: 0; }

#scroll-video-container {
  position: fixed; inset: 0; z-index: -10;
  background: #0a0a0a; top: -20%;
}
#scroll-video-container canvas,
#scroll-video-container video {
  position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
}
#scroll-video-container .overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.2); }

#particles-canvas {
  position: fixed; inset: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 3;
}

nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 2.5rem;
}
nav .logo { font-weight: 700; font-size: 1.25rem; color: #fff; letter-spacing: -0.025em; }
nav .nav-links { display: flex; align-items: center; gap: 1.5rem; }
nav .nav-links a { font-size: 0.875rem; color: #d1d5db; text-decoration: none; transition: color 0.2s; }
nav .nav-links a:hover { color: #fff; }
nav .social { display: flex; align-items: center; gap: 1rem; }
nav .social a { color: #d1d5db; transition: color 0.2s; }
nav .social a:hover { color: #fff; }
nav .social svg { width: 1.25rem; height: 1.25rem; }

#hero {
  position: relative; height: 100vh; width: 100%; display: flex; flex-direction: column;
}
#hero .gradient-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.6), transparent, transparent);
}
#hero .content {
  position: relative; z-index: 10; flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: flex-end; text-align: center;
  padding: 0 1.5rem 6rem;
}
#hero .subtitle { font-size: 0.875rem; color: #9ca3af; margin-bottom: 1rem; letter-spacing: 0.05em; }
#hero h1 { font-size: clamp(1.5rem, 5vw, 3.75rem); font-weight: 600; line-height: 1.15; max-width: 48rem; }
#hero h1 .underlined { position: relative; display: inline-block; }
#hero h1 .underlined .line {
  position: absolute; bottom: 0.25rem; left: 0; width: 100%; height: 10px;
  background: #2C5C88; border-radius: 2px;
}
#hero h1 .underlined span { position: relative; }
#hero .ctas {
  display: flex; align-items: center; gap: 1rem; margin-top: 2.5rem; flex-wrap: wrap; justify-content: center;
}
#hero .code-box {
  display: flex; align-items: center; gap: 0.5rem;
  background: #1a1a1a; border: 1px solid rgba(55,65,81,0.5);
  border-radius: 0.5rem; padding: 0.875rem 2rem;
}
#hero .code-box .prompt { color: #2C5C88; font-family: monospace; font-size: 0.875rem; }
#hero .code-box code { font-size: 0.875rem; color: #e5e7eb; font-family: monospace; }
#hero .cta-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: #2C5C88; color: #fff; font-weight: 500; border-radius: 0.5rem;
  padding: 0.875rem 2rem; font-size: 0.875rem; text-decoration: none; transition: background 0.2s;
}
#hero .cta-btn:hover { background: #3a7aad; }
#hero .bounce-arrow {
  position: relative; z-index: 10; display: flex; justify-content: center; padding-bottom: 2rem;
}
#hero .bounce-arrow svg { width: 1.5rem; height: 1.5rem; color: #6b7280; animation: bounce 1s infinite; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-25%); }
}

#fixed-cards {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 4;
  padding: 2rem 2.5rem; opacity: 0; pointer-events: none;
}
#fixed-cards .grid {
  max-width: 72rem; margin: 0 auto;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.5rem;
}
#fixed-cards .card h3 { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 1rem; }
#fixed-cards .card p { color: #d1d5db; font-size: 0.875rem; line-height: 1.6; }

#section-three {
  position: relative; min-height: 100vh; display: flex; align-items: flex-end;
  justify-content: center; padding: 0 2.5rem 8rem;
}
#section-three .inner {
  position: relative; z-index: 10; display: flex; flex-direction: column;
  align-items: center; text-align: center;
  opacity: 0; transform: translateY(32px); filter: blur(8px);
  transition: opacity 1s ease-out, transform 1s ease-out, filter 1s ease-out;
}
#section-three .inner.visible { opacity: 1; transform: translateY(0); filter: blur(0); }
#section-three .inner p { color: #d1d5db; font-size: 1rem; margin-bottom: 0.75rem; }
#section-three .inner h2 { font-size: clamp(1.875rem, 6vw, 4.5rem); font-weight: 700; }

#content { position: relative; z-index: 2; }

@media (max-width: 768px) {
  nav { padding: 1rem 1.5rem; }
  nav .nav-links { display: none; }
  #hero .content { padding-bottom: 5rem; }
  #hero h1 { font-size: 1.5rem; }
  #hero .ctas { flex-direction: column; }
  #fixed-cards .grid { grid-template-columns: 1fr; gap: 1.5rem; }
  #fixed-cards { padding: 1.5rem 1rem; }
  #section-three { padding-bottom: 5rem; }
}
</style>
</head>
<body>

<div id="scroll-video-container">
  <canvas id="video-canvas"></canvas>
  <video id="video-fallback" muted playsinline preload="auto" crossorigin="anonymous"
    src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260616_212935_bbf608da-62d1-4f25-9be4-c346e4d09cc8.mp4"
  ></video>
  <div class="overlay"></div>
</div>

<canvas id="particles-canvas"></canvas>

<div id="fixed-cards">
  <div class="grid">
    <div class="card">
      <h3>Explore Veldara</h3>
      <p>Veldara merges the elegance of Svelte 5 with the depth of Three.js within easy reach. It's crafted to be robust and adaptable while remaining intuitive and simple to grasp.</p>
    </div>
    <div class="card">
      <h3>Unlock Three.js</h3>
      <p>The web is growing increasingly dimensional. At its heart, Veldara offers a composable declarative API for building performant Three.js experiences on the web.</p>
    </div>
    <div class="card">
      <h3>Connect Everything</h3>
      <p>Veldara ships with tooling for physics, XR, animation, layouting, model loading, and extensive utilities to make building compelling 3D apps for the web effortless.</p>
    </div>
  </div>
</div>

<nav>
  <div style="display:flex;align-items:center;gap:2rem;">
    <span class="logo">veldara</span>
    <div class="nav-links">
      <a href="#">Guides</a>
      <a href="#">Journal</a>
    </div>
  </div>
  <div class="social">
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286z"/></svg></a>
    <a href="#"><svg fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg></a>
  </div>
</nav>

<div id="content">
  <section id="hero">
    <div class="gradient-overlay"></div>
    <div class="content">
      <p class="subtitle">Our Purpose:</p>
      <h1>
        Instantly craft immersive
        <span class="underlined"><span class="line"></span><span>3D worlds</span></span>
        on the web.
      </h1>
      <div class="ctas">
        <div class="code-box">
          <span class="prompt">&gt;</span>
          <code>npm i @veldara/core</code>
        </div>
        <a href="#" class="cta-btn">Get Started <span>&rarr;</span></a>
      </div>
    </div>
    <div class="bounce-arrow">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg>
    </div>
  </section>

  <div style="height:150vh;"></div>
  <div id="cards-trigger" style="height:200vh;"></div>
  <div style="height:100vh;"></div>

  <section id="section-three">
    <div class="inner" id="section-three-inner">
      <p>Presenting</p>
      <h2>Veldara 8</h2>
    </div>
  </section>
</div>

<script>
(function() {
  var VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260616_212935_bbf608da-62d1-4f25-9be4-c346e4d09cc8.mp4';
  var canvas = document.getElementById('video-canvas');
  var videoEl = document.getElementById('video-fallback');
  var ctx = canvas.getContext('2d');
  var frames = [];
  var framesReady = false;
  var lastFrameIndex = -1;
  var videoSeeking = false;

  function resizeCanvas() {
    var dpr = Math.min(devicePixelRatio, 2);
    var rect = canvas.getBoundingClientRect();
    var w = Math.round(rect.width * dpr);
    var h = Math.round(rect.height * dpr);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    lastFrameIndex = -1;
  }

  async function extractFrames() {
    try {
      var response = await fetch(VIDEO_URL, { mode: 'cors' });
      var blob = await response.blob();
      var objectUrl = URL.createObjectURL(blob);
      var video = document.createElement('video');
      video.muted = true; video.playsInline = true; video.crossOrigin = 'anonymous'; video.preload = 'auto'; video.src = objectUrl;
      await new Promise(function(resolve, reject) {
        video.onloadedmetadata = function() { resolve(); };
        video.onerror = function() { reject(); };
        setTimeout(function() { reject(); }, 15000);
      });
      var scale = Math.min(1, 1280 / video.videoWidth);
      var scaledWidth = Math.round(video.videoWidth * scale);
      var scaledHeight = Math.round(video.videoHeight * scale);
      var frameCount = Math.max(30, Math.min(120, Math.round(video.duration * 24)));
      for (var i = 0; i < frameCount; i++) {
        var time = (i / (frameCount - 1)) * (video.duration - 0.05);
        video.currentTime = time;
        await new Promise(function(resolve, reject) {
          var onSeeked = function() { video.removeEventListener('seeked', onSeeked); resolve(); };
          video.addEventListener('seeked', onSeeked);
          setTimeout(function() { video.removeEventListener('seeked', onSeeked); reject(); }, 3000);
        });
        var bitmap = await createImageBitmap(video, { resizeWidth: scaledWidth, resizeHeight: scaledHeight });
        frames.push(bitmap);
      }
      if (frames.length > 0) { framesReady = true; canvas.style.visibility = 'visible'; videoEl.style.display = 'none'; }
      URL.revokeObjectURL(objectUrl);
    } catch(e) {}
  }

  function getProgress() {
    var vh = window.innerHeight;
    var start = vh * 0.5;
    var end = document.documentElement.scrollHeight - vh;
    var range = end - start;
    if (range <= 0) return 0;
    return Math.max(0, Math.min(1, (window.scrollY - start) / range));
  }

  function drawFrame(frame) {
    var cw = canvas.width, ch = canvas.height;
    var s = Math.max(cw / frame.width, ch / frame.height);
    var dw = frame.width * s, dh = frame.height * s;
    ctx.drawImage(frame, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }

  function videoTick() {
    var progress = getProgress();
    if (framesReady && frames.length > 0) {
      var idx = Math.round(progress * (frames.length - 1));
      if (idx !== lastFrameIndex) { lastFrameIndex = idx; if (frames[idx]) drawFrame(frames[idx]); }
    } else if (videoEl.duration && isFinite(videoEl.duration) && videoEl.readyState >= 1) {
      var target = progress * videoEl.duration;
      if (!videoSeeking && Math.abs(videoEl.currentTime - target) > 0.001) { videoSeeking = true; videoEl.currentTime = target; }
    }
    requestAnimationFrame(videoTick);
  }

  videoEl.addEventListener('seeked', function() { videoSeeking = false; });
  videoEl.addEventListener('stalled', function() { videoSeeking = false; });
  videoEl.addEventListener('loadeddata', function() { videoEl.currentTime = 0; });
  canvas.style.visibility = 'hidden';
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  requestAnimationFrame(videoTick);
  extractFrames();

  // Particles
  var pCanvas = document.getElementById('particles-canvas');
  var pCtx = pCanvas.getContext('2d');
  var particles = [];
  function resizeParticles() { pCanvas.width = window.innerWidth; pCanvas.height = window.innerHeight; createParticles(); }
  function createParticles() {
    particles = [];
    var count = Math.floor((pCanvas.width * pCanvas.height) / 12000);
    for (var i = 0; i < count; i++) {
      particles.push({ x: Math.random()*pCanvas.width, y: Math.random()*pCanvas.height, vx: (Math.random()-0.5)*0.3, vy: (Math.random()-0.5)*0.3, size: Math.random()*1.5+0.5, opacity: Math.random()*0.6+0.2 });
    }
  }
  function animateParticles() {
    pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i]; p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = pCanvas.width; if (p.x > pCanvas.width) p.x = 0;
      if (p.y < 0) p.y = pCanvas.height; if (p.y > pCanvas.height) p.y = 0;
      pCtx.beginPath(); pCtx.arc(p.x, p.y, p.size, 0, Math.PI*2);
      pCtx.fillStyle = 'rgba(255,255,255,' + p.opacity + ')'; pCtx.fill();
    }
    requestAnimationFrame(animateParticles);
  }
  resizeParticles(); window.addEventListener('resize', resizeParticles); animateParticles();

  // Hero fade
  window.addEventListener('scroll', function() {
    var fade = Math.max(0, 1 - window.scrollY / (window.innerHeight * 0.3));
    document.getElementById('hero').style.opacity = fade;
  }, { passive: true });

  // Fixed Cards
  var fixedCards = document.getElementById('fixed-cards');
  var cardsGrid = fixedCards.querySelector('.grid');
  function tickCards() {
    var trigger = document.getElementById('cards-trigger');
    var rect = trigger.getBoundingClientRect();
    var triggerTop = rect.top + window.scrollY;
    var triggerHeight = rect.height;
    var scrollY = window.scrollY; var vh = window.innerHeight;
    var start = triggerTop - vh * 0.5;
    var end = triggerTop + triggerHeight - vh * 0.3;
    var range = end - start;
    var progress = range > 0 ? (scrollY - start) / range : 0;
    progress = Math.max(0, Math.min(1, progress));
    var isActive = scrollY >= start - vh*0.2 && scrollY <= end + vh*0.3;
    var fadeIn = Math.min(1, Math.max(0, (scrollY - (start - vh*0.2)) / (vh*0.2)));
    var fadeOut = Math.min(1, Math.max(0, (end + vh*0.3 - scrollY) / (vh*0.3)));
    var containerOpacity = isActive ? Math.min(fadeIn, fadeOut) : 0;
    fixedCards.style.opacity = containerOpacity;
    fixedCards.style.pointerEvents = containerOpacity > 0.1 ? 'auto' : 'none';
    var isMobile = window.innerWidth < 768;
    var revealPct = progress * 130;
    if (isMobile) {
      cardsGrid.style.maskImage = 'linear-gradient(to bottom, black '+revealPct+'%, transparent '+(revealPct+20)+'%)';
      cardsGrid.style.webkitMaskImage = 'linear-gradient(to bottom, black '+revealPct+'%, transparent '+(revealPct+20)+'%)';
    } else {
      cardsGrid.style.maskImage = 'linear-gradient(to right, black '+revealPct+'%, transparent '+(revealPct+15)+'%)';
      cardsGrid.style.webkitMaskImage = 'linear-gradient(to right, black '+revealPct+'%, transparent '+(revealPct+15)+'%)';
    }
    requestAnimationFrame(tickCards);
  }
  requestAnimationFrame(tickCards);

  // Section 3 intersection
  var inner = document.getElementById('section-three-inner');
  var obs = new IntersectionObserver(function(entries) {
    if (entries[0].isIntersecting) { inner.classList.add('visible'); obs.unobserve(inner); }
  }, { threshold: 0.15 });
  obs.observe(inner);
})();
</script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Health Portal"
template_id: "dc375a6e-c5f2-4195-b6b0-6067f7c03e6c"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Health Portal

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `dc375a6e-c5f2-4195-b6b0-6067f7c03e6c`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Health Portal](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/21768bc8-9ece-46b2-9e60-38b8a3595fd2.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a single-page dental clinic landing page using **React + Vite + TypeScript + Tailwind CSS**. No external UI libraries, no icon libraries. Everything lives in one `App.tsx` file. The page has 3 full-screen sections, a splash screen, and a fixed navbar.

---

### SETUP

**Font:** "Open Sauce One" loaded via these exact links in `index.html` `<head>`:
```html
<link href="https://db.onlinewebfonts.com/c/1cd1e7d71e048159076fd90b39846902?family=Open+Sauce+One" rel="stylesheet">
<link href="https://db.onlinewebfonts.com/c/42acf9aa4a6dc2f2886a3f682e337ead?family=Open+Sauce+One+Bold" rel="stylesheet">
```

**Title:** "Dental Health - Quality Healthcare"

**Global CSS (index.css):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body, #root {
    height: 100%;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: 'Open Sauce One', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}
```

**Tailwind config:** Default, no extensions. Content: `['./index.html', './src/**/*.{js,ts,jsx,tsx}']`.

---

### IMAGE URLS (use these EXACT URLs)

```ts
const HERO_IMAGE = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_113640_ccf3cf97-d447-425b-a134-d7b09fc743fc.png&w=1280&q=85';

const SECTION2_IMAGE = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_114219_414dfe80-f15c-4e25-bf52-b13721f4bd88.png&w=1280&q=85';

const SECTION3_IMG1 = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_115253_c19ab167-8dd5-48b4-967d-b9f0d9d6e8fb.png&w=1280&q=85';

const SECTION3_IMG2 = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_115237_fc519057-6e87-4abf-999a-9610b8b085b4.png&w=1280&q=85';

const SECTION3_BG = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_114355_752ba9e6-0942-4abb-9047-5d9bb16632e9.png&w=1280&q=85';
```

---

### DATA CONSTANTS

```ts
const featureBars = ['Advanced Dentistry', 'High Quality Equipment', 'Friendly Staff'];

const services = [
  { name: 'Dental\nVeneers', num: '01', active: true },
  { name: 'Dental\nCrowns', num: '02', active: false },
  { name: 'Teeth\nWhitening', num: '03', active: false },
  { name: 'Dental\nImplants', num: null, active: false },
];
```

---

### CORE TECHNICAL CONCEPT: "MASKED CARDS"

Sections 1 and 2 use a single large background image shared across multiple cards. Each card shows a different "window" into the same image, creating a cohesive mosaic effect. Implementation:

**`useMaskPositions` hook:**
- Takes a ref to the section container and a ref to an array of card elements.
- Uses `ResizeObserver` on the section container.
- For each card, computes `{ x, y, sw, sh }` where x/y is the card's top-left offset relative to the section, sw/sh is the section's width/height.

**`useImageWidth` hook:**
- Loads the image in a `new Image()` object.
- Calculates: `renderWidth = img.naturalWidth * (sectionHeight / img.naturalHeight)`.
- Returns how wide the image would be if scaled to fill the section height.

**`MaskedCard` component:**
- Props: `bgImage`, `position` (from useMaskPositions), `imageWidth` (from useImageWidth), `focalX` (0-1 float), `className`, `children`, `cardRef`, `style`.
- Calculates `overflow = imageWidth > position.sw ? imageWidth - position.sw : 0`, then `focalOffset = overflow * focalX`.
- Applies inline style:
  ```
  backgroundImage: url(bgImage)
  backgroundSize: auto [position.sh]px
  backgroundPosition: -[position.x + focalOffset]px -[position.y]px
  backgroundRepeat: no-repeat
  ```
- `focalX` values: Section 1 mobile=0.7, desktop=0.8. Section 2 mobile=0.65, desktop=0.8.

**`useIsMobile` hook:**
- Listens to `window.matchMedia('(max-width: 767px)')` change events.
- Returns boolean.

---

### ANIMATION: `useStaggeredReveal` hook

- Takes `count` (number of elements) and `threshold` (IntersectionObserver threshold, default 0.15).
- Returns `{ containerRef, getAnimStyle }`.
- `containerRef` is attached to the section; when it crosses the threshold, `visible` becomes true (fires once).
- `getAnimStyle(index)` returns:
  ```css
  opacity: visible ? 1 : 0
  transform: visible ? 'translateY(0)' : 'translateY(24px)'
  transition: opacity 0.6s cubic-bezier(0.16,1,0.3,1) [index*120]ms,
              transform 0.6s cubic-bezier(0.16,1,0.3,1) [index*120]ms
  ```

---

### SPLASH SCREEN

- Fixed overlay covering viewport, `z-[100]`, white background.
- Number counter displayed at **bottom-left** (`items-end justify-start`).
- Counter style: `text-7xl md:text-9xl font-bold tabular-nums p-6 md:p-10 leading-none`, black text.
- Counts from 0 to 100 over exactly 2000ms (20ms per step, 100 steps).
- After reaching 100: wait 200ms, then set `exiting=true` which triggers `opacity-0` with `transition-opacity duration-700`.
- After 900ms total from reaching 100, call `onComplete()` which removes splash from DOM.

---

### NAVBAR

**Container:** `fixed top-0 left-0 right-0 z-50`, `flex items-center justify-between`, `px-4 md:px-6 py-2 md:py-3`, `bg-white/80 backdrop-blur-md`.

**Logo (left side):**
- Two lines stacked: "Dental" and "Health"
- Wrapper: `flex flex-col`
- Text: `text-xl md:text-2xl font-extrabold uppercase tracking-tight leading-none`
- Second line has `-mt-1.5 md:-mt-2` for tight spacing
- Below logo text: "quality healthcare" in `text-[8px] md:text-[9px] font-medium leading-none mt-1.5 md:mt-2`

**Desktop nav (hidden on mobile with `hidden md:block`):**
- "Menu" button: `px-6 py-3 bg-white rounded-full border border-black text-sm font-semibold`, hover: `hover:bg-black hover:text-white transition-colors duration-200`
- "Dental Emergency" text: `text-sm font-semibold text-black`

**Mobile hamburger (visible only on mobile with `md:hidden`):**
- Container: `w-10 h-10 flex items-center justify-center`, `relative`
- 3 spans, each: `absolute h-0.5 w-6 bg-black rounded-full`
- Transition: `transition-all duration-300 ease-[cubic-bezier(0.76,0,0.24,1)]`
- Closed state: top span `-translate-y-2`, middle `opacity-100 scale-x-100`, bottom `translate-y-2`
- Open state: top `rotate-45 translate-y-0`, middle `opacity-0 scale-x-0`, bottom `-rotate-45 translate-y-0`

**Mobile menu overlay (`md:hidden`):**
- Outer: `fixed inset-0 z-40`, pointer-events toggled based on open state
- Backdrop: `absolute inset-0 bg-black/20 backdrop-blur-sm`, fades opacity. Clicking closes menu.
- Panel: `absolute top-0 right-0 h-full w-[85%] max-w-sm bg-white shadow-2xl`, slides with `translate-x-0` (open) / `translate-x-full` (closed), `duration-500 ease-[cubic-bezier(0.76,0,0.24,1)]`
- Content: `flex flex-col justify-center h-full px-8 gap-1`
- Nav links: ['Home', 'Services', 'About', 'Gallery', 'Contact']
  - Each: `text-4xl font-bold text-black hover:text-neutral-500`
  - Staggered entrance: `opacity-0 translate-x-8` -> `opacity-100 translate-x-0`, `transitionDelay: ${100 + i * 60}ms` when open
  - `transition-all duration-500 ease-[cubic-bezier(0.76,0,0.24,1)]`
- Bottom section: `mt-8 pt-8 border-t border-neutral-200`, delayed 450ms
  - "Dental Emergency" text: `text-sm font-semibold text-black mb-4`
  - Button: `w-full px-6 py-4 bg-black rounded-full text-white text-sm font-semibold hover:bg-neutral-800 transition-colors duration-200`, text "Book Appointment"
- When open: `document.body.style.overflow = 'hidden'`. Cleanup on unmount.

---

### SECTION 1 - HERO

**Container:** `<section>`, `h-screen w-full overflow-hidden flex flex-col`, `pt-24 md:pt-24 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2`

Attach both `section1Ref` and `s1Reveal.containerRef` to this element.

Uses `HERO_IMAGE` as shared background via MaskedCard technique.

**3 Feature Bars** (mapped from `featureBars` array):
- Each is a `MaskedCard` with: `w-full h-14 md:h-20 shrink-0 rounded-xl md:rounded-2xl overflow-hidden relative`
- Animated with `s1Reveal.getAnimStyle(i)` for i=0,1,2
- Content: `<span>` centered vertically and horizontally (`flex items-center justify-center h-full`), `text-black text-lg md:text-3xl font-bold text-center`, `relative z-10`

**Main Hero Card** (4th card, index 3):
- `MaskedCard`: `w-full flex-1 min-h-0 rounded-xl md:rounded-2xl overflow-hidden relative`
- Animated with `s1Reveal.getAnimStyle(3)`
- **Top-left text:** `absolute top-4 left-4 md:top-7 md:left-7`, `text-black text-xs md:text-sm font-semibold leading-4 md:leading-5 max-w-[200px] md:max-w-[300px] z-10`
  - Content: "We wish to provide professional dental services" `<br/>` "that match the current technologies"
- **Bottom-left block:** `absolute bottom-5 left-3 md:bottom-8 md:left-4 z-10`
  - Label: `block text-black text-xs md:text-sm font-semibold mb-1 md:mb-2`, text "Trusted Dentist in West New York"
  - Heading: `<h1>` with `text-black text-[clamp(3rem,11vw,11rem)] font-bold leading-[0.79] tracking-tight`, content: "Dental" `<br/>` "Care"
- **Bottom-right text:** `absolute bottom-6 right-4 md:bottom-10 md:right-8`, `text-white text-xs md:text-sm font-semibold z-10`, content: "Free Consultation"

---

### SECTION 2 - SMILE GALLERY

**Container:** `<section>`, `min-h-screen md:h-screen w-full overflow-hidden flex flex-col`, `pt-1.5 md:pt-2 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2`

Attach both `section2Ref` and `s2Reveal.containerRef` to this element.

Uses `SECTION2_IMAGE` as shared background via MaskedCard technique.

**Grid container:** `flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 grid-rows-[auto_auto_auto_auto] md:grid-rows-[1fr_1fr_0.8fr] gap-1.5 md:gap-2`

**Card 0 - Top Left ("Smile Gallery"):**
- `MaskedCard`: `rounded-xl md:rounded-2xl overflow-hidden relative min-h-[160px] md:min-h-0`
- Animated: `s2Reveal.getAnimStyle(0)`
- Heading: `absolute top-4 left-5 md:top-6 md:left-7`, `text-white md:text-black text-2xl md:text-3xl font-bold z-10`, text "Smile Gallery"
- Subtitle: `absolute bottom-4 left-5 md:bottom-6 md:left-7`, `text-white md:text-black text-xs md:text-sm font-semibold z-10`, text "Our cosmetic dental work"

**Card 1 - Top Right (spans 2 rows on desktop):**
- `MaskedCard`: `md:row-span-2 rounded-xl md:rounded-2xl overflow-hidden relative min-h-[200px] md:min-h-0`
- Animated: `s2Reveal.getAnimStyle(1)`
- Text: `absolute bottom-16 left-5 md:bottom-20 md:left-7`, `text-white text-xs md:text-sm font-semibold leading-4 md:leading-5 z-10`, content: "If you want a gorgeous smile," `<br/>` "call us to ask about a smile makeover."
- Button: `absolute bottom-4 right-4 md:bottom-6 md:right-6`, `px-5 py-3 md:px-8 md:py-5 bg-white rounded-full text-black text-base md:text-xl font-bold z-10 hover:scale-105 transition-transform`, text "Call Us"

**Card 2 - Bottom Left ("Smile makeover"):**
- `MaskedCard`: `rounded-xl md:rounded-2xl overflow-hidden relative min-h-[160px] md:min-h-0`
- Animated: `s2Reveal.getAnimStyle(2)`
- Heading: `absolute top-4 left-5 md:top-6 md:left-7`, `text-white md:text-black text-[clamp(3rem,7vw,6rem)] font-bold leading-[0.9] z-10`, content: "Smile" `<br/>` "makeover"

**Card 3 - Bottom Full Width (Services):**
- `MaskedCard`: `col-span-1 md:col-span-2 rounded-xl md:rounded-2xl overflow-hidden relative min-h-[200px] md:min-h-0`
- Animated: `s2Reveal.getAnimStyle(3)`
- Inner container: `absolute inset-0 z-10 flex flex-wrap md:flex-nowrap gap-1.5 md:gap-2 p-2 md:p-3`
- 4 service sub-cards mapped from `services` array:
  - Container: `flex-1 min-w-[calc(50%-4px)] md:min-w-0 rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between`
  - Active: `bg-white/90 backdrop-blur-md`
  - Inactive: `bg-white/20 backdrop-blur-xl`
  - Service name: `<h3>` with `text-xl md:text-4xl font-bold leading-[1.05] whitespace-pre-line`, color: active=`text-black`, inactive=`text-white`
  - Number badge (if `svc.num` exists): `self-end w-8 h-8 md:w-12 md:h-12 rounded-full border flex items-center justify-center text-xs md:text-sm font-semibold`
    - Active: `border-black text-black`
    - Inactive: `border-white text-white`

---

### SECTION 3 - IMPLANT DENTISTRY

**Container:** `<section>`, `min-h-screen md:h-screen w-full overflow-hidden flex flex-col`, `pt-1.5 md:pt-2 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2`

Attach `s3Reveal.containerRef` to this element.

Does NOT use MaskedCard technique. Uses regular `<img>` tags and solid backgrounds.

**Grid:** `flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 gap-1.5 md:gap-2`

#### LEFT COLUMN: `flex flex-col gap-1.5 md:gap-2`

**1. Heading Card:**
- `<div>`: `rounded-xl md:rounded-2xl bg-stone-50 p-5 md:p-7 flex flex-col justify-between flex-[1.2] min-h-[180px] md:min-h-0`
- Animated: `s3Reveal.getAnimStyle(0)`
- Heading: `<h2>` with `text-[clamp(3rem,7vw,6.5rem)] font-bold leading-[0.95] text-black`, content: "Implant" `<br/>` "Dentistry"
- Subtitle: `<p>` with `text-xs md:text-sm font-semibold text-black`, text "Restore Missing Teeth"

**2. Two Image Cards (side by side):**
- Wrapper: `<div>` with `flex gap-1.5 md:gap-2 flex-1 min-h-[140px] md:min-h-0`
- Animated: `s3Reveal.getAnimStyle(1)`
- Left image: `<div className="flex-1 rounded-xl md:rounded-2xl overflow-hidden"><img src={SECTION3_IMG1} alt="Dental implant procedure" className="w-full h-full object-cover" /></div>`
- Right image: `<div className="flex-1 rounded-xl md:rounded-2xl overflow-hidden"><img src={SECTION3_IMG2} alt="Dental restoration" className="w-full h-full object-cover" /></div>`

**3. Consultation Card:**
- `<div>`: `rounded-xl md:rounded-2xl bg-zinc-200 p-5 md:p-7 flex items-end justify-between flex-[0.8] min-h-[160px] md:min-h-0`
- Animated: `s3Reveal.getAnimStyle(2)`
- Left content block:
  - Label: `<p>` with `text-xs md:text-sm font-semibold text-black mb-2 md:mb-3`, text "Consultation"
  - Heading: `<h3>` with `text-xl md:text-3xl font-bold text-black leading-6 md:leading-8`, content: "Dental" `<br/>` "Restoration" `<br/>` "Services"
- Button: `px-5 py-3 md:px-8 md:py-5 bg-white rounded-full text-black text-base md:text-xl font-bold hover:scale-105 transition-transform`, text "Book Online"

#### RIGHT COLUMN: Single tall image card

- `<div>`: `rounded-xl md:rounded-2xl overflow-hidden relative min-h-[350px] md:min-h-0`
- Animated: `s3Reveal.getAnimStyle(3)`
- Background image: `<img src={SECTION3_BG} alt="Smiling patient" className="w-full h-full object-cover" />`
- **Overlay container:** `absolute bottom-3 left-3 right-3 md:bottom-5 md:left-5 md:right-5 flex gap-1.5 md:gap-2`

**Overlay Card 1 (white, left):**
- `flex-1 bg-white rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between h-36 md:h-52`
- Heading: `<h4>` with `text-lg md:text-2xl font-bold text-black leading-5 md:leading-7`, content: "The Process" `<br/>` "of Installing" `<br/>` "Implants"
- Arrow icon: `self-end w-9 h-9 md:w-12 md:h-12 rounded-full border border-black flex items-center justify-center`
  - SVG: `width="14" height="14" viewBox="0 0 14 14" fill="none"`, class `rotate-[-45deg]`
  - Path: `d="M1 7h12m0 0L8 2m5 5L8 12"` with `stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"`

**Overlay Card 2 (glass, right):**
- `flex-1 bg-white/20 backdrop-blur-xl rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between h-36 md:h-52`
- Heading: `<h4>` with `text-lg md:text-2xl font-bold text-white leading-5 md:leading-7`, content: "Caring" `<br/>` "for Dental" `<br/>` "Implants"
- Arrow icon: `self-end w-9 h-9 md:w-12 md:h-12 rounded-full border border-white flex items-center justify-center`
  - Same SVG as above but with added class `text-white`

---

### OUTER WRAPPER

The entire app is wrapped in `<div className="bg-white">` containing:
1. `{showSplash && <SplashScreen />}` (conditionally rendered)
2. `<Navbar />`
3. Section 1
4. Section 2
5. Section 3

---

### KEY DESIGN RULES

- **Spacing between sections:** Only `pb-1.5 md:pb-2` on each section and `pt-1.5 md:pt-2` on sections 2 and 3 -- virtually seamless.
- **Border radius:** All cards use `rounded-xl md:rounded-2xl` with `overflow-hidden`.
- **Color palette:** Strictly black, white, and translucent white (`bg-white/20`, `bg-white/90`) with `backdrop-blur-md` or `backdrop-blur-xl`.
- **Background fills:** `bg-stone-50` and `bg-zinc-200` for Section 3 solid cards.
- **Typography:** Heavy bold/extrabold, `clamp()` for responsive headings, extremely tight leading (0.79, 0.9, 0.95, 1.05).
- **Interactions:** `hover:scale-105 transition-transform` on CTA buttons.
- **Responsive:** Single `md:` (768px) breakpoint. Stacked on mobile, grid on desktop.
- **No external packages** beyond React and Tailwind.

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dental Health - Quality Healthcare</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <link href="https://db.onlinewebfonts.com/c/1cd1e7d71e048159076fd90b39846902?family=Open+Sauce+One" rel="stylesheet">
  <link href="https://db.onlinewebfonts.com/c/42acf9aa4a6dc2f2886a3f682e337ead?family=Open+Sauce+One+Bold" rel="stylesheet">
  <style>
    html, body, #root {
      height: 100%;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Open Sauce One', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    const { useRef, useEffect, useState, useCallback } = React;

    const HERO_IMAGE = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_113640_ccf3cf97-d447-425b-a134-d7b09fc743fc.png&w=1280&q=85';
    const SECTION2_IMAGE = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_114219_414dfe80-f15c-4e25-bf52-b13721f4bd88.png&w=1280&q=85';
    const SECTION3_IMG1 = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_115253_c19ab167-8dd5-48b4-967d-b9f0d9d6e8fb.png&w=1280&q=85';
    const SECTION3_IMG2 = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_115237_fc519057-6e87-4abf-999a-9610b8b085b4.png&w=1280&q=85';
    const SECTION3_BG = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_114355_752ba9e6-0942-4abb-9047-5d9bb16632e9.png&w=1280&q=85';

    const featureBars = ['Advanced Dentistry', 'High Quality Equipment', 'Friendly Staff'];
    const services = [
      { name: 'Dental\nVeneers', num: '01', active: true },
      { name: 'Dental\nCrowns', num: '02', active: false },
      { name: 'Teeth\nWhitening', num: '03', active: false },
      { name: 'Dental\nImplants', num: null, active: false },
    ];

    function useMaskPositions(sectionRef, cardRefs) {
      const [positions, setPositions] = useState([]);
      const measure = useCallback(() => {
        if (!sectionRef.current || !cardRefs.current) return;
        const sRect = sectionRef.current.getBoundingClientRect();
        const newPositions = cardRefs.current.map((card) => {
          if (!card) return { x: 0, y: 0, sw: sRect.width, sh: sRect.height };
          const cRect = card.getBoundingClientRect();
          return { x: cRect.left - sRect.left, y: cRect.top - sRect.top, sw: sRect.width, sh: sRect.height };
        });
        setPositions(newPositions);
      }, [sectionRef, cardRefs]);

      useEffect(() => {
        measure();
        const observer = new ResizeObserver(measure);
        if (sectionRef.current) observer.observe(sectionRef.current);
        return () => observer.disconnect();
      }, [measure, sectionRef]);
      return positions;
    }

    function useImageWidth(src, sectionHeight) {
      const [renderWidth, setRenderWidth] = useState(null);
      useEffect(() => {
        const img = new Image();
        img.onload = () => {
          const scale = sectionHeight / img.naturalHeight;
          setRenderWidth(img.naturalWidth * scale);
        };
        img.src = src;
      }, [src, sectionHeight]);
      return renderWidth;
    }

    function MaskedCard({ bgImage, position, className, children, cardRef, imageWidth, focalX = 0.8, style }) {
      let bgStyle = {};
      if (position) {
        const overflow = imageWidth && imageWidth > position.sw ? imageWidth - position.sw : 0;
        const focalOffset = overflow * focalX;
        bgStyle = {
          backgroundImage: `url(${bgImage})`,
          backgroundSize: `auto ${position.sh}px`,
          backgroundPosition: `-${position.x + focalOffset}px -${position.y}px`,
          backgroundRepeat: 'no-repeat',
        };
      }
      return <div ref={cardRef} className={className} style={{ ...bgStyle, ...style }}>{children}</div>;
    }

    function useStaggeredReveal(count, threshold = 0.15) {
      const containerRef = useRef(null);
      const [visible, setVisible] = useState(false);
      useEffect(() => {
        if (!containerRef.current) return;
        const observer = new IntersectionObserver(([entry]) => {
          if (entry.isIntersecting) { setVisible(true); observer.disconnect(); }
        }, { threshold });
        observer.observe(containerRef.current);
        return () => observer.disconnect();
      }, [threshold]);

      const getAnimStyle = (index) => ({
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(24px)',
        transition: `opacity 0.6s cubic-bezier(0.16,1,0.3,1) ${index * 120}ms, transform 0.6s cubic-bezier(0.16,1,0.3,1) ${index * 120}ms`,
      });
      return { containerRef, getAnimStyle, count };
    }

    function useIsMobile(breakpoint = 768) {
      const [isMobile, setIsMobile] = useState(window.innerWidth < breakpoint);
      useEffect(() => {
        const mq = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);
        const handler = (e) => setIsMobile(e.matches);
        mq.addEventListener('change', handler);
        setIsMobile(mq.matches);
        return () => mq.removeEventListener('change', handler);
      }, [breakpoint]);
      return isMobile;
    }

    function Navbar() {
      const [isOpen, setIsOpen] = useState(false);
      useEffect(() => {
        document.body.style.overflow = isOpen ? 'hidden' : '';
        return () => { document.body.style.overflow = ''; };
      }, [isOpen]);

      return (
        <>
          <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 md:px-6 py-2 md:py-3 bg-white/80 backdrop-blur-md">
            <div className="flex flex-col">
              <span className="text-black text-xl md:text-2xl font-extrabold uppercase tracking-tight flex flex-col leading-none">
                <span>Dental</span>
                <span className="-mt-1.5 md:-mt-2">Health</span>
              </span>
              <span className="text-black text-[8px] md:text-[9px] font-medium leading-none mt-1.5 md:mt-2">quality healthcare</span>
            </div>
            <button className="hidden md:block px-6 py-3 bg-white rounded-full border border-black text-sm font-semibold hover:bg-black hover:text-white transition-colors duration-200">Menu</button>
            <span className="hidden md:block text-sm font-semibold text-black">Dental Emergency</span>
            <button onClick={() => setIsOpen(!isOpen)} className="md:hidden relative w-10 h-10 flex items-center justify-center" aria-label="Toggle menu">
              <span className={`absolute h-0.5 w-6 bg-black rounded-full transition-all duration-300 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'rotate-45 translate-y-0' : '-translate-y-2'}`} />
              <span className={`absolute h-0.5 w-6 bg-black rounded-full transition-all duration-300 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'opacity-0 scale-x-0' : 'opacity-100 scale-x-100'}`} />
              <span className={`absolute h-0.5 w-6 bg-black rounded-full transition-all duration-300 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? '-rotate-45 translate-y-0' : 'translate-y-2'}`} />
            </button>
          </nav>

          <div className={`fixed inset-0 z-40 md:hidden transition-all duration-500 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}>
            <div className={`absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity duration-500 ${isOpen ? 'opacity-100' : 'opacity-0'}`} onClick={() => setIsOpen(false)} />
            <div className={`absolute top-0 right-0 h-full w-[85%] max-w-sm bg-white shadow-2xl transition-transform duration-500 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
              <div className="flex flex-col justify-center h-full px-8 gap-1">
                {['Home', 'Services', 'About', 'Gallery', 'Contact'].map((item, i) => (
                  <a key={item} href="#" onClick={() => setIsOpen(false)} className={`text-4xl font-bold text-black hover:text-neutral-500 transition-all duration-500 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`} style={{ transitionDelay: isOpen ? `${100 + i * 60}ms` : '0ms' }}>{item}</a>
                ))}
                <div className={`mt-8 pt-8 border-t border-neutral-200 transition-all duration-500 ease-[cubic-bezier(0.76,0,0.24,1)] ${isOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`} style={{ transitionDelay: isOpen ? '450ms' : '0ms' }}>
                  <p className="text-sm font-semibold text-black mb-4">Dental Emergency</p>
                  <button className="w-full px-6 py-4 bg-black rounded-full text-white text-sm font-semibold hover:bg-neutral-800 transition-colors duration-200">Book Appointment</button>
                </div>
              </div>
            </div>
          </div>
        </>
      );
    }

    function SplashScreen({ onComplete }) {
      const [count, setCount] = useState(0);
      const [exiting, setExiting] = useState(false);
      useEffect(() => {
        const duration = 2000; const steps = 100; const interval = duration / steps; let current = 0;
        const timer = setInterval(() => {
          current++;
          setCount(current);
          if (current >= 100) { clearInterval(timer); setTimeout(() => setExiting(true), 200); setTimeout(() => onComplete(), 900); }
        }, interval);
        return () => clearInterval(timer);
      }, [onComplete]);

      return (
        <div className={`fixed inset-0 z-[100] bg-white flex items-end justify-start transition-opacity duration-700 ${exiting ? 'opacity-0' : 'opacity-100'}`}>
          <span className="text-black text-7xl md:text-9xl font-bold tabular-nums p-6 md:p-10 leading-none">{count}</span>
        </div>
      );
    }

    function App() {
      const [showSplash, setShowSplash] = useState(true);
      const handleSplashComplete = useCallback(() => setShowSplash(false), []);
      const isMobile = useIsMobile();
      const focalS1 = isMobile ? 0.7 : 0.8;
      const focalS2 = isMobile ? 0.65 : 0.8;

      const section1Ref = useRef(null);
      const section1Cards = useRef([]);
      const section1Positions = useMaskPositions(section1Ref, section1Cards);

      const section2Ref = useRef(null);
      const section2Cards = useRef([]);
      const section2Positions = useMaskPositions(section2Ref, section2Cards);

      const s1Height = section1Positions[0]?.sh ?? window.innerHeight;
      const s2Height = section2Positions[0]?.sh ?? window.innerHeight;
      const heroImgWidth = useImageWidth(HERO_IMAGE, s1Height);
      const s2ImgWidth = useImageWidth(SECTION2_IMAGE, s2Height);

      const s1Reveal = useStaggeredReveal(4, 0.1);
      const s2Reveal = useStaggeredReveal(4, 0.15);
      const s3Reveal = useStaggeredReveal(4, 0.15);

      const setSection1Card = (index) => (el) => { section1Cards.current[index] = el; };
      const setSection2Card = (index) => (el) => { section2Cards.current[index] = el; };

      return (
        <div className="bg-white">
          {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
          <Navbar />

          {/* Section 1 - Hero */}
          <section ref={(el) => { section1Ref.current = el; s1Reveal.containerRef.current = el; }} className="h-screen w-full overflow-hidden flex flex-col pt-24 md:pt-24 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2">
            {featureBars.map((feature, i) => (
              <MaskedCard key={feature} bgImage={HERO_IMAGE} position={section1Positions[i]} cardRef={setSection1Card(i)} imageWidth={heroImgWidth} focalX={focalS1} className="w-full h-14 md:h-20 shrink-0 rounded-xl md:rounded-2xl overflow-hidden relative" style={s1Reveal.getAnimStyle(i)}>
                <span className="relative z-10 flex items-center justify-center h-full text-black text-lg md:text-3xl font-bold text-center">{feature}</span>
              </MaskedCard>
            ))}
            <MaskedCard bgImage={HERO_IMAGE} position={section1Positions[3]} cardRef={setSection1Card(3)} imageWidth={heroImgWidth} focalX={focalS1} className="w-full flex-1 min-h-0 rounded-xl md:rounded-2xl overflow-hidden relative" style={s1Reveal.getAnimStyle(3)}>
              <p className="absolute top-4 left-4 md:top-7 md:left-7 text-black text-xs md:text-sm font-semibold leading-4 md:leading-5 max-w-[200px] md:max-w-[300px] z-10">We wish to provide professional dental services<br />that match the current technologies</p>
              <div className="absolute bottom-5 left-3 md:bottom-8 md:left-4 z-10">
                <span className="block text-black text-xs md:text-sm font-semibold mb-1 md:mb-2">Trusted Dentist in West New York</span>
                <h1 className="text-black text-[clamp(3rem,11vw,11rem)] font-bold leading-[0.79] tracking-tight">Dental<br />Care</h1>
              </div>
              <span className="absolute bottom-6 right-4 md:bottom-10 md:right-8 text-white text-xs md:text-sm font-semibold z-10">Free Consultation</span>
            </MaskedCard>
          </section>

          {/* Section 2 - Smile Gallery */}
          <section ref={(el) => { section2Ref.current = el; s2Reveal.containerRef.current = el; }} className="min-h-screen md:h-screen w-full overflow-hidden flex flex-col pt-1.5 md:pt-2 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2">
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 grid-rows-[auto_auto_auto_auto] md:grid-rows-[1fr_1fr_0.8fr] gap-1.5 md:gap-2">
              <MaskedCard bgImage={SECTION2_IMAGE} position={section2Positions[0]} cardRef={setSection2Card(0)} imageWidth={s2ImgWidth} focalX={focalS2} className="rounded-xl md:rounded-2xl overflow-hidden relative min-h-[160px] md:min-h-0" style={s2Reveal.getAnimStyle(0)}>
                <h2 className="absolute top-4 left-5 md:top-6 md:left-7 text-white md:text-black text-2xl md:text-3xl font-bold z-10">Smile Gallery</h2>
                <p className="absolute bottom-4 left-5 md:bottom-6 md:left-7 text-white md:text-black text-xs md:text-sm font-semibold z-10">Our cosmetic dental work</p>
              </MaskedCard>

              <MaskedCard bgImage={SECTION2_IMAGE} position={section2Positions[1]} cardRef={setSection2Card(1)} imageWidth={s2ImgWidth} focalX={focalS2} className="md:row-span-2 rounded-xl md:rounded-2xl overflow-hidden relative min-h-[200px] md:min-h-0" style={s2Reveal.getAnimStyle(1)}>
                <p className="absolute bottom-16 left-5 md:bottom-20 md:left-7 text-white text-xs md:text-sm font-semibold leading-4 md:leading-5 z-10">If you want a gorgeous smile,<br />call us to ask about a smile makeover.</p>
                <button className="absolute bottom-4 right-4 md:bottom-6 md:right-6 px-5 py-3 md:px-8 md:py-5 bg-white rounded-full text-black text-base md:text-xl font-bold z-10 hover:scale-105 transition-transform">Call Us</button>
              </MaskedCard>

              <MaskedCard bgImage={SECTION2_IMAGE} position={section2Positions[2]} cardRef={setSection2Card(2)} imageWidth={s2ImgWidth} focalX={focalS2} className="rounded-xl md:rounded-2xl overflow-hidden relative min-h-[160px] md:min-h-0" style={s2Reveal.getAnimStyle(2)}>
                <h2 className="absolute top-4 left-5 md:top-6 md:left-7 text-white md:text-black text-[clamp(3rem,7vw,6rem)] font-bold leading-[0.9] z-10">Smile<br />makeover</h2>
              </MaskedCard>

              <MaskedCard bgImage={SECTION2_IMAGE} position={section2Positions[3]} cardRef={setSection2Card(3)} imageWidth={s2ImgWidth} focalX={focalS2} className="col-span-1 md:col-span-2 rounded-xl md:rounded-2xl overflow-hidden relative min-h-[200px] md:min-h-0" style={s2Reveal.getAnimStyle(3)}>
                <div className="absolute inset-0 z-10 flex flex-wrap md:flex-nowrap gap-1.5 md:gap-2 p-2 md:p-3">
                  {services.map((svc) => (
                    <div key={svc.name} className={`flex-1 min-w-[calc(50%-4px)] md:min-w-0 rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between ${svc.active ? 'bg-white/90 backdrop-blur-md' : 'bg-white/20 backdrop-blur-xl'}`}>
                      <h3 className={`text-xl md:text-4xl font-bold leading-[1.05] whitespace-pre-line ${svc.active ? 'text-black' : 'text-white'}`}>{svc.name}</h3>
                      {svc.num && (
                        <div className={`self-end w-8 h-8 md:w-12 md:h-12 rounded-full border flex items-center justify-center text-xs md:text-sm font-semibold ${svc.active ? 'border-black text-black' : 'border-white text-white'}`}>{svc.num}</div>
                      )}
                    </div>
                  ))}
                </div>
              </MaskedCard>
            </div>
          </section>

          {/* Section 3 - Implant Dentistry */}
          <section ref={s3Reveal.containerRef} className="min-h-screen md:h-screen w-full overflow-hidden flex flex-col pt-1.5 md:pt-2 px-3 md:px-5 pb-1.5 md:pb-2 gap-1.5 md:gap-2">
            <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 gap-1.5 md:gap-2">
              <div className="flex flex-col gap-1.5 md:gap-2">
                <div className="rounded-xl md:rounded-2xl bg-stone-50 p-5 md:p-7 flex flex-col justify-between flex-[1.2] min-h-[180px] md:min-h-0" style={s3Reveal.getAnimStyle(0)}>
                  <h2 className="text-[clamp(3rem,7vw,6.5rem)] font-bold leading-[0.95] text-black">Implant<br />Dentistry</h2>
                  <p className="text-xs md:text-sm font-semibold text-black">Restore Missing Teeth</p>
                </div>
                <div className="flex gap-1.5 md:gap-2 flex-1 min-h-[140px] md:min-h-0" style={s3Reveal.getAnimStyle(1)}>
                  <div className="flex-1 rounded-xl md:rounded-2xl overflow-hidden">
                    <img src={SECTION3_IMG1} alt="Dental implant procedure" className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1 rounded-xl md:rounded-2xl overflow-hidden">
                    <img src={SECTION3_IMG2} alt="Dental restoration" className="w-full h-full object-cover" />
                  </div>
                </div>
                <div className="rounded-xl md:rounded-2xl bg-zinc-200 p-5 md:p-7 flex items-end justify-between flex-[0.8] min-h-[160px] md:min-h-0" style={s3Reveal.getAnimStyle(2)}>
                  <div>
                    <p className="text-xs md:text-sm font-semibold text-black mb-2 md:mb-3">Consultation</p>
                    <h3 className="text-xl md:text-3xl font-bold text-black leading-6 md:leading-8">Dental<br />Restoration<br />Services</h3>
                  </div>
                  <button className="px-5 py-3 md:px-8 md:py-5 bg-white rounded-full text-black text-base md:text-xl font-bold hover:scale-105 transition-transform">Book Online</button>
                </div>
              </div>
              <div className="rounded-xl md:rounded-2xl overflow-hidden relative min-h-[350px] md:min-h-0" style={s3Reveal.getAnimStyle(3)}>
                <img src={SECTION3_BG} alt="Smiling patient" className="w-full h-full object-cover" />
                <div className="absolute bottom-3 left-3 right-3 md:bottom-5 md:left-5 md:right-5 flex gap-1.5 md:gap-2">
                  <div className="flex-1 bg-white rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between h-36 md:h-52">
                    <h4 className="text-lg md:text-2xl font-bold text-black leading-5 md:leading-7">The Process<br />of Installing<br />Implants</h4>
                    <div className="self-end w-9 h-9 md:w-12 md:h-12 rounded-full border border-black flex items-center justify-center">
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{transform:'rotate(-45deg)'}}><path d="M1 7h12m0 0L8 2m5 5L8 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    </div>
                  </div>
                  <div className="flex-1 bg-white/20 backdrop-blur-xl rounded-xl md:rounded-2xl p-3 md:p-5 flex flex-col justify-between h-36 md:h-52">
                    <h4 className="text-lg md:text-2xl font-bold text-white leading-5 md:leading-7">Caring<br />for Dental<br />Implants</h4>
                    <div className="self-end w-9 h-9 md:w-12 md:h-12 rounded-full border border-white flex items-center justify-center">
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{transform:'rotate(-45deg)'}} className="text-white"><path d="M1 7h12m0 0L8 2m5 5L8 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Interactive Discovery"
template_id: "96d5ac43-56d2-4a90-822b-2d6a6d0c5cb7"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Interactive Discovery

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `96d5ac43-56d2-4a90-822b-2d6a6d0c5cb7`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Interactive Discovery](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/cb597fcd-4e8f-4648-ba53-cb7c09225093.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-screen, dark-themed hero section for a geology brand called **Lithos**, using **React 18 + TypeScript + Vite + Tailwind CSS** and **lucide-react** for icons. The signature feature is a **cursor-following spotlight that reveals a second image** through a soft circular mask on top of a base image. Match every detail below exactly.

### Fonts
Add this to the top of `src/index.css`, then `@tailwind base/components/utilities`:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');
* { font-family: 'Inter', sans-serif; }
.font-playfair { font-family: 'Playfair Display', serif; }
```
- Body/UI font: **Inter**.
- Display/wordmark accent: **Playfair Display, italic**.

### Asset URLs (use these exactly)
- Base image (`BG_IMAGE_1`):
  `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_195923_b0ba8ace-1d1d-4f2c-9a28-1ab84b330680.png&w=1280&q=85`
- Reveal image (`BG_IMAGE_2`):
  `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85`

### Layout & structure
Root wrapper: `min-h-screen bg-white tracking-[-0.02em]`, inline `fontFamily: "'Inter', sans-serif"`.

**Section** (`<section>`): `relative w-full overflow-hidden h-screen bg-black`, inline `style={{ height: '100dvh' }}`. Layers, by z-index:
1. **Base image** (`z-10`): `absolute inset-0 bg-center bg-cover bg-no-repeat`, background = `BG_IMAGE_1`.
2. **Reveal layer** (`z-30`): a `RevealLayer` component (see below) showing `BG_IMAGE_2`.
3. **Heading** (`z-50`): `absolute top-[14%] left-0 right-0 flex flex-col items-center text-center px-5 pointer-events-none`. An `<h1>` with `text-white leading-[0.95]` containing two block spans:
   - Line 1: `block font-playfair italic font-normal text-5xl sm:text-7xl md:text-8xl`, inline `letterSpacing: '-0.05em'`, text **"Layers hold"**.
   - Line 2: `block font-normal text-5xl sm:text-7xl md:text-8xl -mt-1`, inline `letterSpacing: '-0.08em'`, text **"tales of time"**.
4. **Bottom-left paragraph** (`z-50`): `hidden sm:block absolute bottom-14 left-10 md:left-14 max-w-[260px]`. `<p className="text-sm text-white/80 leading-relaxed">` — "Every layer of sediment records a chapter of our planet, from ancient seabeds to drifting ash, layered across millions of years beneath us."
5. **Bottom-right block** (`z-50`): `absolute bottom-10 sm:bottom-24 left-5 right-5 sm:left-auto sm:right-10 md:right-14 max-w-full sm:max-w-[260px] flex flex-col items-start gap-4 sm:gap-5`. Contains a `<p className="text-xs sm:text-sm text-white/80 leading-relaxed">` — "Our interactive maps let you peel back the crust to trace how stones, fossils, and deep time combine to shape the ground beneath your feet." — and a **Start Digging** button: `bg-[#e8702a] hover:bg-[#d2611f] text-white text-sm font-medium px-7 py-3 rounded-full transition-all hover:scale-[1.03] active:scale-95 hover:shadow-lg hover:shadow-[#e8702a]/30`.

### The cursor spotlight reveal (core mechanic)
In the parent, define `const SPOTLIGHT_R = 260;` and track the mouse with smoothing:
- Refs: `mouse` (raw), `smooth` (eased), `rafRef`; state `cursorPos` (init `{x:-999,y:-999}`).
- `mousemove` listener stores raw `e.clientX/clientY`.
- A `requestAnimationFrame` loop lerps: `smooth.x += (mouse.x - smooth.x) * 0.1` (same for y), then `setCursorPos`. Clean up listener + cancel RAF on unmount.

`RevealLayer({ image, cursorX, cursorY })`:
- Holds a hidden `<canvas>` (`absolute inset-0 pointer-events-none`, `style={{display:'none'}}`) sized to `window.innerWidth/Height` on mount + resize.
- A reveal `<div>` (`absolute inset-0 bg-center bg-cover bg-no-repeat z-30 pointer-events-none`) with the reveal image as background.
- On every render: clear canvas, build a **radial gradient** at `(cursorX, cursorY)` from radius 0 → `SPOTLIGHT_R` with stops:
  `0 → rgba(255,255,255,1)`, `0.4 → 1`, `0.6 → 0.75`, `0.75 → 0.4`, `0.88 → 0.12`, `1 → 0`.
  Fill an arc of radius `SPOTLIGHT_R` with it. Then `canvas.toDataURL()` and apply it as `maskImage`/`webkitMaskImage` on the reveal div with `maskSize: '100% 100%'`. This makes the second image visible only inside the soft glowing circle that trails the cursor.

### Navigation (fixed, over hero)
`<nav className="fixed top-0 left-0 right-0 z-[100] flex items-center justify-between p-4 sm:p-5">`:
- **Left**: an inline SVG logo (26×26, viewBox `0 0 256 256`, `fill="#ffffff"`, path `M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z`) + wordmark `<span className="text-white text-2xl font-playfair italic">Lithos</span>`.
- **Center pill** (`hidden md:flex absolute left-1/2 -translate-x-1/2 bg-white/20 backdrop-blur-md border border-white/30 rounded-full px-2 py-2 items-center gap-1`): buttons **Course** (active: full white text), then **Field Guides, Geology, Plans, Live Tour** (`text-white/80 ... hover:bg-white/20 hover:text-white transition-colors`, `px-4 py-1.5 rounded-full text-sm font-medium`).
- **Right (desktop)**: `hidden md:block bg-white text-gray-900 text-sm font-semibold px-6 py-2.5 rounded-full hover:bg-gray-100` — **Sign Up**.

### Animations (premium, on load)
Add to `index.css`:
```css
@keyframes heroReveal { 0%{opacity:0;transform:translateY(28px);filter:blur(12px)} 100%{opacity:1;transform:translateY(0);filter:blur(0)} }
@keyframes heroFadeUp { 0%{opacity:0;transform:translateY(20px)} 100%{opacity:1;transform:translateY(0)} }
@keyframes heroZoom { 0%{transform:scale(1.12)} 100%{transform:scale(1)} }
.hero-anim { opacity:0; animation-fill-mode:forwards; animation-timing-function:cubic-bezier(0.16,1,0.3,1); }
.hero-reveal { animation-name:heroReveal; animation-duration:1.1s; }
.hero-fade { animation-name:heroFadeUp; animation-duration:1s; }
.hero-zoom { animation:heroZoom 1.8s cubic-bezier(0.16,1,0.3,1) forwards; }
@media (prefers-reduced-motion: reduce){ .hero-anim,.hero-zoom{ animation:none; opacity:1; } }
```
Apply:
- Base image div → add `hero-zoom` (slow Ken Burns zoom-out).
- Heading line 1 → `hero-anim hero-reveal`, inline `animationDelay: '0.25s'`; line 2 → same with `'0.42s'` (blur-rise, staggered).
- Bottom-left paragraph wrapper → `hero-anim hero-fade`, `animationDelay: '0.7s'`.
- Bottom-right wrapper → `hero-anim hero-fade`, `animationDelay: '0.85s'`.

### Responsiveness
- Heading scales `text-5xl` → `sm:text-7xl` → `md:text-8xl`.
- Center nav pill and desktop Sign Up are `hidden` below `md`; the mobile hamburger is `md:hidden`.
- Bottom-left paragraph is `hidden sm:block`; bottom-right block is full-width on mobile (`left-5 right-5`) and right-anchored from `sm`.
- Use `100dvh` so mobile browser chrome doesn't clip the section.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Bloom"
template_id: "c3a56793-c35d-4244-83da-d951e7d526de"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Bloom

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `c3a56793-c35d-4244-83da-d951e7d526de`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Bloom](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/87adcb17-af6f-4539-85f0-cd4e1aef0883.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bloom</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Manrope:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:#000}
::-webkit-scrollbar-thumb{background:#1f2937;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#374151}
body{background:#000;color:#fff;overflow-x:hidden;margin:0;padding:0;font-family:"Space Grotesk",ui-sans-serif,system-ui,sans-serif}

/* --- CONTAINER --- */
.scroll-container{position:relative;width:100%;height:500vh;background:#000}
.fixed-viewport{position:fixed;inset:0;width:100%;height:100%;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#000}

/* --- BRAND HEADER --- */
.premium-brand-header{position:absolute;top:clamp(24px,3vw,48px);left:clamp(24px,3vw,48px);z-index:45;display:flex;align-items:center;gap:clamp(8px,0.8vw,14px);user-select:none;pointer-events:auto;will-change:transform,opacity,filter}
@media(max-width:768px){.premium-brand-header{top:24px;left:24px}}
.premium-brand-text{font-family:"Instrument Serif",serif;font-size:clamp(22px,2.2vw,32px);font-weight:500;color:#fff;letter-spacing:-0.03em}
.premium-brand-logo-svg{width:clamp(28px,2.6vw,44px);height:auto;opacity:0.95}

/* --- NAV HEADER --- */
.premium-header-nav{position:absolute;top:clamp(24px,3vw,48px);right:clamp(24px,3vw,48px);z-index:50;pointer-events:auto;will-change:transform,opacity,filter}
@media(max-width:768px){.premium-header-nav{top:24px;right:24px}}
.premium-nav-desktop{display:block}
.premium-nav-list{display:flex;gap:0;margin:0;padding:0;list-style:none;align-items:center}
.premium-nav-item{margin:0;padding:0}
.premium-nav-link{display:block;background:#fff;color:#111;font-family:"Manrope",sans-serif;font-size:clamp(12px,0.9vw,15px);font-weight:500;text-decoration:none;padding:clamp(8px,0.7vw,12px) clamp(16px,1.3vw,24px);border-radius:8px;transition:opacity .2s ease,transform .2s ease;white-space:nowrap}
.premium-nav-link:hover{opacity:0.9;transform:scale(1.03)}
.premium-nav-link:active{transform:scale(0.97)}

/* --- HAMBURGER --- */
.premium-hamburger{display:none}
@media(max-width:768px){
  .premium-nav-desktop{display:none}
  .premium-hamburger{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;width:44px;height:44px;background:rgba(255,255,255,.12);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.15);border-radius:10px;cursor:pointer;padding:0;z-index:60;position:relative}
  .premium-hamburger:active{transform:scale(0.92)}
}
.premium-hamburger-line{display:block;width:20px;height:1.5px;background:#fff;border-radius:2px;transition:transform .3s cubic-bezier(.16,1,.3,1),opacity .2s ease;transform-origin:center}
.premium-hamburger-line.top-open{transform:translateY(6.5px) rotate(45deg)}
.premium-hamburger-line.mid-open{opacity:0}
.premium-hamburger-line.bot-open{transform:translateY(-6.5px) rotate(-45deg)}

/* --- MOBILE MENU --- */
.premium-mobile-menu{position:fixed;inset:0;z-index:55;background:rgba(0,0,0,.88);backdrop-filter:blur(40px);-webkit-backdrop-filter:blur(40px);display:flex;align-items:center;justify-content:center;pointer-events:auto;opacity:0;visibility:hidden;transition:opacity .3s ease,visibility .3s ease}
.premium-mobile-menu.open{opacity:1;visibility:visible}
.premium-mobile-menu-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;align-items:center;gap:8px}
.premium-mobile-menu-link{font-family:"Instrument Serif",Georgia,serif;font-size:40px;font-weight:400;color:#fff;text-decoration:none;letter-spacing:-0.02em;line-height:1.3;padding:8px 24px;transition:opacity .2s ease}
.premium-mobile-menu-link:hover,.premium-mobile-menu-link:active{opacity:0.6}

/* --- BOTANICAL CARD --- */
.premium-botanical-card{position:absolute;bottom:clamp(24px,3vw,48px);left:clamp(24px,3vw,48px);width:clamp(380px,30vw,540px);max-width:90vw;background:rgba(255,255,255,.16);backdrop-filter:blur(80px);-webkit-backdrop-filter:blur(80px);border-radius:0;padding:clamp(32px,3.2vw,56px);z-index:45;pointer-events:auto;border:1px solid rgba(255,255,255,.15);box-shadow:0 30px 60px rgba(0,0,0,.3);will-change:transform,opacity,filter}
@media(max-width:768px){.premium-botanical-card{bottom:32px;left:24px;padding:32px 24px;width:calc(100vw - 48px)}}
.premium-card-title{font-family:"Instrument Serif",serif;font-size:72px;line-height:1.05;font-weight:400;color:#fff;margin:0 0 clamp(10px,1.2vw,20px) 0;letter-spacing:-0.01em;width:324px;max-width:100%}
.premium-card-title .italic{font-style:italic}
@media(max-width:768px){.premium-card-title{font-size:38px;margin-bottom:10px}}
.premium-card-subtext{font-family:"Manrope",sans-serif;font-size:clamp(12px,1vw,15px);line-height:1.6;font-weight:400;color:rgba(255,255,255,.64);letter-spacing:0.01em;margin:0;width:clamp(260px,22vw,380px);max-width:100%}
@media(max-width:768px){.premium-card-subtext{font-size:13px}}

/* --- CTA CIRCLE --- */
.premium-action-circle{position:absolute;right:calc(-1*(clamp(80px,7vw,112px)/2));bottom:clamp(20px,2.5vw,40px);width:clamp(80px,7vw,112px);height:clamp(80px,7vw,112px);border-radius:50%;background:#CB8DFF;color:#fff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:transform .25s cubic-bezier(.16,1,.3,1),background-color .2s ease;z-index:55;box-shadow:none}
.premium-action-circle:hover{transform:scale(1.08);background:#d9a8ff}
.premium-action-circle:active{transform:scale(0.94)}
.premium-action-circle svg{width:clamp(30px,2.8vw,44px);height:clamp(18px,1.8vw,28px);stroke:#fff;stroke-width:1.75;fill:none;transition:transform .25s ease}
.premium-action-circle:hover svg{transform:translateX(4px)}
@media(max-width:768px){.premium-action-circle{width:64px;height:64px;right:-16px;bottom:-32px}.premium-action-circle svg{width:38px;height:22px}}

/* --- FEATURE CARDS --- */
.premium-features-container{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:max-content;max-width:95%;display:grid;grid-template-columns:repeat(3,280px);justify-content:center;gap:16px;z-index:46;pointer-events:none;align-items:stretch}
.premium-feature-card{background:rgba(255,255,255,.16);backdrop-filter:blur(80px);-webkit-backdrop-filter:blur(80px);border:1px solid rgba(255,255,255,.15);border-radius:0;padding:24px;width:280px;height:440px;box-shadow:0 30px 60px rgba(0,0,0,.3);display:flex;flex-direction:column;justify-content:flex-start;align-items:flex-start;transition:border-color .3s ease;will-change:transform,opacity,filter}
.premium-feature-card:hover{border-color:rgba(255,255,255,.45)}
.premium-feature-icon-wrapper{margin-bottom:32px;color:#CB8DFF;display:flex;align-items:center;justify-content:center}
.premium-feature-icon-wrapper svg{width:clamp(36px,3.5vw,48px);height:clamp(36px,3.5vw,48px);opacity:0.95}
.premium-feature-title{font-family:"Instrument Serif",Georgia,serif;font-size:24px;font-weight:400;line-height:1.15;color:#fff;margin:auto 0 8px 0;letter-spacing:-0.01em}
.premium-feature-desc{font-family:"Manrope",sans-serif;font-size:clamp(12px,1vw,14px);line-height:20px;font-weight:400;color:rgba(255,255,255,.64);margin:0;letter-spacing:0.015em}
@media(max-width:768px){
  .premium-features-container{grid-template-columns:1fr;width:calc(100% - 48px);left:24px;transform:translate(0,-50%);top:50%;gap:16px;height:auto;overflow-y:auto;max-height:80vh}
  .premium-feature-card{padding:24px;width:100%;height:auto;min-height:240px}
  .premium-feature-icon-wrapper{margin-bottom:24px}
}

/* --- MISSION TEXT --- */
.mission-container{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:40;padding:0 24px}
@media(min-width:768px){.mission-container{padding:0 48px}}
.mission-inner{position:relative;width:100%;max-width:64rem;height:100%;display:flex;align-items:center;justify-content:center}
.mission-para{position:absolute;text-align:center;user-select:none;pointer-events:none;font-family:"Instrument Serif",Georgia,serif;font-size:1.875rem;color:rgba(255,255,255,.95);line-height:1.375;letter-spacing:-0.025em;will-change:transform,opacity,filter}
@media(min-width:768px){.mission-para{font-size:3rem}}
@media(min-width:1024px){.mission-para{font-size:3.75rem}}
.mission-pill{display:inline-block;padding:2px 16px;margin:0 6px;background:#CB8DFF;color:#fff;border-radius:9999px;vertical-align:middle;font-family:"Instrument Serif",Georgia,serif}
@media(min-width:768px){.mission-pill{padding:4px 24px;margin:0 10px}}

/* --- FEEDBACK FORM --- */
.feedback-container{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:50;padding:0 24px}
@media(min-width:768px){.feedback-container{padding:0 48px}}
.feedback-form-card{position:relative;width:100%;max-width:28rem;background:rgba(0,0,0,.45);backdrop-filter:blur(48px);-webkit-backdrop-filter:blur(48px);border:1px solid rgba(255,255,255,.1);padding:32px;text-align:center;pointer-events:auto;display:flex;flex-direction:column;align-items:center;justify-content:center;user-select:none;will-change:transform,opacity,filter}
@media(min-width:768px){.feedback-form-card{padding:48px}}
.fb-logo{width:40px;height:40px;margin-bottom:20px}
.fb-title{font-family:"Instrument Serif",Georgia,serif;font-size:1.5rem;color:#fff;font-weight:400;letter-spacing:-0.025em;margin:0 0 8px 0;line-height:1.2;white-space:nowrap}
@media(min-width:768px){.fb-title{font-size:1.875rem}}
.fb-sub{font-family:"Space Grotesk",sans-serif;font-size:10px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:0.05em;margin:0 0 28px 0;line-height:1.625;max-width:20rem}
@media(min-width:768px){.fb-sub{font-size:12px}}
.fb-form{width:100%;display:flex;flex-direction:column;gap:14px}
.fb-input{width:100%;padding:12px 20px;background:rgba(255,255,255,.05);color:#fff;border:1px solid rgba(255,255,255,.1);font-family:"Space Grotesk",sans-serif;font-size:14px;letter-spacing:0.025em;text-align:center;outline:none;transition:all .3s ease}
.fb-input::placeholder{color:rgba(255,255,255,.3)}
.fb-input:hover,.fb-input:focus{background:rgba(255,255,255,.1)}
.fb-input:focus{border-color:#CB8DFF}
@media(min-width:768px){.fb-input{padding:16px 20px;font-size:16px}}
.fb-btn{width:100%;padding:14px 24px;background:#CB8DFF;color:#fff;border:none;cursor:pointer;font-family:"Space Grotesk",sans-serif;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;transition:all .3s ease}
.fb-btn:hover{background:#d9a8ff}
.fb-btn:active{transform:scale(0.98)}
.fb-btn.submitted{background:#059669;cursor:default}
@media(min-width:768px){.fb-btn{padding:16px 24px}}
.fb-success{margin-top:16px;font-family:"Space Grotesk",sans-serif;font-size:12px;color:#34d399;font-weight:500;letter-spacing:0.025em;line-height:1.625;display:none}
.fb-success.show{display:block;animation:fadeIn .5s ease}

/* --- VIDEO BG --- */
.bg-wrapper{position:absolute;top:-5%;left:-5%;right:-5%;bottom:-5%;width:110%;height:110%;pointer-events:none;user-select:none;transform:translate3d(0,0,0);transition:transform .4s cubic-bezier(.15,.85,.35,1)}
.bg-wrapper video{position:absolute;width:0;height:0;opacity:0}
.bg-wrapper canvas{width:100%;height:100%;display:block}

/* --- LOADING --- */
.loading-screen{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#000;z-index:60;transition:opacity 1s ease;padding:24px;text-align:center}
.loading-screen.hidden{opacity:0;pointer-events:none}
.loading-spinner{width:64px;height:64px;margin-bottom:16px;animation:spin 2s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-family:"JetBrains Mono",monospace;font-size:14px;letter-spacing:0.1em;color:#6b7280;text-transform:uppercase;animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}

/* --- ERROR --- */
.error-screen{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#000;z-index:55;padding:24px;text-align:center;display:none}
.error-screen.show{display:flex}
.error-card{padding:16px;border:1px solid #1f2937;border-radius:4px;background:#09090b;max-width:28rem}
.error-title{color:#ef4444;font-family:"JetBrains Mono",monospace;font-size:14px;margin:0 0 8px 0}
.error-msg{color:#9ca3af;font-family:"JetBrains Mono",monospace;font-size:12px;line-height:1.625;margin:0}
</style>
</head>
<body>

<div class="scroll-container" id="scrollContainer">
  <div class="fixed-viewport">

    <!-- Brand header -->
    <div class="premium-brand-header" id="brandHeader">
      <svg viewBox="0 0 49 48" fill="none" xmlns="http://www.w3.org/2000/svg" class="premium-brand-logo-svg">
        <g clip-path="url(#cb)">
          <path d="M48.4404 17.6588C47.7017 15.3617 46.2569 13.3584 44.3131 11.9362C42.3693 10.5141 40.0265 9.74617 37.6207 9.74268H37.0462C37.1235 10.2805 37.164 10.8231 37.1676 11.3665C37.1628 14.3622 36.0924 17.2579 34.1489 19.5323C32.2054 21.8066 29.5166 23.3102 26.5664 23.7724C26.6392 24.0729 26.7121 24.3733 26.8092 24.6655C26.9904 25.2224 27.2122 25.7651 27.4728 26.2894L27.4728 26.3543C27.5942 26.5898 27.7236 26.8252 27.8612 27.0526L27.9178 27.15C28.3242 27.8128 28.796 28.433 29.3259 29.0011L29.5687 29.2609L29.9652 29.6263C30.0866 29.74 30.2161 29.8536 30.3537 29.9592L30.7098 30.2515C30.8797 30.3814 31.0577 30.5032 31.2358 30.625L31.5595 30.8523C31.8508 31.0309 32.1502 31.2095 32.4577 31.3638C33.787 32.0468 35.2378 32.4594 36.7266 32.5778C38.2154 32.6963 39.7129 32.5182 41.1329 32.0539C41.4083 31.9667 41.6785 31.8637 41.9421 31.7454C44.6033 30.6611 46.7546 28.6033 47.961 25.9882C49.1674 23.3731 49.3387 20.3958 48.4404 17.6588Z" fill="white"/>
          <path d="M41.4966 33.1341C40.2425 33.5456 38.9316 33.7566 37.6122 33.7593C35.2977 33.7531 33.0303 33.1034 31.0617 31.8822C29.0931 30.6611 27.5005 28.9163 26.4607 26.8418C26.1937 27.0042 25.9428 27.1747 25.6515 27.3614C25.1901 27.702 24.7546 28.0765 24.3486 28.4819L24.3 28.5306C24.1058 28.7173 23.9278 28.9122 23.7497 29.1151L23.685 29.1963C23.1783 29.7906 22.7336 30.4354 22.3578 31.1206C22.3012 31.2261 22.2445 31.3235 22.196 31.4291C22.1474 31.5346 22.0341 31.7538 21.9613 31.9162C21.8885 32.0786 21.8237 32.2329 21.7671 32.3952C21.7104 32.5576 21.6538 32.6794 21.6052 32.8256C21.5567 32.9717 21.4677 33.2315 21.411 33.4345C21.3544 33.6375 21.3382 33.6699 21.3139 33.7917C21.2236 34.1255 21.1534 34.4644 21.1035 34.8066C20.8672 36.2866 20.9251 37.7989 21.2737 39.2564C21.6223 40.7139 22.2548 42.0879 23.1347 43.2992C23.2966 43.5184 23.4746 43.7376 23.6526 43.9406C25.3534 46.0837 27.7685 47.5385 30.4534 48.0372C33.1384 48.045 35.9125 48.045 38.2653 46.6547C40.6181 45.2645 42.3913 43.0685 43.2586 40.4708C44.1259 37.8732 44.029 35.0487 42.9856 32.517C42.5042 32.7574 42.0067 32.9636 41.4966 33.1341Z" fill="white"/>
          <path d="M20.0045 34.6197C20.4175 31.9862 21.6629 29.5556 23.5571 27.686C23.3224 27.4912 23.0796 27.2882 22.8287 27.1096C21.2988 25.9892 19.5119 25.2743 17.6334 25.0311H17.3987C16.9941 24.9905 16.5894 24.958 16.1686 24.958C14.3714 24.962 12.6002 25.3895 10.9978 26.206C9.39542 27.0226 8.00658 28.2053 6.9432 29.659C6.78135 29.8863 6.63568 30.1217 6.49002 30.3572C5.03583 32.6434 4.4443 35.3759 4.82225 38.0613C5.2002 40.7467 6.52271 43.208 8.55098 45.0008C10.5793 46.7937 13.1796 47.7998 15.8825 47.8376C18.5854 47.8754 21.2127 46.9424 23.29 45.207C22.9121 44.8221 22.5632 44.4096 22.2461 43.9729C21.2738 42.6404 20.575 41.1275 20.1902 39.5219C19.8054 37.9163 19.7423 36.25 20.0045 34.6197Z" fill="white"/>
          <path d="M6.01393 28.9525C7.76739 26.527 10.3287 24.8119 13.234 24.1178C16.1392 23.4238 19.1961 23.7967 21.8509 25.169C21.9723 24.8848 22.0856 24.6006 22.1827 24.3002C22.7183 22.6659 22.8815 20.9318 22.6602 19.2258V18.9903C22.6602 18.7955 22.5873 18.6006 22.5469 18.4139C22.5064 18.2271 22.4821 18.1054 22.4417 17.9592C22.4012 17.8131 22.3608 17.6426 22.3122 17.4802C22.2636 17.3178 22.1827 17.0905 22.118 16.8956C22.0532 16.7008 22.029 16.652 21.9804 16.5384C21.8586 16.2165 21.7181 15.902 21.5596 15.5966C20.8885 14.2565 19.9583 13.0639 18.8232 12.0881C17.6881 11.1124 16.3708 10.3731 14.948 9.91321C14.6972 9.83202 14.4544 9.76706 14.2035 9.71023C13.2994 9.47628 12.3696 9.35628 11.4359 9.35299C8.9636 9.30745 6.54433 10.0747 4.54726 11.5375C2.55019 13.0004 1.08498 15.0786 0.375205 17.4551C-0.334567 19.8315 -0.249922 22.3757 0.616224 24.6993C1.48237 27.023 3.08245 28.9986 5.17231 30.3246C5.42183 29.8488 5.70301 29.3904 6.01393 28.9525Z" fill="white"/>
          <path d="M22.5278 15.0688C23.735 17.4435 24.1546 20.143 23.7255 22.7738C24.025 22.7738 24.3325 22.8225 24.6481 22.8225C25.2227 22.8148 25.796 22.766 26.3637 22.6764C28.9618 22.273 31.3392 20.9756 33.0885 19.0065L33.2585 18.8198C33.4041 18.6493 33.5417 18.4707 33.6793 18.2839C33.8169 18.0972 33.833 18.0891 33.9059 17.9835C33.9787 17.878 34.1406 17.6425 34.2458 17.472C34.351 17.3015 34.4076 17.2122 34.4804 17.0823C34.5533 16.9524 34.6666 16.7575 34.7475 16.587C34.8284 16.4165 34.9013 16.2785 34.9741 16.1243C35.0469 15.97 35.1117 15.8076 35.1845 15.6452C35.2573 15.4829 35.314 15.2961 35.3706 15.1175C35.4273 14.9389 35.4839 14.8008 35.5325 14.6466C35.581 14.4923 35.6377 14.2488 35.6862 14.0458C35.7348 13.8428 35.7591 13.7535 35.7833 13.6073C35.8076 13.4612 35.8643 13.1364 35.8966 12.8929C35.929 12.6493 35.8966 12.6493 35.9452 12.5194C35.9452 12.154 36.0018 11.7887 36.0018 11.4071V10.5952C35.8453 7.88465 34.727 5.31985 32.8491 3.36487C30.9712 1.40989 28.4579 0.193859 25.7639 -0.0631835C23.0699 -0.320226 20.3731 0.398699 18.1616 1.96351C15.9501 3.52831 14.37 5.83563 13.707 8.46797C14.2332 8.56239 14.7523 8.69259 15.2608 8.85768C16.8205 9.36099 18.2656 10.1689 19.5128 11.2349C20.76 12.3008 21.7847 13.6038 22.5278 15.0688Z" fill="white"/>
        </g>
        <defs><clipPath id="cb"><rect width="49" height="48" fill="white"/></clipPath></defs>
      </svg>
      <span class="premium-brand-text">Bloom</span>
    </div>

    <!-- Navigation -->
    <header class="premium-header-nav" id="navHeader">
      <nav class="premium-nav-desktop">
        <ul class="premium-nav-list">
          <li class="premium-nav-item"><a href="#atelier" class="premium-nav-link">Atelier</a></li>
          <li class="premium-nav-item"><a href="#collections" class="premium-nav-link">Collections</a></li>
          <li class="premium-nav-item"><a href="#rituals" class="premium-nav-link">Rituals</a></li>
          <li class="premium-nav-item"><a href="#about" class="premium-nav-link">About</a></li>
          <li class="premium-nav-item"><a href="#contact" class="premium-nav-link">Contact</a></li>
        </ul>
      </nav>
      <button class="premium-hamburger" id="hamburgerBtn" aria-label="Open menu">
        <span class="premium-hamburger-line" id="hLine1"></span>
        <span class="premium-hamburger-line" id="hLine2"></span>
        <span class="premium-hamburger-line" id="hLine3"></span>
      </button>
    </header>

    <!-- Mobile menu -->
    <div class="premium-mobile-menu" id="mobileMenu">
      <nav>
        <ul class="premium-mobile-menu-list">
          <li><a href="#atelier" class="premium-mobile-menu-link mobile-link">Atelier</a></li>
          <li><a href="#collections" class="premium-mobile-menu-link mobile-link">Collections</a></li>
          <li><a href="#rituals" class="premium-mobile-menu-link mobile-link">Rituals</a></li>
          <li><a href="#about" class="premium-mobile-menu-link mobile-link">About</a></li>
          <li><a href="#contact" class="premium-mobile-menu-link mobile-link">Contact</a></li>
        </ul>
      </nav>
    </div>

    <!-- Botanical card -->
    <div class="premium-botanical-card" id="botanicalCard">
      <h2 class="premium-card-title">Merging <span class="italic">Silicon</span> With Organic <span class="italic">Life.</span></h2>
      <p class="premium-card-subtext">Developing Next-Generation Cyber-Botanical Systems Designed To Heal Ecosystems And Advance Human Tech.</p>
      <button class="premium-action-circle" id="ctaBtn" aria-label="Explore systems">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 40 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M29.5 4.5L37 12m0 0l-7.5 7.5M37 12H3"/>
        </svg>
      </button>
    </div>

    <!-- Feature cards -->
    <div class="premium-features-container" id="featuresContainer" style="visibility:hidden">
      <div class="premium-feature-card" id="fCard1" style="opacity:0">
        <div class="premium-feature-icon-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/></svg>
        </div>
        <h3 class="premium-feature-title">Neural Synthesis</h3>
        <p class="premium-feature-desc">Hybrid bio-computing linking mycelium networks with logical silicon cores.</p>
      </div>
      <div class="premium-feature-card" id="fCard2" style="opacity:0">
        <div class="premium-feature-icon-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v18m9-9H3m14.5-4.5l-11 11m11 0l-11-11"/></svg>
        </div>
        <h3 class="premium-feature-title">Ecosystem Remediation</h3>
        <p class="premium-feature-desc">Self-replicating biomechanical flora actively restoring and cleansing heavily toxic soil bases.</p>
      </div>
      <div class="premium-feature-card" id="fCard3" style="opacity:0">
        <div class="premium-feature-icon-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16 3L7 12h12l-6 9"/></svg>
        </div>
        <h3 class="premium-feature-title">Kinetic Transduction</h3>
        <p class="premium-feature-desc">Converting natural photosynthesis cycles into electrical energy for local grids.</p>
      </div>
    </div>

    <!-- Mission text -->
    <div class="mission-container" id="missionContainer" style="visibility:hidden">
      <div class="mission-inner">
        <div class="mission-para" id="mPara1" style="opacity:0">To gracefully cultivate a newly balanced <span class="mission-pill">ecosystem</span> we dissolve all boundaries between technology and nature.</div>
        <div class="mission-para" id="mPara2" style="opacity:0">By rewriting the biological code of our <span class="mission-pill">planet</span> we employ specialized photosynthesis to heal broken landscapes.</div>
        <div class="mission-para" id="mPara3" style="opacity:0">We believe that growing through botanical <span class="mission-pill">symbiosis</span> is the ultimate pathway to power the future of humanity.</div>
      </div>
    </div>

    <!-- Feedback form -->
    <div class="feedback-container" id="feedbackContainer" style="visibility:hidden">
      <div class="feedback-form-card" id="feedbackForm" style="opacity:0">
        <svg viewBox="0 0 49 48" fill="none" xmlns="http://www.w3.org/2000/svg" class="fb-logo">
          <g clip-path="url(#cf)">
            <path d="M48.4404 17.6588C47.7017 15.3617 46.2569 13.3584 44.3131 11.9362C42.3693 10.5141 40.0265 9.74617 37.6207 9.74268H37.0462C37.1235 10.2805 37.164 10.8231 37.1676 11.3665C37.1628 14.3622 36.0924 17.2579 34.1489 19.5323C32.2054 21.8066 29.5166 23.3102 26.5664 23.7724C26.6392 24.0729 26.7121 24.3733 26.8092 24.6655C26.9904 25.2224 27.2122 25.7651 27.4728 26.2894L27.4728 26.3543C27.5942 26.5898 27.7236 26.8252 27.8612 27.0526L27.9178 27.15C28.3242 27.8128 28.796 28.433 29.3259 29.0011L29.5687 29.2609L29.9652 29.6263C30.0866 29.74 30.2161 29.8536 30.3537 29.9592L30.7098 30.2515C30.8797 30.3814 31.0577 30.5032 31.2358 30.625L31.5595 30.8523C31.8508 31.0309 32.1502 31.2095 32.4577 31.3638C33.787 32.0468 35.2378 32.4594 36.7266 32.5778C38.2154 32.6963 39.7129 32.5182 41.1329 32.0539C41.4083 31.9667 41.6785 31.8637 41.9421 31.7454C44.6033 30.6611 46.7546 28.6033 47.961 25.9882C49.1674 23.3731 49.3387 20.3958 48.4404 17.6588Z" fill="white"/>
            <path d="M41.4966 33.1341C40.2425 33.5456 38.9316 33.7566 37.6122 33.7593C35.2977 33.7531 33.0303 33.1034 31.0617 31.8822C29.0931 30.6611 27.5005 28.9163 26.4607 26.8418C26.1937 27.0042 25.9428 27.1747 25.6515 27.3614C25.1901 27.702 24.7546 28.0765 24.3486 28.4819L24.3 28.5306C24.1058 28.7173 23.9278 28.9122 23.7497 29.1151L23.685 29.1963C23.1783 29.7906 22.7336 30.4354 22.3578 31.1206C22.3012 31.2261 22.2445 31.3235 22.196 31.4291C22.1474 31.5346 22.0341 31.7538 21.9613 31.9162C21.8885 32.0786 21.8237 32.2329 21.7671 32.3952C21.7104 32.5576 21.6538 32.6794 21.6052 32.8256C21.5567 32.9717 21.4677 33.2315 21.411 33.4345C21.3544 33.6375 21.3382 33.6699 21.3139 33.7917C21.2236 34.1255 21.1534 34.4644 21.1035 34.8066C20.8672 36.2866 20.9251 37.7989 21.2737 39.2564C21.6223 40.7139 22.2548 42.0879 23.1347 43.2992C23.2966 43.5184 23.4746 43.7376 23.6526 43.9406C25.3534 46.0837 27.7685 47.5385 30.4534 48.0372C33.1384 48.045 35.9125 48.045 38.2653 46.6547C40.6181 45.2645 42.3913 43.0685 43.2586 40.4708C44.1259 37.8732 44.029 35.0487 42.9856 32.517C42.5042 32.7574 42.0067 32.9636 41.4966 33.1341Z" fill="white"/>
            <path d="M20.0045 34.6197C20.4175 31.9862 21.6629 29.5556 23.5571 27.686C23.3224 27.4912 23.0796 27.2882 22.8287 27.1096C21.2988 25.9892 19.5119 25.2743 17.6334 25.0311H17.3987C16.9941 24.9905 16.5894 24.958 16.1686 24.958C14.3714 24.962 12.6002 25.3895 10.9978 26.206C9.39542 27.0226 8.00658 28.2053 6.9432 29.659C6.78135 29.8863 6.63568 30.1217 6.49002 30.3572C5.03583 32.6434 4.4443 35.3759 4.82225 38.0613C5.2002 40.7467 6.52271 43.208 8.55098 45.0008C10.5793 46.7937 13.1796 47.7998 15.8825 47.8376C18.5854 47.8754 21.2127 46.9424 23.29 45.207C22.9121 44.8221 22.5632 44.4096 22.2461 43.9729C21.2738 42.6404 20.575 41.1275 20.1902 39.5219C19.8054 37.9163 19.7423 36.25 20.0045 34.6197Z" fill="white"/>
            <path d="M6.01393 28.9525C7.76739 26.527 10.3287 24.8119 13.234 24.1178C16.1392 23.4238 19.1961 23.7967 21.8509 25.169C21.9723 24.8848 22.0856 24.6006 22.1827 24.3002C22.7183 22.6659 22.8815 20.9318 22.6602 19.2258V18.9903C22.6602 18.7955 22.5873 18.6006 22.5469 18.4139C22.5064 18.2271 22.4821 18.1054 22.4417 17.9592C22.4012 17.8131 22.3608 17.6426 22.3122 17.4802C22.2636 17.3178 22.1827 17.0905 22.118 16.8956C22.0532 16.7008 22.029 16.652 21.9804 16.5384C21.8586 16.2165 21.7181 15.902 21.5596 15.5966C20.8885 14.2565 19.9583 13.0639 18.8232 12.0881C17.6881 11.1124 16.3708 10.3731 14.948 9.91321C14.6972 9.83202 14.4544 9.76706 14.2035 9.71023C13.2994 9.47628 12.3696 9.35628 11.4359 9.35299C8.9636 9.30745 6.54433 10.0747 4.54726 11.5375C2.55019 13.0004 1.08498 15.0786 0.375205 17.4551C-0.334567 19.8315 -0.249922 22.3757 0.616224 24.6993C1.48237 27.023 3.08245 28.9986 5.17231 30.3246C5.42183 29.8488 5.70301 29.3904 6.01393 28.9525Z" fill="white"/>
            <path d="M22.5278 15.0688C23.735 17.4435 24.1546 20.143 23.7255 22.7738C24.025 22.7738 24.3325 22.8225 24.6481 22.8225C25.2227 22.8148 25.796 22.766 26.3637 22.6764C28.9618 22.273 31.3392 20.9756 33.0885 19.0065L33.2585 18.8198C33.4041 18.6493 33.5417 18.4707 33.6793 18.2839C33.8169 18.0972 33.833 18.0891 33.9059 17.9835C33.9787 17.878 34.1406 17.6425 34.2458 17.472C34.351 17.3015 34.4076 17.2122 34.4804 17.0823C34.5533 16.9524 34.6666 16.7575 34.7475 16.587C34.8284 16.4165 34.9013 16.2785 34.9741 16.1243C35.0469 15.97 35.1117 15.8076 35.1845 15.6452C35.2573 15.4829 35.314 15.2961 35.3706 15.1175C35.4273 14.9389 35.4839 14.8008 35.5325 14.6466C35.581 14.4923 35.6377 14.2488 35.6862 14.0458C35.7348 13.8428 35.7591 13.7535 35.7833 13.6073C35.8076 13.4612 35.8643 13.1364 35.8966 12.8929C35.929 12.6493 35.8966 12.6493 35.9452 12.5194C35.9452 12.154 36.0018 11.7887 36.0018 11.4071V10.5952C35.8453 7.88465 34.727 5.31985 32.8491 3.36487C30.9712 1.40989 28.4579 0.193859 25.7639 -0.0631835C23.0699 -0.320226 20.3731 0.398699 18.1616 1.96351C15.9501 3.52831 14.37 5.83563 13.707 8.46797C14.2332 8.56239 14.7523 8.69259 15.2608 8.85768C16.8205 9.36099 18.2656 10.1689 19.5128 11.2349C20.76 12.3008 21.7847 13.6038 22.5278 15.0688Z" fill="white"/>
          </g>
          <defs><clipPath id="cf"><rect width="49" height="48" fill="white"/></clipPath></defs>
        </svg>
        <h3 class="fb-title">Cultivate alignment</h3>
        <p class="fb-sub">Subscribe to biological updates &amp; cybernetic releases.</p>
        <form class="fb-form" id="fbForm">
          <input type="email" required placeholder="name@ecosystem.com" class="fb-input" id="fbEmail">
          <button type="submit" class="fb-btn" id="fbBtn">CONNECT</button>
        </form>
        <p class="fb-success" id="fbSuccess">Welcome to the digital flora. Check your inbox soon.</p>
      </div>
    </div>

    <!-- Video background -->
    <div class="bg-wrapper" id="bgWrapper">
      <video id="v1" src="https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781506095/202606101700_hglz7q.mp4" preload="auto" muted playsinline crossorigin="anonymous"></video>
      <video id="v2" src="https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781506108/202606101702_sd50y0.mp4" preload="auto" muted playsinline crossorigin="anonymous"></video>
      <video id="v3" src="https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781506130/202606101703_jmidj2.mp4" preload="auto" muted playsinline crossorigin="anonymous"></video>
      <canvas id="mainCanvas"></canvas>
    </div>

    <!-- Loading -->
    <div class="loading-screen" id="loadingScreen">
      <svg class="loading-spinner" viewBox="0 0 64 64" style="transform:rotate(-90deg)">
        <circle cx="32" cy="32" r="28" stroke="#1f2937" stroke-width="2" fill="transparent"/>
        <circle cx="32" cy="32" r="28" stroke="#fff" stroke-width="3" fill="transparent" stroke-dasharray="176" stroke-dashoffset="132" stroke-linecap="round"/>
      </svg>
      <p class="loading-text">Loading experience</p>
    </div>

    <!-- Error -->
    <div class="error-screen" id="errorScreen">
      <div class="error-card">
        <p class="error-title">Video Load Error</p>
        <p class="error-msg">Unable to load video resources. Please check your connection and try reloading.</p>
      </div>
    </div>

  </div>
</div>

<script>
(function(){
  var container = document.getElementById('scrollContainer');
  var videos = { v1: document.getElementById('v1'), v2: document.getElementById('v2'), v3: document.getElementById('v3') };
  var canvas = document.getElementById('mainCanvas');
  var bgWrapper = document.getElementById('bgWrapper');
  var brandHeader = document.getElementById('brandHeader');
  var navHeader = document.getElementById('navHeader');
  var botanicalCard = document.getElementById('botanicalCard');
  var featuresContainer = document.getElementById('featuresContainer');
  var fCard1 = document.getElementById('fCard1');
  var fCard2 = document.getElementById('fCard2');
  var fCard3 = document.getElementById('fCard3');
  var missionContainer = document.getElementById('missionContainer');
  var mPara1 = document.getElementById('mPara1');
  var mPara2 = document.getElementById('mPara2');
  var mPara3 = document.getElementById('mPara3');
  var feedbackContainer = document.getElementById('feedbackContainer');
  var feedbackForm = document.getElementById('feedbackForm');
  var loadingScreen = document.getElementById('loadingScreen');
  var errorScreen = document.getElementById('errorScreen');

  var targetProgress = 0, currentProgress = 0;
  var durations = { v1: 0, v2: 0, v3: 0 };
  var metaLoaded = { v1: false, v2: false, v3: false };
  var seeking = { v1: false, v2: false, v3: false };
  var pendingSeek = { v1: -1, v2: -1, v3: -1 };
  var offscreen = null;

  function getActiveKey(p) { return p <= 0.333 ? 'v1' : p <= 0.666 ? 'v2' : 'v3'; }

  // Canvas draw with double-buffer
  function drawFrame() {
    var p = currentProgress;
    var key = getActiveKey(p);
    var video = videos[key];
    if (!video || video.readyState < 2) return;
    var dpr = window.devicePixelRatio || 1;
    var cW = canvas.width / dpr, cH = canvas.height / dpr;
    if (cW === 0 || cH === 0) return;
    var vW = video.videoWidth || 1920, vH = video.videoHeight || 1080;
    var vA = vW / vH, cA = cW / cH;
    var dW = cW, dH = cH, oX = 0, oY = 0;
    if (vA > cA) { dW = cH * vA; oX = (cW - dW) / 2; }
    else { dH = cW / vA; oY = (cH - dH) / 2; }
    if (!offscreen) offscreen = document.createElement('canvas');
    if (offscreen.width !== canvas.width || offscreen.height !== canvas.height) {
      offscreen.width = canvas.width; offscreen.height = canvas.height;
    }
    var oc = offscreen.getContext('2d');
    if (!oc) return;
    try {
      oc.setTransform(dpr, 0, 0, dpr, 0, 0);
      oc.clearRect(0, 0, cW, cH);
      oc.drawImage(video, oX, oY, dW, dH);
      var ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(offscreen, 0, 0);
    } catch(e) {}
  }

  function handleResize() {
    var parent = canvas.parentElement;
    if (!parent) return;
    var dpr = window.devicePixelRatio || 1;
    var w = parent.clientWidth, h = parent.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
    if (offscreen) { offscreen.width = canvas.width; offscreen.height = canvas.height; }
    drawFrame();
  }

  function safeSeek(key, targetTime) {
    var video = videos[key];
    if (!video) return;
    var dur = durations[key] || video.duration || 10;
    var clamped = Math.max(0, Math.min(targetTime, dur - 0.05));
    if (Math.abs(video.currentTime - clamped) < 0.01) return;
    if (seeking[key]) { pendingSeek[key] = clamped; return; }
    seeking[key] = true; pendingSeek[key] = -1;
    video.currentTime = clamped;
  }

  ['v1','v2','v3'].forEach(function(key) {
    videos[key].addEventListener('seeked', function() {
      seeking[key] = false;
      if (key === getActiveKey(currentProgress)) drawFrame();
      if (pendingSeek[key] >= 0) { var t = pendingSeek[key]; pendingSeek[key] = -1; safeSeek(key, t); }
    });
  });

  // Loading
  function checkAllReady() {
    if (metaLoaded.v1 && metaLoaded.v2 && metaLoaded.v3) {
      setTimeout(function() { loadingScreen.classList.add('hidden'); handleResize(); }, 100);
    }
  }
  ['v1','v2','v3'].forEach(function(key) {
    var el = videos[key];
    function onMeta() {
      var d = el.duration;
      if (d && !isNaN(d) && d > 0 && d !== Infinity) { durations[key] = d; metaLoaded[key] = true; checkAllReady(); }
    }
    el.addEventListener('loadedmetadata', onMeta);
    el.addEventListener('durationchange', onMeta);
    el.addEventListener('canplay', onMeta);
    el.addEventListener('error', function() { errorScreen.classList.add('show'); });
    if (el.readyState >= 1) onMeta();
  });
  setTimeout(function() {
    ['v1','v2','v3'].forEach(function(key) {
      if (!metaLoaded[key]) { durations[key] = videos[key].duration || 10; metaLoaded[key] = true; }
    });
    checkAllReady();
  }, 8000);

  window.addEventListener('resize', handleResize);

  // Cursor parallax
  window.addEventListener('mousemove', function(e) {
    var x = (e.clientX - window.innerWidth / 2) / (window.innerWidth / 2);
    var y = (e.clientY - window.innerHeight / 2) / (window.innerHeight / 2);
    bgWrapper.style.transform = 'translate3d(' + (x * -24) + 'px,' + (y * -24) + 'px,0)';
  });

  // Scroll progress
  window.addEventListener('scroll', function() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var maxScroll = container.scrollHeight - window.innerHeight;
    targetProgress = maxScroll > 0 ? Math.max(0, Math.min(1, scrollTop / maxScroll)) : 0;
  }, { passive: true });

  // Helpers
  function setVisible(el, v) { if (!el) return; el.style.visibility = v ? 'visible' : 'hidden'; el.style.pointerEvents = v ? 'auto' : 'none'; }
  function applyStyle(el, op, tx, ty, bl) {
    if (!el) return;
    el.style.opacity = op;
    el.style.transform = 'translate3d(' + tx + 'px,' + ty + 'px,0)';
    el.style.filter = 'blur(' + bl + 'px)';
  }

  // Main rAF loop
  function tick() {
    currentProgress += (targetProgress - currentProgress) * 0.08;
    var p = currentProgress;

    var activeKey = getActiveKey(p);
    var pLocal = activeKey === 'v1' ? Math.max(0, Math.min(1, p * 3))
      : activeKey === 'v2' ? Math.max(0, Math.min(1, (p - 0.333) * 3))
      : Math.max(0, Math.min(1, (p - 0.666) * 3));
    safeSeek(activeKey, pLocal * (durations[activeKey] || 10));

    // Botanical Card
    var f = Math.min(1, Math.max(0, p / 0.15));
    applyStyle(botanicalCard, 1 - f, f * -35, f * 35, f * 16);
    botanicalCard.style.pointerEvents = f > 0.95 ? 'none' : 'auto';

    // Nav header
    f = Math.min(1, Math.max(0, (p - 0.03) / 0.15));
    applyStyle(navHeader, 1 - f, 0, f * -35, f * 14);
    navHeader.style.pointerEvents = f > 0.95 ? 'none' : 'auto';

    // Brand header
    f = Math.min(1, Math.max(0, (p - 0.06) / 0.15));
    applyStyle(brandHeader, 1 - f, f * -25, f * -35, f * 12);
    brandHeader.style.pointerEvents = f > 0.95 ? 'none' : 'auto';

    // Feature cards
    var show = p > 0.13 && p < 0.55;
    setVisible(featuresContainer, show);
    function animCard(el, enterStart, enterDur, exitStart, exitDur, tx, ty) {
      if (!el) return;
      var op = 0, bl = 16, x = tx, y = ty;
      if (p >= enterStart && p <= 0.333) {
        var r = Math.min(1, Math.max(0, (p - enterStart) / enterDur));
        op = r; bl = (1 - r) * 16; x = (1 - r) * tx; y = (1 - r) * ty;
      } else if (p > 0.333 && p <= exitStart + exitDur) {
        var r = Math.min(1, Math.max(0, (p - exitStart) / exitDur));
        op = 1 - r; bl = r * 16; x = r * tx; y = r * ty;
      }
      applyStyle(el, op, x, y, bl);
    }
    animCard(fCard1, 0.15, 0.15, 0.333, 0.12, -35, 35);
    animCard(fCard2, 0.18, 0.13, 0.333, 0.15, 0, 35);
    animCard(fCard3, 0.21, 0.11, 0.333, 0.18, 35, 35);

    // Mission paragraphs
    setVisible(missionContainer, p > 0.44);
    function animPara(el, inS, inE, holdE, outE) {
      if (!el) return;
      var op = 0, bl = 20, y = 120;
      if (p >= inS && p < inE) { var r = (p - inS) / (inE - inS); op = r; bl = (1 - r) * 20; y = (1 - r) * 120; }
      else if (p >= inE && p <= holdE) { op = 1; bl = 0; y = 0; }
      else if (p > holdE && p <= outE) { var r = (p - holdE) / (outE - holdE); op = 1 - r; bl = r * 20; y = r * -120; }
      else if (p > outE) { op = 0; bl = 20; y = -120; }
      applyStyle(el, op, 0, y, bl);
    }
    animPara(mPara1, 0.44, 0.47, 0.59, 0.62);
    animPara(mPara2, 0.62, 0.65, 0.77, 0.80);
    animPara(mPara3, 0.80, 0.83, 0.95, 0.98);

    // Feedback form
    setVisible(feedbackContainer, p > 0.93);
    if (p > 0.93) {
      var opF = 0, blF = 20, yF = 120;
      if (p >= 0.94 && p < 0.97) { var r = (p - 0.94) / 0.03; opF = r; blF = (1 - r) * 20; yF = (1 - r) * 120; }
      else if (p >= 0.97) { opF = 1; blF = 0; yF = 0; }
      applyStyle(feedbackForm, opF, 0, yF, blF);
    }

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // Hamburger menu
  var menuOpen = false;
  var hamburgerBtn = document.getElementById('hamburgerBtn');
  var mobileMenu = document.getElementById('mobileMenu');
  var hLine1 = document.getElementById('hLine1');
  var hLine2 = document.getElementById('hLine2');
  var hLine3 = document.getElementById('hLine3');
  hamburgerBtn.addEventListener('click', function() {
    menuOpen = !menuOpen;
    mobileMenu.classList.toggle('open', menuOpen);
    hLine1.classList.toggle('top-open', menuOpen);
    hLine2.classList.toggle('mid-open', menuOpen);
    hLine3.classList.toggle('bot-open', menuOpen);
    hamburgerBtn.setAttribute('aria-label', menuOpen ? 'Close menu' : 'Open menu');
  });
  document.querySelectorAll('.mobile-link').forEach(function(a) {
    a.addEventListener('click', function() {
      menuOpen = false;
      mobileMenu.classList.remove('open');
      hLine1.classList.remove('top-open');
      hLine2.classList.remove('mid-open');
      hLine3.classList.remove('bot-open');
    });
  });

  // CTA button
  document.getElementById('ctaBtn').addEventListener('click', function() {
    window.scrollTo({ top: window.innerHeight * 0.9, behavior: 'smooth' });
  });

  // Feedback form
  var fbForm = document.getElementById('fbForm');
  var fbBtn = document.getElementById('fbBtn');
  var fbSuccess = document.getElementById('fbSuccess');
  fbForm.addEventListener('submit', function(e) {
    e.preventDefault();
    var email = document.getElementById('fbEmail').value.trim();
    if (email) {
      fbBtn.textContent = 'SUBMITTED';
      fbBtn.classList.add('submitted');
      fbBtn.disabled = true;
      fbSuccess.classList.add('show');
    }
  });
})();
</script>
</body>
</html>

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Scroll Landing Page"
template_id: "22c28996-f14b-4dad-9464-79f90c4818fa"
section: "sites"
category_slug: "other"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Scroll Landing Page

> **Секція:** `SITES` | **Категорія:** `other`  
> **ID шаблону:** `22c28996-f14b-4dad-9464-79f90c4818fa`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Interactive

### 🖼 Прев'ю:
![Scroll Landing Page](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/722111cd-e8bb-4086-848f-feb1b0c54f87.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
**Create a React + Vite + Tailwind CSS v4 landing page for "WISA" -- a premium football/soccer organization website. The page has a scroll-driven video background, 3 content sections, and a glassmorphism footer. Use ONLY these dependencies: react 19, motion (framer-motion v12+), gsap, lucide-react, tailwindcss v4 with @tailwindcss/vite plugin. The design is dark, cinematic, minimal, with Manrope (sans) and JetBrains Mono (mono) fonts.**

---

### GLOBAL SETUP

**package.json dependencies (exact):**
```
react, react-dom ^19.0.0
motion ^12.23.24
gsap ^3.14.2
lucide-react ^0.546.0
tailwindcss ^4.1.14
@tailwindcss/vite ^4.1.14
@vitejs/plugin-react ^5.0.4
vite ^6.2.0
```

**vite.config.ts:** Use `@tailwindcss/vite` plugin + `@vitejs/plugin-react`. Alias `@` to project root.

**index.html:** Standard HTML5. Include `<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>` in head.

**src/index.css -- EXACT:**
```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700&display=swap');
@import "tailwindcss";

@theme {
  --font-sans: "Manrope", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
}

@keyframes flyOutRight {
  0% { transform: translateX(0); }
  100% { transform: translateX(250%); }
}

@keyframes flyInLeft {
  0% { transform: translateX(-250%); }
  100% { transform: translateX(0); }
}

.animate-fly-out {
  animation: flyOutRight 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.animate-fly-in {
  animation: flyInLeft 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes flyOutUp {
  0% { transform: translateY(0); }
  100% { transform: translateY(-150%); }
}

@keyframes flyInUp {
  0% { transform: translateY(150%); }
  100% { transform: translateY(0); }
}

.animate-fly-out-up {
  animation: flyOutUp 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.animate-fly-in-up {
  animation: flyInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
```

These define 4 keyframe animations:
- `flyOutRight / flyInLeft` (250% translateX, 0.5s) -- for the arrow button hover
- `flyOutUp / flyInUp` (150% translateY, 0.4s) -- for nav text hover
- All use `cubic-bezier(0.4, 0, 0.2, 1)` easing with `forwards` fill mode

---

### COMPONENT: ScrollReveal (`src/components/ScrollReveal.tsx` + `ScrollReveal.css`)

**ScrollReveal.css:**
```css
.scroll-reveal { margin: 0; }
.scroll-reveal-text { display: flex; flex-wrap: wrap; margin: 0; }
.word { display: inline-block; white-space: pre; }
```

**ScrollReveal.tsx:** A GSAP-powered word-by-word scroll reveal component.
- Props: `children` (string), `scrollContainerRef?`, `enableBlur` (default true), `baseOpacity` (default 0.1), `baseRotation` (default 3), `blurStrength` (default 4), `containerClassName`, `textClassName`, `rotationEnd` (default "bottom bottom"), `wordAnimationEnd` (default "bottom bottom")
- Splits children text by whitespace into `<span className="word">` elements using `useMemo`
- Three GSAP ScrollTrigger animations:
  1. **Rotation**: Container rotates from `baseRotation` degrees to 0, origin "0% 50%", scrub true, trigger start "top bottom", end = `rotationEnd`
  2. **Opacity**: Each `.word` fades from `baseOpacity` to 1, stagger 0.05, scrub true, trigger start "top bottom-=20%", end = `wordAnimationEnd`
  3. **Blur** (if `enableBlur`): Each `.word` goes from `blur(blurStrength px)` to `blur(0px)`, same stagger/trigger as opacity
- Renders: `<h2 ref={containerRef} className="scroll-reveal {containerClassName}"><p className="scroll-reveal-text {textClassName}">{splitText}</p></h2>`
- Cleanup: kills all ScrollTrigger instances on unmount

---

### COMPONENT: Reveal (inline in App.tsx)

A motion.div wrapper for viewport-triggered fade-in:
```tsx
function Reveal({ children, delay = 0, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```
Easing is `[0.16, 1, 0.3, 1]` (ease-out-expo style).

---

### COMPONENT: NavItem (inline in App.tsx)

A hover-animated navigation link with vertical text fly animation:
- Uses a `cycle` counter state (useState(0))
- On `mouseEnter` and `mouseLeave`: increment cycle
- When `cycle === 0` (initial, no hover yet): render single `<span>` with `text-white/64` and `group-hover:text-white transition-colors duration-300`
- When `cycle > 0`: render TWO spans keyed by cycle -- one with `.animate-fly-out-up` (exits upward), one absolute-positioned with `.animate-fly-in-up` (enters from below)
- Container: `<a>` with `relative overflow-hidden group flex items-center justify-center py-1`

---

### MAIN APP (src/App.tsx) - ARCHITECTURE

**Video URL constant:**
```
const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260521_064421_279656fd-e76f-40a0-8fed-7456d4f7715a.mp4';
```

**State & Refs:**
- `arrowCycle` (useState(0)) -- for arrow button hover animation, same pattern as NavItem
- `videoRef` (useRef HTMLVideoElement)
- `videoContainerRef` (useRef HTMLDivElement)
- `isLoaded` (useState false) -- tracks when video is ready
- `screen3Ref` (useRef HTMLDivElement) -- reference to footer section for scroll calculation
- `scrollY` from motion's `useScroll()`
- `headerY` = `useTransform(scrollY, [0, 500, 800], [0, 0, -150])` -- header slides up and out after scrolling past 500px

---

### SCROLL-DRIVEN VIDEO - CRITICAL IMPLEMENTATION

**Effect 1: Video Loading**
```tsx
useEffect(() => {
  const video = videoRef.current;
  if (!video) return;
  const handleCanPlay = () => setIsLoaded(true);
  video.addEventListener('canplaythrough', handleCanPlay);
  video.load();
  return () => video.removeEventListener('canplaythrough', handleCanPlay);
}, []);
```

**Effect 2: Scroll-to-Video-Scrub (with the `video.seeking` guard)**
```tsx
useEffect(() => {
  if (!isLoaded) return;
  const video = videoRef.current;
  if (!video || !video.duration) return;

  const handleScroll = () => {
    if (!screen3Ref.current || video.seeking) return;
    // ^^ CRITICAL: "video.seeking" check tells the browser: "Only update the video
    // frame when you've completely finished rendering the previous one."
    // Without this guard, rapid scroll events queue up competing .currentTime assignments,
    // causing visible frame tearing, flickering, and dropped frames. The browser's
    // internal seek operation is asynchronous -- setting .currentTime while a previous
    // seek is still in progress gets silently ignored or causes visual glitches.
    // By checking video.seeking, we skip scroll events that arrive before the prior
    // frame has been decoded and painted, resulting in smooth, tear-free scrubbing.

    const rect = screen3Ref.current.getBoundingClientRect();
    const absoluteTop = window.scrollY + rect.top;
    const stopScroll = Math.max(1, absoluteTop - (window.innerHeight * 0.2));
    const scrollFraction = Math.max(0, Math.min(1, window.scrollY / stopScroll));
    video.currentTime = scrollFraction * video.duration;
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
  return () => window.removeEventListener('scroll', handleScroll);
}, [isLoaded]);
```

The scroll fraction maps from 0 (top of page) to 1 (when the footer section is 20% of viewport height from top). This means the video plays through its full duration as the user scrolls from top to the footer.

---

### SECTION 0: LOADING SCREEN

Shown when `!isLoaded`. Fixed fullscreen, z-50, black bg, centered:
- "LOADING" text: `text-[10px] font-mono tracking-widest mb-4 text-white/50`
- Progress bar below: `w-64 h-[1px] bg-white/10 mt-8 overflow-hidden` with inner `h-full bg-white w-1/3 animate-pulse`

---

### LAYER STRUCTURE

The entire page is layered:
1. **Fixed video background** (`fixed inset-0 z-0 bg-black`) -- video is absolutely centered with cover behavior using `transform: translate(-50%, -50%)`, `minWidth/minHeight: 100%`, `objectFit: cover`
2. **Fixed header** (z-20) -- animated with motion, slides out via `headerY` transform
3. **Scrollable content** (`relative z-10 pointer-events-none`) -- all sections flow here, with `pointer-events-auto` on interactive areas

---

### SECTION 1: HERO (Screen 1)

Container: `w-[90%] mx-auto h-screen flex flex-col py-8 md:py-12 lg:py-16 pb-12`

Inner main: `flex-1 w-full pointer-events-auto flex flex-col md:grid md:grid-cols-12 md:grid-rows-[1fr_auto] gap-y-8 md:gap-y-0 md:gap-x-8`

**Grid layout (desktop 12-col, 2-row):**

1. **Heading** (bottom-left): `md:row-start-2 md:col-start-1 md:col-span-8 flex items-end`
   - H1: `text-[clamp(2.5rem,6vw,5rem)] leading-[1.05] font-medium tracking-tight text-white whitespace-nowrap`
   - Text: "Championing" `<br/>` "The Pitch Of Legends"
   - Wrapped in `<Reveal delay={0.2}>`

2. **Description paragraph** (center-right): `md:row-start-1 md:col-start-8 md:col-span-5 flex flex-col justify-center items-start md:items-end text-left md:text-right`
   - Paragraph: `text-[clamp(1rem,1.6vw,1.375rem)] text-white/64 leading-[1.3] font-normal max-w-[460px] relative -top-[90px]`
   - Text: "Advanced preparation and training of world-class football teams for leagues, tournaments, and trophies. **We bring the trophy closer to your cabinet.**" (bold part is `font-semibold text-white`)
   - Wrapped in `<Reveal delay={0.3}>`

3. **CTA Button** (bottom-right): `md:row-start-2 md:col-start-8 md:col-span-5 flex items-end justify-start md:justify-end`
   - Two-part button with 1px gap (`flex items-stretch gap-1 group cursor-pointer`)
   - **Text part**: `px-8 py-5 bg-white/8 backdrop-blur-[80px]` -> on group-hover: `bg-white`. Text: "EXPLORE OUR STADIUMS" in `font-mono text-[12px] tracking-[-0.01em] text-white/90` -> hover: `text-black`
   - **Arrow part**: `px-6 bg-white/8 backdrop-blur-[80px]` -> hover: `bg-white`. Contains `<ArrowRight>` (lucide, w-5 h-5) with the same fly-out/fly-in animation pattern as NavItem but horizontal (`.animate-fly-out` / `.animate-fly-in`)
   - `arrowCycle` state drives the animation, same increment pattern on mouseEnter/mouseLeave
   - Wrapped in `<Reveal delay={0.4}>`

---

### SECTION 1.5: SPACER

`<div className="h-[200px] w-full"></div>` -- 200px empty gap

---

### SECTION 2: SCROLL-REVEAL TEXT + 3-COLUMN GRID

Container: `w-[90%] mx-auto min-h-screen flex flex-col justify-center py-8 md:py-12 lg:py-16 pointer-events-auto`

Inner: `max-w-[1200px] w-full`

**ScrollReveal component usage:**
```tsx
<ScrollReveal
  baseOpacity={0.1}
  enableBlur={true}
  baseRotation={3}
  blurStrength={4}
  textClassName="text-[clamp(2rem,4.5vw,4rem)] leading-[1.1] font-medium tracking-tight text-white w-full"
>
  Complete Football Programs For Professional Player Development. We Build The Foundations For Next-Generation Strikers, Midfielders, And Star Defenders.
</ScrollReveal>
```

**3-Column Grid below** (`mt-24 grid grid-cols-1 md:grid-cols-12 gap-12 md:gap-8`):

1. **Col 1 (md:col-span-4)**: Globe SVG (71x43 wireframe globe) + WISA logo SVG (157x25, scaled to h-[18px] w-auto) side by side with `gap-4`. Below: tagline "Winning the future on pitch" in `text-[11px] font-mono tracking-widest text-white/60 uppercase leading-relaxed`. Wrapped in `<Reveal delay={0.1}>`

2. **Col 2 (md:col-span-4)**: H3 "Performance Analytics / Facilities" (`text-xl font-medium text-white`), paragraph below (`text-[15px] text-white/80 leading-relaxed`). Wrapped in `<Reveal delay={0.2}>`

3. **Col 3 (md:col-span-4)**: H3 "Matchday Premium / Fan Experiences!" same styling, paragraph same styling. Wrapped in `<Reveal delay={0.3}>`

---

### SECTION 2.5: SPACER

Another `h-[200px]` spacer

---

### SECTION 3: FOOTER (ref={screen3Ref})

This is the scroll endpoint for the video scrub calculation. Wrapped in `pointer-events-auto`.

**Footer container**: `width: 90%, margin: 0 auto, paddingBottom: 64px` (inline styles)

**Inner card** (glassmorphism): `backgroundColor: rgba(26, 26, 26, 0.6)`, `backdropFilter: blur(80px)`, `WebkitBackdropFilter: blur(80px)`, `border: 1px solid rgba(255, 255, 255, 0.1)`, `padding: clamp(32px, 4vw, 64px)` -- all inline styles

**CTA Section** (top of footer card):
- Flexbox wrap, `alignItems: flex-end`, `justifyContent: space-between`, `gap: 40px`
- Bottom border: `1px solid rgba(255, 255, 255, 0.1)`, `paddingBottom: clamp(48px, 4vw, 80px)`
- H2: "Ready To Score / Your Winning Season?" -- `fontSize: clamp(2rem, 4.5vw, 3.5rem)`, `fontWeight: 500`, `letterSpacing: -0.02em`, `lineHeight: 1.05`
- Button: Same two-part pattern (text + arrow) but with white bg / black text, `padding: 20px 32px` and `20px 24px`. Text: "START YOUR SEASONS" in `font-mono, 12px, -0.01em tracking, bold 700`

**Footer Links Grid** (`paddingTop: clamp(48px, 4vw, 64px)`):
- CSS Grid: `repeat(auto-fit, minmax(160px, 1fr))`, `gap: clamp(32px, 3vw, 48px)`
- 4 columns:
  1. **Brand**: WISA logo SVG (h:14px) + tagline paragraph (13px, rgba white 0.4, maxWidth 220)
  2. **Company**: Header "COMPANY" (10px mono, 0.1em tracking, rgba white 0.3) + links: About, Rosters, Press, Contact (14px, rgba white 0.6)
  3. **Services**: Header "SERVICES" same style + links: Coaching, Training Camp, Fitness, Tryout
  4. **Connect**: Header "CONNECT" same style + links: LinkedIn, X / Twitter, YouTube, Newsletter

**Copyright Bar** (`marginTop: 56, paddingTop: 32, borderTop: 1px solid rgba white 0.1`):
- Flex wrap space-between
- Left: "2026 WISA. ALL RIGHTS RESERVED." (11px mono, rgba white 0.25, 0.1em tracking)
- Right: PRIVACY | TERMS links (same styling, gap-24px)

---

### FIXED HEADER

`<motion.header>` with:
- `style={{ y: headerY }}` -- slides out after scroll 500-800px
- `initial={{ opacity: 0, y: 20 }}`, `animate={{ opacity: 1 }}`, easing `[0.16, 1, 0.3, 1]`, duration 0.8
- Classes: `fixed top-0 left-1/2 -translate-x-1/2 z-20 w-[90%] flex items-center justify-between pointer-events-auto py-4 md:py-6 lg:py-8`

**Left: WISA Logo SVG** (157x25, white, 4 paths spelling "WISA")

**Right: Navigation bar** (`hidden lg:flex items-stretch bg-[#1A1A1A]/40 backdrop-blur-[80px]`):
- Nav links container: `flex items-center justify-between px-6 font-mono text-xs tracking-[-0.01em] w-[480px]`
- 5 NavItem components: LEAGUES, STADIUMS, TRAINING, COMPETITIONS, TICKETS
- CTA button: `bg-white text-black px-6 py-5 font-mono text-xs leading-4 font-bold tracking-[-0.01em] hover:bg-gray-200 transition-colors w-[148px]` -- text "BUY MATCH PASS"

---

### SVG ASSETS

**WISA Logo** (used 3 times -- header, section 2, footer): 157x25 viewBox, 4 white paths. The paths spell "W I S A" in a custom typeface.

**Globe icon** (used in section 2 col 1): 71x43 viewBox, wireframe globe with horizontal/vertical/meridian lines, stroke white, no fill.

Both SVGs are inlined directly. They are too detailed to describe -- copy the exact path data from the source code above.

---

### KEY DESIGN TOKENS SUMMARY

| Token | Value |
|-------|-------|
| Font sans | Manrope 300-700 |
| Font mono | JetBrains Mono 400-700 |
| Background | Pure black (#000) |
| Text primary | white |
| Text secondary | white/64 (rgba 255,255,255,0.64) |
| Text muted | white/60, white/50, white/40, white/25 |
| Glass bg | #1A1A1A at 40% opacity |
| Glass blur | 80px |
| Glass border | rgba(255,255,255,0.1) |
| Button bg | white/8 -> white on hover |
| Spacing rhythm | 90% viewport width container, clamp-based responsive values |
| Easing (motion) | [0.16, 1, 0.3, 1] |
| Easing (CSS) | cubic-bezier(0.4, 0, 0.2, 1) |
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Future-State"
template_id: "1df26e26-393b-482a-a456-f6864616cd0a"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Future-State

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `1df26e26-393b-482a-a456-f6864616cd0a`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Future-State](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/c5d221ef-64f0-42d9-b368-a756e0398aae.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a dark, cinematic single-page landing site for an AI product called NOVA_AI using Vite + React + TypeScript + Tailwind CSS, with icons from lucide-react only. No other UI packages.

Global setup

- `index.html` title: `NOVA_AI — Today AI Aligns With Bold Dreams`. Load this font in `<head>`:

  `<link href="https://db.onlinewebfonts.com/c/4556933d6966c60eda45bebad34d9c90?family=Flexo+Soft+Medium" rel="stylesheet" />`

- `index.css`: Tailwind base/components/utilities; `body { font-family: 'Flexo Soft Medium', system-ui, sans-serif; background-color: #0a0a0a; color: #fff; -webkit-font-smoothing: antialiased; }`; `::selection { background-color: rgba(255,255,255,0.2); }`

- `tailwind.config.js`: extend `fontFamily` so BOTH `sans` and `mono` map to `['"Flexo Soft Medium"', 'system-ui', 'sans-serif']`.

- `App.tsx` renders, inside `<div className="relative">`: `<ScrollVideo />`, `<Navbar />`, then `<main>` containing `<SectionOne />`, a spacer `<div aria-hidden className="h-[80vh]" />`, and `<SectionTwo />`.

Component 1 — ScrollVideo (scroll-scrubbed video background)

Fixed full-viewport background (`fixed inset-0 -z-10 bg-[#0a0a0a]`) that scrubs a video based on total page scroll progress. Video URL (exact):

`https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260611_104107_121bfb5a-b1df-4e0d-8240-25b81f7cc85d.mp4`

Implementation details:

1. On mount, `fetch` the video as a blob, create an object URL, and pre-extract frames into `ImageBitmap[]`: create an off-DOM `<video>` (muted, playsInline, preload auto), wait for metadata, scale to max width 1280, frame count = `clamp(round(duration * 24), 30, 120)`, seek evenly across `duration - 0.05` and `createImageBitmap` each frame (with resize). Support cancellation; close bitmaps and revoke the object URL on unmount.

2. Render a `<canvas className="absolute inset-0 h-full w-full">`. While frames aren't ready, render a fallback `<video>` element (same URL, muted, playsInline, `object-cover`, absolute inset-0 full size) and scrub it by setting `currentTime` (guard with a `seeking` flag + `seeked` listener; only seek when delta > 0.001s).

3. Animation loop (`requestAnimationFrame`): target progress = `window.scrollY / (scrollHeight - innerHeight)` clamped 0–1, smoothed each tick via `smoothed += (target - smoothed) * 0.1`. Map smoothed progress to a frame index and only redraw when the index changes. Draw with "cover" math (scale = max of canvas/frame ratios, center the overflow). Canvas resolution = clientWidth/Height × devicePixelRatio capped at 2; re-size on window resize. Passive scroll listener.

4. Overlay `<div className="absolute inset-0 bg-black/20" />` for text contrast.

Component 2 — Reveal (staggered scroll animation wrapper)

Reusable component: props `children`, `delay?: number` (ms), `className?: string`, `as?: 'div' | 'span'` (default `'div'`). Uses an IntersectionObserver (threshold 0.15) and sets visible = `entry.isIntersecting` — i.e., animations REPLAY when elements leave and re-enter the viewport. Renders:

`transition-all duration-700 ease-out will-change-transform`, visible → `translate-y-0 opacity-100`, hidden → `translate-y-8 opacity-0`, plus `style={{ transitionDelay: `${delay}ms` }}` and the passed className. Disconnect observer on unmount.

Component 3 — Navbar (fixed corners)

- Top-left (`fixed left-5 top-5 z-50 sm:left-8 sm:top-7 md:left-12`): wordmark link `(NOVA_AI)` in `font-mono text-lg font-medium tracking-tight text-white drop-shadow-md sm:text-xl md:text-2xl` wrapped in `<Reveal>`; below it (delay 150) `[ v.01b ]` in `mt-6 font-mono text-[10px] text-white/60 sm:mt-8 sm:text-xs`.

- Top-right `<nav>` (`fixed right-5 top-5 z-50 sm:right-8 sm:top-7 md:right-12`): vertical right-aligned `<ul>` (`flex flex-col items-end gap-1.5 sm:gap-2`) with links `main`, `tiers`, `features`, `talk to us`. Each `<li>` wraps a `<Reveal delay={100 + i * 120}>` containing an anchor: `group flex items-center gap-1 font-mono text-xs text-white/80 drop-shadow-md transition-colors duration-300 hover:text-white sm:text-sm` plus an `ArrowUpRight` icon (size 14) that translates up-right on group hover (`group-hover:-translate-y-0.5 group-hover:translate-x-0.5`).

Component 4 — SectionOne (hero, bottom-anchored)

`<section className="relative flex min-h-screen flex-col justify-end supports-[height:100svh]:min-h-[100svh]">`. Content row: `relative flex flex-col gap-10 px-5 pb-16 sm:flex-row sm:items-end sm:justify-between sm:gap-8 sm:px-8 md:px-12 md:pb-20`.

- Left: `<h1 className="max-w-xl text-4xl font-medium uppercase leading-[1.05] tracking-tight text-white drop-shadow-lg sm:text-5xl md:text-6xl lg:text-7xl">` with four staggered lines, each a `<Reveal as="span" className="block ...">`:

  1. delay 100, `pl-6 sm:pl-12`: `Today AI`

  2. delay 220, no indent: `Aligns ` + `<span className="normal-case italic font-light">with</span>`

  3. delay 340, `pl-10 sm:pl-20`: `// Bold`

  4. delay 460, `pl-16 sm:pl-32`: `Dreams`

- Right column (`flex w-full max-w-xs flex-col items-start` — visible on ALL breakpoints, stacks under the headline on mobile):

  - Reveal delay 400: row `mb-6 flex w-full items-center justify-between font-mono text-white sm:mb-8` with `( A )` (text-lg) and `[ 001 /004 ]` (`text-xs text-white/70`).

  - Reveal delay 520: paragraph `mb-6 text-sm leading-relaxed text-white/85 drop-shadow-md sm:mb-8`: "NovaAI is where your bravest work finds its true expression. We hand you the means not only to form the future."

  - Reveal delay 640: full-width pill CTA `Begin Today`: `block w-full rounded-full border border-white/60 px-8 py-3 text-center font-mono text-xs uppercase tracking-[0.15em] text-white transition-all duration-300 hover:bg-white hover:text-black`.

- Absolute bottom-left (Reveal delay 760, `bottom-5 left-5 sm:bottom-6 sm:left-8 md:left-12`): `Share2` icon button (size 18, `text-white/80 hover:text-white`, aria-label "Share").

- Absolute bottom-center (Reveal delay 760, `bottom-5 left-1/2 -translate-x-1/2 sm:bottom-6`): `ArrowDown` size 18 with `animate-bounce text-white/80`.

Component 5 — SectionTwo

`<section className="relative flex min-h-screen flex-col supports-[height:100svh]:min-h-[100svh]">`.

- Middle row: `relative flex flex-1 flex-col justify-center gap-10 px-5 pt-24 sm:flex-row sm:items-center sm:justify-between sm:gap-8 sm:px-8 sm:pt-0 md:px-12`.

  - `<h2 className="max-w-sm text-4xl font-medium uppercase leading-[1.05] tracking-tight text-white drop-shadow-lg sm:text-5xl md:text-6xl">`, two Reveal lines: delay 100 `Learn ` + italic `<span className="normal-case italic font-light">to see</span>`; delay 220 `Brilliantly`.

  - Reveal delay 340: `flex items-center justify-between font-mono text-white sm:justify-start sm:gap-16 md:gap-24` with `( B )` (text-lg) and `[ 002 /004 ]` (`text-xs text-white/70`).

- Bottom block: `relative flex flex-col gap-10 px-5 pb-16 sm:px-8 md:px-12 md:pb-20`.

  - Reveal delay 460 paragraph (`max-w-xs text-sm leading-relaxed text-white/85 drop-shadow-md`): "Our AI doesn't just respond — it interprets, sharpens, and delivers. From outline to final render, it supplies the insight you want."

  - Reveal delay 580 CTA `Run The Demo`, in-flow full-width on mobile, absolutely bottom-centered on sm+: wrapper `w-full max-w-xs sm:absolute sm:bottom-16 sm:left-1/2 sm:w-auto sm:max-w-none sm:-translate-x-1/2 md:bottom-20`; anchor `block rounded-full border border-white/60 px-10 py-3 text-center font-mono text-xs uppercase tracking-[0.15em] text-white transition-all duration-300 hover:bg-white hover:text-black`.

- Reveal delay 700, absolute bottom-left (same classes as Section 1): `Share2` icon button.

Responsiveness rules

Mobile-first: hero and section content stack vertically (`flex-col`) and switch to side-by-side (`sm:flex-row`) at 640px; horizontal padding scales `px-5 → sm:px-8 → md:px-12`; headline sizes scale `text-4xl → sm:text-5xl → md:text-6xl (→ lg:text-7xl hero)`; headline indents shrink on mobile; Section 2 gets `pt-24` on mobile to clear the fixed nav. All text must remain readable over the video (drop shadows + black/20 overlay).
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Urban Jungle"
template_id: "e426b8bc-a3f6-4568-90b1-d8442528e52f"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Urban Jungle

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `e426b8bc-a3f6-4568-90b1-d8442528e52f`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Urban Jungle](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/e3f7bd4f-8047-44f1-b3d2-c63fb27a633c.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a scroll-driven hero section landing page using React 19, Vite, Tailwind CSS v4 (using @tailwindcss/vite plugin), GSAP (with ScrollTrigger + ScrollToPlugin), hls.js, and react-router-dom (BrowserRouter). The page body is black with white text. The root container is 500vh tall.

SETUP
Dependencies (package.json):

react, react-dom, react-router-dom, gsap, hls.js, lucide-react, motion, tailwindcss v4, @tailwindcss/vite, @vitejs/plugin-react, vite
Vite config: Use @tailwindcss/vite and @vitejs/plugin-react plugins.

Entry point (main.tsx): Wrap <App /> in <StrictMode> and <BrowserRouter>.

Custom headline font: Download the font file from https://dirtylinestudio.com/wp-content/uploads/2022/05/Dirtyline-36daysoftype-2022.woff2 and save it to the public/ directory as Dirtyline-36daysoftype-2022.woff2. Then register it via @font-face in CSS.

Google Fonts (loaded via CSS @import): Manrope:wght@400;500;600;700 and Instrument+Serif:ital@0;1

Tailwind v4 theme (index.css):

@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
@import "tailwindcss";

@theme {
  --font-sans: "Manrope", ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  --font-serif: "Instrument Serif", ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  --font-dirtyline: "Dirtyline36Daysoftype2022", sans-serif;
  --animate-marquee: marquee 20s linear infinite;
  @keyframes marquee {
    100% { transform: translateX(-50%); }
  }
}

@font-face {
  font-family: 'Dirtyline36Daysoftype2022';
  src: url('/Dirtyline-36daysoftype-2022.woff2') format('woff2');
  font-style: normal;
  font-weight: normal;
  text-rendering: optimizeLegibility;
  font-display: swap;
}

body {
  background-color: black;
  color: white;
}

LAYER 1: BACKGROUND -- ScrollVideo Component
A full-screen fixed video background that scrubs its playback position based on scroll progress (scroll at top = frame 0, scroll at bottom = last frame).

Video source (Mux HLS stream):
https://stream.mux.com/43NlHXsaMrmyzWamMk87m01fNyxSTekAD669BBAPBNm00.m3u8

Props: src (string), className (string)

Implementation:

Use hls.js. On MANIFEST_PARSED, force the highest quality level: hls.currentLevel = maxLevel; hls.startLevel = maxLevel. Config: maxBufferLength: 120, maxMaxBufferLength: 600, maxBufferSize: 200 * 1024 * 1024, startPosition: 0, capLevelToPlayerSize: false, startLevel: -1, autoStartLoad: true.
For Safari (native HLS), set video.src = src directly.
Track buffer progress via FRAG_BUFFERED event, calculating (bufferedEnd / duration) * 100.
The <video> element is rendered directly (no canvas). Classes: w-full h-full object-cover scale-[1.35]. Attributes: muted, playsInline, crossOrigin="anonymous".
Scroll-to-seek: Use GSAP ScrollTrigger.create with trigger: document.documentElement, start: 'top top', end: 'bottom bottom', scrub: true. On onUpdate, calculate targetTime = self.progress * duration. Throttle seeking: track a currentTarget variable. If video.seeking is true, set seekPending = true. On the seeked event, if seekPending, call doSeek() again with the latest currentTarget. This prevents hammering the decoder.
if (!video.seeking).
Тепер ми кажемо браузеру: "Оновлюй кадр відео ТІЛЬКИ тоді, коли ти повністю закінчив малювати попередній"."
Mouse parallax on video wrapper: On mousemove, GSAP tweens the wrapper's x/y by moveX * -30 and moveY * -30, where moveX/moveY are normalized mouse offset from center (-1 to 1). Duration: 1.5, ease: power2.out.
Loading overlay: Show a fixed, z-50, centered black overlay with "Loading... {progress}%" in white, text-2xl font-sans. Hide once canplay fires.
Wrapper div classes: fixed top-0 left-0 w-full h-full z-0 scale-[1.05] origin-center

LAYER 2: HERO TEXT -- ScrollFloat Component
A fixed overlay at z-10, positioned at the bottom of the viewport: fixed inset-0 flex flex-col justify-end p-4 md:p-8 pointer-events-none.

Text content: "Unleash The\nFull Power" (literal newline between the two lines).

ScrollFloat component implementation:

Splits the text string by \n into lines, then by spaces into words, then into individual characters.
Each line is wrapped in <span style="display: block">.
Each word is wrapped in <span style="display: inline-block; white-space: nowrap">.
Each character is wrapped in <span class="char">.
Word separators: &nbsp; between words.
Animation: Uses gsap.fromTo on all .char elements. FROM: {opacity: 1, yPercent: 0, scaleY: 1, scaleX: 1, transformOrigin: '50% 0%'}. TO: {opacity: 0, yPercent: 250, scaleY: 1.2, scaleX: 0.9}. So the text starts fully visible and animates away as you scroll down.
ScrollTrigger config: trigger: document.body, start: 'top top', end: '+=1000', scrub: 1.5.
Stagger: 0.05, ease: power2.inOut, duration: 1.
Typography: Font family: font-dirtyline (the Dirtyline custom font). Font size: clamp(4rem, 15vw, 317px). Line height: 0.85. Letter spacing: 0%. Color: white.

ScrollFloat.css:
.scroll-float-text { display: inline-block; }
.char { display: inline-block; }

LAYER 3: GLASS PANEL -- GlassPanel Component (About Us section)
Positioned absolutely at the bottom of the 500vh container: absolute bottom-0 left-0 w-full h-screen. It slides up from below as you scroll to the bottom.

Slide-up animation: gsap.fromTo on the panel wrapper: from {y: '100%'} to {y: '0%'}, ease: none. ScrollTrigger: trigger is the container div, start: 'top bottom', end: 'bottom bottom', scrub: 1.5.

Panel wrapper: w-full max-w-[1250px] h-[900px] max-h-[85vh] pointer-events-auto with perspective: 1000px inline style.

Panel itself: w-full h-full flex flex-col justify-between rounded-3xl relative overflow-hidden with inline styles:
backgroundColor: 'rgba(0, 0, 0, 0.16)'
backdropFilter: 'blur(160px)'
WebkitBackdropFilter: 'blur(160px)'
border: '1px solid rgba(255, 255, 255, 0.1)'
transformStyle: 'preserve-3d'
willChange: 'transform'

3D mouse parallax on panel: On mousemove, GSAP tweens: x: moveX * 20, y: moveY * 20, rotationY: moveX * 4, rotationX: -moveY * 4. Ease: power3.out, duration: 1.

Content (all centered text):
Subtitle: <p> with font-serif italic text-white/70 text-base md:text-lg mb-4 md:mb-6 -- text: "About Us"
Main heading: <h2> with font-serif text-white text-4xl md:text-6xl lg:text-[96px] leading-[1.1] lg:leading-[92.6px] tracking-tight w-full max-w-[1000px] mx-auto -- text: "We transform sterile concrete into thriving urban jungles. Our innovative designs bring wild nature back to modern cities. Experience the bloom" where the italic words (urban, nature, bloom) are wrapped in <span className="italic">.
All text is centered: the content area uses flex flex-col items-center justify-center px-6 md:px-12 text-center.

Bottom marquee (text-based logos, not images):
Instead of image logos, use text brand names as the marquee items. Use names like "VOICEFLOW", "ZENDESK", "PENDO", "GLIDE", "CANVA". Each name is rendered as white text, opacity-40 hover:opacity-100 transition-opacity duration-300, uppercase, font-sans font-semibold text-sm tracking-widest. The marquee row is duplicated 4x for seamless infinite scroll, using the CSS animate-marquee keyframe (translateX(-50%) over 20s linear infinite). The marquee sits at the bottom of the glass panel, separated by a border-t border-white/10 py-6.

LAYER 4: PILL NAVIGATION -- PillNav Component
Fixed at top center of viewport (position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 100). Font: Manrope, 600 weight, 14px, uppercase, 0.05em letter-spacing.

Structure:
A circular black logo button (48x48px, border-radius: 50%) containing a 4-petal SVG icon (white fill, 24x24). The SVG paths:
m50,50c0,18.2,14.77,32.98,32.97,32.98,0-18.2-14.77-32.98-32.97-32.98Z
m17.02,82.98c18.2,0,32.98-14.77,32.98-32.98-18.2,0-32.98,14.77-32.98,32.98Z
m82.98,17.02c-18.2,0-32.97,14.77-32.97,32.97,18.2,0,32.97-14.77,32.97-32.97Z
m17.02,17.02c0,18.2,14.77,32.97,32.98,32.97,0-18.2-14.77-32.97-32.98-32.97Z
viewBox: 0 0 100 100. On hover, the SVG container rotates 360deg via GSAP (duration: 0.2).

Nav items container: black background, border-radius: 50px, padding: 4px, border: 2px solid #000. Contains a <ul> with flex layout, gap: 4px.

Each nav pill: padding: 8px 24px, border-radius: 50px, background-color: #f0f0f0, color: #000, font-weight: 600, font-size: 14px, letter-spacing: 0.05em, text-transform: uppercase, overflow: hidden, position: relative.

Pill hover effect (GSAP-powered liquid fill):
Each pill contains a hidden .hover-circle element (absolute, black, border-radius: 50%, scale: 0).
The circle's size is calculated dynamically: R = (w*w/4 + h*h) / (2*h), D = 2*R + 2, positioned at bottom: -delta where delta = R - sqrt(R*R - w*w/4) + 1. Transform origin: 50% ${D - delta}px.
A .label-stack contains two labels: .pill-label (dark text, visible) and .pill-label-hover (white text, hidden below).
On hover enter: a GSAP timeline plays forward -- circle scales to 3, pill-label slides up out of view, pill-label-hover slides up into view (white text over black circle). Timeline tweened to end in 0.3s.
On hover leave: timeline tweened back to 0 in 0.2s.

Nav items: HOME, ABOUT, SERVICES, CONTACT.
HOME onClick: gsap.to(window, { duration: 3, scrollTo: 0, ease: 'power3.inOut' })
ABOUT onClick: gsap.to(window, { duration: 3, scrollTo: document.body.scrollHeight, ease: 'power3.inOut' })

Initial load animation: Logo scales from 0 to 1 (duration 0.6). Nav items container width animates from 0 to auto (duration 0.6).

Responsive: At 768px breakpoint, desktop nav items are hidden and replaced with a hamburger button (two 24x2px lines, gap 4px). On toggle, lines animate to X shape (rotation +/-45deg, y +/-3px). A popover menu appears below with fade+slide animation.

PillNav.css (full):
.pill-nav-container { position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 100; font-family: 'Manrope', sans-serif; }
.pill-nav { display: flex; align-items: center; background-color: transparent; padding: 0; gap: 0; }
.pill-logo { display: flex; align-items: center; justify-content: center; border-radius: 50%; background-color: #000; width: 48px; height: 48px; flex-shrink: 0; }
.logo-svg-container { display: flex; align-items: center; justify-content: center; }
.pill-nav-items { background-color: #000; border-radius: 50px; padding: 4px; border: 2px solid #000; }
.pill-list { display: flex; align-items: center; gap: 4px; list-style: none; margin: 0; padding: 0; }
.pill { position: relative; display: block; padding: 8px 24px; border-radius: 50px; text-decoration: none; color: #000; font-weight: 600; font-size: 14px; letter-spacing: 0.05em; text-transform: uppercase; overflow: hidden; background-color: #f0f0f0; transition: background-color 0.3s ease; }
.pill.is-active { background-color: #e0e0e0; }
.hover-circle { position: absolute; background-color: #000; border-radius: 50%; pointer-events: none; z-index: 0; transform: scale(0); }
.label-stack { position: relative; display: block; z-index: 1; overflow: hidden; height: 1.2em; }
.pill-label, .pill-label-hover { display: block; line-height: 1.2em; text-align: center; }
.pill-label-hover { position: absolute; top: 0; left: 0; width: 100%; color: #fff; }
.mobile-menu-button { background: none; border: none; cursor: pointer; display: flex; flex-direction: column; gap: 4px; padding: 8px; }
.hamburger-line { width: 24px; height: 2px; background-color: var(--pill-text); display: block; }
.mobile-menu-popover { position: absolute; top: 100%; left: 0; right: 0; margin-top: 8px; background-color: var(--pill-bg); border-radius: 16px; padding: 16px; visibility: hidden; }
.mobile-menu-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
.mobile-menu-link { color: var(--pill-text); text-decoration: none; font-size: 1.1rem; display: block; text-align: center; }
@media (min-width: 769px) { .mobile-only { display: none !important; } }
@media (max-width: 768px) { .desktop-only { display: none !important; } }

APP COMPONENT ASSEMBLY
<ScrollVideo src="https://stream.mux.com/43NlHXsaMrmyzWamMk87m01fNyxSTekAD669BBAPBNm00.m3u8" />
<PillNav />
<div style={{ position: "relative", height: "500vh" }}>
  <ScrollFloat>{`Unleash The\nFull Power`}</ScrollFloat>
  <GlassPanel />
</div>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "SaaS Value"
template_id: "2826eb48-2c0a-4186-ba16-57e129ba3fbe"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 SaaS Value

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `2826eb48-2c0a-4186-ba16-57e129ba3fbe`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![SaaS Value](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5094f990-7c41-461d-9f8e-6e61104ca6ae.png)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-viewport hero section for a SaaS landing page called "Questly" using React, TypeScript, Tailwind CSS 3, and Vite. Use `lucide-react` for all icons. No other UI libraries.

---

FONT

Use the font "Nimbus Sans TW01" loaded from this stylesheet in `index.html`:

```
https://db.onlinewebfonts.com/c/bb5de19d87c09a95216dc6ccd96e37c6?family=Nimbus+Sans+TW01
```

Set the font stack in both `tailwind.config.js` and `index.css`:

```
'Nimbus Sans TW01', 'Helvetica Neue', Helvetica, Arial, sans-serif
```

Enable `-webkit-font-smoothing: antialiased` and `-moz-osx-font-smoothing: grayscale` on `html`.

---

BACKGROUND IMAGE

The full hero section uses this image as a `background-image` (cover, centered):

```
https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260611_133301_d5f2a94a-b22e-4e4a-a6b6-eacdddf1f5b0.png&w=1280&q=85
```

Applied via inline `style={{ backgroundImage: url(...) }}` on the `

`. The section is `relative min-h-[100svh] overflow-hidden bg-cover bg-center flex flex-col`.

---

GRASS OVERLAY

An absolutely positioned grass PNG sits at the bottom of the section, full width, `z-10`, pointer-events-none, select-none:

```
https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1781191264/grass_eam204.png
```

Classes: `pointer-events-none absolute bottom-0 left-0 z-10 w-full select-none`

---

LOGO (SVG Component)

A custom SVG logo component used in the navbar and dashboard sidebar. It uses `currentColor` for fill so it inherits text color. ViewBox: `0 0 256 256`. Path data:

```
M 144 256 L 27.598 256 L 144 139.598 Z M 256 207.5 L 200 256 L 200 56 L 0 56 L 48 0 L 256 0 Z M 0 204.402 L 0 112 L 92.402 112 Z
```

---

NAVBAR

- Positioned with `animate-fade-down relative z-20`
- Flex row: logo left, nav links center, CTA + hamburger right
- Horizontal padding: `px-5 sm:px-8 lg:px-10`, vertical: `py-4 sm:py-5`
- Logo: `text-gray-900`, icon sized `w-5 h-5 sm:w-6 sm:h-6`
- Desktop nav links (hidden below `md`): `text-[13px] text-gray-700`, hover `text-gray-900`, gap-8. Items: "Toolkit" (with `ChevronDown` icon `w-3.5 h-3.5`), "Plans", "News"
- CTA button: `bg-gray-900 text-white text-[13px] font-medium px-4 sm:px-5 py-2 rounded-full hover:bg-gray-800`
- Hamburger (md:hidden): `w-9 h-9 rounded-full text-gray-900 hover:bg-gray-900/10`, toggles `Menu`/`X` icons (`w-5 h-5`)
- Mobile dropdown (when open): `absolute left-4 right-4 top-full rounded-2xl bg-white/80 backdrop-blur-xl ring-1 ring-gray-200 px-5 py-3 animate-fade-up`. Links: `text-[15px] text-gray-700 hover:text-gray-900 border-b border-gray-200 last:border-b-0`

---

HERO CONTENT (centered, text-center)

Spacing between navbar and content uses a flex spacer: `flex-1 min-h-8 sm:min-h-12 lg:min-h-16 shrink-0`

Headline (h1)
- `text-gray-900 font-normal leading-[1.05] tracking-tight`
- Sizes: `text-[40px] min-[400px]:text-[44px] sm:text-6xl lg:text-7xl xl:text-[80px]`
- Two lines, each a `` with staggered `animate-fade-up`:
  - Line 1: "Get cited." (no delay)
  - Line 2: "Effortlessly." (`[animation-delay:100ms]`)

### Search Bar (form)
- `animate-fade-up [animation-delay:220ms] mt-5 sm:mt-6 w-full max-w-xl`
- Pill container: `flex items-center gap-3 rounded-full bg-white/60 backdrop-blur-md ring-1 ring-gray-200 pl-5 pr-1.5 py-1.5`
- Input: `flex-1 bg-transparent text-sm sm:text-base text-gray-900 placeholder-gray-500 outline-none py-2`, placeholder: "What makes content rank in AI search?"
- Submit button: `w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-900 text-white hover:scale-105 active:scale-95 transition-transform shrink-0`, contains `ArrowUp` icon `w-4 h-4 sm:w-[18px] sm:h-[18px]`

### Description
- `animate-fade-up [animation-delay:340ms] mt-4 sm:mt-5 text-gray-600 text-sm sm:text-base lg:text-lg leading-relaxed max-w-md`
- Text: "Ship articles that answer actual customer questions -- and be seen on [Sparkles icon] ChatGPT"
- Line break `
` before the dash
- `Sparkles` icon: `inline w-4 h-4 -mt-1`

### CTA Buttons
- `animate-fade-up [animation-delay:460ms] mt-4 sm:mt-5 flex flex-wrap items-center justify-center gap-3`
- **Primary**: `bg-gray-900 text-white text-sm font-medium px-6 py-2.5 rounded-full hover:bg-gray-800 hover:shadow-lg transition-all` -- "Try It Free"
- **Secondary**: `text-gray-700 text-sm font-medium px-6 py-2.5 rounded-full ring-1 ring-gray-300 hover:bg-gray-100 transition-colors` -- "Talk to sales"

---

## DASHBOARD MOCKUP (below the hero content)

Another flex spacer (`flex-1 min-h-10 sm:min-h-12 lg:min-h-16 shrink-0`) separates the content from the dashboard.

### Container
- `animate-hero-rise [animation-delay:620ms] relative z-0 w-[92%] sm:w-[84%] lg:w-[72%] max-w-4xl mx-auto shrink-0 -mb-10 sm:-mb-20 lg:-mb-32`
- Uses a **ScaledDashboard** wrapper: a `ResizeObserver`-based component that renders the mockup at a fixed design width of **896px** and scales it down via CSS `transform: scale()` to fit its container, with `transformOrigin: 'top left'`. The outer div's height is set to `inner.offsetHeight * scale` to prevent layout overflow.

### Mockup Chrome
- Outer: `rounded-t-2xl overflow-hidden bg-[#1a1a1c] shadow-[0_-20px_80px_rgba(0,0,0,0.35)] ring-1 ring-white/10 text-left`
- **Title bar**: `bg-[#242427] border-b border-white/5 px-4 py-2.5`
  - Traffic lights: three spans `w-2.5 h-2.5 rounded-full` colored `#ff5f57`, `#febc2e`, `#28c840`
  - Icons (all `w-3.5 h-3.5 text-white/40`): `PanelLeft`, `ChevronLeft`, `ChevronRight` (text-white/25)
  - Center URL bar: `bg-[#1a1a1c] rounded-md px-6 py-1 text-[10px] text-white/60` with `Monitor` icon -- text "questly.ai"
  - Right icons: `RotateCw`, `Share`, `Plus`, `Copy`

### Sidebar (22% width)
- `border-r border-white/5 bg-[#1e1e21] px-3 py-3.5`
- Logo icon `w-4 h-4 text-white/70` + `Grid` icon `w-3.5 h-3.5 text-white/30`
- Workspace badge: `w-4 h-4 rounded bg-[#e8553f]` with "C" letter, label "CareNest" `text-[10px] text-white/80`
- Nav items: Compass/Uncover, Layers/Subjects, ListTodo/Inbox -- `text-[10px] text-white/60`
- Recent articles list with "Ready to Release" green dots `text-[#28c840]/70`

### Main Content Area
- Header: workspace icon (larger `w-9 h-9 rounded-lg bg-[#e8553f]`), "CareNest" `text-sm font-medium text-white`, subtitle `text-[10px] text-white/45`, and a "Generate" button with `Sparkles` icon
- **Stats grid** (4 columns): `grid-cols-4 divide-x divide-white/5 rounded-xl bg-white/[0.03] ring-1 ring-white/5`
  - RELEASED: 62 / Posts indexed
  - BREADTH: 12 / Subject groups
  - REMAINING: 412 / Ready to draft
  - MAX REACH: 3,156,200 / Searches a month
  - Values: `text-xl font-medium text-white`, labels: `text-[8px] tracking-wider text-white/35`
- **Subject cards** (3 columns): Elder Care, Mobility, Home Safety -- `rounded-lg bg-white/[0.03] ring-1 ring-white/5`
- **Drafting inbox** table: 5 rows with question, volume, difficulty, status columns. "Drafting" status colored `text-[#febc2e]/80`

---

## ANIMATIONS (defined in index.css)

```css
@keyframes fade-up {
  from { opacity: 0; transform: translateY(24px); filter: blur(6px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}

@keyframes fade-down {
  from { opacity: 0; transform: translateY(-16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes hero-rise {
  from { opacity: 0; transform: translateY(64px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.animate-fade-up { animation: fade-up 0.9s cubic-bezier(0.22, 1, 0.36, 1) both; }
.animate-fade-down { animation: fade-down 0.7s cubic-bezier(0.22, 1, 0.36, 1) both; }
.animate-hero-rise { animation: hero-rise 1.1s cubic-bezier(0.22, 1, 0.36, 1) both; }
```

Staggered delays applied via inline `[animation-delay:Xms]` Tailwind arbitrary values. Respect `prefers-reduced-motion: reduce` by disabling all three animations.

---

RESPONSIVE BREAKPOINTS SUMMARY

| Element | Mobile (<640) | SM (640+) | MD (768+) | LG (1024+) | XL (1280+) |
|---|---|---|---|---|---|
| Headline | 40px / 44px@400 | 60px | -- | 70px | 80px |
| Nav links | Hidden (hamburger) | -- | Visible | -- | -- |
| Search bar width | full | -- | -- | -- | max-w-xl |
| Dashboard width | 92% | 84% | -- | 72% | -- |
| Dashboard bottom overlap | -mb-10 | -mb-20 | -- | -mb-32 | -- |

---

FILE STRUCTURE

```
src/
  App.tsx            -- renders <Hero />
  main.tsx           -- ReactDOM.createRoot
  index.css          -- Tailwind directives + custom keyframes
  components/
    Hero.tsx          -- main section with bg image, content, ScaledDashboard, grass overlay
    Navbar.tsx        -- top nav with mobile drawer
    Logo.tsx          -- SVG logo component
    DashboardMockup.tsx -- full browser-chrome dashboard mockup
```
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Pulse 3D"
template_id: "7855df67-3a7b-4960-bc88-65c35f0de69d"
section: "sites"
category_slug: "3d"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Pulse 3D

> **Секція:** `SITES` | **Категорія:** `3d`  
> **ID шаблону:** `7855df67-3a7b-4960-bc88-65c35f0de69d`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
3D Website

### 🖼 Прев'ю:
![Pulse 3D](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/d5c66feb-65be-4b0e-9ec5-e9e1cc4c92c6.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
## PROJECT OVERVIEW

Build a **single-screen, scroll-driven, custom-gesture landing page** called **"Inner Circle"**. There is **no native browser scrolling** — `document.body` and `html` both have `overflow: hidden`. A wheel/touch gesture controller drives a single `scrollProgress` numeric state from `0` to `3.5`. All animations (video scrubbing, text exits, rising panel, cylindrical drum) are derived from this single value.

### Stack
- **Vite + React 19 + TypeScript**
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **GSAP 3.15** for char-level split-text and parallax wiggle
- **lucide-react** for menu icons (`Menu`, `X`)
- `motion`, `@google/genai`, `express`, `dotenv` installed (the page itself only needs GSAP + Tailwind + React)

### Fonts (loaded in `src/index.css`)
```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Michroma&display=swap');
@import "tailwindcss";

@theme {
  --font-manrope: "Manrope", sans-serif;
  --font-michroma: "Michroma", sans-serif;
}
```
- Use `font-manrope` for body, paragraph drum text, header subtitle, nav.
- Use `font-michroma` for the giant hero title and tile labels.

### Global CSS (also in `index.css`)
```css
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #11010a; }
::-webkit-scrollbar-thumb { background: #ea1f63; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #ff5c93; }

html, body {
  background-color: #11010a;
  color: #ffffff;
  overflow-x: hidden;
  font-family: var(--font-manrope);
}

@keyframes marquee-scroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.marquee-container {
  display: flex; overflow: hidden; width: 100%; position: relative;
  mask-image: linear-gradient(to right, transparent, white 20%, white 80%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, white 20%, white 80%, transparent);
}
.marquee-track {
  display: flex; width: max-content; flex-wrap: nowrap;
  animation: marquee-scroll linear infinite;
  will-change: transform;
}
```

### Color palette
- Hero background magenta: `#FF005E`
- Second screen near-black/wine: `#11010a`
- Loader accents: `#ea1f63`, `pink-500` (`#ec4899`), `#ff5c93`
- Text: white (`#ffffff`) and `text-white/60` for low-emphasis drum copy
- **No purple/indigo anywhere.**

### Data files

`src/types.ts`:
```ts
export interface NavigationItem { id: string; label: string; scrollRatio: number; }
export interface Project { title: string; category: string; description: string; tags: string[]; }
export interface ExpertiseItem { title: string; percentage: number; description: string; }
```

`src/data.ts`:
```ts
export const NAVIGATION_ITEMS: NavigationItem[] = [
  { id: "projects",  label: "Projects",  scrollRatio: 0.25 },
  { id: "expertise", label: "Expertise", scrollRatio: 0.50 },
  { id: "about",     label: "About",     scrollRatio: 0.95 },
  { id: "contact",   label: "Manifesto", scrollRatio: 3.50 },
];
```
(Keep `PROJECTS_DATA` and `EXPERTISE_DATA` as defined — unused on this page but kept for parity.)

---

## ROOT LAYOUT (`src/App.tsx`)

### State
- `scrollProgress: number` (0 → 3.5)
- `lerpedScrollProgress: number` — smoothed copy of `scrollProgress`, updated each rAF tick with `currentLerp += (target - currentLerp) * 0.08`. Threshold `0.0001`.
- `activeSectionId: string` — derived via `updateActiveSection(progress)`:
  - `< 0.18` → "hero"
  - `0.18–0.45` → "projects"
  - `0.45–0.68` → "expertise"
  - `0.68–1.15` → "about"
  - else → "contact"

### Gesture controller (runs once on mount)
- Sets `document.body.style.overflow = "hidden"` and same on `documentElement`.
- `wheel` listener (passive: false, `preventDefault()`): `scaleFactor = 0.0006`, new value = `clamp(prev + deltaY * 0.0006, 0, 3.5)`.
- `touchstart` saves `lastTouchY`. `touchmove`: `deltaTouchY = lastTouchY - currentTouchY`, `scaleFactor = 0.0015`, clamp same range.
- If a programmatic nav animation is in flight, cancel it on any user input.

### Programmatic navigation (`handleNavigateToSection`)
- Duration: `1200ms`, easeInOutCubic:
  ```
  ease = p < 0.5 ? 4p³ : 1 - (-2p + 2)³ / 2
  ```
- Lerps `scrollProgress` from current to `item.scrollRatio` while calling `updateActiveSection` each frame.

### Derived values
```ts
const secondScreenProgress = clamp01((lerped - 1.15) / 0.50);
const easedRisingProgress  = 1 - Math.pow(1 - secondScreenProgress, 3);
const smoothBlurAmount     = Math.sin(secondScreenProgress * Math.PI / 2) * 64;
```

### Markup skeleton
```tsx
<main className="relative w-screen h-screen overflow-hidden bg-[#FF005E] text-white">
  <div className="relative w-full h-full overflow-hidden">

    {/* FIRST SCREEN — gets blurred as second screen rises */}
    <div
      className="absolute inset-0 w-full h-full z-10 transition-transform duration-[100ms] ease-out"
      style={{ filter: secondScreenProgress > 0 ? `blur(${smoothBlurAmount}px)` : "none" }}
    >
      <VideoScrubber scrollProgress={Math.min(1, lerpedScrollProgress)} />

      {/* Hero title strip pinned to bottom */}
      <div className="absolute bottom-[40px] left-[1%] right-[1%] w-[98%] pointer-events-none z-20 select-none flex justify-center items-center">
        <ScrollExitSplitText
          scrollProgress={Math.min(1, lerpedScrollProgress)}
          containerClassName="w-full text-[10.4vw] leading-none font-michroma font-normal uppercase text-white whitespace-nowrap text-center transition-all duration-300 will-change-transform"
          style={{ letterSpacing: "-0.07em" }}
        >
          INNER CIRCLE
        </ScrollExitSplitText>
      </div>

      <SoapTiles scrollProgress={lerpedScrollProgress} />
    </div>

    <Header activeSectionId={activeSectionId} onNavigate={handleNavigateToSection} />

    {/* SECOND SCREEN — rises from below, rounded top */}
    <div
      className="absolute bottom-0 left-0 w-full h-full bg-[#11010a] rounded-t-[48px] overflow-hidden z-40"
      style={{
        transform: `translateY(${(1 - easedRisingProgress) * 100}%)`,
        visibility: secondScreenProgress > 0 ? "visible" : "hidden",
        willChange: "transform",
      }}
    >
      <div className="absolute top-5 left-1/2 -translate-x-1/2 w-16 h-[5px] bg-white rounded-full z-50 pointer-events-none" />
      <SecondVideoScrubber scrollProgress={lerpedScrollProgress} />
      <CylindricalTextDrum scrollProgress={lerpedScrollProgress} />

      <div className="absolute bottom-8 sm:bottom-12 md:bottom-16 left-0 w-full sm:w-[65%] md:w-[60%] pl-6 sm:pl-12 md:pl-20 pr-6 sm:pr-12 md:pr-16 z-50 pointer-events-auto">
        <div className="w-full border-t border-white/[0.08] pt-6">
          <Marquee gap="80px" speed={25} fade>
            <GoogleWordmark size={100} />
            <GithubWordmark size={100} />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/voiceflow-logo-svg-150px.svg" alt="Voiceflow" className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/zendesk-logo-svg-150px.svg"   alt="Zendesk"   className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/pendo-logo-svg-150px.svg"     alt="Pendo"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/glide-logo-svg-150px.svg"     alt="Glide"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/canva-logo-svg-150px.svg"     alt="Canva"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
          </Marquee>
        </div>
      </div>
    </div>
  </div>
</main>
```

---

## SECTION 1 — HERO (First Screen)

### 1a. Background video — `VideoScrubber`
- **Video URL (exact):**
  `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781342006/202606021731-e_hqa6sn.mp4`
- `<video>` is `playsInline muted preload="auto"`, `object-cover`, full size, `pointer-events-none`.
- Wrapped in a `style={{ scale: "1.05" }}` div with `will-change-transform`. Container background is `bg-[#FF005E]`.
- **Scrub algorithm:** On every rAF tick:
  - `targetTime = clamp(scrollProgress * duration, 0, duration)` (fallback duration `4.2`).
  - `current += (target - current) * 0.15` (lerp).
  - Seek only when `!video.seeking && Math.abs(video.currentTime - current) > 0.01` → `video.currentTime = current`.
- **GSAP mouse parallax** on the container: on `mousemove`, compute `mx = e.clientX/innerWidth - 0.5`, `my = ...`. Animate `x: -mx*40, y: -my*40, duration: 1.2, ease: "power2.out", overwrite: "auto"`.
- **Loader overlay** (while `!isLoaded`): full-bleed `bg-[#FF005Ef4]`, centered: a 64×64 wrapper with `animate-ping` pink-500/20 ring + a 40×40 spinner ring (`border-4 border-[#ea1f63]/20 border-t-[#ea1f63] animate-spin`), label "LOADING SCROLL STREAM..." in `font-manrope font-semibold text-[12px] uppercase tracking-[0.25em] text-pink-500 drop-shadow-[0_0_8px_rgba(234,31,99,0.4)]`.

### 1b. Hero title — `ScrollExitSplitText`
- Text: `INNER CIRCLE`
- Class on outer container (from App): `text-[10.4vw] leading-none font-michroma font-normal uppercase text-white whitespace-nowrap text-center`, `letterSpacing: -0.07em`.
- Positioned: `absolute bottom-[40px] left-[1%] right-[1%] w-[98%]`, `z-20`, `pointer-events-none`.
- **Split-text mechanic:** split into lines → words → characters. Each char is a `span.char inline-block will-change-transform`. Words separated by a literal `&nbsp;` span.
- **GSAP timeline** (paused, controlled by scroll):
  ```ts
  tl.fromTo(chars,
    { opacity: 1, yPercent: 0, y: 0, scaleY: 1, scaleX: 1, transformOrigin: "50% 0%" },
    { opacity: 0, yPercent: 300, y: "25vh", scaleY: 1.2, scaleX: 0.9, stagger: 0.03, ease: "power2.inOut" }
  );
  ```
- On every `scrollProgress` change: `gsap.to(timeline, { progress: scrollProgress, duration: 0.6, ease: "power1.out", overwrite: "auto" })`. This produces a smooth lag/scrub.

### 1c. Reveal tiles — `SoapTiles`
- Three white pill-cards stacked vertically on the left:
  1. `Private Discord & Networking` — baseXOffset `120`, delay `0ms`
  2. `Weekly Market Alpha Drops` — baseXOffset `180`, delay `100ms`
  3. `Exclusive Web3 Tooling Access` — baseXOffset `240`, delay `200ms`
- Container: `absolute left-4 right-4 md:left-[64px] top-[38%] md:top-1/2 -translate-y-1/2 flex flex-col gap-2 md:gap-[10px] z-40 pointer-events-auto transition-all duration-[800ms] ease-out`. Hidden state: `opacity-0 -translate-x-6 md:-translate-x-12 pointer-events-none`. Visible when `scrollProgress > 0.75`.
- Each tile class: `group relative h-[52px] sm:h-[72px] md:h-[138px] text-black bg-white rounded-xl sm:rounded-2xl md:rounded-[34px] flex items-center justify-center px-4 sm:px-8 md:px-14 w-full md:w-auto md:self-start cursor-pointer origin-left transition-all duration-[400ms] cubic-bezier(0.16, 1, 0.3, 1) whitespace-nowrap`.
- **Entry animation:** `easeProgress = clamp01((scrollProgress - 0.75) / 0.22)`. Each tile:
  - `translateX = (easeProgress - 1) * responsiveOffset` (on mobile, offset is `× 0.25`)
  - `opacity = easeProgress`
  - `filter = blur(${(1 - easeProgress) * 12}px)`
- **Hover behavior (desktop only):** hovered tile scales `1.2`. Non-hovered tiles shift vertically by `±13.8px` (`baseHeight * 0.1`, with `baseHeight` 138/52) — up if above hovered, down if below. On mobile, hover scale stays `1.0`.
- Label inside each tile: `font-michroma font-medium text-[11px] sm:text-[14px] md:text-[23px] leading-[16px] sm:leading-[22px] md:leading-[34px] tracking-tight`, `letter-spacing: -0.03em`.

### 1d. Header — `Header`
- Container: `absolute top-4 left-4 right-4 sm:top-8 sm:left-8 sm:right-8 md:top-[64px] md:left-[64px] md:right-[64px] flex items-center justify-between z-40`.
- **Logo group (left):** clicking navigates to scrollRatio `0`. Contains:
  - `Logo` — 48×48 SVG with this exact path: a stylized "M" mark (`viewBox="0 0 80 80"`, single `<path>`, see code snippet below).
  - Subtitle (hidden < sm): three lines `Full Workflow Automation.` / `We Manage Everything. You` / `Unwind.` in `font-manrope font-normal tracking-wide text-[12px] leading-[16px] text-white`.
- **Desktop nav (≥ md):** the 4 NAVIGATION_ITEMS as buttons: `font-manrope font-medium text-[12px] leading-[16px] tracking-wider text-white px-4 py-2 rounded-full hover:bg-white hover:text-black transition-all duration-300`.
- **Mobile burger:** circular `w-10 h-10 rounded-full border border-white/10 bg-white/5`. Toggles a full-screen overlay `fixed inset-0 bg-[#11010a]/98 backdrop-blur-xl z-30` with each item in `font-michroma text-[16px] uppercase tracking-widest py-4 px-6 border-b border-white/5`; active item: `text-[#FF005E] font-semibold`.

Logo path (exact):
```
M40 80C17.9086 80 0 62.0914 0 40V0C15.0436 0 28.1476 8.30466 34.9776 20.5796C25.6529 22.8063 18.7198 31.1937 18.7198 41.2004V42.0962C18.7198 53.3099 27.8104 62.4004 39.0242 62.4004H39.9199L39.9197 41.2004C39.9197 52.9088 49.4113 62.4004 61.1198 62.4004L61.1198 41.2004C61.1198 29.5187 51.6717 20.0437 40 20.0005L40 0H41.6902C62.8481 0 80 17.1519 80 38.3099V40C80 62.0914 62.0914 80 40 80Z
```

---

## SECTION 2 — SECOND SCREEN (Rising Panel)

### Reveal mechanics
- Triggered when `lerpedScrollProgress > 1.15`. Becomes fully on-screen at `1.65`.
- Panel: `absolute bottom-0 left-0 w-full h-full bg-[#11010a] rounded-t-[48px] overflow-hidden z-40`.
- `transform: translateY((1 - easedRisingProgress) * 100%)` where `easedRisingProgress = 1 - (1 - secondScreenProgress)^3`.
- `visibility: hidden` when `secondScreenProgress === 0`.
- While rising, the **first screen blurs** up to `64px` via `Math.sin(p * π/2) * 64`.
- **iOS grab-handle pill:** `absolute top-5 left-1/2 -translate-x-1/2 w-16 h-[5px] bg-white rounded-full z-50 pointer-events-none`.

### 2a. Background video — `SecondVideoScrubber`
- **Video URL (exact):**
  `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781342027/2026060218225-v_kcy5rl.mp4`
- Same component skeleton as `VideoScrubber` but with these differences:
  - Background color of the loader bg: `bg-[#11010af4]`.
  - `DRUM_START = 1.45`, `DRUM_END = 3.50`.
  - `drumProgress = clamp01((scrollProgress - 1.45) / (3.50 - 1.45))`, `target = drumProgress * duration`.
  - Same lerp `0.15`, same `!video.seeking && diff > 0.01` guard.
  - Same GSAP mouse parallax `x/y: ±40px, duration 1.2, ease "power2.out"`.
  - Loader label: `LOADING DRUM STREAM...` with `border-pink-500/20 border-t-pink-500`.

### 2b. Cylindrical text drum — `CylindricalTextDrum`
- Container: `absolute inset-y-0 left-0 w-full sm:w-[65%] md:w-[60%] z-30 flex flex-col items-start justify-center pointer-events-none select-none text-left pl-6 sm:pl-12 md:pl-20 py-16`, with `perspective: 1000px; perspectiveOrigin: 25% 50%`.
- Inner: `relative w-full h-[85vh] flex flex-col justify-center items-start overflow-visible` with `transformStyle: "preserve-3d"`.
- **Geometry:** `R = 380`, `lineHeight = 32`.
- `targetIndex = clamp01((scrollProgress - 1.45) / 2.05) * (LINES.length - 1)`.
- For each line `idx`:
  - `indexDiff = idx - targetIndex`
  - `translateY = indexDiff * 32`
  - `angleRad = translateY / 380`, `angleDeg = angleRad * 180/π`
  - `translateZ = cos(angleRad) * 380 - 380`
  - `baseScale = 0.78 + cos(angleRad) * 0.22`
  - `opacity = max(0, (cos(angleRad) - 0.2) / 0.8)`
  - `depthBlur = min(8, max(0, (|indexDiff| - 1.5) * 0.75))`
  - Apply `transform: translateY(${ty}px) translateZ(${tz}px) rotateX(${-angleDeg * 0.8}deg) scale(${baseScale})`, `transformOrigin: "left center"`, plus blur when > 0.1.
- Each line `<p>`: `font-manrope text-[18px] sm:text-[24px] md:text-[28px] lg:text-[32px] font-semibold leading-[0.90] tracking-tight whitespace-nowrap`, `letter-spacing: -0.035em`.
- Text segments: if `highlight === true` use `text-white font-bold opacity-100`; else `text-white/60`. Empty `""` line renders a sized spacer at `opacity * 0.3`.
- **Use the exact `LINES` array below — 32 entries (one empty string at index 15):**

```
1.  Welcome to the [ultimate convergence]
2.  of [digital rebels], [underground creators],
3.  and [top-tier product builders] who
4.  refuse to follow [guidelines].
5.  This is where [high-end design principles]
6.  meet [pure technical execution],
7.  without the [corporate bureaucracy] and
8.  meaningless [standard aesthetics].
9.  We [gather in the shadows] to build
10. the [next generation] of [scalable interfaces],
11. [automated workflows], and [decentralized assets]
12. that move the [cultural needle forward].
13. Experience [zero-bullshit networking],
14. weekly [alpha allocations], and [unreleased]
15. [toolkits] to shape the [internet's landscape].
16. (empty line)
17. This is [not another social club]
18. for casual enthusiasts or [template consumers].
19. This is a [highly selective environment]
20. engineered for [hyper-productive creators],
21. [UI/UX visionaries], and [AI prompt architects]
22. who operate at the [absolute limits]
23. of [digital product creation].
24. Our [framework is simple]:
25. [eliminate intermediate noise],
26. [automate the execution layer],
27. and [deploy elite digital products]
28. while others are still [scheduling meetings].
29. We loop through [complex design systems],
30. [break conventional grids], and
31. [execute fluid interactions] that
32. [redefine digital environments].
```
(Words in `[brackets]` are `highlight: true`.)

### 2c. Logo marquee — `Marquee`
- Position: `absolute bottom-8 sm:bottom-12 md:bottom-16 left-0 w-full sm:w-[65%] md:w-[60%] pl-6 sm:pl-12 md:pl-20 pr-6 sm:pr-12 md:pr-16 z-50`.
- Inside a wrapper `border-t border-white/[0.08] pt-6`.
- `<Marquee gap="80px" speed={25} fade>` produces two duplicated tracks animated infinitely with the keyframe `marquee-scroll` (0% → -50%) over `25s` linear infinite, masked with a left/right transparent fade at 15%/85%.
- Children in order: `<GoogleWordmark size={100} />`, `<GithubWordmark size={100} />`, then `<img>` tags for these exact URLs, each styled `h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity`, `referrerPolicy="no-referrer"`:
  - `https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/voiceflow-logo-svg-150px.svg`
  - `.../zendesk-logo-svg-150px.svg`
  - `.../pendo-logo-svg-150px.svg`
  - `.../glide-logo-svg-150px.svg`
  - `.../canva-logo-svg-150px.svg`
- `GoogleWordmark` and `GithubWordmark` are inline `<svg>` wordmarks at `viewBox="0 0 115 30"` / `0 0 110 30` — see file for exact text/paths.

---

## INTERACTIONS — Summary table

| Trigger | Effect |
|---|---|
| Mouse wheel | `scrollProgress += deltaY * 0.0006`, clamp `[0, 3.5]` |
| Touch drag | `scrollProgress += (lastY - currentY) * 0.0015` |
| Nav click | 1200ms easeInOutCubic lerp to target ratio |
| `scrollProgress` 0 → 1 | Hero video scrubs forward, "INNER CIRCLE" chars fall (300% y, 25vh) with 0.03 stagger |
| `scrollProgress` > 0.75 | Soap tiles fade/slide in (over a 0.22 range), with 12px → 0 blur |
| Hover tile (desktop) | Hovered tile scales 1.2, neighbors shift ±13.8px |
| `scrollProgress` > 1.15 | Second screen rises (ease-out cubic), first screen blurs to 64px |
| `scrollProgress` 1.45 → 3.50 | Second video scrubs; cylindrical drum rotates; line at center is at scale 1.0/opacity 1.0 |
| Mouse move (anywhere) | Both videos parallax-translate ±40px via GSAP `power2.out`, 1.2s |

---

## DATA PERSISTENCE

Supabase is available. This page is presentational and does not persist user state, so no database tables are required for the recreation. If extending with capture forms, waitlist sign-ups, or analytics events, create a Supabase table with RLS enabled and `auth.uid()`-based policies (one INSERT policy for `authenticated`, restrictive SELECT).

---

## FILE STRUCTURE

```
src/
  App.tsx
  main.tsx
  index.css
  types.ts
  data.ts
  components/
    Header.tsx
    Logo.tsx
    Logos.tsx                 (GoogleWordmark, GithubWordmark exported)
    Marquee.tsx
    VideoScrubber.tsx
    SecondVideoScrubber.tsx
    ScrollExitSplitText.tsx
    SoapTiles.tsx
    CylindricalTextDrum.tsx
```

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "3D Portfolio"
template_id: "d53960dc-c8f4-481a-bd7c-7e9f11d9ecaa"
section: "sites"
category_slug: "portfolio"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 3D Portfolio

> **Секція:** `SITES` | **Категорія:** `portfolio`  
> **ID шаблону:** `d53960dc-c8f4-481a-bd7c-7e9f11d9ecaa`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Portfolio

### 🖼 Прев'ю:
![3D Portfolio](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5445fe81-adf7-437b-9238-5328a3de900c.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
## PROJECT OVERVIEW

Build a **single-screen, scroll-driven, custom-gesture landing page** called **"Inner Circle"**. There is **no native browser scrolling** — `document.body` and `html` both have `overflow: hidden`. A wheel/touch gesture controller drives a single `scrollProgress` numeric state from `0` to `3.5`. All animations (video scrubbing, text exits, rising panel, cylindrical drum) are derived from this single value.

### Stack
- **Vite + React 19 + TypeScript**
- **Tailwind CSS v4** (via `@tailwindcss/vite`)
- **GSAP 3.15** for char-level split-text and parallax wiggle
- **lucide-react** for menu icons (`Menu`, `X`)
- `motion`, `@google/genai`, `express`, `dotenv` installed (the page itself only needs GSAP + Tailwind + React)

### Fonts (loaded in `src/index.css`)
```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Michroma&display=swap');
@import "tailwindcss";

@theme {
  --font-manrope: "Manrope", sans-serif;
  --font-michroma: "Michroma", sans-serif;
}
```
- Use `font-manrope` for body, paragraph drum text, header subtitle, nav.
- Use `font-michroma` for the giant hero title and tile labels.

### Global CSS (also in `index.css`)
```css
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #11010a; }
::-webkit-scrollbar-thumb { background: #ea1f63; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #ff5c93; }

html, body {
  background-color: #11010a;
  color: #ffffff;
  overflow-x: hidden;
  font-family: var(--font-manrope);
}

@keyframes marquee-scroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.marquee-container {
  display: flex; overflow: hidden; width: 100%; position: relative;
  mask-image: linear-gradient(to right, transparent, white 20%, white 80%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, white 20%, white 80%, transparent);
}
.marquee-track {
  display: flex; width: max-content; flex-wrap: nowrap;
  animation: marquee-scroll linear infinite;
  will-change: transform;
}
```

### Color palette
- Hero background magenta: `#FF005E`
- Second screen near-black/wine: `#11010a`
- Loader accents: `#ea1f63`, `pink-500` (`#ec4899`), `#ff5c93`
- Text: white (`#ffffff`) and `text-white/60` for low-emphasis drum copy
- **No purple/indigo anywhere.**

### Data files

`src/types.ts`:
```ts
export interface NavigationItem { id: string; label: string; scrollRatio: number; }
export interface Project { title: string; category: string; description: string; tags: string[]; }
export interface ExpertiseItem { title: string; percentage: number; description: string; }
```

`src/data.ts`:
```ts
export const NAVIGATION_ITEMS: NavigationItem[] = [
  { id: "projects",  label: "Projects",  scrollRatio: 0.25 },
  { id: "expertise", label: "Expertise", scrollRatio: 0.50 },
  { id: "about",     label: "About",     scrollRatio: 0.95 },
  { id: "contact",   label: "Manifesto", scrollRatio: 3.50 },
];
```
(Keep `PROJECTS_DATA` and `EXPERTISE_DATA` as defined — unused on this page but kept for parity.)

---

## ROOT LAYOUT (`src/App.tsx`)

### State
- `scrollProgress: number` (0 → 3.5)
- `lerpedScrollProgress: number` — smoothed copy of `scrollProgress`, updated each rAF tick with `currentLerp += (target - currentLerp) * 0.08`. Threshold `0.0001`.
- `activeSectionId: string` — derived via `updateActiveSection(progress)`:
  - `< 0.18` → "hero"
  - `0.18–0.45` → "projects"
  - `0.45–0.68` → "expertise"
  - `0.68–1.15` → "about"
  - else → "contact"

### Gesture controller (runs once on mount)
- Sets `document.body.style.overflow = "hidden"` and same on `documentElement`.
- `wheel` listener (passive: false, `preventDefault()`): `scaleFactor = 0.0006`, new value = `clamp(prev + deltaY * 0.0006, 0, 3.5)`.
- `touchstart` saves `lastTouchY`. `touchmove`: `deltaTouchY = lastTouchY - currentTouchY`, `scaleFactor = 0.0015`, clamp same range.
- If a programmatic nav animation is in flight, cancel it on any user input.

### Programmatic navigation (`handleNavigateToSection`)
- Duration: `1200ms`, easeInOutCubic:
  ```
  ease = p < 0.5 ? 4p³ : 1 - (-2p + 2)³ / 2
  ```
- Lerps `scrollProgress` from current to `item.scrollRatio` while calling `updateActiveSection` each frame.

### Derived values
```ts
const secondScreenProgress = clamp01((lerped - 1.15) / 0.50);
const easedRisingProgress  = 1 - Math.pow(1 - secondScreenProgress, 3);
const smoothBlurAmount     = Math.sin(secondScreenProgress * Math.PI / 2) * 64;
```

### Markup skeleton
```tsx
<main className="relative w-screen h-screen overflow-hidden bg-[#FF005E] text-white">
  <div className="relative w-full h-full overflow-hidden">

    {/* FIRST SCREEN — gets blurred as second screen rises */}
    <div
      className="absolute inset-0 w-full h-full z-10 transition-transform duration-[100ms] ease-out"
      style={{ filter: secondScreenProgress > 0 ? `blur(${smoothBlurAmount}px)` : "none" }}
    >
      <VideoScrubber scrollProgress={Math.min(1, lerpedScrollProgress)} />

      {/* Hero title strip pinned to bottom */}
      <div className="absolute bottom-[40px] left-[1%] right-[1%] w-[98%] pointer-events-none z-20 select-none flex justify-center items-center">
        <ScrollExitSplitText
          scrollProgress={Math.min(1, lerpedScrollProgress)}
          containerClassName="w-full text-[10.4vw] leading-none font-michroma font-normal uppercase text-white whitespace-nowrap text-center transition-all duration-300 will-change-transform"
          style={{ letterSpacing: "-0.07em" }}
        >
          INNER CIRCLE
        </ScrollExitSplitText>
      </div>

      <SoapTiles scrollProgress={lerpedScrollProgress} />
    </div>

    <Header activeSectionId={activeSectionId} onNavigate={handleNavigateToSection} />

    {/* SECOND SCREEN — rises from below, rounded top */}
    <div
      className="absolute bottom-0 left-0 w-full h-full bg-[#11010a] rounded-t-[48px] overflow-hidden z-40"
      style={{
        transform: `translateY(${(1 - easedRisingProgress) * 100}%)`,
        visibility: secondScreenProgress > 0 ? "visible" : "hidden",
        willChange: "transform",
      }}
    >
      <div className="absolute top-5 left-1/2 -translate-x-1/2 w-16 h-[5px] bg-white rounded-full z-50 pointer-events-none" />
      <SecondVideoScrubber scrollProgress={lerpedScrollProgress} />
      <CylindricalTextDrum scrollProgress={lerpedScrollProgress} />

      <div className="absolute bottom-8 sm:bottom-12 md:bottom-16 left-0 w-full sm:w-[65%] md:w-[60%] pl-6 sm:pl-12 md:pl-20 pr-6 sm:pr-12 md:pr-16 z-50 pointer-events-auto">
        <div className="w-full border-t border-white/[0.08] pt-6">
          <Marquee gap="80px" speed={25} fade>
            <GoogleWordmark size={100} />
            <GithubWordmark size={100} />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/voiceflow-logo-svg-150px.svg" alt="Voiceflow" className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/zendesk-logo-svg-150px.svg"   alt="Zendesk"   className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/pendo-logo-svg-150px.svg"     alt="Pendo"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/glide-logo-svg-150px.svg"     alt="Glide"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
            <img src="https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/canva-logo-svg-150px.svg"     alt="Canva"     className="h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity" referrerPolicy="no-referrer" />
          </Marquee>
        </div>
      </div>
    </div>
  </div>
</main>
```

---

## SECTION 1 — HERO (First Screen)

### 1a. Background video — `VideoScrubber`
- **Video URL (exact):**
  `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781342006/202606021731-e_hqa6sn.mp4`
- `<video>` is `playsInline muted preload="auto"`, `object-cover`, full size, `pointer-events-none`.
- Wrapped in a `style={{ scale: "1.05" }}` div with `will-change-transform`. Container background is `bg-[#FF005E]`.
- **Scrub algorithm:** On every rAF tick:
  - `targetTime = clamp(scrollProgress * duration, 0, duration)` (fallback duration `4.2`).
  - `current += (target - current) * 0.15` (lerp).
  - Seek only when `!video.seeking && Math.abs(video.currentTime - current) > 0.01` → `video.currentTime = current`.
- **GSAP mouse parallax** on the container: on `mousemove`, compute `mx = e.clientX/innerWidth - 0.5`, `my = ...`. Animate `x: -mx*40, y: -my*40, duration: 1.2, ease: "power2.out", overwrite: "auto"`.
- **Loader overlay** (while `!isLoaded`): full-bleed `bg-[#FF005Ef4]`, centered: a 64×64 wrapper with `animate-ping` pink-500/20 ring + a 40×40 spinner ring (`border-4 border-[#ea1f63]/20 border-t-[#ea1f63] animate-spin`), label "LOADING SCROLL STREAM..." in `font-manrope font-semibold text-[12px] uppercase tracking-[0.25em] text-pink-500 drop-shadow-[0_0_8px_rgba(234,31,99,0.4)]`.

### 1b. Hero title — `ScrollExitSplitText`
- Text: `INNER CIRCLE`
- Class on outer container (from App): `text-[10.4vw] leading-none font-michroma font-normal uppercase text-white whitespace-nowrap text-center`, `letterSpacing: -0.07em`.
- Positioned: `absolute bottom-[40px] left-[1%] right-[1%] w-[98%]`, `z-20`, `pointer-events-none`.
- **Split-text mechanic:** split into lines → words → characters. Each char is a `span.char inline-block will-change-transform`. Words separated by a literal `&nbsp;` span.
- **GSAP timeline** (paused, controlled by scroll):
  ```ts
  tl.fromTo(chars,
    { opacity: 1, yPercent: 0, y: 0, scaleY: 1, scaleX: 1, transformOrigin: "50% 0%" },
    { opacity: 0, yPercent: 300, y: "25vh", scaleY: 1.2, scaleX: 0.9, stagger: 0.03, ease: "power2.inOut" }
  );
  ```
- On every `scrollProgress` change: `gsap.to(timeline, { progress: scrollProgress, duration: 0.6, ease: "power1.out", overwrite: "auto" })`. This produces a smooth lag/scrub.

### 1c. Reveal tiles — `SoapTiles`
- Three white pill-cards stacked vertically on the left:
  1. `Private Discord & Networking` — baseXOffset `120`, delay `0ms`
  2. `Weekly Market Alpha Drops` — baseXOffset `180`, delay `100ms`
  3. `Exclusive Web3 Tooling Access` — baseXOffset `240`, delay `200ms`
- Container: `absolute left-4 right-4 md:left-[64px] top-[38%] md:top-1/2 -translate-y-1/2 flex flex-col gap-2 md:gap-[10px] z-40 pointer-events-auto transition-all duration-[800ms] ease-out`. Hidden state: `opacity-0 -translate-x-6 md:-translate-x-12 pointer-events-none`. Visible when `scrollProgress > 0.75`.
- Each tile class: `group relative h-[52px] sm:h-[72px] md:h-[138px] text-black bg-white rounded-xl sm:rounded-2xl md:rounded-[34px] flex items-center justify-center px-4 sm:px-8 md:px-14 w-full md:w-auto md:self-start cursor-pointer origin-left transition-all duration-[400ms] cubic-bezier(0.16, 1, 0.3, 1) whitespace-nowrap`.
- **Entry animation:** `easeProgress = clamp01((scrollProgress - 0.75) / 0.22)`. Each tile:
  - `translateX = (easeProgress - 1) * responsiveOffset` (on mobile, offset is `× 0.25`)
  - `opacity = easeProgress`
  - `filter = blur(${(1 - easeProgress) * 12}px)`
- **Hover behavior (desktop only):** hovered tile scales `1.2`. Non-hovered tiles shift vertically by `±13.8px` (`baseHeight * 0.1`, with `baseHeight` 138/52) — up if above hovered, down if below. On mobile, hover scale stays `1.0`.
- Label inside each tile: `font-michroma font-medium text-[11px] sm:text-[14px] md:text-[23px] leading-[16px] sm:leading-[22px] md:leading-[34px] tracking-tight`, `letter-spacing: -0.03em`.

### 1d. Header — `Header`
- Container: `absolute top-4 left-4 right-4 sm:top-8 sm:left-8 sm:right-8 md:top-[64px] md:left-[64px] md:right-[64px] flex items-center justify-between z-40`.
- **Logo group (left):** clicking navigates to scrollRatio `0`. Contains:
  - `Logo` — 48×48 SVG with this exact path: a stylized "M" mark (`viewBox="0 0 80 80"`, single `<path>`, see code snippet below).
  - Subtitle (hidden < sm): three lines `Full Workflow Automation.` / `We Manage Everything. You` / `Unwind.` in `font-manrope font-normal tracking-wide text-[12px] leading-[16px] text-white`.
- **Desktop nav (≥ md):** the 4 NAVIGATION_ITEMS as buttons: `font-manrope font-medium text-[12px] leading-[16px] tracking-wider text-white px-4 py-2 rounded-full hover:bg-white hover:text-black transition-all duration-300`.
- **Mobile burger:** circular `w-10 h-10 rounded-full border border-white/10 bg-white/5`. Toggles a full-screen overlay `fixed inset-0 bg-[#11010a]/98 backdrop-blur-xl z-30` with each item in `font-michroma text-[16px] uppercase tracking-widest py-4 px-6 border-b border-white/5`; active item: `text-[#FF005E] font-semibold`.

Logo path (exact):
```
M40 80C17.9086 80 0 62.0914 0 40V0C15.0436 0 28.1476 8.30466 34.9776 20.5796C25.6529 22.8063 18.7198 31.1937 18.7198 41.2004V42.0962C18.7198 53.3099 27.8104 62.4004 39.0242 62.4004H39.9199L39.9197 41.2004C39.9197 52.9088 49.4113 62.4004 61.1198 62.4004L61.1198 41.2004C61.1198 29.5187 51.6717 20.0437 40 20.0005L40 0H41.6902C62.8481 0 80 17.1519 80 38.3099V40C80 62.0914 62.0914 80 40 80Z
```

---

## SECTION 2 — SECOND SCREEN (Rising Panel)

### Reveal mechanics
- Triggered when `lerpedScrollProgress > 1.15`. Becomes fully on-screen at `1.65`.
- Panel: `absolute bottom-0 left-0 w-full h-full bg-[#11010a] rounded-t-[48px] overflow-hidden z-40`.
- `transform: translateY((1 - easedRisingProgress) * 100%)` where `easedRisingProgress = 1 - (1 - secondScreenProgress)^3`.
- `visibility: hidden` when `secondScreenProgress === 0`.
- While rising, the **first screen blurs** up to `64px` via `Math.sin(p * π/2) * 64`.
- **iOS grab-handle pill:** `absolute top-5 left-1/2 -translate-x-1/2 w-16 h-[5px] bg-white rounded-full z-50 pointer-events-none`.

### 2a. Background video — `SecondVideoScrubber`
- **Video URL (exact):**
  `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781342027/2026060218225-v_kcy5rl.mp4`
- Same component skeleton as `VideoScrubber` but with these differences:
  - Background color of the loader bg: `bg-[#11010af4]`.
  - `DRUM_START = 1.45`, `DRUM_END = 3.50`.
  - `drumProgress = clamp01((scrollProgress - 1.45) / (3.50 - 1.45))`, `target = drumProgress * duration`.
  - Same lerp `0.15`, same `!video.seeking && diff > 0.01` guard.
  - Same GSAP mouse parallax `x/y: ±40px, duration 1.2, ease "power2.out"`.
  - Loader label: `LOADING DRUM STREAM...` with `border-pink-500/20 border-t-pink-500`.

### 2b. Cylindrical text drum — `CylindricalTextDrum`
- Container: `absolute inset-y-0 left-0 w-full sm:w-[65%] md:w-[60%] z-30 flex flex-col items-start justify-center pointer-events-none select-none text-left pl-6 sm:pl-12 md:pl-20 py-16`, with `perspective: 1000px; perspectiveOrigin: 25% 50%`.
- Inner: `relative w-full h-[85vh] flex flex-col justify-center items-start overflow-visible` with `transformStyle: "preserve-3d"`.
- **Geometry:** `R = 380`, `lineHeight = 32`.
- `targetIndex = clamp01((scrollProgress - 1.45) / 2.05) * (LINES.length - 1)`.
- For each line `idx`:
  - `indexDiff = idx - targetIndex`
  - `translateY = indexDiff * 32`
  - `angleRad = translateY / 380`, `angleDeg = angleRad * 180/π`
  - `translateZ = cos(angleRad) * 380 - 380`
  - `baseScale = 0.78 + cos(angleRad) * 0.22`
  - `opacity = max(0, (cos(angleRad) - 0.2) / 0.8)`
  - `depthBlur = min(8, max(0, (|indexDiff| - 1.5) * 0.75))`
  - Apply `transform: translateY(${ty}px) translateZ(${tz}px) rotateX(${-angleDeg * 0.8}deg) scale(${baseScale})`, `transformOrigin: "left center"`, plus blur when > 0.1.
- Each line `<p>`: `font-manrope text-[18px] sm:text-[24px] md:text-[28px] lg:text-[32px] font-semibold leading-[0.90] tracking-tight whitespace-nowrap`, `letter-spacing: -0.035em`.
- Text segments: if `highlight === true` use `text-white font-bold opacity-100`; else `text-white/60`. Empty `""` line renders a sized spacer at `opacity * 0.3`.
- **Use the exact `LINES` array below — 32 entries (one empty string at index 15):**

```
1.  Welcome to the [ultimate convergence]
2.  of [digital rebels], [underground creators],
3.  and [top-tier product builders] who
4.  refuse to follow [guidelines].
5.  This is where [high-end design principles]
6.  meet [pure technical execution],
7.  without the [corporate bureaucracy] and
8.  meaningless [standard aesthetics].
9.  We [gather in the shadows] to build
10. the [next generation] of [scalable interfaces],
11. [automated workflows], and [decentralized assets]
12. that move the [cultural needle forward].
13. Experience [zero-bullshit networking],
14. weekly [alpha allocations], and [unreleased]
15. [toolkits] to shape the [internet's landscape].
16. (empty line)
17. This is [not another social club]
18. for casual enthusiasts or [template consumers].
19. This is a [highly selective environment]
20. engineered for [hyper-productive creators],
21. [UI/UX visionaries], and [AI prompt architects]
22. who operate at the [absolute limits]
23. of [digital product creation].
24. Our [framework is simple]:
25. [eliminate intermediate noise],
26. [automate the execution layer],
27. and [deploy elite digital products]
28. while others are still [scheduling meetings].
29. We loop through [complex design systems],
30. [break conventional grids], and
31. [execute fluid interactions] that
32. [redefine digital environments].
```
(Words in `[brackets]` are `highlight: true`.)

### 2c. Logo marquee — `Marquee`
- Position: `absolute bottom-8 sm:bottom-12 md:bottom-16 left-0 w-full sm:w-[65%] md:w-[60%] pl-6 sm:pl-12 md:pl-20 pr-6 sm:pr-12 md:pr-16 z-50`.
- Inside a wrapper `border-t border-white/[0.08] pt-6`.
- `<Marquee gap="80px" speed={25} fade>` produces two duplicated tracks animated infinitely with the keyframe `marquee-scroll` (0% → -50%) over `25s` linear infinite, masked with a left/right transparent fade at 15%/85%.
- Children in order: `<GoogleWordmark size={100} />`, `<GithubWordmark size={100} />`, then `<img>` tags for these exact URLs, each styled `h-6 w-auto object-contain brightness-0 invert opacity-80 hover:opacity-100 transition-opacity`, `referrerPolicy="no-referrer"`:
  - `https://raw.githubusercontent.com/dsMagnatov/Acreage-landing-assets/refs/heads/main/voiceflow-logo-svg-150px.svg`
  - `.../zendesk-logo-svg-150px.svg`
  - `.../pendo-logo-svg-150px.svg`
  - `.../glide-logo-svg-150px.svg`
  - `.../canva-logo-svg-150px.svg`
- `GoogleWordmark` and `GithubWordmark` are inline `<svg>` wordmarks at `viewBox="0 0 115 30"` / `0 0 110 30` — see file for exact text/paths.

---

## INTERACTIONS — Summary table

| Trigger | Effect |
|---|---|
| Mouse wheel | `scrollProgress += deltaY * 0.0006`, clamp `[0, 3.5]` |
| Touch drag | `scrollProgress += (lastY - currentY) * 0.0015` |
| Nav click | 1200ms easeInOutCubic lerp to target ratio |
| `scrollProgress` 0 → 1 | Hero video scrubs forward, "INNER CIRCLE" chars fall (300% y, 25vh) with 0.03 stagger |
| `scrollProgress` > 0.75 | Soap tiles fade/slide in (over a 0.22 range), with 12px → 0 blur |
| Hover tile (desktop) | Hovered tile scales 1.2, neighbors shift ±13.8px |
| `scrollProgress` > 1.15 | Second screen rises (ease-out cubic), first screen blurs to 64px |
| `scrollProgress` 1.45 → 3.50 | Second video scrubs; cylindrical drum rotates; line at center is at scale 1.0/opacity 1.0 |
| Mouse move (anywhere) | Both videos parallax-translate ±40px via GSAP `power2.out`, 1.2s |

---

## DATA PERSISTENCE

Supabase is available. This page is presentational and does not persist user state, so no database tables are required for the recreation. If extending with capture forms, waitlist sign-ups, or analytics events, create a Supabase table with RLS enabled and `auth.uid()`-based policies (one INSERT policy for `authenticated`, restrictive SELECT).

---

## FILE STRUCTURE

```
src/
  App.tsx
  main.tsx
  index.css
  types.ts
  data.ts
  components/
    Header.tsx
    Logo.tsx
    Logos.tsx                 (GoogleWordmark, GithubWordmark exported)
    Marquee.tsx
    VideoScrubber.tsx
    SecondVideoScrubber.tsx
    ScrollExitSplitText.tsx
    SoapTiles.tsx
    CylindricalTextDrum.tsx
```

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Luxury Focus"
template_id: "d0b1576c-73e7-4b55-a31f-87f4fa22047a"
section: "sites"
category_slug: "ecommerce"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Luxury Focus

> **Секція:** `SITES` | **Категорія:** `ecommerce`  
> **ID шаблону:** `d0b1576c-73e7-4b55-a31f-87f4fa22047a`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
E-commerce

### 🖼 Прев'ю:
![Luxury Focus](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/cd2350c1-d8c9-4863-a1c5-3b0464cd6cb3.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Recreate "SCULPTED BY TIME" Luxury Jewelry Scroll Experience

Build a single-page React + TypeScript + Vite landing page for a luxury jewelry brand. It is a **scroll-driven cinematic experience**: the page is very tall, and scrolling scrubs through two background videos while editorial text fades/blurs away and product panels slide in. Use **Tailwind CSS v4** (via `@tailwindcss/vite`) and `lucide-react` for icons. Everything lives in a single `src/App.tsx` component. No backend / no data persistence is needed.

## Stack & setup
- Dependencies: `react@19`, `react-dom@19`, `vite@6`, `@vitejs/plugin-react`, `@tailwindcss/vite`, `tailwindcss@4`, `lucide-react`, `motion`.
- `src/main.tsx` renders `<App />` into `#root`.
- `index.html` has `<div id="root"></div>` and loads `/src/main.tsx`.

## Fonts (src/index.css)
```css
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Manrope:wght@200;300;400;500;600;700;800&display=swap');
@import "tailwindcss";

@theme {
  --font-serif: "Instrument Serif", serif;
  --font-sans: "Manrope", sans-serif;
}
```
- Serif display font: **Instrument Serif** (`font-serif`).
- Sans UI font: **Manrope** (`font-sans`).

## Asset URLs (use exactly)
- Background video 1 (plays during first 40% of scroll):
  `https://res.cloudinary.com/dbfd996z4/video/upload/q_auto/f_auto/v1781009724/11111111_gvewuj.mp4`
- Background video 2 (plays during second half):
  `https://res.cloudinary.com/dbfd996z4/video/upload/q_auto/f_auto/v1781009724/2222222_x4qpet.mp4`
- Hero product PNG (ring): `https://res.cloudinary.com/dbfd996z4/image/upload/q_auto/f_auto/v1781009782/rng_awymkj.png`
- Panel product 1 (earrings): `https://res.cloudinary.com/dbfd996z4/image/upload/q_auto/f_auto/v1781017114/202606091756_msbh8b.jpg`
- Panel product 2 (ring): `https://res.cloudinary.com/dbfd996z4/image/upload/q_auto/f_auto/v1781019866/2606091843_kfonxp.jpg`

(Note: there is no CloudFront URL in this project — all media is served from Cloudinary at the `dbfd996z4` account. The `/public/main` and `/public/second` JPG frame sequences exist as fallbacks but the live page scrubs the two Cloudinary MP4s, not the JPGs.)

## Color & theme
- Page background: `#020202` (near-black), text white.
- Signature accent (titles, progress bar, hover states, cart dot): `#FBFF8D` (luminous pale chartreuse-yellow).
- Slide-in product panel background: `#FAF9F5` (warm off-white), text `#121212`; muted greys `#8E8B84`, `#73716C`, `#E5E5E2`.
- NO purple/violet anywhere.

## Layout structure (single root `div`, `h-[650vh]`, `bg-[#020202]`, `overflow-x-hidden`, `antialiased`, `font-sans`)

### 1. Fixed background video stage (`fixed inset-0 z-0`, pointer-events-none)
- Two `<video>` elements stacked absolutely, `object-cover`, `muted playsInline preload="auto"`.
- Video 1 opacity `0.85` when `progress < 0.48`, else `0`; Video 2 opacity `0.85` when `progress >= 0.48`, else `0`. Cross-fade with `transition-opacity duration-700 ease-in-out`.
- A hidden `<canvas>` (kept in DOM, `display:none`).
- Three gradient overlays for typography contrast: top (`h-44`, black 85%→transparent), bottom (`h-56`, black 90%→transparent), left (`w-1/2`, black 40%→transparent, only `lg:block`).

### 2. Top progress bar (`fixed top-0 left-0 h-[2.5px] bg-[#FBFF8D] z-50`)
- Width = `${progress * 100}%`, `transition-all duration-75`, pointer-events-none.

### 3. Editorial overlay (`fixed inset-0 z-10`, flex column space-between, padding `p-6 md:p-10 lg:p-12`)
- `pointerEvents: 'none'` when `progress > 0.45`; `visibility: hidden` when `progress >= 0.45`.
- **Header** (`flex justify-between items-start`):
  - Left column (`flex flex-col gap-10`): a 48×48 white brand crest **SVG** (5-petal abstract floral logo — provide the multi-path SVG), and 40px below it a sub-header: `<h3>` "Contemporary Luxury For The / Discerning Minimalist" (semibold, 12-13px, tracking -0.03em) + a `<p>` (11px, white/50, max-width 260px): "Exclusive creations tailored for true aesthetes. We forge more than simple ornaments; we build tactile artifacts of your personal legacy."
  - Right nav (`flex items-center gap-5..8`, 13px white/70): links **Collections, Atelier, Our story, Contact**, each with animated underline-on-hover (`after:` pseudo growing from w-0 to w-full) and `hover:scale-105`. Then a vertical separator, a **User** icon link, and a **ShoppingBag** button (with a pulsing `#FBFF8D` 6.5px dot badge). The bag button smooth-scrolls to the very bottom of the page.
- **Hero main** (`grid grid-cols-1 lg:grid-cols-12`, items-end):
  - Left (cols 1-7): giant serif headline `#FBFF8D`, uppercase, `leading-[0.88]`, fluid `fontSize: clamp(2.5rem, 5.6vw, 7.5rem)`, three lines each as own div: "&nbsp;&nbsp;&nbsp;&nbsp;*SCULPTED*" (italic), "BY TIME. WORN", "BY *YOU*" (italic). Below it two manifesto `<p>` blocks (11px white/50, width 260px) — text: "We craft modern jewelry that speaks volumes through silence..." and "Every piece acts as a personal manifesto...".
  - Right (cols 8-12, max-w-240px): product caption block — small label "Abyssal Silver Ring", `<h2>` "18K White Gold & Rough Onyx", a 10.5px description; then a transparent product card (`aspect-[4/5]`, `hover:scale-[1.04]`) holding the ring PNG (`object-contain`, `group-hover:scale-105`); then a centered serif price "$1,850" that turns `#FBFF8D` on group hover.

### 4. Slide-in product sheet (`fixed top-0 left-0 h-full w-full sm:w-[600px] lg:w-[648px] bg-[#FAF9F5] text-[#121212] z-30`)
- Transform: `translate-x-0` when open else `-translate-x-full`, `transition-transform duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)]`, shadow `12px 0 45px rgba(0,0,0,0.22)`, `overflow-y-auto`.
- Open when `progress >= 0.40 && progress < 0.50` (first card) OR `progress >= 0.90` (second card).
- Top-left **BACK TO SERIES** button (ArrowLeft icon, uppercase, tracking 0.16em) that smooth-scrolls back: to 82% if `progress >= 0.90`, else to 35%.
- Centered product header: category label (uppercase, tracking 0.15em, `#8E8B84`), serif `<h2>` title, 12px description `#73716C`; then a centered product image (`max-w-[460px]`).
- Footer transaction row (border-top, full-bleed via negative margins): a black **ADD TO ATELIER BAG** button (`h-[50px]`, uppercase tracking 0.15em), a `#E5E5E2` quantity stepper (− value +), and a large serif dynamic price `${price * quantity}`.
- **Dynamic product data** driven by `isSecondCard` (`progress >= 0.90`):
  - Second card: category "Atelier Core Edition", title "Sterling Silver Sculpture Ring", price 1350, image = ring JPG, with the sculpture description.
  - Otherwise: category "Aura Fine Earrings", title "18K White Gold & Pink Sapphire", price 1850, image = earrings JPG, with the drop-stud description.
  - Reset `quantity` to 1 whenever the active product title changes.

## Scroll & animation engine (the core)
Use refs (not state) for animation values to avoid re-renders; only `progress` and `quantity` are React state.

- **State refs:** `targetScrollFractionRef`, `currentScrollFractionRef`, `targetVideoRatioRef`, `currentVideoTimeRef`, `targetVideoSecondRatioRef`, `currentVideoSecondTimeRef`, `targetFrameRef`, `currentFrameRef`. `totalFrames = 480`.
- **Scroll listener:** compute `scrollTop / (scrollHeight - clientHeight)`, clamp 0–1, store in `targetScrollFractionRef`. Passive listener; also run once on mount and once after a 500ms timeout.
- **requestAnimationFrame loop** (`smoothUpdate`):
  1. Lerp `currentScrollFraction` toward target by factor **0.05** (snap when very close) — gives a weighted, cinematic, "catch-up" feel. `setProgress(currentScrollFraction)`.
  2. Map `activeProgress` to phases:
     - `<= 0.40`: ratio = p/0.40 → video1 ratio = ratio, video2 = 0, frame = 1 + ratio*239.
     - `0.40–0.50`: video1 = 1.0, frame = 240 (hold — first panel open).
     - `0.50–0.90`: video1 = 1.0, video2 ratio = (p-0.50)/0.40, frame = 241 + ratio*239.
     - `> 0.90`: both = 1.0, frame = 480 (second panel open).
  3. Scrub each video by lerping `currentVideoTime` toward `targetRatio * video.duration` by factor **0.08**, and set `video.currentTime` — **but only when `!video.seeking`** (skip issuing a new seek while the browser is still painting the previous frame, to prevent stutter). Same guard for the second video.
  4. Lerp `currentFrameRef` toward `targetFrameRef` by 0.08, clamped to [1, 480].
  5. Re-request the frame; cancel on cleanup.

## Stagger helper (`getStaggerStyle(start, end)`)
Maps `progress` within a [start,end] window to a fade-out: `opacity = 1 - ratio`, `translateY = -75 * ratio`, `filter: blur(${ratio*16}px)`, `willChange`, and a `cubic-bezier(0.16,1,0.3,1)` 0.35s transition; `pointerEvents: 'none'` once opacity < 0.15. Apply staggered windows to each editorial element so they melt upward and blur away as you scroll (logo 0.00–0.12, subheader 0.06–0.18, nav 0.03–0.15, title lines 0.09/0.12/0.15 → +0.11, manifesto 0.18/0.21, right caption 0.14–0.25, card 0.18–0.29, price 0.20–0.31).

## Embedded `<style>` extras
- `@keyframes scrollLine`.
- Custom dark webkit scrollbar (6px, track `#020202`, thumb white/15, hover `#FBFF8D`/40).
- Media query `(max-height:780px) and (min-width:1024px)`: tighten `#sculpted-title` margin and `#product-image-card` padding.

## Behavior summary
Scrolling 0→100% of the 650vh page: hero text melts away → video 1 scrubs forward → first earrings panel slides in (~40-50%) → video 2 scrubs → second ring panel slides in (~90%+). The ShoppingBag button jumps to the final panel; the panel BACK button scrolls back into the video sequence. All motion is buttery via double-lerp (scroll smoothing 0.05 + media smoothing 0.08) and the `!seeking` seek guard.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Prisma Creative Studio"
template_id: "0dcd204d-4015-49b5-844b-c9ad4fdfb582"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Prisma Creative Studio

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `0dcd204d-4015-49b5-844b-c9ad4fdfb582`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Prisma Creative Studio](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/cc57c386-0fb1-4745-b14c-9e83ff589a2e.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a React + Vite + TypeScript + Tailwind CSS landing page for a creative studio called "Prisma". The page has 3 sections: Hero, About, and Features. Use framer-motion for animations and lucide-react for icons. The design is dark, moody, and cinematic with a warm cream color palette.

FONTS

Load two Google Fonts in index.html:

Almarai (weights: 300, 400, 700, 800) -- used as the global default font
Instrument Serif (italic only) -- used for italic accent text in the About section
In index.css, set the global font family:


* { font-family: 'Almarai', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif; }
In tailwind.config.js, extend:

colors.primary: #DEDBC8 (warm cream, used for all primary text and accents)
fontFamily.serif: ['"Instrument Serif"', 'serif']
COLOR SYSTEM

Background: black (#000000) globally, #101010 for the About card, #212121 for Features cards
Primary text color: #E1E0CC (applied via inline style, slightly different from Tailwind primary)
Tailwind primary: #DEDBC8 (used for utility classes like text-primary, text-primary/70)
Gray text: text-gray-400, text-gray-500
Navbar link color: rgba(225, 224, 204, 0.8) with hover: #E1E0CC
CUSTOM CSS UTILITIES (index.css)

Two SVG noise texture utilities:

.noise-overlay: fractal noise (baseFrequency: 0.85, numOctaves: 3) used as overlay on hero video
.bg-noise: fractal noise (baseFrequency: 0.9, numOctaves: 4) used as subtle background in Features section
Both use inline SVG data URIs with feTurbulence filter.

SECTION 1: HERO

Full viewport height (h-screen). The entire section has p-4 md:p-6 padding creating an inset effect. Inside is a container with rounded-2xl md:rounded-[2rem] and overflow-hidden.

Background video:

URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_170732_8a9ccda6-5cff-4628-b164-059c500a2b41.mp4
autoPlay loop muted playsInline, object-cover, fills entire container
Noise overlay on top: .noise-overlay with opacity-[0.7] mix-blend-overlay pointer-events-none
Gradient overlay: bg-gradient-to-b from-black/30 via-transparent to-black/60
Navbar:

Absolutely positioned at top center
Black background pill that hangs from top edge: bg-black rounded-b-2xl md:rounded-b-3xl px-4 py-2 md:px-8
5 nav items: "Our story", "Collective", "Workshops", "Programs", "Inquiries"
Text size: text-[10px] sm:text-xs md:text-sm
Gap between items: gap-3 sm:gap-6 md:gap-12 lg:gap-14
Link color: rgba(225, 224, 204, 0.8), hover: #E1E0CC (inline styles)
Hero Content (bottom-aligned):

Absolutely positioned at bottom: absolute bottom-0 left-0 right-0
12-column grid: left 8 columns for heading, right 4 columns for text + button
Giant heading "Prisma" using WordsPullUp component:
Responsive sizes: text-[26vw] sm:text-[24vw] md:text-[22vw] lg:text-[20vw] xl:text-[19vw] 2xl:text-[20vw]
font-medium leading-[0.85] tracking-[-0.07em]
Color: #E1E0CC
Has a superscript asterisk (*) on the final "a" of "Prisma": positioned with absolute top-[0.65em] -right-[0.3em] text-[0.31em]
Pull-up animation: each word slides up from y:20 with staggered delay of 0.08s, triggered by useInView
Description paragraph (right column):
"Prisma is a worldwide network of visual artists, filmmakers and storytellers bound not by place, status or labels but by passion and hunger to unlock potential through our unique perspectives."
text-primary/70 text-xs sm:text-sm md:text-base, line-height: 1.2
Framer motion: fade up from y:20, delay 0.5s, custom ease [0.16, 1, 0.3, 1]
CTA Button "Join the lab":
Pill shape: bg-primary rounded-full
Black text, font-medium, text-sm sm:text-base
Right side has a black circle (bg-black rounded-full w-9 h-9 sm:w-10 sm:h-10) containing a white/cream ArrowRight icon
Hover: gap increases (hover:gap-3), circle scales up (group-hover:scale-110)
Framer motion: fade up from y:20, delay 0.7s, same custom ease
SECTION 2: ABOUT

bg-black, padded section with centered content
Inner card: bg-[#101010], centered text, max-w-6xl
Top: small label "Visual arts" in text-primary, text-[10px] sm:text-xs
Main heading uses WordsPullUpMultiStyle component with 3 segments:
"I am Marcus Chen," -- font-normal (Almarai)
"a self-taught director." -- italic font-serif (Instrument Serif italic)
"I have skills in color grading, visual effects, and narrative design." -- font-normal
Container: text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl max-w-3xl mx-auto leading-[0.95] sm:leading-[0.9]
Each word animates in with pull-up effect (y:20 to y:0), staggered at 0.08s delay
Body paragraph below with scroll-linked character opacity animation:
Text: "Over the last seven years, I have worked with Parallax, a Berlin-based production house that crafts cinema, series, and Noir Studio in Paris. Together, we have created work that has earned international acclaim at several major festivals."
text-[#DEDBC8], text-xs sm:text-sm md:text-base
Each character is individually wrapped in an AnimatedLetter component
Uses useScroll with target offset ['start 0.8', 'end 0.2']
Each character's opacity transitions from 0.2 to 1 based on scroll position, creating a progressive text reveal effect
Character staggering: charProgress = index / totalChars, range [charProgress - 0.1, charProgress + 0.05]
SECTION 3: FEATURES

min-h-screen bg-black, with subtle .bg-noise overlay at opacity-[0.15]
Header text uses WordsPullUpMultiStyle:
Line 1: "Studio-grade workflows for visionary creators." in cream
Line 2: "Built for pure vision. Powered by art." in text-gray-500
Both: text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal
4-column card grid (lg:h-[480px], gap-3 sm:gap-2 md:gap-1):

Each card has staggered entrance animation: scale from 0.95 + fade in, triggered by useInView (once, margin "-100px"), staggered at 0.15s intervals with ease [0.22, 1, 0.36, 1].

Card 1 - Video card: Full video background (URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260406_133058_0504132a-0cf3-4450-a370-8ea3b05c95d4.mp4), autoPlay loop muted playsInline, object-cover. Bottom text: "Your creative canvas." in #E1E0CC.

Card 2 - "Project Storyboard." (01): bg-[#212121], small image icon at top (https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171918_4a5edc79-d78f-4637-ac8b-53c43c220606.png&w=1280&q=85, 10x10 sm:12x12 rounded), title with number, 4 checklist items with green Check icons, "Learn more" link with rotated arrow (-45deg).

Card 3 - "Smart Critiques." (02): Same layout as Card 2. Icon: https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171741_ed9845ab-f5b2-4018-8ce7-07cc01823522.png&w=1280&q=85. 3 checklist items about AI analysis, creative notes, tool integrations.

Card 4 - "Immersion Capsule." (03): Same layout. Icon: https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171809_f56666dc-c099-4778-ad82-9ad4f209567b.png&w=1280&q=85. 3 checklist items about notification silencing, ambient soundscapes, schedule syncing.

All feature card checklist items use Check icon from lucide-react in text-primary color, with text-gray-400 description text. "Learn more" buttons use ArrowRight rotated -45deg.

SHARED ANIMATION COMPONENTS

WordsPullUp: Splits text by spaces, each word is a motion.span that slides up (y:20 to 0) with staggered delay. Uses useInView (once: true). Supports showAsterisk prop that adds a superscript * after the last character "a" of the final word.

WordsPullUpMultiStyle: Takes an array of {text, className} segments, splits all into individual words preserving per-word className. Same pull-up animation. Words are wrapped in inline-flex flex-wrap justify-center.

RESPONSIVE BREAKPOINTS

The page is fully responsive across mobile, tablet, and desktop. Cards in Features switch from 1-col (mobile) to 2-col (md) to 4-col (lg). Hero text scales from 26vw down to 19vw. Navbar items compress with smaller gaps on mobile. All padding, font sizes, and spacing use Tailwind responsive prefixes (sm/md/lg/xl/2xl).

TECH STACK

Vite + React 18 + TypeScript
Tailwind CSS 3
framer-motion (for all animations: pull-up text, fade-in, scroll-linked opacity, card entrances)
lucide-react (ArrowRight, Check icons)
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Art Landing"
template_id: "1e54147e-7a5b-478a-ac4e-bb3ae434ee78"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Art Landing

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `1e54147e-7a5b-478a-ac4e-bb3ae434ee78`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Art Landing](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/19b3f988-43ae-4a23-b6ed-1c64390c83df.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a two-section scroll-based landing page using React 19, TypeScript, Vite, Tailwind CSS v4, and `motion/react` (Framer Motion). The page uses Manrope, Italiana, and Marck Script fonts, with a video hero and a red second section featuring a cloud transition.

## Setup

**package.json dependencies:**
- `react` ^19, `react-dom` ^19
- `motion` ^12 (for `motion/react`)
- `tailwindcss` ^4.1, `@tailwindcss/vite` ^4.1
- `vite` ^6, `@vitejs/plugin-react` ^5
- `lucide-react`, `typescript` ~5.8

**vite.config.ts:** include `@vitejs/plugin-react` and `@tailwindcss/vite` plugins.

## src/index.css

```css
@import url('https://fonts.googleapis.com/css2?family=Italiana&family=Manrope:wght@400;600&family=Marck+Script&display=swap');
@import "tailwindcss";

@theme {
  --font-manrope: "Manrope", sans-serif;
  --font-italiana: "Italiana", serif;
  --font-marck: "Marck Script", cursive;
}
```

## src/App.tsx — Structure

**Root:** `<main>` with ref `containerRef`, classes `h-screen overflow-y-auto overflow-x-hidden font-manrope bg-black relative`.

**Scroll setup:**
```tsx
const containerRef = useRef<HTMLDivElement>(null);
const { scrollY } = useScroll({ container: containerRef });
const cloudYDesktop = useTransform(scrollY, [0, 300], [0, -100]);
const cloudYMobile  = useTransform(scrollY, [0, 300], [0, -24]);
```

### Section 1 — Video Hero

`<section className="relative h-screen w-full flex-shrink-0 overflow-hidden">`

- **Background video** (absolute inset-0, z-10, `w-full h-full object-cover`, autoPlay loop muted playsInline):
  - src: `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781500730/baby-track-video_crqby5.mp4`
- **Overlay** `absolute inset-0 z-30 pointer-events-none`.

**Top-left logo block** (`absolute top-[24px] left-[20px] md:top-[64px] md:left-[64px] pointer-events-auto max-w-[calc(100vw-140px)] md:max-w-none`):
- Flex row, gap-[16px] md:gap-[24px], items-center.
- SVG logo, white fill, 48x48 mobile / 64x64 desktop, viewBox `0 0 120 120`, path:
  `M60 120C26.8629 120 0 93.1371 0 60V0C22.5654 0 42.2213 12.4569 52.4662 30.8691C38.4788 34.2089 28.0787 46.7902 28.0787 61.8006V63.1443C28.0787 79.9648 41.7146 93.6006 58.5353 93.6006H59.8789L59.8785 61.8006C59.8785 79.3633 74.1159 93.6006 91.6787 93.6006L91.6787 61.8006C91.6787 44.2783 77.5071 30.0661 60 30.0008L60 0H62.5352C94.2722 0 120 25.7279 120 57.4648V60C120 93.1371 93.1371 120 60 120Z`
- Tagline: white, `text-[11px] md:text-[16px] w-[112px] md:w-auto leading-[1.2] font-semibold tracking-[0.02em]`.
  - Desktop (`hidden md:block`): "Effortless Growth / Operations. We Handle All Tasks. / Stay Calm." with `<br />` after each.
  - Mobile (`block md:hidden`): "Complete Business / Automation. We Handle All / Tasks. You Relax."

**Left description** (desktop only, below logo): `hidden md:flex mt-[400px] flex-col gap-[24px] w-full max-w-[320px] text-white text-[14px] font-normal leading-relaxed`. Two paragraphs about SaaS automation.

**Top-right CTA button** (`absolute top-[24px] right-[20px] md:top-[64px] md:right-[64px]`):
`px-5 py-3 md:px-10 md:py-7 border border-white rounded-[100%] text-white text-[12px] md:text-[18px] font-italiana uppercase tracking-widest hover:bg-white/10 hover:backdrop-blur-[48px] transition-all duration-300 cursor-pointer bg-black/10 backdrop-blur-sm md:bg-transparent md:backdrop-blur-none`
Label: "Get started".

**Bottom heading container** (`absolute bottom-[32px] left-[20px] right-[20px] md:left-auto md:bottom-[64px] md:right-[64px] md:max-w-[1200px] text-left md:text-right`):
- Mobile paragraphs (`md:hidden flex flex-col gap-[16px] max-w-[280px] text-white text-[12px] font-normal mb-[32px]`).
- `<h1 className="text-white text-[36px] leading-[1.1] md:text-[96px] font-italiana md:leading-[88px]">`:
  - Desktop: "Intelligent Daily / Routine Automation / For Your Business. / You Relax".
  - Mobile (`text-[32px]`): "Intelligent Daily Routine / Automation For Your / Business. You Relax".

### Section 2 — Red Background

`<section className="relative min-h-screen w-full bg-[#FF0000] flex flex-col z-10">`

**Cloud overlays** (two `motion.div`, one desktop, one mobile, both absolute top-0 left-0 w-full z-[100] pointer-events-none `-translate-y-1/2`):
- style `y: cloudYDesktop` / `y: cloudYMobile`.
- `<img src="https://res.cloudinary.com/dsdhxhhqh/image/upload/v1781500777/cloude_vj4pjv.png" className="w-full h-auto block" referrerPolicy="no-referrer" />`

**Content wrapper:** `flex-1 flex flex-col items-center w-full pt-[100px] md:pt-[400px]`.

Inner content block (`flex flex-col items-center w-full px-8 text-center z-20 relative max-w-[900px] h-auto md:h-[620px] mx-auto`):
- Same SVG logo, 80x80, white.
- Paragraph: `text-white text-[16px] h-[100px] max-w-[400px] leading-[1.6] mb-[40px] uppercase tracking-wider mx-auto`. Text: "We built this platform with a single purpose to eliminate operational chaos and restore balance to your daily business routine".
- Signature: `font-marck text-white text-[120px] leading-none mb-[32px]` reading `S.P.D`.
- Two centered paragraphs: white, `text-[16px] w-[400px] max-w-full`, font-light, first with `mb-[24px]`, container `mb-[100px] md:mb-24`.

**Bottom video block** (`relative w-full shrink-0`):
- Top fade: `absolute top-0 left-0 w-full h-[100px] bg-gradient-to-b from-[#FF0000] to-transparent z-10 pointer-events-none`.
- Video (autoPlay loop muted playsInline, `w-full h-auto block object-contain`):
  - src: `https://res.cloudinary.com/dsdhxhhqh/video/upload/v1781500762/track-video_2_haxdch.mp4`

## Animations
- Cloud parallax: maps scroll 0→300px to translateY 0→-100px (desktop) and 0→-24px (mobile), via `useTransform` with the section's container scroll.
- Button hover: background fades to `white/10` with `backdrop-blur-[48px]` over 300ms.

## Notes
- Videos are Cloudinary, not CloudFront. There are no CloudFront URLs in this project.
- All assets above are the only external URLs used.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Synthesis"
template_id: "9e17acbc-2f7a-4260-a7bf-7c3dcf30225c"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Synthesis

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `9e17acbc-2f7a-4260-a7bf-7c3dcf30225c`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Synthesis](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/c74071c2-3493-42ee-be64-6b31779427cf.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a premium scroll-driven landing page for "Elias Norden — Health Capital" using Vite + React + TypeScript + Tailwind CSS. Dark navy aesthetic, white text throughout.

**Fonts (load in index.html):**
- Body font: `Roobert TRIAL` via `<link href="https://db.onlinewebfonts.com/c/0ab46e1b2f236c9fad58c1e34cdecdf1?family=Roobert+TRIAL" rel="stylesheet" />`, fallback `system-ui, sans-serif`
- Accent serif: `Instrument Serif` (regular + italic) via `<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet" />`
- Tailwind config: `fontFamily: { sans: ['"Roobert TRIAL"', 'system-ui', 'sans-serif'], instrument: ['"Instrument Serif"', 'Georgia', 'serif'] }`, custom colors `navy-950: #020b1f`, `navy-900: #041536`

**Global CSS:** `html { scroll-behavior: smooth }`, body uses Roobert TRIAL, background `#020b1f`, white text, `-webkit-font-smoothing: antialiased`, `::selection { background: rgba(255,255,255,0.2) }`. Page title: "Elias Norden — Health Capital".

**Navbar (fixed, top, z-50, transparent):**
- Flex row, justify-between, padding `px-4 py-4 sm:px-6 sm:py-5 md:px-12 md:py-7`
- Left logo link: "Elias Norden" — `text-lg sm:text-xl md:text-2xl tracking-tight text-white`, where "Norden" is wrapped in `<span className="font-instrument italic">` with NO font-weight applied
- Right links: Articles, Allocations, Inquire — `text-[10px] sm:text-[11px] md:text-xs font-medium uppercase tracking-[0.14em] sm:tracking-[0.18em] text-white/80 hover:text-white transition-colors duration-300`, gaps `gap-4 sm:gap-6 md:gap-10`

**Hero section — scroll-scrubbed video (the core feature):**
- Outer `<section>` is `relative h-[700vh]`; inside it a `sticky top-0 h-screen overflow-hidden bg-navy-950 supports-[height:100svh]:h-[100svh]` viewport
- Video URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260610_193933_20e7efd7-2d68-4946-a270-04cb7b9ab74b.mp4`
- On mount: fetch the video as a blob, create an object URL, then pre-extract frames into `ImageBitmap[]` by seeking through a detached `<video>` element — frame count = `clamp(round(duration * 24), 30, 110)`, frames resized to max width 1280 via `createImageBitmap(video, { resizeWidth, resizeHeight })`. Clean up bitmaps and object URL on unmount; handle cancellation
- While frames extract, render a fallback muted/playsInline `<video>` scrubbed by setting `currentTime` (guard with a `seeking` flag and `seeked` listener); once frames are ready, switch to a full-screen `<canvas>` drawn with object-cover math (`scale = max(cw/fw, ch/fh)`, centered). Canvas resizes with `devicePixelRatio` capped at 2
- Scroll logic in a single `requestAnimationFrame` loop: compute raw progress = `-section.getBoundingClientRect().top / (section.offsetHeight - window.innerHeight)` clamped 0–1, then smooth it with lerp `smoothed += (target - smoothed) * 0.1`
- Phase boundaries: `SCRUB_END = 0.55`, `FADE_END = 0.65`. Phase 1 (0–0.55): video scrubs frame-by-frame with scroll. Phase 2 (0.55–0.65): hero layer fades out while a near-black layer (`bg-[#000308]`) fades in (set opacities directly via refs, no React state). Phase 3 (0.65–1.0): three paragraphs reveal sequentially, one per third of remaining scroll
- Overlay on video: `absolute inset-0 bg-black/35`

**Hero headline (centered over video):**
- `<h1 className="max-w-5xl text-center text-[2rem] leading-[1.15] tracking-tight text-white sm:text-5xl sm:leading-[1.1] md:text-6xl lg:text-7xl">` — NO font-weight class (natural weight)
- Text: "Merging science, defi and `<br className="hidden sm:block" />` lifespans into *true wellness.*" where "true wellness." is `<span className="font-instrument italic">` with no font-weight

**Press logos strip (bottom-right of hero):**
- Label "In the news:" — `text-right text-xs sm:text-sm text-white/70`
- Right-aligned flex-wrap row, `gap-x-5 gap-y-3 sm:gap-x-8 sm:gap-y-4 md:gap-x-12`, each `text-sm sm:text-lg md:text-xl text-white/90 hover:opacity-60 transition-opacity duration-300`:
  - Praxis — `font-instrument font-bold tracking-wide`
  - VENTURE BULLETIN — `font-sans font-bold tracking-tight`
  - Blockdispatch — `font-sans font-semibold italic`
  - Healthspan.Quarterly — `font-mono font-medium tracking-tighter`
  - Vetted / TJ — `font-instrument italic tracking-wide`
  - biofuture.io — `font-sans font-light tracking-widest`
- Container padding: `px-5 pb-10 sm:px-6 sm:pb-16 md:px-12 md:pb-24`

**Navy reveal layer (fades in after scrub):**
- `absolute inset-0 bg-[#000308]`, starts `opacity-0 pointer-events-none` (pointer-events enabled when fade > 0.5), centered `max-w-4xl space-y-6 sm:space-y-10 text-center`
- Three paragraphs, each `text-lg sm:text-2xl md:text-3xl leading-relaxed md:leading-snug text-white transition-all duration-700 ease-out`, animating from `translate-y-8 opacity-0` to `translate-y-0 opacity-100` as visibleCount increments:
  1. "Elias is committed to a tomorrow where people enjoy more vibrant, rewarding decades beside loved ones."
  2. "In pursuit of this purpose, in 2021 he co-founded the Healthspan Research Alliance, a global nonprofit backing early-stage science on prolonging the healthy human lifespan."
  3. "Elias is also a managing partner and co-founder of VitalVC, a venture capital firm backing bold pioneers in biotech and lifespans."

**App structure:** `<div className="bg-navy-950"><Navbar /><Hero /></div>`. Use lucide-react for any icons. No purple hues.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Velorah"
template_id: "cc20c9e6-ea3d-4b95-9e37-0ba328de281c"
section: "sites"
category_slug: "agency"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Velorah

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `cc20c9e6-ea3d-4b95-9e37-0ba328de281c`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency

### 🖼 Прев'ю:
![Velorah](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/e75796b1-3ace-4ff2-a82c-4378581abbf2.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a single-page hero section with a fullscreen looping background video, glassmorphic navigation, and cinematic typography. Use React + Vite + Tailwind CSS + TypeScript with shadcn/ui.

Video Background:

Fullscreen <video> element with autoPlay, loop, muted, playsInline
Source URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4
Positioned absolute inset-0 w-full h-full object-cover z-0

Fonts:

Import from Google Fonts: Instrumental Serif (display) and Inter weights 400/500 (body)
CSS variables: --font-display: 'Instrument Serif', serif and --font-body: 'Inter', sans-serif
Body uses var(--font-body), headings use inline fontFamily: "'Instrument Serif', serif"

Color Theme (dark, HSL values for CSS variables):

--background: 201 100% 13% (deep navy blue)
--foreground: 0 0% 100% (white)
--muted-foreground: 240 4% 66% (muted gray)
--primary: 0 0% 100%, --primary-foreground: 0 0% 4%
--secondary: 0 0% 10%, --muted: 0 0% 10%, --accent: 0 0% 10%
--border: 0 0% 18%, --input: 0 0% 18%

Navigation Bar:

relative z-10, flex row, justify-between, px-8 py-6, max-w-7xl mx-auto
Logo: "Velorah®" (® as <sup className="text-xs">), text-3xl tracking-tight, Instrument Serif font, text-foreground
Nav links (hidden on mobile, md:flex): Home (active, text-foreground), Studio, About, Journal, Reach Us — all text-sm text-muted-foreground with hover:text-foreground transition-colors
CTA button: "Begin Journey", liquid-glass rounded-full px-6 py-2.5 text-sm text-foreground, hover:scale-[1.03]

Hero Section:

relative z-10, flex column, centered, text-center, px-6 pt-32 pb-40 py-[90px]
H1: "Where dreams rise through the silence." — text-5xl sm:text-7xl md:text-8xl, leading-[0.95], tracking-[-2.46px], max-w-7xl, font-normal, Instrument Serif. The words "dreams" and "through the silence." wrapped in <em className="not-italic text-muted-foreground"> for color contrast
Subtext: text-muted-foreground text-base sm:text-lg max-w-2xl mt-8 leading-relaxed — "We're designing tools for deep thinkers, bold creators, and quiet rebels. Amid the chaos, we build digital spaces for sharp focus and inspired work."
CTA button: "Begin Journey", liquid-glass rounded-full px-14 py-5 text-base text-foreground mt-12, hover:scale-[1.03] cursor-pointer

Liquid Glass Effect (CSS class .liquid-glass):

.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

Animations (CSS keyframes + classes):

@keyframes fade-rise {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-rise { animation: fade-rise 0.8s ease-out both; }
.animate-fade-rise-delay { animation: fade-rise 0.8s ease-out 0.2s both; }
.animate-fade-rise-delay-2 { animation: fade-rise 0.8s ease-out 0.4s both; }

H1 gets animate-fade-rise
Subtext gets animate-fade-rise-delay
Hero CTA button gets animate-fade-rise-delay-2

Layout: No decorative blobs, radial gradients, or overlays. Minimalist, cinematic, vertically centered hero. The video provides all visual depth.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Conversion"
template_id: "a9b792d8-51e5-4809-ac0e-298a9b7f1c26"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Conversion

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `a9b792d8-51e5-4809-ac0e-298a9b7f1c26`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Conversion](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/0fe4d0ea-b7cf-4968-9cb2-89de00a06c96.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
**Build a fullscreen hero section with a looping background video, navigation bar, and centered content. Use React, TypeScript, Tailwind CSS, and Lucide React icons. Here are the exact specifications:**

---

## Fonts

Load two fonts in `index.html`:
- **Qanelas-Heavy** from `https://db.onlinewebfonts.com/c/3010f9da43a41a81d5daa32bd6edebc2?family=Qanelas-Heavy`
- **Inter** (weights 400, 500, 600, 700) from Google Fonts

Define custom font utility classes in `index.css`:
- `.font-qanelas` -- font-family: 'Qanelas-Heavy', sans-serif; font-weight: 900;
- `.font-inter` -- font-family: 'Inter', sans-serif;

Register both in `tailwind.config.js` under `theme.extend.fontFamily`.

---

## Layout

The entire section is `w-full h-screen overflow-hidden` with `font-inter` as the base font. Everything is stacked via `relative`/`absolute` positioning.

---

## Background Video

A `<video>` element set to `autoPlay muted loop playsInline` with class `absolute inset-0 w-full h-full object-cover`. The video source URL is:

```
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260613_235144_2f72690f-ad2d-4b1d-9dc1-96fc97d01ca5.mp4
```

---

## Content Layer

A `relative z-10 flex flex-col h-full` container holds everything on top of the video.

---

## Navigation Bar

- Container: `flex items-center justify-between`, padding `px-5 sm:px-6 md:px-12 lg:px-16 py-4 md:py-5`
- Has the `animate-nav` class (fades down from -20px, 0.6s duration, 0.1s delay, ease-out-expo curve)

**Left -- Brand:**
- Text: `text-xl sm:text-2xl font-bold text-gray-900`
- First part: `"Zipwire."` in `font-qanelas italic`
- Second part: `"Dev"` in `font-inter font-normal text-gray-600`

**Center -- Desktop nav links (hidden below md):**
- `flex items-center gap-8`
- Four links: "Overview" (#overview), "Docs" (#docs), "Our Team" (#team), "Upgrade" (#upgrade)
- Each: `text-sm font-medium text-gray-800 hover:text-gray-600 transition-colors`

**Right -- Desktop actions (hidden below md):**
- Language indicator: a small `w-5 h-4 rounded-sm bg-black` box with white "DE" text (10px), next to "EN" in `font-medium`
- Green CTA button: `bg-[#4CAF50] hover:bg-[#43A047] text-white text-sm font-semibold px-5 py-2.5 rounded-full transition-colors` with a `Download` icon (w-4 h-4) and text "Get It Today"

**Right -- Mobile hamburger (md:hidden):**
- A button with a `relative w-6 h-6` container holding both `X` and `Menu` icons absolutely positioned
- Icons crossfade with rotation: `transition-all duration-300`, the active icon is `opacity-100 rotate-0`, the inactive is `opacity-0` with `rotate-90` or `-rotate-90`

---

## Mobile Menu

- Uses two state variables: `menuOpen` (controls open/close intent) and `menuVisible` (controls DOM presence)
- When `menuOpen` becomes true, `menuVisible` is set true via `useEffect`
- On close, `menuOpen` is set false (triggers exit animation), then `animationend` listener sets `menuVisible` false to unmount
- Container: `absolute top-[60px] left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-lg`
- Gets class `mobile-menu-enter` when opening (slides down from -12px, 0.35s, ease-out-expo) or `mobile-menu-exit` when closing (slides up, 0.25s, ease-in)
- Contains the same 4 nav links (each with `onClick` that calls `handleCloseMenu`) plus the language indicator and green CTA button separated by a `border-t border-gray-200`
- Menu items stagger in via `hero-fade-up` animation with delays: 0.06s, 0.1s, 0.14s, 0.18s, 0.22s (applied via `.mobile-menu-enter > div > *:nth-child(n)` CSS selectors)

---

## Hero Content

- Container: `flex-1 flex flex-col items-center justify-start pt-20 sm:pt-24 md:pt-24 px-4 sm:px-6`

**Heading (animate-hero-1, delay 0.2s):**
- `font-qanelas uppercase text-center tracking-tight text-gray-900`
- Responsive sizing: `text-[2.5rem] leading-[0.95] sm:text-5xl md:text-7xl lg:text-8xl xl:text-[110px]`
- Text: `"Push.Route.Deploy"`

**Subtitle (animate-hero-2, delay 0.45s):**
- `mt-4 sm:mt-5 md:mt-7 text-center text-gray-700 font-medium leading-relaxed max-w-2xl px-2`
- Responsive sizing: `text-sm sm:text-base md:text-lg lg:text-xl`
- Text: `"Get Full Mesh Data Streams, Automatic UDP Hole Punching, Granular Controls, And Many More Cool Tricks!"`

**QR Code Card (animate-hero-3, delay 0.7s):**
- Wrapper: `mt-6 sm:mt-8 md:mt-10 flex flex-col items-center`
- Card: `rounded-xl p-1.5 inline-flex flex-col items-center bg-[#4CAF50]`
- Image: `rounded-lg object-cover` with responsive sizing `w-28 h-28 sm:w-36 sm:h-36 md:w-40 md:h-40`
- Image URL: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260614_015530_9919c38f-0eff-4385-b433-4f14fbf00c73.png&w=1280&q=85`
- Label beneath image: `"Try Now"` in `text-white text-[11px] sm:text-xs font-semibold mt-1.5 sm:mt-2 mb-0.5 tracking-wide`

---

## Scroll Indicator

- Positioned `absolute bottom-4 sm:bottom-6 left-1/2 -translate-x-1/2 animate-bounce`
- Contains a `ChevronDown` icon, `w-5 h-5 sm:w-6 sm:h-6 text-gray-600`

---

## Animations (all in index.css)

All entrance animations use `opacity: 0` as the initial state with `animation-fill-mode: forwards`.

| Class | Keyframes | Duration | Delay | Easing |
|---|---|---|---|---|
| `.animate-nav` | `nav-fade-down` (translateY -20px to 0) | 0.6s | 0.1s | cubic-bezier(0.16, 1, 0.3, 1) |
| `.animate-hero-1` | `hero-fade-up` (translateY 30px to 0) | 0.8s | 0.2s | cubic-bezier(0.16, 1, 0.3, 1) |
| `.animate-hero-2` | `hero-fade-up` | 0.8s | 0.45s | cubic-bezier(0.16, 1, 0.3, 1) |
| `.animate-hero-3` | `hero-fade-up` | 0.8s | 0.7s | cubic-bezier(0.16, 1, 0.3, 1) |
| `.mobile-menu-enter` | `menu-slide-down` (translateY -12px to 0) | 0.35s | 0 | cubic-bezier(0.16, 1, 0.3, 1) |
| `.mobile-menu-exit` | `menu-slide-up` (translateY 0 to -12px) | 0.25s | 0 | cubic-bezier(0.7, 0, 0.84, 0) |
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Web3 EOS Hero"
template_id: "299cdf95-e857-4537-b540-326f9385855f"
section: "sites"
category_slug: "web3"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Web3 EOS Hero

> **Секція:** `SITES` | **Категорія:** `web3`  
> **ID шаблону:** `299cdf95-e857-4537-b540-326f9385855f`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Web3

### 🖼 Прев'ю:
![Web3 EOS Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/c987166d-09dc-48d0-a682-d1dcff00e60d.png)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-screen hero section for a Web3 landing page. Use the font "General Sans" (from Fontshare) throughout. The entire section has a pure black (#000000) background with a fullscreen looping background video (muted, autoplay, playsInline) using this URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260217_030345_246c0224-10a4-422c-b324-070b7c0eceda.mp4. The video is covered by a 50% black overlay (bg-black/50) for readability. All content sits on top of the video.

Navbar:

Horizontally spread across the top with 120px horizontal padding and 20px vertical padding.

Left side: a placeholder logo wordmark (use "LOGOIPSUM" or similar) in white, 187px wide and 25px tall, followed by 4 nav links spaced 30px apart: "Get Started", "Developers", "Features", "Resources". Each nav link is white, 14px, font-medium, with a small white 14px chevron-down arrow icon to the right (14px gap between label and arrow). Nav links are hidden on mobile.

Right side: a "Join Waitlist" pill button. This button has a subtle layered construction — a fully rounded pill shape with a thin 0.6px solid white outer border, and inside that, a black-background pill with the text "Join Waitlist" in white, 14px, font-medium, centered with 29px horizontal and 11px vertical padding. There's also a subtle white glow/light streak effect along the top edge of the button (a blurred white-to-transparent gradient blob positioned at the top).

Hero Content (centered below the navbar):

Vertically centered in the remaining viewport space, pushed down with about 280px top padding on desktop (200px on mobile), 102px bottom padding.

All content is horizontally centered and stacked vertically with 40px gaps.

Badge/pill: A small rounded pill (20px border-radius) with 10% white background and a 1px white/20% border. Inside: a tiny 4px white dot, then text reading "Early access available from" in white at 60% opacity, followed by " May 1, 2026" in solid white. Font is 13px, font-medium.

Heading: Large text reading "Web3 at the Speed of Experience", max-width 613px, 56px on desktop / 36px on mobile, font-medium, line-height 1.28. The text has a gradient fill — a linear-gradient at ~144.5 degrees going from solid white (at ~28%) to fully transparent black (at ~115%), applied as a background-clip text effect so the text itself shows the gradient.

Subtitle: Below the heading with a 24px gap. Text reads: "Powering seamless experiences and real-time connections, EOS is the base for creators who move with purpose, leveraging resilience, speed, and scale to shape the future." — 15px, font-normal, white at 70% opacity, max-width 680px, centered.

CTA Button: A "Join Waitlist" pill button similar to the navbar button but with a white background and black text instead. Same layered construction: 0.6px white outer border, white glow streak on top, and inside the white pill the text is 14px font-medium black, with 29px horizontal and 11px vertical padding.

The entire layout is responsive — nav links collapse on screens below md breakpoint, heading scales down, and padding adjusts.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Aetheris Voyage"
template_id: "07c9ca13-9834-4ef0-8627-752c63ef7c90"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Aetheris Voyage

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `07c9ca13-9834-4ef0-8627-752c63ef7c90`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero Section

### 🖼 Прев'ю:
![Aetheris Voyage](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/c11307fb-cc3a-4489-b275-7ae07aa283b2.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build Prompt: Cinematic Space-Travel Landing Page
Build a single-page landing site with two full-height sections (Hero + Capabilities), both using looping background videos with custom JS crossfade, a shared liquid-glass design system, and Framer Motion entrance animations.

Tech stack (pinned, CDN-only)
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
<script src="https://unpkg.com/framer-motion@11.11.17/dist/framer-motion.js"></script>
<script>window.Motion = window.FramerMotion;</script>
Body is bg: #000. Page is a React app mounted on #root, all components are <script type="text/babel"> files exporting via window.X = X.

Fonts
Google Fonts:

family=Instrument+Serif:ital@0;1&family=Barlow:wght@300;400;500;600
Tailwind config adds:

font-heading → 'Instrument Serif', serif (always italic in use)
font-body → 'Barlow', sans-serif
Default border radius override: DEFAULT: "9999px" (so bare rounded → pill).

Liquid-glass utilities (exact CSS, in a <style> block)
Two variants — .liquid-glass (subtle, for nav/chips/cards) and .liquid-glass-strong (heavier blur, for primary CTA):

.liquid-glass {
background: rgba(255,255,255,0.01);
background-blend-mode: luminosity;
backdrop-filter: blur(4px);
-webkit-backdrop-filter: blur(4px);
border: none;
box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
position: relative;
overflow: hidden;
}
.liquid-glass::before {
content: "";
position: absolute; inset: 0;
border-radius: inherit;
padding: 1.4px;
background: linear-gradient(180deg,
rgba(255,255,255,0.45) 0%,
rgba(255,255,255,0.15) 20%,
rgba(255,255,255,0) 40%,
rgba(255,255,255,0) 60%,
rgba(255,255,255,0.15) 80%,
rgba(255,255,255,0.45) 100%);
-webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
-webkit-mask-composite: xor;
mask-composite: exclude;
pointer-events: none;
}
.liquid-glass-strong { /* same but: */
backdrop-filter: blur(50px);
box-shadow: 4px 4px 4px rgba(0,0,0,0.05), inset 0 1px 1px rgba(255,255,255,0.15);
}
.liquid-glass-strong::before { /* same but 0.5 / 0.2 / 0 / 0 / 0.2 / 0.5 stops */ }
FadingVideo component (custom JS crossfade, no CSS transitions)
Wraps a <video autoPlay muted playsInline preload="auto"> starting at opacity: 0. Behavior:

FADE_MS = 500, FADE_OUT_LEAD = 0.55 seconds.
fadeTo(target, duration) uses requestAnimationFrame; reads current opacity from http://video.style.opacity so each new fade resumes from wherever the last one left off. Each call calls cancelAnimationFrame on the previous rAF id before starting.
On loadeddata: set opacity 0, play(), fadeTo(1).
On timeupdate: if fadingOutRef not set and duration - currentTime <= 0.55 and > 0, flip the ref and fadeTo(0).
On ended: set opacity 0; after setTimeout(100ms) reset currentTime = 0, play(), clear fadingOutRef, fadeTo(1).
loop attribute is OFF (we implement looping manually via ended).
Cleanup on unmount: cancel rAF, remove listeners.
Section 1 — Hero (full viewport, black bg)
Background video (120% width/height, top-aligned, centered horizontally — focal point is the top of frame):

src: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260418_080021_d598092b-c4c2-4e53-8e46-94cf9064cd50.mp4
class: absolute left-1/2 top-0 -translate-x-1/2 object-cover object-top z-0
style: { width: "120%", height: "120%" }
No overlay. z-10 layer holds: Navbar → Hero content (flex-1, centered) → Partners.

Navbar (fixed top-4, px-8 / lg:px-16, z-50)
Left: 48×48 liquid-glass circle with italic serif lowercase "a" (Instrument Serif).
Center (desktop only): liquid-glass pill, px-1.5 py-1.5, holding 5 text links — Home, Voyages, Worlds, Innovation, Plan Launch — each px-3 py-2 text-sm font-medium text-white/90 font-body. Followed by a white pill button Claim a Spot + ArrowUpRight icon (bg-white text-black, whitespace-nowrap).
Right: 48×48 invisible spacer to balance logo.
Hero content (centered, pt-24 px-4)
All animated with Framer Motion, initial: {filter: blur(10px), opacity: 0, y: 20}, easeOut.

Badge (delay 0.4s): liquid-glass rounded-full pill. Contains white pill chip "New" (bg-white text-black px-3 py-1 text-xs font-semibold) + text "Maiden Crewed Voyage to Mars Arrives 2026" (text-sm text-white/90, pr-3).
Headline — BlurText component (word-by-word animation, see below). Text: "Venture Past Our Sky Across the Universe". Classes: text-6xl md:text-7xl lg:text-[5.5rem] font-heading italic text-white leading-[0.8] max-w-2xl justify-center tracking-[-4px].
Subheading (delay 0.8s, mt-4 text-sm md:text-base text-white max-w-2xl font-body font-light leading-tight): "Discover the universe in ways once unimaginable. Our pioneering vessels and breakthrough engineering bring deep-space exploration within reach—secure and extraordinary."
CTAs (delay 1.1s, flex items-center gap-6 mt-6):
Primary: liquid-glass-strong rounded-full px-5 py-2.5 text-sm font-medium text-white with "Start Your Voyage" + ArrowUpRight (h-5 w-5).
Secondary: bare text link, "View Liftoff" + Play icon (h-4 w-4, filled).
Stats row (delay 1.3s, flex items-stretch gap-4 mt-8): two liquid-glass cards, p-5 w-[220px] rounded-[1.25rem], each:
Top: white 28×28 outline SVG icon (clock for card 1, globe for card 2).
Bottom: large number in Instrument Serif italic white (text-4xl tracking-[-1px] leading-none): "34.5 Min" / "2.8B+". Label below (text-xs text-white font-body font-light mt-2): "Average Videos Watch Time" / "Users Across the Globe".
Partners (bottom of hero, delay 1.4s)
flex flex-col items-center gap-4 pb-8:

liquid-glass rounded-full chip (px-3.5 py-1 text-xs font-medium text-white): "Collaborating with top aerospace pioneers globally".
Row of 5 names in Instrument Serif italic white, text-2xl md:text-3xl tracking-tight, gap-12/md:gap-16: Aeon · Vela · Apex · Orbit · Zeno.
BlurText component (word-by-word blur-in)
IntersectionObserver triggers on 10% visibility. Splits text by spaces. Each word is a motion.span with:

initial: {filter: 'blur(10px)', opacity: 0, y: 50}
3-step keyframes to {filter: 'blur(5px)', opacity: 0.5, y: -5} → {filter: 'blur(0px)', opacity: 1, y: 0}
duration: 0.7 (stepDuration 0.35 × 2), times: [0, 0.5, 1], ease: easeOut
Stagger: delay = (i * 100) / 1000 seconds
display: inline-block, marginRight: 0.28em (not non-breaking-space — letter-spacing -4px eats nbsp).
Parent <p> is display: flex; flexWrap: wrap; justifyContent: center; rowGap: 0.1em.
Section 2 — Capabilities (min-h-screen, black bg)
Background video (full-bleed, no 120% scale):

src: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260418_094631_d30ab262-45ee-4b7d-99f3-5d5848c8ef13.mp4
class: absolute inset-0 w-full h-full object-cover z-0
Same FadingVideo treatment. No overlay.

Content (relative z-10 px-8 md:px-16 lg:px-20 pt-24 pb-10 flex flex-col min-h-screen):

Header (mb-auto):

Kicker: text-sm font-body text-white/80 mb-6 → // Capabilities
Heading: font-heading italic text-white text-6xl md:text-7xl lg:text-[6rem] leading-[0.9] tracking-[-3px]:
Production
evolved
(two lines, <br/> between).
Three cards (grid grid-cols-1 md:grid-cols-3 gap-6 mt-16): each is liquid-glass rounded-[1.25rem] p-6 min-h-[360px] flex flex-col.

Top row of each card (flex items-start justify-between gap-4):

Left: 44×44 nested liquid-glass square (rounded-[0.75rem]) with a white Material Icons SVG (fill currentColor, h-6 w-6 text-white). Use random Material icons — these three used:
AI Scenery: image icon — path M5 21q-.825 0-1.412-.587T3 19V5q0-.825.588-1.412T5 3h14q.825 0 1.413.588T21 5v14q0 .825-.587 1.413T19 21H5Zm1-4h12l-3.75-5-3 4L9 13l-3 4Z
Batch Production: movie icon — path M4 6.47 5.76 10H20v8H4V6.47M22 4h-4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.89-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4Z
Smart Lighting: lightbulb icon — path M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1Zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7Z
Right: flex flex-wrap justify-end gap-1.5 max-w-[70%] — 4 small liquid-glass pill tags (rounded-full px-3 py-1 text-[11px] text-white/90 font-body whitespace-nowrap):
Card 1: Natural Context · Photo Realism · Infinite Settings · Eco-Vibe
Card 2: Scale Fast · Visual Consistency · Time Saver · Ready to Post
Card 3: Ray Tracing · Physical Shadows · Studio Quality · Sunlight Sync
Middle: flex-1 spacer.

Bottom of each card (mt-6):

Title h3: font-heading italic text-white text-3xl md:text-4xl tracking-[-1px] leading-none — "AI Scenery" / "Batch Production" / "Smart Lighting"
Body p (mt-3 text-sm text-white/90 font-body font-light leading-snug max-w-[32ch]):
"AI analyzes your product to create indistinguishable natural environments — from Icelandic cliffs to misty forests."
"Style your entire product line in minutes. Create a unified visual identity for catalogues and social media without weeks of retouching."
"Automatic lighting and material adjustment. Achieve flawless integration with realistic shadows and sunlight."
Icons (inline lucide-style SVGs, currentColor stroke)
ArrowUpRight: 24×24, M7 17L17 7 + M7 7h10v10, strokeWidth 2, round caps.
Play: 24×24 filled polygon 6 4 20 12 6 20 6 4.
Notes
All text white; no green, no gradient backgrounds.
No CSS transitions on the videos — fades must be rAF-driven per the FadingVideo spec.
Videos are full-bleed with no dark overlay; contrast comes from the liquid-glass chrome.
Framer Motion dev warnings about list keys can be suppressed with a console.error filter wrapper — they're benign.
The detailed prompt above captures every element, style, animation, video URL, and font to recreate the landing page exactly.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Cyberpunk Reveal"
template_id: "f833317f-a056-4b80-9ae0-246d97dbfbb2"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Cyberpunk Reveal

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `f833317f-a056-4b80-9ae0-246d97dbfbb2`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Cyberpunk Reveal](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/d205a9f6-b2ae-4638-9663-a7ea5c5ea245.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Recreate a cyberpunk-style hero section (React + Vite + TypeScript + Tailwind CSS, lucide-react icons)**

Build a single-page app with a full-screen hero section in `src/App.tsx`. Stack: React 18, Tailwind CSS, lucide-react (icons only, `Menu` and `X`). No other packages.

## Assets

```
BG_IMAGE_1 (base, red-tinted portrait):
https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_125121_afb71ce9-9c64-4c54-90b5-c89c0764c052.png&w=1920&q=85

BG_IMAGE_2 (alternate reveal image):
https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_135737_0da59642-725b-451a-997b-b0283d95a42a.png&w=1280&q=85
```

## Fonts (index.css)

- Google Fonts import: `JetBrains Mono` weights 300–800 plus italic 400/500.
- Apply globally: `* { font-family: 'JetBrains Mono', monospace; }` and a `.font-helvetica-neue` class that also resolves to JetBrains Mono.
- Also declare a `@font-face` for 'Helvetica Neue Roman' from `/fonts/HelveticaNeue-Roman.woff2` / `.woff` (weight 400, `font-display: swap`) — declared but the mono font is what renders.
- Root wrapper div: `min-h-screen bg-white tracking-[-0.02em]` with inline `fontFamily: "'JetBrains Mono', monospace"`.

## Navbar (fixed, z-50)

`<nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between md:justify-center p-4 sm:p-5">`

- **Desktop (md+): ONE centered pill** — `bg-black/60 backdrop-blur-md rounded-full pl-3 pr-2 py-2 flex items-center gap-1` containing, in order: a 22x22 white SVG logo (geometric angular mark, viewBox 0 0 256 256, path: `M 256 64 L 256 128 L 192.5 128 L 160 95 L 128 64 L 96 95 L 63.5 128 L 64 128 L 128 192 L 128 256 L 64.5 256 L 32 223 L 0 192 L 0 64 L 64 0 L 192 0 Z M 256 192 L 256 256 L 192.5 256 L 160 223 L 128 192 L 128 128 L 192 128 Z`); text link buttons "Module" (white, active), "Case Records", "Biotech", "Tiers", "Live Demo" (gray-300, `text-sm font-medium px-3 py-1.5 rounded-full hover:bg-white/10 hover:text-white`); and a white CTA "Connect" (`bg-white text-gray-900 text-sm font-semibold px-5 py-1.5 rounded-full hover:bg-gray-100 ml-1`).
- **Mobile (<md):** logo in its own black/60 blurred pill (left) and a hamburger toggle pill (right) using lucide `Menu`/`X` size 22. Toggling opens a full-width white dropdown (`fixed top-0 z-40 pt-16 pb-6 px-5 shadow-lg`) listing the 5 links (gray-800, `py-3 border-b border-gray-100`) plus a dark "Connect" pill button; tapping a link closes it.

## Hero section (100dvh, `relative overflow-hidden`)

Layers bottom to top:

1. **Grid background (z-0):** full-size SVG at `opacity: 0.1`, a 48px square `<pattern>` of grid lines (`stroke #64748b`, width 0.6). The pattern's x/y offset follows the mouse with parallax: target = (normalized cursor position − 0.5) × 16px, eased at 0.06 lerp per frame.
2. **Base image (z-10):** `bg-center bg-cover` div with BG_IMAGE_1, with a Ken Burns intro: `@keyframes kenBurns { from { transform: scale(1.12) } to { scale(1) } }`, 2.4s `cubic-bezier(0.22,1,0.36,1)` forwards.
3. **Cursor spotlight reveal layer (z-30):** a second `bg-cover` div with BG_IMAGE_2, masked by a canvas-generated radial gradient that follows the smoothed cursor. Implementation: a hidden full-window canvas; every frame, clear it and fill a circle (radius 260px) at the cursor with a radial gradient (stops: 0→1 opacity, 0.4→1, 0.6→0.75, 0.75→0.4, 0.88→0.12, 1→0), export via `toDataURL()` and set as `mask-image`/`-webkit-mask-image` (`mask-size: 100% 100%`) on the image div. Cursor smoothing: rAF loop with lerp factor 0.1 toward real mouse position, starting offscreen at (−999,−999).
4. **Stats on a fading circular arc (z-50, hidden below sm):** container `absolute inset-y-0 right-0 pointer-events-none`, SVG `viewBox="0 0 380 700"` `preserveAspectRatio="xMaxYMid meet"` `class="h-full w-auto"`. Concentric arcs centered at `(-110, 300)` (off-canvas left, so arcs sweep in from the subject). Data:
   - r=330, arc from −92° to 16°, dot at −46°, stat "10+" / "YEARS REAL"
   - r=395, arc −56° to 60°, dot at 2°, stat "40+" / "USE FORMS"
   - r=460, arc −14° to 72°, dot at 44°, stat "95%" / "REPEAT MEMBERS"

   Each arc is a path (`A r r 0 0 1`) stroked at 1.1 with a per-arc `userSpaceOnUse` linearGradient from arc start point to end point, white with stop-opacities 0 → 0.5 (22%) → 0.5 (55%) → 0.1 (85%) → 0 (100%) so both ends fade out. At each dot position (polar from center): a filled white circle r=3.4, a white ring r=7 at 35% stroke opacity, the number at dot+(16,4) in white 32px (suffix as `<tspan>` 19px raised `dy="-10"`, letter-spacing −1px), and the uppercase label at dot+(18,22), 8.5px, weight 600, letter-spacing 2px, 80% opacity.
5. **Hero text block (z-50):** `absolute bottom-12 sm:bottom-16 md:bottom-24 left-5 sm:left-8 md:left-12 max-w-[300px] sm:max-w-md`:
   - Eyebrow: `Gateway to your *augmented self*` (italic span), `text-[11px] sm:text-xs font-semibold tracking-[0.12em] text-white/90`
   - H1: `A window / of coming / enhancements` (manual `<br/>`), `text-4xl sm:text-5xl md:text-6xl leading-[1.05] tracking-[-0.08em] text-white`
   - Paragraph: "A future where carbon fiber, titanium, and human instinct align. Not machine. Not human. Something wonderfully poised between." `text-sm sm:text-base text-white/90 leading-relaxed`
   - CTA "Reserve Now": white pill `px-7 sm:px-8 py-3 sm:py-3.5 rounded-full shadow-lg shadow-black/20`, hover `scale-[1.04]`, active `scale-95`, plus a shine sweep: an absolutely-positioned gradient span (`from-transparent via-white/60 to-transparent`) translating from `-translate-x-full` to `translate-x-full` over 700ms on group hover.

## Animations (CSS keyframes in index.css)

- `.hero-rise`: from `opacity:0; translateY(26px); blur(8px)` to clear; 0.95s `cubic-bezier(0.22,1,0.36,1)` forwards; staggered inline delays — eyebrow 0.15s, H1 0.3s, paragraph 0.5s, button 0.7s.
- `.nav-drop`: from `opacity:0; translateY(-18px)`; 0.8s same easing, 0.1s delay; applied to all nav pills.
- `.arc-line`: stroke-draw via `stroke-dasharray/offset` set to the arc length (computed `r × Δangle(rad)`, passed as CSS var `--len`), animating offset to 0 over 1.6s `cubic-bezier(0.65,0,0.35,1)`; delays staggered `0.4s + i × 0.22s`.
- `.arc-dot`: `popIn` overshoot (scale 0.4 → 1.25 → 1) 0.55s back-out easing, delay = lineDelay + 0.9s; needs `transform-box: fill-box; transform-origin: center`.
- `.arc-ring`: infinite `pulseRing` (scale 1→1.45, opacity 0.35→0) 2.8s ease-in-out, delay markDelay + 0.3s.
- `.arc-text`: simple fadeIn 0.7s, number at markDelay + 0.15s, label + 0.3s.
- Wrap all of the above in `@media (prefers-reduced-motion: reduce)` resetting animation/opacity/transform/dashoffset.

## Behavior notes

- All mouse-driven effects run in one `requestAnimationFrame` loop; clean up listener and rAF on unmount.
- Stats arc is decorative: `pointer-events-none`, hidden on mobile (`hidden sm:block`).
- Everything must remain readable: white text over the red imagery.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "CoderCrest"
template_id: "a997a3e1-36ff-4298-bbab-7e9d15001cf8"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 CoderCrest

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `a997a3e1-36ff-4298-bbab-7e9d15001cf8`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![CoderCrest](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/1a724fea-d9e1-4685-a5b9-565ccfc972fb.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a React + TypeScript component named HeroSection in src/components/HeroSection.tsx using Tailwind CSS and the hls.js npm package (install it: npm install hls.js).

Layout & Background:

A <section> that is 100vh tall, position: relative, overflow: hidden, flex column centered, with background: #000.
A fullscreen HLS video background using this Mux stream URL: 
https://stream.mux.com/tLkHO1qZoaaQOUeVWo8hEBeGQfySP02EPS02BmnNFyXys.m3u8

The video is <video autoPlay loop muted playsInline> with classes absolute inset-0 w-full h-full object-cover and zIndex: 0. Play it through hls.js: if Hls.isSupported(), create an Hls({ autoStartLoad: true }) instance, loadSource, attachMedia, and play on MANIFEST_PARSED. Else, fall back to native application/vnd.apple.mpegurl support. Clean up the Hls instance on unmount. No overlay over the video — full opacity.
Content container:

A div with classes relative z-10 flex flex-col items-center text-center px-4 max-w-5xl mx-auto and inline style marginTop: 380 (pushes content down 380px).
Headline (<h1>):

Font: 'YDYoonche L', 'YDYoonche M', sans-serif
fontSize: clamp(2.2rem, 7vw, 6.5rem), color: #fff, fontWeight: 300, letterSpacing: -0.01em, lineHeight: 1.1, className="leading-tight".
Three lines:
"The vision" — gradient text using background: linear-gradient(90deg, #666666 0%, #d0d0d0 50%, #666666 100%) with WebkitBackgroundClip: text, WebkitTextFillColor: transparent, backgroundClip: text, display: block, lineHeight: 1.1, marginBottom: -0.22em.
"of engineering" — same gradient styling as line 1.
A flex line flex items-center justify-center gap-3 flex-wrap with white text containing in order:
<span style={{color:'#999'}}>is</span>
A circular video icon (see below) playing the human clip
<span>human</span>
<span style={{color:'#999', position:'relative', top:'0.15em', marginLeft:'0.25em'}}>+</span>
A circular video icon playing the AI clip
<span>AI</span>
VideoIcon component:

Outer <span> with classes inline-block align-middle rounded-full overflow-hidden, sized via inline style width/height: clamp(48px, 10vw, ${size}px) (default size=72, but the hero passes size={110} for both icons), flexShrink: 0.
Inner <video autoPlay loop muted playsInline> with width: 100%, height: 100%, objectFit: cover, display: block. Call videoRef.current.play().catch(() => {}) in a useEffect.
Two CloudFront MP4 sources:
VIDEO_HUMAN: 
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260424_090051_64ea5059-da6b-492b-a171-aa7ecc767dc3.mp4

VIDEO_AI: 
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260424_093237_ff0ddc63-c068-4e29-96da-fdd0e40af133.mp4

Subheading (<p>):

Classes mt-4 max-w-xl text-center px-2.
fontSize: clamp(0.95rem, 2.2vw, 1.2rem), color: #ccc, lineHeight: 1.4, fontWeight: 400.
Text: "We help you map the talent you need, track the talent you have, and close your gaps to thrive in a GenAI world."
CTA Button:

Classes: mt-6 transition-all duration-300 hover:scale-[1.03] hover:shadow-[0px_6px_32px_8px_rgba(39,243,169,0.22)] active:scale-[0.98]
Inline style: padding: '12px 28px', background: '#000', boxShadow: '0px 6px 24px 6px rgba(39, 243, 169, 0.15)', borderRadius: 8, outline: '1px solid #30463C', outlineOffset: -1, border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10.
Inner <span> with color: '#fff', fontSize: 14, fontWeight: 400, text: "Join The Movement!".
Animations / interactions:

All three videos auto-play, loop, muted, inline.
Button has a 300ms transition: scales to 1.03 and gains a brighter green glow on hover, scales to 0.98 on active.
Fonts:

The headline expects 'YDYoonche L' / 'YDYoonche M' to be loaded globally (e.g., via index.css or an external font provider). It falls back to sans-serif.

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Gateway Portal"
template_id: "6038092c-1018-4b1e-a2b0-06ac7401fa50"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Gateway Portal

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `6038092c-1018-4b1e-a2b0-06ac7401fa50`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Gateway Portal](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/6a203d4b-2a98-4555-a5db-8b261caff7d0.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a React + TypeScript (Vite) single-page hero called Auragate — an immersive, scroll-driven landing experience with a portal zoom-in effect, parallax mouse motion, and an arc-shaped testimonial card carousel. Use inline `style` objects (not CSS modules); Tailwind is only used for a few layout utility classes on one element. No UI libraries.

Fonts & `index.html`
In `index.html`, set `<title>Step Into Wonder</title>` and load these exact fonts in `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Viaoda+Libre&family=Imprima&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
<link href="https://db.onlinewebfonts.com/c/e2bba9cf49b298d6be781c2274694ea3?family=Mr+Dafoe+Regular" rel="stylesheet" />
<link href="https://db.onlinewebfonts.com/c/0976a2619014c5855690b7509fab4c6e?family=Helvetica+Now+Display" rel="stylesheet" />
```
Two font families are used throughout:
- `'Helvetica Now Display', sans-serif` — all UI text, headings, body, buttons.
- `'Mr Dafoe Regular', cursive` — decorative script accents ("Discover", "Aura" in the wordmark, the large "A.").

Global CSS (`index.css`)
Tailwind directives at top. Then: universal `box-sizing: border-box`; `html, body` with `margin/padding: 0`, `background: #0a0608`, `scroll-behavior: auto`, `overflow-x: clip`; `body` font-family `'Helvetica Now Display', 'Inter', sans-serif` with `-webkit-font-smoothing: antialiased`. Add `html { scrollbar-gutter: stable; }` to prevent scrollbar layout shift. Include a `@keyframes bobUp` (0/100% translateY(0), 50% translateY(-6px)).

Assets (use these exact URLs)
```js
const PORTAL_BG = 'https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1781046673/image_1_ksxfzb.png';
const WORLD_BG  = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_231253_53c0854c-d13c-42c1-9fc0-17e87cd34091.png&w=1280&q=85';
```
`PORTAL_BG` is the foreground "portal" image you zoom into; `WORLD_BG` is the cloud/world background revealed behind it.

Layout structure (z-index stack on `#0a0608` root)
1. Fixed world background (`zIndex 0`): `position: fixed; inset: 0; overflow: hidden`. Inner `worldRef` div (`transformOrigin: 50% 50%`, `willChange: transform`) holding `WORLD_BG` `` at `width/height 100%`, `objectFit: cover`. Never scrolls.
2. **Fixed nav** (`zIndex 50`): see below.
3. **Intro track** (`zIndex 5`): `height: 160vh`, contains a `position: sticky; top: 0; height: 100vh; overflow: hidden` stage holding the portal + Scene 1 UI.
4. **Section 2** (`zIndex 10`): scrollable testimonial content + footer, rendered over the fixed world bg.

### Scroll & motion engine
- `useIsMobile()` hook: matchMedia `(max-width: 767px)`, initial `window.innerWidth < 768`.
- Track scroll progress 0→1 across the pinned intro: `progress = clamp(window.scrollY / (introRef.offsetHeight - innerHeight), 0, 1)`. Store in both state and a ref. Listen on `scroll` (passive) and `resize`.
- Helper math: `easeInOut(t) = t<0.5 ? 2t² : -1+(4-2t)t`, `lerp(a,b,t)`, `clamp`.
- **Mouse parallax** via `requestAnimationFrame`: read raw mouse as `(clientX/innerWidth - 0.5)2` (same for Y). Smooth toward it with `lerp(..., 0.07)` each frame. Invert (`rx=-mx, ry=-my`). Magnitudes `MAG = { world: 6, portal: 7 }`.
- Each frame, with `ep = easeInOut(scrollProgress)`:
  - World: `scale = lerp(1, 1.18, ep)`, `transform: scale(s) translate(rx6px, ry6px)`.
  - Portal: `scale = lerp(1, 7.5, ep)`, `transform: scale(s) translate(rx7px, ry*7px)`, `transformOrigin: '52% 38%'`.
- **Opacity transitions** driven by scrollProgress:
  - `portalOpacity` = 1 until 0.66, then fades to 0 over the next 0.22 of scroll.
  - `scene1Opacity` = `clamp(1 - scrollProgress/0.22, 0, 1)` (Scene 1 UI fades out in the first 22% of scroll). When `< 0.05`, set `pointerEvents: none`.
- `uiVisible` state flips true 600ms after mount; Scene 1 UI fades/slides up (`translateY(24px)→0`, `opacity 0→1`, `transition: opacity 1s ease, transform 1s ease`, `transitionDelay: 0.3s`).

### Navigation (fixed, top)
Flex row, space-between, padding `26px 40px` desktop / `18px 20px` mobile.
- **Left:** `` — inline-flex baseline-aligned: "Aura" in Mr Dafoe (36px / 30px mobile) + "gate" in Helvetica Now Display weight 500 (24px / 20px), `letterSpacing: -0.02em`, white.
- **Right:** a pill **"Watch Demo"** button (white bg, `#161616` text, weight 600, `borderRadius: 999px`, padding `11px 22px` / `9px 16px`, hover bg `#e6e6e6`) immediately followed by a round 42px (38px mobile) white hamburger button containing an SVG of two rounded horizontal lines (`stroke #161616`, width 1.6). Both transition bg `0.25s`.

### Scene 1 hero copy (bottom-anchored, fades out on scroll)
A bottom-aligned container with Tailwind classes `absolute inset-x-0 bottom-0 flex flex-col md:flex-row md:items-end md:justify-between gap-12 md:gap-20`, padding `0 44px 52px` (`0 22px 40px` mobile).
- **Column 1** (`maxWidth 560px`, left aligned): `

` Helvetica Now Display weight 500, white, `lineHeight 1.04`, `letterSpacing -0.02em`, `fontSize clamp(40px,4vw,58px)` (mobile `clamp(30px,9vw,44px)`). The word **"Discover"** is a leading span in Mr Dafoe, color `#9a9a9a`, `fontSize 1.15em`, `marginRight 0.12em`. Full text:
  > *Discover* Living \
 Digital Worlds \
 Vivid, Alive, Endless
  
  Below it a `

` (weight 400, `13–14px`, `lineHeight 1.6`, `color rgba(255,255,255,0.5)`, `maxWidth 340px`, `marginTop 18px`): "Experience immersive worlds with stories that blur the line between imagination, AI and living reality made for you."
- **Column 2** (hidden on mobile, flex, `gap 14px`): a large "A." in Mr Dafoe (64px, white, `lineHeight 0.8`) next to a `

` (weight 400, 11px, `color rgba(255,255,255,0.5)`, `maxWidth 150px`): "A studio is a trusted partner in your journey through wonderland."

### Section 2 — "Real wonders" + arc carousel
Centered column, `paddingTop 14vh` (12vh mobile), `paddingBottom 60px`.
- Centered `

` (weight 500, `clamp(34px,4vw,52px)`, white, `letterSpacing -0.02em`, `lineHeight 1.1`, `textShadow 0 2px 20px rgba(0,0,0,0.35)`): "Real wonders.\
Real worlds."
- Centered `

` (weight 500, 17px, `maxWidth 420px`, white, `textShadow 0 2px 16px rgba(0,0,0,0.3)`, `marginTop 16px`): "See how Auragate helps others, and find out what it can do for you."
- Below: `` with these 7 testimonial quotes (in order):
  1. "It is amazing to see and feel the worlds I am stepping into each day."
  2. "I have been feeling much more alive inside these living worlds, even on the long days."
  3. "My wonder has been growing so fast that it is hard to believe the difference. Auragate gave me exactly the vision I needed."
  4. "The first two scenes felt alive. I tried everything we dreamed up and it worked."
  5. "The wonder of it all really moved me, it even brought a tear to my eyes every time."
  6. "I finally feel immersed, like the worlds were built just for me."
  7. "Stepping into it was effortless and the worlds have been unlike anything I dreamt."

### ArcCardCarousel (the signature component)
A fanned arc of cards centered on screen. State `active` starts at `floor(total/2)`. Constants (desktop / mobile): `cardW 300/230`, `cardH 420/320`, `stepX 295/170`, `dropY 52/34`, `tilt 8/7`, `containerH 560/460`. Container `position: relative; width: 100%; height: containerH`.

For each card compute signed position `pos` relative to `active` wrapped into `[-half, +half]`; `abs = |pos|`; `isCenter = pos===0`. 
- **Transform:** `translateX(posstepX) translateY(absdropY + (isCenter ? 30 : 0)) rotate(postilt deg)` — this creates the downward-curving arc with outer cards dropped and rotated. (mobile center bump = 22.)
- `opacity`: center `1`, else `max(0, 0.6 - (abs-1)0.2)`. `zIndex: 100 - abs`. `pointerEvents: isCenter ? 'auto' : 'none'`. `transition: transform 0.55s cubic-bezier(0.22,1,0.36,1), opacity 0.55s ease`.
- **Card face:** `borderRadius 28px` (22 mobile). 
  - **Center card:** solid `background: rgb(247,251,255)`, `border 1px solid rgba(255,255,255,0.6)`, no backdrop filter, and `boxShadow: '0 8px 24px rgba(0,0,0,0.08), 0 0 50px rgba(255,255,255,0.55), 0 0 90px rgba(255,255,255,0.35)'` (soft dark + layered white glow). Quote text color `#2c2420`.
  - **Inactive cards:** frosted glass — `background: linear-gradient(135deg, rgba(255,255,255,0.42) 0%, rgba(255,255,255,0.24) 100%)`, `backdropFilter: blur(18px) saturate(140%)` (+ `-webkit-`), `border 1px solid rgba(255,255,255,0.28)`, `boxShadow: 'inset 0 1px 1px rgba(255,255,255,0.45)'` (inset highlight only, no drop shadow). Quote text `rgba(255,255,255,0.85)`.
  - Quote `

`: Helvetica Now Display weight 500, 17px (15 mobile), `lineHeight 1.5`, `letterSpacing -0.01em`, wrapped in typographic quotes `“…”`, centered, card uses flex center.
- **Nav buttons** (absolute, `bottom: -40px`, centered, `gap 10px`): two round 46px (42px mobile) buttons. Prev (`dir -1`): `background rgba(255,255,255,0.2)`, no shadow, white chevron-left SVG with a glowing `drop-shadow` filter (`rgba(255,255,255,0.7) 0 0 6px` + `rgba(255,255,255,0.4) 0 0 14px`). Next (`dir 1`): `background rgba(255,255,255,0.9)`, `boxShadow 0 6px 18px rgba(0,0,0,0.18)`, dark `#2c2420` chevron-right. Clicking advances `active` by `±1` with modulo wrap.

### Footer
`position: relative`, padding `160px 44px 52px` (`120px 22px 40px` mobile). CSS grid: desktop `1.4fr 1fr 1fr 1fr`, mobile `1fr 1fr` (`gap 40px` / `32px 20px`), `maxWidth 1280px`, centered. First cell (full-width on mobile) = `` + a `rgba(255,255,255,0.55)` 12px line "© 2026 Auragate". Then three columns:
- **Explore:** How it works, Features
- **Contact:** X (Twitter), hello@auragate.com
- **Legal:** Privacy Policy, Terms of Service

Each column: a `rgba(255,255,255,0.55)` weight-500 13px title (`marginBottom 18px`), then a `gap 12px` list of white weight-500 14px links (`textDecoration none`, hover `opacity 0.65`).

### Responsiveness
Everything keys off the `isMobile` boolean (767px breakpoint): reduced paddings, font clamps, smaller carousel constants, Column 2 of the hero hidden, footer grid collapses to 2 columns with the brand cell spanning full width.

Behavior summary
On load, the user sees the portal image full-screen with the hero copy at the bottom. Mouse movement gently parallaxes both layers in opposite directions. Scrolling through the 160vh pinned track zooms the portal in to 7.5× while the world background scales to 1.18×; the hero copy fades out first (by 22%), then the portal fades out (66%→88%), revealing the cloud world and the "Real wonders" testimonial carousel section, ending in the footer.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "VEX Ventures"
template_id: "19aa7b16-bd0c-4ee1-a981-4abe63836ba4"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 VEX Ventures

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `19aa7b16-bd0c-4ee1-a981-4abe63836ba4`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero Section

### 🖼 Прев'ю:
![VEX Ventures](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/d8c9613b-727d-4ec2-8c14-1cb688fb1c69.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Recreate this hero section exactly. Here are the complete specifications:

Video Background:

Full-screen background video, absolutely positioned, covering the entire viewport (object-cover)
Video URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4
Autoplay, loop, muted, playsInline
NO dark overlay, NO gradient overlay, NO semi-transparent layer on top of the video. The video plays raw with no dimming whatsoever.
Typography (CRITICAL - must be applied globally):

Import the Google Font Inter via a <link> tag in index.html:

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
Set the body font-family in CSS to: 'Inter', sans-serif
Apply -webkit-font-smoothing: antialiased and -moz-osx-font-smoothing: grayscale on the body
Also extend the Tailwind config to set fontFamily: { sans: ['Inter', 'sans-serif'] } so all Tailwind font-sans usage picks up Inter automatically
Navbar:

Wrapped in horizontal page padding: px-6 md:px-12 lg:px-16 with pt-6 top padding
The navbar bar itself uses the .liquid-glass class and has rounded-xl, px-4 py-2, flex layout with items-center justify-between
Left: Logo text "VEX" - text-2xl font-semibold tracking-tight
Center (hidden on mobile, visible md+): Links "Story", "Investing", "Building", "Advisory" - text-sm, gap-8, hover transitions to gray-300
Right: "Start a Chat" button - bg-white text-black px-6 py-2 rounded-lg text-sm font-medium, hover to gray-100
Hero Content (Bottom of viewport):

Container: same horizontal padding as navbar, flex column filling remaining height, content pushed to bottom with flex-1 flex flex-col justify-end, bottom padding pb-12 lg:pb-16
On large screens: 2-column grid (lg:grid lg:grid-cols-2 lg:items-end)
Left Column - Main content:

Heading: "Shaping tomorrow\nwith vision and action." (literal line break between "tomorrow" and "with")

Responsive sizes: text-4xl md:text-5xl lg:text-6xl xl:text-7xl
font-normal, mb-4
Inline style: letterSpacing: '-0.04em'
Character-by-character entrance animation: Each character starts at opacity: 0 and translateX(-18px), then transitions to opacity: 1 and translateX(0). Each character gets a staggered delay calculated as: (lineIndex * lineLength * charDelay) + (charIndex * charDelay) where charDelay = 30ms. The whole animation starts after 200ms initial delay. Each character transition is 500ms.
Spaces render as \u00A0 (non-breaking space)
Subheading: "We back visionaries and craft ventures that define what comes next."

text-base md:text-lg text-gray-300 mb-5
Fade-in animation: starts at 800ms delay, 1000ms duration
Buttons row: flex-wrap with gap-4

"Start a Chat" - bg-white text-black px-8 py-3 rounded-lg font-medium
"Explore Now" - liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium, hover transitions to white bg + black text
Fade-in animation: starts at 1200ms delay, 1000ms duration
Right Column - Tag:

Aligned to bottom-right on large screens (flex items-end justify-start lg:justify-end)
Glass card: liquid-glass border border-white/20 px-6 py-3 rounded-xl
Text: "Investing. Building. Advisory." - text-lg md:text-xl lg:text-2xl font-light
Fade-in animation: starts at 1400ms delay, 1000ms duration
Liquid Glass CSS (place in global CSS):


.liquid-glass {
  background: rgba(0, 0, 0, 0.4);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.1) 80%, rgba(255,255,255,0.3) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
FadeIn component: A wrapper that starts with opacity: 0 and transitions to opacity: 1 after a configurable delay (ms) using a setTimeout + React state. Transition duration is also configurable. Uses inline transitionDuration style and Tailwind's transition-opacity class.

AnimatedHeading component: Splits text by \n into lines, then each line into individual characters. Each character is an inline-block <span> with CSS transitions on opacity and transform (translateX). Animation triggers via React state after the initial delay.

Color scheme: Black background, white text, gray-300 for secondary text, white/20 for borders. No purple, no indigo.

Stack: React + TypeScript, Tailwind CSS, Vite. No extra UI libraries needed. Icons from lucide-react if needed (none currently used in the hero).
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Luxury Real Estate"
template_id: "1a48eb1a-0c1f-453c-b50d-127ac7011f50"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Luxury Real Estate

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `1a48eb1a-0c1f-453c-b50d-127ac7011f50`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Luxury Real Estate](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/d4c9ed29-e22a-4a7a-bed7-bfad93d7cb0a.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page React + TypeScript + Tailwind CSS + Vite landing page for a luxury real estate brand named "Velar.". Use only `lucide-react` for icons. The app is in `src/App.tsx`. Use the exact specifications below.

Global Setup

- Page background: `#f5f0ea` (warm off-white).
- Body wrapper: `overflow-x: clip`.
- Fonts (loaded via `@import` inside an inline `<style>` block):
  - Primary: `Syne` weights 400, 700, 800, 900 from Google Fonts.
  - Secondary: `Inter` weights 300, 400, 500, 600 from Google Fonts.
- Constants:
  - `GRASS_GREEN = '#213138'` (deep teal — used for preloader background and default logo color).
  - `FULL_TEXT = 'Velar.'`
  - `HOUSE_IMG = 'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780471903/building_bzziky.png'`
  - `BG_IMG = 'https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260603_073200_7082add5-f1f8-4873-8696-d6f78a44089b.png&w=1920&q=85`
- Gallery videos (5, in order):
  1. `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260528_154759_4cdc8175-8261-497c-b688-9477c76545d4.mp4`
  2. `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260528_154751_39b1b9bb-2708-4211-b6a2-d39f93309e52.mp4`
  3. `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260528_154737_eba7900c-0313-483c-a30a-632c747ccc42.mp4`
  4. `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260602_144009_4348fe33-f885-4345-8e92-3fe1c2625d32.mp4`
  5. `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260602_145337_e44eaa8c-6bb1-4a6e-a70f-ed0231cbaccb.mp4`

Section 1 — Preloader / Intro Overlay

- Fixed full-viewport overlay (`z-index: 100`) filled with `#213138`, centered flex.
- Renders an animated typewriter of the word `Velar.` in Syne, font-size `2.6rem`, color white, letter-spacing `-0.02em`. Letters use weight 700 except `.` which is weight 900.
- A blinking white cursor (3px × 1.1em rounded bar, animation `blink 0.7s step-end infinite` toggling opacity 0/1) follows the last typed letter.
- Timings (using `setTimeout`):
  - `CHAR_INTERVAL = 140ms`, `TYPE_START = 600ms`.
  - Reveal letters one at a time at `TYPE_START + i * CHAR_INTERVAL`.
  - `LIFT_AT = TYPE_START + 6 * CHAR_INTERVAL + 700ms`.
  - Hide cursor at `LIFT_AT − 150ms`.
  - Start "lifting" the overlay upward at `LIFT_AT`: `transform: translateY(-100%)` with transition `transform 1.5s cubic-bezier(0.45, 0, 0.15, 1)`.
  - At `LIFT_AT + 1300ms`, fade in the hero text (`opacity 0 → 1`, `translateY(-28px) → 0`, transition `0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.1s`).
  - At `LIFT_AT + 2100ms`, set `liftDone` true and disable the overlay's transition (so it stays parked off-screen).

Section 2 — Fixed Navigation

- Fixed top nav `z-50`, padding `px-6 md:px-10 lg:px-16`, `py-5 md:py-6`, flex justify-between.
- Left: word `Velar.` in Syne, `text-xl`, weight 700 for letters and 900 for `.`. Color = `navColor` (see scroll behavior).
- Right: hamburger toggle button. Two stacked 28px-wide × 1px lines, top one shrinks to `w-5` on hover. When open, swap to a Lucide `X` icon, size 24.
- Scroll behavior: track whether any "dark section" (refs to Section 4 and Section 5) currently overlaps the viewport top (`rect.top <= 0 && rect.bottom > 0`). If so, `navOnDark = true` and `navColor = '#ffffff'`. Otherwise `navColor = '#213138'`. Color transitions: `color 0.35s ease`.
- Mobile menu: when open, full-screen `#f5f0ea` overlay (`z-40`) centered with 4 vertically stacked links: `Residences`, `Story`, `Listings`, `Inquire`. Each link is Syne, `text-4xl`, `font-light`, `tracking-widest`, uppercase, black with hover `text-gray-500`. Click closes menu.

Section 3 — Hero

- `<section>` `position: relative`, `min-height: 100vh`, `overflow: visible`.
- Background: `BG_IMG` as `background-image`, `background-size: cover`, `background-position: center center`, `background-repeat: no-repeat`.
- Hero text block (`.hero-text-block`) inside, `z-index: 10`, hidden initially, fades+slides in (see preloader timings).
- Top row (`.hero-heading-top`, padded `px-6 md:px-10 lg:px-16`, flex `items-end justify-between`, `margin-bottom: -0.04em`):
  - Left: `LIVE IN` — Syne 800, uppercase, black, `letter-spacing: -0.03em`, `line-height: 1`. Size via CSS class `.hero-own-the`.
  - Right (desktop only ≥1024px, `.hero-subtitle-desktop`): two-line right-aligned paragraph in Syne 700, `clamp(10px, 0.95vw, 14px)`, max-width 300px, opacity 0.7, line-height 1.6, margin-bottom `0.2em`, letter-spacing `0.02em`:
    > Stately homes built with vision,
    > scope, and architectural finesse.
- Headline row (wrapped in `overflow: hidden`):
  - `IRREPLACEABLE` — Syne 800, uppercase, black, `letter-spacing: -0.03em`, padded `px-6 md:px-10 lg:px-16`. Size via `.hero-extraordinary`.
- Mobile/tablet subtitle (`.hero-subtitle-mobile`, padded `px-6`), Syne 600, `clamp(12px, 3vw, 15px)`, opacity 0.65, margin-top `0.9em`:
  > Premium real estate with vision,
  > depth, and architectural clarity.

Hero Responsive Type Sizes

```css
@media (max-width: 639px) {
  .hero-subtitle-desktop { display: none !important; }
  .hero-subtitle-mobile  { display: block !important; }
  .hero-text-block { padding-top: 90px !important; }
  .hero-heading-top { justify-content: flex-start !important; }
  .hero-own-the { font-size: 7.5vw !important; }
  .hero-extraordinary { font-size: 14.5vw !important; white-space: normal !important; word-break: break-word !important; line-height: 0.9 !important; }
}
@media (min-width: 640px) and (max-width: 1023px) {
  .hero-subtitle-desktop { display: none !important; }
  .hero-subtitle-mobile  { display: block !important; }
  .hero-text-block { padding-top: 110px !important; }
  .hero-heading-top { justify-content: flex-start !important; }
  .hero-own-the { font-size: 5.5vw !important; }
  .hero-extraordinary { font-size: 11vw !important; white-space: normal !important; word-break: break-word !important; line-height: 0.9 !important; }
}
@media (min-width: 1024px) {
  .hero-subtitle-desktop { display: block !important; }
  .hero-subtitle-mobile  { display: none !important; }
  .hero-text-block { padding-top: calc(28vh - 50px) !important; }
  .hero-own-the { font-size: 3vw !important; }
  .hero-extraordinary { font-size: clamp(52px, 6.5vw, 9vw) !important; white-space: nowrap !important; line-height: 0.88 !important; }
}
```

Section 4 — Scroll-Driven House Animation (the centerpiece)

- A `position: fixed` wrapper at `z-index: 22`, `pointer-events: none`, `will-change: transform`, default `bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; min-width: 1400px;`.
- Inside, an inner div performs the initial "rise from below" entrance: starts at `translateY(102vh)`, transitions to `translateY(0)` with `transform 1.5s cubic-bezier(0.45, 0, 0.15, 1) 0.4s`, triggered when `lifting` becomes true. Once `liftDone` true the transition is removed so the scroll handler can take over.
- Renders `` at width 100%, aria-hidden.
- After `liftDone`, a scroll/resize listener (`updateHousePosition`) computes:
  - `baseW = max(window.innerWidth, 1400)`.
  - `triggerPoint = -(heroH  0.30)` — animation starts when 30% of hero has scrolled off.
  - `endPoint = heroRect.top - (darkRect.bottom - vh)` — ends when the bottom of Section 5 reaches viewport bottom.
  - `progress = clamp((heroRect.top − triggerPoint) / (endPoint − triggerPoint), 0, 1)`.
  - `t = smoothstep(smoothstep(progress))` where `smoothstep(t) = tt(3−2t)` (applied twice).
  - `startX = (vw − baseW) / 2`, `startY = vh − imgH` (bottom-centered).
  - `finalScale = 1.45`, `finalX = (vw − baseW  finalScale) / 2` (bottom-centered), `mobileOffset = vw < 1024 ? −250 : 4`, `finalY = darkRect.bottom − imgH * finalScale + 500 + mobileOffset`.
  - Interpolates `currentX`, `currentY`, `currentScale` linearly via `t`.
- At `progress <= 0` resets to resting (bottom-centered, scale 1). Otherwise sets `top: 0; left: 0; transform: translate(currentX, currentY) scale(currentScale); transform-origin: top left;`.

## Section 5 — Dark Statement + Stats (sticky)

- Outer wrapper: `position: relative; height: 200vh; z-index: 20`.
- Inner `

` (`s2-section`): `position: sticky; top: 0; height: 100vh; background: #1a1a1a; overflow: hidden`. Above it is a tiny `4vh` `#1a1a1a` scroll spacer.
- Content wrapper `.s2-content`: flex column, padding `px-6 md:px-10 lg:px-16`, `padding-top: clamp(30px, 4vw, 60px)`, `padding-bottom: clamp(60px, 8vw, 120px)`.
- Statement text (`.s2-statement`), Inter 300, color `#e8e4df`, letter-spacing `-0.02em`, `line-height: 1.35`, `white-space: nowrap`, font-size `clamp(22px, 2.6vw, 42px)`. Wrapper has `max-width: 1200px`, centered, `padding-left: 25%`. Lines (with hard `
`s):
  > Every estate we present is hand-chosen
  > through a frame of permanence, refinement,
  > and timeless detail. Standards are not
  > a flourish. It is our discipline.
- Stats row (`.s2-stats-row`): same max-width/centered/padding-left 25%, `margin-top: clamp(48px, 6vw, 80px)`. Three columns in a flex row, each `flex:1`, with a left border (`1px solid rgba(255,255,255,0.2)`) between items and `padding-left: clamp(20px, 2.5vw, 40px)` on items 2–3:
  1. `120+` — `Portfolio Holdings`
  2. `12` — `Global Locations`
  3. `98%` — `Patron Loyalty Rate`
  - Numbers: Inter 300, white, font-size `clamp(36px, 4.5vw, 72px)`, line-height 1.1. Use a `CountUp` component that, when the element first crosses 30% into the viewport (IntersectionObserver), animates from 0 to `end` over 2000ms with easing `1 - (1 - t)^3`, rendering `Math.round(eased * end) + suffix`.
  - Labels: Inter 400, `rgba(255,255,255,0.6)`, font-size `clamp(12px, 1.1vw, 16px)`, `margin-top: clamp(4px, 0.5vw, 8px)`, letter-spacing `0.01em`.
- Tablet/mobile rules:
  - `≤767px`: remove the 25% left padding entirely (set to 0).
  - `768–1023px`: reduce padding-left to 15%, set `min-height: 70vh` and adjust paddings.

## Section 6 — Hover-Expand Gallery (slides over Section 5)

- `

` (`s3-gallery-section`) `position: relative; z-index: 25; margin-top: -100vh; background: #1a1a1a; height: 100vh; overflow: hidden`. This makes it slide up over Section 5 as the user scrolls.
- Background ticker (`.s3-ticker-wrap`): absolutely positioned `inset:0`, flex center, `overflow: hidden`, `z-index: 0`, `pointer-events: none`. Contains a `.ticker-track` with two copies of a giant repeating string:
  > `Velar.   Velar.   Velar.   Velar.   Velar.   Velar.   Velar.   Velar.  ` (with ` ` separators)
  - Each span: Syne 800, `clamp(100px, 14vw, 220px)`, white, `white-space: nowrap`, letter-spacing `-0.02em`, `user-select: none`, `padding-right: 0.3em`. (The ticker can also be animated with a horizontal scroll keyframe — left as a static layered word-mark behind the gallery here.)
- Gallery content (`.s3-gallery-content`): z-index 1, flex center, full height, padding `clamp(24px, 4vw, 60px)`.
- Row (`.gallery-expand-row`): flex with `gap:6px`, height 70%, max-width 1200px. Each item (`.gallery-expand-item`): `flex:1 1 0%`, full height, `border-radius:12px`, `overflow:hidden`, `cursor:pointer`, transition `flex 0.5s cubic-bezier(0.4, 0, 0.2, 1)`. On hover, the hovered item grows to `flex: 4`, others shrink — classic accordion expand.
- Each item contains the corresponding video (autoplay, loop, muted, playsInline) covering the tile (`object-fit: cover`).

### Gallery Mobile/Tablet Rules (≤1023px)

```css
.s3-gallery-section { height: auto; min-height: 100vh; overflow: visible; }
.s3-ticker-wrap { position: sticky; top: 0; height: 100vh; width: 100%; margin-bottom: -100vh; }
.s3-gallery-content { height: auto; align-items: flex-start; padding: 80px 16px 60px; }
.gallery-expand-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; height: auto; width: 100%; max-width: 700px; }
.gallery-expand-item { flex: none; height: auto; aspect-ratio: 4/5; border-radius: 10px; transition: transform 0.3s ease; }
.gallery-expand-item:hover { flex: none; transform: scale(1.02); }
.gallery-expand-item:last-child:nth-child(odd) { grid-column: 1 / -1; max-width: calc(50% - 4px); justify-self: center; }
@media (max-width: 479px) {
  .s3-gallery-content { padding: 60px 12px 48px; }
  .gallery-expand-row { gap: 6px; }
}
```

## Behavior Recap

- Preloader types `Velar.` then slides up out of view, simultaneously revealing the hero text and rising the house image from below the viewport.
- The house image stays bottom-centered behind the hero text on initial load.
- As the user scrolls past 30% of the hero, the house begins drifting upward and scaling up to 1.45×, remaining horizontally centered, while pinning toward the bottom of the dark statement section.
- The nav logo color cross-fades to white whenever a dark section sits at the viewport top.
- Section 5 stays sticky as Section 6 (gallery) slides up over it thanks to negative `margin-top: -100vh` and higher `z-index`.
- Stat numbers count up once on scroll into view.
- Gallery tiles accordion-expand on hover (desktop) or 2-column grid (mobile/tablet).

## Tech Notes

- Use only `react`, `react-dom`, `lucide-react`, Tailwind, and Vite. No additional libraries.
- All animation logic lives inside a single `App.tsx` using `useState`, `useEffect`, `useRef`, `useCallback`, and `IntersectionObserver`.
- Use Supabase if any persistence is later needed; this page itself has no data layer.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "SkyElite Private Jets"
template_id: "49691aca-ab7d-42fc-96bc-8aa3edecd16c"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 SkyElite Private Jets

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `49691aca-ab7d-42fc-96bc-8aa3edecd16c`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![SkyElite Private Jets](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/45637c57-b277-47c3-a7c5-c7b6ec886951.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a premium private jet landing page hero section with the following specifications:

Video Background:
Use this exact CloudFront video URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_091828_e240eb17-6edc-4129-ad9d-98678e3fd238.mp4
Video should autoplay, be muted, loop continuously, and include playsInline attribute
Video covers entire viewport (100vh) using object-cover

Navigation Bar:
Brand name "SkyElite" on the left (text-2xl, font-semibold, text-gray-900)
Desktop menu items (hidden on mobile, visible md:flex): Start, Story, Rates, Benefits, FAQ
Navigation links in gray-900 with hover:text-gray-700 transition
Mobile hamburger menu button using Lucide React icons (Menu/X)
Mobile menu appears as dropdown with white/95 opacity background, backdrop blur, rounded corners, shadow
Max width 7xl, centered with px-8 py-6

Hero Content (centered, -mt-80 to pull up):
Small uppercase label: "PRIVATE JETS" (text-sm, font-semibold, gray-600, tracking-wider, mb-4)
Large two-line heading with overlapping effect:
Line 1: "Premium." (text-6xl md:text-7xl lg:text-8xl, font-normal, text-gray-500, leading-none, tracking-tighter)
Line 2: "Accessible." (same size, color: #202A36, negative margin-top: -12px for overlap)
Subtitle: "Your dedication deserves recognition." (text-lg md:text-xl, gray-600, mb-6, max-w-2xl)
Two call-to-action buttons (gap-4, centered):
"Discover" button: px-4 py-2, rounded-full, bg-gray-300, text-gray-800, font-medium, hover:bg-gray-400
"Book Now" button: px-4 py-2, rounded-full, white text, bg-color #202A36, hover color #1a2229 with smooth transitions

Typography:
Use Inter font (import from Google Fonts: 400, 500, 600, 700 weights)
Apply to entire body via CSS

Technical Setup:
React with TypeScript
Tailwind CSS for styling
Lucide React for icons
useState hook for mobile menu toggle
Full screen height container (h-screen)
Responsive breakpoints: mobile-first, md, lg
All transitions use transition-colors class

Layout Structure:
Outer container: min-h-screen, bg-gray-50
Hero section: relative, h-screen, overflow-hidden
Content wrapper: relative, h-full, flex flex-col
Main content area: flex-1, flex items-center justify-center

Make it clean, modern, and premium-looking with smooth interactions.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Mythic Naturecore"
template_id: "eaf7a19d-f5b4-47a4-a186-7bfad37c2f8e"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Mythic Naturecore

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `eaf7a19d-f5b4-47a4-a186-7bfad37c2f8e`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Mythic Naturecore](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5b009982-e059-4499-9b79-029880ba33ac.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Recreate a high-fidelity, premium interactive landing page named "Reverie" using React, TypeScript, and a combination of Tailwind CSS and inline styles. The project must have a smooth, hardware-accelerated scroll-linked animation system, 3D/parallax mouse-tracking effects, responsive layouts, and elegant micro-animations.

---

1. Typography & Global Styles

- Fonts:
  - Load the following Google Fonts:
    - Headers: `'Viaoda Libre', serif` (elegant serif font).
    - Body, nav links, and captions: `'Imprima', sans-serif` (clean, sleek sans-serif font).
- Global Reset & Base CSS:
  - `html, body { margin: 0; padding: 0; background: #0a0608; scroll-behavior: auto; }`
  - Body font should default to `'Imprima', sans-serif`.
  - Add `scrollbar-gutter: stable;` to the `html` tag to prevent layout shifts.
  - Include an animation utility:
    ```css
    @keyframes bobUp {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-6px); }
    }
    ```

---

2. Assets Asset Mapping

Define these exact asset constants at the top of the file:
```typescript
const PORTAL_BG = 'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779974947/portal_bg_mu60k9.png';
const CURTAIN_LEFT = 'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975070/curtain_left_cdht6q.png';
const CURTAIN_RIGHT = 'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975071/curtain_right_a9bn3i.png';
const WORLD_BG = 'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975077/world_bg_jzzcn1.jpg';

// The cards MUST remain in this exact order (Card 3, Card 1, Card 2)
const CARD_IMAGES = [
  'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975070/card_3_nbwm25.jpg',
  'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975070/card_2_wr6al6.jpg', // Representing Card 1
  'https://res.cloudinary.com/dsdhxhhqh/image/upload/v1779975070/card_1_jz8otj.jpg', // Representing Card 2
];
```

---

3. State Management & Mathematical Helpers

- Math Utilities:
  - Easing curve: `easeInOut(t) = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t`
  - Linear Interpolation: `lerp(a, b, t) = a + (b - a) * t`
  - Constraint: `clamp(val, min, max) = Math.max(min, Math.min(max, val))`
- Parallax Magnitudes:
  - `MAG.world = 6`, `MAG.portal = 7`, `MAG.curtainL = 14`, `MAG.curtainR = 14`
- Hook for Responsiveness:
  - Implement a `useIsMobile()` hook responding to media query max-width of `767px` to dynamically update layouts.
- Scroll Tracking:
  - The page height must be exactly `480vh`. Inside, a single sticky container spans `100vh`.
  - Calculate normalized `scrollProgress` from `0` to `1` by reading window scroll position relative to the scrollable height.
- Smooth Mouse Tracking (Parallax):
  - Normalize coordinates `rx`, `ry` between `-1` and `1` relative to the center of the viewport.
  - Implement a `requestAnimationFrame` render loop (`tick`) to smoothly interpolate current position towards target cursor position (lerp step speed: `0.07`) to eliminate frame-rate stutters.
- Entrance Animation Delays:
  - On mount, transition curtains open after `100ms`, fade UI in after `600ms`. Disable entry CSS transitions after `2200ms` so mouse movement doesn't experience lag or delay.

---

4. Animation Timelines (Scroll & Mouse Parallax)

Apply these precise styling updates in the render loop on every frame:
1. World Layer (`WORLD_BG`):
   - Scale: Lerps from `1` (at start) to `1.18` (at maximum scroll).
   - Parallax: `transform = scale(${scale}) translate3d(${rx * 6}px, ${ry * 6}px, 0)`
2. Portal Frame (`PORTAL_BG`):
   - Scale: Lerps from `1` to `7.5` (creating an immersive zoom-through effect).
   - Origin: `52% 38%`
   - Opacity: Starts at `1`, fades out after `65%` scroll: `clamp(1 - (scrollProgress - 0.65) / 0.2, 0, 1)`
   - Parallax: `transform = scale(${scale}) translate3d(${rx * 7}px, ${ry * 7}px, 0)`
3. Curtain Left (`CURTAIN_LEFT`):
   - Initial Opening Offset: `62%` shift left.
   - Scroll Offset: Moves further leftward up to `150%` as eased progress goes `0` to `1`.
   - Curtain Scroll Scale: Lerps from `1` to `1.3`.
   - Parallax & GPU Layer: `transform = translateX(calc(-${totalShift}% + ${rx * 14}px)) translateY(${ry * 14 * 0.3}px) scale(${curtainScrollScale}) translateZ(0)`
4. Curtain Right (`CURTAIN_RIGHT`):
   - Symmetrically mirrors Curtain Left.
   - Parallax & GPU Layer: `transform = translateX(calc(${totalShift}% + ${rx * 14}px)) translateY(${ry * 14 * 0.3}px) scale(${curtainScrollScale}) translateZ(0)`

---

5. Layout & Components

Navigation Bar
- Position: Absolute at the top, `zIndex: 50`. Responsive padding: `18px 20px` (mobile), `22px 48px` (desktop).
- Desktop (>=768px): Split navigation.
  - Left side: Links `Worlds`, `Atelier`, `Immersions`.
  - Center: SVG Star Logo (clean star shape in path `M14 2l2.09 6.42H23l-5.45 ...` inside a `28x28` viewport).
  - Right side: Links `Craft`, `Codex`, `Connect`.
- Mobile (<768px): Centered star logo with an `Explore` link on the left and a `Connect` link on the right.
- Link Styling: uppercase, `12px`, letter spacing `0.12em`, white color with `0.9` opacity, no text decoration.

Scene 1: Hero Section (Entrance)
- Opacity: Fades out smoothly on scroll: `clamp(1 - scrollProgress / 0.22, 0, 1)`.
- Entrance Transition: Slide upward by `20px` on mount with opacity transition `0.9s ease` delayed by `300ms`.
- Responsive Layout:
  - Mobile (<768px): Center-aligned vertical column. Text is dark brown (`#3b1a0a`). Heading: `FALL › INTO REVERIE` (Viaoda Libre). Subheading paragraph (max-width `280px`). Below it, displays a single card with image `CARD_IMAGES[0]`, showing a rounded white play button icon and "View Reel".
  - Tablet (768px - 1099px): Center-aligned column. Text is dark brown (`#3b1a0a`). Headline and paragraph (max-width `400px`). Shows all 3 cards in a horizontal row:
    - Card 3: Image `CARD_IMAGES[0]`, Play button + "View Reel"
    - Card 1: Image `CARD_IMAGES[1]`, "32 World Patrons" in large elegant text
    - Card 2: Image `CARD_IMAGES[2]`, Play button + "View Reel"
  - Desktop (>=1100px): Split-screen horizontal layout. Text is white.
    - Left Container: Aligned to the left (top `46%`, left `60px`). Title: `FALL › INTO REVERIE` (Viaoda Libre). Subheading paragraph. Max-width `440px`.
    - Right Container: Aligned to the right (top `50%`, right `40px`). Row of 3 card containers (`158px x 158px`) with rounded corners (`28px`), bottom linear gradient, glassmorphic bottom blur (`backdropFilter: 'blur(6px)'`), play icon buttons or patron metrics overlay.
- Card Interactive Styling:
  - Backdrop blur filter on bottom labels: `backdropFilter: 'blur(6px)'`, linear gradient to top `rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.18) 60%, transparent 100%`.
- Slider Dots (Bottom Left):
  - Absolutely positioned at bottom left (`60px` desktop, centered mobile).
  - Renders 4 horizontal pill indicators: first indicator is wide (`28px`), other three are thin (`14px`), colored in white with opacities.
- Scroll Cue (Descend):
  - Absolutely positioned at `bottom: 36px`, centered horizontally. Hidden on mobile.
  - Text: uppercase "Descend" in `10px`, letter-spacing `0.22em`, color `rgba(255,255,255,0.6)`.
  - Icon: A chevron SVG surrounded by a `34px x 34px` round circular border animated with the `bobUp 1.8s ease-in-out infinite` bounce animation.

Scene 2: Call to Action (Forge Beyond)
- Opacity: Fades in on scroll: `clamp((scrollProgress - 0.68) / 0.16, 0, 1)`.
- Layout: Centered vertical flex container (`zIndex: 46`), active only when opacity is visible.
- Content:
  - Centered text wrapper.
  - Heading: `FORGE BEYOND THE REAL` (Viaoda Libre, size clamp `38px` to `78px`, color `#ffffff`, letter spacing `0.03em`, line-height `1.05`, elegant text shadow `0 2px 20px rgba(0,0,0,0.4)`).
  - Paragraph: `Singular voyages to astonishing destinations, shaped for those who seek beauty beyond the ordinary and the known.` (Imprima, size `20px` desktop / `14px` mobile, max-width `480px` desktop / `260px` mobile, line-height `1.6`, color `rgba(255,255,255,0.82)`).
```
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Reveal Hero"
template_id: "0dc51e7c-7783-46b2-97b8-c01af61a0882"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Reveal Hero

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `0dc51e7c-7783-46b2-97b8-c01af61a0882`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Reveal Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5a9ac7c2-d5dc-439c-928b-aec36c99542e.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page React + TypeScript + Vite + Tailwind CSS project that recreates the following hero section exactly. Use `lucide-react` for icons. Do not install any other UI or animation libraries.

### Project setup

- React 18, TypeScript, Vite, Tailwind CSS.
- Dependencies: `react`, `react-dom`, `lucide-react`, `@supabase/supabase-js`.
- File `src/index.css` must be:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  font-family: 'Inter', sans-serif;
}
```

### Assets (use these URLs verbatim, do NOT download)

- `BG_IMAGE_1` = `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260512_012043_9764f2d0-5c6e-4faa-94a6-a8253df08c5e.png&w=1280&q=85`
- `BG_IMAGE_2` = `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260512_012949_6b24738e-6e5f-4b6f-93d7-5772f4d32285.png&w=1280&q=85`

### Constants

- `SPOTLIGHT_R = 260`
- `GRID_CELL = 48`

### Behavior / animations

1. **Grid background** — inline SVG, opacity 0.1, full-cover, absolutely positioned behind content. A `<pattern id="grid">` with `width=48`, `height=48`, `patternUnits="userSpaceOnUse"`, whose `x` and `y` are bound to a ref-driven `gridOffset`. Pattern contains a single `<path d="M 48 0 L 0 0 0 48" fill="none" stroke="#64748b" strokeWidth="0.6" />`. A `<rect width="100%" height="100%" fill="url(#grid)" />` fills it.
2. **Mouse tracking** — on `mousemove` store raw `{x, y}` in a ref. A `requestAnimationFrame` loop eases a `smooth` ref toward `mouse` with factor `0.1`. Using `smooth`, compute normalized offset `cx = (smooth.x - rect.left) / rect.width - 0.5` (same for y), then ease `gridOffset` toward `cx * 16` / `cy * 16` with factor `0.06`. Update a `cursorPos` state with the smoothed coords each frame.
3. **Reveal layer (spotlight)** — a hidden `<canvas>` sized to `window.innerWidth` × `window.innerHeight`. Each frame (in a `useEffect` that runs on every render of `RevealLayer`):
   - Clear canvas.
   - Create `createRadialGradient(cursorX, cursorY, 0, cursorX, cursorY, 260)` with stops:
     - `0` → `rgba(255,255,255,1)`
     - `0.4` → `rgba(255,255,255,1)`
     - `0.6` → `rgba(255,255,255,0.75)`
     - `0.75` → `rgba(255,255,255,0.4)`
     - `0.88` → `rgba(255,255,255,0.12)`
     - `1` → `rgba(255,255,255,0)`
   - Draw a full circle `arc(cursorX, cursorY, 260, 0, 2π)` filled with that gradient.
   - Convert canvas to `toDataURL()` and apply as `maskImage` / `webkitMaskImage` on a `<div>` sized `100% 100%` whose background is `BG_IMAGE_2` (`bg-center bg-cover bg-no-repeat`). Mask size `100% 100%`.
4. Resize listener resets canvas width/height to `window.innerWidth` / `window.innerHeight`.

### Layout / JSX structure

Top-level `App`:

- Root `<div className="min-h-screen bg-white" style={{ fontFamily: 'Inter, sans-serif' }}>`.
- Fixed nav: `<nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-5 sm:px-8 py-4 sm:py-5">`.

**Logo** (inline SVG, first child of nav, inside `<div className="flex items-center">`):

```html
<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 256 256" fill="none">
  <path d="M 256 64 L 256 128 L 192.5 128 L 160 95 L 128 64 L 96 95 L 63.5 128 L 64 128 L 128 192 L 128 256 L 64.5 256 L 32 223 L 0 192 L 0 64 L 64 0 L 192 0 Z M 256 192 L 256 256 L 192.5 256 L 160 223 L 128 192 L 128 128 L 192 128 Z" fill="#111111" />
</svg>
```

**Desktop pill nav** (hidden on mobile): `<div className="hidden md:flex absolute left-1/2 -translate-x-1/2 bg-gray-900 rounded-full px-2 py-1.5 items-center gap-1">` containing buttons in order:
- `Device` — active: `bg-white text-gray-900 text-sm font-medium px-4 py-1.5 rounded-full`
- `Real Stories`, `Science`, `Plans`, `Reach Us` — each: `text-gray-300 text-sm font-medium px-4 py-1.5 rounded-full hover:text-white transition-colors`

**Desktop CTA** (right): `<button className="hidden md:flex bg-gray-900 text-white text-sm font-medium px-5 py-2 rounded-full items-center gap-2 hover:bg-gray-700 transition-colors">` with green dot `<span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>` + text `Reserve Yours`.

**Mobile hamburger** (shown `md:hidden`): toggles `menuOpen` state; icon is lucide `Menu` (size 22) or `X` (size 22) when open; button classes `md:hidden text-gray-900 p-1`.

**Mobile dropdown** (when `menuOpen`): `fixed top-0 left-0 right-0 z-40 bg-white pt-16 pb-6 px-5 shadow-lg flex flex-col gap-1 md:hidden`, maps items `['Device','Real Stories','Science','Plans','Reach Us']` to `<button className="text-gray-800 text-base font-medium py-3 border-b border-gray-100 text-left hover:text-gray-500 transition-colors">`, then a `Reserve Yours` button: `mt-4 bg-gray-900 text-white text-sm font-medium px-5 py-3 rounded-full flex items-center gap-2 justify-center hover:bg-gray-700 transition-colors` with the green dot span.

**Hero section** (`<section>`): `relative w-full overflow-hidden` with inline `style={{ height: '100vh' }}`. Children in order:

1. The grid SVG described above (`opacity: 0.1`, `z-0`, pointer-events none, `absolute inset-0 w-full h-full`).
2. Base image div: `absolute inset-0 bg-center bg-cover bg-no-repeat z-10` with `backgroundImage: url('<BG_IMAGE_1>')`.
3. `<RevealLayer>` (hidden canvas + masked div with `BG_IMAGE_2`, `z-30`, pointer-events none).
4. Hero text block: `<div className="absolute bottom-12 sm:bottom-12 md:bottom-56 left-5 sm:left-8 md:left-12 max-w-[260px] sm:max-w-xs z-50">` containing:
   - `<p className="text-[10px] sm:text-[11px] font-semibold tracking-[0.18em] text-gray-600 uppercase mb-2 sm:mb-3">PureFlow One</p>`
   - `<h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 leading-tight mb-4 sm:mb-6">Clean Air, Clear<br />Mind. Anywhere.</h1>`
   - A `<div className="flex items-center gap-3 sm:gap-4">` with:
     - `<button className="bg-gray-900 text-white text-xs sm:text-sm font-medium px-4 sm:px-6 py-2 sm:py-2.5 rounded-full hover:bg-gray-700 transition-colors">Discover</button>`
     - `<button className="flex items-center gap-2 text-gray-700 text-xs sm:text-sm font-medium hover:text-gray-900 transition-colors">` containing lucide `<Play size={12} className="fill-gray-700" />` and text `View Specs`.

### Notes

- All icons from `lucide-react`: `Play`, `Menu`, `X`.
- Font: Inter (Google Fonts) weights 300–700.
- No purple/indigo colors; neutrals + `bg-green-400` status dot only.
- Responsive: tablet (`sm`) keeps hero text at the same bottom as mobile (`bottom-12`); only desktop (`md`+) raises it (`bottom-56`).
- Use `useRef` + `requestAnimationFrame` (no external animation libs). Canvas-based radial mask reveal must update each frame.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Cinematic Brand"
template_id: "00ec97f0-b8e4-42b7-ae22-7a29c3601764"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Cinematic Brand

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `00ec97f0-b8e4-42b7-ae22-7a29c3601764`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Cinematic Brand](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/4bdfcf4e-7a13-4baf-841c-430314d5a1a8.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-screen cinematic hero landing page for a brand called "VERTX". Use React, TypeScript, Vite, Tailwind CSS, Framer Motion, and Lucide React icons.

## Font

Use the custom font **"Quire Sans Pro"** loaded from this CDN in `index.html`:
```
https://db.onlinewebfonts.com/c/5a981c7d02abe9aec215dbe4606407e2?family=Quire+Sans+Pro
```
Set it as the default `sans` font family in `tailwind.config.js`:
```js
fontFamily: {
  sans: ['"Quire Sans Pro"', 'sans-serif'],
},
```

## Page Title
`Nexora — Beyond the Interface`

## Background Video

Use this CloudFront video URL as a full-screen looping background:
```
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260606_170109_f96e01a5-b0db-4274-b24d-8d97e99ec928.mp4
```
The `<video>` element should be `absolute inset-0`, `object-cover`, with attributes: `autoPlay`, `muted`, `loop`, `playsInline`, `preload="auto"`. Also use a `useRef` + `useEffect` to call `.play()` on mount as a fallback for autoplay.

## Navbar (fixed, top, z-50)

- Animates in from top using Framer Motion: `initial={{ y: -24, opacity: 0 }}`, `animate={{ y: 0, opacity: 1 }}`, `transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}`.
- Outer: `fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-5 sm:pt-4`.
- Inner container: `mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:h-16 sm:px-6`.
- **Logo (left):** Lucide `Hexagon` icon (strokeWidth 1.5, 24x24, white) + text "VERTX" (`text-[15px] font-semibold tracking-tight text-white sm:text-base`). The Hexagon rotates 30deg on hover via a `group` + `group-hover:rotate-[30deg]` with `transition-transform duration-300`.
- **Right side:** Two buttons:
  1. "Contact" -- ghost style: `rounded-full border border-white/15 bg-white/5 px-5 py-2 text-[13px] font-medium text-white/80 backdrop-blur-sm transition-all hover:border-white/30 hover:text-white hover:scale-105 active:scale-100`.
  2. "Sign Up" -- primary style with `btn-glow` class: `rounded-full bg-slate-950 px-5 py-2 text-[13px] font-medium text-white transition-transform hover:scale-105 active:scale-100`.

## Hero Content (centered, shifted up 50px)

The content wrapper: `relative z-10 flex min-h-screen flex-col items-center justify-center px-5 pt-20 text-center sm:px-6 sm:pt-24` with inline style `marginTop: '-50px'`.

### 1. Eyebrow text
Wrapped in a `FadeUp` component (delay=0, mb-4 sm:mb-6):
- A `<p>` with: `flex items-center gap-2 text-[10px] font-medium uppercase tracking-[0.25em] text-white/60 sm:gap-3 sm:text-xs md:text-sm md:tracking-[0.3em]`.
- Starts with a small horizontal line: `<span className="inline-block h-px w-4 bg-white/40 sm:w-6" />`.
- Text: **"The future is unfolding"**.

### 2. Main Heading (h1)
`max-w-4xl text-[1.75rem] font-medium leading-[1.15] tracking-tight text-white sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl`.
- Uses a `TypingEffect` component that splits the text into individual characters, each animated with Framer Motion (`initial={{ opacity: 0 }}`, `animate={{ opacity: 1 }}`, staggered with `delay: i * 0.045`, `duration: 0.15`). Words are kept as `inline-block` spans so they wrap naturally, with `&nbsp;` between words.
- Text: **"Innovation that reshapes the fabric of experience"**.

### 3. Subheading
Wrapped in `FadeUp` (delay=2.4, mt-4 sm:mt-6):
- `max-w-xs text-xs font-light leading-relaxed text-white/50 sm:max-w-xl sm:text-sm md:text-base lg:text-lg`.
- Text: **"We craft platforms where insight, power, and design converge -- giving rise to something the world hasn't seen."** (use an em dash).

### 4. Buttons row
Container: `mt-8 flex w-full max-w-sm flex-col items-center gap-3 sm:mt-10 sm:w-auto sm:max-w-none sm:flex-row sm:gap-5`. Stacks vertically on mobile, horizontal on sm+.

- **"Begin Now" button** (FadeUp delay=2.8): `btn-glow flex w-full items-center justify-center gap-2.5 rounded-full bg-slate-950 py-2.5 pl-6 pr-3 text-sm font-medium text-white transition-transform hover:scale-105 active:scale-100 sm:w-auto sm:gap-3 sm:py-3.5 sm:pl-10 sm:pr-5 sm:text-lg`. Contains a circular play icon on the right: a `<span>` styled as `flex h-7 w-7 items-center justify-center rounded-full border border-white/30 sm:h-9 sm:w-9` with a Lucide `Play` icon (`h-3 w-3 fill-current sm:h-4 sm:w-4`).

- **"Watch the story" button** (FadeUp delay=3.0): `w-full rounded-full border border-white/15 bg-white/5 px-6 py-2.5 text-sm font-medium text-white/80 backdrop-blur-sm transition-all hover:border-white/30 hover:text-white hover:scale-105 active:scale-100 sm:w-auto sm:px-10 sm:py-3.5 sm:text-lg`.

## FadeUp Component

A reusable animation wrapper using Framer Motion:
- Props: `children`, `className`, `delay` (default 0), `duration` (default 0.6), `y` (default 24).
- Uses `useInView` with `{ once: true }` to trigger only when scrolled into view.
- `initial={{ opacity: 0, y }}`, animates to `{ opacity: 1, y: 0 }` when in view.
- Easing: `[0.25, 0.46, 0.45, 0.94]`.

## TypingEffect Component

A character-by-character reveal animation:
- Props: `text`, `className`, `charDelay` (default 0.045).
- Uses `useInView` with `{ once: true }`.
- Splits text by spaces into words, then each word into characters. Each character is a `<motion.span>` with `initial={{ opacity: 0 }}`, `animate={{ opacity: 1 }}` (when in view), `transition={{ duration: 0.15, delay: globalCharIndex * charDelay }}`. Characters and words are `inline-block`. Words are separated by `&nbsp;`.

## Custom CSS (index.css)

The `btn-glow` class creates an inner white glow effect on primary buttons:
```css
.btn-glow {
  outline: 1.5px solid rgba(255, 255, 255, 0.6);
  outline-offset: -1.5px;
  box-shadow: inset 0 0 14px 0 rgba(255, 255, 255, 0.7);
}

@media (min-width: 640px) {
  .btn-glow {
    outline-width: 2px;
    outline-offset: -2px;
  }
}
```

## Outer Section
The root `<section>` wrapping everything: `relative min-h-screen w-full overflow-hidden bg-black`.

## Dependencies
- `react`, `react-dom` (v18)
- `framer-motion`
- `lucide-react`
- `tailwindcss`, `autoprefixer`, `postcss`
- Vite + TypeScript
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Modern Agency"
template_id: "f76e1d7f-7b83-4495-aa4c-db691d7adae3"
section: "sites"
category_slug: "agency"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Modern Agency

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `f76e1d7f-7b83-4495-aa4c-db691d7adae3`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency

### 🖼 Прев'ю:
![Modern Agency](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/1dfe284a-5b6e-43ed-9e1f-094a8dc46408.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a React + Vite + Tailwind CSS landing page for "Axion Studio" - a design agency site. Use the `shaders` package (npm: `shaders`) for the hero background, `lucide-react` for icons. The page has 3 sections. Match every detail exactly:

---

## SECTION 1: HERO (Full viewport height)

**Background:** Light gray `#EFEFEF` with a full-screen animated shader overlay (positioned absolute, inset-0, z-10, pointer-events-none). The shader stack uses components from `shaders/react`:
- `Swirl` - colorA: `#ffffff`, colorB: `#f0f0f0`, detail: 1.7
- `ChromaFlow` - baseColor: `#ffffff`, downColor/leftColor/rightColor/upColor: `#ff5f03`, momentum: 13, radius: 3.5
- `FlutedGlass` - aberration: 0.61, angle: 31, frequency: 8, highlight: 0.12, highlightSoftness: 0, lightAngle: -90, refraction: 4, shape: "rounded", softness: 1, speed: 0.15
- `FilmGrain` - strength: 0.05

**Navigation (z-20, relative):** A pill-shaped white navbar (`bg-white rounded-full`) with 5px padding, inside a max-w-[1440px] container with p-2 sm:p-3.

- LEFT: Dark circle logo (w-9 h-9 sm:w-10 sm:h-10, bg-gray-900, rounded-full) with white text "AX" (10px/11px, font-bold, tracking-tight). Next to it (hidden on mobile, shown md+): nav links "Projects", "Studio", "Journal", "Connect" - 14px, text-gray-900, hover:text-gray-500, transition-colors duration-300, gap-6.

- RIGHT (hidden on mobile, shown md+): 
  - Text "Taking on projects for Q1 2026" (13px, text-gray-600, hidden below lg)
  - Clock icon (lucide, size 14) + live London time "{HH:MM} in London" (13px, text-gray-600)
  - CTA button: bg-gray-900, text-white, 13px font-medium, rounded-full, pl-5 pr-2 py-2. Text "Book a strategy call" with a HOVER TEXT ROLL animation: the text is duplicated inside a flex-col container with overflow-hidden h-[20px], on group-hover it translates -50% vertically (duration-500, ease cubic-bezier(0.25,0.1,0.25,1)). Arrow icon in a white circle (w-6 h-6) that rotates -45deg on hover (same easing).

- MOBILE: A "Menu"/"Close" toggle button (md:hidden), bg-gray-900, rounded-full, with Menu/X icons from lucide-react.

**Mobile Menu Overlay:** Fixed inset-0, z-50. Black/60 backdrop. A white bottom sheet (rounded-2xl, mx-3 mb-3) that slides up (translate-y-full to translate-y-0, duration-500, ease cubic-bezier(0.32,0.72,0,1)). Contains: time badge, nav links (28px/32px font-medium), and a "Start a project" button with arrow.

**Hero Content (z-20):** Positioned at the bottom of the viewport using flexbox (flex-1 spacer above). Max-w-[1440px], px-5 sm:px-8 lg:px-12, pb-14 sm:pb-16 lg:pb-20.

- Small label: "Axion Studio" (13px/14px, text-gray-900, tracking-wide, mb-5 sm:mb-8)
- Headline h1: "We craft digital experiences / for brands ready to dominate / their category online." - clamp(1.75rem,7vw,4.2rem) on mobile, clamp(2.5rem,5vw,4.2rem) on sm+. font-medium, leading-[1.08], tracking-[-0.03em], text-gray-900. Line breaks hidden on mobile (uses `<br className="hidden sm:block" />` with `<span className="sm:hidden"> </span>` fallback spaces).
- CTA row (mt-8 sm:mt-12, flex-col sm:flex-row, gap-4 sm:gap-5):
  - Orange button: bg-[#F26522], hover:bg-[#e05a1a], text-white, 13px/14px, rounded-full, pl-5 sm:pl-6 pr-2 py-2. Same text-roll hover animation for "Start a project". White circle (w-7 h-7 sm:w-8 sm:h-8) with orange ArrowRight that rotates -45deg on hover.
  - Partner badge: White pill with subtle shadow (0_2px_8px_rgba(0,0,0,0.08)), hover shadow (0_4px_16px_rgba(0,0,0,0.12)), rounded-[4px]. Contains an inline SVG icon (the starburst/compass shape below, w-5 h-5 sm:w-6 sm:h-6, fill-current text-[#E8704E]), text "Certified Partner" (13px/14px font-medium), and a dark badge "Featured" (10px/11px, bg-gray-900, text-white, px-1.5 sm:px-2 py-0.5, rounded).

**SVG Icon for partner badge:**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="m19.6 66.5 19.7-11 .3-1-.3-.5h-1l-3.3-.2-11.2-.3L14 53l-9.5-.5-2.4-.5L0 49l.2-1.5 2-1.3 2.9.2 6.3.5 9.5.6 6.9.4L38 49.1h1.6l.2-.7-.5-.4-.4-.4L29 41l-10.6-7-5.6-4.1-3-2-1.5-2-.6-4.2 2.7-3 3.7.3.9.2 3.7 2.9 8 6.1L37 36l1.5 1.2.6-.4.1-.3-.7-1.1L33 25l-6-10.4-2.7-4.3-.7-2.6c-.3-1-.4-2-.4-3l3-4.2L28 0l4.2.6L33.8 2l2.6 6 4.1 9.3L47 29.9l2 3.8 1 3.4.3 1h.7v-.5l.5-7.2 1-8.7 1-11.2.3-3.2 1.6-3.8 3-2L61 2.6l2 2.9-.3 1.8-1.1 7.7L59 27.1l-1.5 8.2h.9l1-1.1 4.1-5.4 6.9-8.6 3-3.5L77 13l2.3-1.8h4.3l3.1 4.7-1.4 4.9-4.4 5.6-3.7 4.7-5.3 7.1-3.2 5.7.3.4h.7l12-2.6 6.4-1.1 7.6-1.3 3.5 1.6.4 1.6-1.4 3.4-8.2 2-9.6 2-14.3 3.3-.2.1.2.3 6.4.6 2.8.2h6.8l12.6 1 3.3 2 1.9 2.7-.3 2-5.1 2.6-6.8-1.6-16-3.8-5.4-1.3h-.8v.4l4.6 4.5 8.3 7.5L89 80.1l.5 2.4-1.3 2-1.4-.2-9.2-7-3.6-3-8-6.8h-.5v.7l1.8 2.7 9.8 14.7.5 4.5-.7 1.4-2.6 1-2.7-.6-5.8-8-6-9-4.7-8.2-.5.4-2.9 30.2-1.3 1.5-3 1.2-2.5-2-1.4-3 1.4-6.2 1.6-8 1.3-6.4 1.2-7.9.7-2.6v-.2H49L43 72l-9 12.3-7.2 7.6-1.7.7-3-1.5.3-2.8L24 86l10-12.8 6-7.9 4-4.6-.1-.5h-.3L17.2 77.4l-4.7.6-2-2 .2-3 1-1 8-5.5Z"/></svg>
```

---

## SECTION 2: ABOUT (White background)

`bg-white`, pt-16 sm:pt-20 lg:pt-32, pb-12 sm:pb-16 lg:pb-24, overflow-hidden. Max-w-[1440px] container.

**Badge row:** px-5 sm:px-8 lg:px-12, flex items-center gap-3, mb-6 sm:mb-8.
- Numbered circle: w-6 h-6 sm:w-7 sm:h-7, rounded-full, bg-gray-900, text-white, 11px/12px font-semibold. Shows "1".
- Pill label: "Introducing Axion" - 12px/13px, font-medium, border border-gray-200, rounded-full, px-3 sm:px-4 py-1 sm:py-1.5.

**Heading h2:** "Strategy-led creatives, delivering / results in digital and beyond." - clamp(1.5rem,4vw,3.2rem), font-medium, leading-[1.12], tracking-[-0.02em], text-gray-900, mb-12 sm:mb-16 lg:mb-28.

**Content area (responsive):**

- MOBILE/TABLET (lg:hidden): Stacked - paragraph + button, then images.
  - Paragraph: "Through research, creative thinking and iteration we help growing brands realize their digital full potential." - 15px/17px, leading-[1.6], font-medium, text-gray-900.
  - Button: "About our studio" - orange (#F26522), same text-roll animation, white arrow circle rotates -45deg.
  - Two images: flex-col sm:flex-row, gap-4 sm:gap-5. First: sm:w-[45%] aspect-[438/346]. Second: sm:w-[55%] aspect-[900/600]. Both rounded-xl sm:rounded-2xl, object-cover.

- DESKTOP (hidden lg:grid): `grid-cols-[26%_1fr_48%] items-end gap-6 xl:gap-8`.
  - Left column (self-end): Small image, aspect-[438/346], rounded-2xl.
  - Center column (self-start, flex justify-end): Paragraph (16px/18px, leading-[1.65], whitespace-nowrap, with `<br/>` between lines) + orange button.
  - Right column (self-end): Large image, aspect-[3/2], rounded-2xl.

**Image URLs:**
- Small image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090123_74be96d4-9c1b-40cf-932a-96f4f4babed3.png&w=1280&q=85`
- Large image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_090133_c157d30b-a99a-4477-bec1-a446149ec3f2.png&w=1280&q=85`

---

## SECTION 3: CASE STUDIES (Light gray background)

`bg-[#F5F5F5]`, pt-16 sm:pt-20 lg:pt-28, pb-16 sm:pb-20 lg:pb-28. Max-w-[1440px] container.

**Badge row:** Same pattern as Section 2, but number is "2", label is "Featured client work", border-gray-300.

**Heading h2:** "Our projects" - same clamp sizing as hero headline (clamp(1.75rem,7vw,4.2rem) / clamp(2.5rem,5vw,4.2rem)), font-medium, leading-[1.08], tracking-[-0.03em], mb-10 sm:mb-14 lg:mb-16.

**Cards Grid:** `grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6 lg:gap-7`, px-5 sm:px-8 lg:px-12.

**Card 1 (Narrativ):**
- Video container: aspect-[329/246], rounded-2xl, overflow-hidden, bg-[#1a1d2e], group, cursor-pointer.
- Video: `src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260516_122702_390f5305-8719-41d5-ae80-d23ab3796c28.mp4"`, autoPlay, muted, loop, playsInline, w-full h-full object-cover.
- Hover button (absolute bottom-4 left-4): A white circle (h-9 w-9) that expands to w-[148px] on group-hover (transition-all duration-300 ease-in-out). Contains "Learn more" text (13px, font-medium, opacity-0 to opacity-100 on hover with delay-100) and a link/chain SVG icon (14x14, -rotate-45 to rotate-0 on hover). The SVG is the lucide "link" icon drawn manually with two arc paths.
- Description: "Winner of Site of the Month 2025 - an interactive 3D showcase driving record engagement" - 13px/14px, text-gray-600, mt-4, leading-relaxed.
- Title: "Narrativ" - 14px/15px, font-semibold, text-gray-900, mt-1.

**Card 2 (Luminar):**
- Video container: aspect-square, rounded-2xl, overflow-hidden, bg-[#6b6b6b], group, cursor-pointer.
- Video: `src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260516_123323_f909c2b8-ff6c-4edf-882b-8ebcdbe389b5.mp4"`, autoPlay, muted, loop, playsInline, w-full h-full object-cover.
- Hover button (absolute bottom-4 left-4): A DARK circle (bg-gray-900, h-9 w-9) that expands to w-[168px] on group-hover. Contains "View case study" text (13px, font-medium, text-white) and a white ArrowRight icon (size 14) that transitions from -rotate-45 to rotate-0 on hover.
- Description: "Transforming a dated platform into a conversion-focused brand experience" - 13px/14px, text-gray-600, mt-4, leading-relaxed.
- Title: "Luminar" - 14px/15px, font-semibold, text-gray-900, mt-1.

---

## GLOBAL STYLES (index.css):

Standard Tailwind directives plus two utility classes (not actively used in current layout but defined):
- `.liquid-glass`: rgba(255,255,255,0.01) bg, backdrop-filter blur(4px), inset box-shadow, pseudo-element gradient border using mask-composite.
- `.liquid-glass-strong`: Same but blur(50px), no pseudo-element.

---

## TECHNICAL DETAILS:
- **Framework:** React 18 + TypeScript + Vite
- **Styling:** Tailwind CSS 3.4 (default config, no custom theme extensions)
- **Packages:** `shaders` (for Shader, ChromaFlow, FilmGrain, FlutedGlass, Swirl from `shaders/react`), `lucide-react` (ArrowRight, Clock, Menu, X)
- **Font:** System default (no custom font loaded)
- **All animations use:** `duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)]` unless noted otherwise
- **Max content width:** 1440px, centered with mx-auto
- **Responsive breakpoints:** Default Tailwind (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
- **Live clock:** Updates every second, shows London timezone in HH:MM format
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "3D Collectible Hero"
template_id: "05a04f40-448e-46f3-a9e1-72ab98d682c2"
section: "sites"
category_slug: "3d"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 3D Collectible Hero

> **Секція:** `SITES` | **Категорія:** `3d`  
> **ID шаблону:** `05a04f40-448e-46f3-a9e1-72ab98d682c2`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
3D Website

### 🖼 Прев'ю:
![3D Collectible Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/8ea5ef79-bef0-4427-9de0-3ca094f5d250.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single full-viewport hero section in React + TypeScript + Vite + Tailwind CSS, using `lucide-react` for icons. The component is a character-figurine carousel called "TOONHUB".

**Fonts (load in `index.html` head):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
```
Body font: `'Inter', sans-serif`. Display font (huge ghost text + bottom-right link): `'Anton', sans-serif`.

**Image data (4 items, exact URLs and colors):**
```ts
const IMAGES = [
  { src: 'https://fifth-gentle-45902158.figma.site/_components/v2/4de492f6d9cf8244ad5293233e5c6f52407d42fc/1.02464a56.png', bg: '#F4845F', panel: '#F79B7F' },
  { src: 'https://fifth-gentle-45902158.figma.site/_components/v2/4de492f6d9cf8244ad5293233e5c6f52407d42fc/2.b977faab.png', bg: '#6BBF7A', panel: '#85CC92' },
  { src: 'https://fifth-gentle-45902158.figma.site/_components/v2/4de492f6d9cf8244ad5293233e5c6f52407d42fc/3.4df853b4.png', bg: '#E882B4', panel: '#ED9DC4' },
  { src: 'https://fifth-gentle-45902158.figma.site/_components/v2/4de492f6d9cf8244ad5293233e5c6f52407d42fc/4.4457fbce.png', bg: '#6EB5FF', panel: '#8DC4FF' },
];
```
Preload all 4 images on mount via `new Image()`.

**State & logic:**
- `activeIndex` (0–3), `isAnimating` boolean lock, `isMobile` (`window.innerWidth < 640`, updated on resize).
- `navigate('next' | 'prev')`: ignore if animating; set `isAnimating=true`; bump `activeIndex` `(prev+1)%4` or `(prev+3)%4`; release lock after `650ms`.
- Roles derived from activeIndex: `center=activeIndex`, `left=(activeIndex+3)%4`, `right=(activeIndex+1)%4`, `back=(activeIndex+2)%4`.

**Layout structure:**
Outer `<div>` has `backgroundColor: IMAGES[activeIndex].bg`, transition `background-color 650ms cubic-bezier(0.4,0,0.2,1)`, `fontFamily: 'Inter, sans-serif'`, `relative w-full overflow-hidden`. Inside, a `relative w-full` div with `height: 100vh; overflow: hidden`.

1. **Grain overlay** (`absolute inset-0 pointer-events-none`, zIndex 50): SVG fractalNoise data URI, `baseFrequency=0.9`, `numOctaves=4`, opacity 0.08 inside SVG, container `opacity: 0.4`, `backgroundSize: 200px 200px`, repeat.

2. **Giant ghost text "3D SHAPE"** (`absolute inset-x-0 flex items-center justify-center pointer-events-none select-none`, zIndex 2, `top: 18%`): font Anton, `fontSize: clamp(90px, 28vw, 380px)`, weight 900, color white, opacity 1, lineHeight 1, uppercase, letterSpacing `-0.02em`, whiteSpace nowrap.

3. **Top-left brand label "TOONHUB"** (`absolute top-6 left-4 sm:left-8`, zIndex 60): `text-xs font-semibold uppercase`, white, opacity 0.9, letterSpacing `0.18em`.

4. **Carousel** (`absolute inset-0`, zIndex 3): map all 4 IMAGES; each item is `position:absolute`, `aspectRatio: '0.6 / 1'`, with role-based styles below. Inside, an `<img>` `width:100%; height:100%; objectFit:contain; objectPosition:bottom center; draggable=false`.

   Per-role style:
   - **center**: `transform: translateX(-50%) scale(${isMobile?1.25:1.68})`, no blur, opacity 1, zIndex 20, `left:50%`, `height: isMobile?'60%':'92%'`, `bottom: isMobile?'22%':0`.
   - **left**: `translateX(-50%) scale(1)`, blur 2px, opacity 0.85, zIndex 10, `left: isMobile?'20%':'30%'`, `height: isMobile?'16%':'28%'`, `bottom: isMobile?'32%':'12%'`.
   - **right**: same as left but `left: isMobile?'80%':'70%'`.
   - **back**: `translateX(-50%) scale(1)`, blur 4px, opacity 1, zIndex 5, `left:50%`, `height: isMobile?'13%':'22%'`, `bottom: isMobile?'32%':'12%'`.

   Transition on each item: `transform 650ms cubic-bezier(0.4,0,0.2,1), filter 650ms ..., opacity 650ms ..., left 650ms ...`. `willChange: transform, filter, opacity`.

5. **Bottom-left text + nav buttons** (`absolute bottom-6 left-4 sm:bottom-20 sm:left-24`, zIndex 60, `maxWidth:320px`):
   - `<p>` "TOONHUB FIGURINES" — bold uppercase, tracking-widest, `mb-2 sm:mb-3 text-base sm:text-[22px]`, white, opacity 0.95, letterSpacing `0.02em`.
   - `<p>` (hidden on mobile, `hidden sm:block`): "The artwork is stunning, shipped fully prepared. The finish is a vision, the 3D craft is flawless. Many thanks! Wishing you the win. Order now." — `text-xs sm:text-sm`, white, opacity 0.85, lineHeight 1.6, `mb-4 sm:mb-5`.
   - Two circular buttons (`w-12 h-12 sm:w-16 sm:h-16`, transparent bg, 2px white border, white icon): `ArrowLeft` and `ArrowRight` from lucide-react, size 26, strokeWidth 2.25. On hover: scale 1.08 + bg `rgba(255,255,255,0.12)`. Transition `transform 150ms, background-color 150ms`. Click triggers `navigate('prev')` / `navigate('next')`.

6. **Bottom-right link "DISCOVER IT"** (`absolute bottom-6 right-4 sm:bottom-20 sm:right-10`, zIndex 60): `<a>` flex items-center, font Anton, `fontSize: clamp(20px, 4vw, 56px)`, weight 400, white, opacity 0.95→1 on hover (200ms), letterSpacing `-0.02em`, lineHeight 1, uppercase, no underline. Followed by `ArrowRight` (`w-5 h-5 sm:w-8 sm:h-8`, strokeWidth 2.25).

**Behavior summary:** clicking arrows rotates roles; background color, image positions, scales, blurs, and opacities all crossfade simultaneously over 650ms with `cubic-bezier(0.4,0,0.2,1)`. The character images sit at the bottom of the screen overlapping the giant "3D SHAPE" text behind them.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Liquid Glass Agency"
template_id: "00fbce56-bbac-44ec-89bd-f96fd304c489"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Liquid Glass Agency

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `00fbce56-bbac-44ec-89bd-f96fd304c489`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Liquid Glass Agency](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/2810603d-6677-433c-9c71-af47da21814e.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a dark, premium, single-page landing page for an AI-powered web design agency using React + Vite + Tailwind CSS + shadcn/ui + Framer Motion (motion/react). The page has a luxury editorial aesthetic -- black backgrounds, white text, liquid glass (glassmorphism) effects, and cinematic video backgrounds.

FONTS
Import from Google Fonts:

https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Barlow:wght@300;400;500;600&display=swap
* Headings: Instrument Serif (italic) -- used via Tailwind class font-heading
* Body: Barlow (weights 300, 400, 500, 600) -- used via Tailwind class font-body
Tailwind config extends fontFamily:

heading: ["'Instrument Serif'", "serif"]
body: ["'Barlow'", "sans-serif"]

COLOR THEME (CSS custom properties, HSL format)

:root {
  --background: 213 45% 67%;
  --foreground: 0 0% 100%;
  --card: 213 45% 62%;
  --card-foreground: 0 0% 100%;
  --primary: 0 0% 100%;
  --primary-foreground: 213 45% 67%;
  --secondary: 213 45% 72%;
  --secondary-foreground: 0 0% 100%;
  --muted: 213 35% 60%;
  --muted-foreground: 0 0% 100% / 0.7;
  --accent: 213 45% 72%;
  --accent-foreground: 0 0% 100%;
  --destructive: 0 84.2% 60.2%;
  --border: 0 0% 100% / 0.2;
  --input: 0 0% 100% / 0.2;
  --ring: 0 0% 100% / 0.3;
  --radius: 9999px;
  --glass-bg: rgba(255, 255, 255, 0.12);
  --glass-border: rgba(255, 255, 255, 0.25);
  --glass-shadow: 0 4px 30px rgba(0, 0, 0, 0.08);
  --glass-blur: 16px;
}

LIQUID GLASS CSS (the core visual effect)
Two utility classes defined in index.css under @layer components:
.liquid-glass (subtle):

.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0.15) 20%,
    rgba(255, 255, 255, 0) 40%,
    rgba(255, 255, 255, 0) 60%,
    rgba(255, 255, 255, 0.15) 80%,
    rgba(255, 255, 255, 0.45) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
.liquid-glass-strong (more prominent, used on CTA buttons):

.liquid-glass-strong {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(50px);
  -webkit-backdrop-filter: blur(50px);
  border: none;
  box-shadow: 4px 4px 4px rgba(0, 0, 0, 0.05),
    inset 0 1px 1px rgba(255, 255, 255, 0.15);
  position: relative;
  overflow: hidden;
}
.liquid-glass-strong::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.5) 0%,
    rgba(255, 255, 255, 0.2) 20%,
    rgba(255, 255, 255, 0) 40%,
    rgba(255, 255, 255, 0) 60%,
    rgba(255, 255, 255, 0.2) 80%,
    rgba(255, 255, 255, 0.5) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
The ::before pseudo-element creates a gradient border effect using the mask-composite trick (thin glowing border that fades in the middle).

ASSETS & MEDIA URLS
Hero background video (MP4, CloudFront):

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260307_083826_e938b29f-a43a-41ec-a153-3d4730578ab8.mp4
Poster image: /images/hero_bg.jpeg (local file in public/images/)
StartSection video (HLS via Mux):

https://stream.mux.com/9JXDljEVWYwWu01PUkAemafDugK89o01BR6zqJ3aS9u00A.m3u8
Stats section video (HLS via Mux, displayed desaturated):

https://stream.mux.com/NcU3HlHeF7CUL86azTTzpy3Tlb00d6iF3BmCdFslMJYM.m3u8
CTA/Footer section video (HLS via Mux):

https://stream.mux.com/8wrHPCX2dC3msyYU9ObwqNdm00u3ViXvOSHUMRYSEe5Q.m3u8
Feature GIFs (imported from src/assets/):
* feature-1.gif -- used in FeaturesChess row 1 (right side)
* feature-2.gif -- used in FeaturesChess row 2 (left side)
Logo icon: src/assets/logo-icon.png (12x12 Tailwind = h-12 w-12)

SECTION-BY-SECTION BREAKDOWN
1. NAVBAR (fixed, floating)
* Fixed position: fixed top-4 left-0 right-0 z-50, horizontal padding px-8 lg:px-16, vertical py-3
* Left: Logo image (h-12 w-12)
* Center (desktop only, hidden md:flex): Navigation links inside a liquid-glass rounded-full px-1.5 py-1 pill container
    * Links: "Home", "Services", "Work", "Process", "Pricing"
    * Each link: px-3 py-2 text-sm font-medium text-foreground/90 font-body
    * Last item: white solid button "Get Started" with ArrowUpRight icon, bg-white text-black rounded-full px-3.5 py-1.5 text-sm
2. HERO SECTION
* Container: relative overflow-visible, fixed height 1000px
* Background video: <video> tag with autoPlay, loop, muted, playsInline. Positioned absolute left-0 w-full h-auto object-contain z-0 with top: 20%. Source is the CloudFront MP4 URL. Poster is /images/hero_bg.jpeg.
* Dark overlay: absolute inset-0 bg-black/5 z-0
* Bottom gradient fade: absolute bottom-0, height 300px, linear-gradient(to bottom, transparent, black)
* Content (z-10, centered, paddingTop: 150px):
    * Badge pill: liquid-glass rounded-full px-1 py-1 with inner white "New" badge (bg-white text-black rounded-full px-3 py-1 text-xs font-semibold) and text "Introducing AI-powered web design."
    * Heading (BlurText component): "The Website Your Brand Deserves" -- text-6xl md:text-7xl lg:text-[5.5rem] font-heading italic text-foreground leading-[0.8] max-w-2xl tracking-[-4px], animated word-by-word from bottom with blur, delay 100ms
    * Subtext (motion.p): "Stunning design. Blazing performance. Built by AI, refined by experts. This is web design, wildly reimagined." -- blur-in animation, delay 0.8s, text-sm md:text-base text-white font-body font-light leading-tight
    * CTA buttons (motion.div, delay 1.1s):
        * "Get Started" -- liquid-glass-strong rounded-full px-5 py-2.5 with ArrowUpRight icon
        * "Watch the Film" -- text-only with Play icon (filled)
    * Partners bar at bottom (mt-auto pb-8 pt-16): "Trusted by the teams behind" liquid-glass pill, then 5 partner names rendered in text-2xl md:text-3xl font-heading italic text-white with gap-12 md:gap-16: Stripe, Vercel, Linear, Notion, Figma
3. BlurText COMPONENT (custom animated text)
* Splits text by words or letters
* Uses IntersectionObserver to trigger on scroll
* Each word/letter is a <motion.span> that animates from {filter: 'blur(10px)', opacity: 0, y: 50} (when direction=bottom) through {filter: 'blur(5px)', opacity: 0.5, y: -5} to {filter: 'blur(0px)', opacity: 1, y: 0}
* Staggered by index with configurable delay (default 200ms per element)
* Step duration 0.35s per keyframe step
4. START SECTION ("How It Works")
* Full-width section with HLS video background using hls.js library
* Video: autoPlay, loop, muted, playsInline, absolute inset-0 w-full h-full object-cover
* Top and bottom gradient fades (200px each, black to transparent)
* Content centered (z-10, minHeight 500px):
    * Badge: "How It Works" in liquid-glass rounded-full px-3.5 py-1
    * Heading: "You dream it. We ship it." -- text-4xl md:text-5xl lg:text-6xl font-heading italic tracking-tight leading-[0.9]
    * Subtext: "Share your vision. Our AI handles the rest--wireframes, design, code, launch. All in days, not quarters." -- text-white/60 font-body font-light text-sm md:text-base
    * CTA: "Get Started" liquid-glass-strong rounded-full px-6 py-3
5. FEATURES CHESS (alternating rows)
* Section header: "Capabilities" badge + "Pro features. Zero complexity." heading
* Row 1 (flex, content left / image right):
    * Title: "Designed to convert. Built to perform."
    * Body: "Every pixel is intentional. Our AI studies what works across thousands of top sites--then builds yours to outperform them all."
    * Button: "Learn more" liquid-glass-strong
    * Gif: https://motionsites.ai/assets/hero-finlytic-preview-CV9g0FHP.gif download and place inside liquid-glass rounded-2xl overflow-hidden
* Row 2 (flex-row-reverse, content right / image left):
    * Title: "It gets smarter. Automatically."
    * Body: "Your site evolves on its own. AI monitors every click, scroll, and conversion--then optimizes in real time. No manual updates. Ever."
    * Button: "See how it works" liquid-glass-strong
    * gif: https://motionsites.ai/assets/hero-wealth-preview-B70idl_u.gif download and place inside liquid-glass rounded-2xl overflow-hidden
6. FEATURES GRID ("Why Us")
* Section header: "Why Us" badge + "The difference is everything." heading
* 4-column grid (grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6), each card is liquid-glass rounded-2xl p-6:
    1. Icon: Zap -- "Days, Not Months" -- "Concept to launch at a pace that redefines fast. Because waiting isn't a strategy."
    2. Icon: Palette -- "Obsessively Crafted" -- "Every detail considered. Every element refined. Design so precise, it feels inevitable."
    3. Icon: BarChart3 -- "Built to Convert" -- "Layouts informed by data. Decisions backed by performance. Results you can measure."
    4. Icon: Shield -- "Secure by Default" -- "Enterprise-grade protection comes standard. SSL, DDoS mitigation, compliance. All included."
    * Each icon sits in a liquid-glass-strong rounded-full w-10 h-10 circle
7. STATS SECTION
* HLS video background (Mux URL), displayed with filter: saturate(0) (desaturated/B&W)
* Top and bottom gradient fades (200px each)
* Content: liquid-glass rounded-3xl p-12 md:p-16 card with 4-column grid:
    * "200+" / "Sites launched"
    * "98%" / "Client satisfaction"
    * "3.2x" / "More conversions"
    * "5 days" / "Average delivery"
    * Values: text-4xl md:text-5xl lg:text-6xl font-heading italic
    * Labels: text-white/60 font-body font-light text-sm
8. TESTIMONIALS
* Section header: "What They Say" badge + "Don't take our word for it." heading
* 3-column grid (md:grid-cols-3 gap-6), each card is liquid-glass rounded-2xl p-8:
    1. "A complete rebuild in five days. The result outperformed everything we'd spent months building before." -- Sarah Chen, CEO, Luminary
    2. "Conversions up 4x. That's not a typo. The design just works differently when it's built on real data." -- Marcus Webb, Head of Growth, Arcline
    3. "They didn't just design our site. They defined our brand. World-class doesn't begin to cover it." -- Elena Voss, Brand Director, Helix
    * Quote: text-white/80 font-body font-light text-sm italic
    * Name: text-white font-body font-medium text-sm
    * Role: text-white/50 font-body font-light text-xs
9. CTA + FOOTER
* HLS video background (Mux URL)
* Top and bottom gradient fades (200px each)
* Content (z-10, centered):
    * Heading: "Your next website starts here." -- text-5xl md:text-6xl lg:text-7xl font-heading italic leading-[0.85]
    * Subtext: "Book a free strategy call. See what AI-powered design can do. No commitment, no pressure. Just possibilities."
    * Two buttons:
        * "Book a Call" -- liquid-glass-strong rounded-full px-6 py-3
        * "View Pricing" -- bg-white text-black rounded-full px-6 py-3
    * Footer bar (mt-32 pt-8 border-t border-white/10):
        * Left: "(c) 2026 Studio. All rights reserved." text-white/40 text-xs
        * Right: "Privacy", "Terms", "Contact" links text-white/40 text-xs

KEY DEPENDENCIES

{
  "motion": "^12.35.0",
  "hls.js": "^1.6.15",
  "lucide-react": "^0.462.0",
  "react-router-dom": "^6.30.1"
}
Icons used from lucide-react: ArrowUpRight, Play, Zap, Palette, BarChart3, Shield

OVERALL PAGE STRUCTURE

<div bg-black>
  <div z-10>
    <Navbar />           -- fixed floating nav
    <Hero />             -- 1000px tall, CloudFront MP4 video bg
    <div bg-black>
      <StartSection />   -- HLS video bg, "How It Works"
      <FeaturesChess />  -- alternating text/gif rows
      <FeaturesGrid />   -- 4-card grid
      <Stats />          -- HLS video bg (desaturated), stats card
      <Testimonials />   -- 3-card grid
      <CtaFooter />      -- HLS video bg, CTA + footer
    </div>
  </div>
</div>

ANIMATION PATTERNS
1. BlurText (heading): Word-by-word stagger from bottom with gaussian blur dissolve, IntersectionObserver triggered
2. Hero subtext: motion.p with filter: blur(10px) -> blur(0px), opacity: 0 -> 1, y: 20 -> 0, delay 0.8s, duration 0.6s
3. Hero CTA buttons: Same blur-in pattern, delay 1.1s
4. All video backgrounds: autoPlay, loop, muted, playsInline with top/bottom black gradient fades (200px typically, 300px on hero bottom)

DESIGN PATTERNS USED THROUGHOUT
* Every section badge: liquid-glass rounded-full px-3.5 py-1 text-xs font-medium text-white font-body
* Every section heading: text-4xl md:text-5xl lg:text-6xl font-heading italic text-white tracking-tight leading-[0.9]
* Every body text: text-white/60 or text-white/70, font-body font-light text-sm md:text-base
* Primary CTA: liquid-glass-strong rounded-full with ArrowUpRight icon
* Secondary CTA: bg-white text-black rounded-full
* Card containers: liquid-glass rounded-2xl
* Video overlay fades: always linear-gradient(to bottom/top, black, transparent) with pointer-events-none

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Dreamcore Landing"
template_id: "15d97df4-3f8f-40b7-b119-093ba40b7053"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Dreamcore Landing

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `15d97df4-3f8f-40b7-b119-093ba40b7053`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Dreamcore Landing](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5d2ea933-749e-497b-b7c1-5ec6aa6b0a66.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page immersive parallax landing page in React + TypeScript + Tailwind CSS using Vite. The page has two scroll-driven scenes inside a sticky viewport. Everything lives in a single `src/App.tsx` file. Use Google Fonts: **Viaoda Libre** (serif headings) and **Imprima** (sans-serif body). No external UI libraries. Use `lucide-react` only as a dependency (it is not used in this page). Use Tailwind for responsive layout breakpoints only; all other styling is inline React `CSSProperties`.

---

### GLOBAL SETUP

**`tailwind.config.js`** -- Override the `xl` breakpoint to `1100px`:
```js
screens: { xl: '1100px' }
```

**`index.css`** -- Include Tailwind directives, global reset, dark background `#0a0608`, `font-family: 'Imprima', sans-serif`, `scrollbar-gutter: stable`, and a `@keyframes bobUp` animation that translates Y by `-6px` at 50%.

**`index.html`** -- Load Google Fonts via `<link>`:
```
https://fonts.googleapis.com/css2?family=Viaoda+Libre&family=Imprima&display=swap
```
Title: "Step Into Wonder"

---

### IMAGE ASSETS (use these exact URLs)

```
PORTAL_BG    = "https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779707217/image_1_vdzwae.png"
CURTAIN_LEFT = "https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779706559/curtain_left_znkmva.png"
CURTAIN_RIGHT= "https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779706564/curtain_right_paeyym.png"
WORLD_BG     = "https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779706392/image_2_gkcdlx.png"
BOTTOM_CLOUDS= "https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779706555/bottom_clouds_xskut6.png"

CARD_IMAGES[0] = "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260525_160507_2ccbb4eb-1469-484f-af25-59168ad9a233.png&w=1280&q=85"
CARD_IMAGES[1] = "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260525_160644_072a7f68-a101-4ded-a332-7d37707dbdd1.png&w=1280&q=85"
CARD_IMAGES[2] = "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260525_160706_1c153d04-0dfb-4ac9-a4ef-e74f301c329c.png&w=1280&q=85"
```

---

### SCENE 2 CARD DATA (9 cards for the arc slider)

```
{ title: 'Hidden Realms',   desc: 'Luminous sanctuaries unseen by wandering eyes',  color: '#f3cdd6' }
{ title: 'Wild Solitudes',  desc: 'Dissolve into untamed horizons and deep calm',   color: '#dcedc2' }
{ title: 'Silent Havens',   desc: 'Remote escapes far beyond ordinary reach',       color: '#c3e3f4' }
{ title: 'Bespoke Quests',  desc: 'Journeys shaped around your vision and soul',    color: '#f0e4c0' }
{ title: 'Vivid Drifts',    desc: 'Surreal passages through breathtaking terrain',  color: '#dcd2f2' }
{ title: 'Mystic Crests',   desc: 'Timeless ridgelines wrapped in cloud and myth',  color: '#f3cdd6' }
{ title: 'Deep Currents',   desc: 'Glowing depths alive with uncharted wonder',     color: '#c3e3f4' }
{ title: 'Gilded Dusk',     desc: 'Amber horizons that stretch past all reason',    color: '#f0e4c0' }
{ title: 'Glassy Tides',    desc: 'Calm waters holding skies of pure stillness',    color: '#dcedc2' }
```

---

### ARCHITECTURE

The outer container is `height: 480vh; position: relative`. Inside it is a `position: sticky; top: 0; height: 100vh; overflow: hidden; background: #0a0608` viewport. All layers stack via absolute positioning and z-index.

**Scroll progress** = `window.scrollY / (container.scrollHeight - window.innerHeight)`, clamped 0-1.

**Helper functions:**
- `easeInOut(t)`: quadratic ease `t < 0.5 ? 2*t*t : -1 + (4 - 2*t)*t`
- `lerp(a, b, t)`: linear interpolation
- `clamp(val, min, max)`

**`useIsMobile()`** hook: `matchMedia('(max-width: 767px)')` -- returns boolean.

---

### LAYER STACK (bottom to top by z-index)

#### Layer 1: World Background (z-index: auto/0)
- `ref={worldRef}`, absolute inset 0, `transformOrigin: '50% 50%'`
- `WORLD_BG` image, `object-fit: cover`
- Parallax: `scale(lerp(1, 1.18, ep))`, mouse offset `MAG.world = 6`

#### Layer 2: Bottom Clouds (z-index: 10)
- `ref={cloudsRef}`, absolute bottom:0, left:0, right:0, `transformOrigin: '50% 100%'`
- `BOTTOM_CLOUDS` image, `width: 100%, height: auto`
- Parallax: `scale(lerp(1, 1.4, ep))`, mouse offset `MAG.clouds = 9` (Y dampened to `0.4x`)
- Opacity: fades from 0.7 to 1 in the first 5% of scroll

#### Layer 2.5: Arc Card Slider (z-index: 9)
- Absolute, `bottom: 60px (mobile) / 80px (desktop)`, centered horizontally
- Opacity = `scene2Opacity`
- Contains `<ArcCardSlider>` component (details below)

#### Layer 3: Portal Frame (z-index: 15)
- `ref={portalRef}`, absolute inset 0, `transformOrigin: '52% 38%'`
- `PORTAL_BG` image, `object-fit: cover`
- Parallax: `scale(lerp(1, 7.5, ep))`, mouse offset `MAG.portal = 7`
- Opacity: 1 until scroll 0.65, then fades to 0 by scroll 0.85

#### Layer 3.5: Bottom Fade (z-index: 16)
- Absolute bottom, `height: 40%`, `linear-gradient(to top, rgba(0,0,0,0.45) 0%, transparent 100%)`, `pointer-events: none`

#### Layer 4L: Curtain Left (z-index: 16)
- `ref={curtainLRef}`, absolute inset 0, `transformOrigin: 'left center'`
- `CURTAIN_LEFT` image, `object-fit: cover`, `object-position: right center`
- On mount (after 100ms), shifts left by `translateX(-62%)` with `transition: transform 1.8s cubic-bezier(0.16, 1, 0.3, 1)`
- On scroll: additional `translateX` via `lerp(0, 150, ep)%`, scale `lerp(1, 1.3, ep)`
- Mouse offset: `MAG.curtainL = 14` (Y dampened to `0.3x`)
- After entrance animation (2200ms), transition switches to `none` for responsive parallax

#### Layer 4R: Curtain Right (z-index: 16)
- Mirror of Layer 4L but `transformOrigin: 'right center'`, `object-position: left center`
- Shifts right instead of left, `MAG.curtainR = 14`

#### Top Fade Gradient (z-index: 45)
- Absolute top, `height: 42vh`, `linear-gradient(to bottom, rgba(0,0,0,0.45) 0%, transparent 100%)`, `pointer-events: none`

---

### NAVIGATION (z-index: 50)

Absolute top, full width, `display: flex, justify-content: space-between, align-items: center`.

**Nav link style:** `font-family: 'Imprima', sans-serif`, `font-size: 12px`, `letter-spacing: 0.12em`, `text-transform: uppercase`, `color: #fff`, `opacity: 0.9`, no text decoration.

**Mobile** (`padding: 18px 20px`): Three items -- "Explore" (11px) | StarLogo SVG | "Connect" (11px)

**Desktop** (`padding: 22px 48px`): Left group ["Worlds", "Atelier", "Immersions"] with `gap: 36px` | StarLogo SVG center | Right group ["Craft", "Codex", "Connect"] with `gap: 36px`

**StarLogo** -- inline SVG, 28x28, white star path + 3 small circles:
```
<path d="M14 2l2.09 6.42H23l-5.45 3.96 2.09 6.42L14 14.84l-5.64 4.06 2.09-6.42L4.96 8.42h6.95L14 2z" fill="white" opacity="0.9" />
<circle cx="14" cy="24" r="1.5" fill="white" opacity="0.6" />
<circle cx="6" cy="6" r="1" fill="white" opacity="0.4" />
<circle cx="22" cy="6" r="1" fill="white" opacity="0.4" />
```

---

### SCENE 1 UI (z-index: 20)

Opacity = `clamp(1 - scrollProgress / 0.22, 0, 1)`. Fades out in first ~22% of scroll.

Uses **three separate Tailwind-responsive layout blocks** (not JS branching for layout):

#### Mobile layout (`md:hidden`)
- Centered column, `padding: 80px 24px 100px`
- Fade-in: `opacity 0.9s ease, transform 0.9s ease`, delay `0.3s`, triggers on `uiVisible`
- **Heading** (Viaoda Libre): "FALL > INTO" line (`clamp(26px, 7vw, 42px)`, `tracking-widest`, color `#3b1a0a`) then "REVERIE" (`clamp(52px, 16vw, 80px)`, `tracking-tight`, `leading-none`, color `#3b1a0a`). The ">" is a `›` character in color `#6b2e0e` at `0.8em`. "INTO" is italic.
- **Subtext** (Imprima): "Crafting boundless digital worlds where the edge between AI, vision, and living myth dissolves." -- `15px`, `leading-relaxed`, color `#5c2d0e`, `max-width: 280px`
- **Single card**: 140x140px, `border-radius: 22px`, `CARD_IMAGES[0]` as background-cover, `box-shadow: 0 8px 32px rgba(0,0,0,0.5)`. Bottom gradient overlay (60% height). Bottom-left overlay: white circle (26px) with play triangle SVG + "View Reel" text (13px, white).

#### Tablet layout (`hidden md:flex xl:hidden`)
- Centered column, `gap: 28px`, `padding: 80px 32px 96px`
- Same fade-in animation as mobile
- **Heading**: same structure as mobile but dark brown text (`#3b1a0a`), sizes `clamp(28px, 5vw, 44px)` / `clamp(60px, 12vw, 86px)`
- **Subtext**: same text, `16px`, color `#5c2d0e`, `max-width: 400px`
- **Three cards in a row** (`flex gap-3.5`): each 140x140px, `border-radius: 22px`. Each has:
  - Background gradient overlay (60% height, multi-stop)
  - Backdrop blur layer (44% height, masked gradient)
  - Card 1: play button + "View Reel"
  - Card 2: number "32" (Viaoda Libre, 28px, white) + "World Patrons"
  - Card 3: play button + "View Reel"

#### Desktop layout (`hidden xl:block` / `hidden xl:flex`)
- **Heading block**: absolute, `top: 46%`, `left: 60px`, `maxWidth: 440px`, `translateY(-50%)` centered
  - White text with heavy `text-shadow: 0 2px 24px rgba(0,0,0,0.7), 0 1px 4px rgba(0,0,0,0.9)`
  - "FALL > INTO": `clamp(32px, 4.5vw, 54px)`, `line-height: 1.1`, `letter-spacing: 0.04em`. The `>` is `rgba(255,220,180,0.7)`.
  - "REVERIE": `clamp(50px, 7.5vw, 88px)`, `line-height: 0.9`, `letter-spacing: -0.02em`
  - Subtext: `18px`, `line-height: 1.7`, color `rgba(255,245,235,0.88)`, `max-width: 300px`, `text-shadow: 0 1px 12px rgba(0,0,0,0.8)`
  - Fade-in: opacity+transform, delay `0.3s`

- **Cards block**: absolute, `right: 40px`, `top: 50%`, `translateY(-50%)`, `flex gap: 12px`
  - Three cards, each 158x158px, `border-radius: 28px`, `box-shadow: 0 8px 32px rgba(0,0,0,0.45)`
  - Each has: gradient overlay, backdrop blur layer (same as tablet), bottom content area at 12px inset
  - Play cards: 30px white circle + 18px "View Reel"
  - Number card: "32" at 36px Viaoda Libre + 18px "World Patrons"
  - Fade-in delay: `0.55s`

#### Slider Dots (bottom of Scene 1)
- Absolute, bottom `28px (mobile, centered)` / `40px (desktop, left: 60px)`
- 4 dots: first is `28px wide`, rest `14px`, all `4px tall`, `border-radius: 2px`
- Active dot: `rgba(255,255,255,0.9)`, inactive: `rgba(255,255,255,0.35)`
- Fade-in delay: `0.8s`

#### Scroll Cue (desktop only)
- Absolute `bottom: 36px`, centered
- "DESCEND" text: `10px`, `letter-spacing: 0.22em`, uppercase, `rgba(255,255,255,0.6)`
- Below: `ScrollChevron` -- 34px circle with 1.5px border `rgba(255,255,255,0.5)`, chevron SVG inside, `animation: bobUp 1.8s ease-in-out infinite`
- Fade-in delay: `0.9s`

---

### SCENE 2 UI (z-index: 46)

Opacity = `clamp((scrollProgress - 0.68) / 0.16, 0, 1)`. Fades in between scroll 68%-84%.

- Centered column
- **Heading** (Viaoda Libre): "FORGE BEYOND THE REAL" -- `clamp(28px, 8vw, 44px) mobile / clamp(38px, 6.5vw, 78px) desktop`, white, `letter-spacing: 0.03em`, `line-height: 1.05`, `text-shadow: 0 2px 20px rgba(0,0,0,0.4)`
- **Subtext** (Imprima): "Singular voyages to astonishing destinations, shaped for those who seek beauty beyond the ordinary and the known." -- `14px mobile / 20px desktop`, `line-height: 1.6`, `letter-spacing: -0.01em`, `max-width: 260px mobile / 480px desktop`, color `rgba(255,255,255,0.82)`
- Margin-top: `8vh mobile / 12vh desktop`

---

### ARC CARD SLIDER COMPONENT

Props: `cards[]`, `rotationOffset: number`, `isMobile: boolean`

**Layout math:**
- `cardSpacingDeg`: 12 (mobile) / 9 (desktop) degrees between cards
- `centerIndex`: `Math.floor(totalCards / 2)`
- `arcRadius`: 700 (mobile) / 1100 (desktop) px
- `cardW`: 160 (mobile) / 220 (desktop) px
- `cardH`: 175 (mobile) / 230 (desktop) px
- `sliderH`: 260 (mobile) / 360 (desktop) px

**`rotationOffset`** is driven by scroll: `lerp(0, arcSweepDeg, clamp((scrollProgress - 0.70) / 0.30, 0, 1))` where `arcSweepDeg = (totalCards - 1) * 10`.

**Per card positioning:**
```
baseDeg = (i - centerIndex) * cardSpacingDeg
deg     = baseDeg - rotationOffset + (centerIndex * cardSpacingDeg)
rad     = deg * PI / 180
x       = sin(rad) * arcRadius
y       = arcRadius - cos(rad) * arcRadius
```
Each card is absolutely positioned at `bottom: -y + (140 mobile / 200 desktop)px`, `left: calc(50% + x - halfW)`, `transform: rotate(deg)`, `transformOrigin: halfW arcRadius`.

**Card appearance:**
- Rounded rect (`18px mobile / 26px desktop`), background = `card.color` (pastel)
- `box-shadow: 0 8px 40px rgba(80,40,60,0.18)`
- Top-right: numbered circle (24px, `1.5px border rgba(80,50,60,0.3)`, text `rgba(80,50,60,0.6)`, 10px Imprima) showing zero-padded index
- Bottom: card title in Viaoda Libre (`22px mobile / 30px`, color `#3a2530`) + description in Imprima (`12px mobile / 15px`, color `rgba(58,37,48,0.65)`)

---

### ENTRANCE ANIMATION SEQUENCE

1. **t=100ms**: Curtains open -- `curtainsOpenRef` flips to true, causing 62% horizontal shift on each curtain with `1.8s cubic-bezier(0.16, 1, 0.3, 1)` transition
2. **t=600ms**: `uiVisible` = true -- all Scene 1 UI elements fade/slide in with staggered delays (0.3s heading, 0.55s cards, 0.8s dots, 0.9s scroll cue)
3. **t=2200ms**: `entranceDone` = true -- curtain CSS transition switches to `none` so parallax is instant

---

### MOUSE PARALLAX (desktop)

`requestAnimationFrame` loop smooths raw mouse position at `speed = 0.07` (lerp). Each layer is offset by its `MAG` value in the reverse direction of the mouse. The transforms combine mouse offset with scroll-driven scale/translate.

**MAG values:** world=6, clouds=9, portal=7, curtainL=14, curtainR=14
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Aethera Studio"
template_id: "439ca2fe-30cd-4e11-ba2b-f4943e43a836"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Aethera Studio

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `439ca2fe-30cd-4e11-ba2b-f4943e43a836`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero Section

### 🖼 Прев'ю:
![Aethera Studio](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/ac68d70e-ca45-4398-9bc7-f35113ccac19.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Prompt: Cinematic Hero Section with Looping Video Background

Create a fullscreen single-page hero section using React + Vite + Tailwind CSS + TypeScript with the following specifications:

Fonts:
Display text (headings, logo): Instrument Serif
Body text (navigation, descriptions): Inter
Import both fonts in /src/styles/fonts.css

Video Background:
URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4
Position: top: '300px' with inset: 'auto 0 0 0'
Implement custom fade-in/fade-out loop logic using React useEffect and useRef:
Use requestAnimationFrame to continuously monitor currentTime and duration
Fade in over 0.5s at the start (opacity 0 to 1)
Fade out over 0.5s before the end (opacity 1 to 0)
On ended event: set opacity to 0, wait 100ms, reset currentTime = 0, then play() again
This creates a seamless manual loop with smooth fade transitions
Add gradient overlays: absolute inset-0 bg-gradient-to-b from-background via-transparent to-background positioned over the video

Navigation Bar:
Logo: "Aethera®" (with registered trademark symbol as superscript)
Logo styling: text-3xl, tracking-tight, Instrument Serif, color #000000
Menu items: Home (color #000000), Studio, About, Journal, Reach Us (all others #6F6F6F)
Menu items: text-sm with transition-colors
CTA button: "Begin Journey", rounded-full, px-6 py-2.5, text-sm, black background (#000000), white text, hover scale 1.03
Layout: flex justify-between, px-8 py-6, max-w-7xl mx-auto

Hero Section:
Positioning: paddingTop: 'calc(8rem - 75px)', pb-40
Layout: centered (flex flex-col items-center justify-center text-center), px-6
Headline:
Text: "Beyond silence, we build the eternal."
Styling: text-5xl sm:text-7xl md:text-8xl, max-w-7xl, font-normal
Font: Instrument Serif
Line height: 0.95
Letter spacing: -2.46px
Color: #000000 for main text, #6F6F6F for italic emphasized words ("silence," and "the eternal.")
Animation: animate-fade-rise

Description:
Text: "Building platforms for brilliant minds, fearless makers, and thoughtful souls. Through the noise, we craft digital havens for deep work and pure flows."
Styling: text-base sm:text-lg, max-w-2xl, mt-8, leading-relaxed
Color: #6F6F6F
Animation: animate-fade-rise-delay

Hero CTA Button:
Text: "Begin Journey"
Styling: rounded-full, px-14 py-5, text-base, mt-12
Colors: black background (#000000), white text (#FFFFFF)
Hover: scale 1.03
Animation: animate-fade-rise-delay-2

Colors:
Background: white (#FFFFFF)
Headlines/logos/buttons: black (#000000)
Descriptions/menu items: gray (#6F6F6F)
Button text: white (#FFFFFF)

Animations (in /src/styles/theme.css):
fade-rise: opacity 0 to 1, translateY 20px to 0, duration 0.8s, ease-out
fade-rise-delay: same as fade-rise but with 0.2s delay
fade-rise-delay-2: same as fade-rise but with 0.4s delay

Layout Structure:
Container: relative min-h-screen w-full overflow-hidden
Background video layer (z-0)
Gradient overlay on video
Navigation bar (z-10)
Hero section (z-10)
All elements should be responsive and maintain the glassmorphic aesthetic with the specified padding, positioning, and smooth animations.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Grow AI Talent Platform"
template_id: "39135d64-38f2-4a31-9ba0-1d71581aae2e"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Grow AI Talent Platform

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `39135d64-38f2-4a31-9ba0-1d71581aae2e`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![Grow AI Talent Platform](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/98ac55b5-d150-40eb-94bb-cb6a8d77aad1.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a dark-themed landing page hero section with a navbar, headline, CTA button, background video with fade-in/out loop, and a logo marquee. Use React + Vite + Tailwind CSS + TypeScript with shadcn/ui. Install @fontsource/geist-sans.

1. Theme & Design Tokens (index.css)
Set up a single dark theme (no light mode toggle). All colors in HSL:
:root {
  --background: 260 87% 3%;
  --foreground: 40 6% 95%;
  --card: 240 6% 9%;
  --card-foreground: 40 6% 95%;
  --popover: 240 6% 9%;
  --popover-foreground: 40 6% 95%;
  --primary: 262 83% 58%;
  --primary-foreground: 0 0% 100%;
  --secondary: 240 4% 16%;
  --secondary-foreground: 40 6% 95%;
  --muted: 240 4% 16%;
  --muted-foreground: 240 5% 65%;
  --accent: 262 83% 58%;
  --accent-foreground: 0 0% 100%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 0 0% 100%;
  --border: 240 4% 20%;
  --input: 240 4% 20%;
  --ring: 262 83% 58%;
  --radius: 0.75rem;
  --hero-heading: 40 10% 96%;
  --hero-sub: 40 6% 82%;
}

Body font: 'Geist Sans', 'Inter', system-ui, sans-serif
Import these font weights:
@import "@fontsource/geist-sans/400.css";
@import "@fontsource/geist-sans/500.css";
@import "@fontsource/geist-sans/600.css";
@import "@fontsource/geist-sans/700.css";

2. Liquid Glass Utility (index.css)
Add a .liquid-glass utility class in @layer utilities:
.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

3. Tailwind Config
Add these to tailwind.config.ts:
All the semantic color tokens mapped to hsl(var(--token))
A hero color group: hero.heading and hero.sub
A marquee keyframe: 0% { transform: translateX(0%) } → 100% { transform: translateX(-50%) }
Animation: marquee: "marquee 20s linear infinite"

4. Button Variants
In the shadcn button.tsx, add two custom variants:
hero: "bg-primary text-primary-foreground rounded-full px-6 py-3 text-base font-medium hover:bg-primary/90"
heroSecondary: "liquid-glass text-foreground rounded-full px-6 py-3 text-base font-normal hover:bg-white/5"

5. Navbar Component
Full-width, py-5 px-8, flex row, justify-between
Left: A logo image (32px height). Use a logo.png from src/assets/logo.png
Center: Nav items as plain buttons: "Features" (with ChevronDown icon), "Solutions", "Plans", "Learning" (with ChevronDown icon). Text is text-foreground/90 text-base, gap-1 between items
Right: "Sign Up" button using heroSecondary variant, size="sm", rounded-full px-4 py-2
Below the navbar, add a full-width 1px gradient divider: mt-[3px] w-full h-px bg-gradient-to-r from-transparent via-foreground/20 to-transparent

6. Hero Section
Section with bg-background relative overflow-hidden
Contains the Navbar at the top
Below navbar + divider, centered content with pt-20 px-4
Headline "Grow": text-[230px] font-normal leading-[1.02] tracking-[-0.024em], font-family 'General Sans', sans-serif, bg-clip-text text-transparent with background-image: linear-gradient(223deg, #E8E8E9 0%, #3A7BBF 104.15%)
Subtext: text-hero-sub text-center text-lg leading-8 max-w-md mt-4 opacity-80, two lines: "The most powerful AI ever deployed" / "in talent acquisition" (split with <br/>)
CTA Button: heroSecondary variant, text "Schedule a Consult", px-[29px] py-[24px], wrapped in a div with mt-8 mb-[66px]

7. Social Proof / Video Section
Immediately below the hero, a separate <section> with relative w-full overflow-hidden.
Background Video: <video> element: autoPlay muted playsInline, absolute inset-0 w-full h-full object-cover, initial style={{ opacity: 0 }}
Source URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260308_114720_3dabeb9e-2c39-4907-b747-bc3544e2d5b7.mp4
Fade logic (JavaScript): Use requestAnimationFrame to continuously read currentTime and duration. Fade in over 0.5s at the start, fade out over 0.5s at the end. On ended, set opacity to 0, wait 100ms, reset currentTime = 0, and play() again. This creates a seamless manual loop with fade transitions.
Gradient overlays: absolute inset-0 bg-gradient-to-b from-background via-transparent to-background
Content (z-10): flex flex-col items-center pt-16 pb-24 px-4 gap-20
A h-40 spacer div for video visibility

Logo Marquee at max-w-5xl:
Left side: text "Relied on by brands / across the globe" in text-foreground/50 text-sm, with <br/>, whitespace-nowrap shrink-0
Right side: horizontally scrolling marquee using animate-marquee (the 20s infinite animation)
Logos are placeholder brands: Vortex, Nimbus, Prysma, Cirrus, Kynder, Halcyn — duplicated for seamless loop
Each logo: a small liquid-glass w-6 h-6 rounded-lg square with the first letter, plus the brand name in text-base font-semibold text-foreground
Gap between logos: gap-16

8. Page Composition
The Index page simply renders <HeroSection /> then <SocialProofSection /> sequentially with no wrapper styling.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Luxury Ecommerce Design"
template_id: "41a92961-434d-4113-9cf8-b91c8002c683"
section: "sites"
category_slug: "ecommerce"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Luxury Ecommerce Design

> **Секція:** `SITES` | **Категорія:** `ecommerce`  
> **ID шаблону:** `41a92961-434d-4113-9cf8-b91c8002c683`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Ecommerce

### 🖼 Прев'ю:
![Luxury Ecommerce Design](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/25cb6020-214c-4bfc-94ae-27b43a73a577.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a React + Tailwind CSS beauty/skincare brand landing page called "STRETCH" with 3 sections. Use Vite, React 18, TypeScript, Tailwind CSS, and lucide-react for icons. The system font stack is used (no custom fonts loaded). The page has smooth scroll-triggered fade-in animations using IntersectionObserver, button hover lift animations, and full responsive design with a mobile hamburger menu.

---

## SECTION 1: HERO (Full viewport height, split 50/50 on desktop, stacked on mobile)

**Announcement Bar** (absolute positioned, top of page, z-30):
- Background: `#F9F4F0`, text black
- Centered text: "free shipping for orders over 50€"
- ChevronLeft and ChevronRight icons (size 16) on each side
- Padding: `py-2.5` mobile, `py-3` desktop

**Navigation** (absolute positioned below announcement bar at `top-[38px]` mobile / `top-[42px]` desktop, z-30):
- Left: Logo text "STRETCH" — `text-lg sm:text-xl font-bold tracking-[0.2em] uppercase`
- Center (hidden on mobile, visible md+): 4 links — "shop", "learn", "journal", "theme" — `text-sm`, with an underline animation on hover (a `<span>` inside that goes from `w-0` to `w-full` on group-hover, `h-[1px] bg-white transition-all duration-300`)
- Right: 
  - French flag (3 colored divs: `bg-blue-700`, white, `bg-red-600` in a `w-6 h-4` container) + "eur €" text + ChevronDown — hidden on mobile
  - Vertical divider `w-px h-5 bg-white/30 mx-2` — hidden on mobile
  - User icon (hidden below sm), Search icon, ShoppingBag icon (all size 20)
  - Menu/X hamburger toggle (visible below md)

**Mobile Menu** (fixed fullscreen overlay, z-40):
- `bg-black/95 backdrop-blur-sm`
- Centered vertically: same 4 nav links at `text-3xl font-light`
- Transition: `opacity` + `pointer-events` toggle over `duration-500`

**Hero Left Half** (`w-full lg:w-1/2`, `min-h-[60vh] lg:min-h-0`):
- Background: Full-bleed absolute image:
  ```
  https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260516_101925_8e509c31-4e75-4ae1-b164-2605265b2d47.png&w=1280&q=85
  ```
- Content (relative z-10, fade-in animation: `translate-y-8` to `translate-y-0`, `opacity-0` to `opacity-100`, `duration-1000`):
  - Heading: "ethical beauty," (line break) "sustainable impact." — `text-4xl sm:text-5xl md:text-6xl lg:text-[clamp(3.5rem,5vw,6rem)] font-light leading-[1.05] mb-6`
  - Under "impact." word: decorative SVG with 3 wavy gold lines (`stroke="#C8A45C"`, strokeWidths 2, 1.5, 1) — absolutely positioned `-bottom-1 left-0 w-full h-4`
  - Paragraph: "Committed to sustainable beauty and minimize our impact on the planet." — `text-sm md:text-base text-white/80 mb-10 max-w-md`
  - Button: "about us" — `px-10 py-4 bg-white text-black rounded-full text-sm` with `.btn-primary` class

**Hero Right Half** (`w-full lg:w-1/2`, `min-h-[40vh] lg:min-h-0`):
- Video slideshow (3 slides, auto-advances every 5000ms):
  - Video 1: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260516_112022_cddf2487-4ffe-45b6-ba4c-99ab79003cc5.mp4`
  - Video 2: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_175400_b46d1cd2-2050-45e2-9d13-b9c0bacb16b3.mp4`
  - Video 3: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_182440_671605c8-2ed8-4507-a4cb-a62a8f61316f.mp4`
  - All videos: `autoPlay loop muted playsInline`, `object-cover`, absolute `inset-0`
  - Transition between slides: `transition-opacity duration-700`
- Controls (absolute `bottom-6 right-6` z-20):
  - 3 dot indicators: `w-2 h-2 rounded-full`, active = `bg-white scale-125`, inactive = `bg-white/50`
  - Pause/Play toggle button: `w-8 h-8 rounded-full border border-white/50`, Pause/Play icon size 14

---

## SECTION 2: BEST SELLERS (Background `#F9F4F0`, text black)

- Padding: `py-12 sm:py-16 px-4 sm:px-6 lg:px-10`
- Fade-in animation on scroll (translate-y-6 to 0, opacity 0 to 1)

**Tabs:**
- Two buttons: "best sellers" and "sets"
- Text: `text-2xl sm:text-4xl md:text-5xl font-medium`
- Active tab: `text-[#1a1a1a]` with a filled dot `w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-[#1a1a1a]` that has a scale-in CSS animation
- Inactive tab: `text-gray-400`, hover → `text-gray-600`

**Product Carousel** (horizontal scroll, `overflow-x-auto scrollbar-hide`):
- Vertical scroll (mouse wheel) is hijacked to scroll horizontally
- Each product card: `w-[260px] sm:w-[280px] md:w-[300px] lg:w-[calc(25%-1px)]`
- Cards have `border border-gray-200` on all 4 sides, with `-ml-[1px] first:ml-0` to collapse shared borders
- Cards fade in staggered: each card has `transitionDelay: ${200 + index * 80}ms`
- On hover: product image scales to 105% (`transition-transform duration-500`)

**7 Products (in order):**
1. Category: "ILLUMINATE" | Name: "Illuminating cleansing gel" | Price: "€36,00" | Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260518_193822_8c95f5ed-b142-454f-ab87-59ad1f09e758.png&w=1280&q=85`
2. Category: "UNIFY" | Subcategory: "TIGHTEN PORES" | Name: "Unifying serum spray" | Price: "€34,00" | Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260518_194048_278bf3cc-7d1f-43c1-9dc7-73d8fcd9949c.png&w=1280&q=85`
3. Category: "NATURAL GLOW" | Name: "Super glow set" | Price: "€92,00" | Old price: "€99,00" | Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260518_194058_d89610de-05f8-45e4-8196-0680296c565a.png&w=1280&q=85`
4. Category: "PROTECT" | Subcategory: "ILLUMINATE" | Name: "Radiance day oil" | Price: "€59,00" | Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260518_194112_1763cbb2-3171-4ad3-9f38-1b738b8f1bb6.png&w=1280&q=85`
5. Category: "HYDRATE" | Subcategory: "NOURISH" | Name: "Deep moisture cream" | Price: "€48,00" | Image: same as product 1
6. Category: "RENEW" | Name: "Night repair elixir" | Price: "€72,00" | Old price: "€79,00" | Image: same as product 2
7. Category: "SMOOTH" | Subcategory: "REFINE" | Name: "Gentle exfoliating toner" | Price: "€42,00" | Image: same as product 3

**Card layout:**
- Top: category label (`text-xs font-medium tracking-wider uppercase`) + optional subcategory (`text-xs text-gray-500 uppercase mt-0.5`) in a `px-4 h-12` container
- Middle: image in `mx-4 aspect-[3/4] rounded-lg overflow-hidden bg-[#F9F4F0]`, `object-cover`
- Bottom: product name (`text-sm`, centered) + price row (with optional strikethrough old price in `text-gray-400 line-through`)

**Scroll Progress Bar:**
- `mt-8 sm:mt-10 mx-auto max-w-[280px]`
- Track: `h-[2px] bg-gray-300 rounded-full`
- Thumb: `width: 30%`, `bg-[#1a1a1a]`, position calculated as `translateX(${scrollProgress * (100 / 0.3)}%)`

---

## SECTION 3: CATEGORIES (Background black, text white)

- 3-column grid on desktop (`grid-cols-1 md:grid-cols-3`), no gaps, no dividers between columns
- Fade-in animation on scroll (translate-y-12 to 0, opacity 0 to 1, duration-1000)

**3 Category Cards (each):**
- Min height: `min-h-[400px] sm:min-h-[500px] md:min-h-[750px]`
- Padding: `p-6 sm:p-8 md:p-12`
- Full-bleed background video (absolute, `object-cover`)
- On hover: video scales to 105% (`transition-transform duration-700`)
- Dark overlay: `bg-black/10` → hover `bg-black/20` (`transition-colors duration-500`)
- Vertical text (rotated): `writingMode: 'vertical-lr', transform: 'rotate(180deg)'` — `text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-medium` — moves up 2px on hover
- Button at bottom: "shop [name]" — `px-8 py-3 bg-white text-black rounded-full text-sm` with `.btn-primary`

**Category data:**
1. Name: "face" | Video: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_203023_87a26602-2898-4acc-a396-c7a2b5ad84fd.mp4`
2. Name: "beauty tools" | Video: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_203415_b86e3f19-2aec-46cd-9a86-b64c40118e38.mp4`
3. Name: "body" | Video: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_203051_85fee398-ea01-4aa0-972b-137a74213be5.mp4`

---

## CSS (index.css):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.btn-primary {
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.btn-primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 0%, rgba(0, 0, 0, 0.05) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn-primary:hover::before {
  transform: translateX(100%);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@keyframes scale-in {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.animate-scale-in {
  animation: scale-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## ANIMATIONS SUMMARY:
1. **useInView hook** — custom IntersectionObserver hook (threshold configurable, default 0.15). Once element enters viewport, sets `isVisible = true` permanently (unobserves after).
2. **Hero text** — fades in + slides up 8px over 1000ms
3. **Best sellers tabs** — fades in + slides up 6px over 800ms
4. **Product cards** — staggered fade-in (each 80ms apart, starting at 200ms delay), slides up 8px over 500ms
5. **Categories section** — fades in + slides up 12px over 1000ms
6. **Tab dot** — scale-in keyframe with bounce easing `cubic-bezier(0.34, 1.56, 0.64, 1)` over 300ms
7. **Buttons (.btn-primary)** — lift 2px + shadow on hover, light sweep effect via `::before` pseudo-element
8. **Product images** — scale to 105% on card hover over 500ms
9. **Category videos** — scale to 105% on card hover over 700ms
10. **Nav links** — underline grows from left (`w-0` to `w-full`) over 300ms on hover

---

## TECH STACK:
- Vite + React 18 + TypeScript
- Tailwind CSS 3.4
- lucide-react for icons (ChevronLeft, ChevronRight, User, Search, ShoppingBag, ChevronDown, Pause, Play, Menu, X)
- No other UI libraries
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Layered Depth"
template_id: "99571c25-1552-426b-bfc5-c5e383e1ea2d"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Layered Depth

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `99571c25-1552-426b-bfc5-c5e383e1ea2d`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Layered Depth](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/c4b51154-bbbc-4fcf-81a4-514716cf15d2.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a React + Vite + TypeScript + Tailwind CSS landing page for an architecture studio called "Qelora". The page has exactly two sections: a Hero and a Section 2. The entire site uses inline styles (no Tailwind utility classes in JSX -- Tailwind is only used for base reset). Use only `react`, `react-dom`, and `lucide-react` as dependencies (icons are all inline SVGs here, lucide is not actually used in this page).

---

FONTS

Load these three custom fonts in `index.html` `<head>`:

```html
<link href="https://db.onlinewebfonts.com/c/076f8c5b3b67616658dd1e4e9bac62ec?family=Zimula+Trial+Med" rel="stylesheet">
<link href="https://db.onlinewebfonts.com/c/08d8ca53f66ab5b48659912fa0136b78?family=Zimula+Trial+Bd" rel="stylesheet">
```

Also import in `index.css`:
```css
@import url('https://db.onlinewebfonts.com/c/46024824a3dd3309c3a7f46f4f1283ba?family=Zimula+Trial+Reg');
```

Font usage:
- Body / default: `'Zimula Trial Med', sans-serif`
- Bold / logo / hero text: `'Zimula Trial Bd', sans-serif`
- The `Reg` import is available but Med is the primary weight used everywhere

---

GLOBAL CSS (`index.css`)

```css
@import url('https://db.onlinewebfonts.com/c/46024824a3dd3309c3a7f46f4f1283ba?family=Zimula+Trial+Reg');

@tailwind base;
@tailwind components;
@tailwind utilities;

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Zimula Trial Med', sans-serif;
  background: #0e0c0a;
  overflow-x: hidden;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0e0c0a; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
```

---

COLOR PALETTE

- Dark background: `#0e0c0a`
- Primary text: `#241f21`, `#282425`, `#2a2420`
- White: `#fff`
- Dark accent: `#100e0c`
- Warm transparent overlays: `rgba(235, 230, 218, 0.12)`, `rgba(242, 238, 230, 0.38)`
- Frosted glass backgrounds: `rgba(248,245,240,0.72)`, `rgba(248,245,240,0.88)`, `rgba(248,245,240,0.92)`, `rgba(248,245,240,0.96)`

---

ASSET URLs (Cloudinary, not CloudFront)

Videos:
- Background video (Hero): `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/f_auto/v1779808200/bg-video_xsmysw.mp4`
- Bird enter animation: `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/v1779808206/bird-entrada_e72qt7.webm`
- Bird idle 1: `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/v1779808282/bird-idle_fzjami.webm`
- Bird idle 2: `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/v1779808284/bird-idle2_rajmgo.webm`
- Bird leave animation: `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/v1779808286/bird-saida_ifroz1.webm`
- Background video (Section 2): `https://res.cloudinary.com/dy5er7kv5/video/upload/q_auto/f_auto/v1779835701/bg-2-video_sgbpqt.mp4`

Images:
- Q logo (unused but declared): `https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779808187/q-logo_isvugc.png`
- Center sculpture/slab: `https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1779854565/slab_v1_kb4vqk.png`
- CTA card photo (Pexels): `https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=400`

---

APP STRUCTURE

```
src/
  main.tsx      -> StrictMode, renders 
  App.tsx       ->  then , no routing
  Hero.tsx      -> Hero section component
  Section2.tsx  -> Second section component
  index.css     -> Global styles
```

---

SECTION 1: HERO (`Hero.tsx`)

Container: `position: relative`, `width: 100%`, `minHeight: 100vh`, `overflow: visible`, `fontFamily: 'Zimula Trial Med', sans-serif`.

Responsive breakpoint: `isMobile = window.innerWidth < 768`, checked on mount and resize.

Layer 1 -- Background Video (z-index: 0)
- `` with `autoPlay muted loop playsInline`
- `position: absolute`, `inset: 0`, `width: 100%`, `height: 100vh`, `objectFit: cover`
- Source: `BG_VIDEO` URL

#### Layer 2 -- Warm Overlay (z-index: 1)
- A div covering the hero with `background: rgba(235, 230, 218, 0.12)`, `height: 100vh`, `pointerEvents: none`

#### Layer 3 -- Bird Animation System (z-index: 8)
- Container: `position: absolute`, `top: 0`, `left: 0`, `width: 100%`, `height: 100vh`, `pointerEvents: none`, `aria-hidden`
- Contains 4 `` elements (enter, idle1, idle2, leave), each toggled visible/hidden via `display` property
- **Desktop:** Each video is `position: absolute`, `inset: 0`, `width: 100%`, `height: 100%`, `objectFit: cover`
- **Mobile:** Each video is `position: absolute`, `top: 50%`, `left: 0`, `transform: translateY(-50%)`, `width: 100%`, `height: auto` (full width, auto height, vertically centered)
- **State machine:** Type `'enter' | 'idle1' | 'idle2' | 'leave' | 'hidden'`
  - On page load: play `enter` video
  - When `enter` ends: transition to `idle1`
  - When `idle1` ends: transition to `idle2`
  - When `idle2` ends: transition back to `idle1` (infinite loop)
  - **On scroll down** (past 10px threshold): pause all idle/enter videos, reset their `currentTime` to 0, play `leave` video
  - **On scroll back to top** (below 10px): pause leave video, reset, play `enter` video again
- Uses both React state and refs (`birdStateRef`) to avoid stale closures in scroll handlers
- All videos are preloaded with `.load()` on mount
- The `playVideo` helper sets `currentTime = 0`, checks `readyState >= 2`, then plays (or waits for `canplay` event)

#### Layer 4 -- Center Brand Text "Qelora" (z-index: 5)
- Absolutely positioned container filling `100vh`, `display: flex`, `alignItems: center`, `justifyContent: center`, `pointerEvents: none`
- Text: `"Qelora"` in `'Zimula Trial Bd', sans-serif`
- Font size: mobile `26vw`, desktop `22vw`
- `letterSpacing: -0.05em`, `color: #241f21`, `lineHeight: 1`
- `marginBottom`: mobile `8vh`, desktop `12vh`

#### Layer 5 -- Sculpture Image (z-index: 5)
- `` with `position: absolute`, `top: 50%`, `left: 50%`
- `transform: translateX(-50%) translateY(${-heroScroll  0.3}px)` -- parallax that moves UP as user scrolls down
- Width: mobile `220vw`, desktop `160vw`; `height: auto`
- `pointerEvents: none`, `willChange: transform`

#### Layer 6 -- Fixed Navbar (z-index: 100)
- `position: fixed`, `top: 0`, full width
- Padding: mobile `16px 20px`, desktop `20px 36px`
- **Left:** Brand name "Qelora" with registered trademark superscript. Font: `'Zimula Trial Bd'`, size: mobile `20px`, desktop `24px`, `letterSpacing: -0.03em`, `color: #241f21`. The `(R)` sup has `fontSize: 0.4em`, `verticalAlign: super`
- **Right (desktop):** `NavPills` component -- a row of pill buttons for `['Projects', 'Studio', 'Responsibility', 'Archive']` plus an `EN` language selector
  - Each pill: `background: rgba(248,245,240,0.92)`, `borderRadius: 12px`, `padding: 13px 22px 8px`, `height: 40px`, `fontSize: 13px`, `textTransform: uppercase`, `letterSpacing: 0.07em`, `color: #241f21`
  - Active pill has `fontWeight: 700` and a 3px round dot at `bottom: 3px`, centered
  - Non-active: `fontWeight: 500`
  - Language pill: separate rounded capsule (`borderRadius: 100px`), `padding: 8px 14px`, `background: rgba(248,245,240,0.88)`, `backdropFilter: blur(12px)`, `boxShadow: 0 2px 20px rgba(0,0,0,0.1)`, contains "EN" text and a chevron-down SVG
- **Right (mobile):** Hamburger button, `42x42px`, `borderRadius: 100px`, same frosted glass style. Shows X icon when open, 3-line hamburger when closed

#### Layer 7 -- Mobile Dropdown Menu (z-index: 99)
- `position: fixed`, `top: 70px`, `left: 16px`, `right: 16px`
- `background: rgba(248,245,240,0.96)`, `backdropFilter: blur(16px)`, `borderRadius: 18px`, `padding: 8px`, `boxShadow: 0 8px 40px rgba(0,0,0,0.14)`
- Each menu item: full-width button, `padding: 14px 20px`, `fontSize: 13px`, uppercase, `letterSpacing: 0.07em`, `borderBottom: 1px solid rgba(40,36,37,0.08)`
- Bottom: EN language selector row

#### Layer 8 -- Bottom Panels (z-index: 20)
- `bottom` is calculated as: `bottomOffset + heroScroll  0.5` where `bottomOffset` is 24px on mobile, 36px on desktop. This creates a parallax push-down effect as user scrolls.

**Desktop layout (side-by-side):**

- **Bottom-left panel:** `position: absolute`, `left: 36px`, `borderRadius: 18px`, `padding: 22px 28px`, `maxWidth: 270px`
  - Headline: `"Designing places\nbeyond\nwhat's expected"` -- `fontSize: clamp(17px, 2vw, 24px)`, `lineHeight: 1.28`, `color: #282425`, `letterSpacing: -0.01em`
  - Below: 1px border-top divider (`rgba(40,36,37,0.2)`), then "EXPLORE OUR APPROACH" link with down-arrow SVG. `fontSize: 11px`, uppercase, `letterSpacing: 0.1em`

- **Bottom-right panel:** `position: absolute`, `right: 36px`, `borderRadius: 18px`, `width: clamp(210px, 21vw, 290px)`, `height: 180px`, `overflow: hidden`
  - Background: Pexels photo covering the entire card
  - Dark gradient overlay: `linear-gradient(to bottom, rgba(16,14,12,0.55) 0%, transparent 60%)`
  - Top text: `"Every lasting space begins\nwith a quiet dialogue."` -- `color: #fff`, `fontSize: 13px`, `lineHeight: 1.35`
  - Bottom: inline flex with a white circle (envelope SVG icon, 36x36px, `borderRadius: 12px`) and a white "START A PROJECT" button (`fontSize: 11px`, uppercase, `letterSpacing: 0.07em`, `fontWeight: 700`, `borderRadius: 12px`, `height: 36px`)

**Mobile layout (stacked):**
- Single flex column container, `left: 20px`, `right: 20px`, `gap: 12px`
- **Top card:** Tagline panel with `background: rgba(248,245,240,0.72)`, `backdropFilter: blur(8px)`, `borderRadius: 16px`, `padding: 18px 20px`. Same text as desktop but single line: "Designing places beyond what's expected", `fontSize: 17px`. Same divider + "Explore our approach" link below.
- **Bottom card:** CTA card, `borderRadius: 16px`, `height: 120px`. Same structure as desktop right panel but adapted for mobile (text `fontSize: 12px`, same button row).

---

### SECTION 2 (`Section2.tsx`)

**Container:** `position: relative`, `width: 100%`, `minHeight: 100vh`, `display: flex`, `flexDirection: column`, `alignItems: center`, `justifyContent: center`, `overflow: hidden`, `fontFamily: 'Zimula Trial Med', sans-serif`

#### Layer 1 -- Background Video (z-index: 0)
- `` with `autoPlay muted loop playsInline`, `position: absolute`, `inset: 0`, `width: 100%`, `height: 100%`, `objectFit: cover`
- Source: `BG_VIDEO_2` URL

#### Layer 2 -- Warm Overlay (z-index: 1)
- `background: rgba(242, 238, 230, 0.38)`, `position: absolute`, `inset: 0`, `pointerEvents: none`

#### Layer 3 -- Center Headline (z-index: 2)
- Absolutely positioned, `inset: 0`, flex centered, `pointerEvents: none`, `textAlign: center`, `padding: 0 24px`
- Text: `"What stands the\ntest of time is all\nthat guides the\nwork."` using `
` tags
- `fontSize: clamp(32px, 5.5vw, 80px)`, `lineHeight: 1.18`, `color: #2a2420`, `maxWidth: 780px`, `letterSpacing: -0.025em`, `fontWeight: 400`

#### Layer 4 -- Bottom Element (z-index: 2)
- `position: absolute`, `bottom: clamp(24px, 4vh, 48px)`, full width, flex column centered, `padding: 0 24px`
- **Vertical line:** `width: 1px`, `height: 56px`, `background: rgba(42,36,32,0.25)`
- **Below (margin-top: 22px):** flex column centered, `gap: 14px`
  - **Map pin SVG:** 24x28px outline pin icon, `stroke: #2a2420`, `strokeWidth: 1.4`
  - **Subtext:** `"Civic bodies and private clients trust us to shape resilient communities and purposeful places."` -- `fontSize: clamp(11px, 1.4vw, 13px)`, `color: #2a2420`, `letterSpacing: 0.04em`, `lineHeight: 1.6`, `maxWidth: 340px`, `opacity: 0.75`

---

### KEY BEHAVIORS SUMMARY

1. **Bird animation state machine:** enter -> idle1 <-> idle2 loop; scroll triggers leave; scroll back triggers re-enter
2. **Parallax effects:** Sculpture image moves up with `translateY(-scrollY  0.3)`. Bottom panels push down with `bottom = offset + scrollY  0.5`
3. Responsive at 768px breakpoint: Nav collapses to hamburger, panels stack vertically, bird videos switch from cover-fill to width-100%/height-auto/vertically-centered, sculpture grows from 160vw to 220vw, brand text grows from 22vw to 26vw
4. All styling is inline -- no CSS classes in JSX, no Tailwind utility classes on elements
5. No third-party animation libraries -- all animations are native video playback + scroll-driven inline style changes via React state
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "IntelligentX"
template_id: "62f9072f-395b-4c1d-b777-c0cbc37f9434"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 IntelligentX

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `62f9072f-395b-4c1d-b777-c0cbc37f9434`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![IntelligentX](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/40cb1730-46ee-4ce8-9fdf-dbb203e5be00.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Prompt:
Build a modern React landing page using Vite, Tailwind CSS, and motion/react for elegant animations. The application must feature a highly polished, aesthetic hero section and a glassmorphic navigation bar.
1. Typography & Global CSS (src/index.css)
Import the fonts "Inter" and "Outfit" from Google Fonts.
Set --font-sans to Inter and --font-display to Outfit.
Set --color-brand-green to #9fff00 and --color-bg-base strictly to #EDEEF5.
Ensure the body uses @apply bg-bg-base text-zinc-900 font-sans antialiased; to carry the #EDEEF5 background throughout the entire page.
2. Component Structure (src/App.tsx)
Import Navbar and Hero.
Return a div containing the <Navbar /> and <main><Hero /></main>.
Set the wrapper container classes to min-h-screen bg-bg-base selection:bg-brand-green selection:text-black.
3. Navbar Component (src/components/Navbar.tsx)
Give it fixed styling: fixed top-0 left-0 w-full z-50 py-6 md:py-10 bg-gradient-to-b from-[#f1f1f1]/80 to-transparent backdrop-blur-[2px].
Container layout: A 12-column grid (grid-cols-12 max-w-7xl mx-auto).
Left (Cols 1-3): A geometric flower/clover SVG icon (fill: #1a1a1a) beside the brand name "mėntality" using the display font.
Center (Cols 4-9): Desktop-only hidden nav links: "service", "patient resources", "about us", "education center". Styled small and lowercase.
Right (Cols 10-12): "find help" anchor link, a black rounded button reading "get started →", and an elegant animated hamburger toggle icon for mobile.
Include an AnimatePresence and motion.div drawer that slides down for mobile with the navigation links.
4. Hero Component (src/components/Hero.tsx)
Main styling: <section className="relative min-h-[110vh] sm:min-h-[140vh] w-full flex flex-col items-center justify-start overflow-hidden bg-bg-base">
Background Video Container:
Absolute wrapper: <div className="absolute top-[15vh] sm:top-[20vh] left-0 w-full h-[95vh] sm:h-[120vh] z-0 pointer-events-none">
The video itself should be <video autoPlay loop muted playsInline className="w-full h-full object-cover opacity-100" />
Exact CloudFront URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260603_132049_036591b8-6e92-4760-b94c-a7ea6eef315c.mp4
Gradient Mask: Below the video in the wrapper, add <div className="absolute top-0 left-0 w-full h-24 sm:h-32 bg-gradient-to-b from-bg-base to-transparent"></div> to smoothly blend the video into the #EDEEF5 background.
Hero Content Alignment: Use <div className="max-w-7xl w-full mx-auto px-8 md:px-16 lg:px-20 relative z-10 grid grid-cols-12 gap-x-4 md:gap-x-8">. Place the text in col-span-12 md:col-span-10 md:col-start-2.
Hero Header (motion.h1): Needs a slide-up fade (initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}).
Exact text formatting:
[#1a1a1a] Remix: Mentality offers
[#8e8e8e] information
(line break)
[#8e8e8e] and resources to help you manage
(line break)
[#8e8e8e] your [Eye Icon Puipl UI Element] mental wellbeing.
For the Eye Icon Element between "your" and "mental", create an inline pill-shaped visual: w-[16px] md:w-[42px] lg:w-[62px] border-[2px] border-[#1a1a1a] rounded-full inline-flex items-center justify-center containing a tiny solid black dot (w-2 h-2).
Search Pill Component:
Add a delayed slide-up animation (delay: 0.15) under the header text.
Make a custom capsule <div className="bg-white rounded-[6px] border border-black/[0.05] p-1 pl-4 flex items-center shadow-sm">.
Include an <input placeholder="Ask me anything..."> with transparent background so it looks integrated.
Trailing action button: <button className="bg-[#1a1a1a] text-white w-9 h-9 rounded-full relative"> containing an SVG chevron/arrow icon.
Architectural Edge Anchors:
Absolute middle right edge: Create a glassmorphic pill button for language switching (pl — en).
Absolute bottom left corner: Place "2024" in small neat text.
Absolute bottom right corner: Place "mental health tools" in small neat text.
Ensure there are no artificial margins/padding below the video to make sure the video takes exactly 100% of the Hero viewport, while allowing the #EDEEF5 background base to anchor the entire page cleanly.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Glassmorphism Agency"
template_id: "bc98e01b-5962-46a1-b889-d92bb252ec3c"
section: "sites"
category_slug: "agency"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Glassmorphism Agency

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `bc98e01b-5962-46a1-b889-d92bb252ec3c`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency

### 🖼 Прев'ю:
![Glassmorphism Agency](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/cdfe1de8-ab9b-4089-8681-7109e858a5e9.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a production-ready, responsive landing page using React, Tailwind CSS v4, and Vite. The design should feature a high-end, dark-mode "glassmorphism" aesthetic with specific purple/pink gradients.

1. Tech Stack & Libraries:
Use hls.js for video streaming.
Use motion/react (formerly Framer Motion) for animations.
Use react-use-measure for sizing logic.
Use clsx and tailwind-merge for class management.
Use lucide-react for standard icons (if needed), but I will provide custom SVG paths for specific UI elements.

2. Global Styling:
Background: Dark/Black (#010101).
Primary Gradient: A diagonal gradient used for accents: from-[#FA93FA] via-[#C967E8] to-[#983AD6].
Typography: Modern sans-serif, center-aligned hero text.

3. Hero Section Components:
Announcement Pill:
A pill-shaped top badge.
Background: Semi-transparent dark (bg-[rgba(28,27,36,0.15)]) with a subtle border.
Icon: A "Zap" icon inside a gradient-filled box with a glow effect.
Text: "Used by founders. Loved by devs." in light grey.

Main Headline (H1):
Large text (responsive sizing: 48px mobile to 80px desktop).
Text: "Your Vision" on line 1, "Our Digital Reality." on line 2.
Style: Text should have a gradient fill (White to Purple/Pink).

Subheadline:
Text: "We turn bold ideas into modern designs that don't just look amazing, they grow your business fast."
Color: text-white/80.

CTA Button:
"Book a 15-min call" text.
Rounded full button with a white background and black text.
Includes a circle icon with an arrow inside, styled with the primary purple gradient.
Outer border wrapper with a glass effect.

4. Hero Video Integration (Critical Details):
Source: HLS Stream URL: https://customer-cbeadsgr09pnsezs.cloudflarestream.com/697945ca6b876878dba3b23fbd2f1561/manifest/video.m3u8
Fallback: If HLS fails, fallback to this MP4: /_videos/v1/f0c78f536d5f21a047fb7792723a36f9d647daa1
Implementation: Do NOT use react-player. Use a native <video> tag with a custom useEffect hook implementation of hls.js.
Styling:
Blend Mode: Use mix-blend-screen so the video black background blends into the page.
Positioning: The video should be at the bottom of the hero. Apply a negative top margin (-mt-[150px]) so it overlaps behind the text.
Z-Index: Ensure the text content is z-20 (above) and video is z-10 (below).
Layout: The video must be 100% width (w-full), auto height, and stretch edge-to-edge without being cropped (do not use object-contain or fixed heights).
Overlay: Add a gradient fade (from-[#010101] via-transparent to-[#010101]) over the video container.

5. Logo Cloud Section (Animated):
Place this section immediately below the video.
Background: Semi-transparent glass (bg-black/20 backdrop-blur-sm) with a top border (border-white/5).
Layout:
Desktop: "Powering the best teams" text on the left, separated by a vertical divider. Animated logo slider on the right.
Mobile: Stacked vertically.
Animation: Create an InfiniteSlider component using motion/react that scrolls logos horizontally forever.
Logos: Use these SVG URLs (OpenAI, Nvidia, GitHub, etc.) and apply brightness-0 invert to make them white.
https://html.tailus.io/blocks/customers/openai.svg
https://html.tailus.io/blocks/customers/nvidia.svg
(Include others similarly)

Please assemble these into a cohesive Hero.tsx, App.tsx, and components/ui/infinite-slider.tsx structure.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Retro-Futurist"
template_id: "6ee7a7f0-df58-4173-b4d9-305245467e95"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Retro-Futurist

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `6ee7a7f0-df58-4173-b4d9-305245467e95`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Retro-Futurist](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/db70fb5b-6bff-49c4-b667-d3c363f49536.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a full-screen hero landing page for a creative agency called "Mainframe" using React, TypeScript, Vite, and Tailwind CSS. Here is every detail:

---

FONTS

Load two fonts in `index.html` via these stylesheet links:
- Heading: `https://db.onlinewebfonts.com/c/5ac3fe7c6abd2f62067f266d89671492?family=HelveticaNowDisplay-Medium`
- Body: `https://db.onlinewebfonts.com/c/1aa3377e489837a26d019bba501e779d?family=HelveticaNowDisplayW01-Rg`

In `index.css`, define CSS variables:
```css
:root {
  --font-heading: 'HelveticaNowDisplay-Medium', 'Helvetica Neue', Arial, sans-serif;
  --font-body: 'HelveticaNowDisplayW01-Rg', 'Helvetica Neue', Arial, sans-serif;
}
body {
  font-family: var(--font-body);
}
```

The entire page uses `var(--font-body)` except the logo text which uses `var(--font-heading)`.

---

BACKGROUND VIDEO (mouse-scrub controlled)

- A full-screen `` element is `position: fixed; inset: 0; z-index: 0; object-fit: cover; object-position: 70% center;`.
- Video source URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260530_042513_df96a13b-6155-4f6e-8b93-c9dee66fba08.mp4`
- The video is `muted`, `playsInline`, `preload="auto"`. It does NOT autoplay.
- The video scrubs forward/backward based on horizontal mouse movement. Use a `mousemove` event listener on `window`. Track `prevX`, compute `delta = currentX - prevX`, convert to a time offset: `(delta / window.innerWidth)  SENSITIVITY  video.duration` where `SENSITIVITY = 0.8`. Clamp `targetTime` between 0 and `video.duration`. Use `video.currentTime` to seek, and an `onSeeked` handler to queue the next seek if `targetTime` has moved, preventing seek-flooding.

---

**NAVBAR (fixed, z-index: 10)**

- Fixed to top, full width. Padding: `px-5 sm:px-8 py-4 sm:py-5`. Flex row, `justify-between`, `items-center`.
- **Logo (left):** Flex row with `gap-3`. Text "Mainframe(R)" (use the registered trademark symbol) at `text-[21px] sm:text-[26px]`, `tracking-tight`, black, using `var(--font-heading)`. Beside it, a decorative asterisk character `✳︎` at `text-[25px] sm:text-[30px]`, black, `select-none`, `letter-spacing: -0.02em`.
- **Desktop nav links (center, hidden below md):** Flex row, `text-[23px]`, black. Links: "Labs", "Studio", "Openings", "Shop" separated by commas rendered as `, `. Each link has `hover:opacity-60 transition-opacity`.
- **Desktop CTA (right, hidden below md):** An anchor "Get in touch" at `text-[23px]`, black, `underline underline-offset-2`, `hover:opacity-60 transition-opacity`.
- **Mobile hamburger (visible below md):** A button with 3 horizontal bars (each `w-6 h-[2px] bg-black`), spaced with `gap-[5px]`. On toggle, the top bar rotates 45deg and translates down 7px, middle bar fades to opacity 0, bottom bar rotates -45deg and translates up 7px. All transitions are `duration-300`.
- **Mobile overlay (z-index: 9):** `fixed inset-0 bg-white/95 backdrop-blur-sm`, flex column, vertically centered, left-aligned with `px-8 gap-8`. Same links at `text-[32px] font-medium`, plus "Get in touch" underlined. Fades in/out with `opacity` and `pointerEvents` toggled. Hidden on md+.

---

**HERO SECTION (z-index: 1)**

- Full `h-screen`, flex column. On mobile: `justify-end pb-12`. On `md:`: `justify-center pb-0`. Horizontal padding: `px-5 sm:px-8 md:px-10`. `overflow-hidden`.
- Content container: `max-w-xl`, `relative z-10`.

**1. Blurred intro label:**
- `pointer-events-none`, `select-none`, `mb-5 sm:mb-6`.
- Font size: `clamp(18px, 4vw, 26px)`, `line-height: 1.3`, `font-weight: 400`, `color: #000`, `filter: blur(4px)`.
- Two lines of text:
  - Line 1: "Hey there, meet A.R.I.A,"
  - Line 2: "Mainframe's Adaptive Response Interface Agent"
- Separated by a `
`.

**2. Typewriter text:**
- Text: `"Glad you stopped in. Good taste tends to find us. Now, what are we building?"`
- Custom `useTypewriter` hook: takes `text`, `speed` (default 38ms per character), `startDelay` (default 600ms). After the delay, an interval reveals one character at a time. Returns `{ displayed, done }`.
- Rendered in a `

` tag, black, `mb-5 sm:mb-6`, font size `clamp(18px, 4vw, 26px)`, `line-height: 1.35`, `font-weight: 400`, `min-height: 54px`.
- While typing, show a blinking cursor: `inline-block w-[2px] h-[1.1em] bg-black align-middle ml-[2px]` with CSS animation `blink 1s step-end infinite` (`opacity: 1 at 0%/100%, 0 at 50%`). Cursor disappears when `done` is true.

**3. Action pill buttons:**
- Appear with a fade-in + slide-up animation (`opacity 0->1`, `translateY(8px)->0`, `transition: opacity 0.4s ease, transform 0.4s ease`). They become visible 400ms after page load, independent of the typewriter animation (do NOT wait for typing to finish).
- Container: `flex flex-wrap gap-y-1`.
- **4 white pill buttons:** Labels: "Pitch us an idea", "Come work here", "Send a brief hello", "See how we operate". Each is `inline-flex items-center justify-center bg-white text-black border border-black/10 rounded-full text-[13px] sm:text-[15px] px-4 sm:px-5 py-[0.3em] mx-[0.2em] mb-[0.4em] white-space: nowrap`. Hover: `bg-black text-white`, `transition-colors duration-200`.
- **1 outline pill button:** Text "Reach us: hello@mainframe.co" (email is underlined with `underline-offset-1`), followed by a small 12x12 copy icon (inline SVG of two overlapping rectangles). Styled: `text-white bg-transparent border border-white rounded-full`, same sizing as above, with `gap-2 sm:gap-3` between text and icon. Hover: `bg-white text-black`. On click, copies "hello@mainframe.co" to clipboard via `navigator.clipboard.writeText()`.

---

DEPENDENCIES

Only React, ReactDOM, Tailwind CSS, and Vite. No other UI libraries. Lucide-react is available but not used in this component.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Asme"
template_id: "b13da45e-7145-4847-a7ed-1767e4e056d5"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Asme

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `b13da45e-7145-4847-a7ed-1767e4e056d5`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero Section

### 🖼 Прев'ю:
![Asme](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/f59cc52b-900f-429d-be5c-108288f47d61.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page hero section with a full-screen looping background video, liquid glass UI elements, and a dark cinematic aesthetic. Use React, TypeScript, Tailwind CSS, and Lucide React icons. Here are the exact specifications:

Background Video:

Full-screen muted autoplaying video covering the entire viewport, positioned absolutely with object-cover
Video source URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_115001_bcdaa3b4-03de-47e7-ad63-ae3e392c32d4.mp4
The video is shifted down by 17% (translate-y-[17%]) so the top portion of the video is cropped -- the interesting content is in the lower portion of the frame
The video loops seamlessly with a custom JavaScript fade system (no CSS transitions): 500ms requestAnimationFrame-based fade-in on load/loop start, 500ms fade-out when 0.55 seconds remain before the video ends. A fadingOutRef boolean prevents re-triggering the fade-out from repeated timeUpdate events. On ended, opacity is set to 0, then after 100ms the video resets to currentTime = 0, plays, and fades back in. Each new fade cancels any running animation frame to prevent competing animations. Fades resume from the current opacity rather than snapping.
The outer container is min-h-screen bg-black with overflow-hidden

Font:

Import Google Font "Instrument Serif" (both regular and italic) via CSS @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap')
The heading uses fontFamily: "'Instrument Serif', serif" applied via inline style

Liquid Glass CSS (.liquid-glass class):

background: rgba(255, 255, 255, 0.01) with background-blend-mode: luminosity
backdrop-filter: blur(4px) and -webkit-backdrop-filter: blur(4px)
border: none
box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1)
position: relative; overflow: hidden
A ::before pseudo-element creates the glass border effect:
position: absolute; inset: 0; border-radius: inherit; padding: 1.4px
background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%, rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%, rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%)
Mask trick for border-only rendering: -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); -webkit-mask-composite: xor; mask-composite: exclude
pointer-events: none

Layout (all inside one full-screen flex column):

Navigation bar (relative z-20, padding pl-6 pr-6 py-6):
Inner container: rounded-full px-6 py-3 flex items-center justify-between max-w-5xl mx-auto
Left side: Logo area with a Globe icon (size 24) and text "Asme" in white, font-semibold text-lg, with gap-2
Next to the logo (with gap-8): three nav links ("Features", "Pricing", "About") -- hidden on mobile, shown on md: -- styled text-white/80 hover:text-white transition-colors text-sm font-medium
Right side (gap-4): "Sign Up" as plain white text button, "Login" as a liquid-glass rounded-full px-6 py-2 button

Hero content area (relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-12 text-center -translate-y-[20%]):
Heading: "Built for the curious" -- text-5xl md:text-6xl lg:text-7xl text-white mb-8 tracking-tight whitespace-nowrap with Instrument Serif font
Below the heading, a max-w-xl w-full space-y-4 container:
Email input bar: liquid-glass rounded-full pl-6 pr-2 py-2 flex items-center gap-3. Inside: a transparent email input (placeholder: "Enter your email", text-white placeholder:text-white/40 text-base) and a white circular submit button (bg-white rounded-full p-3 text-black) containing an ArrowRight icon (size 20)
Subtitle text: text-white text-sm leading-relaxed px-4 -- "Stay updated with the latest news and insights. Subscribe to our newsletter today and never miss out on exciting updates."
Manifesto button: centered, liquid-glass rounded-full px-8 py-3 text-white text-sm font-medium hover:bg-white/5 transition-colors

Social icons footer (relative z-10 flex justify-center gap-4 pb-12):
Three circular icon buttons, each liquid-glass rounded-full p-4 text-white/80 hover:text-white hover:bg-white/5 transition-all
Icons: Instagram, Twitter, Globe (all size 20) from lucide-react
Each has an aria-label

Tech stack: Vite + React 18 + TypeScript, Tailwind CSS 3, lucide-react for all icons. Default Tailwind config with no extensions. No other UI libraries.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Cursor Follow"
template_id: "3e07757d-5385-44bd-bac0-9086fb6f19aa"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Cursor Follow

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `3e07757d-5385-44bd-bac0-9086fb6f19aa`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Cursor Follow](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/daaeabba-f943-4055-a17b-a31ba36303cd.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a fullscreen hero section for a site called "Orbis.Nft" using React, TypeScript, Tailwind CSS, and Vite. Recreate every detail below precisely.

---

### Video Background with Mouse-Scrub Effect

Use this video as the fullscreen background:
```
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260525_095441_eb28d7e5-72cf-4336-a4cd-543f46f4ff20.mp4
```

The video does NOT autoplay. Instead, implement a **mouse-scrub interaction**: as the user moves their mouse left/right across the viewport, the video scrubs forward/backward through its timeline. Implementation details:

- The video is paused on load at `currentTime = 0`.
- Track the mouse's horizontal position as a normalized value (0 to 1) across `window.innerWidth`.
- On each `mousemove`, compute the delta from the previous X position. Multiply that delta by a `SENSITIVITY` constant of `0.8` and by the video's `duration` to get a time offset.
- Maintain a `targetTime` that accumulates these offsets, clamped between 0 and `duration`.
- Use the video's `seeked` event to chain seeks: when a seek completes, if `targetTime` has diverged from `currentTime` by more than 0.01s, seek again. This prevents dropped seeks since the browser can only process one seek at a time.
- Use a `useRef` to store mutable state (`targetTime`, `isSeeking` flag, `prevX`) to avoid re-renders.
- The `<video>` element has attributes: `muted`, `playsInline`, `preload="auto"`, and is styled `absolute inset-0 h-full w-full object-cover`.

---

### Google Fonts

Load two Google Fonts in `index.html` via `<link>`:
```
https://fonts.googleapis.com/css2?family=Anton&family=Condiment&display=swap
```
- **Anton** -- used for the hero heading (mapped to Tailwind as `font-grotesk`).
- **Condiment** -- a cursive script used for the accent text (mapped as `font-condiment`).

Include `<link rel="preconnect">` tags for `fonts.googleapis.com` and `fonts.gstatic.com` (with `crossorigin`).

---

### Tailwind Config

Extend the default Tailwind theme with:
- **Colors:**
  - `background`: `#010828` (deep navy)
  - `cream`: `#EFF4FF` (off-white for heading text)
  - `neon`: `#6FFF00` (bright green for the cursive accent)
- **Font families:**
  - `grotesk`: `['Anton', 'sans-serif']`
  - `condiment`: `['Condiment', 'cursive']`

---

### Global CSS (`index.css`)

```css
body {
  background-color: #010828;
  color: #EFF4FF;
  margin: 0;
  overflow-x: hidden;
}
```

Also include a `.liquid-glass` utility class (not used in the hero itself, but part of the design system):
- `background: rgba(255, 255, 255, 0.01)` with `background-blend-mode: luminosity`
- `backdrop-filter: blur(4px)` (with `-webkit-` prefix)
- `border: none`
- `box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1)`
- A `::before` pseudo-element creating a gradient border effect using a `mask-composite: exclude` technique. The gradient goes from `rgba(255,255,255,0.45)` at top/bottom to transparent in the middle, with `padding: 1.4px`.

---

### Navbar

A `<nav>` fixed to the top (`fixed top-0 left-0 right-0 z-50`), using `flex items-center justify-between`, with padding `px-5 sm:px-8 py-4 sm:py-5`.

**Left: Logo (inline SVG)**
A custom geometric SVG logo, 28x28, viewBox `0 0 256 256`, filled `#111111`:
```
M 256 64 L 256 128 L 192.5 128 L 160 95 L 128 64 L 96 95 L 63.5 128 L 64 128 L 128 192 L 128 256 L 64.5 256 L 32 223 L 0 192 L 0 64 L 64 0 L 192 0 Z M 256 192 L 256 256 L 192.5 256 L 160 223 L 128 192 L 128 128 L 192 128 Z
```

**Center: Desktop pill navigation (hidden on mobile, `hidden md:flex`)**
Absolutely centered with `absolute left-1/2 -translate-x-1/2`. Dark pill container: `bg-gray-900 rounded-full px-2 py-1.5`. Contains 5 nav items: `['Device', 'Real Stories', 'Science', 'Plans', 'Reach Us']`. The first item is the active state: `bg-white text-gray-900 text-sm font-medium px-4 py-1.5 rounded-full`. All others: `text-gray-300 text-sm font-medium px-4 py-1.5 rounded-full hover:text-white transition-colors`.

**Right: Desktop CTA button (hidden on mobile, `hidden md:flex`)**
`bg-gray-900 text-white text-sm font-medium px-5 py-2 rounded-full` with `hover:bg-gray-700 transition-colors`. Contains a small green dot (`w-2 h-2 rounded-full bg-green-400`) followed by text "Reserve Yours".

**Mobile: Hamburger toggle (`md:hidden`)**
Uses `Menu` and `X` icons from `lucide-react` at `size={22}`, colored `text-gray-900`. Toggles a dropdown.

**Mobile dropdown menu**
When open: `fixed top-0 left-0 right-0 z-40 bg-white pt-16 pb-6 px-5 shadow-lg flex flex-col gap-1 md:hidden`. Each nav item is a full-width button: `text-gray-800 text-base font-medium py-3 border-b border-gray-100 text-left hover:text-gray-500 transition-colors`. Includes the same "Reserve Yours" CTA at the bottom with `mt-4`, centered, `rounded-full`.

---

### Hero Text (Bottom-Left)

Positioned inside a `relative z-10 flex flex-col h-full` container. The text block is anchored to the bottom: `flex-1 flex items-end pb-16 sm:pb-20 lg:pb-24 px-6 lg:px-12`. Inner wrapper: `relative lg:ml-12 max-w-[780px]`.

**Main heading `<h1>`:**
- Font: `font-grotesk` (Anton)
- Size: `text-[40px] sm:text-[60px] md:text-[75px] lg:text-[90px]`
- `uppercase`, color `text-cream` (#EFF4FF)
- Line height: `leading-[1.05] sm:leading-[1] md:leading-[1] lg:leading-[1]`
- Text content (with line breaks):
  ```
  Beyond earth
  and ( its ) familiar
  boundaries
  ```
  The parentheses around "its" have spaces inside them: `{'( '}its{' )'}`.

**Cursive accent `<span>`:**
- Absolutely positioned relative to the heading wrapper: `absolute -right-4 sm:right-0 md:right-4 top-0 sm:top-2 md:top-4`
- Font: `font-condiment` (Condiment cursive)
- Size: `text-[24px] sm:text-[32px] md:text-[40px] lg:text-[48px]`
- Color: `text-neon` (#6FFF00)
- Slight rotation: `-rotate-1`
- `opacity-90`
- Inline style: `mixBlendMode: 'exclusion'`
- Text: "Nft collection"

---

### Overall Layout

The root `<section>` is `relative h-screen w-full overflow-hidden bg-background`. The video sits at `absolute inset-0` behind everything. The content layer sits at `relative z-10`. The nav is `fixed z-50`.

The page title in `index.html` is "Orbis.Nft".

---

### Dependencies

- `react`, `react-dom` (v18)
- `lucide-react` (for Menu and X icons)
- Tailwind CSS 3, PostCSS, Autoprefixer
- Vite with `@vitejs/plugin-react`
- TypeScript

No other UI libraries needed.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Logoisum Video Agency"
template_id: "6e3f1e0b-a817-4dce-8cc3-ef0514675774"
section: "sites"
category_slug: "agency"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Logoisum Video Agency

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `6e3f1e0b-a817-4dce-8cc3-ef0514675774`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency

### 🖼 Прев'ю:
![Logoisum Video Agency](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/1657a57a-4fbc-458c-9564-ead0ee38bef2.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a premium, high-end hero section for a video editing agency named 'Logoisum' with the following specifications:

Background: Implement a full-screen, looping video background using this URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260228_065522_522e2295-ba22-457e-8fdb-fbcd68109c73.mp4. The video must be muted, autoplaying, and set to object-cover to fill the section without any color overlays.

Navigation Bar: A floating white navigation bar with rounded-[16px] and a subtle shadow.

Left: The agency logo.

Center: A menu with links for 'About', 'Works', 'Services', and 'Testimonial' using 14px Barlow Medium font.

Right: A dark (#222) primary CTA button labeled 'Book A Free Meeting' featuring a unique 45-degree arrow icon in a circular housing.

Typography & Hero Content:

Primary Headline: Centered layout. The first line 'Agency that makes your' should use a bold/medium Barlow font with tight tracking (tracking-[-4px]). The second line 'videos & reels viral' must use a large, elegant 'Instrument Serif' italic font (text-[84px]).

Subtext: Below the headline, add the text 'Short-form video editing for Influencers, Creators and Brands' in Barlow Medium, 18px, centered.

Secondary CTA: A large white pill-shaped button below the subtext labeled 'See Our Workreel' with a small play icon on the left.

Overall Aesthetic: The design should be minimal, ultra-modern, and responsive. Ensure all text and buttons are layered on top of the video background with clear visibility and proper spacing (min-h-[90vh]).
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Luxury Botanical"
template_id: "e27c6b2c-51d6-4e90-9cfd-82f116ad4036"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Luxury Botanical

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `e27c6b2c-51d6-4e90-9cfd-82f116ad4036`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Luxury Botanical](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/20b24312-a75a-45b1-b6ab-a1ed9531002c.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Bentley — Beyond The Collection</title>

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@300;400;500;600&family=Great+Vibes&display=swap"
  rel="stylesheet"
/>

<script src="https://cdn.tailwindcss.com"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: {
          serif: ['"Instrument Serif"', "serif"],
          sans: ["Manrope", "sans-serif"],
          script: ['"Great Vibes"', "cursive"],
        },
      },
    },
  };
</script>

<style>
  *, *::before, *::after { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #000; }
  body {
    font-family: "Manrope", ui-sans-serif, system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
  }

  .orbit-container {
    position: relative;
    margin-left: auto;
    margin-right: auto;
  }
  .orbit-scaling-container {
    width: 100%;
    height: 100%;
    position: relative;
  }
  .orbit-scaling-container--responsive {
    position: absolute;
    left: 50%;
    top: 50%;
    transform-origin: center center;
  }
  .orbit-rotation-wrapper {
    width: 100%;
    height: 100%;
    transform-origin: center center;
    position: relative;
  }
  .orbit-path-svg {
    position: absolute;
    inset: 0;
    pointer-events: none;
  }
  .orbit-item {
    position: absolute;
    will-change: transform;
    user-select: none;
  }
  .orbit-center-content {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }
  .orbit-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 50%;
  }

  @keyframes scrollArrow {
    0%   { transform: translateY(-6px); opacity: 0; }
    40%  { opacity: 1; }
    100% { transform: translateY(10px); opacity: 0; }
  }
  .scroll-arrow {
    animation: scrollArrow 1.6s ease-in-out infinite;
  }
</style>

<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
<script type="module">
  import React from "https://esm.sh/react@18.3.1";
  import * as ReactDOMClient from "https://esm.sh/react-dom@18.3.1/client?deps=react@18.3.1";
  import * as FM from "https://esm.sh/framer-motion@11.18.2?deps=react@18.3.1,react-dom@18.3.1";
  window.React = React;
  window.ReactDOM = ReactDOMClient;
  window.FM = FM;
  window.__depsReady = true;
  window.dispatchEvent(new Event("deps-ready"));
</script>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel" data-presets="react">
(function () {
  const start = () => {
    const { useRef, useState, useEffect, useMemo } = React;
    const { createRoot } = ReactDOM;
    const {
      motion,
      useScroll,
      useTransform,
      useMotionTemplate,
      useMotionValue,
      useAnimationFrame,
      animate
    } = window.FM;

    /* ============================================================
       OrbitImages
       ============================================================ */

    function generateEllipsePath(cx, cy, rx, ry) {
      return `M ${cx - rx} ${cy} A ${rx} ${ry} 0 1 0 ${cx + rx} ${cy} A ${rx} ${ry} 0 1 0 ${cx - rx} ${cy}`;
    }

    function OrbitItem({
      item,
      title,
      desc,
      index,
      totalItems,
      pathValue,
      itemSizeValue,
      rotationValue,
      progress,
      fill,
      scaleStrength,
      focalPoint = 50
    }) {
      const itemOffset = fill ? index / totalItems * 100 : 0;

      const offsetPercentage = useTransform(progress, (p) => {
        return ((p + itemOffset) % 100 + 100) % 100;
      });

      const offsetDistance = useTransform(offsetPercentage, (p) => `${p}%`);

      const itemScale = useTransform(() => {
        const rawPos = offsetPercentage.get();
        const strength = scaleStrength ? scaleStrength.get() : 0;
        let dist = Math.abs(rawPos - focalPoint);
        if (dist > 50) dist = 100 - dist;
        let targetScale = 1;
        if (dist < 20) {
          const ratio = dist / 20;
          const cosCurve = (Math.cos(ratio * Math.PI) + 1) / 2;
          targetScale = 0.4 + cosCurve * 0.6;
        } else {
          targetScale = 0.4;
        }
        return 1 - strength * (1 - targetScale);
      });

      const offsetPath = useMotionTemplate`path("${pathValue}")`;
      const zIndexMV = useTransform(itemScale, (s) => Math.round(s * 100));
      const counterRotate = useTransform(rotationValue, (r) => `rotate(${-r}deg)`);
      const labelOpacity = useTransform(scaleStrength || useMotionValue(0), (s) => s);

      return (
        <motion.div
          className="orbit-item"
          style={{
            width: itemSizeValue,
            height: itemSizeValue,
            offsetPath,
            offsetRotate: "0deg",
            offsetAnchor: "center center",
            offsetDistance,
            scale: itemScale,
            zIndex: zIndexMV,
            pointerEvents: "auto"
          }}>
          <motion.div style={{ transform: counterRotate, width: "100%", height: "100%", position: "relative" }}>
            {item}
            {(title || desc) &&
              <motion.div
                style={{
                  position: "absolute",
                  left: "115%",
                  top: "50%",
                  transform: "translateY(-50%)",
                  width: "min(360px, 95%)",
                  color: "#000",
                  opacity: labelOpacity,
                  pointerEvents: "none",
                  fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif"
                }}>
                {title &&
                  <div style={{
                    fontFamily: "'Instrument Serif', serif",
                    fontSize: "clamp(26px, 3vw, 40px)",
                    lineHeight: 1.05,
                    letterSpacing: "-0.01em",
                    marginBottom: "14px",
                    whiteSpace: "normal"
                  }}>
                    {title}
                  </div>
                }
                {desc &&
                  <div style={{
                    fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif",
                    fontWeight: 400,
                    fontSize: "clamp(13px, 1vw, 15px)",
                    lineHeight: 1.5,
                    color: "rgba(0,0,0,0.72)"
                  }}>
                    {desc}
                  </div>
                }
              </motion.div>
            }
          </motion.div>
        </motion.div>
      );
    }

    function OrbitImages({
      images = [],
      altPrefix = "Orbiting image",
      baseWidth = 1400,
      radiusX = 700,
      radiusY = 170,
      duration = 40,
      itemSize = 64,
      direction = "normal",
      fill = true,
      width = 100,
      height = 100,
      className = "",
      showPath = false,
      pathColor = "rgba(0,0,0,0.1)",
      pathWidth = 2,
      easing = "linear",
      paused = false,
      centerContent,
      responsive = false,
      progressOverride,
      radiusXOverride,
      radiusYOverride,
      itemSizeOverride,
      rotationOverride,
      translateXOverride,
      focusStrength
    }) {
      const containerRef = useRef(null);
      const [scale, setScale] = useState(1);

      const designCenterX = baseWidth / 2;
      const designCenterY = baseWidth / 2;

      const currentRadiusX = radiusXOverride || useMotionValue(radiusX);
      const currentRadiusY = radiusYOverride || useMotionValue(radiusY);
      const currentItemSize = itemSizeOverride || useMotionValue(itemSize);
      const currentRotation = rotationOverride || useMotionValue(-8);
      const currentTranslateX = translateXOverride || useMotionValue(0);

      const pathValue = useTransform([currentRadiusX, currentRadiusY], ([rx, ry]) => {
        return generateEllipsePath(designCenterX, designCenterY, rx, ry);
      });

      useEffect(() => {
        if (!responsive || !containerRef.current) return;
        const updateScale = () => {
          if (!containerRef.current) return;
          setScale(containerRef.current.clientWidth / baseWidth);
        };
        updateScale();
        const observer = new ResizeObserver(updateScale);
        observer.observe(containerRef.current);
        return () => observer.disconnect();
      }, [responsive, baseWidth]);

      const internalProgress = useMotionValue(0);

      useEffect(() => {
        if (paused || progressOverride) return;
        const controls = animate(internalProgress, direction === "reverse" ? -100 : 100, {
          duration,
          ease: easing,
          repeat: Infinity,
          repeatType: "loop"
        });
        return () => controls.stop();
      }, [internalProgress, duration, easing, direction, paused, progressOverride]);

      const activeProgress = progressOverride || internalProgress;
      const containerWidth = responsive ? "100%" : typeof width === "number" ? width : "100%";
      const containerHeight = responsive ? "auto" : typeof height === "number" ? height : typeof width === "number" ? width : "auto";

      const items = images.map((entry, index) => {
        const src = typeof entry === "string" ? entry : entry.src;
        return (
          <motion.img
            key={src}
            src={src}
            alt={`${altPrefix} ${index + 1}`}
            draggable={false}
            className="orbit-image"
            whileHover={{ scale: 1.2 }}
            transition={{ duration: 0.3 }}
            style={{ cursor: "pointer", pointerEvents: "auto" }}
          />
        );
      });

      return (
        <div
          ref={containerRef}
          className={`orbit-container ${className}`}
          style={{
            width: containerWidth,
            height: containerHeight,
            aspectRatio: responsive ? "1 / 1" : undefined
          }}
          aria-hidden="true">
          <div
            className={responsive ? "orbit-scaling-container orbit-scaling-container--responsive" : "orbit-scaling-container"}
            style={{
              width: responsive ? baseWidth : "100%",
              height: responsive ? baseWidth : "100%",
              transform: responsive ? `translate(-50%, -50%) scale(${scale})` : undefined
            }}>
            <motion.div className="orbit-rotation-wrapper" style={{ rotate: currentRotation, x: currentTranslateX }}>
              {showPath &&
                <svg width="100%" height="100%" viewBox={`0 0 ${baseWidth} ${baseWidth}`} className="orbit-path-svg">
                  <path d={pathValue.get()} fill="none" stroke={pathColor} strokeWidth={pathWidth / scale} />
                </svg>
              }
              {items.map((item, index) => {
                const entry = images[index];
                const title = typeof entry === "object" ? entry.title : null;
                const desc = typeof entry === "object" ? entry.desc : null;
                return (
                  <OrbitItem
                    key={index}
                    item={item}
                    title={title}
                    desc={desc}
                    index={index}
                    totalItems={items.length}
                    pathValue={pathValue}
                    itemSizeValue={currentItemSize}
                    rotationValue={currentRotation}
                    progress={activeProgress}
                    fill={fill}
                    scaleStrength={focusStrength}
                    focalPoint={50}
                  />
                );
              })}
            </motion.div>
          </div>
          {centerContent && <div className="orbit-center-content">{centerContent}</div>}
        </div>
      );
    }

    /* ============================================================
       StaySection
       ============================================================ */

    function StaySection() {
      const blurUp = {
        initial: { opacity: 0, y: 40, filter: "blur(20px)" },
        whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
        viewport: { once: true, amount: 0.3 },
        transition: { duration: 1, ease: "easeOut" }
      };

      return (
        <section
          className="relative w-full overflow-hidden"
          style={{ minHeight: "100vh", backgroundColor: "#ffffff" }}>
          <img
            src="https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780401858/pasted-1779282335552-1_gmztyi.png"
            alt=""
            aria-hidden="true"
            className="absolute inset-x-0 bottom-0 w-full pointer-events-none select-none"
            style={{ objectFit: "cover", objectPosition: "center bottom" }}
          />

          <div className="relative max-w-[1480px] mx-auto px-8 md:px-16 pt-20 md:pt-24 pb-20 md:pb-24 min-h-screen flex flex-col" style={{ gap: "32px" }}>
            <motion.div {...blurUp}>
              <div style={{
                fontFamily: "'Instrument Serif', serif",
                fontSize: "clamp(60px, 11vw, 160px)",
                lineHeight: 0.95,
                letterSpacing: "-0.01em",
                color: "#000"
              }}>
                Stay <span style={{ fontStyle: "italic" }}>in</span>
              </div>
              <div style={{
                fontFamily: "Manrope, ui-sans-serif, sans-serif",
                fontWeight: 400,
                lineHeight: 0.95,
                letterSpacing: "-0.02em",
                color: "#000",
                fontSize: "64px"
              }}>
                the collection
              </div>
            </motion.div>

            <motion.div
              {...blurUp}
              transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
              className="max-w-md">
              <p className="mb-6" style={{
                fontFamily: "Manrope, ui-sans-serif, sans-serif",
                fontSize: "15px",
                lineHeight: 1.55,
                color: "rgba(0,0,0,0.78)"
              }}>
                Editions and invitations from the Bentley fragrance studio, sent twice a season.
              </p>
              <form
                className="flex items-center border-b border-black/40 pb-2 gap-3"
                onSubmit={(e) => e.preventDefault()}>
                <input
                  type="email"
                  placeholder="your@email.com"
                  className="bg-transparent flex-1 outline-none"
                  style={{ fontFamily: "Manrope, ui-sans-serif, sans-serif", fontSize: "15px", color: "#000" }}
                />
                <button type="submit" style={{
                  fontFamily: "Manrope, ui-sans-serif, sans-serif",
                  fontSize: "11px",
                  fontWeight: 500,
                  letterSpacing: "0.25em",
                  textTransform: "uppercase",
                  color: "#000"
                }}>
                  Subscribe →
                </button>
              </form>
            </motion.div>
          </div>
        </section>
      );
    }

    /* ============================================================
       Footer
       ============================================================ */

    function Footer() {
      const blurUp = {
        initial: { opacity: 0, y: 40, filter: "blur(20px)" },
        whileInView: { opacity: 1, y: 0, filter: "blur(0px)" },
        viewport: { once: true, amount: 0.3 },
        transition: { duration: 1, ease: "easeOut" }
      };

      const Column = ({ heading, items }) => (
        <div>
          <div className="mb-5 text-black/55" style={{
            fontFamily: "Manrope, ui-sans-serif, sans-serif",
            fontSize: "11px",
            fontWeight: 500,
            letterSpacing: "0.3em",
            textTransform: "uppercase"
          }}>
            {heading}
          </div>
          <ul className="space-y-3">
            {items.map((label) => (
              <li key={label}>
                <a href="#" className="hover:underline" style={{
                  fontFamily: "Manrope, ui-sans-serif, sans-serif",
                  fontSize: "15px",
                  fontWeight: 400,
                  color: "rgba(0,0,0,0.85)"
                }}>
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      );

      return (
        <footer className="relative w-full text-black overflow-hidden" style={{ backgroundColor: "#f4ecdc" }}>
          <div className="relative max-w-[1480px] mx-auto px-8 md:px-16 pt-12 md:pt-14 pb-12">
            <motion.div
              {...blurUp}
              transition={{ duration: 1, ease: "easeOut", delay: 0.15 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-12 md:gap-10 mb-20 md:mb-24">
              <Column heading="Discover" items={["All fragrances", "The bottle", "Sustainability", "Editions"]} />
              <Column heading="Studio" items={["Our story", "Perfumers", "Atelier visits", "Press"]} />
              <Column heading="Contact" items={["Boutiques", "Concierge", "Returns", "Care guide"]} />

              <div>
                <div className="mb-5 text-black/55" style={{
                  fontFamily: "Manrope, ui-sans-serif, sans-serif",
                  fontSize: "11px",
                  fontWeight: 500,
                  letterSpacing: "0.3em",
                  textTransform: "uppercase"
                }}>
                  Newsletter
                </div>
                <p className="mb-5 text-black/65" style={{
                  fontFamily: "Manrope, ui-sans-serif, sans-serif",
                  fontSize: "14px",
                  lineHeight: 1.5
                }}>
                  Editions and invitations, sent twice a season.
                </p>
                <form
                  className="flex items-center border-b border-black/30 pb-2 gap-3"
                  onSubmit={(e) => e.preventDefault()}>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="bg-transparent flex-1 outline-none"
                    style={{ fontFamily: "Manrope, ui-sans-serif, sans-serif", fontSize: "14px", color: "#000" }}
                  />
                  <button type="submit" style={{
                    fontFamily: "Manrope, ui-sans-serif, sans-serif",
                    fontSize: "11px",
                    fontWeight: 500,
                    letterSpacing: "0.25em",
                    textTransform: "uppercase"
                  }}>
                    Subscribe →
                  </button>
                </form>
              </div>
            </motion.div>

            <motion.div
              {...blurUp}
              transition={{ duration: 0.9, ease: "easeOut", delay: 0.25 }}
              className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 pt-8 border-t border-black/15">
              <div className="text-black/55" style={{
                fontFamily: "Manrope, ui-sans-serif, sans-serif",
                fontSize: "11px",
                fontWeight: 500,
                letterSpacing: "0.3em",
                textTransform: "uppercase"
              }}>
                © 2026 Beyond The Collection
              </div>
              <div className="flex items-center gap-5" style={{
                fontFamily: "Manrope, ui-sans-serif, sans-serif",
                fontSize: "11px",
                fontWeight: 500,
                letterSpacing: "0.28em",
                textTransform: "uppercase"
              }}>
                <a href="#" className="hover:underline">Instagram</a>
                <span className="text-black/30">·</span>
                <a href="#" className="hover:underline">TikTok</a>
                <span className="text-black/30">·</span>
                <a href="#" className="hover:underline">Spotify</a>
              </div>
              <div className="text-black/55" style={{
                fontFamily: "Manrope, ui-sans-serif, sans-serif",
                fontSize: "11px",
                fontWeight: 500,
                letterSpacing: "0.3em",
                textTransform: "uppercase"
              }}>
                EN · USD
              </div>
            </motion.div>
          </div>
        </footer>
      );
    }

    /* ============================================================
       App
       ============================================================ */

    const orbitImagesData = [
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390315/BL1996-Beyond_wild_vetiver_Flakon_100ml_300dpi_a55ie5.webp",
        title: "Wild Vetiver",
        desc: "Smoky vetiver wrapped in saffron and leather — a grounded, untamed signature."
      },
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390315/BL2156_BEYOND_RADIANT_OSMANTHUS_hoc3up.webp",
        title: "Radiant Osmanthus",
        desc: "Apricot-tinged osmanthus over soft musks. Quietly luminous, never loud."
      },
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390315/BL2157_BEYOND_VIBRANT_HIBISCUS_pgiehq.webp",
        title: "Vibrant Hibiscus",
        desc: "Bright hibiscus and pink pepper resting on creamy sandalwood."
      },
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390315/BL2158_BEYOND_MELLOW_HELIOTROPE_agqych.webp",
        title: "Mellow Heliotrope",
        desc: "Almond, vanilla and heliotrope petals — a powdery, hushed warmth."
      },
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390317/BL2371-BL2372-BL2373-Magnetic-Amber_web_2_dbmtpy.webp",
        title: "Magnetic Amber",
        desc: "Resinous amber, oud and rich woods. The collection's deepest note."
      },
      {
        src: "https://res.cloudinary.com/dsdhxhhqh/image/upload/v1780390315/BL2156_BEYOND_RADIANT_OSMANTHUS_1_hlc4v1.webp",
        title: "Crystal Edition",
        desc: "A limited cut of the bottle — etched facets, lavender pour, leather collar."
      }
    ];

    const VIDEO_SRC = "https://d8j0ntlcm91z4.cloudfront.net/user_3BA1nJibL92zfZpAJB3BLBU6tQI/hf_20260520_114550_b72cc2b7-2267-4d9e-b19f-f3bb4b0c7084.mp4";
    const TARGET_RADIUS = 650;

    function App() {
      const containerRef = useRef(null);

      const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end end"]
      });

      const rx = useTransform(scrollYProgress, [0, 0.08, 1], ["0%", "55%", "55%"]);
      const ry = useTransform(scrollYProgress, [0, 0.08, 1], ["0%", "55%", "55%"]);
      const clipPath = useMotionTemplate`ellipse(${rx} ${ry} at 50% 50%)`;

      const textOpacity = useTransform(
        scrollYProgress,
        [0.03, 0.08, 0.15, 0.22, 0.90, 0.98, 1],
        [0, 1, 1, 0, 0, 1, 1]
      );
      const textBlurVal = useTransform(
        scrollYProgress,
        [0.03, 0.08, 0.15, 0.22, 0.90, 0.98, 1],
        [15, 0, 0, 15, 15, 0, 0]
      );
      const filterText = useMotionTemplate`blur(${textBlurVal}px)`;
      const yElement = useTransform(
        scrollYProgress,
        [0.03, 0.08, 0.15, 0.22, 0.90, 0.98, 1],
        [20, 0, 0, 20, 20, 0, 0]
      );

      const scrollHintOpacity = useTransform(scrollYProgress, [0, 0.03, 0.08], [1, 1, 0]);

      const orbitItemSize = useTransform(scrollYProgress, [0.15, 0.25, 0.85, 0.95, 1], [80, 360, 360, 80, 80]);
      const orbitRx = useTransform(scrollYProgress, [0.15, 0.25, 0.85, 0.95, 1], [330, TARGET_RADIUS, TARGET_RADIUS, 330, 330]);
      const orbitRy = useTransform(scrollYProgress, [0.15, 0.25, 0.85, 0.95, 1], [140, TARGET_RADIUS, TARGET_RADIUS, 140, 140]);
      const orbitRotation = useTransform(scrollYProgress, [0.15, 0.25, 0.85, 0.95, 1], [-15, 0, 0, -15, -15]);
      const orbitTx = useTransform(
        scrollYProgress,
        [0.15, 0.25, 0.85, 0.95, 1],
        [0, -(TARGET_RADIUS + 200), -(TARGET_RADIUS + 200), 0, 0]
      );
      const focusStrength = useTransform(scrollYProgress, [0.15, 0.25, 0.85, 0.95, 1], [0, 1, 1, 0, 0]);

      const orbitProgress = useMotionValue(0);
      const prevScroll = useRef(0);

      useAnimationFrame((time, delta) => {
        const pos = scrollYProgress.get();
        const scrollDelta = pos - prevScroll.current;
        prevScroll.current = pos;

        let frameSpeed = 0;
        if (pos > 0.15 && pos < 0.85) {
          frameSpeed = scrollDelta * 200;
        } else {
          frameSpeed = delta / 1000 * 2.5;
        }

        orbitProgress.set(orbitProgress.get() + frameSpeed);
      });

      return (
        <>
          <div ref={containerRef} className="relative w-full h-[600vh] bg-black">
            <div className="sticky top-0 w-full h-screen overflow-hidden text-white">

              {/* Video background */}
              <video autoPlay loop muted playsInline className="absolute inset-0 w-full h-full object-cover z-0">
                <source src={VIDEO_SRC} type="video/mp4" />
              </video>

              {/* Top-left logo text */}
              <div
                className="absolute z-10 flex flex-col items-start text-left text-black select-none leading-[0.95]"
                style={{ top: "120px", left: "96px" }}>
                <div className="flex items-baseline">
                  <span style={{ fontFamily: "'Instrument Serif', serif", fontSize: "clamp(32px, 5vw, 64px)" }}>
                    Beyond
                  </span>
                  <span style={{
                    fontFamily: "'Instrument Serif', serif",
                    fontStyle: "italic",
                    fontSize: "clamp(32px, 5vw, 64px)",
                    marginLeft: "0.05em"
                  }}>
                    The
                  </span>
                </div>
                <span style={{
                  fontFamily: "Manrope, ui-sans-serif, system-ui, sans-serif",
                  fontWeight: 400,
                  fontSize: "clamp(28px, 4.4vw, 56px)",
                  letterSpacing: "-0.01em",
                  marginTop: "0.05em"
                }}>
                  Collection
                </span>
              </div>

              {/* Scroll hint arrow */}
              <motion.div
                className="absolute z-10 left-1/2 -translate-x-1/2 flex flex-col items-center text-white select-none pointer-events-none"
                style={{ bottom: "40px", opacity: scrollHintOpacity }}>
                <div className="relative w-[20px] h-[34px] overflow-hidden">
                  <svg
                    className="scroll-arrow absolute inset-0"
                    width="20" height="34" viewBox="0 0 20 34" fill="none"
                    xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M10 4 V28 M3 21 L10 28 L17 21" stroke="#ffffff" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
              </motion.div>

              {/* Clip-path reveal with orbit */}
              <motion.div
                className="absolute z-20 flex items-center justify-center overflow-hidden"
                style={{
                  clipPath,
                  rotate: -15,
                  width: "150vw",
                  height: "150vh",
                  left: "-25vw",
                  top: "-25vh"
                }}>
                <div className="absolute inset-0 bg-white" />
                <div
                  className="relative flex flex-col items-center justify-center"
                  style={{ width: "100vw", height: "100vh", transform: "rotate(15deg)" }}>
                  <motion.div className="w-[90vw] max-w-[1200px] aspect-square relative z-0">
                    <OrbitImages
                      images={orbitImagesData}
                      shape="ellipse"
                      direction="normal"
                      duration={40}
                      fill={true}
                      showPath={false}
                      responsive={true}
                      baseWidth={800}
                      progressOverride={orbitProgress}
                      radiusXOverride={orbitRx}
                      radiusYOverride={orbitRy}
                      itemSizeOverride={orbitItemSize}
                      rotationOverride={orbitRotation}
                      translateXOverride={orbitTx}
                      focusStrength={focusStrength}
                    />
                  </motion.div>
                </div>
              </motion.div>

              {/* Text overlays */}
              <div className="absolute inset-0 z-[60] pointer-events-none">

                {/* Center brand text */}
                <div className="absolute top-[48%] left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-50">
                  <motion.div
                    className="flex flex-col items-center whitespace-nowrap pointer-events-auto"
                    style={{
                      filter: filterText,
                      opacity: textOpacity,
                      WebkitFontSmoothing: "antialiased",
                      WebkitBackfaceVisibility: "hidden",
                      transform: "translateZ(0)"
                    }}>
                    <div className="flex items-baseline text-black leading-none mb-1">
                      <span className="font-serif text-[45px] md:text-[55px] tracking-tight text-black">Beyond </span>
                      <span className="font-serif text-[45px] md:text-[55px] italic tracking-tight text-black">The</span>
                    </div>
                    <span className="font-sans text-[28px] md:text-[36px] tracking-tight text-black mt-[-5px]">Collection</span>
                  </motion.div>
                </div>

                {/* Top-right info */}
                <motion.div
                  className="absolute top-32 right-[calc(6vw+150px)] md:right-[214px] flex flex-col items-start text-left pointer-events-auto cursor-text"
                  style={{ y: yElement, filter: filterText, opacity: textOpacity }}>
                  <span className="font-serif text-[40px] leading-none mb-3 text-black">2K26</span>
                  <span className="font-serif text-[16px] uppercase tracking-widest text-black leading-[20px] text-left">
                    JOIN AN EXCLUSIVE<br />COMMUNITY
                  </span>
                </motion.div>

                {/* Bottom-left number */}
                <motion.div
                  className="absolute bottom-8 left-8 md:bottom-16 md:left-16 flex flex-col items-start text-black pointer-events-auto cursor-text"
                  style={{ y: yElement, filter: filterText, opacity: textOpacity }}>
                  <span className="font-serif text-[40px] leading-none mb-1 text-black">0651</span>
                  <span className="font-serif text-[16px] uppercase tracking-widest text-black">COLLECTION</span>
                </motion.div>

                {/* Bottom-right CTA */}
                <div className="absolute bottom-16 right-[6vw] md:right-[10vw] flex flex-col items-start z-10 pointer-events-auto">
                  <motion.p
                    className="font-serif text-[16px] uppercase tracking-widest text-black leading-[20px] mb-6 text-left w-[240px] cursor-text"
                    style={{ y: yElement, filter: filterText, opacity: textOpacity }}>
                    JOIN AN EXCLUSIVE COMMUNITY OF SAILORS. WHETHER YOU CRAVE THE THRILL OF THE OPEN
                  </motion.p>
                  <motion.div
                    className="flex gap-0 pointer-events-auto items-center"
                    style={{ y: yElement, filter: filterText, opacity: textOpacity }}>
                    <button className="bg-black hover:bg-black/90 transition-colors text-white rounded-[40px] px-8 py-3.5 font-serif tracking-[0.1em] uppercase text-[12px] md:text-[14px] z-10">
                      BUY COLLECTION
                    </button>
                    <button className="bg-black hover:bg-black/90 transition-colors w-[46px] h-[46px] flex items-center justify-center rounded-[50%] text-white -ml-2 z-0">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="ml-1">
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                    </button>
                  </motion.div>
                </div>
              </div>

              {/* Header */}
              <motion.header
                className="absolute top-0 left-0 w-full px-6 md:px-12 py-5 md:py-6 flex justify-between items-center z-[100] pointer-events-none"
                style={{ opacity: scrollHintOpacity }}>
                <a href="#" className="flex items-center gap-3 text-black select-none pointer-events-auto" aria-label="Bentley">
                  <svg width="54" height="40" viewBox="0 0 84 60" fill="none" aria-hidden="true">
                    <g fill="currentColor">
                      <path d="M42 22 C30 22 19 16 4 12 C9 26 18 33 30 33 L42 33 Z" />
                      <path d="M42 22 C54 22 65 16 80 12 C75 26 66 33 54 33 L42 33 Z" />
                      <path d="M34 25 C36 28 39 30 42 30 C45 30 48 28 50 25 L42 22 Z" opacity="0.7" />
                    </g>
                    <text x="42" y="52" textAnchor="middle" fontFamily="'Instrument Serif', serif" fontSize="22" fontStyle="italic" fill="currentColor">B</text>
                  </svg>
                  <span style={{
                    fontFamily: "Manrope, ui-sans-serif, sans-serif",
                    fontWeight: 600,
                    fontSize: "14px",
                    letterSpacing: "0.42em",
                    textTransform: "uppercase"
                  }}>
                    Bentley
                  </span>
                </a>

                <a
                  href="#"
                  className="pointer-events-auto inline-flex items-center gap-2 bg-black text-white rounded-full pl-5 pr-2 py-2 hover:bg-black/85 transition-colors"
                  style={{
                    fontFamily: "Manrope, ui-sans-serif, sans-serif",
                    fontSize: "11px",
                    fontWeight: 500,
                    letterSpacing: "0.22em",
                    textTransform: "uppercase"
                  }}>
                  <span className="hidden sm:inline">Shop the collection</span>
                  <span className="sm:hidden">Shop</span>
                  <span className="inline-flex w-7 h-7 items-center justify-center rounded-full bg-white/15">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </span>
                </a>
              </motion.header>

            </div>
          </div>

          <StaySection />
          <Footer />
        </>
      );
    }

    createRoot(document.getElementById("root")).render(<App />);
  };

  if (window.__depsReady) start();
  else window.addEventListener("deps-ready", start, { once: true });
})();
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Innovation"
template_id: "c834efed-6db2-421b-b9d7-4dc5c438e3e5"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Innovation

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `c834efed-6db2-421b-b9d7-4dc5c438e3e5`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Innovation](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/0483571f-62cd-446d-9a65-2ecaa7c14a0d.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
RECREATION PROMPT

Build a single-page landing site using React + TypeScript + Vite + Tailwind CSS + framer-motion + lucide-react. The entire page has a bg-black background. The font loaded via Google Fonts is Instrument Serif (italic and regular). Import it in index.css:


@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap');
LIQUID GLASS CSS (in index.css, inside @layer components)
Create a reusable .liquid-glass class used on every glass element:


.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.45) 0%,
    rgba(255, 255, 255, 0.15) 20%,
    rgba(255, 255, 255, 0) 40%,
    rgba(255, 255, 255, 0) 60%,
    rgba(255, 255, 255, 0.15) 80%,
    rgba(255, 255, 255, 0.45) 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
SECTION 1 -- HERO (full-viewport, in Index.tsx)
Full-screen (min-h-screen) container with overflow-hidden relative flex flex-col.

Background video: absolute, covers the entire viewport (absolute inset-0 w-full h-full object-cover object-bottom). URL:


https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260405_074625_a81f018a-956b-43fb-9aee-4d1508e30e6a.mp4
Attributes: muted, autoPlay, playsInline, preload="auto". Starts at opacity: 0.

Video fade logic (vanilla JS via refs, no CSS transitions):

On canplay: play the video, then animate opacity from 0 to 1 over 500ms using requestAnimationFrame.
On timeupdate: when remaining time <= 0.55s, animate opacity from current to 0 over 500ms.
On ended: set opacity to 0, wait 100ms, reset currentTime to 0, play again, fade back to 1 over 500ms.
This creates a seamless loop with smooth crossfade to black between plays.
Navbar (relative z-20, px-6 py-6):

A liquid-glass rounded-full pill, max-w-5xl mx-auto, px-6 py-3, flex between left/right.
Left: Globe icon (24px, white) + "Asme" text (white, font-semibold, text-lg). Hidden on mobile: nav links "Features", "Pricing", "About" (text-white/80 hover:text-white text-sm font-medium, gap-8 ml-8).
Right: "Sign Up" text button (white, text-sm, font-medium) + "Login" button (liquid-glass rounded-full px-6 py-2, white text-sm font-medium).
Hero content (relative z-10, flex-1 flex flex-col items-center justify-center, px-6 py-12 text-center, -translate-y-[20%]):

Heading: text-7xl md:text-8xl lg:text-9xl, white, tracking-tight whitespace-nowrap, font-family 'Instrument Serif', serif. Text: Know it then <em className="italic">all</em>.
Email input: max-w-xl w-full. A liquid-glass rounded-full pill with pl-6 pr-2 py-2 flex items-center gap-3. Inside: transparent <input> with placeholder "Enter your email" (text-white placeholder:text-white/40). A white circular submit button (bg-white rounded-full p-3 text-black) containing ArrowRight icon (20px).
Subtitle: text-white text-sm leading-relaxed px-4. Text: "Stay updated with the latest news and insights. Subscribe to our newsletter today and never miss out on exciting updates."
Manifesto button: liquid-glass rounded-full px-8 py-3 text-white text-sm font-medium hover:bg-white/5 transition-colors.
Social icons footer (relative z-10, flex justify-center gap-4 pb-12):

Three liquid-glass rounded-full p-4 buttons for Instagram, Twitter, Globe icons (20px). text-white/80 hover:text-white hover:bg-white/5 transition-all.
SECTION 2 -- ABOUT SECTION (separate component AboutSection.tsx)
Uses framer-motion useInView (ref, { once: true, margin: "-100px" }).
bg-black pt-32 md:pt-44 pb-10 md:pb-14 px-6 overflow-hidden.
Subtle radial gradient overlay: bg-[radial-gradient(ellipse_at_top,_rgba(255,255,255,0.03)_0%,_transparent_70%)].
Label: "About Us" -- text-white/40 text-sm tracking-widest uppercase. Animates: opacity: 0, y: 20 -> opacity: 1, y: 0, duration 0.6.
Heading: text-4xl md:text-6xl lg:text-7xl text-white leading-[1.1] tracking-tight. Animates: opacity: 0, y: 40 -> opacity: 1, y: 0, duration 0.8, delay 0.1. Text structure:
Pioneering then ideas (Instrument Serif italic, text-white/60) for
Line break (hidden on mobile)
minds that then create, build, and inspire. (all Instrument Serif italic, text-white/60)
SECTION 3 -- FEATURED VIDEO (separate component FeaturedVideoSection.tsx)
bg-black pt-6 md:pt-10 pb-20 md:pb-32 px-6 overflow-hidden. Max-w-6xl.
A rounded-3xl overflow-hidden aspect-video container that animates opacity: 0, y: 60 -> opacity: 1, y: 0, duration 0.9.
Video: w-full h-full object-cover, muted, autoPlay, loop, playsInline, preload="auto". URL:

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260402_054547_9875cfc5-155a-4229-8ec8-b7ba7125cbf8.mp4
Gradient overlay on video: bg-gradient-to-t from-black/60 via-transparent to-transparent.
Bottom overlay content (absolute bottom-0 left-0 right-0 p-6 md:p-10):
Flex row on desktop, column on mobile.
Left: a liquid-glass rounded-2xl p-6 md:p-8 max-w-md card. Label "Our Approach" (text-white/50 text-xs tracking-widest uppercase mb-3). Body text (text-white text-sm md:text-base leading-relaxed): "We believe in the power of curiosity-driven exploration. Every project starts with a question, and every answer opens a new door to innovation."
Right: "Explore more" button (liquid-glass rounded-full px-8 py-3, white text-sm font-medium) with whileHover={{ scale: 1.05 }} and whileTap={{ scale: 0.95 }}.
SECTION 4 -- PHILOSOPHY / INNOVATION x VISION (separate component PhilosophySection.tsx)
bg-black py-28 md:py-40 px-6 overflow-hidden. Max-w-6xl.
Heading: text-5xl md:text-7xl lg:text-8xl text-white tracking-tight mb-16 md:mb-24. Animates opacity: 0, y: 40 -> opacity: 1, y: 0, duration 0.8. Text: Innovation then x in Instrument Serif italic text-white/40, then Vision.
Two-column grid (grid-cols-1 md:grid-cols-2 gap-8 md:gap-12):
Left: Video in rounded-3xl overflow-hidden aspect-[4/3]. Animates from opacity: 0, x: -40. URL:

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260307_083826_e938b29f-a43a-41ec-a153-3d4730578ab8.mp4
muted, autoPlay, loop, playsInline, preload="auto".
Right: Animates from opacity: 0, x: 40. Two text blocks separated by a w-full h-px bg-white/10 divider.
Block 1: Label "Choose your space" (text-white/40 text-xs tracking-widest uppercase mb-4). Body (text-white/70 text-base md:text-lg leading-relaxed): "Every meaningful breakthrough begins at the intersection of disciplined strategy and remarkable creative vision. We operate at that crossroads, turning bold thinking into tangible outcomes that move people and reshape industries."
Block 2: Label "Shape the future". Body: "We believe that the best work emerges when curiosity meets conviction. Our process is designed to uncover hidden opportunities and translate them into experiences that resonate long after the first impression."
SECTION 5 -- SERVICES / WHAT WE DO (separate component ServicesSection.tsx)
bg-black py-28 md:py-40 px-6 overflow-hidden. Max-w-6xl.
Subtle radial gradient: bg-[radial-gradient(ellipse_at_center,_rgba(255,255,255,0.02)_0%,_transparent_60%)].
Header row: flex between "What we do" (text-3xl md:text-5xl text-white tracking-tight) and "Our services" label (text-white/40 text-sm, hidden on mobile). Animates opacity: 0, y: 30 -> visible, duration 0.7.
Two-card grid (grid-cols-1 md:grid-cols-2 gap-6 md:gap-8):
Each card: liquid-glass rounded-3xl overflow-hidden with group class. Animates opacity: 0, y: 50 -> visible, duration 0.8, staggered by 0.15s.
Card video area: aspect-video, object-cover, transition-transform duration-700 group-hover:scale-105. Gradient overlay: bg-gradient-to-t from-black/40 to-transparent.
Card body (p-6 md:p-8): tag label (uppercase, tracking-widest, text-white/40 text-xs), ArrowUpRight icon in a liquid-glass rounded-full p-2 circle, title (text-white text-xl md:text-2xl mb-3 tracking-tight), description (text-white/50 text-sm leading-relaxed).
Card 1: Video URL:

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4
Tag: "Strategy". Title: "Research & Insight". Description: "We dig deep into data, culture, and human behavior to surface the insights that drive meaningful, lasting change."
Card 2: Video URL:

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260324_151826_c7218672-6e92-402c-9e45-f1e0f454bdc4.mp4
Tag: "Craft". Title: "Design & Execution". Description: "From concept to launch, we obsess over every detail to deliver experiences that feel effortless and look extraordinary."

```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Growth Marketing SaaS"
template_id: "c0c573cd-604e-48ef-a912-8cc11aefe25d"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Growth Marketing SaaS

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `c0c573cd-604e-48ef-a912-8cc11aefe25d`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Growth Marketing SaaS](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/5be3ef32-6b4d-4598-bc78-10b44dac32dc.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single landing page with only a fixed Navbar and a full-screen Hero section that contains a parallax dashboard mock and a foreground grass image. Use React + Vite + TypeScript + Tailwind + framer-motion + lucide-react. No backend.

1. Global setup

`index.html` — add fonts in `<head>`
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet" />
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0..1,0" rel="stylesheet" />
```

Body background must be `#08020e`.

`tailwind.config.ts` — extend
```ts
fontFamily: { inter: ['Inter','ui-sans-serif','system-ui','sans-serif'] },
colors: {
  landing: {
    surface: "rgba(255,255,255,0.10)",
    "surface-hover": "rgba(255,255,255,0.16)",
    border: "rgba(255,255,255,0.10)",
    "border-strong": "rgba(255,255,255,0.20)",
    text: "rgba(255,255,255,0.80)",
    "text-muted": "rgba(255,255,255,0.60)",
  },
}
```

`src/index.css` — add
```css
body { background-color: #08020e; margin: 0; min-height: 100vh; color: white; }

.landing-root {
  --background: 0 0% 0%;
  --foreground: 0 0% 98%;
  --radius: 0.75rem;
  background-color: hsl(var(--background));
  color: hsl(var(--foreground));
}

/* Liquid glass utility */
.liquid-glass {
  background: rgba(255,255,255,0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: ''; position: absolute; inset: 0;
  border-radius: inherit; padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}

.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
```

Wrap the page in `<div className="landing-root font-inter min-h-screen relative overflow-x-hidden">`.

2. Asset URLs (all remote — no local files)

- Hero background video: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260521_014404_fadafdb1-4df6-4699-be9c-77d25f39a3d0.mp4`
- Dashboard live-preview video: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_115001_bcdaa3b4-03de-47e7-ad63-ae3e392c32d4.mp4`
- Foreground grass PNG: `https://miptxtnhvjrkpmnjgdhk.supabase.co/storage/v1/object/public/training-assets/landing%2Fhero-bottom-bg.png`

3. Components

`MIcon` (Google Material Symbols)
```tsx
export const MIcon = ({ name, size = 16, className = "", filled = false, weight = 400, style }: {
  name: string; size?: number; className?: string; filled?: boolean; weight?: number; style?: React.CSSProperties;
}) => (
  <span aria-hidden className={`material-symbols-outlined select-none leading-none inline-flex items-center justify-center ${className}`}
    style={{ fontSize: size, width: size, height: size,
      fontVariationSettings: `'FILL' ${filled?1:0}, 'wght' ${weight}, 'GRAD' 0, 'opsz' ${Math.min(48,Math.max(20,size))}`,
      ...style }}>{name}</span>
);
```

`AnimatedText` — text slides up on hover, replacement slides in from below (40px, 0.2s easeInOut). Uses framer-motion `motion.div` parent (`overflow-hidden`) with two stacked `motion.span` children; rest variant `{y:0}` / `{y:40}`, hover variant `{y:-40}` / `{y:0}`.

`FadeUp` — framer-motion wrapper: `initial={{opacity:0, y:24}}`, `whileInView={{opacity:1, y:0}}`, `viewport={{once:true, amount:0.3}}`, `transition={{ duration:0.6, delay, ease:[0.22,1,0.36,1] }}`. Honors `useReducedMotion`. Accepts `delay`, `duration`, `y` props.

`PrimaryButton` — white pill CTA
- Classes: `inline-flex items-center justify-center rounded-full bg-white/80 hover:bg-white text-black leading-none transition-colors h-12 px-9 text-sm font-medium`
- Wraps children in `<AnimatedText>`.

`SecondaryButton` — glass pill
- Classes: `inline-flex items-center justify-center rounded-full bg-landing-surface hover:bg-landing-surface-hover border border-landing-border text-foreground backdrop-blur-[2.5px] font-medium leading-none h-8 px-4 text-sm` (size=sm)
- Wraps children in `<AnimatedText>`.

`HeroBadge`
```tsx
<div className="inline-flex items-center justify-center rounded-full bg-landing-surface border border-landing-border px-4 h-7 text-sm text-landing-text">
  {children}
</div>
```

4. Navbar (fixed, transparent)

```tsx
const navItems = [
  { name: "About", href: "#about" },
  { name: "Features", href: "#features" },
  { name: "What you get", href: "#what-you-get" },
  { name: "Pricing", href: "#pricing" },
];
```

- `<nav className="fixed top-0 left-0 right-0 z-50 w-full bg-transparent">`
- Inner: `mx-auto flex h-16 max-w-[1080px] items-center justify-between px-6 lg:px-0`
- Left logo: `<a href="/" className="flex items-center gap-2 text-foreground">` with `<MIcon name="rocket_launch" size={20} />` + `<span className="text-base font-semibold tracking-tight">UI Rocket</span>`
- Center (lg only): `flex items-center gap-8`, each link `text-sm text-landing-text hover:text-foreground transition-colors`, wrap label in `<AnimatedText>`. Smooth-scroll on click via `document.getElementById(id)?.scrollIntoView({behavior:"smooth"})`.
- Right actions (lg only): `flex items-center gap-5` → "Login" link (same style as nav links, wrapped in AnimatedText) + `<SecondaryButton href="/auth" size="sm">Get started</SecondaryButton>`
- Mobile: menu button (`MIcon name="menu" size={24}`) opens a right-side sheet (use shadcn Sheet) with the same items stacked.

5. Hero section

```tsx
const HERO_VIDEO = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260521_014404_fadafdb1-4df6-4699-be9c-77d25f39a3d0.mp4";
const GRASS_IMG  = "https://miptxtnhvjrkpmnjgdhk.supabase.co/storage/v1/object/public/training-assets/landing%2Fhero-bottom-bg.png";
```

Inside the Hero component, set up scroll-linked parallax:
```ts
const sectionRef = useRef<HTMLElement>(null);
const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start start", "end start"] });
const dashboardY    = useTransform(scrollYProgress, [0, 1],   ["0%", "-25%"]);
const grassY        = useTransform(scrollYProgress, [0, 1],   ["0%",  "20%"]);
const contentY      = useTransform(scrollYProgress, [0, 1],   ["0%", "-60%"]);
const contentOpacity= useTransform(scrollYProgress, [0, 0.6], [1, 0]);
```

Structure:
```tsx
<section ref={sectionRef} id="hero" className="relative w-full min-h-screen">
  {/* 1) Background video — full bleed, no overlay */}
  <video src={HERO_VIDEO} autoPlay muted loop playsInline
    className="absolute inset-0 w-full h-full object-cover z-0" />

  {/* 2) Centered copy + CTA, with scroll fade/translate */}
  <motion.div style={{ y: contentY, opacity: contentOpacity }}
    className="relative z-20 flex flex-col items-center text-center px-4 sm:px-6 pt-28 sm:pt-36 md:pt-44 max-w-[980px] mx-auto">
    <FadeUp delay={0}>
      <HeroBadge>Founder member sale special</HeroBadge>
    </FadeUp>
    <FadeUp delay={0.1}>
      <h1 className="mt-8 text-foreground text-[38px] sm:text-[52px] md:text-[64px] leading-[1.05] tracking-[-0.03em] max-w-[960px]">
        Are you a designer or builder who wants to stay ahead of AI?
      </h1>
    </FadeUp>
    <FadeUp delay={0.2}>
      <p className="mt-6 text-landing-text text-base sm:text-lg leading-[1.5] max-w-[520px]">
        Learn to turn your ideas into stunning websites with AI
      </p>
    </FadeUp>
    <FadeUp delay={0.3} className="mt-10">
      <PrimaryButton as="button">Get course</PrimaryButton>
    </FadeUp>
  </motion.div>

  {/* 3) Dashboard mock — slower parallax (-25%) */}
  <motion.div style={{ y: dashboardY }}
    className="relative z-10 mt-8 sm:mt-10 md:mt-12 px-4 sm:px-6">
    <DashboardMock />
  </motion.div>

  {/* 4) Foreground grass — in front of dashboard, drifts down 20% */}
  <motion.img src={GRASS_IMG} alt="" aria-hidden style={{ y: grassY }}
    className="pointer-events-none select-none absolute left-0 right-0 bottom-[-40px] sm:bottom-[-100px] lg:bottom-[-220px] w-full z-30 object-cover" />
</section>
```

6. DashboardMock — liquid-glass wrapper with two-column grid

```tsx
<div className="liquid-glass w-full max-w-[1100px] aspect-[3/4] sm:aspect-[16/10] lg:aspect-[16/9] rounded-2xl mx-auto overflow-hidden p-2 sm:p-3">
  <div className="grid h-full grid-cols-1 sm:grid-cols-[minmax(220px,320px)_1fr] gap-2 sm:gap-3">
    <div className="min-h-0 hidden sm:block"><ChatPanel animateMessagesIn /></div>
    <div className="min-h-0"><LivePreviewHero /></div>
  </div>
</div>
```

`ChatPanel` (left column)
- Container: `flex h-full flex-col overflow-hidden rounded-2xl border border-white/10`, inline style `background: rgba(8,8,10,0.6); backdropFilter: blur(24px); WebkitBackdropFilter: blur(24px)`.
- Header: `flex items-center gap-2 px-4 py-3 border-b border-white/5`. Circle `w-7 h-7 rounded-full bg-white/5 flex items-center justify-center` with `<MIcon name="auto_awesome" size={14} className="text-white/80" />`. Text column: `Vibe Design course` (`text-sm font-medium text-white`) + subtitle `Learn how to build website with AI` (`text-[11px] text-white/40`).
- Messages list: `flex-1 overflow-y-auto scrollbar-hide px-4 py-5 space-y-4`. Each row wrapped in `<FadeUp delay={i*0.12} y={16}>`. Layout:
  - Row: `flex justify-end` (user) or `flex justify-start` (assistant).
  - Bubble: `max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed`; user = `bg-white/15 text-white/90`; assistant = `bg-white/5 text-white/70 border border-white/5`.
- Seed messages (exact text):
  1. assistant — "Welcome to the Vibe Design course! I'll guide you through building stunning websites with AI. What would you like to learn first?"
  2. user — "I want to learn how to build a hero section with a cinematic video background using AI."
  3. assistant — "Great choice! In this course, you'll learn how to create full-screen looping videos, liquid glass nav bars, email signups, and manifesto buttons — all with AI assistance. Let's dive in!"
- Input: outer `p-3 border-t border-white/5`. Inner `liquid-glass rounded-2xl flex items-end gap-2 p-2` with a `<textarea rows={1}>` (`flex-1 resize-none bg-transparent px-3 py-2 text-sm text-white placeholder:text-white/40 focus:outline-none max-h-32`, placeholder "Ask about the course...") and a send button `bg-white text-black rounded-xl p-2 hover:bg-white/90` containing `<MIcon name="arrow_upward" size={16} className="text-black" />`. Enter (no shift) sends; appends a user message then a canned assistant reply. After updates, scroll list to bottom smoothly.

`LivePreviewHero` (right column)
Uses `lucide-react` icons `Globe, ArrowRight, Instagram, Twitter`.

- Outer: `relative w-full h-full min-h-[500px] overflow-hidden rounded-2xl bg-black`.
- Background video (with JS fade-in/out loop):
  ```tsx
  <video ref={videoRef} src={DASHBOARD_VIDEO} muted autoPlay playsInline preload="auto"
    className="absolute inset-0 w-full h-full object-cover translate-y-[17%]"
    style={{ opacity: 0 }} />
  ```
  Behavior (in `useEffect`):
  - On `loadeddata`: set opacity 0, `play()`, fade opacity to 1 over 500ms via `requestAnimationFrame` linear tween.
  - On `timeupdate`: when `duration - currentTime < 0.55s` and not already fading out, fade opacity to 0 over 500ms.
  - On `ended`: snap opacity to 0, after 100ms reset `currentTime=0`, `play()`, reset fadingOut flag, fade back to 1.
  - Cleanup all listeners and cancel RAF on unmount.

- Inner content stack (`relative z-10 flex flex-col min-h-full h-full`):

  Mini-nav `relative z-20 px-3 sm:px-4 py-3`, inside a `rounded-full px-2 sm:px-4 py-1.5 flex items-center justify-between max-w-5xl mx-auto`:
  - Left group `flex items-center gap-3 sm:gap-5`: `Globe size={14} text-white` + `<span className="text-white font-semibold text-xs sm:text-sm">Asme</span>`. After it, `hidden md:flex items-center gap-5` of links `Features`, `Pricing`, `About` each `text-white/80 hover:text-white text-[11px] font-medium`.
  - Right group `flex items-center gap-2 sm:gap-3`: "Sign Up" link (`text-white text-[11px] font-medium hidden sm:inline`) + glass pill `<a className="liquid-glass rounded-full px-3 sm:px-4 py-1 text-white text-[11px] font-medium">Login</a>`.

  Hero block `relative z-10 flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-4 text-center -translate-y-[8%] sm:-translate-y-[15%]`:
  - `<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl text-white mb-4 sm:mb-5 tracking-tight whitespace-nowrap" style={{ fontFamily: "'Instrument Serif', serif" }}>Built for the curious</h1>`
  - Inner column `max-w-sm w-full space-y-3`:
    - Email pill `liquid-glass rounded-full pl-4 pr-1.5 py-1.5 flex items-center gap-2`: `<input type="email" placeholder="Enter your email" className="flex-1 bg-transparent text-white placeholder:text-white/40 text-xs focus:outline-none" />` + circular submit `bg-white rounded-full p-1.5 text-black` with `<ArrowRight size={14} />`.
    - Paragraph `text-white/80 text-[11px] leading-relaxed px-2`: "Stay updated with the latest news and insights. Subscribe to our newsletter today and never miss out on exciting updates."
    - Centered glass pill button: `liquid-glass rounded-full px-5 py-1.5 text-white text-[11px] font-medium hover:bg-white/5 transition-colors` → label "Manifesto".

  Socials row `relative z-10 flex justify-center gap-2 pb-4 sm:pb-6` — three glass round buttons (`liquid-glass rounded-full p-2 text-white/80 hover:text-white hover:bg-white/5 transition-all`) wrapping `Instagram`, `Twitter`, `Globe` icons at `size={14}`.

7. Page assembly

```tsx
export default function Page() {
  return (
    <div className="landing-root font-inter min-h-screen relative overflow-x-hidden">
      <Navbar />
      <Hero />
    </div>
  );
}
```

8. Behavioral notes (must match)

- Hero video is autoplay/muted/loop/playsInline with no dark overlay.
- Z-index stack: video `z-0`, dashboard `z-10`, copy/CTA `z-20`, grass `z-30`, navbar `z-50`.
- Hero copy fades + translates up to `-60%` during scroll through the section, fully fading by 60% scroll progress.
- Dashboard parallaxes up (`-25%`); grass drifts down (`+20%`) — creates depth.
- All button labels animate with the "text slides up, replacement slides in from below" effect via `AnimatedText`.
- Inter is the global UI font; the dashboard hero `<h1>` "Built for the curious" uses Instrument Serif.
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "AI Automation Hero"
template_id: "ee193bf3-f2f6-40d5-81e7-ba9ba5639766"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 AI Automation Hero

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `ee193bf3-f2f6-40d5-81e7-ba9ba5639766`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
AI / SaaS

### 🖼 Прев'ю:
![AI Automation Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/d65eb41d-5ffa-499e-ab20-1e0b60eca17a.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a full-screen hero section with the following exact specifications:

Layout & Structure:
- Full viewport height (h-screen), full width, relative positioning with overflow-hidden
- Background color: #070612 (dark purple-black)
- Content aligned to the left side, vertically centered
- Max-width container (max-w-7xl) with horizontal padding (px-6 lg:px-12)

Background Video:
Video Source: HLS stream from https://stream.mux.com/s8pMcOvMQXc4GD6AX4e1o01xFogFxipmuKltNfSYza0200.m3u8
- Autoplaying, looping, muted video positioned absolutely behind content
- Video shifted 200px to the right (margin-left: 200px)
- Video scaled to 1.2x with origin-left, object-cover, full height
- Bottom fade gradient (h-40) from background color to transparent (z-10)

Badge (top element):
- Pill-shaped badge with rounded-full, border border-white/20, backdrop-blur-sm
- Contains a Sparkles icon (lucide-react, w-3 h-3, text-white/80)
- Text: "New AI Automation Ally" in text-sm font-medium text-white/80
- Animated with blur-in effect (0.6s duration, no delay)

Main Heading:
- Three lines of text:
  - Line 1: "Unlock the Power of AI" (block display)
  - Line 2: "for Your" (inline)
  - Line 3: "Business." in serif italic font (inline)
- Font sizes: text-4xl md:text-5xl lg:text-6xl
- Font weight: font-medium
- Line height: leading-tight lg:leading-[1.2]
- Color: white (text-foreground)
- Each word animates in with staggered split-text animation (0.08s delay between words, 0.6s duration, y: 40px -> 0, opacity: 0 -> 1)

Subtitle:
- Text: "Our cutting-edge AI platform automates, analyzes, and accelerates your workflows so you can focus on what really matters."
- Styling: text-white/80, text-lg, font-normal, leading-relaxed, max-w-xl
- Animated with blur-in effect (0.4s delay, 0.6s duration)

CTA Buttons (bottom):
- Two buttons side by side with gap-4, flex-wrap
- Primary button "Book A Free Call":
  - Solid white background (bg-foreground), dark text (text-background)
  - Rounded-full, px-5 py-3
  - Includes right arrow icon (ArrowRight from lucide-react)
  - Links to /book-call
- Secondary button "Learn now":
  - Semi-transparent background (bg-white/20), backdrop-blur-sm
  - Rounded-full, px-8 py-3
  - White text
- Both buttons animated with blur-in effect (0.6s delay, 0.6s duration)

Animations (using framer-motion):
- BlurIn component: opacity 0->1, blur 10px->0, y 20->0
- SplitText component: splits text by words, staggers each word's animation

Z-index layering:
- Video: z-0
- Bottom gradient: z-10
- Content: z-20

Spacing:
- 12-unit gap (gap-12) between badge/heading group and CTA buttons
- 6-unit gap (gap-6) between badge and heading, and between heading and subtitle
```

---
*NeuroFlow Academy Site Templates*


---


---
title: "Build With Us"
template_id: "b95bc843-2e09-4035-b833-67ae5e995ccd"
section: "sites"
category_slug: "other"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Build With Us

> **Секція:** `SITES` | **Категорія:** `other`  
> **ID шаблону:** `b95bc843-2e09-4035-b833-67ae5e995ccd`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Contact us

### 🖼 Прев'ю:
![Build With Us](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/6c758bc0-4a44-4dba-af63-0e69197ab60d.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a single-page React + TypeScript + Vite + Tailwind site that is a full-screen video-background landing page with a contact form. Use `lucide-react` for icons.

**Layout & Sizing**
- Root: `min-h-screen` white background with padding `p-3 sm:p-4 md:p-6`.
- Inside the root, one large rounded card with `rounded-2xl sm:rounded-3xl`, `overflow-hidden`. Heights: `min-h-[calc(100vh-24px)] sm:min-h-[calc(100vh-32px)] md:min-h-[calc(100vh-48px)] lg:h-[calc(100vh-48px)]`. On desktop it locks to viewport; on tablet/mobile it expands to content.
- Background video fills the card (`absolute inset-0 w-full h-full object-cover`). The video element has `autoPlay muted loop playsInline`. Use this exact URL:
  ```
  https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260602_150901_c45b90ec-18d7-42ff-90e2-b95d7109e330.mp4
  ```
- Content layer: `relative z-10 flex flex-col` with the same min-height ladder as the card and `lg:h-full`, padding `p-4 sm:p-6 md:p-8`, `gap-6`.

**Fonts**
- Import from Google Fonts in `index.css`: `Inter` (weights 300–700) and `Instrument Serif` (italic + regular).
- Set `* { font-family: 'Inter', sans-serif; }` globally.
- Use `Instrument Serif` italic for one accent word inline (see headline below).

**Navbar (top)**
- Pill bar with `bg-white/60 backdrop-blur-md rounded-2xl shadow-sm`, padding `pl-3 sm:pl-4 pr-2 py-2`, `w-full sm:w-auto`, `flex items-center gap-3 sm:gap-6`.
- Logo: 32x32 inline SVG (`viewBox="0 0 256 256"`) with two black filled paths forming a stylized "M":
  `M 256 256 L 128 256 L 0 128 L 128 128 Z M 256 128 L 128 128 L 0 0 L 128 0 Z`.
- Links (hidden on mobile, shown `sm:flex`): `Our story`, `Expertise`, `Our work`, `Journal` — class `text-gray-800 text-sm font-medium hover:opacity-60 transition-opacity whitespace-nowrap`.
- CTA button on the right: black pill `bg-black text-white text-sm font-medium px-4 sm:px-5 py-2 rounded-xl hover:bg-gray-800` with label `Start a project`. On mobile it floats right with `ml-auto`.

**Spacer**
- A `<div className="flex-1 min-h-[2rem]" />` between nav and the bottom row.

**Bottom row (headline + form)**
- Container: `flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6`.

**Headline (left)**
- `<p>` with white text, `text-3xl sm:text-4xl xl:text-5xl font-medium leading-tight drop-shadow-lg lg:max-w-lg xl:max-w-2xl shrink-0`.
- Content (with `<br />`):
  `We craft bold ideas` / `and ship them as *products*`
- The word `products` is wrapped in a `<span>` with inline style: `fontFamily: "'Instrument Serif', serif"`, `fontStyle: 'italic'`, `fontWeight: 400`.

**Contact form card (right)**
- Outer: `w-full lg:w-[min(480px,45%)] shrink-0`.
- Card: `bg-white rounded-2xl sm:rounded-3xl shadow-2xl overflow-hidden`, inner padding `p-4 sm:p-6`, `flex flex-col gap-4`.

1. **Heading:** `Say hello! 👋` — `text-xl sm:text-2xl font-semibold text-black tracking-tight`.

2. **Email + socials row** (always horizontal): `flex flex-row items-center justify-between gap-3 bg-gray-50 rounded-2xl px-4 py-2.5`.
   - Left: small grey label `Drop us a line`, then mailto link `hello@forma.co` in `text-blue-600 font-semibold hover:underline truncate`.
   - Right: four 32x32 rounded-xl buttons (`w-8 h-8 rounded-xl flex items-center justify-center hover:opacity-80 transition-opacity`) using lucide icons size 13:
     - Twitter — `bg-gray-100 text-gray-800`
     - Circle — `bg-pink-100 text-pink-500`
     - Instagram — `bg-orange-100 text-orange-400`
     - Linkedin — `bg-blue-100 text-blue-600`
   - Extract this into a small `SocialBtn` helper component.

3. **OR divider:** horizontal lines on either side of the word `OR` (`text-gray-400 font-medium text-sm`, lines `flex-1 h-px bg-gray-200`).

4. **Form** (`flex flex-col gap-4`):
   - Label `Tell us about your vision` (`text-sm font-medium text-black`).
   - Name + Email inputs side by side on `sm:` (`flex flex-col sm:flex-row gap-2`), placeholders `Full name` and `Email`. Input style: `flex-1 min-w-0 text-sm px-3 py-2.5 rounded-xl border border-gray-200 bg-transparent placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition`.
   - Textarea, 4 rows, placeholder `What are you looking to build or improve...`, same input style plus `resize-none`.
   - Service tags section: label `I need help with...`. Tags wrap (`flex flex-wrap gap-1.5`). Each tag is a button `text-xs font-medium px-3 py-2 rounded-lg border transition-all`. Inactive: `bg-white text-gray-700 border-gray-200 hover:border-gray-400`. Active (selected): `bg-gray-100 text-black border-black`. Multi-select toggle via state.
     - Services list (exact order): `Website`, `Mobile App`, `Web App`, `E-Commerce`, `Visual Identity`, `3D & Motion`, `Digital Marketing`, `Growth & Consulting`, `Other`.
   - Submit button: `w-full bg-black text-white text-sm font-semibold py-3 rounded-2xl hover:bg-gray-800 transition-colors disabled:opacity-60`. Label: `Send my message` (or `Sending...` while submitting).

5. **Submit behavior:** On submit, set `sending=true`, await a 1-second fake delay (`new Promise(r => setTimeout(r, 1000))`), then show a success state in place of the form: centered column with `py-6 gap-3`, a 48x48 green check pill (`w-12 h-12 rounded-full bg-green-50 flex items-center justify-center text-xl` containing `✓`), heading `You're all set!` (`text-base font-semibold text-gray-900`), and subtext `Expect a reply within 24 hours.` (`text-sm text-gray-500`).

**State (useState)**
- `selected: string[]` (toggled service chips)
- `name`, `email`, `message`: strings
- `sending`, `sent`: booleans

**Transitions/animations**
- All interactive elements use Tailwind `transition-*` utilities (opacity, colors, all).
- No external animation library; rely on Tailwind hover/focus transitions and `backdrop-blur-md` on the navbar.

**Constants at the top of the file**
- `VIDEO_URL` (the CloudFront URL above) and `SERVICES` array.

**Files**
- `src/App.tsx` — entire component plus `SocialBtn` helper.
- `src/index.css` — Google Fonts import + Tailwind directives + global `* { font-family: 'Inter', sans-serif; }`.
- Standard Vite + Tailwind config (`tailwind.config.js` scanning `./index.html` and `./src/**/*.{ts,tsx}`).
```

---
*NeuroFlow Academy Site Templates*


---

