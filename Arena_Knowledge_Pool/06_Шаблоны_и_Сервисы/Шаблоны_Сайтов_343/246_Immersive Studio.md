---
title: "Immersive Studio"
template_id: "9caf273b-5607-4b0f-b32b-35f847869328"
section: "sites"
category_slug: "agency"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/5f86c158-8bea-4f53-863d-178e5c88af30.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Immersive Studio

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `9caf273b-5607-4b0f-b32b-35f847869328`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/5f86c158-8bea-4f53-863d-178e5c88af30.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPTS:
# EXACT RECREATION PROMPT

## Tech Stack
Create a Vite + React + TypeScript project with Tailwind CSS. Install these exact dependencies:
- `framer-motion` (for animations)
- `lucide-react` (for the ArrowUpRight icon)
- `tailwindcss`, `postcss`, `autoprefixer` (devDependencies)

## Fonts (in index.html `<head>`)
```html
<link href="https://db.onlinewebfonts.com/c/23ed6ab5114b3c4b57abae46cf8a5029?family=PP+Editorial+New+Ultralight" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
```
Set page `<title>` to `Lumenvox Atelier`.

## Global CSS (src/index.css)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;


body {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

## Custom CSS Classes (in index.css)

### Liquid Glass Button Effect
```css
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
```

### Hero Heading Font
```css
.hero-heading {
  font-family: 'PP Editorial New Ultralight', serif;
  font-weight: 200;
  line-height: 0.85;
  letter-spacing: -0.02em;
}
```

### Keyframe Animations
```css
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-down {
  animation: slideDown 0.8s ease-out forwards;
}
```

### Mobile Menu Overlay (full-screen, dark #030318 background)
```css
.menu-overlay {
  position: fixed; inset: 0; z-index: 40;
  display: flex; flex-direction: column;
  background: #030318;
  opacity: 0; visibility: hidden;
  transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1),
              visibility 0s linear 0.5s;
}

.menu-overlay.is-open {
  opacity: 1; visibility: visible;
  transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1),
              visibility 0s linear 0s;
}

.menu-overlay.is-closing {
  opacity: 0;
  transition: opacity 0.4s cubic-bezier(0.22, 1, 0.36, 1) 0.15s,
              visibility 0s linear 0.55s;
}
```

### Menu Lines (horizontal dividers that scale in)
```css
.menu-overlay .menu-line {
  display: block; width: 100%; height: 1px;
  background: rgba(255, 255, 255, 0.1);
  transform: scaleX(0); transform-origin: left;
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.menu-overlay.is-open .menu-line { transform: scaleX(1); }
```
Stagger delays for menu lines: `0.05s, 0.15s, 0.25s, 0.35s` (nth-child 1-4).

### Menu Items (staggered slide-up)
```css
.menu-overlay .menu-item {
  opacity: 0; transform: translateY(30px);
  transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1),
              transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.menu-overlay.is-open .menu-item { opacity: 1; transform: translateY(0); }
.menu-overlay.is-closing .menu-item {
  opacity: 0; transform: translateY(-20px);
  transition: opacity 0.3s, transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
```
Opening stagger delays: 0.1s, 0.17s, 0.24s, 0.31s, 0.38s (nth-child 1-5).
Closing stagger delays: 0.12s, 0.09s, 0.06s, 0.03s, 0s (nth-child 1-5).

### Hamburger Icon
```css
.hamburger-line {
  display: block; width: 24px; height: 1.5px; background: white;
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s ease;
  transform-origin: center;
}
.hamburger-open .hamburger-line:nth-child(1) { transform: translateY(5px) rotate(45deg); }
.hamburger-open .hamburger-line:nth-child(2) { opacity: 0; transform: scaleX(0); }
.hamburger-open .hamburger-line:nth-child(3) { transform: translateY(-5px) rotate(-45deg); }
```

## StaggeredFade Component (src/components/StaggeredFade.tsx)
A component that splits text into individual letters and animates each letter with a staggered fade-up using framer-motion. Props: `text` (string), `delay` (per-letter delay, default 0.05), `className` (optional).

- Uses `useInView` from framer-motion with `once: true` to trigger when scrolled into view.
- Each letter starts at `{ opacity: 0, y: 8 }` and animates to `{ opacity: 1, y: 0 }`.
- Per-letter transition: `{ delay: i * delay, duration: 0.4, ease: [0.22, 1, 0.36, 1] }`.
- Spaces are rendered as non-breaking spaces (`\u00A0`).

## Page Structure (App.tsx)

### State
- `menuOpen` (boolean) — controls mobile menu visibility
- `menuClosing` (boolean) — controls closing animation phase
- On `menuOpen` change: set `body.style.overflow` to `'hidden'` or `''`
- `handleCloseMenu`: sets `menuClosing=true`, then after 550ms sets `menuOpen=false` and `menuClosing=false`
- `toggleMenu`: if open & not closing → close; if not closing → open

### Nav Items Array
```
['REEL WORK', 'PROCESS & METHODS', 'INNER WORKSHOP']
```

### Layout (root div: `relative w-full h-screen overflow-hidden`)

**1. Background Video** (absolute, full-cover):
```html
<video
  className="absolute inset-0 w-full h-full object-cover"
  src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260717_084049_407d831b-67ef-4e76-9330-45386e0a9915.mp4"
  autoPlay loop muted playsInline
/>
```

**2. Bottom Gradient Overlay** (for text contrast):
```html
<div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-[#030318]/80 to-transparent pointer-events-none" />
```

**3. Content Container** (`relative z-10 flex flex-col h-full px-4 sm:px-6 md:px-10 lg:px-14 py-4 sm:py-5 md:py-8`):

**3a. Desktop Navbar** (`hidden lg:flex items-center justify-between w-full animate-slide-down`):
- Brand text: `LUMENVOX ATELIER` — white, 10px, tracking-[0.15em], uppercase, font-medium
- 3 nav links (from array): white/80, 10px, tracking-[0.15em], uppercase, hover→white, 300ms transition
- CTA link: `START A PROJECT` + ArrowUpRight icon (size 12) — white, 10px, tracking-[0.15em], uppercase, hover→white/80

**3b. Mobile/Tablet Navbar** (`flex lg:hidden items-center justify-between w-full animate-slide-down relative z-50`):
- Brand text: `LUMENVOX ATELIER` (same styling)
- Hamburger button: 40×40px, 3 lines (24px × 1.5px, white), gap-[5px]. Class `hamburger-open` applied when `menuOpen && !menuClosing`.

**3c. Mobile Menu Overlay** (class `menu-overlay` + `is-open` when open + `is-closing` when closing):
- Full-screen flex column, centered, `#030318` background
- Each nav item wrapped with `menu-line` dividers (1px, white/10%, scaleX animation)
- Nav items: white, `text-xl sm:text-2xl`, tracking-[0.25em], uppercase, `py-6 sm:py-8`, hover→white/70
- Final item: `START A PROJECT` + ArrowUpRight (size 18), flex with gap-3

**3d. Spacer** (`flex-1`)

**3e. Hero Content** (bottom-aligned):

**Row 1 — Large Typography** (`flex flex-col md:flex-row md:justify-between md:items-end mb-4 sm:mb-6 md:mb-8`):

Left column:
- `<p>`: `hero-heading`, `text-[6vw] sm:text-[5vw] md:text-[3.5vw] lg:text-[3vw]`, white, `mb-2 sm:mb-4 md:mb-6`. Text: `Visions So` via StaggeredFade (delay=0.06)
- `<h1>`: `hero-heading`, `text-[14vw] sm:text-[13vw] md:text-[10vw] lg:text-[9vw]`, white, `leading-none`. Text: `UNDENIABLE` via StaggeredFade (delay=0.05)

Right column (`text-right mt-2 sm:mt-3 md:mt-0`):
- `<p>`: `hero-heading`, `text-[14vw] sm:text-[13vw] md:text-[10vw] lg:text-[9vw]`, white, `mb-2 sm:mb-4 md:mb-6`, `leading-none`. Text: `So` via StaggeredFade (delay=0.08)
- `<h1>`: same sizing. Text: `RESIST` via StaggeredFade (delay=0.05)

**Row 2 — Bottom Bar** (`flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 sm:gap-6 pt-4 sm:pt-5 md:pt-6`):

Left column (`flex items-start gap-4 sm:gap-5 md:gap-8`):

- **Logo image** (framer-motion `motion.div`):
  - Animation: `initial={{ opacity: 0, scale: 0.8 }}` → `animate={{ opacity: 1, scale: 1 }}`, `transition={{ delay: 0.6, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}`
  - Sizing: `w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20`, `rounded-2xl`, `overflow-hidden`, `flex-shrink-0`, `border border-white/20`
  - Image src: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260717_095034_599c0e43-e5a1-48c0-b169-f1267d71a58c.png&w=1280&q=85`
  - Image class: `w-full h-full object-cover`, alt="Logo"

- **Info columns** (`hidden sm:flex items-start gap-6 md:gap-14`):
  - Column 1 (framer-motion `motion.div`, delay=0.8, y:16→0, duration 0.6, same ease):
    - Label: `01 — OUR CRAFT` — white, `text-[10px] sm:text-[11px] md:text-[13px]`, tracking-[0.15em], uppercase, `mb-1 sm:mb-1.5`
    - Description: `Visual systems, immersive platforms and artistic vision forged into one cohesive entity.` — white/80, `text-[9px] sm:text-[10px] md:text-[11px]`, `leading-relaxed`, uppercase, tracking-wide, `max-w-[220px] md:max-w-[260px]`
  - Column 2 (framer-motion, delay=1.0, same animation):
    - Label: `02 — OUR APPROACH` (same label styling)
    - Description: `Intention shapes the story. Form amplifies the mood. Detail seals it in memory.` (same desc styling)

Right column — **CTA Button** (framer-motion `motion.a`, delay=1.2, y:16→0, duration 0.6, same ease):
- Class: `liquid-glass rounded-full px-5 py-2.5 sm:px-6 sm:py-3 md:px-8 md:py-4 flex items-center gap-2 sm:gap-3 text-white text-[9px] sm:text-[10px] md:text-xs tracking-[0.2em] uppercase hover:bg-white/5 transition-all duration-300 group`
- Text: `START A PROJECT`
- Icon: ArrowUpRight (size 14), class: `group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300`

## Animation Timing Summary
| Element | Animation | Delay | Duration | Ease |
|---------|-----------|-------|----------|------|
| Navbar | slideDown | 0s | 0.8s | ease-out |
| Hero letters | staggered fade-up | per-letter × delay | 0.4s | [0.22,1,0.36,1] |
| Logo image | scale 0.8→1 + fade | 0.6s | 0.6s | [0.22,1,0.36,1] |
| Info col 1 | y:16→0 + fade | 0.8s | 0.6s | [0.22,1,0.36,1] |
| Info col 2 | y:16→0 + fade | 1.0s | 0.6s | [0.22,1,0.36,1] |
| CTA button | y:16→0 + fade | 1.2s | 0.6s | [0.22,1,0.36,1] |
| Mobile menu items | y:30→0 + fade | 0.1-0.38s stagger | 0.5s | [0.22,1,0.36,1] |
| Menu lines | scaleX 0→1 | 0.05-0.35s stagger | 0.6s | [0.22,1,0.36,1] |

## Colors
- Background: `#030318` (dark navy)
- Text primary: white
- Text secondary: `white/80`
- Borders/dividers: `white/20`, `white/10`
- Gradient overlay: `from-[#030318]/80 to-transparent`

## Exact Copy (all text on the page)
- Brand: `LUMENVOX ATELIER`
- Nav: `REEL WORK`, `PROCESS & METHODS`, `INNER WORKSHOP`
- Hero: `Visions So` / `UNDENIABLE` / `So` / `RESIST`
- Info 1 label: `01 — OUR CRAFT`
- Info 1 desc: `Visual systems, immersive platforms and artistic vision forged into one cohesive entity.`
- Info 2 label: `02 — OUR APPROACH`
- Info 2 desc: `Intention shapes the story. Form amplifies the mood. Detail seals it in memory.`
- CTA: `START A PROJECT`

## Responsive Breakpoints
- **<640px (mobile)**: hamburger menu, info columns hidden, smallest font sizes, single-column hero
- **640-1023px (tablet)**: hamburger menu, info columns visible, medium sizes
- **≥1024px (desktop)**: full desktop navbar, all elements visible, largest sizes

---

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Lumenvox Atelier</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      background: #030318;
    }

    .wrapper {
      position: relative;
      width: 100%;
      height: 100vh;
      overflow: hidden;
    }

    /* Background Video */
    .bg-video {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    /* Bottom Gradient */
    .bottom-gradient {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 33%;
      background: linear-gradient(to top, rgba(3,3,24,0.8), transparent);
      pointer-events: none;
    }

    /* Content Container */
    .content {
      position: relative;
      z-index: 10;
      display: flex;
      flex-direction: column;
      height: 100%;
      padding: 2rem 3.5rem;
    }

    /* Navbar */
    .navbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      animation: slideDown 0.8s ease-out forwards;
    }

    .nav-brand {
      color: white;
      font-size: 10px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      font-weight: 500;
      text-decoration: none;
    }

    .nav-link {
      color: rgba(255,255,255,0.8);
      font-size: 10px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      text-decoration: none;
      transition: color 0.3s;
    }

    .nav-link:hover {
      color: white;
    }

    .nav-cta {
      color: white;
      font-size: 10px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: color 0.3s;
    }

    .nav-cta:hover {
      color: rgba(255,255,255,0.8);
    }

    .nav-cta svg {
      width: 12px;
      height: 12px;
    }

    /* Spacer */
    .spacer { flex: 1; }

    /* Hero Typography */
    .hero-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 2rem;
    }

    .hero-heading {
      font-family: Georgia, 'Times New Roman', serif;
      font-weight: 200;
      line-height: 0.85;
      letter-spacing: -0.02em;
      color: white;
    }

    .hero-sub {
      font-size: 3vw;
      margin-bottom: 1.5rem;
    }

    .hero-main {
      font-size: 9vw;
    }

    .hero-right {
      text-align: right;
    }

    /* Staggered Letter Animation */
    .stagger-letter {
      display: inline-block;
      opacity: 0;
      transform: translateY(8px);
      animation: letterReveal 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    /* Bottom Bar */
    .bottom-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      padding-top: 1.5rem;
    }

    .bottom-left {
      display: flex;
      align-items: flex-start;
      gap: 2rem;
    }

    /* Logo Image */
    .logo-img-wrap {
      width: 80px;
      height: 80px;
      border-radius: 1rem;
      overflow: hidden;
      flex-shrink: 0;
      border: 1px solid rgba(255,255,255,0.2);
      opacity: 0;
      transform: scale(0.8);
      animation: scaleIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.6s forwards;
    }

    .logo-img-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    /* Info Columns */
    .info-columns {
      display: flex;
      align-items: flex-start;
      gap: 3.5rem;
    }

    .info-col {
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .info-col:nth-child(1) { animation-delay: 0.8s; }
    .info-col:nth-child(2) { animation-delay: 1.0s; }

    .info-col .label {
      color: white;
      font-size: 13px;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }

    .info-col .desc {
      color: rgba(255,255,255,0.8);
      font-size: 11px;
      line-height: 1.6;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      max-width: 260px;
    }

    /* CTA Button */
    .cta-btn {
      display: flex;
      align-items: center;
      gap: 12px;
      color: white;
      font-size: 12px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      text-decoration: none;
      padding: 1rem 2rem;
      border-radius: 9999px;
      position: relative;
      overflow: hidden;
      background: rgba(255,255,255,0.01);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
      opacity: 0;
      transform: translateY(16px);
      animation: fadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 1.2s forwards;
      transition: background 0.3s;
    }

    .cta-btn::before {
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

    .cta-btn:hover {
      background: rgba(255,255,255,0.05);
    }

    .cta-btn svg {
      width: 14px;
      height: 14px;
      transition: transform 0.3s;
    }

    .cta-btn:hover svg {
      transform: translate(2px, -2px);
    }

    /* Mobile Hamburger */
    .hamburger {
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 5px;
      width: 40px;
      height: 40px;
      background: none;
      border: none;
      cursor: pointer;
      z-index: 60;
    }

    .hamburger span {
      display: block;
      width: 24px;
      height: 1.5px;
      background: white;
      transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s ease;
      transform-origin: center;
    }

    .hamburger.open span:nth-child(1) { transform: translateY(6.5px) rotate(45deg); }
    .hamburger.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
    .hamburger.open span:nth-child(3) { transform: translateY(-6.5px) rotate(-45deg); }

    /* Mobile Menu Overlay */
    .menu-overlay {
      position: fixed;
      inset: 0;
      z-index: 50;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background: #030318;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1), visibility 0s linear 0.5s;
    }

    .menu-overlay.is-open {
      opacity: 1;
      visibility: visible;
      transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1), visibility 0s linear 0s;
    }

    .menu-overlay a {
      color: white;
      font-size: 1.5rem;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      text-decoration: none;
      padding: 1.5rem 0;
      display: block;
      text-align: center;
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1), transform 0.5s cubic-bezier(0.22, 1, 0.36, 1), color 0.3s;
    }

    .menu-overlay a:hover { color: rgba(255,255,255,0.7); }

    .menu-overlay.is-open a {
      opacity: 1;
      transform: translateY(0);
    }

    .menu-overlay.is-open a:nth-child(1) { transition-delay: 0.1s; }
    .menu-overlay.is-open a:nth-child(2) { transition-delay: 0.17s; }
    .menu-overlay.is-open a:nth-child(3) { transition-delay: 0.24s; }
    .menu-overlay.is-open a:nth-child(4) { transition-delay: 0.31s; }

    .menu-line {
      width: 100%;
      max-width: 28rem;
      height: 1px;
      background: rgba(255,255,255,0.1);
      transform: scaleX(0);
      transform-origin: left;
      transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
    }

    .menu-overlay.is-open .menu-line { transform: scaleX(1); }

    /* Keyframes */
    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes scaleIn {
      from { opacity: 0; transform: scale(0.8); }
      to { opacity: 1; transform: scale(1); }
    }

    @keyframes letterReveal {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Responsive */
    @media (max-width: 1023px) {
      .navbar .nav-link,
      .navbar .nav-cta {
        display: none;
      }
      .hamburger {
        display: flex;
      }
      .content {
        padding: 1.25rem 1.5rem;
      }
      .info-columns {
        display: none;
      }
      .hero-sub { font-size: 5vw; }
      .hero-main { font-size: 13vw; }
      .logo-img-wrap { width: 48px; height: 48px; }
    }

    @media (min-width: 640px) and (max-width: 1023px) {
      .content { padding: 1.25rem 1.5rem; }
      .info-columns { display: flex; gap: 1.5rem; }
      .logo-img-wrap { width: 64px; height: 64px; }
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <!-- Background Video -->
    <video
      class="bg-video"
      src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260717_084049_407d831b-67ef-4e76-9330-45386e0a9915.mp4"
      autoplay
      loop
      muted
      playsinline
    ></video>

    <!-- Bottom Gradient -->
    <div class="bottom-gradient"></div>

    <!-- Content -->
    <div class="content">
      <!-- Navbar -->
      <nav class="navbar">
        <span class="nav-brand">LUMENVOX ATELIER</span>
        <a href="#" class="nav-link">REEL WORK</a>
        <a href="#" class="nav-link">PROCESS & METHODS</a>
        <a href="#" class="nav-link">INNER WORKSHOP</a>
        <a href="#" class="nav-cta">
          START A PROJECT
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
        </a>
        <button class="hamburger" id="hamburgerBtn" aria-label="Toggle menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </nav>

      <!-- Mobile Menu -->
      <div class="menu-overlay" id="menuOverlay">
        <div class="menu-line"></div>
        <a href="#" onclick="closeMenu()">REEL WORK</a>
        <div class="menu-line"></div>
        <a href="#" onclick="closeMenu()">PROCESS & METHODS</a>
        <div class="menu-line"></div>
        <a href="#" onclick="closeMenu()">INNER WORKSHOP</a>
        <div class="menu-line"></div>
        <a href="#" onclick="closeMenu()" style="display:flex;align-items:center;justify-content:center;gap:12px;">
          START A PROJECT
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
        </a>
      </div>

      <!-- Spacer -->
      <div class="spacer"></div>

      <!-- Hero Content -->
      <div>
        <!-- Row 1: Typography -->
        <div class="hero-row">
          <div>
            <p class="hero-heading hero-sub" id="line1"></p>
            <h1 class="hero-heading hero-main" id="line2"></h1>
          </div>
          <div class="hero-right">
            <p class="hero-heading hero-main" style="margin-bottom:1.5rem" id="line3"></p>
            <h1 class="hero-heading hero-main" id="line4"></h1>
          </div>
        </div>

        <!-- Row 2: Bottom Bar -->
        <div class="bottom-bar">
          <div class="bottom-left">
            <!-- Logo -->
            <div class="logo-img-wrap">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260717_095034_599c0e43-e5a1-48c0-b169-f1267d71a58c.png&w=1280&q=85"
                alt="Logo"
              />
            </div>

            <!-- Info Columns -->
            <div class="info-columns">
              <div class="info-col">
                <p class="label">01 — OUR CRAFT</p>
                <p class="desc">Visual systems, immersive platforms and artistic vision forged into one cohesive entity.</p>
              </div>
              <div class="info-col">
                <p class="label">02 — OUR APPROACH</p>
                <p class="desc">Intention shapes the story. Form amplifies the mood. Detail seals it in memory.</p>
              </div>
            </div>
          </div>

          <!-- CTA Button -->
          <a href="#" class="cta-btn">
            START A PROJECT
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
          </a>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Staggered letter animation
    function staggerText(elementId, text, baseDelay, perLetterDelay) {
      const el = document.getElementById(elementId);
      el.innerHTML = '';
      text.split('').forEach((char, i) => {
        const span = document.createElement('span');
        span.className = 'stagger-letter';
        span.textContent = char === ' ' ? '\u00A0' : char;
        span.style.animationDelay = (baseDelay + i * perLetterDelay) + 's';
        el.appendChild(span);
      });
    }

    staggerText('line1', 'Visions So', 0.2, 0.06);
    staggerText('line2', 'UNDENIABLE', 0.3, 0.05);
    staggerText('line3', 'So', 0.4, 0.08);
    staggerText('line4', 'RESIST', 0.5, 0.05);

    // Mobile menu toggle
    const hamburger = document.getElementById('hamburgerBtn');
    const overlay = document.getElementById('menuOverlay');
    let menuOpen = false;

    hamburger.addEventListener('click', () => {
      menuOpen = !menuOpen;
      if (menuOpen) {
        overlay.classList.add('is-open');
        hamburger.classList.add('open');
        document.body.style.overflow = 'hidden';
      } else {
        closeMenu();
      }
    });

    function closeMenu() {
      overlay.classList.remove('is-open');
      hamburger.classList.remove('open');
      document.body.style.overflow = '';
      menuOpen = false;
    }
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*