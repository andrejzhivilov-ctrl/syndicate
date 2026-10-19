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