---
title: "Cosmic"
template_id: "fee147af-a915-4e0f-bad6-94a023fe4760"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Cosmic

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `fee147af-a915-4e0f-bad6-94a023fe4760`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Cosmic](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/e3ebcf3a-ad05-4f31-8664-0c0604e0d7e2.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
**Create a full-viewport, dark cinematic hero section for a brand called "COSMIQ." using React, Tailwind CSS, and lucide-react. No other packages. Use Vite + TypeScript.**

---

### Fonts (loaded in `index.html`)

Load these three fonts via `<link>` tags in the `<head>`:

1. **Anton** (Google Fonts) -- used for the logo "COSMIQ." and mobile menu link labels
2. **Inter** weights 300/400/500/600 (Google Fonts) -- used for nav links, share button, and tagline
3. **Black Mustang** (OnlineWebFonts) -- used for the main headline

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
<link href="https://db.onlinewebfonts.com/c/70c5608e6eeb5d6f6fe1b2e5be774ec6?family=Black+Mustang" rel="stylesheet" />
```

Page title: `COSMIQ - What's Beyond`

---

### Layout

- Full viewport: `w-full h-[100dvh] overflow-hidden bg-[#0a0a0a]` with `position: relative`.
- All elements are absolutely/fixed positioned within this container using z-index layering.

---

### Z-Index Layers (bottom to top)

| Z-Index | Element |
|---------|---------|
| 0 | Stars background |
| 1 | Video |
| 5 | Headline text ("WHAT'S BEYOND") |
| 6 | Animated circles |
| 8 | Rock image overlay |
| 10 | Navigation bar |
| 100 | Mobile menu (fixed, full-screen) |

---

### 1. Stars Background (z-0)

- 40 tiny white dots (`div` elements) absolutely positioned across the viewport.
- Sizes alternate: every 3rd dot is 2x2px, others are 1x1px.
- Positions are deterministic: `left: (i * 37 + 13) % 100 %`, `top: (i * 53 + 7) % 100 %`.
- Each star has a `starTwinkle` animation: fades between `opacity: 0.2` and `opacity: 0.8`, duration `2 + (i % 4)` seconds, delay `(i * 0.3) % 3` seconds, infinite, ease-in-out.

---

### 2. Background Video (z-1)

- `<video>` element, absolute, covering full viewport with `object-cover`.
- **Source URL:** `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260613_233050_b3f1adc5-8b5f-41bb-b52a-0a79bd796ba8.mp4`
- Attributes: `muted`, `autoPlay`, `playsInline`. Does NOT loop.
- On `loadedMetadata`, set `playbackRate = 1.56`.
- On `ended`, set a `videoEnded` state to `true` (triggers headline animation and rock reveal).

---

### 3. Animated Circles (z-6)

Two concentric circles centered on the viewport (`left-1/2 top-1/2`, translated `-50%, -50%`). Both are `rounded-full border border-white pointer-events-none`.

**Inner circle:**
- Size: `min(95vw, 95vh)`, maxWidth/maxHeight: 1200px.
- Appears after 800ms delay (state-controlled).
- Entrance animation `circleShrink`: 3s, starts at `scale(4) opacity:0`, ends at `scale(1) opacity:0.3`. Easing: `cubic-bezier(0.16, 1, 0.3, 1)`.
- After entrance, plays `circlePulse` infinitely: 6s ease-in-out, gently oscillates between `scale(1) opacity:0.3` and `scale(1.03) opacity:0.4`.

**Outer circle:**
- Size: `min(160vw, 160vh)`, maxWidth/maxHeight: 2200px.
- Entrance animation `circleShrinkOuter`: 3.5s with 0.2s delay, starts at `scale(5) opacity:0`, ends at `scale(1) opacity:0.2`.
- After entrance, plays `circlePulseOuter` infinitely: 8s ease-in-out, oscillates between `scale(1) opacity:0.2` and `scale(1.02) opacity:0.28`.

---

### 4. Headline Text -- "WHAT'S BEYOND" (z-5)

- Positioned with: `bottom-[21vh] sm:bottom-[24vh] md:bottom-[10vh]`, full width, centered horizontally using flex.
- Horizontal padding: `px-2 sm:px-4 md:px-8`.
- `overflow-hidden` wrapper for the reveal effect.
- Font: `"Black Mustang", Anton, sans-serif`.
- Font size: `clamp(2.8rem, 17vw, 23rem)`.
- Letter spacing: `-0.04em`. Line height: `0.85`. White space: `nowrap`. Color: white.
- **Letter-by-letter reveal animation:** Each character is a separate `<span>` with `display: inline-block`. When `videoEnded` is false, each span is at `translateY(120%) opacity:0`. When true, it transitions to `translateY(0) opacity:1`.
  - Transform transition: `0.8s cubic-bezier(0.16, 1, 0.3, 1)` with stagger delay of `i * 60ms`.
  - Opacity transition: `0.5s ease-out` with same stagger delay.
- Spaces are rendered as `\u00A0` with width `0.25em`.

---

### 5. Rock Image Overlay (z-8)

- Absolute, covers full viewport (`inset-0`), `pointer-events-none`.
- Contains an `<img>` with `w-full h-full object-cover block`.
- **Image URL:** `https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1781394960/rock_vca457.png`
- Fades in when `videoEnded` is true: `opacity 0 -> 1`, transition `0.6s ease-out`.
- This image sits ON TOP of the headline text (z-8 vs z-5), creating a parallax/depth effect where the rock partially covers the bottom of the text.

---

### 6. Navigation Bar (z-10)

- Absolute, top of viewport: `top-0 left-0 right-0`, flex, `items-center justify-between`.
- Padding: `px-5 sm:px-8 md:px-12 py-4 sm:py-6`.
- Fades in: `fadeIn 1s ease-out 0.5s both`.

**Logo (left):**
- Text "COSMIQ." in white, `text-lg`, uppercase, `tracking-widest`.
- Font: `Anton, sans-serif`, letter-spacing: `0.15em`.

**Desktop Nav Links (center, hidden on mobile, visible md+):**
- Three links: "Discover", "Story", "Connect".
- `text-white/70 hover:text-white`, `text-xs`, `tracking-[0.25em]`, uppercase.
- Font: `Inter, sans-serif`. Transition: `colors 300ms`.
- Gap: `gap-10`.

**Right side:**
- Desktop (md+): "Share" text button + `Share2` icon from lucide-react. Same styling as nav links. Icon is `w-4 h-4`.
- Mobile: Hamburger `Menu` icon from lucide-react, `w-5 h-5`, white.

---

### 7. Full-Screen Mobile Menu (z-100, fixed)

Triggered by tapping the hamburger. Uses two states: `menuOpen` (controls mount/unmount) and `menuAnimating` (controls CSS transitions for enter/exit).

**Open:** Set `menuOpen = true`, then on next `requestAnimationFrame` set `menuAnimating = true`.
**Close:** Set `menuAnimating = false`, then after 600ms set `menuOpen = false`.

**Layers:**
1. **Backdrop:** `absolute inset-0 bg-[#0a0a0a]`, opacity transitions over 500ms.
2. **Circle reveal:** A `div` positioned at `top-4 right-5`, `rounded-full bg-white/[0.03]`. Grows from `0` to `300vmax` width/height with `transform: translate(50%, -50%)`. Easing: `cubic-bezier(0.16, 1, 0.3, 1)`, duration 800ms.
3. **Top bar:** Logo "COSMIQ." on left, `X` close icon on right. Fades in with 200ms delay.
4. **Nav links:** Three links ("Discover", "Story", "Connect") in a vertical column. Each is a row with the label on the left and an `ArrowUpRight` icon on the right. Separated by `border-b border-white/[0.08]`.
   - Label font: `Anton, sans-serif`, `text-4xl`, `tracking-tight`. On hover: `tracking-wider`.
   - Icon: `ArrowUpRight` from lucide-react, `w-5 h-5 text-white/30`. On hover: white, translates `+1px right, -1px up`.
   - Staggered entrance: each link has `300 + i * 100 ms` delay, slides up from `translateY(30px)`.
5. **Bottom section:** "Share" button with `Share2` icon, plus a decorative `12px-wide 1px-tall` white/20 line and tagline "Explore the unknown" in `text-[10px] tracking-[0.3em] text-white/30 uppercase`. Appears with 650ms delay.

---

### 8. CSS Keyframes (in `index.css`)

```css
@keyframes circleShrink {
  0% { transform: translate(-50%, -50%) scale(4); opacity: 0; }
  20% { opacity: 0.3; }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
}

@keyframes circleShrinkOuter {
  0% { transform: translate(-50%, -50%) scale(5); opacity: 0; }
  25% { opacity: 0.2; }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 0.2; }
}

@keyframes textReveal {
  0% { transform: translateY(100%); opacity: 0; }
  60% { opacity: 1; }
  100% { transform: translateY(0); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes rockFadeIn {
  0% { opacity: 0; transform: translateX(-50%) scale(0.95); }
  100% { opacity: 1; transform: translateX(-50%) scale(1); }
}

@keyframes starTwinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.8; }
}

@keyframes circlePulse {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.4; transform: translate(-50%, -50%) scale(1.03); }
}

@keyframes circlePulseOuter {
  0%, 100% { opacity: 0.2; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.28; transform: translate(-50%, -50%) scale(1.02); }
}
```

Also in `index.css`, a global reset:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { overflow-x: hidden; background: #0a0a0a; }
```

---

### Animation Sequence (Timeline)

1. **0ms** -- Page loads. Stars visible and twinkling. Video begins playing at 1.56x speed.
2. **500ms** -- Nav bar fades in (1s duration).
3. **800ms** -- Circles begin their shrink-in animation (inner 3s, outer 3.5s).
4. **Video ends** -- Headline "WHAT'S BEYOND" reveals letter-by-letter from bottom. Rock image fades in over 0.6s, overlaying the bottom portion of the text for depth.
5. **~3.8s** -- Circles finish entrance, begin gentle infinite pulse.

---

### Dependencies

- `react` ^18.3.1
- `react-dom` ^18.3.1
- `lucide-react` ^0.344.0 (for `Share2`, `Menu`, `X`, `ArrowUpRight` icons)
- `tailwindcss` ^3.4.1
- `vite` ^5.4.2 with `@vitejs/plugin-react`

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>COSMIQ - What's Beyond</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <link href="https://db.onlinewebfonts.com/c/70c5608e6eeb5d6f6fe1b2e5be774ec6?family=Black+Mustang" rel="stylesheet" />
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { overflow-x: hidden; background: #0a0a0a; height: 100%; }

    @keyframes circleShrink {
      0% { transform: translate(-50%, -50%) scale(4); opacity: 0; }
      20% { opacity: 0.3; }
      100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
    }
    @keyframes circleShrinkOuter {
      0% { transform: translate(-50%, -50%) scale(5); opacity: 0; }
      25% { opacity: 0.2; }
      100% { transform: translate(-50%, -50%) scale(1); opacity: 0.2; }
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes starTwinkle {
      0%, 100% { opacity: 0.2; }
      50% { opacity: 0.8; }
    }
    @keyframes circlePulse {
      0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
      50% { opacity: 0.4; transform: translate(-50%, -50%) scale(1.03); }
    }
    @keyframes circlePulseOuter {
      0%, 100% { opacity: 0.2; transform: translate(-50%, -50%) scale(1); }
      50% { opacity: 0.28; transform: translate(-50%, -50%) scale(1.02); }
    }

    .hero {
      position: relative;
      width: 100%;
      height: 100dvh;
      overflow: hidden;
      background: #0a0a0a;
    }

    /* Stars */
    .star {
      position: absolute;
      border-radius: 50%;
      background: white;
    }

    /* Video */
    .hero-video {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      z-index: 1;
    }

    /* Circles */
    .circle {
      position: absolute;
      left: 50%;
      top: 50%;
      border-radius: 50%;
      border: 1px solid white;
      pointer-events: none;
      z-index: 6;
      opacity: 0;
    }
    .circle-inner {
      width: min(95vw, 95vh);
      height: min(95vw, 95vh);
      max-width: 1200px;
      max-height: 1200px;
      transform: translate(-50%, -50%) scale(4);
    }
    .circle-inner.animated {
      animation: circleShrink 3s cubic-bezier(0.16, 1, 0.3, 1) forwards, circlePulse 6s ease-in-out 3s infinite;
    }
    .circle-outer {
      width: min(160vw, 160vh);
      height: min(160vw, 160vh);
      max-width: 2200px;
      max-height: 2200px;
      transform: translate(-50%, -50%) scale(5);
    }
    .circle-outer.animated {
      animation: circleShrinkOuter 3.5s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards, circlePulseOuter 8s ease-in-out 3.7s infinite;
    }

    /* Nav */
    .nav {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1.25rem;
      animation: fadeIn 1s ease-out 0.5s both;
    }
    @media (min-width: 640px) { .nav { padding: 1.5rem 2rem; } }
    @media (min-width: 768px) { .nav { padding: 1.5rem 3rem; } }

    .logo {
      color: white;
      font-size: 1.125rem;
      text-transform: uppercase;
      font-family: 'Anton', sans-serif;
      letter-spacing: 0.15em;
    }

    .nav-links {
      display: none;
      align-items: center;
      gap: 2.5rem;
    }
    @media (min-width: 768px) { .nav-links { display: flex; } }

    .nav-link {
      color: rgba(255,255,255,0.7);
      font-size: 0.75rem;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      text-decoration: none;
      font-family: 'Inter', sans-serif;
      transition: color 0.3s;
    }
    .nav-link:hover { color: white; }

    .nav-right {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .share-btn {
      display: none;
      align-items: center;
      gap: 0.5rem;
      color: rgba(255,255,255,0.7);
      font-size: 0.75rem;
      letter-spacing: 0.25em;
      text-transform: uppercase;
      font-family: 'Inter', sans-serif;
      background: none;
      border: none;
      cursor: pointer;
      transition: color 0.3s;
    }
    .share-btn:hover { color: white; }
    @media (min-width: 768px) { .share-btn { display: flex; } }

    .share-icon {
      width: 16px;
      height: 16px;
      color: rgba(255,255,255,0.7);
      cursor: pointer;
      transition: color 0.3s;
      display: none;
    }
    .share-icon:hover { color: white; }
    @media (min-width: 768px) { .share-icon { display: block; } }

    .menu-btn {
      position: relative;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      cursor: pointer;
    }
    @media (min-width: 768px) { .menu-btn { display: none; } }

    /* Headline */
    .headline-wrapper {
      position: absolute;
      bottom: 21vh;
      left: 0;
      right: 0;
      z-index: 5;
      overflow: hidden;
      padding: 0 0.5rem;
    }
    @media (min-width: 640px) { .headline-wrapper { bottom: 24vh; padding: 0 1rem; } }
    @media (min-width: 768px) { .headline-wrapper { bottom: 10vh; padding: 0 2rem; } }

    .headline-inner {
      overflow: hidden;
      display: flex;
      justify-content: center;
    }

    .headline {
      color: white;
      line-height: 0.85;
      padding-bottom: 0.5rem;
      display: flex;
      font-family: "Black Mustang", Anton, sans-serif;
      font-size: clamp(2.8rem, 17vw, 23rem);
      letter-spacing: -0.04em;
      white-space: nowrap;
    }
    @media (min-width: 640px) { .headline { padding-bottom: 1rem; } }

    .headline-char {
      display: inline-block;
      transform: translateY(120%);
      opacity: 0;
      transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s ease-out;
    }
    .headline-char.revealed {
      transform: translateY(0);
      opacity: 1;
    }

    /* Rock overlay */
    .rock-overlay {
      position: absolute;
      inset: 0;
      z-index: 8;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.6s ease-out;
    }
    .rock-overlay.visible { opacity: 1; }
    .rock-overlay img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* Mobile menu */
    .mobile-menu {
      position: fixed;
      inset: 0;
      z-index: 100;
      display: none;
    }
    .mobile-menu.open { display: block; }
    @media (min-width: 768px) { .mobile-menu { display: none !important; } }

    .menu-backdrop {
      position: absolute;
      inset: 0;
      background: #0a0a0a;
      opacity: 0;
      transition: opacity 0.5s ease-out;
    }
    .mobile-menu.animating .menu-backdrop { opacity: 1; }

    .menu-circle-reveal {
      position: absolute;
      top: 1rem;
      right: 1.25rem;
      border-radius: 50%;
      background: rgba(255,255,255,0.03);
      width: 0;
      height: 0;
      transform: translate(50%, -50%);
      transition: width 0.8s cubic-bezier(0.16,1,0.3,1), height 0.8s cubic-bezier(0.16,1,0.3,1);
    }
    .mobile-menu.animating .menu-circle-reveal {
      width: 300vmax;
      height: 300vmax;
    }

    .menu-topbar {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 1.25rem;
      opacity: 0;
      transition: opacity 0.3s;
    }
    .mobile-menu.animating .menu-topbar {
      opacity: 1;
      transition-delay: 200ms;
    }

    .menu-close-btn {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      cursor: pointer;
    }

    .menu-content {
      position: relative;
      z-index: 2;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: calc(100dvh - 64px);
      padding: 0 2rem 2.5rem;
    }

    .menu-nav {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      margin-top: 3rem;
    }

    .menu-nav-link {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1.25rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      text-decoration: none;
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.5s, transform 0.5s;
    }
    .mobile-menu.animating .menu-nav-link:nth-child(1) { opacity: 1; transform: translateY(0); transition-delay: 300ms; }
    .mobile-menu.animating .menu-nav-link:nth-child(2) { opacity: 1; transform: translateY(0); transition-delay: 400ms; }
    .mobile-menu.animating .menu-nav-link:nth-child(3) { opacity: 1; transform: translateY(0); transition-delay: 500ms; }

    .menu-nav-label {
      color: white;
      font-size: 2.25rem;
      letter-spacing: -0.025em;
      font-family: 'Anton', sans-serif;
      transition: letter-spacing 0.5s;
    }
    .menu-nav-link:hover .menu-nav-label { letter-spacing: 0.05em; }

    .menu-nav-arrow {
      width: 20px;
      height: 20px;
      color: rgba(255,255,255,0.3);
      transition: color 0.3s, transform 0.3s;
    }
    .menu-nav-link:hover .menu-nav-arrow {
      color: white;
      transform: translate(4px, -4px);
    }

    .menu-bottom {
      display: flex;
      flex-direction: column;
      gap: 2rem;
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.5s, transform 0.5s;
    }
    .mobile-menu.animating .menu-bottom {
      opacity: 1;
      transform: translateY(0);
      transition-delay: 650ms;
    }

    .menu-share-btn {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      color: rgba(255,255,255,0.5);
      background: none;
      border: none;
      cursor: pointer;
      font-family: 'Inter', sans-serif;
      transition: color 0.3s;
    }
    .menu-share-btn:hover { color: white; }
    .menu-share-btn svg { width: 16px; height: 16px; }
    .menu-share-btn span { font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase; }

    .menu-deco-line {
      width: 3rem;
      height: 1px;
      background: rgba(255,255,255,0.2);
    }

    .menu-tagline {
      color: rgba(255,255,255,0.3);
      font-size: 10px;
      letter-spacing: 0.3em;
      text-transform: uppercase;
      line-height: 1.625;
      font-family: 'Inter', sans-serif;
    }

    /* SVG icon base */
    .icon { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  </style>
</head>
<body>
  <div class="hero">
    <!-- Stars -->
    <div id="stars" style="position:absolute;inset:0;z-index:0;"></div>

    <!-- Video -->
    <video class="hero-video" muted autoplay playsinline id="heroVideo"
      src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260613_233050_b3f1adc5-8b5f-41bb-b52a-0a79bd796ba8.mp4">
    </video>

    <!-- Circles -->
    <div class="circle circle-inner" id="circleInner"></div>
    <div class="circle circle-outer" id="circleOuter"></div>

    <!-- Nav -->
    <nav class="nav">
      <div class="logo">COSMIQ.</div>
      <div class="nav-links">
        <a href="#" class="nav-link">Discover</a>
        <a href="#" class="nav-link">Story</a>
        <a href="#" class="nav-link">Connect</a>
      </div>
      <div class="nav-right">
        <button class="share-btn">Share</button>
        <svg class="share-icon icon" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        <button class="menu-btn" id="menuOpenBtn" aria-label="Open menu">
          <svg width="20" height="20" viewBox="0 0 24 24" class="icon" style="color:white"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
      </div>
    </nav>

    <!-- Headline -->
    <div class="headline-wrapper">
      <div class="headline-inner">
        <h1 class="headline" id="headline"></h1>
      </div>
    </div>

    <!-- Rock overlay -->
    <div class="rock-overlay" id="rockOverlay">
      <img src="https://res.cloudinary.com/dy5er7kv5/image/upload/q_auto/f_auto/v1781394960/rock_vca457.png" alt="" />
    </div>

    <!-- Mobile menu -->
    <div class="mobile-menu" id="mobileMenu">
      <div class="menu-backdrop"></div>
      <div class="menu-circle-reveal"></div>
      <div class="menu-topbar">
        <div class="logo">COSMIQ.</div>
        <button class="menu-close-btn" id="menuCloseBtn" aria-label="Close menu">
          <svg width="20" height="20" viewBox="0 0 24 24" class="icon" style="color:white"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="menu-content">
        <nav class="menu-nav">
          <a href="#" class="menu-nav-link" onclick="closeMenu()">
            <span class="menu-nav-label">Discover</span>
            <svg class="menu-nav-arrow icon" viewBox="0 0 24 24"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
          </a>
          <a href="#" class="menu-nav-link" onclick="closeMenu()">
            <span class="menu-nav-label">Story</span>
            <svg class="menu-nav-arrow icon" viewBox="0 0 24 24"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
          </a>
          <a href="#" class="menu-nav-link" onclick="closeMenu()">
            <span class="menu-nav-label">Connect</span>
            <svg class="menu-nav-arrow icon" viewBox="0 0 24 24"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
          </a>
        </nav>
        <div class="menu-bottom">
          <button class="menu-share-btn">
            <svg viewBox="0 0 24 24" class="icon"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
            <span>Share</span>
          </button>
          <div style="display:flex;flex-direction:column;gap:0.75rem;">
            <div class="menu-deco-line"></div>
            <p class="menu-tagline">Explore the unknown</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Stars
    const starsContainer = document.getElementById('stars');
    for (let i = 0; i < 40; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      const size = i % 3 === 0 ? 2 : 1;
      star.style.width = size + 'px';
      star.style.height = size + 'px';
      star.style.left = ((i * 37 + 13) % 100) + '%';
      star.style.top = ((i * 53 + 7) % 100) + '%';
      star.style.animation = `starTwinkle ${2 + (i % 4)}s ease-in-out ${(i * 0.3) % 3}s infinite`;
      starsContainer.appendChild(star);
    }

    // Video
    const video = document.getElementById('heroVideo');
    video.addEventListener('loadedmetadata', () => { video.playbackRate = 1.56; });
    video.addEventListener('ended', () => {
      revealHeadline();
      document.getElementById('rockOverlay').classList.add('visible');
    });

    // Circles - appear after 800ms
    setTimeout(() => {
      const inner = document.getElementById('circleInner');
      const outer = document.getElementById('circleOuter');
      inner.style.display = 'block';
      outer.style.display = 'block';
      setTimeout(() => {
        inner.classList.add('animated');
        outer.classList.add('animated');
      }, 100);
    }, 800);

    // Headline letter-by-letter
    const headlineText = "WHAT'S BEYOND";
    const headlineEl = document.getElementById('headline');
    headlineText.split('').forEach((char, i) => {
      const span = document.createElement('span');
      span.className = 'headline-char';
      span.style.transitionDelay = (i * 60) + 'ms';
      if (char === ' ') {
        span.innerHTML = '\u00A0';
        span.style.width = '0.25em';
      } else {
        span.textContent = char;
      }
      headlineEl.appendChild(span);
    });

    function revealHeadline() {
      document.querySelectorAll('.headline-char').forEach(el => el.classList.add('revealed'));
    }

    // Mobile menu
    const mobileMenu = document.getElementById('mobileMenu');
    document.getElementById('menuOpenBtn').addEventListener('click', () => {
      mobileMenu.classList.add('open');
      requestAnimationFrame(() => mobileMenu.classList.add('animating'));
    });

    function closeMenu() {
      mobileMenu.classList.remove('animating');
      setTimeout(() => mobileMenu.classList.remove('open'), 600);
    }
    document.getElementById('menuCloseBtn').addEventListener('click', closeMenu);
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*