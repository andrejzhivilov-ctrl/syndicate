---
title: "Network Hero"
template_id: "c9270933-5f87-4e54-9d0e-4f788831a5e8"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Network Hero

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `c9270933-5f87-4e54-9d0e-4f788831a5e8`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Network Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/45a24257-7c43-497b-bd58-60aa8cf2da90.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a single-page React + Vite landing page for "Marketeam" -- a marketing talent platform. Use Inter (400, 500, 600, 700) and Urbanist (600, 700) from Google Fonts. The page is a full-viewport hero with a header, left content area, right animated circles visualization, and a bottom logo ticker strip.

---

### Background

Full-page background image covering the entire viewport:
```
https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_111401_56af5012-2263-45d3-849a-8688084d7c2a.png&w=1280&q=85
```
Applied as `background: url(...) center center / cover no-repeat` on the root `.app` container.

---

### Header

- Flexbox row, `justify-content: space-between`, padding `24px 64px`, max-width `1920px`, centered.
- **Left side**: Logo image + nav links
  - Logo: `<img>` with height 32px from: `https://polo-pecan-73837341.figma.site/_assets/v11/17ae538989a509947a8de3892c644664895e69b1.png`
  - Nav links: "Your Team", "Solutions", "Blog", "Pricing" -- color `#000000`, 15px, font-weight 400, with underline animation on hover (scaleX from 0 to 1, transform-origin left, 0.3s ease).
- **Right side**: "Log In" link + "Join Now" button
  - Log In: color `#ffffff`, 15px, weight 500, same underline hover as nav but white.
  - Join Now: pill button (border-radius 50px), black bg (`#000000`), white text, padding `12px 26px`, 15px, weight 500. On hover a `#A068FF` fill slides in from left using `::after` with `translateX(-100%)` to `translateX(0)`, cubic-bezier(0.22, 1, 0.36, 1), 0.4s. Button uses `overflow: hidden`.
  - The button is wrapped in a `.btn-border-wrap` div that has a rotating conic-gradient border using `::before` with `inset: -3px`, `padding: 3px`, mask technique for border-only effect. The gradient is: `conic-gradient(from var(--border-angle), #A068FF, #070319, #A068FF, #070319, #A068FF)`. It rotates via CSS `@property --border-angle` from `0deg` to `360deg` in 3s linear infinite.

---

### Hero Left

- `flex: 0 1 600px`, `padding-top: 40px`
- **Heading**: Typewriter effect, font Urbanist, 64px, weight 600, line-height 64px, letter-spacing -1.5px. Text: "Unlock Top Marketing Talent You Thought Was Out of Reach -- Now Just One Click Away!". The first 67 characters are colored `#000000`, the rest `#ffffff`. A blinking purple cursor (`#A068FF`) appears during typing. Typing speed: 35ms per character, starts after 400ms delay.
- **"Start Project" button**: Same pill style as Join Now but slightly larger (padding `14px 28px`, 16px), bg `#060218`. Has a right-arrow chevron SVG icon (18x18). Hover fill slides from right (`translateX(100%)` to `translateX(0)`). Also wrapped in `.btn-border-wrap` with the same rotating gradient border. Appears after typing finishes (animation-delay 3.2s).
- **Cursor element**: A purple cursor icon (SVG: pointer arrow filled `#A068FF`) + "David" label (pill badge, bg `#A068FF`, white text, 16px, weight 500, padding `8px 16px`, border-radius 20px). Positioned `margin-left: 290px`, `margin-top: 40px`. Appears with animation-delay 3.6s.

---

### Hero Right -- Circles Visualization

- Container: `720x720px`, centered.
- 4 concentric circles (orbits), each rotating slowly:
  - Orbit 1 (innermost): 353px diameter, spins left (counterclockwise) 30s
  - Orbit 2: 501px diameter, spins right 40s
  - Orbit 3: 649px diameter, spins right 50s
  - Orbit 4 (outermost): 797px diameter, spins left 60s
- Each circle has a 1px gradient border: `linear-gradient(180deg, rgba(217, 161, 255, 0) 0%, rgba(217, 161, 255, 1) 43%, rgba(217, 161, 255, 0) 100%)` applied via the mask technique.
- **Center circle (orbit-1)**: Displays an animated count-up number "20k+" (Urbanist 64px, weight 500) and "Specialists" label (Urbanist 16px, weight 600). Counter-rotates to stay upright.
- **Avatars** placed on orbits using `transform: translate(-50%, -50%) rotate(Xdeg) translate(radius) rotate(-Xdeg)`:
  - Avatar images (58px default, some 78px/88px) from these URLs:
    - `https://polo-pecan-73837341.figma.site/_assets/v11/aa51718fb3af3637e6d666b6543fc27a175fada6.png` (orbit 1, at 270deg, 177px radius, square with border-radius 20px, purple glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/ca755f7f93c1126fb8bdbf99ab364a33aa9ab272.png` (orbit 2, at 60deg, 251px, round, yellow glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/dc01064c7093dcc32674876ee3cf5e41c4a485c6.png` (orbit 2, at 180deg, 251px, 78px, pink glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/d5470a58b02388336141575048720f19a50de832.png` (orbit 2, at 300deg, 251px, square border-radius 20px, blue glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/018736aa5d0275c4ce56cfebaf2ae3007d81ca1e.png` (orbit 3, at 130deg, 325px, 88px, pink glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/c76d8a0b99676de31c014344bfaf75bad090758d.png` (orbit 4, at 30deg, 399px, purple glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/7b1b5f039de7b54cc9913e96c1923c3b15a157fa.png` (orbit 4, at 95deg, 399px, 88px, square border-radius 24px, orange glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/9ae171d8895199349755c43fbff00e122221a027.png` (orbit 4, at 220deg, 399px, 88px, square border-radius 24px, pink glow)
    - `https://polo-pecan-73837341.figma.site/_assets/v11/926c9eb7b4bc1df846fa0e39f0b0dc3fefd80671.png` (orbit 4, at 320deg, 399px, purple glow)
  - Each avatar has a staggered fly-in animation (scale 0.3 + rotate -180deg + blur -> normal), delays from 0.6s to 2.3s.

---

### Logo Ticker (Bottom)

- Horizontal infinitely scrolling strip of partner logos, `gap: 64px`, 20s animation.
- Fade masks on left/right edges (linear-gradient mask).
- 5 unique SVG logos repeated 4x for seamless loop:
  - `https://polo-pecan-73837341.figma.site/_assets/v11/1e7b0e6fcc016cd28aec5c68990118b8c54c35a5.svg`
  - `https://polo-pecan-73837341.figma.site/_assets/v11/3eac03c183db2ae080d910159211c14843398b61.svg`
  - `https://polo-pecan-73837341.figma.site/_assets/v11/17705a4c0023a0e5a99154dfb10582adbbf4260b.svg`
  - `https://polo-pecan-73837341.figma.site/_assets/v11/0e5f442b09dc5c248e3e60d40a65505fb1887228.svg`
  - `https://polo-pecan-73837341.figma.site/_assets/v11/63f99030ceb459e3c9ab9e429cfa2353491d3816.svg`
- Each logo: `width: 137px`, `height: 40px`, `object-fit: contain`.

---

### Entrance Animations

- Header: fade-down (translateY -20px to 0, 0.8s)
- Hero left: fade-up (translateY 40px to 0, 1s)
- Hero right circles: scale-in (scale 0.85 to 1 + opacity, 1.2s, delay 0.3s)
- Logos section: fade-up, delay 0.6s
- All using `cubic-bezier(0.22, 1, 0.36, 1)` easing.

---

### Responsive Breakpoints

- **1280px**: circles scale 0.85
- **1024px**: stack layout (flex-direction column), heading 48px, circles scale 0.7, nav gap shrinks
- **768px**: hide nav, heading 36px, circles scale 0.5
- **480px**: heading 28px, circles scale 0.4, smaller buttons/logos

---

### Key Colors

- Primary accent: `#A068FF`
- Background dark: `#060218` / `#070319`
- Text dark: `#000000`
- Text light: `#ffffff`
- Body bg fallback: `#0a0a0a`

---

### Technical Details

- React (useState, useEffect, useRef), Vite build
- Custom `useCountUp` hook: animates 0 to 20 over 2s with easeOutCubic, starts after 1.2s delay
- `TypewriterHeading` component: types char by char at configurable speed
- CSS `@property --border-angle` for the animated border gradient
- No external animation libraries -- pure CSS animations + JS for typewriter/counter

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Marketeam</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Urbanist:wght@500;600;700&display=swap" rel="stylesheet" />
  <style>
    @property --border-angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: #0a0a0a;
      color: #ffffff;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
    }

    .app {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background: url('https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_111401_56af5012-2263-45d3-849a-8688084d7c2a.png&w=1280&q=85') center center / cover no-repeat;
    }

    /* Header */
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 24px 64px;
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 48px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: #fff;
    }

    .logo-img {
      height: 32px;
      width: auto;
      object-fit: contain;
    }

    .nav {
      display: flex;
      align-items: center;
      gap: 32px;
    }

    .nav-link {
      color: #000000;
      text-decoration: none;
      font-size: 15px;
      font-weight: 400;
      position: relative;
      transition: transform 0.3s ease;
    }

    .nav-link::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 100%;
      height: 1px;
      background: #000000;
      transform: scaleX(0);
      transform-origin: left;
      transition: transform 0.3s ease;
    }

    .nav-link:hover::after {
      transform: scaleX(1);
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .login-link {
      color: #ffffff;
      text-decoration: none;
      font-size: 15px;
      font-weight: 500;
      letter-spacing: 0.5px;
      position: relative;
    }

    .login-link::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 100%;
      height: 1px;
      background: #ffffff;
      transform: scaleX(0);
      transform-origin: left;
      transition: transform 0.3s ease;
    }

    .login-link:hover::after {
      transform: scaleX(1);
    }

    .btn-border-wrap {
      position: relative;
      display: inline-block;
      border-radius: 50px;
    }

    .btn-border-wrap::before {
      content: '';
      position: absolute;
      inset: -3px;
      border-radius: 50px;
      background: conic-gradient(from var(--border-angle), #A068FF, #070319, #A068FF, #070319, #A068FF);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      padding: 3px;
      pointer-events: none;
      z-index: 0;
      animation: border-spin 3s linear infinite;
    }

    .join-btn {
      position: relative;
      background: #000000;
      color: #ffffff;
      border: none;
      padding: 12px 26px;
      border-radius: 50px;
      font-size: 15px;
      font-weight: 500;
      cursor: pointer;
      overflow: hidden;
      transition: none;
      z-index: 1;
    }

    .join-btn::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #A068FF;
      border-radius: 50px;
      transform: translateX(-100%);
      transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
      z-index: -1;
    }

    .join-btn:hover::after {
      transform: translateX(0);
    }

    .join-btn:active {
      opacity: 0.8;
    }

    /* Animations */
    .animate-fade-up {
      opacity: 0;
      transform: translateY(40px);
      animation: fade-up 1s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .animate-fade-down {
      opacity: 0;
      transform: translateY(-20px);
      animation: fade-down 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .animate-fade-in {
      opacity: 0;
      animation: fade-in 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .animate-scale-in {
      opacity: 0;
      transform: scale(0.85);
      animation: scale-in 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .animate-delay-300 { animation-delay: 0.3s; }
    .animate-delay-600 { animation-delay: 0.6s; }
    .animate-delay-3000 { animation-delay: 3.2s; }
    .animate-delay-3500 { animation-delay: 3.6s; }

    @keyframes border-spin {
      to { --border-angle: 360deg; }
    }

    @keyframes fade-up {
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fade-down {
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fade-in {
      to { opacity: 1; }
    }

    @keyframes scale-in {
      to { opacity: 1; transform: scale(1); }
    }

    /* Typewriter */
    .typewriter-cursor {
      display: inline-block;
      color: #A068FF;
      font-weight: 300;
      animation: blink-cursor 0.7s step-end infinite;
      margin-left: 2px;
    }

    @keyframes blink-cursor {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }

    /* Hero */
    .hero {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 60px 64px 80px;
      width: 100%;
      max-width: 1920px;
      margin: 0 auto;
      gap: 80px;
      flex: 1;
    }

    .hero-left {
      flex: 0 1 600px;
      padding-top: 40px;
      max-width: 600px;
    }

    .hero-heading {
      font-family: 'Urbanist', sans-serif;
      font-size: 64px;
      font-weight: 600;
      line-height: 64px;
      letter-spacing: -1.5px;
      color: #ffffff;
      margin-bottom: 40px;
    }

    .heading-dark {
      color: #000000;
    }

    .start-btn {
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #060218;
      color: #ffffff;
      border: none;
      padding: 14px 28px;
      border-radius: 50px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      overflow: hidden;
      transition: none;
      z-index: 1;
    }

    .start-btn::after {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 100%;
      height: 100%;
      background: #A068FF;
      border-radius: 50px;
      transform: translateX(100%);
      transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
      z-index: -1;
    }

    .start-btn:hover::after {
      transform: translateX(0);
    }

    .start-btn:active {
      opacity: 0.8;
    }

    .cursor-element {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 40px;
      margin-left: 290px;
    }

    .cursor-icon {
      transform: rotate(-5deg) translateY(-10px);
    }

    .cursor-label {
      background: #A068FF;
      color: #ffffff;
      padding: 8px 16px;
      border-radius: 20px;
      font-family: 'Inter', sans-serif;
      font-size: 16px;
      font-weight: 500;
      line-height: 24px;
    }

    /* Circles */
    .hero-right {
      flex: 1;
      max-width: 900px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .circles-container {
      position: relative;
      width: 720px;
      height: 720px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .orbit {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .orbit-1 { animation: spin-left 30s linear infinite; }
    .orbit-2 { animation: spin-right 40s linear infinite; }
    .orbit-3 { animation: spin-right 50s linear infinite; }
    .orbit-4 { animation: spin-left 60s linear infinite; }

    @keyframes spin-left {
      from { transform: rotate(0deg); }
      to { transform: rotate(-360deg); }
    }

    @keyframes spin-right {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    .circle {
      position: absolute;
      border-radius: 50%;
      background: transparent;
    }

    .circle::before {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 50%;
      padding: 1px;
      background: linear-gradient(180deg, rgba(217, 161, 255, 0) 0%, rgba(217, 161, 255, 1) 43%, rgba(217, 161, 255, 0) 100%);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
    }

    .circle-1 {
      width: 353px;
      height: 353px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      animation: counter-text 30s linear infinite;
    }

    @keyframes counter-text {
      from { rotate: 0deg; }
      to { rotate: 360deg; }
    }

    .circle-2 { width: 501px; height: 501px; }
    .circle-3 { width: 649px; height: 649px; }
    .circle-4 { width: 797px; height: 797px; }

    .circle-number {
      font-family: 'Urbanist', sans-serif;
      font-size: 64px;
      font-weight: 500;
      color: #ffffff;
      line-height: 64px;
    }

    .circle-label {
      font-family: 'Urbanist', sans-serif;
      font-size: 16px;
      font-weight: 600;
      line-height: 24px;
      color: #ffffff;
    }

    .circle-avatar {
      position: absolute;
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: #2a2a2a;
      border: 1px solid #3d3d3d;
      top: 50%;
      left: 50%;
      overflow: visible;
      z-index: 0;
      opacity: 0;
      animation: avatar-fly-in 1s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .avatar-1 { animation-delay: 0.6s; }
    .avatar-2 { animation-delay: 0.9s; }
    .avatar-3 { animation-delay: 1.1s; }
    .avatar-4 { animation-delay: 1.3s; }
    .avatar-5 { animation-delay: 1.5s; }
    .avatar-6 { animation-delay: 1.7s; }
    .avatar-7 { animation-delay: 1.9s; }
    .avatar-8 { animation-delay: 2.1s; }
    .avatar-9 { animation-delay: 2.3s; }

    @keyframes avatar-fly-in {
      0% {
        opacity: 0;
        scale: 0.3;
        rotate: -180deg;
        filter: brightness(2) blur(4px);
      }
      50% {
        opacity: 1;
        filter: brightness(1.5) blur(0px);
      }
      100% {
        opacity: 1;
        scale: 1;
        rotate: 0deg;
        filter: brightness(1) blur(0px);
      }
    }

    .avatar-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 50%;
      position: relative;
      z-index: 1;
    }

    .avatar-1 {
      transform: translate(-50%, -50%) rotate(270deg) translate(177px) rotate(-270deg);
      border: 1px solid rgba(160, 104, 255, 0.3);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(160, 104, 255, 0.5);
    }
    .avatar-1 .avatar-img { border-radius: 0; }

    .avatar-2 {
      transform: translate(-50%, -50%) rotate(60deg) translate(251px) rotate(-60deg);
      border: 1px solid rgba(247, 197, 114, 0.2);
      border-radius: 50%;
    }
    .avatar-2 .avatar-img {
      border-radius: 50%;
      box-shadow: 0 4px 20px rgba(247, 197, 114, 0.5);
    }

    .avatar-3 {
      transform: translate(-50%, -50%) rotate(180deg) translate(251px) rotate(-180deg);
      border: 1px solid rgba(221, 37, 144, 0.2);
      width: 78px;
      height: 78px;
    }
    .avatar-3 .avatar-img { box-shadow: 0 4px 20px rgba(221, 37, 144, 0.5); }

    .avatar-4 {
      transform: translate(-50%, -50%) rotate(300deg) translate(251px) rotate(-300deg);
      border: 1px solid rgba(74, 144, 217, 0.3);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(74, 144, 217, 0.5);
    }
    .avatar-4 .avatar-img { border-radius: 0; }

    .avatar-5 {
      transform: translate(-50%, -50%) rotate(130deg) translate(325px) rotate(-130deg);
      border: 1px solid rgba(255, 116, 159, 0.2);
      width: 88px;
      height: 88px;
    }
    .avatar-5 .avatar-img { box-shadow: 0 4px 20px rgba(255, 116, 159, 0.5); }

    .avatar-6 {
      transform: translate(-50%, -50%) rotate(30deg) translate(399px) rotate(-30deg);
    }
    .avatar-6 .avatar-img { box-shadow: 0 4px 20px rgba(161, 105, 255, 0.5); }

    .avatar-7 {
      transform: translate(-50%, -50%) rotate(95deg) translate(399px) rotate(-95deg);
      border-radius: 24px;
      border: 1px solid rgba(254, 161, 138, 0.3);
      overflow: hidden;
      width: 88px;
      height: 88px;
      box-shadow: 0 4px 20px rgba(254, 161, 138, 0.5);
    }
    .avatar-7 .avatar-img { border-radius: 0; }

    .avatar-8 {
      transform: translate(-50%, -50%) rotate(220deg) translate(399px) rotate(-220deg);
      border-radius: 24px;
      border: 1px solid rgba(255, 91, 145, 0.3);
      overflow: hidden;
      width: 88px;
      height: 88px;
      box-shadow: 0 4px 20px rgba(255, 91, 145, 0.5);
    }
    .avatar-8 .avatar-img { border-radius: 0; }

    .avatar-9 {
      transform: translate(-50%, -50%) rotate(320deg) translate(399px) rotate(-320deg);
    }
    .avatar-9 .avatar-img { box-shadow: 0 4px 20px rgba(161, 105, 255, 0.5); }

    /* Logos Ticker */
    .logos-section {
      padding: 40px 0;
      margin-top: auto;
      overflow: hidden;
      background: transparent;
    }

    .logos-ticker {
      width: 100%;
      overflow: hidden;
      mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
      -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
    }

    .logos-track {
      display: flex;
      align-items: center;
      gap: 64px;
      width: max-content;
      animation: ticker-scroll 20s linear infinite;
    }

    .ticker-logo {
      width: 137px;
      height: 40px;
      object-fit: contain;
      opacity: 1;
      border: none;
      flex-shrink: 0;
    }

    @keyframes ticker-scroll {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }

    /* Responsive */
    @media (max-width: 1280px) {
      .circles-container {
        transform: scale(0.85);
      }
    }

    @media (max-width: 1024px) {
      .header { padding: 20px 24px; }
      .header-left { gap: 24px; }
      .nav { gap: 20px; }

      .hero {
        flex-direction: column;
        align-items: center;
        padding: 40px 24px 60px;
        gap: 48px;
      }

      .hero-left {
        flex: none;
        padding-top: 0;
        max-width: 100%;
        text-align: center;
      }

      .hero-heading {
        font-size: 48px;
        line-height: 52px;
      }

      .start-btn { margin: 0 auto; }

      .cursor-element {
        justify-content: center;
        margin-left: 100px;
      }

      .hero-right {
        flex: none;
        width: 100%;
        max-width: 600px;
      }

      .circles-container {
        transform: scale(0.7);
      }
    }

    @media (max-width: 768px) {
      .nav { display: none; }
      .header { padding: 16px 20px; }

      .hero {
        padding: 32px 20px 48px;
        gap: 40px;
      }

      .hero-left { padding-top: 40px; }

      .hero-heading {
        font-size: 36px;
        line-height: 40px;
        letter-spacing: -1px;
      }

      .cursor-element { margin-left: 60px; }

      .hero-right { max-width: 400px; }

      .circles-container {
        transform: scale(0.5);
      }

      .logos-section { padding: 24px 0; }
      .ticker-logo { height: 28px; }
      .logos-track { gap: 40px; }
    }

    @media (max-width: 480px) {
      .header { padding: 14px 16px; }
      .login-link { font-size: 13px; }
      .join-btn { padding: 10px 20px; font-size: 13px; }

      .hero {
        padding: 24px 16px 40px;
        gap: 32px;
      }

      .hero-left { padding-top: 48px; }

      .hero-heading {
        font-size: 28px;
        line-height: 34px;
        margin-bottom: 28px;
      }

      .start-btn { padding: 12px 24px; font-size: 14px; }

      .cursor-element {
        margin-top: 28px;
        margin-left: 40px;
      }

      .cursor-label { font-size: 14px; padding: 6px 12px; }

      .hero-right { max-width: 320px; }

      .circles-container {
        transform: scale(0.4);
      }

      .ticker-logo { height: 22px; }
      .logos-track { gap: 32px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <header class="header animate-fade-down">
      <div class="header-left">
        <a href="#" class="logo">
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/17ae538989a509947a8de3892c644664895e69b1.png" alt="Marketeam" class="logo-img" />
        </a>
        <nav class="nav">
          <a href="#" class="nav-link">Your Team</a>
          <a href="#" class="nav-link">Solutions</a>
          <a href="#" class="nav-link">Blog</a>
          <a href="#" class="nav-link">Pricing</a>
        </nav>
      </div>
      <div class="header-right">
        <a href="#" class="login-link">Log In</a>
        <div class="btn-border-wrap">
          <button class="join-btn">Join Now</button>
        </div>
      </div>
    </header>

    <main class="hero">
      <div class="hero-left animate-fade-up">
        <h1 class="hero-heading" id="typewriter-heading"></h1>
        <div class="animate-fade-in animate-delay-3000">
          <div class="btn-border-wrap">
            <button class="start-btn">
              <span>Start Project</span>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M7 5l4 4-4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="cursor-element animate-fade-in animate-delay-3500">
          <svg class="cursor-icon" width="24" height="24" viewBox="0 0 14 18" fill="none">
            <path d="M1 1l4.5 14 2-5.5L13 7.5 1 1z" fill="#A068FF" stroke="#A068FF" stroke-width="0.5" stroke-linejoin="round"/>
          </svg>
          <span class="cursor-label">David</span>
        </div>
      </div>

      <div class="hero-right animate-scale-in animate-delay-300">
        <div class="circles-container">
          <div class="orbit orbit-4">
            <div class="circle circle-4"></div>
            <div class="circle-avatar avatar-6">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/c76d8a0b99676de31c014344bfaf75bad090758d.png" alt="" class="avatar-img" />
            </div>
            <div class="circle-avatar avatar-7">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/7b1b5f039de7b54cc9913e96c1923c3b15a157fa.png" alt="" class="avatar-img" />
            </div>
            <div class="circle-avatar avatar-8">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/9ae171d8895199349755c43fbff00e122221a027.png" alt="" class="avatar-img" />
            </div>
            <div class="circle-avatar avatar-9">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/926c9eb7b4bc1df846fa0e39f0b0dc3fefd80671.png" alt="" class="avatar-img" />
            </div>
          </div>
          <div class="orbit orbit-3">
            <div class="circle circle-3"></div>
            <div class="circle-avatar avatar-5">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/018736aa5d0275c4ce56cfebaf2ae3007d81ca1e.png" alt="" class="avatar-img" />
            </div>
          </div>
          <div class="orbit orbit-2">
            <div class="circle circle-2"></div>
            <div class="circle-avatar avatar-2">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/ca755f7f93c1126fb8bdbf99ab364a33aa9ab272.png" alt="" class="avatar-img" />
            </div>
            <div class="circle-avatar avatar-3">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/dc01064c7093dcc32674876ee3cf5e41c4a485c6.png" alt="" class="avatar-img" />
            </div>
            <div class="circle-avatar avatar-4">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/d5470a58b02388336141575048720f19a50de832.png" alt="" class="avatar-img" />
            </div>
          </div>
          <div class="orbit orbit-1">
            <div class="circle circle-1">
              <span class="circle-number" id="counter">0k+</span>
              <span class="circle-label">Specialists</span>
            </div>
            <div class="circle-avatar avatar-1">
              <img src="https://polo-pecan-73837341.figma.site/_assets/v11/aa51718fb3af3637e6d666b6543fc27a175fada6.png" alt="" class="avatar-img" />
            </div>
          </div>
        </div>
      </div>
    </main>

    <section class="logos-section animate-fade-up animate-delay-600">
      <div class="logos-ticker">
        <div class="logos-track">
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/1e7b0e6fcc016cd28aec5c68990118b8c54c35a5.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/3eac03c183db2ae080d910159211c14843398b61.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/17705a4c0023a0e5a99154dfb10582adbbf4260b.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/0e5f442b09dc5c248e3e60d40a65505fb1887228.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/63f99030ceb459e3c9ab9e429cfa2353491d3816.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/1e7b0e6fcc016cd28aec5c68990118b8c54c35a5.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/3eac03c183db2ae080d910159211c14843398b61.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/17705a4c0023a0e5a99154dfb10582adbbf4260b.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/0e5f442b09dc5c248e3e60d40a65505fb1887228.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/63f99030ceb459e3c9ab9e429cfa2353491d3816.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/1e7b0e6fcc016cd28aec5c68990118b8c54c35a5.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/3eac03c183db2ae080d910159211c14843398b61.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/17705a4c0023a0e5a99154dfb10582adbbf4260b.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/0e5f442b09dc5c248e3e60d40a65505fb1887228.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/63f99030ceb459e3c9ab9e429cfa2353491d3816.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/1e7b0e6fcc016cd28aec5c68990118b8c54c35a5.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/3eac03c183db2ae080d910159211c14843398b61.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/17705a4c0023a0e5a99154dfb10582adbbf4260b.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/0e5f442b09dc5c248e3e60d40a65505fb1887228.svg" alt="" class="ticker-logo" />
          <img src="https://polo-pecan-73837341.figma.site/_assets/v11/63f99030ceb459e3c9ab9e429cfa2353491d3816.svg" alt="" class="ticker-logo" />
        </div>
      </div>
    </section>
  </div>

  <script>
    // Typewriter effect
    (function() {
      const fullText = "Unlock Top Marketing Talent You Thought Was Out of Reach \u2013 Now Just One Click Away!";
      const splitIndex = 67;
      const heading = document.getElementById('typewriter-heading');
      const speed = 35;
      const startDelay = 400;
      let i = 0;

      setTimeout(function() {
        const interval = setInterval(function() {
          i++;
          const darkPart = fullText.slice(0, Math.min(i, splitIndex));
          const lightPart = i > splitIndex ? fullText.slice(splitIndex, i) : '';
          const cursor = i < fullText.length ? '<span class="typewriter-cursor">|</span>' : '';
          heading.innerHTML = '<span class="heading-dark">' + darkPart + '</span>' + lightPart + cursor;
          if (i >= fullText.length) clearInterval(interval);
        }, speed);
      }, startDelay);
    })();

    // Count-up effect
    (function() {
      const target = 20;
      const duration = 2000;
      const startDelay = 1200;
      const counterEl = document.getElementById('counter');

      setTimeout(function() {
        const startTime = performance.now();
        function animate(now) {
          const elapsed = now - startTime;
          const progress = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          const current = Math.floor(eased * target);
          counterEl.textContent = current + 'k+';
          if (progress < 1) requestAnimationFrame(animate);
        }
        requestAnimationFrame(animate);
      }, startDelay);
    })();
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*