---
title: "Sky Estate"
template_id: "ec3caebf-7adb-4251-898e-d2c930aea766"
section: "sites"
category_slug: "travel"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/2752c998-10d8-4126-9dde-e78326fc3271.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Sky Estate

> **Секція:** `SITES` | **Категорія:** `travel`  
> **ID шаблону:** `ec3caebf-7adb-4251-898e-d2c930aea766`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/2752c998-10d8-4126-9dde-e78326fc3271.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
**Create a luxury real estate landing page called "Galaxy Home" (brand name "Aether Lane") using React, TypeScript, Vite, Tailwind CSS, and Framer Motion. Use the Google Font "Inter Tight" (weights 400, 500, 600, 700). The page has a dark/cosmic aesthetic with parallax scrolling effects and layered imagery.**

---

### Tech Stack & Dependencies
- React 18, TypeScript, Vite
- Tailwind CSS 3.4
- Framer Motion 12
- Lucide React for icons

### Tailwind Config
Custom brand colors:
- `brand-blue`: `#8F9EFF`
- `brand-navy`: `#271C40`
- `brand-dark`: `#020319`

Custom animations:
- `marquee`: translateX 0% to -50%, 30s linear infinite
- `marquee-reverse`: translateX -50% to 0%, 30s linear infinite

Font: `'Inter Tight', system-ui, sans-serif`

### Global CSS
```css
body { font-family: 'Inter Tight', system-ui, sans-serif; overflow-x: hidden; }
* { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
html { scroll-behavior: smooth; }
```

---

### Section 1: Navbar (fixed, centered, floating pill)
- Fixed at top center with `z-[60]`, padding `px-4 pt-4 md:pt-6`
- Pill shape: `rounded-full bg-[#312D7C]/40 backdrop-blur-[15px]`, gaps `gap-4 md:gap-8 lg:gap-20`, padding `px-4 py-3`
- Logo: custom SVG (4-petal/clover shape) at `h-6 w-6 md:h-7 md:w-7`, fill white, viewBox `0 0 256 256`, path: `M 228 0 C 172.772 0 128 44.772 128 100 L 128 0 L 0 0 L 0 28 C 0 83.228 44.772 128 100 128 L 0 128 L 0 256 L 28 256 C 83.228 256 128 211.228 128 156 L 128 256 L 256 256 L 256 228 C 256 172.772 211.228 128 156 128 L 256 128 L 256 0 Z`
- Brand name: "Aether Lane", `text-base md:text-xl font-medium text-white`, gap-2 from logo
- Nav links: `['Home', 'About', 'Estates', 'Projects', 'Inquire']`, hidden on mobile, `gap-6`, `text-sm`, first link white, rest `text-[#B6B8C3] hover:text-white`
- CTA button: "Get in touch", `rounded-full border border-white/80 px-6 py-2 text-[15px] font-medium`, background: `linear-gradient(180deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.10) 76%), radial-gradient(ellipse at 50% 100%, rgba(255,255,255,0.7) 0%, transparent 100%), #BEC7FF`, text color `text-brand-navy/80 drop-shadow-sm`, hover scale 1.05
- Mobile: Animated hamburger (3 bars that animate to X using Framer Motion), opens fullscreen overlay (`bg-brand-dark/95 backdrop-blur-xl`) with staggered link animations (fade up + blur)

---

### Section 2: Hero (full viewport height, parallax layers)
- Full `h-screen w-full overflow-hidden`, `z-10`
- Uses `useScroll` targeting the section with offset `['start start', 'end start']`
- Parallax `bgY`: transforms scrollYProgress [0,1] to ['0%', '8%']

**Layer 1 (z-0) - Sky background:**
- Image URL: `https://soft-zoom-63098134.figma.site/_assets/v11/7af55796a90a26e2d57c9fa2a48815874023cff0.png`
- `h-[120%] w-full object-cover`, animated with `y: bgY`

**Layer 2 (z-10) - Title text:**
- Positioned with `pt-[22vh] md:pt-32 lg:pt-36`, centered
- Text: "Galaxy  Home" (with `&nbsp;&nbsp;` double space between words)
- Font: `text-[clamp(3rem,14vw,14rem)] font-semibold leading-none whitespace-nowrap`
- Gradient text: `bg-clip-text text-transparent`, `backgroundImage: 'linear-gradient(to bottom, #A8B4FF, #FFFFFF)'`
- `mix-blend-lighten` to blend with layers

**Layer 3 (z-20) - Subtexts:**
- Left: "Elegance Above the Skyline" at `left-6 top-[200px] md:left-12 md:top-[320px] lg:left-24`, `text-lg md:text-[22px] md:leading-6 font-medium text-white/70 mix-blend-overlay`, hidden on mobile
- Right: "Your Dream Residence Starts Here" at `right-6 top-[200px] md:right-12 md:top-[320px] lg:right-24`, same styling but `text-white`, hidden on mobile

**Layer 4 (z-30) - Building image (overlaps text):**
- Image URL: `https://soft-zoom-63098134.figma.site/_assets/v11/644aba5492aa8bd5756bc5c6d65255d577b1aaf3.png`
- `h-[120%] w-full object-cover`, same parallax `y: bgY`

---

### Section 3: Mountain Background + Content (overlaps hero by -25vh)
- Wrapper: `relative z-40 -mt-[25vh]`
- Mountain image in background with separate parallax: `useScroll` on entire wrapper (offset `['start start', 'end end']`), transforms to ['0%', '-20%']
- Mountain image URL: `https://soft-zoom-63098134.figma.site/_assets/v11/3d8fdaf726b804c1299840860af873a910ce1571.png`
- `h-[120%] w-full object-cover object-top`, positioned `absolute -top-[10vh] left-0 right-0 bottom-0`

---

### Section 4: Content Section (inside mountain wrapper)
- Padding: `pt-24 sm:pt-32 md:pt-40`

**Description block:**
- Centered column, `px-5 sm:px-6 py-16 md:py-32`
- Text: "Explore distinguished estates, iconic design, and meticulously curated homes across the globe's most sought-after destinations."
- `max-w-[600px] text-sm sm:text-base md:text-lg font-medium text-white/90 leading-relaxed text-center`
- Text shadow: `2px 4px 26px rgba(0, 0, 0, 0.56)`
- CTA button: same style as navbar "Get in touch", `mt-6 sm:mt-7 px-8 sm:px-10 py-2.5 sm:py-3 text-base sm:text-lg`

---

### Section 5: Text Fill Section (scroll-driven character reveal)
- Container: `max-w-[820px]` centered, `px-5 sm:px-6 pb-16 sm:pb-24 pt-8 sm:pt-12 md:px-12`
- Text: "We present refined estates that merge remarkable design, prime surroundings, and relentless craftsmanship. Each residence is chosen for the experience it delivers not merely the footprint it provides."
- Font: `text-xl sm:text-2xl md:text-[40px] md:leading-[48px] text-center leading-snug tracking-tight font-medium text-white`
- Animation: Each character uses `useTransform` on scroll progress. Characters start at `opacity: 0.25` and animate to `opacity: 1` as the user scrolls. Uses `useScroll` with offset `['start 0.8', 'end 0.2']`. Each character calculates its own start/end threshold based on its index relative to total character count (range +/- 0.01 around its position).

---

### Section 6: Logo Marquee (infinite scroll)
- Container: `max-w-[820px]` centered, `py-4 sm:py-6`, overflow hidden
- Row 1 (left to right): Sparkles/"Prism", Waves/"Cascade", Star/"Pinnacle" (repeated), uses `animate-marquee`
- Row 2 (right to left): Zap/"Impulse", Orbit/"Nexus", Gem/"Radiant" (repeated), uses `animate-marquee-reverse`
- Each logo item: Lucide icon (`h-4 w-4 sm:h-5 sm:w-5 text-white/80`) + name (`text-sm sm:text-base font-medium text-white/90 whitespace-nowrap`)
- Double-duplicated arrays for seamless loop, `gap-8 sm:gap-12`

---

### Section 7: Stats Section
- `px-5 sm:px-6 py-16 md:py-32`
- White gradient overlay on top: `absolute -top-[400px] left-0 right-0 bottom-0`, `bg-gradient-to-b from-transparent via-white/60 to-white`
- Heading: "Only the proven results here", `text-2xl md:text-[40px] md:leading-[44px] font-medium text-brand-navy text-center mb-10 sm:mb-16`
- Stats grid: `grid-cols-2 md:flex`, `max-w-5xl` centered
- Stats data:
  - "500" / "Estates Delivered"
  - "25" / "Exclusive Markets"
  - "12" / "Years in the Field"
  - "99%" / "Owner Satisfaction"
- Values: `text-4xl sm:text-5xl md:text-[64px] md:leading-[76px] font-semibold text-brand-navy`
- Labels: `text-sm sm:text-base md:text-xl font-medium text-brand-navy/70 text-center`
- Dividers between stats (desktop only): `h-[80px] w-px bg-brand-navy/20 mx-8 lg:mx-12`
- Animate in view with Framer Motion `useInView` (once, margin -100px): fade up (`opacity: 0, y: 30` to `opacity: 1, y: 0`), staggered by 0.15s per stat, duration 0.6s

---

### Image URLs (exact)
1. Sky/hero background: `https://soft-zoom-63098134.figma.site/_assets/v11/7af55796a90a26e2d57c9fa2a48815874023cff0.png`
2. Building (transparent foreground): `https://soft-zoom-63098134.figma.site/_assets/v11/644aba5492aa8bd5756bc5c6d65255d577b1aaf3.png`
3. Mountain/landscape: `https://soft-zoom-63098134.figma.site/_assets/v11/3d8fdaf726b804c1299840860af873a910ce1571.png`

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Galaxy Home | Luxury Real Estate</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      font-family: 'Inter Tight', system-ui, sans-serif;
      overflow-x: hidden;
      background: #000;
    }

    /* Navbar */
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 60;
      display: flex;
      justify-content: center;
      padding: 16px 16px 0;
    }

    @media (min-width: 768px) {
      .navbar { padding-top: 24px; }
    }

    .navbar-pill {
      display: flex;
      align-items: center;
      gap: 16px;
      border-radius: 9999px;
      background: rgba(49, 45, 124, 0.4);
      backdrop-filter: blur(15px);
      -webkit-backdrop-filter: blur(15px);
      padding: 12px 16px;
    }

    @media (min-width: 768px) {
      .navbar-pill { gap: 32px; }
    }

    @media (min-width: 1024px) {
      .navbar-pill { gap: 80px; }
    }

    .navbar-brand {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .navbar-brand svg {
      width: 24px;
      height: 24px;
    }

    @media (min-width: 768px) {
      .navbar-brand svg { width: 28px; height: 28px; }
    }

    .navbar-brand span {
      font-size: 16px;
      font-weight: 500;
      color: white;
    }

    @media (min-width: 768px) {
      .navbar-brand span { font-size: 20px; }
    }

    .navbar-links {
      display: none;
      align-items: center;
      gap: 24px;
      list-style: none;
    }

    @media (min-width: 768px) {
      .navbar-links { display: flex; }
    }

    .navbar-links a {
      font-size: 14px;
      color: #B6B8C3;
      text-decoration: none;
      transition: color 0.2s;
    }

    .navbar-links a:hover,
    .navbar-links a.active {
      color: white;
    }

    .btn-cta {
      position: relative;
      overflow: hidden;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.8);
      padding: 8px 24px;
      font-size: 15px;
      font-weight: 500;
      color: rgba(39, 28, 64, 0.8);
      background: linear-gradient(180deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.10) 76%), radial-gradient(ellipse at 50% 100%, rgba(255,255,255,0.7) 0%, transparent 100%), #BEC7FF;
      cursor: pointer;
      transition: transform 0.2s;
      text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    .btn-cta:hover {
      transform: scale(1.05);
    }

    .btn-cta-nav {
      display: none;
    }

    @media (min-width: 768px) {
      .btn-cta-nav { display: block; }
    }

    .hamburger {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      background: none;
      border: none;
      cursor: pointer;
      position: relative;
      z-index: 60;
    }

    @media (min-width: 768px) {
      .hamburger { display: none; }
    }

    .hamburger span {
      position: absolute;
      left: 8px;
      height: 2px;
      width: 20px;
      border-radius: 9999px;
      background: white;
      transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    .hamburger span:nth-child(1) { top: 10px; }
    .hamburger span:nth-child(2) { top: 17px; }
    .hamburger span:nth-child(3) { top: 24px; }

    .hamburger.open span:nth-child(1) { transform: rotate(45deg); top: 17px; }
    .hamburger.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
    .hamburger.open span:nth-child(3) { transform: rotate(-45deg); top: 17px; }

    .mobile-menu {
      position: fixed;
      inset: 0;
      z-index: 55;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: rgba(2, 3, 25, 0.95);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }

    .mobile-menu.open {
      opacity: 1;
      pointer-events: all;
    }

    .mobile-menu nav {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 32px;
    }

    .mobile-menu a {
      font-size: 30px;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.9);
      text-decoration: none;
      transition: color 0.2s;
      opacity: 0;
      transform: translateY(20px);
      filter: blur(4px);
      transition: opacity 0.35s ease, transform 0.35s ease, filter 0.35s ease;
    }

    .mobile-menu.open a {
      opacity: 1;
      transform: translateY(0);
      filter: blur(0);
    }

    .mobile-menu.open a:nth-child(1) { transition-delay: 0.1s; }
    .mobile-menu.open a:nth-child(2) { transition-delay: 0.16s; }
    .mobile-menu.open a:nth-child(3) { transition-delay: 0.22s; }
    .mobile-menu.open a:nth-child(4) { transition-delay: 0.28s; }
    .mobile-menu.open a:nth-child(5) { transition-delay: 0.34s; }

    .mobile-menu .btn-cta {
      margin-top: 16px;
      padding: 12px 32px;
      font-size: 18px;
      opacity: 0;
      transform: translateY(20px);
      filter: blur(4px);
      transition: opacity 0.35s ease, transform 0.35s ease, filter 0.35s ease, background 0.2s;
    }

    .mobile-menu.open .btn-cta {
      opacity: 1;
      transform: translateY(0);
      filter: blur(0);
      transition-delay: 0.4s;
    }

    /* Hero */
    .hero {
      position: relative;
      z-index: 10;
      height: 100vh;
      width: 100%;
      overflow: hidden;
    }

    .hero-sky {
      position: absolute;
      inset: 0;
      z-index: 0;
    }

    .hero-sky img {
      width: 100%;
      height: 120%;
      object-fit: cover;
    }

    .hero-title-wrap {
      position: absolute;
      inset: 0;
      z-index: 10;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding-top: 22vh;
    }

    @media (min-width: 768px) {
      .hero-title-wrap { padding-top: 128px; }
    }

    @media (min-width: 1024px) {
      .hero-title-wrap { padding-top: 144px; }
    }

    .hero-title {
      white-space: nowrap;
      text-align: center;
      font-size: clamp(3rem, 14vw, 14rem);
      font-weight: 600;
      line-height: 1;
      background-image: linear-gradient(to bottom, #A8B4FF, #FFFFFF);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      mix-blend-mode: lighten;
    }

    .hero-subtext {
      position: absolute;
      z-index: 20;
      mix-blend-mode: overlay;
      display: none;
    }

    @media (min-width: 768px) {
      .hero-subtext { display: block; }
    }

    .hero-subtext-left {
      left: 48px;
      top: 320px;
    }

    @media (min-width: 1024px) {
      .hero-subtext-left { left: 96px; }
    }

    .hero-subtext-right {
      right: 48px;
      top: 320px;
    }

    @media (min-width: 1024px) {
      .hero-subtext-right { right: 96px; }
    }

    .hero-subtext p {
      font-size: 22px;
      line-height: 24px;
      font-weight: 500;
    }

    .hero-subtext-left p {
      color: rgba(255, 255, 255, 0.7);
    }

    .hero-subtext-right p {
      color: white;
    }

    .hero-building {
      position: absolute;
      inset: 0;
      z-index: 30;
    }

    .hero-building img {
      width: 100%;
      height: 120%;
      object-fit: cover;
    }

    /* Mountain wrapper */
    .mountain-wrapper {
      position: relative;
      z-index: 40;
      margin-top: -25vh;
    }

    .mountain-bg {
      position: absolute;
      top: -10vh;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 0;
    }

    .mountain-bg img {
      width: 100%;
      height: 120%;
      object-fit: cover;
      object-position: top;
    }

    .mountain-content {
      position: relative;
      z-index: 10;
    }

    /* Content Section */
    .content-section {
      position: relative;
      padding-top: 96px;
    }

    @media (min-width: 640px) {
      .content-section { padding-top: 128px; }
    }

    @media (min-width: 768px) {
      .content-section { padding-top: 160px; }
    }

    .description-block {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 64px 20px;
    }

    @media (min-width: 768px) {
      .description-block { padding: 128px 24px; }
    }

    .description-text {
      max-width: 600px;
      text-align: center;
      font-size: 14px;
      font-weight: 500;
      line-height: 1.625;
      color: rgba(255, 255, 255, 0.9);
      text-shadow: 2px 4px 26px rgba(0, 0, 0, 0.56);
    }

    @media (min-width: 640px) {
      .description-text { font-size: 16px; }
    }

    @media (min-width: 768px) {
      .description-text { font-size: 18px; }
    }

    .description-block .btn-cta {
      margin-top: 24px;
      padding: 10px 32px;
      font-size: 16px;
    }

    @media (min-width: 640px) {
      .description-block .btn-cta {
        margin-top: 28px;
        padding: 12px 40px;
        font-size: 18px;
      }
    }

    /* Text Fill Section */
    .text-fill-section {
      position: relative;
      display: flex;
      width: 100%;
      align-items: center;
      justify-content: center;
    }

    .text-fill-inner {
      width: 100%;
      max-width: 820px;
      padding: 32px 20px 64px;
    }

    @media (min-width: 640px) {
      .text-fill-inner { padding: 48px 24px 96px; }
    }

    @media (min-width: 768px) {
      .text-fill-inner { padding: 48px 48px 96px; }
    }

    .text-fill-paragraph {
      text-align: center;
      font-size: 20px;
      line-height: 1.3;
      letter-spacing: -0.02em;
    }

    @media (min-width: 640px) {
      .text-fill-paragraph { font-size: 24px; }
    }

    @media (min-width: 768px) {
      .text-fill-paragraph { font-size: 40px; line-height: 48px; }
    }

    .text-fill-paragraph .char {
      font-weight: 500;
      color: white;
      opacity: 0.25;
      transition: opacity 0.05s linear;
    }

    /* Logo Marquee */
    .marquee-section {
      position: relative;
      max-width: 820px;
      margin: 0 auto;
      overflow: hidden;
      padding: 16px 0;
    }

    @media (min-width: 640px) {
      .marquee-section { padding: 24px 0; }
    }

    .marquee-row {
      display: flex;
      overflow: hidden;
      margin-bottom: 20px;
    }

    @media (min-width: 640px) {
      .marquee-row { margin-bottom: 32px; }
    }

    .marquee-row:last-child {
      margin-bottom: 0;
    }

    .marquee-track {
      display: flex;
      align-items: center;
      gap: 32px;
      animation: marquee 30s linear infinite;
    }

    @media (min-width: 640px) {
      .marquee-track { gap: 48px; }
    }

    .marquee-row-reverse .marquee-track {
      animation: marquee-reverse 30s linear infinite;
    }

    @keyframes marquee {
      0% { transform: translateX(0%); }
      100% { transform: translateX(-50%); }
    }

    @keyframes marquee-reverse {
      0% { transform: translateX(-50%); }
      100% { transform: translateX(0%); }
    }

    .logo-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 0 12px;
      flex-shrink: 0;
    }

    @media (min-width: 640px) {
      .logo-item { gap: 8px; padding: 0 16px; }
    }

    .logo-item svg {
      width: 16px;
      height: 16px;
      color: rgba(255, 255, 255, 0.8);
    }

    @media (min-width: 640px) {
      .logo-item svg { width: 20px; height: 20px; }
    }

    .logo-item span {
      white-space: nowrap;
      font-size: 14px;
      font-weight: 500;
      color: rgba(255, 255, 255, 0.9);
    }

    @media (min-width: 640px) {
      .logo-item span { font-size: 16px; }
    }

    /* Stats Section */
    .stats-section {
      position: relative;
      padding: 64px 20px;
    }

    @media (min-width: 768px) {
      .stats-section { padding: 128px 24px; }
    }

    .stats-gradient {
      pointer-events: none;
      position: absolute;
      top: -400px;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 0;
      background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.6) 50%, white);
    }

    .stats-content {
      position: relative;
      z-index: 10;
      max-width: 1024px;
      margin: 0 auto;
    }

    .stats-title {
      margin-bottom: 40px;
      text-align: center;
      font-size: 24px;
      font-weight: 500;
      color: #271C40;
    }

    @media (min-width: 640px) {
      .stats-title { margin-bottom: 64px; }
    }

    @media (min-width: 768px) {
      .stats-title { font-size: 40px; line-height: 44px; }
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 32px;
    }

    @media (min-width: 768px) {
      .stats-grid {
        display: flex;
        flex-wrap: nowrap;
        align-items: center;
        justify-content: center;
        gap: 0;
      }
    }

    .stat-item-wrap {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }

    @media (min-width: 768px) {
      .stat-item { width: 200px; gap: 16px; }
    }

    .stat-item.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .stat-value {
      font-size: 36px;
      font-weight: 600;
      color: #271C40;
    }

    @media (min-width: 640px) {
      .stat-value { font-size: 48px; }
    }

    @media (min-width: 768px) {
      .stat-value { font-size: 64px; line-height: 76px; }
    }

    .stat-label {
      text-align: center;
      font-size: 14px;
      font-weight: 500;
      color: rgba(39, 28, 64, 0.7);
    }

    @media (min-width: 640px) {
      .stat-label { font-size: 16px; }
    }

    @media (min-width: 768px) {
      .stat-label { font-size: 20px; }
    }

    .stat-divider {
      display: none;
      width: 1px;
      height: 80px;
      background: rgba(39, 28, 64, 0.2);
      margin: 0 32px;
    }

    @media (min-width: 768px) {
      .stat-divider { display: block; }
    }

    @media (min-width: 1024px) {
      .stat-divider { margin: 0 48px; }
    }
  </style>
</head>
<body>

  <!-- Navbar -->
  <header class="navbar">
    <nav class="navbar-pill">
      <div class="navbar-brand">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="white">
          <path d="M 228 0 C 172.772 0 128 44.772 128 100 L 128 0 L 0 0 L 0 28 C 0 83.228 44.772 128 100 128 L 0 128 L 0 256 L 28 256 C 83.228 256 128 211.228 128 156 L 128 256 L 256 256 L 256 228 C 256 172.772 211.228 128 156 128 L 256 128 L 256 0 Z" />
        </svg>
        <span>Aether Lane</span>
      </div>

      <ul class="navbar-links">
        <li><a href="#home" class="active">Home</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#estates">Estates</a></li>
        <li><a href="#projects">Projects</a></li>
        <li><a href="#inquire">Inquire</a></li>
      </ul>

      <button class="btn-cta btn-cta-nav">Get in touch</button>

      <button class="hamburger" id="hamburger" aria-label="Toggle menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </nav>
  </header>

  <!-- Mobile Menu -->
  <div class="mobile-menu" id="mobile-menu">
    <nav>
      <a href="#home">Home</a>
      <a href="#about">About</a>
      <a href="#estates">Estates</a>
      <a href="#projects">Projects</a>
      <a href="#inquire">Inquire</a>
      <button class="btn-cta">Get in touch</button>
    </nav>
  </div>

  <!-- Hero -->
  <section class="hero" id="hero">
    <div class="hero-sky" id="hero-sky">
      <img src="https://soft-zoom-63098134.figma.site/_assets/v11/7af55796a90a26e2d57c9fa2a48815874023cff0.png" alt="" />
    </div>

    <div class="hero-title-wrap">
      <h1 class="hero-title">Galaxy&nbsp;&nbsp;Home</h1>
    </div>

    <div class="hero-subtext hero-subtext-left">
      <p>Elegance Above the Skyline</p>
    </div>

    <div class="hero-subtext hero-subtext-right">
      <p>Your Dream Residence Starts Here</p>
    </div>

    <div class="hero-building" id="hero-building">
      <img src="https://soft-zoom-63098134.figma.site/_assets/v11/644aba5492aa8bd5756bc5c6d65255d577b1aaf3.png" alt="Luxury hilltop residence" />
    </div>
  </section>

  <!-- Mountain Wrapper -->
  <div class="mountain-wrapper" id="mountain-wrapper">
    <div class="mountain-bg" id="mountain-bg">
      <img src="https://soft-zoom-63098134.figma.site/_assets/v11/3d8fdaf726b804c1299840860af873a910ce1571.png" alt="" />
    </div>

    <div class="mountain-content">
      <!-- Content Section -->
      <section class="content-section">
        <div class="description-block">
          <p class="description-text">Explore distinguished estates, iconic design, and meticulously curated homes across the globe's most sought-after destinations.</p>
          <button class="btn-cta">Get in touch</button>
        </div>

        <!-- Text Fill Section -->
        <div class="text-fill-section" id="text-fill-section">
          <div class="text-fill-inner">
            <p class="text-fill-paragraph" id="text-fill-paragraph"></p>
          </div>
        </div>

        <!-- Logo Marquee -->
        <div class="marquee-section">
          <div class="marquee-row">
            <div class="marquee-track" id="marquee-row-1"></div>
          </div>
          <div class="marquee-row marquee-row-reverse">
            <div class="marquee-track" id="marquee-row-2"></div>
          </div>
        </div>
      </section>

      <!-- Stats Section -->
      <section class="stats-section">
        <div class="stats-gradient"></div>
        <div class="stats-content">
          <h2 class="stats-title">Only the proven results here</h2>
          <div class="stats-grid" id="stats-grid"></div>
        </div>
      </section>
    </div>
  </div>

  <script>
    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobile-menu');

    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open');
      document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
    });

    mobileMenu.querySelectorAll('a, .btn-cta').forEach(el => {
      el.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });

    // Parallax
    const heroSection = document.getElementById('hero');
    const heroSky = document.getElementById('hero-sky');
    const heroBuilding = document.getElementById('hero-building');
    const mountainWrapper = document.getElementById('mountain-wrapper');
    const mountainBg = document.getElementById('mountain-bg');

    function updateParallax() {
      const heroRect = heroSection.getBoundingClientRect();
      const heroProgress = Math.min(1, Math.max(0, -heroRect.top / heroRect.height));
      const heroY = heroProgress * 8;
      heroSky.style.transform = `translateY(${heroY}%)`;
      heroBuilding.style.transform = `translateY(${heroY}%)`;

      const wrapperRect = mountainWrapper.getBoundingClientRect();
      const wrapperHeight = mountainWrapper.offsetHeight;
      const scrolled = -wrapperRect.top;
      const total = wrapperHeight - window.innerHeight;
      const mountainProgress = Math.min(1, Math.max(0, scrolled / total));
      const mountainY = mountainProgress * -20;
      mountainBg.style.transform = `translateY(${mountainY}%)`;
    }

    window.addEventListener('scroll', updateParallax, { passive: true });
    updateParallax();

    // Text Fill Section
    const TEXT_FILL = 'We present refined estates that merge remarkable design, prime surroundings, and relentless craftsmanship. Each residence is chosen for the experience it delivers not merely the footprint it provides.';
    const textFillSection = document.getElementById('text-fill-section');
    const textFillParagraph = document.getElementById('text-fill-paragraph');

    const words = TEXT_FILL.split(' ');
    let html = '';
    words.forEach((word, wi) => {
      html += '<span style="display:inline-block;white-space:nowrap">';
      for (let i = 0; i < word.length; i++) {
        html += `<span class="char">${word[i]}</span>`;
      }
      html += '</span>';
      if (wi < words.length - 1) {
        html += '<span class="char">\u00A0</span>';
      }
    });
    textFillParagraph.innerHTML = html;

    const chars = textFillParagraph.querySelectorAll('.char');
    const totalChars = chars.length;

    function updateTextFill() {
      const rect = textFillSection.getBoundingClientRect();
      const start = window.innerHeight * 0.8;
      const end = window.innerHeight * 0.2;
      const progress = Math.min(1, Math.max(0, (start - rect.top) / (start - end + rect.height)));

      chars.forEach((char, i) => {
        const charProgress = i / totalChars;
        const charStart = Math.max(0, charProgress - 0.01);
        const charEnd = Math.min(1, charProgress + 0.01);
        let opacity;
        if (progress <= charStart) {
          opacity = 0.25;
        } else if (progress >= charEnd) {
          opacity = 1;
        } else {
          opacity = 0.25 + (0.75 * (progress - charStart) / (charEnd - charStart));
        }
        char.style.opacity = opacity;
      });
    }

    window.addEventListener('scroll', updateTextFill, { passive: true });
    updateTextFill();

    // Logo Marquee
    const ICONS = {
      sparkles: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
      waves: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/></svg>',
      star: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
      zap: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
      orbit: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><path d="M10.4 21.9a10 10 0 0 0 9.941-15.416"/><path d="M13.5 2.1a10 10 0 0 0-9.841 15.416"/></svg>',
      gem: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/></svg>'
    };

    const row1Data = [
      { icon: 'sparkles', name: 'Prism' },
      { icon: 'waves', name: 'Cascade' },
      { icon: 'star', name: 'Pinnacle' },
      { icon: 'sparkles', name: 'Prism' },
      { icon: 'waves', name: 'Cascade' },
      { icon: 'star', name: 'Pinnacle' },
    ];

    const row2Data = [
      { icon: 'zap', name: 'Impulse' },
      { icon: 'orbit', name: 'Nexus' },
      { icon: 'gem', name: 'Radiant' },
      { icon: 'orbit', name: 'Nexus' },
      { icon: 'gem', name: 'Radiant' },
    ];

    function buildMarqueeRow(data, containerId) {
      const container = document.getElementById(containerId);
      const doubled = [...data, ...data, ...data, ...data];
      container.innerHTML = doubled.map(item =>
        `<div class="logo-item">${ICONS[item.icon]}<span>${item.name}</span></div>`
      ).join('');
    }

    buildMarqueeRow(row1Data, 'marquee-row-1');
    buildMarqueeRow(row2Data, 'marquee-row-2');

    // Stats Section
    const stats = [
      { value: '500', label: 'Estates Delivered' },
      { value: '25', label: 'Exclusive Markets' },
      { value: '12', label: 'Years in the Field' },
      { value: '99%', label: 'Owner Satisfaction' },
    ];

    const statsGrid = document.getElementById('stats-grid');
    stats.forEach((stat, i) => {
      const wrap = document.createElement('div');
      wrap.className = 'stat-item-wrap';

      const item = document.createElement('div');
      item.className = 'stat-item';
      item.style.transitionDelay = `${i * 0.15}s`;
      item.innerHTML = `
        <span class="stat-value">${stat.value}</span>
        <span class="stat-label">${stat.label}</span>
      `;
      wrap.appendChild(item);

      if (i < stats.length - 1) {
        const divider = document.createElement('div');
        divider.className = 'stat-divider';
        wrap.appendChild(divider);
      }

      statsGrid.appendChild(wrap);
    });

    // Stats animation on scroll
    const statItems = document.querySelectorAll('.stat-item');
    const statsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          statItems.forEach(item => item.classList.add('visible'));
          statsObserver.disconnect();
        }
      });
    }, { rootMargin: '-100px' });

    statsObserver.observe(statsGrid);
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*