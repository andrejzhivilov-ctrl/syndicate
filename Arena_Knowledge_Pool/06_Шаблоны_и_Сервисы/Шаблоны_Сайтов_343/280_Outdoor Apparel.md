---
title: "Outdoor Apparel"
template_id: "85014503-9d71-489e-8408-cfb2bfa9208f"
section: "sites"
category_slug: "ecommerce"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/7125e99b-25b2-4d63-8110-3726d409dae9.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Outdoor Apparel

> **Секція:** `SITES` | **Категорія:** `ecommerce`  
> **ID шаблону:** `85014503-9d71-489e-8408-cfb2bfa9208f`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Fashion

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/7125e99b-25b2-4d63-8110-3726d409dae9.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Build a single-page landing website for a fictional outdoor technical gear brand called **ALP1NE** (stylized as `ALP1NE™`). It should be a vanilla HTML/CSS/JS page served by Vite (no React, no frameworks). The entire site lives in one `index.html` file with inline `<style>` and `<script>` tags. Use the font **Inter Tight weight 600 only** from Google Fonts.

---

### GLOBAL SETUP

- Title: `ALP1NE™`
- Font: `Inter Tight`, weight 600 only. Load via: `https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600&display=swap`
- Add `<link rel="preconnect">` for: `fonts.googleapis.com`, `fonts.gstatic.com` (crossorigin), `i.ibb.co` (crossorigin), `d8j0ntlcm91z4.cloudfront.net` (crossorigin)
- CSS reset: `* { box-sizing: border-box; margin: 0; padding: 0; }`
- `html`: `overscroll-behavior: none; overflow-x: hidden;`
- `body`: `background-color: transparent; font-family: "Inter Tight", sans-serif; font-weight: 600; min-height: 100vh; overflow-x: hidden;`

---

### SECTION 1: FIXED BACKGROUND VIDEO (Hero)

A full-viewport fixed video that scrubs forward/backward based on scroll position (not autoplaying normally).

- Container (`#background-wrapper`): `position: fixed; top: 0; left: 0; width: 100%; height: 100vh; z-index: 1; overflow: hidden;`
- Video element (`#bg-video`, class `bg-video`): `width: 100%; height: 100%; object-fit: cover; display: block;`
- Video attributes: `playsinline webkit-playsinline autoplay muted preload="auto" referrerpolicy="no-referrer"`
- **Video URL**: `https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260706_124521_30407ad9-28f0-481c-9d64-641c619e47e0.mp4`
- The video is "primed" on load for iOS Safari compatibility (muted play then immediate pause to unlock frame-accurate seeking).
- Scroll-to-video mapping: The hero spacer is 250vh tall. As the user scrolls from 0 to that height, `video.currentTime` is lerped from 0 to `video.duration` using `requestAnimationFrame` with smoothing factor 0.12.

---

### SECTION 2: FIXED HEADER (Navigation Bar)

A fixed header at the very top (`z-index: 100`) with three groups: left, center, right.

- Container (`#header-container`): `position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 12px 14px 0; background: transparent;`

**Cell/Pill base style** (class `.cell`):
- `background-color: #ffffff` (solid white, NOT translucent, for header cells)
- `backdrop-filter: none`
- `color: #000000`
- `font-family: "Inter Tight", sans-serif; font-weight: 600; font-size: 18px; letter-spacing: 0.01em;`
- `padding: 10px 14px; border-radius: 3px; white-space: nowrap; display: inline-flex; align-items: center; justify-content: center;`

**Left group** (`#header-left`): `display: flex; gap: 6px; align-items: center;`
- Cell 1: `ALP1NE™` (id: `cell-brand`)
- Cell 2: Live clock (id: `clock-text`) showing `HH:MM:SS (PST) Weekday Month D YYYY` format, updated every second via `setInterval`. Uses browser local time.

**Center group** (`#header-center`): `display: flex; gap: 6px; align-items: center;`
- Cell: `Collection` (class `center-cell`, `min-width: 140px`)
- Cell: `Journal` (class `center-cell`)
- Cell: `About` (class `center-cell`)

**Right group** (`#header-right`): `display: flex; gap: 6px; align-items: center;`
- Cell: `Instagram`
- Cell: `Press`
- Cell: `Menu` (id: `menu-toggle-btn`, hidden on desktop via `display: none !important`, shown on tablet/mobile)

---

### SECTION 3: MOBILE/TABLET MENU OVERLAY

At `<=1024px` viewport: hide clock, center nav, Instagram, and Press from the header. Show only `ALP1NE™` and `Menu` button. The `Menu` button toggles a fullscreen overlay.

- Overlay (`#mobile-menu-overlay`): `position: fixed; inset: 0; z-index: 99;`
- Inactive state: `opacity: 0; pointer-events: none; background: rgba(0,0,0,0); backdrop-filter: blur(0px);`
- Active state (class `.active`): `opacity: 1; pointer-events: auto; background: rgba(0,0,0,0.08); backdrop-filter: blur(25px);`
- Transition: `opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1)` + matching for background-color and backdrop-filter.
- Content (`.mobile-menu-content`): centered column with `gap: 14px`.
- Each `.cell` inside starts at `opacity: 0; transform: translateY(20px) scale(0.96);` and animates to `opacity: 1; transform: translateY(0) scale(1);` with staggered delays (0.04s increments per child).
- Items: Clock (non-interactive), Collection, Journal, About, Instagram, Press.
- Clicking `Menu` toggles `.active` class and changes button text to `Close`. Clicking any menu item also closes.
- At `<=1024px`, brand cell and menu toggle shrink to `font-size: 16px; padding: 10px 14px;`

---

### SECTION 4: BOTTOM TITLE (Fixed Overlay Text)

A fixed text element at the bottom of the viewport that animates on scroll.

- Container (`#bottom-title-container`): `position: fixed; bottom: 12px; left: 14px; right: 14px; z-index: 19; pointer-events: none; display: flex; justify-content: center; align-items: flex-end; mix-blend-mode: difference;`
- Text (h1, class `bottom-title-text`): `font-size: 80px; font-weight: 600; line-height: 1.0; letter-spacing: -0.015em; text-transform: uppercase; color: #ffffff; mix-blend-mode: difference; text-align: center;`
- Content: `We work in weathered nylon, laminated layers, and raw shell.`
- Responsive: 60px at <=1200px, 40px at <=768px, 28px at <=480px.
- **Scroll animation**: As the user scrolls through the hero (0% to 85% of hero spacer height), the title:
  - Translates up by 150px
  - Scales down from 1.0 to 0.8
  - Fades out (opacity 1 to 0, starting at 30% progress)
  - Blurs up to 24px
  - All smoothed with lerp factor 0.12 per frame.

---

### SECTION 5: SCROLLABLE CONTENT — HERO SPACER

- A transparent div (class `hero-spacer`): `height: 250vh; pointer-events: none;`
- This creates the scroll distance that drives the video scrub and title animation. The first viewport of the page shows the fixed video + bottom title; scrolling through this spacer plays the video forward.

---

### SECTION 6: OLIVE/KHAKI TEXT BLOCK WITH PARALLAX GEAR COLLAGE

After the hero spacer, a section with dark olive background, large white text (with `mix-blend-mode: difference`), and scattered product cutout images that parallax on scroll.

**Section container** (class `yellow-text-section`):
- `background-color: #575234; width: 100%; padding: 224px 24px; display: flex; justify-content: center; align-items: center; position: relative; z-index: 20;`
- CSS variable `--pscale: 1` (scales down at breakpoints: 0.72 at <=1200px, 0.5 at <=768px, 0.4 at <=480px)

**Text block** (`.text-block-container`):
- `max-width: 1406px; width: 100%; margin: 0 auto; color: #ffffff; mix-blend-mode: difference; display: flex; flex-direction: column; gap: 32px; position: relative; z-index: 10;`
- Each `<p>`: `font-size: 70px; line-height: 1.05; letter-spacing: -0.03em; text-indent: 140px; text-align: left;`
- Responsive: 54px/100px indent at <=1200px, 34px/60px at <=768px, 24px/40px at <=480px.

**Text content** (5 paragraphs with decorative Unicode symbols inline):
1. `We build gear ⟡ for people who see the outdoors ≠ as more than scenery ∴ they see it as a challenge.`
2. `Every jacket ⊹ every layer ⊹ every detail is engineered ∿ to perform in the harshest conditions ⟶ so you can stay focused on the journey.`
3. `We believe true performance ⟡ isn't measured by appearance ∴ but by how your gear responds to rain ∧ snow ∧ relentless wind ∧ high-altitude environments.`
4. `Whether you're heading into a multi-day expedition ↟ climbing a summit ◇ or hiking before sunrise ⊹ our equipment is built to help you move with confidence.`
5. `Because the moments that matter most begin where comfort ends ✦ adventure begins.`

**Parallax gear images** — Scattered product cutout PNGs in two layers:

BACK LAYER (`.parallax-layer.back`, `z-index: 5` — behind text):
- Jacket: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/jacket.fca57bc0.png` | class `item-jacket` | position: `top: 2%; left: 7%` | width: `calc(640px * var(--pscale))` | data-speed="0.14" data-drift="-0.22" data-rot="-0.6"
- Gaiters: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/gaiters.aa2524de.png` | class `item-gaiters` | position: `top: 58%; left: 74%` | width: `calc(346px * var(--pscale))` | data-speed="0.42" data-drift="0.26" data-rot="-1.0"

FRONT LAYER (`.parallax-layer.front`, `z-index: 11` — in front of text):
- Shorts: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/shorts.1a032e36.png` | class `item-shorts` | position: `top: 9%; left: 66%` | width: `calc(326px * var(--pscale))` | data-speed="0.44" data-drift="0.28" data-rot="0.9"
- Cap: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/cap.b10e4e2c.png` | class `item-cap` | position: `top: 33%; left: 7%` | width: `calc(310px * var(--pscale))` | data-speed="0.46" data-drift="-0.30" data-rot="1.4"
- Scarf: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/scarf.427effaf.png` | class `item-scarf` | position: `top: 28%; left: 64%` | width: `calc(467px * var(--pscale))` | data-speed="0.30" data-drift="0.24" data-rot="-1.2"
- Backpack: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/backpack.0558dccb.png` | class `item-backpack` | position: `top: 50%; left: 37%` | width: `calc(596px * var(--pscale))` | data-speed="0.18" data-drift="0.16" data-rot="0.5"
- Boot: `https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/boot.545d53aa.png` | class `item-boot` | position: `top: 72%; left: 13%` | width: `calc(224px * var(--pscale))` | data-speed="0.60" data-drift="-0.30" data-rot="1.8"

**Parallax animation logic**:
- Each item has `data-speed`, `data-drift`, and `data-rot` attributes.
- On each animation frame, calculate how far the viewport center is from the section center, normalize to a -1.2..1.2 range, smooth with lerp 0.12.
- Vertical offset: `-smoothP * speed * 520px`
- Horizontal offset: `smoothP * speed * drift * 520px`
- Rotation: `smoothP * rot * 4deg`
- Applied via `transform: translate3d(x, y, 0) rotate(r)`

---

### SECTION 7: LOOP SCROLL SPACER

- A div (`#loop-scroll-spacer`): `height: 3400px; width: 100%; background-color: #575234; position: relative; z-index: 20;`
- This olive-colored spacer provides scroll distance that drives the product slider reveal animation below.

---

### SECTION 8: PRODUCT SLIDER (Scroll-Driven Clip-Path Reveal)

A fixed overlay that reveals through an expanding clip-path window as the user scrolls through the loop-scroll-spacer, then swipes horizontally between full-screen product cards.

**Overlay** (`#product-slider-overlay`): `position: fixed; inset: 0; z-index: 30; display: flex; clip-path: inset(50% 50% 50% 50%);`

**Reveal animation**:
- Calculated from the bottom of the page: `REVEAL_PX = 700` scroll pixels for the window to open, then `CARD_PX = 900 * (NUM_CARDS - 1)` scroll pixels for card transitions.
- The clip-path animates from `inset(50% 50% 50% 50%)` (invisible) to `inset(0px 0px round 3px)` (full viewport) using `easeInOutCubic` easing, smoothed with lerp 0.15.

**Card track** (`#product-slider-track`): `display: flex; height: 100%; will-change: transform;`

**Product cards** (4 cards, each `100vw x 100vh`, `flex-shrink: 0`):

1. Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111701_92784626-1c2b-4db6-afd7-dd456e7a4717.png&w=1920&q=85` | Label: `Shell Jacket ↟` | Price: `$1,200`
2. Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111730_62a35ec8-335d-4bea-9337-780589328a03.png&w=1920&q=85` | Label: `Arc Layer ◇` | Price: `$890`
3. Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111749_b8ced0e0-177c-4cca-9d14-b3fdd7bedf27.png&w=1920&q=85` | Label: `Field Cap ⊹` | Price: `$180`
4. Image: `https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111837_c28c966d-4a92-408f-8ac3-0c9bac445704.png&w=1920&q=85` | Label: `Summit Haul 40 ↟` | Price: `$540`

**Card image styling**: `width: 140%; height: 100%; object-fit: cover; margin-left: -20%;` with horizontal parallax (18% shift factor) as cards scroll.

**Card info overlay**: positioned `bottom: 32px; left: 32px;` as a flex row with gap 8px. Each info cell is solid white, `font-size: 18px; padding: 13px; letter-spacing: -0.03em;`

**Center symbol** (`#slider-symbol`): `position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 600px; color: #ffffff; mix-blend-mode: difference; z-index: 51; transition: opacity 0.2s ease;`
- Randomly swaps between these Unicode symbols on each card transition: `◇ ≠ ↟ ✦ ⊹ ∧ ⟡ ∴ ⟶ ∿`
- Swap animation: fade out opacity to 0, wait 150ms, change character, fade back to 1.
- At <=768px: `font-size: 200px`

---

### ANIMATION ARCHITECTURE (requestAnimationFrame loop)

One single `requestAnimationFrame` loop (`animate()`) drives everything:

1. **Video scrub**: Maps scroll position (0 to hero spacer height) to video currentTime (0 to duration). Smoothed with lerp 0.12. Rate-limited to seek no more than every 30ms.
2. **Title animation**: Maps scroll fraction (0-0.85) to translateY (-150px), scale (1.0 to 0.8), opacity (fade starting at 30%), and blur (up to 24px). Also fades with the slider reveal.
3. **Parallax gear items**: Activates when viewport is near the olive section. Normalized distance drives per-item transforms.
4. **Slider reveal**: Last portion of scroll (bottom REVEAL_PX + CARD_PX of total page) drives clip-path expansion with easeInOutCubic.
5. **Card swipe**: After reveal completes, remaining scroll drives horizontal translateX on the track.
6. **Card image parallax**: Each card image shifts horizontally based on its distance from the current position.
7. **Symbol swap**: Fires when the rounded card index changes.

All values use lerp smoothing (factors 0.12-0.15) for buttery 60fps animation without any libraries.

---

### iOS / MOBILE COMPATIBILITY

- Video is primed via `play().then(pause())` pattern on load and on first touch/click events.
- All `-webkit-` prefixes included for clip-path and backdrop-filter.
- `playsinline` and `webkit-playsinline` attributes on video.
- Touch events registered as `{ passive: true }`.

SOURCE CODE:
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ALP1NE™</title>

    <!-- Preconnect to asset hosts so font/image/video sockets open early -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="preconnect" href="https://images.higgs.ai" crossorigin />
    <link rel="preconnect" href="https://order-twine-70493179.figma.site" crossorigin />
    <link rel="preconnect" href="https://d8j0ntlcm91z4.cloudfront.net" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600&display=swap" />

    <style>
      /* Reset and base styles */
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      html {
        overscroll-behavior: none;
        overflow-x: hidden;
      }
      
      body {
        background-color: transparent;
        font-family: "Inter Tight", sans-serif;
        font-weight: 600;
        min-height: 100vh;
        overflow-x: hidden;
      }

      /* Background wrapper fixed at the bottom layer */
      #background-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        z-index: 1;
        overflow: hidden;
      }

      .bg-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
      }

      /* Header container */
      #header-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 14px 0;
        background: transparent;
      }

      /* Groups */
      #header-left,
      #header-center,
      #header-right {
        display: flex;
        gap: 6px;
        align-items: center;
      }

      /* Cell/Pill base styles */
      .cell {
        background-color: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        color: #000000;
        font-family: "Inter Tight", sans-serif;
        font-weight: 600;
        font-size: 18px;
        letter-spacing: 0.01em;
        padding: 10px 14px;
        border-radius: 3px;
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }

      /* Center cells: "Work", "Index", "Information" — each a fixed width (~140px, scale to fit label + padding) */
      .center-cell {
        min-width: 140px;
      }

      /* Fully opaque solid white and blur-free cells for headers and mobile overlay menu */
      #header-container .cell,
      .mobile-menu-content .cell {
        background-color: #ffffff !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
      }

      /* Bottom Title Container and Text styling */
      #bottom-title-container {
        position: fixed;
        bottom: 12px;
        left: 14px;
        right: 14px;
        z-index: 19;
        pointer-events: none;
        display: flex;
        justify-content: center;
        align-items: flex-end;
        mix-blend-mode: difference;
      }

      .bottom-title-text {
        font-family: "Inter Tight", sans-serif;
        font-size: 80px;
        font-weight: 600;
        line-height: 1.0; /* 100% line height */
        letter-spacing: -0.015em;
        text-transform: uppercase;
        color: #ffffff;
        mix-blend-mode: difference;
        width: 100%;
        margin: 0;
        padding: 0;
        text-align: center;
      }

      @media (max-width: 1200px) {
        .bottom-title-text {
          font-size: 60px;
        }
      }
      @media (max-width: 768px) {
        .bottom-title-text {
          font-size: 40px;
        }
      }
      @media (max-width: 480px) {
        .bottom-title-text {
          font-size: 28px;
        }
      }

      /* Scrollable content area and Yellow text section styling */
      #scrollable-content {
        position: relative;
        z-index: 20;
        width: 100%;
      }

      .hero-spacer {
        height: 250vh;
        pointer-events: none;
      }

      .yellow-text-section {
        background-color: #575234;
        width: 100%;
        padding: 224px 24px;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        z-index: 20;
      }

      .text-block-container {
        max-width: 1406px;
        width: 100%;
        margin: 0 auto;
        color: #ffffff;
        mix-blend-mode: difference;
        display: flex;
        flex-direction: column;
        gap: 32px;
        position: relative;
        z-index: 10;
      }

      .text-block-container p {
        font-family: "Inter Tight", sans-serif;
        font-weight: 600;
        font-size: 70px;
        line-height: 1.05;
        letter-spacing: -0.03em;
        text-indent: 140px;
        margin: 0;
        text-align: left;
      }

      /* Scattered gear items — parallax collage over the olive section */
      .parallax-layer {
        position: absolute;
        inset: 0;
        pointer-events: none;
        overflow: hidden;
      }
      .parallax-layer.back { z-index: 5; }
      .parallax-layer.front { z-index: 11; }

      /* --pscale: 1 = images at their exact original pixel size (desktop);
         lowered at breakpoints so the whole collage shrinks proportionally. */
      .yellow-text-section { --pscale: 1; }

      .parallax-item {
        position: absolute;
        height: auto;
        will-change: transform;
        user-select: none;
        -webkit-user-select: none;
        -webkit-user-drag: none;
        transform: translate3d(0, 0, 0);
      }

      /* Base placement — top/left in %, width = ORIGINAL px (× --pscale).
         Layout/order/layering mirror the reference screenshot; sizes are the source files' own. */
      .item-jacket   { top: 2%;  left: 7%;   width: calc(640px * var(--pscale)); }  /* куртка  — behind */
      .item-shorts   { top: 9%;  left: 66%;  width: calc(326px * var(--pscale)); }  /* шорты   — behind */
      .item-cap      { top: 33%; left: 7%;   width: calc(310px * var(--pscale)); }  /* кепка+очки — behind */
      .item-scarf    { top: 28%; left: 64%;  width: calc(467px * var(--pscale)); }  /* шарф/баф — behind */
      .item-backpack { top: 50%; left: 37%;  width: calc(596px * var(--pscale)); }  /* рюкзак  — front */
      .item-gaiters  { top: 58%; left: 74%;  width: calc(346px * var(--pscale)); }  /* защита ног — front */
      .item-boot     { top: 72%; left: 13%;  width: calc(224px * var(--pscale)); }  /* ботинок — front */

      /* Loop Scrolling Styles */
      #loop-scroll-spacer {
        height: 3400px;
        width: 100%;
        background-color: #575234;
        position: relative;
        z-index: 20;
      }

      /* Product Slider — fixed layer revealed through a growing clip window */
      #product-slider-overlay {
        position: fixed;
        inset: 0;
        z-index: 30;
        display: flex;
        clip-path: inset(50% 50% 50% 50%);
        -webkit-clip-path: inset(50% 50% 50% 50%);
        will-change: clip-path;
      }

      #product-slider {
        width: 100%;
        height: 100%;
        overflow: hidden;
      }

      #product-slider-track {
        display: flex;
        height: 100%;
        will-change: transform;
      }

      .product-card {
        width: 100vw;
        height: 100vh;
        flex-shrink: 0;
        position: relative;
        overflow: hidden;
      }

      .card-image {
        width: 140%;
        height: 100%;
        object-fit: cover;
        display: block;
        margin-left: -20%;
        will-change: transform;
      }

      .card-info {
        position: absolute;
        bottom: 32px;
        left: 32px;
        display: flex;
        flex-direction: row;
        gap: 8px;
        align-items: center;
      }

      #product-slider-overlay .cell {
        background-color: #ffffff !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        font-size: 18px !important;
        padding: 13px !important;
        letter-spacing: -0.03em;
      }

      #slider-symbol {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: "Inter Tight", sans-serif;
        font-weight: 600;
        font-size: 600px;
        line-height: 1;
        color: #ffffff;
        mix-blend-mode: difference;
        pointer-events: none;
        user-select: none;
        -webkit-user-select: none;
        z-index: 51;
        transition: opacity 0.2s ease;
      }

      @media (max-width: 768px) {
        #slider-symbol { font-size: 200px; }
      }

      /* Mobile and Tablet Menu Overlay & Styling */
      #menu-toggle-btn {
        display: none !important;
      }

      #mobile-menu-overlay {
        position: fixed;
        inset: 0;
        z-index: 99;
        background: rgba(0, 0, 0, 0);
        backdrop-filter: blur(0px);
        -webkit-backdrop-filter: blur(0px);
        pointer-events: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                    background-color 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                    backdrop-filter 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                    -webkit-backdrop-filter 0.4s cubic-bezier(0.16, 1, 0.3, 1);
      }

      #mobile-menu-overlay.active {
        opacity: 1;
        pointer-events: auto;
        background: rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
      }

      .mobile-menu-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 14px;
        width: auto;
        max-width: 90%;
        text-align: center;
      }

      .mobile-menu-content .cell {
        cursor: pointer;
        user-select: none;
        opacity: 0;
        transform: translateY(20px) scale(0.96);
        transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1),
                    transform 0.45s cubic-bezier(0.16, 1, 0.3, 1),
                    background-color 0.2s ease;
      }

      #mobile-menu-overlay.active .mobile-menu-content .cell {
        opacity: 1;
        transform: translateY(0) scale(1);
      }

      /* Stagger delays for beautiful sequential entering animations */
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(1) { transition-delay: 0.04s; }
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(2) { transition-delay: 0.08s; }
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(3) { transition-delay: 0.12s; }
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(4) { transition-delay: 0.16s; }
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(5) { transition-delay: 0.20s; }
      #mobile-menu-overlay.active .mobile-menu-content .cell:nth-child(6) { transition-delay: 0.24s; }

      .mobile-menu-content .cell:active {
        transform: scale(0.97);
        background-color: rgba(255, 255, 255, 0.8);
      }

      @media (max-width: 1024px) {
        #clock-text,
        #header-center,
        #cell-instagram,
        #cell-email {
          display: none !important;
        }

        #menu-toggle-btn {
          display: inline-flex !important;
          cursor: pointer;
          user-select: none;
        }

        #header-right {
          gap: 6px;
        }

        /* Identical sizing, styling, and fit-content width for Logo, Menu Toggle and all Mobile Menu Items */
        #cell-brand,
        #menu-toggle-btn,
        .mobile-menu-content .cell {
          font-size: 16px !important;
          padding: 10px 14px !important;
          min-width: unset !important;
          width: fit-content !important;
          box-sizing: border-box !important;
          white-space: nowrap !important;
          border-radius: 3px !important;
          line-height: normal !important;
          height: auto !important;
        }
      }

      @media (max-width: 1200px) {
        .yellow-text-section {
          padding: 160px 20px;
          --pscale: 0.72;
        }
        .text-block-container p {
          font-size: 54px;
          text-indent: 100px;
          letter-spacing: -0.025em;
        }
      }

      @media (max-width: 768px) {
        .yellow-text-section {
          padding: 120px 16px;
          --pscale: 0.5;
        }
        .text-block-container p {
          font-size: 34px;
          text-indent: 60px;
          letter-spacing: -0.02em;
        }
      }

      @media (max-width: 480px) {
        .yellow-text-section {
          padding: 80px 12px;
          --pscale: 0.4;
        }
        .text-block-container p {
          font-size: 24px;
          text-indent: 40px;
          letter-spacing: -0.015em;
        }
      }
    </style>
  </head>
  <body>
    <header id="header-container">
      <!-- LEFT GROUP -->
      <div id="header-left">
        <div id="cell-brand" class="cell">ALP1NE™</div>
        <div id="clock-text" class="cell">--:--:-- (PST) ------- ---- - ----</div>
      </div>

      <!-- CENTER GROUP -->
      <div id="header-center">
        <div id="cell-work" class="cell center-cell">Collection</div>
        <div id="cell-index" class="cell center-cell">Journal</div>
        <div id="cell-info" class="cell center-cell">About</div>
      </div>

      <!-- RIGHT GROUP -->
      <div id="header-right">
        <div id="cell-instagram" class="cell">Instagram</div>
        <div id="cell-email" class="cell">Press</div>
        <div id="menu-toggle-btn" class="cell">Menu</div>
      </div>
    </header>

    <!-- MOBILE/TABLET OVERLAY MENU -->
    <div id="mobile-menu-overlay">
      <div class="mobile-menu-content">
        <div id="mobile-clock-text" class="cell" style="pointer-events: none;">--:--:-- (PST) ------- ---- - ----</div>
        <div id="mobile-cell-work" class="cell center-cell">Collection</div>
        <div id="mobile-cell-index" class="cell center-cell">Journal</div>
        <div id="mobile-cell-info" class="cell center-cell">About</div>
        <div id="mobile-cell-instagram" class="cell">Instagram</div>
        <div id="mobile-cell-email" class="cell">Press</div>
      </div>
    </div>

    <!-- BACKGROUND VIDEO -->
    <div id="background-wrapper">
      <video id="bg-video" class="bg-video" src="https://d8j0ntlcm91z4.cloudfront.net/user_39ca84eAE1ODL9hbR5VhoEj8tBf/hf_20260706_124521_30407ad9-28f0-481c-9d64-641c619e47e0.mp4" playsinline webkit-playsinline autoplay muted preload="auto" referrerpolicy="no-referrer"></video>
    </div>

    <!-- BOTTOM TITLE -->
    <div id="bottom-title-container">
      <h1 class="bottom-title-text">We work in weathered nylon, laminated layers, and raw shell.</h1>
    </div>

    <!-- PRODUCT SLIDER OVERLAY -->
    <div id="product-slider-overlay">
      <div id="product-slider">
        <div id="product-slider-track">
          <div class="product-card">
            <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111701_92784626-1c2b-4db6-afd7-dd456e7a4717.png&w=1920&q=85" class="card-image" decoding="async" />
            <div class="card-info">
              <div class="cell">Shell Jacket ↟</div>
              <div class="cell">$1,200</div>
            </div>
          </div>
          <div class="product-card">
            <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111730_62a35ec8-335d-4bea-9337-780589328a03.png&w=1920&q=85" class="card-image" decoding="async" />
            <div class="card-info">
              <div class="cell">Arc Layer ◇</div>
              <div class="cell">$890</div>
            </div>
          </div>
          <div class="product-card">
            <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111749_b8ced0e0-177c-4cca-9d14-b3fdd7bedf27.png&w=1920&q=85" class="card-image" decoding="async" />
            <div class="card-info">
              <div class="cell">Field Cap ⊹</div>
              <div class="cell">$180</div>
            </div>
          </div>
          <div class="product-card">
            <img src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260707_111837_c28c966d-4a92-408f-8ac3-0c9bac445704.png&w=1920&q=85" class="card-image" decoding="async" />
            <div class="card-info">
              <div class="cell">Summit Haul 40 ↟</div>
              <div class="cell">$540</div>
            </div>
          </div>
        </div>
      </div>
      <div id="slider-symbol">◇</div>
    </div>

    <!-- SCROLLABLE CONTENT AREA -->
    <div id="scrollable-content">
      <!-- HERO SPACER: Keeps the first screen clear for the fixed video and bottom title -->
      <div class="hero-spacer"></div>

      <!-- YELLOW TEXT BLOCK SECTION -->
      <section class="yellow-text-section">
        <!-- SCATTERED GEAR ITEMS — BEHIND TEXT (blend through difference) -->
        <div class="parallax-layer back">
          <img class="parallax-item item-jacket" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/jacket.fca57bc0.png" alt="" loading="lazy" decoding="async" data-speed="0.14" data-drift="-0.22" data-rot="-0.6" />
          <img class="parallax-item item-gaiters" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/gaiters.aa2524de.png" alt="" loading="lazy" decoding="async" data-speed="0.42" data-drift="0.26" data-rot="-1.0" />
        </div>

        <div class="text-block-container">
          <p>We build gear ⟡ for people who see the outdoors ≠ as more than scenery ∴ they see it as a challenge.</p>
          <p>Every jacket ⊹ every layer ⊹ every detail is engineered ∿ to perform in the harshest conditions ⟶ so you can stay focused on the journey.</p>
          <p>We believe true performance ⟡ isn't measured by appearance ∴ but by how your gear responds to rain ∧ snow ∧ relentless wind ∧ high-altitude environments.</p>
          <p>Whether you're heading into a multi-day expedition ↟ climbing a summit ◇ or hiking before sunrise ⊹ our equipment is built to help you move with confidence.</p>
          <p>Because the moments that matter most begin where comfort ends ✦ adventure begins.</p>
        </div>

        <!-- SCATTERED GEAR ITEMS — IN FRONT OF TEXT -->
        <div class="parallax-layer front">
          <img class="parallax-item item-shorts" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/shorts.1a032e36.png" alt="" loading="lazy" decoding="async" data-speed="0.44" data-drift="0.28" data-rot="0.9" />
          <img class="parallax-item item-cap" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/cap.b10e4e2c.png" alt="" loading="lazy" decoding="async" data-speed="0.46" data-drift="-0.30" data-rot="1.4" />
          <img class="parallax-item item-scarf" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/scarf.427effaf.png" alt="" loading="lazy" decoding="async" data-speed="0.30" data-drift="0.24" data-rot="-1.2" />
          <img class="parallax-item item-backpack" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/backpack.0558dccb.png" alt="" loading="lazy" decoding="async" data-speed="0.18" data-drift="0.16" data-rot="0.5" />
          <img class="parallax-item item-boot" src="https://order-twine-70493179.figma.site/_components/v2/5922cc7522062a402e02d607e26cc654a692d2ad/boot.545d53aa.png" alt="" loading="lazy" decoding="async" data-speed="0.60" data-drift="-0.30" data-rot="1.8" />
        </div>
      </section>

      <!-- LOOP SCROLL SPACER -->
      <div id="loop-scroll-spacer"></div>
    </div>

    <script>
      // Live-updating clock in the exact format: "HH:MM:SS (PST) Weekday Month D YYYY"
      // e.g. "05:17:37 (PST) Monday July 6 2026"
      // updating every second via JS setInterval, using the browser's local time.
      
      const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
      const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

      function updateClock() {
        const now = new Date();
        
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        const dayName = weekdays[now.getDay()];
        const monthName = months[now.getMonth()];
        const dateNum = now.getDate();
        const year = now.getFullYear();
        
        const clockString = `${hours}:${minutes}:${seconds} (PST) ${dayName} ${monthName} ${dateNum} ${year}`;
        
        const clockEl = document.getElementById('clock-text');
        if (clockEl) {
          clockEl.textContent = clockString;
        }
        const mobileClockEl = document.getElementById('mobile-clock-text');
        if (mobileClockEl) {
          mobileClockEl.textContent = clockString;
        }
      }

      // Initial update and interval setup
      updateClock();
      setInterval(updateClock, 1000);

      // --- MOBILE / TABLET MENU TOGGLE LOGIC ---
      const menuToggleBtn = document.getElementById('menu-toggle-btn');
      const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');

      if (menuToggleBtn && mobileMenuOverlay) {
        menuToggleBtn.addEventListener('click', () => {
          const isOpen = mobileMenuOverlay.classList.contains('active');
          if (isOpen) {
            mobileMenuOverlay.classList.remove('active');
            menuToggleBtn.textContent = 'Menu';
            document.body.style.overflow = '';
          } else {
            mobileMenuOverlay.classList.add('active');
            menuToggleBtn.textContent = 'Close';
            document.body.style.overflow = 'hidden';
          }
        });

        // Close menu when clicking any item inside the overlay
        const mobileItems = mobileMenuOverlay.querySelectorAll('.cell');
        mobileItems.forEach(item => {
          if (item.id !== 'mobile-clock-text') {
            item.addEventListener('click', () => {
              mobileMenuOverlay.classList.remove('active');
              menuToggleBtn.textContent = 'Menu';
              document.body.style.overflow = '';
            });
          }
        });
      }

      // --- SMOOTH SCROLL CONTROLLED VIDEO PLAYBACK & TITLE ANIMATION ---
      const video = document.getElementById('bg-video');
      const titleContainer = document.getElementById('bottom-title-container');
      const heroSpacer = document.querySelector('.hero-spacer');
      const yellowSection = document.querySelector('.yellow-text-section');

      // Scattered gear items — cache elements and their parallax params once
      const parallaxItems = Array.from(document.querySelectorAll('.parallax-item')).map(el => ({
        el,
        speed: parseFloat(el.dataset.speed) || 0,
        drift: parseFloat(el.dataset.drift) || 0,
        rot: parseFloat(el.dataset.rot) || 0,
      }));
      let smoothP = 0;                // smoothed, section-normalized scroll progress (-1..1)
      const PARALLAX_TRAVEL = 520;    // px of vertical travel for a speed=1 item over the full range
      const PARALLAX_ROT = 4;         // deg of tilt for a rot=1 item over the full range

      const overlay = document.getElementById('product-slider-overlay');
      const track = document.getElementById('product-slider-track');
      const cards = document.querySelectorAll('.product-card');
      const cardImages = Array.from(cards).map(c => c.querySelector('.card-image'));
      const symbolEl = document.getElementById('slider-symbol');

      let targetTime = 0;
      let currentTime = 0;
      let currentScrollFraction = 0;
      let lastVideoSeekTime = 0;
      const sliderSymbols = ['◇', '≠', '↟', '✦', '⊹', '∧', '⟡', '∴', '⟶', '∿'];
      let lastSliderSymbolIdx = 0;

      // Scroll-driven reveal + card timeline
      const NUM_CARDS = document.querySelectorAll('.product-card').length;
      const REVEAL_PX = 700;                    // scroll length of the window-open phase
      const CARD_PX   = 900 * (NUM_CARDS - 1);  // scroll length of the card-swipe phase (per transition)
      const PARALLAX  = 0.18;
      let currentReveal = 0;   // smoothed 0..1
      let currentCard   = 0;   // smoothed 0..1 across the whole card phase
      let lastCardIndex = 0;

      function clamp01(v) { return Math.max(0, Math.min(1, v)); }
      function easeInOutCubic(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
      function switchSymbol() {
        symbolEl.style.opacity = '0';
        setTimeout(() => {
          let idx;
          do { idx = Math.floor(Math.random() * sliderSymbols.length); }
          while (idx === lastSliderSymbolIdx);
          symbolEl.textContent = sliderSymbols[idx];
          lastSliderSymbolIdx = idx;
          symbolEl.style.opacity = '1';
        }, 150);
      }

      let heroScrollDistance = heroSpacer ? heroSpacer.offsetHeight : window.innerHeight;
      let yellowSecTop = yellowSection ? yellowSection.offsetTop : 0;
      let yellowSecHeight = yellowSection ? yellowSection.offsetHeight : 0;

      // Prime the video so mobile Safari (iOS) will render seeked frames.
      // iOS won't paint / allow currentTime scrubbing on a video that was never played;
      // a muted inline play()->pause() unlocks frame-accurate seeking.
      let videoPrimed = false;
      function primeVideo() {
        if (!video || videoPrimed) return;
        video.muted = true;
        const p = video.play();
        if (p && typeof p.then === 'function') {
          p.then(() => { video.pause(); videoPrimed = true; }).catch(() => {});
        } else {
          try { video.pause(); } catch (e) {}
          videoPrimed = true;
        }
      }
      // Fallback: unlock on the first user gesture (older iOS requires one)
      window.addEventListener('touchstart', primeVideo, { passive: true });
      window.addEventListener('click', primeVideo, { passive: true });
      primeVideo();

      function updateTargetTime() {
        const scrollTop = window.scrollY;
        const scrollFraction = heroScrollDistance > 0 ? Math.min(1, scrollTop / heroScrollDistance) : 0;
        if (video && video.duration) {
          targetTime = scrollFraction * video.duration;
        }
      }

      // Optimize resizing - recalculate and cache layout-triggering properties
      function handleResize() {
        heroScrollDistance = heroSpacer ? heroSpacer.offsetHeight : window.innerHeight;
        yellowSecTop = yellowSection ? yellowSection.offsetTop : 0;
        yellowSecHeight = yellowSection ? yellowSection.offsetHeight : 0;
        updateTargetTime();
      }

      window.addEventListener('scroll', updateTargetTime, { passive: true });
      window.addEventListener('resize', handleResize, { passive: true });

      if (video) {
        video.addEventListener('loadedmetadata', () => {
          handleResize();
          primeVideo();
          currentTime = targetTime;
          video.currentTime = currentTime;
        });

        video.addEventListener('loadeddata', () => {
          handleResize();
          primeVideo();
          currentTime = targetTime;
          video.currentTime = currentTime;
        });
      }

      // Fallback polling for duration in case events already fired
      const checkDurationInterval = setInterval(() => {
        if (video && video.duration) {
          handleResize();
          clearInterval(checkDurationInterval);
        }
      }, 100);

      // Initialize initial scroll fraction
      if (heroScrollDistance > 0) {
        currentScrollFraction = Math.min(1, window.scrollY / heroScrollDistance);
      }

      function animate() {
        const scrollTop = window.scrollY;
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const cardStart = maxScroll - CARD_PX;
        const revealStart = cardStart - REVEAL_PX;

        // Deterministic scroll → state mapping (fully reversible)
        const revealRaw = clamp01((scrollTop - revealStart) / REVEAL_PX);
        const cardRaw = clamp01((scrollTop - cardStart) / CARD_PX);
        currentReveal += (revealRaw - currentReveal) * 0.15;
        currentCard += (cardRaw - currentCard) * 0.15;

        const scrollFraction = heroScrollDistance > 0 ? Math.min(1, scrollTop / heroScrollDistance) : 0;
        currentScrollFraction += (scrollFraction - currentScrollFraction) * 0.12;

        // --- SCATTERED GEAR ITEMS: scroll parallax around the olive section ---
        if (parallaxItems.length) {
          const secCenter = yellowSecTop + yellowSecHeight / 2;
          const dist = (scrollTop + window.innerHeight / 2) - secCenter;
          // Normalize by the section's travel range so motion stays subtle and
          // bounded regardless of section/viewport height (0 when centered, ±1 at edges).
          const range = (yellowSecHeight + window.innerHeight) / 2;
          const p = range > 0 ? Math.max(-1.2, Math.min(1.2, dist / range)) : 0;
          smoothP += (p - smoothP) * 0.12;
          for (let i = 0; i < parallaxItems.length; i++) {
            const it = parallaxItems[i];
            const y = -smoothP * it.speed * PARALLAX_TRAVEL;
            const x = smoothP * it.speed * it.drift * PARALLAX_TRAVEL;
            const r = smoothP * it.rot * PARALLAX_ROT;
            it.el.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${r}deg)`;
          }
        }

        // --- HERO TITLE animation (unchanged), hidden as the window opens ---
        const animStart = 0;
        const animEnd = 0.85;
        let t = (currentScrollFraction - animStart) / (animEnd - animStart);
        t = Math.max(0, Math.min(1, t));

        const scaleP = t;
        const translateY = -150 * scaleP;
        const scale = 1.0 - 0.20 * scaleP;

        const staggerStart = 0.3;
        const fadeP = t > staggerStart ? (t - staggerStart) / (1.0 - staggerStart) : 0;

        let opacityFinal = (1.0 - fadeP) * (1 - currentReveal);
        let blurValFinal = 24 * fadeP;

        if (titleContainer) {
          titleContainer.style.transform = `translateY(${translateY}px) scale(${scale})`;
          titleContainer.style.opacity = opacityFinal;
          titleContainer.style.filter = `blur(${blurValFinal}px)`;
          titleContainer.style.webkitFilter = `blur(${blurValFinal}px)`;
        }

        // --- WINDOW: grow a clip-path window (from zero) that reveals the slider behind ---
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        if (currentReveal < 0.003) {
          // Fully closed at rest — nothing of the slider shows on the hero
          overlay.style.clipPath = 'inset(50% 50% 50% 50%)';
          overlay.style.webkitClipPath = 'inset(50% 50% 50% 50%)';
        } else {
          const eased = easeInOutCubic(currentReveal);
          const w = vw * eased;
          const h = vh * eased;
          const insetX = Math.max(0, (vw - w) / 2);
          const insetY = Math.max(0, (vh - h) / 2);
          const clip = `inset(${insetY}px ${insetX}px round 3px)`;
          overlay.style.clipPath = clip;
          overlay.style.webkitClipPath = clip;
        }

        // --- CARDS: horizontal swipe driven by scroll ---
        const pos = currentCard * (NUM_CARDS - 1);   // 0 .. NUM_CARDS-1
        track.style.transform = `translateX(${-pos * vw}px)`;

        // --- PARALLAX inside each card ---
        const maxShift = vw * 0.18;
        for (let i = 0; i < cardImages.length; i++) {
          const delta = (i - pos) * vw;
          const shift = Math.max(-maxShift, Math.min(maxShift, -delta * PARALLAX));
          cardImages[i].style.transform = `translateX(${shift}px)`;
        }

        // --- SYMBOL swaps randomly on card crossing ---
        const idx = Math.round(pos);
        if (idx !== lastCardIndex) { lastCardIndex = idx; switchSymbol(); }

        // --- VIDEO scrub (hero zone only) ---
        if (video && video.duration) {
          const diff = targetTime - currentTime;
          if (Math.abs(diff) > 0.001) {
            currentTime += diff * 0.12;
          }
          if (!video.seeking) {
            const videoDiff = currentTime - video.currentTime;
            if (Math.abs(videoDiff) > 0.03) {
              const now = performance.now();
              if (now - lastVideoSeekTime > 30) {
                video.currentTime = currentTime;
                lastVideoSeekTime = now;
              }
            }
          }
        }

        requestAnimationFrame(animate);
      }

      requestAnimationFrame(animate);
    </script>
  </body>
</html>
```

---
*NeuroFlow Academy Site Templates*