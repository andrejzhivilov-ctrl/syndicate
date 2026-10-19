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