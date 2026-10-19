---
title: "Product Studio"
template_id: "1be37c8a-8ce0-44e6-a199-38c73f192072"
section: "sites"
category_slug: "agency"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/539ffd45-0379-4153-8091-21c67d7e7595.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Product Studio

> **Секція:** `SITES` | **Категорія:** `agency`  
> **ID шаблону:** `1be37c8a-8ce0-44e6-a199-38c73f192072`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Agency Website



### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/539ffd45-0379-4153-8091-21c67d7e7595.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a two-section dark landing page for a digital studio called "KineticForge" using **React + TypeScript + Vite + Tailwind CSS**. Use **lucide-react** for the logo icon (`Atom`). No other UI libraries.

---

### FONT SETUP

In `index.html`, load "Helvetica Now Var" via this stylesheet link in `<head>`:
```
https://db.onlinewebfonts.com/c/e66905e07608167a84e6ad52f638c3c6?family=Helvetica+Now+Var
```

In `tailwind.config.js`, extend `fontFamily.sans` to:
```js
sans: ['"Helvetica Now Var"', 'sans-serif']
```

Page title: "Kinetic Forge"

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

html, body {
  overflow-x: hidden;
}
```

---

### ARCHITECTURE: FIXED STACKED BACKGROUND VIDEOS WITH SCROLL-TRIGGERED CROSSFADE

The page has two fullscreen videos positioned `fixed inset-0 z-0`, absolutely stacked on top of each other. All page content scrolls over them in a wrapper with `relative z-10`.

**Video 1 (Hero background):**
- URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260703_152235_56f10620-8704-4c63-8ddd-f146a7085404.mp4`
- Attributes: `muted`, `playsInline`, `autoPlay`, `loop`, `preload="auto"`
- Classes: `absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-in-out`
- Starts at opacity 1

**Video 2 (Section 2 background):**
- URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260703_075205_41edc37d-b74b-4c8c-a1e2-2b7879cb4386.mp4`
- Attributes: `muted`, `playsInline`, `loop`, `preload="auto"`
- Classes: same as video 1
- Starts at opacity 0

**Crossfade Logic (IntersectionObserver):**
- Observe section 2 with `threshold: 0.15`
- When section 2 enters viewport: set video 1 opacity to 0, video 2 opacity to 1, reset video 2 `currentTime = 0` and call `.play()`
- When section 2 exits viewport: set video 1 opacity to 1, video 2 opacity to 0, call video 1 `.play()`
- Use React state `activeVideo` (1 or 2) to control inline `style={{ opacity: activeVideo === N ? 1 : 0 }}`

---

### NAVBAR (fixed, z-50)

Position: `fixed top-0 left-0 right-0 z-50`
Layout: `flex items-center justify-between px-6 py-5 md:px-10 lg:px-14`

**Left side:**
- Lucide `Atom` icon: `w-6 h-6 text-white strokeWidth={1.5}`
- Text "KineticForge": `text-white text-base font-medium tracking-tight`
- Container: `flex items-center gap-2`

**Right side (desktop, hidden on mobile):**
- `hidden md:flex items-center gap-8 text-white/80 text-sm font-light`
- Items: "our studio", "expertise", "projects", "get in touch"
- Each: `hover:text-white transition-colors cursor-pointer`

**Right side (mobile hamburger, hidden on desktop):**
- Button: `md:hidden text-white relative w-6 h-6 flex items-center justify-center z-50`
- Two `<span>` elements representing lines:
  - Each: `absolute w-5 h-[1.5px] bg-white transition-all duration-300 ease-[cubic-bezier(0.25,0.1,0.25,1)]`
  - Closed state: first line `-translate-y-[5px]`, second line `translate-y-[5px]`
  - Open state: first line `rotate-45 translate-y-0`, second line `-rotate-45 translate-y-0`

---

### MOBILE MENU OVERLAY

Container: `fixed inset-0 z-40 bg-black/95 backdrop-blur-xl flex flex-col items-center justify-center md:hidden`
Transition: `transition-all duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)]`
- Open: `opacity-100 pointer-events-auto`
- Closed: `opacity-0 pointer-events-none`

**Menu items** (same 4 nav labels):
- `text-white text-2xl font-light tracking-wide cursor-pointer hover:text-white/70`
- Stagger animation: `transition-all duration-500 ease-[cubic-bezier(0.25,0.1,0.25,1)]`
  - Open: `opacity-100 translate-y-0` with `transitionDelay: ${100 + i * 75}ms`
  - Closed: `opacity-0 translate-y-4` with `transitionDelay: '0ms'`
- Each item closes the menu on click

**Body scroll lock:** When menu is open, set `document.body.style.overflow = 'hidden'`; restore on close/unmount.

---

### SECTION 1: HERO

Container: `h-screen w-full flex flex-col items-center justify-center px-6 text-center`

**Heading:**
```
Transforming the
online interaction
since 2001
```
- Line breaks using `<br />`
- Classes: `text-white text-4xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-normal leading-[1.1] tracking-[-0.06em] max-w-5xl`

**Subheading:**
```
A Vancouver digital studio Specializing
in Web Products and Interface Design
```
- Line break between the two lines using `<br className="hidden sm:block" />` (hidden on mobile, visible on sm+)
- Classes: `mt-6 sm:mt-8 text-white/70 text-sm sm:text-lg font-light max-w-lg leading-relaxed`

---

### SECTION 2: ABOUT + CLIENTS

Container: `min-h-screen w-full` (this element gets the IntersectionObserver ref)
Inner layout: `flex flex-col lg:flex-row min-h-screen`

#### Left Column
Container: `flex-1 flex flex-col justify-between px-6 pt-24 pb-12 md:px-10 lg:px-14 lg:pt-28 lg:pb-20`

**Heading:**
```
We craft award
winning platforms
and tools
```
- Line breaks using `<br />`
- Classes: `text-white text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-normal leading-[1.1] tracking-[-0.06em] max-w-lg`

**Body text block** (below heading, `mt-10 lg:mt-0`):
- Wrapper: `max-w-sm space-y-5`
- Paragraph 1: "With studios in Vancouver, Montreal and Berlin, we design and develop full-scale digital products that generate real outcomes, cut costs, boost engagement and grow revenue."
- Paragraph 2: "For over 23 years, Kinetic Forge has partnered with organizations large and small with a roster that features some of the most recognized names worldwide. We're always eager to arrange a meeting to explore your next venture so don't hesitate to reach out for a free consultation or quote!"
- Both paragraphs: `text-white/60 text-xs sm:text-sm leading-relaxed font-light`

**Button:**
- Text: "Learn more here"
- Classes: `mt-6 sm:mt-8 border border-white/30 text-white text-xs sm:text-sm font-light px-5 sm:px-6 py-2.5 sm:py-3 rounded-sm hover:bg-white/10 transition-colors`

#### Right Column
Container: `flex-1 flex flex-col justify-end px-6 pb-12 md:px-10 lg:px-14 lg:pb-20`

**Label:** "Partners we're proud to work with"
- Classes: `text-white/60 text-xs sm:text-sm font-light mb-6 sm:mb-8`

**Client Grid:**
- Container: `grid grid-cols-2 gap-x-8 sm:gap-x-12 gap-y-8 sm:gap-y-10 max-w-md`

**6 grid items:**

1. **NASA** -- `<span>` with classes: `text-white text-xl sm:text-3xl font-bold tracking-widest`
2. **Google** -- `<span>` with classes: `text-white text-xl sm:text-3xl font-medium tracking-tight`
3. **Canadian Digital Service** -- SVG infinity-loop icon (w-6 h-6 sm:w-8 sm:h-8, fill="currentColor", white) + text "Canadian\nDigital Service" (text-[10px] sm:text-xs font-light, line break via `<br />`)
   - SVG path: `M18.6,6.62C17.16,6.62 15.8,7.18 14.83,8.15L7.8,14.39C7.16,15.03 6.31,15.38 5.4,15.38C3.53,15.38 2,13.87 2,12C2,10.13 3.53,8.62 5.4,8.62C6.31,8.62 7.16,8.97 7.84,9.65L8.97,10.65L10.5,9.31L9.22,8.2C8.2,7.18 6.84,6.62 5.4,6.62C2.42,6.62 0,9.04 0,12C0,14.96 2.42,17.38 5.4,17.38C6.84,17.38 8.2,16.82 9.17,15.85L16.2,9.61C16.84,8.97 17.69,8.62 18.6,8.62C20.47,8.62 22,10.13 22,12C22,13.87 20.47,15.38 18.6,15.38C17.69,15.38 16.84,15.03 16.16,14.35L15.03,13.34L13.5,14.68L14.78,15.8C15.8,16.82 17.16,17.38 18.6,17.38C21.58,17.38 24,14.96 24,12C24,9.04 21.58,6.62 18.6,6.62Z`
4. **United Nations** -- SVG globe icon (w-8 h-8 sm:w-10 sm:h-10, stroke="currentColor", strokeWidth="0.8", fill="none") with: circle cx=12 cy=12 r=10, ellipse cx=12 cy=12 rx=4 ry=10, three horizontal lines at y=7, y=12, y=17 (x1=4/2/4 x2=20/22/20) + text "United Nations" (text-[10px] sm:text-xs font-light)
5. **Canada** -- SVG star icon (w-5 h-5 sm:w-7 sm:h-7, fill="currentColor", white) path: `M12 2L9.5 8.5H2L8 12.5L5.5 19L12 15L18.5 19L16 12.5L22 8.5H14.5L12 2Z` + text "Canada" (text-xs sm:text-sm font-light)
6. **Department of Administration** -- `<span>` "mn" (text-base sm:text-lg font-bold) + text "Department of\nAdministration" (text-[10px] sm:text-xs font-light, line break via `<br />`)

All grid items use `flex items-center gap-2 sm:gap-3` (except NASA and Google which use `flex items-center justify-start`).

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kinetic Forge</title>
  <link href="https://db.onlinewebfonts.com/c/e66905e07608167a84e6ad52f638c3c6?family=Helvetica+Now+Var" rel="stylesheet" />
  <style>
    *, *::before, *::after {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html, body {
      overflow-x: hidden;
      font-family: "Helvetica Now Var", sans-serif;
      background: #000;
    }

    /* Fixed stacked background videos */
    .video-layer {
      position: fixed;
      inset: 0;
      z-index: 0;
    }

    .video-layer video {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.7s ease-in-out;
    }

    /* Navbar */
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 50;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.25rem 1.5rem;
    }

    @media (min-width: 768px) {
      .navbar { padding-left: 2.5rem; padding-right: 2.5rem; }
    }

    @media (min-width: 1024px) {
      .navbar { padding-left: 3.5rem; padding-right: 3.5rem; }
    }

    .navbar-brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .navbar-brand span {
      color: white;
      font-size: 1rem;
      font-weight: 500;
      letter-spacing: -0.025em;
    }

    .nav-links {
      display: none;
      align-items: center;
      gap: 2rem;
      list-style: none;
    }

    @media (min-width: 768px) {
      .nav-links { display: flex; }
    }

    .nav-links li {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.875rem;
      font-weight: 300;
      cursor: pointer;
      transition: color 0.2s;
    }

    .nav-links li:hover {
      color: white;
    }

    /* Hamburger */
    .hamburger {
      display: flex;
      position: relative;
      width: 1.5rem;
      height: 1.5rem;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      cursor: pointer;
      z-index: 50;
    }

    @media (min-width: 768px) {
      .hamburger { display: none; }
    }

    .hamburger span {
      position: absolute;
      width: 1.25rem;
      height: 1.5px;
      background: white;
      transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    .hamburger span:first-child {
      transform: translateY(-5px);
    }

    .hamburger span:last-child {
      transform: translateY(5px);
    }

    .hamburger.open span:first-child {
      transform: translateY(0) rotate(45deg);
    }

    .hamburger.open span:last-child {
      transform: translateY(0) rotate(-45deg);
    }

    /* Mobile menu overlay */
    .mobile-menu {
      position: fixed;
      inset: 0;
      z-index: 40;
      background: rgba(0, 0, 0, 0.95);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    @media (min-width: 768px) {
      .mobile-menu { display: none !important; }
    }

    .mobile-menu.open {
      opacity: 1;
      pointer-events: auto;
    }

    .mobile-menu ul {
      list-style: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2rem;
    }

    .mobile-menu li {
      color: white;
      font-size: 1.5rem;
      font-weight: 300;
      letter-spacing: 0.025em;
      cursor: pointer;
      opacity: 0;
      transform: translateY(1rem);
      transition: all 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
    }

    .mobile-menu li:hover {
      color: rgba(255, 255, 255, 0.7);
    }

    .mobile-menu.open li {
      opacity: 1;
      transform: translateY(0);
    }

    .mobile-menu.open li:nth-child(1) { transition-delay: 100ms; }
    .mobile-menu.open li:nth-child(2) { transition-delay: 175ms; }
    .mobile-menu.open li:nth-child(3) { transition-delay: 250ms; }
    .mobile-menu.open li:nth-child(4) { transition-delay: 325ms; }

    /* Scrollable content */
    .content {
      position: relative;
      z-index: 10;
    }

    /* Hero */
    .hero {
      height: 100vh;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 0 1.5rem;
      text-align: center;
    }

    .hero h1 {
      color: white;
      font-size: 2.25rem;
      font-weight: 400;
      line-height: 1.1;
      letter-spacing: -0.06em;
      max-width: 64rem;
    }

    @media (min-width: 640px) { .hero h1 { font-size: 3.75rem; } }
    @media (min-width: 768px) { .hero h1 { font-size: 4.5rem; } }
    @media (min-width: 1024px) { .hero h1 { font-size: 6rem; } }
    @media (min-width: 1280px) { .hero h1 { font-size: 8rem; } }

    .hero p {
      margin-top: 1.5rem;
      color: rgba(255, 255, 255, 0.7);
      font-size: 0.875rem;
      font-weight: 300;
      max-width: 32rem;
      line-height: 1.625;
    }

    @media (min-width: 640px) {
      .hero p { font-size: 1.125rem; margin-top: 2rem; }
    }

    .hero p .br-desktop {
      display: none;
    }

    @media (min-width: 640px) {
      .hero p .br-desktop { display: block; }
    }

    /* Section 2 */
    .section2 {
      min-height: 100vh;
      width: 100%;
    }

    .section2-inner {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    @media (min-width: 1024px) {
      .section2-inner { flex-direction: row; }
    }

    /* Left col */
    .left-col {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 6rem 1.5rem 3rem;
    }

    @media (min-width: 768px) {
      .left-col { padding-left: 2.5rem; padding-right: 2.5rem; }
    }

    @media (min-width: 1024px) {
      .left-col { padding: 7rem 3.5rem 5rem; }
    }

    .left-col h2 {
      color: white;
      font-size: 1.5rem;
      font-weight: 400;
      line-height: 1.1;
      letter-spacing: -0.06em;
      max-width: 32rem;
    }

    @media (min-width: 640px) { .left-col h2 { font-size: 1.875rem; } }
    @media (min-width: 768px) { .left-col h2 { font-size: 2.25rem; } }
    @media (min-width: 1024px) { .left-col h2 { font-size: 3rem; } }

    .left-col .body-text {
      margin-top: 2.5rem;
    }

    @media (min-width: 1024px) {
      .left-col .body-text { margin-top: 0; }
    }

    .left-col .paragraphs {
      max-width: 24rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .left-col .paragraphs p {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.75rem;
      line-height: 1.625;
      font-weight: 300;
    }

    @media (min-width: 640px) {
      .left-col .paragraphs p { font-size: 0.875rem; }
    }

    .cta-btn {
      margin-top: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
      font-size: 0.75rem;
      font-weight: 300;
      padding: 0.625rem 1.25rem;
      border-radius: 2px;
      background: transparent;
      cursor: pointer;
      transition: background 0.2s;
    }

    @media (min-width: 640px) {
      .cta-btn { font-size: 0.875rem; padding: 0.75rem 1.5rem; margin-top: 2rem; }
    }

    .cta-btn:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    /* Right col */
    .right-col {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 0 1.5rem 3rem;
    }

    @media (min-width: 768px) {
      .right-col { padding-left: 2.5rem; padding-right: 2.5rem; }
    }

    @media (min-width: 1024px) {
      .right-col { padding: 0 3.5rem 5rem; }
    }

    .right-col .label {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.75rem;
      font-weight: 300;
      margin-bottom: 1.5rem;
    }

    @media (min-width: 640px) {
      .right-col .label { font-size: 0.875rem; margin-bottom: 2rem; }
    }

    .client-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      column-gap: 2rem;
      row-gap: 2rem;
      max-width: 28rem;
    }

    @media (min-width: 640px) {
      .client-grid { column-gap: 3rem; row-gap: 2.5rem; }
    }

    .client-grid .client {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    @media (min-width: 640px) {
      .client-grid .client { gap: 0.75rem; }
    }

    .client-grid .nasa {
      color: white;
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.1em;
    }

    @media (min-width: 640px) { .client-grid .nasa { font-size: 1.875rem; } }

    .client-grid .google {
      color: white;
      font-size: 1.25rem;
      font-weight: 500;
      letter-spacing: -0.025em;
    }

    @media (min-width: 640px) { .client-grid .google { font-size: 1.875rem; } }

    .client-grid .client-text {
      color: white;
      font-size: 10px;
      font-weight: 300;
      line-height: 1.4;
    }

    @media (min-width: 640px) { .client-grid .client-text { font-size: 0.75rem; } }

    .client-grid .canada-text {
      color: white;
      font-size: 0.75rem;
      font-weight: 300;
    }

    @media (min-width: 640px) { .client-grid .canada-text { font-size: 0.875rem; } }

    .client-grid .mn-logo {
      color: white;
      font-size: 1rem;
      font-weight: 700;
      flex-shrink: 0;
    }

    @media (min-width: 640px) { .client-grid .mn-logo { font-size: 1.125rem; } }

    .client-grid svg {
      flex-shrink: 0;
    }
  </style>
</head>
<body>

  <!-- Fixed stacked background videos -->
  <div class="video-layer">
    <video id="video1" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260703_152235_56f10620-8704-4c63-8ddd-f146a7085404.mp4" muted playsinline autoplay loop preload="auto" style="opacity: 1;"></video>
    <video id="video2" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260703_075205_41edc37d-b74b-4c8c-a1e2-2b7879cb4386.mp4" muted playsinline loop preload="auto" style="opacity: 0;"></video>
  </div>

  <!-- Navbar -->
  <nav class="navbar">
    <div class="navbar-brand">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9-4.54-4.52-9.87-6.54-11.9-4.5-2.04 2.03-.02 7.36 4.5 11.9 4.54 4.52 9.87 6.54 11.9 4.5Z"/><path d="M15.7 15.7c4.52-4.54 6.54-9.87 4.5-11.9-2.03-2.04-7.36-.02-11.9 4.5-4.52 4.54-6.54 9.87-4.5 11.9 2.03 2.04 7.36.02 11.9-4.5Z"/></svg>
      <span>KineticForge</span>
    </div>

    <ul class="nav-links">
      <li>our studio</li>
      <li>expertise</li>
      <li>projects</li>
      <li>get in touch</li>
    </ul>

    <button class="hamburger" id="hamburgerBtn" aria-label="Menu">
      <span></span>
      <span></span>
    </button>
  </nav>

  <!-- Mobile Menu Overlay -->
  <div class="mobile-menu" id="mobileMenu">
    <ul>
      <li>our studio</li>
      <li>expertise</li>
      <li>projects</li>
      <li>get in touch</li>
    </ul>
  </div>

  <!-- Scrollable content -->
  <div class="content">

    <!-- Hero Section -->
    <section class="hero">
      <h1>
        Transforming the<br />
        online interaction<br />
        since 2001
      </h1>
      <p>
        A Vancouver digital studio Specializing<br class="br-desktop" />
        in Web Products and Interface Design
      </p>
    </section>

    <!-- Section 2 - About + Clients -->
    <section class="section2" id="section2">
      <div class="section2-inner">

        <!-- Left Column -->
        <div class="left-col">
          <h2>
            We craft award<br />
            winning platforms<br />
            and tools
          </h2>

          <div class="body-text">
            <div class="paragraphs">
              <p>With studios in Vancouver, Montreal and Berlin, we design and develop full-scale digital products that generate real outcomes, cut costs, boost engagement and grow revenue.</p>
              <p>For over 23 years, Kinetic Forge has partnered with organizations large and small with a roster that features some of the most recognized names worldwide. We're always eager to arrange a meeting to explore your next venture so don't hesitate to reach out for a free consultation or quote!</p>
            </div>
            <button class="cta-btn">Learn more here</button>
          </div>
        </div>

        <!-- Right Column - Clients -->
        <div class="right-col">
          <p class="label">Partners we're proud to work with</p>

          <div class="client-grid">
            <!-- NASA -->
            <div class="client">
              <span class="nasa">NASA</span>
            </div>

            <!-- Google -->
            <div class="client">
              <span class="google">Google</span>
            </div>

            <!-- Canadian Digital Service -->
            <div class="client">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="white" class="cds-icon"><path d="M18.6,6.62C17.16,6.62 15.8,7.18 14.83,8.15L7.8,14.39C7.16,15.03 6.31,15.38 5.4,15.38C3.53,15.38 2,13.87 2,12C2,10.13 3.53,8.62 5.4,8.62C6.31,8.62 7.16,8.97 7.84,9.65L8.97,10.65L10.5,9.31L9.22,8.2C8.2,7.18 6.84,6.62 5.4,6.62C2.42,6.62 0,9.04 0,12C0,14.96 2.42,17.38 5.4,17.38C6.84,17.38 8.2,16.82 9.17,15.85L16.2,9.61C16.84,8.97 17.69,8.62 18.6,8.62C20.47,8.62 22,10.13 22,12C22,13.87 20.47,15.38 18.6,15.38C17.69,15.38 16.84,15.03 16.16,14.35L15.03,13.34L13.5,14.68L14.78,15.8C15.8,16.82 17.16,17.38 18.6,17.38C21.58,17.38 24,14.96 24,12C24,9.04 21.58,6.62 18.6,6.62Z"/></svg>
              <span class="client-text">Canadian<br />Digital Service</span>
            </div>

            <!-- United Nations -->
            <div class="client">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="0.8"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="17" x2="20" y2="17"/></svg>
              <span class="client-text">United Nations</span>
            </div>

            <!-- Canada -->
            <div class="client">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M12 2L9.5 8.5H2L8 12.5L5.5 19L12 15L18.5 19L16 12.5L22 8.5H14.5L12 2Z"/></svg>
              <span class="canada-text">Canada</span>
            </div>

            <!-- Department of Administration -->
            <div class="client">
              <span class="mn-logo">mn</span>
              <span class="client-text">Department of<br />Administration</span>
            </div>
          </div>
        </div>

      </div>
    </section>

  </div>

  <script>
    // Hamburger menu toggle
    const hamburger = document.getElementById('hamburgerBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    let menuOpen = false;

    hamburger.addEventListener('click', () => {
      menuOpen = !menuOpen;
      hamburger.classList.toggle('open', menuOpen);
      mobileMenu.classList.toggle('open', menuOpen);
      document.body.style.overflow = menuOpen ? 'hidden' : '';
    });

    mobileMenu.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        menuOpen = false;
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        document.body.style.overflow = '';
      });
    });

    // Video crossfade on scroll using IntersectionObserver
    const video1 = document.getElementById('video1');
    const video2 = document.getElementById('video2');
    const section2 = document.getElementById('section2');

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            video1.style.opacity = '0';
            video2.style.opacity = '1';
            video2.currentTime = 0;
            video2.play();
          } else {
            video1.style.opacity = '1';
            video2.style.opacity = '0';
            video1.play();
          }
        });
      },
      { threshold: 0.15 }
    );

    observer.observe(section2);
  </script>

</body>
</html>
```

---
*NeuroFlow Academy Site Templates*