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