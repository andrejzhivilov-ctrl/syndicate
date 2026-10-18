---
title: "Eco Intelligence"
template_id: "87c05afe-766a-47b3-afde-ed44ac3746dc"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Eco Intelligence

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `87c05afe-766a-47b3-afde-ed44ac3746dc`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero

### 🖼 Прев'ю:
![Eco Intelligence](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/6fae0e47-82cf-4784-a1e0-987b550fdc8e.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a full-screen hero section for a brand called "TERRA NOVA" using React, Tailwind CSS, and Lucide React icons. It must be fully mobile responsive. Use Vite + React + TypeScript + Tailwind.

**Fonts:**
- Load "Bebas Neue" from Google Fonts for the large background text.
- Load "Helvetica Neue Light" from: `https://db.onlinewebfonts.com/c/0e6de1ec911a2e267ff136bbdd384a44?family=Helvetica+Neue+Light`
- Set body font-family to: `'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif` with antialiased rendering.

**Background:**
- Full-screen `<video>` element set to autoPlay, muted, loop, playsInline, covering the entire viewport with `object-cover`.
- Video source URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_204426_c2ec12c0-3159-4601-8f8f-484c9a687833.mp4`
- Fallback background color: `#f5f4f0`

**Layout Structure (all content layered on top of the video with `relative z-10`):**

1. **Navbar** - Flex row, space-between, padding `px-5 sm:px-6 md:px-12 py-5 md:py-6`. Always black text on all screen sizes.
   - Left: A hamburger Menu icon (Lucide `Menu`, 20x20, strokeWidth 1.5) that opens a slide-in mobile menu. The word "Menu" is hidden below `sm` breakpoint.
   - Right: A small black dot (8x8 rounded-full) + "Book a call" text (text-sm tracking-wide).
   - Both sides have `hover:opacity-60 transition-opacity duration-300`.

2. **Main Content Area** - Takes remaining height (`flex-1`), with horizontal margin `mx-5 sm:mx-6 md:mx-12`, position relative.

   - **Vertical border lines (desktop only, hidden below md):** Two absolute-positioned columns (left edge and right edge), each containing: a thin 1px vertical line (bg-black/20) at 15% height, a "+" character (text-black/40, text-xs), a flex-1 line, another "+", and another 15% line.

   - **Decorative glass rectangles (desktop only, hidden below md):** Centered absolutely (top-1/2 left-1/2 -translate). A 2-col 3-row grid (220x330px at md). Three squares placed at positions [row1-col1], [row2-col1], [row3-col2]. Each square is 110x110px at md, with `bg-white/10 border border-white/40` and this exact box-shadow: `inset 0 2px 20px rgba(255,255,255,0.5), inset 0 -2px 14px rgba(0,0,0,0.2), 0 0 20px rgba(255,255,255,0.15), 0 0 40px rgba(255,255,255,0.05)`.

   - **Large background text "TERRA NOVA":** Absolutely positioned at `top-[2%]`, centered horizontally, full viewport width, pointer-events-none, select-none, overflow-hidden. Font is `font-['Bebas_Neue']`, size `text-[18vw] sm:text-[22vw] md:text-[30vw]`, leading-[0.85], tracking-tighter, whitespace-nowrap. The text uses a radial-gradient fill to appear as a subtle ghost/transparent text: `radial-gradient(83.65% 627.96% at 7.96% 53.9%, #c8c8c8 0%, rgba(200, 200, 200, 0) 52.41%, #c8c8c8 100%)` with `background-clip: text` and `-webkit-text-fill-color: transparent`.

   - **Bottom 2-column content (pinned to bottom with `mt-auto`):** Padding `pb-6 sm:pb-8 md:pb-12`, flex-col on mobile, flex-row on md+ with items-end and justify-between. Gap `gap-6 md:gap-12`, inner padding `px-2 sm:px-4 md:px-8`.

     **Left Column** (max-w-sm, `text-white sm:text-black`):
     - Heading: "Signals from" + line break + "the Deep Green". Sizes: `text-xl sm:text-2xl md:text-3xl lg:text-4xl`, font-light, leading-tight, tracking-tight.
     - Paragraph below (mt-3 md:mt-4): "An open research collective mapping, decoding, and archiving the silent vibrations that bind our planet's ecological networks." Sizes: `text-xs sm:text-sm`, color `text-white/70 sm:text-black/60`, max-w-[280px].
     - **Slanted/chamfered button** labeled "Start listening":
       - Dimensions: `w-[220px] sm:w-[260px] h-[44px] sm:h-[48px]`
       - Always black text.
       - Shape is a hexagon-like polygon with 14px chamfer cut at top-left and bottom-right corners, drawn via SVG `<polygon>` with stroke="currentColor" strokeWidth="1.5" and fill-transparent.
       - **On mobile only:** Has a white glass backdrop effect behind it: `bg-white/60 backdrop-blur-md border border-black/20` clipped to the same chamfer polygon shape using CSS `clip-path: polygon(14px 0, 100% 0, 100% calc(100% - 14px), calc(100% - 14px) 100%, 0 100%, 0 14px)`. On sm+ this glass effect is removed (`sm:bg-transparent sm:backdrop-blur-none sm:border-transparent`).
       - Content inside: label text (text-xs sm:text-sm tracking-wide) on left, ArrowRight icon (16x16) on right, with px-5 sm:px-6.
       - `hover:opacity-70 transition-opacity duration-300`.

     **Right Column - Glass Card** (max-w-xs md:max-w-[320px]):
     - `bg-white/60 backdrop-blur-md border border-white/80 p-5 sm:p-6 md:p-8 rounded-sm`
     - Header row: "Latest findings" (text-base sm:text-lg md:text-xl font-medium tracking-tight) left-aligned, "//02" (text-xs text-black/40) right-aligned. Below is a border-b border-black/10 with pb-3 md:pb-4.
     - Two content blocks (space-y-4 md:space-y-5, mt-4 md:mt-5):
       1. Title: "Canopy Pulse Analysis 09.17" (text-sm md:text-base font-semibold tracking-tight). Description: "Identified harmonic oscillation links between root mycelia networks and surrounding atmospheric moisture." (text-xs md:text-sm text-black/50 mt-1 md:mt-1.5 leading-relaxed).
       2. Title: "Watershed Harmonic Index 11.06". Description: "Forecasting framework for ecosystem regeneration spanning six continents using over 2,400 sensor arrays."
     - **Waveform SVG decoration** at bottom (mt-5 md:mt-6, centered): An SVG (viewBox 0 0 220 50, w-full) with a single `<path>` drawing a smooth waveform curve. Stroke: black, strokeWidth: 1.8, fill: none, strokeLinecap: round. Path data: `M0 30 C10 30 12 45 18 45 C24 45 26 10 34 10 C42 10 44 40 52 40 C60 40 62 5 70 5 C78 5 80 42 88 42 C96 42 98 15 106 15 C114 15 116 38 124 38 C132 38 134 20 142 20 C150 20 152 35 160 35 C168 35 170 22 178 22 C186 22 188 32 196 32 C204 32 210 28 220 28`

3. **Mobile Menu (slide-in overlay):**
   - State-controlled open/close. When open, body overflow is hidden.
   - **Backdrop:** Fixed full-screen, `bg-black/40 backdrop-blur-sm`, fades in/out with `transition-opacity duration-500`.
   - **Panel:** Fixed, top-0 left-0, full height, `w-full sm:w-[380px]`, `bg-[#f5f4f0]`, slides in from left with `transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]`.
   - Inside panel (px-8 sm:px-10 py-6, flex-col h-full):
     - Close button at top: X icon (20x20, strokeWidth 1.5) + "Close" text, mb-12.
     - Nav links: ['About', 'Research', 'Projects', 'Journal', 'Contact']. Each is a block `py-4 border-b border-black/10`. Text is `text-2xl sm:text-3xl font-light tracking-tight`. On hover, text slides right 8px and an ArrowRight icon (16x16) fades in from the right. Each link has a staggered entrance animation (opacity + translateY) with delays starting at 150ms, incrementing by 75ms.
     - Bottom section (mt-auto pb-8): border-t border-black/10 pt-6, "Get in touch" label (text-xs text-black/40 uppercase tracking-wide mb-3), email link "hello@terranova.earth" (text-sm text-black/70 hover:text-black). Also has staggered entrance with 600ms delay.

**CSS Reset (index.css):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  font-family: 'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}
```

**Key responsive behavior:**
- Mobile (< 640px): White text for heading/paragraph, glass-backed button, no vertical lines, no glass rectangles, compact spacing.
- Tablet (sm, 640px+): Text turns black, button loses glass backdrop, layout still single column.
- Desktop (md, 768px+): Two-column bottom layout, vertical border lines appear, glass rectangles appear, larger font sizes and spacing throughout.

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Terra Nova</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
  <link href="https://db.onlinewebfonts.com/c/0e6de1ec911a2e267ff136bbdd384a44?family=Helvetica+Neue+Light" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      font-family: 'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
    }
    .ghost-text {
      background: radial-gradient(83.65% 627.96% at 7.96% 53.9%, #c8c8c8 0%, rgba(200, 200, 200, 0) 52.41%, #c8c8c8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .glass-rect {
      box-shadow: inset 0 2px 20px rgba(255,255,255,0.5), inset 0 -2px 14px rgba(0,0,0,0.2), 0 0 20px rgba(255,255,255,0.15), 0 0 40px rgba(255,255,255,0.05);
    }
    .menu-panel {
      transition: transform 500ms cubic-bezier(0.16, 1, 0.3, 1);
    }
    .nav-link span:first-child {
      transition: transform 300ms;
    }
    .nav-link:hover span:first-child {
      transform: translateX(8px);
    }
    .nav-link svg {
      opacity: 0;
      transform: translateX(-8px);
      transition: all 300ms;
    }
    .nav-link:hover svg {
      opacity: 1;
      transform: translateX(0);
    }
    .btn-glass {
      clip-path: polygon(14px 0, 100% 0, 100% calc(100% - 14px), calc(100% - 14px) 100%, 0 100%, 0 14px);
    }
  </style>
</head>
<body>

<section class="relative h-screen w-full overflow-hidden bg-[#f5f4f0]">
  <!-- Background Video -->
  <video autoplay muted loop playsinline class="absolute inset-0 w-full h-full object-cover">
    <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_204426_c2ec12c0-3159-4601-8f8f-484c9a687833.mp4" type="video/mp4" />
  </video>

  <!-- Content Layer -->
  <div class="relative z-10 h-full flex flex-col">
    <!-- Navigation -->
    <nav class="flex items-center justify-between px-5 sm:px-6 md:px-12 py-5 md:py-6">
      <button onclick="openMenu()" class="flex items-center gap-2 sm:gap-3 cursor-pointer hover:opacity-60 transition-opacity duration-300">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
        <span class="text-sm tracking-wide hidden sm:inline">Menu</span>
      </button>
      <div class="flex items-center gap-2 cursor-pointer hover:opacity-60 transition-opacity duration-300">
        <span class="w-2 h-2 rounded-full bg-black"></span>
        <span class="text-sm tracking-wide">Book a call</span>
      </div>
    </nav>

    <!-- Main Content Area -->
    <div class="flex-1 relative mx-5 sm:mx-6 md:mx-12 flex flex-col">
      <!-- Left vertical line -->
      <div class="absolute left-0 top-0 bottom-0 hidden md:flex flex-col items-center">
        <div class="w-px bg-black/20 h-[15%]"></div>
        <span class="text-black/40 text-xs leading-none py-1">+</span>
        <div class="w-px bg-black/20 flex-1"></div>
        <span class="text-black/40 text-xs leading-none py-1">+</span>
        <div class="w-px bg-black/20 h-[15%]"></div>
      </div>

      <!-- Right vertical line -->
      <div class="absolute right-0 top-0 bottom-0 hidden md:flex flex-col items-center">
        <div class="w-px bg-black/20 h-[15%]"></div>
        <span class="text-black/40 text-xs leading-none py-1">+</span>
        <div class="w-px bg-black/20 flex-1"></div>
        <span class="text-black/40 text-xs leading-none py-1">+</span>
        <div class="w-px bg-black/20 h-[15%]"></div>
      </div>

      <!-- Decorative glass rectangles -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none hidden md:block">
        <div class="grid grid-cols-2 grid-rows-3 w-[220px] h-[330px]">
          <div class="w-[110px] h-[110px] bg-white/10 border border-white/40 glass-rect"></div>
          <div></div>
          <div class="w-[110px] h-[110px] bg-white/10 border border-white/40 glass-rect"></div>
          <div></div>
          <div></div>
          <div class="w-[110px] h-[110px] bg-white/10 border border-white/40 glass-rect"></div>
        </div>
      </div>

      <!-- Large Background Text -->
      <div class="absolute top-[2%] left-1/2 -translate-x-1/2 w-screen pointer-events-none select-none overflow-hidden">
        <h1 class="ghost-text text-center font-['Bebas_Neue'] text-[18vw] sm:text-[22vw] md:text-[30vw] leading-[0.85] tracking-tighter whitespace-nowrap">
          TERRA NOVA
        </h1>
      </div>

      <!-- Bottom 2-column content -->
      <div class="mt-auto pb-6 sm:pb-8 md:pb-12 flex flex-col md:flex-row md:items-end md:justify-between gap-6 md:gap-12 px-2 sm:px-4 md:px-8">
        <!-- Left column -->
        <div class="flex flex-col gap-5 md:gap-6 max-w-sm text-white sm:text-black">
          <div>
            <h2 class="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-light leading-tight tracking-tight">
              Signals from<br/>the Deep Green
            </h2>
            <p class="mt-3 md:mt-4 text-xs sm:text-sm text-white/70 sm:text-black/60 leading-relaxed max-w-[280px]">
              An open research collective mapping, decoding, and archiving the silent vibrations that bind our planet's ecological networks.
            </p>
          </div>

          <!-- Slanted Button -->
          <button class="group relative w-[220px] sm:w-[260px] h-[44px] sm:h-[48px] hover:opacity-70 transition-opacity duration-300 text-black">
            <div class="absolute inset-0 bg-white/60 backdrop-blur-md border border-black/20 sm:bg-transparent sm:backdrop-blur-none sm:border-transparent btn-glass"></div>
            <svg class="absolute inset-0 w-full h-full" viewBox="0 0 260 48" preserveAspectRatio="none" fill="none">
              <polygon points="14,0 260,0 260,34 246,48 0,48 0,14" stroke="currentColor" stroke-width="1.5" fill="transparent"/>
            </svg>
            <div class="relative flex items-center justify-between h-full px-5 sm:px-6">
              <span class="text-xs sm:text-sm tracking-wide">Start listening</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </div>
          </button>
        </div>

        <!-- Right column - Card -->
        <div class="bg-white/60 backdrop-blur-md border border-white/80 p-5 sm:p-6 md:p-8 max-w-xs md:max-w-[320px] rounded-sm">
          <div class="flex items-baseline justify-between mb-1 border-b border-black/10 pb-3 md:pb-4">
            <h3 class="text-base sm:text-lg md:text-xl font-medium tracking-tight">Latest findings</h3>
            <span class="text-xs text-black/40">//02</span>
          </div>

          <div class="space-y-4 md:space-y-5 mt-4 md:mt-5">
            <div>
              <h4 class="text-sm md:text-base font-semibold tracking-tight">Canopy Pulse Analysis 09.17</h4>
              <p class="text-xs md:text-sm text-black/50 mt-1 md:mt-1.5 leading-relaxed">
                Identified harmonic oscillation links between root mycelia networks and surrounding atmospheric moisture.
              </p>
            </div>
            <div>
              <h4 class="text-sm md:text-base font-semibold tracking-tight">Watershed Harmonic Index 11.06</h4>
              <p class="text-xs md:text-sm text-black/50 mt-1 md:mt-1.5 leading-relaxed">
                Forecasting framework for ecosystem regeneration spanning six continents using over 2,400 sensor arrays.
              </p>
            </div>
          </div>

          <!-- Waveform -->
          <div class="mt-5 md:mt-6 flex items-center justify-center">
            <svg width="220" height="50" viewBox="0 0 220 50" fill="none" class="w-full">
              <path d="M0 30 C10 30 12 45 18 45 C24 45 26 10 34 10 C42 10 44 40 52 40 C60 40 62 5 70 5 C78 5 80 42 88 42 C96 42 98 15 106 15 C114 15 116 38 124 38 C132 38 134 20 142 20 C150 20 152 35 160 35 C168 35 170 22 178 22 C186 22 188 32 196 32 C204 32 210 28 220 28" stroke="black" stroke-width="1.8" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Mobile Menu Backdrop -->
  <div id="menuBackdrop" class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm transition-opacity duration-500 opacity-0 pointer-events-none" onclick="closeMenu()"></div>

  <!-- Mobile Menu Panel -->
  <div id="menuPanel" class="fixed top-0 left-0 z-50 h-full w-full sm:w-[380px] bg-[#f5f4f0] menu-panel -translate-x-full">
    <div class="flex flex-col h-full px-8 sm:px-10 py-6">
      <!-- Close button -->
      <button onclick="closeMenu()" class="self-start flex items-center gap-2 hover:opacity-60 transition-opacity duration-300 mb-12">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        <span class="text-sm tracking-wide">Close</span>
      </button>

      <!-- Nav Links -->
      <nav class="flex flex-col gap-0" id="navLinks">
        <a href="#" class="nav-link block py-4 border-b border-black/10 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
          <div class="flex items-center justify-between">
            <span class="text-2xl sm:text-3xl font-light tracking-tight">About</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </div>
        </a>
        <a href="#" class="nav-link block py-4 border-b border-black/10 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
          <div class="flex items-center justify-between">
            <span class="text-2xl sm:text-3xl font-light tracking-tight">Research</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </div>
        </a>
        <a href="#" class="nav-link block py-4 border-b border-black/10 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
          <div class="flex items-center justify-between">
            <span class="text-2xl sm:text-3xl font-light tracking-tight">Projects</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </div>
        </a>
        <a href="#" class="nav-link block py-4 border-b border-black/10 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
          <div class="flex items-center justify-between">
            <span class="text-2xl sm:text-3xl font-light tracking-tight">Journal</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </div>
        </a>
        <a href="#" class="nav-link block py-4 border-b border-black/10 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
          <div class="flex items-center justify-between">
            <span class="text-2xl sm:text-3xl font-light tracking-tight">Contact</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </div>
        </a>
      </nav>

      <!-- Bottom info -->
      <div id="menuBottom" class="mt-auto pb-8 opacity-0 translate-y-4 transition-all duration-500" style="transition-delay: 0ms">
        <div class="border-t border-black/10 pt-6">
          <p class="text-xs text-black/40 tracking-wide uppercase mb-3">Get in touch</p>
          <a href="mailto:hello@terranova.earth" class="text-sm text-black/70 hover:text-black transition-colors duration-300 block">
            hello@terranova.earth
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<script>
  const backdrop = document.getElementById('menuBackdrop');
  const panel = document.getElementById('menuPanel');
  const navLinks = document.querySelectorAll('#navLinks a');
  const menuBottom = document.getElementById('menuBottom');

  function openMenu() {
    document.body.style.overflow = 'hidden';
    backdrop.classList.remove('opacity-0', 'pointer-events-none');
    backdrop.classList.add('opacity-100', 'pointer-events-auto');
    panel.classList.remove('-translate-x-full');
    panel.classList.add('translate-x-0');

    navLinks.forEach((link, i) => {
      link.style.transitionDelay = (150 + i * 75) + 'ms';
      setTimeout(() => {
        link.classList.remove('opacity-0', 'translate-y-4');
        link.classList.add('opacity-100', 'translate-y-0');
      }, 10);
    });

    menuBottom.style.transitionDelay = '600ms';
    setTimeout(() => {
      menuBottom.classList.remove('opacity-0', 'translate-y-4');
      menuBottom.classList.add('opacity-100', 'translate-y-0');
    }, 10);
  }

  function closeMenu() {
    document.body.style.overflow = '';
    backdrop.classList.add('opacity-0', 'pointer-events-none');
    backdrop.classList.remove('opacity-100', 'pointer-events-auto');
    panel.classList.add('-translate-x-full');
    panel.classList.remove('translate-x-0');

    navLinks.forEach((link) => {
      link.style.transitionDelay = '0ms';
      link.classList.add('opacity-0', 'translate-y-4');
      link.classList.remove('opacity-100', 'translate-y-0');
    });

    menuBottom.style.transitionDelay = '0ms';
    menuBottom.classList.add('opacity-0', 'translate-y-4');
    menuBottom.classList.remove('opacity-100', 'translate-y-0');
  }
</script>

</body>
</html>
```

---
*NeuroFlow Academy Site Templates*