---
title: "Apex Pulse"
template_id: "962c24c6-ffe5-4d75-a531-8d56cfa8df42"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Apex Pulse

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `962c24c6-ffe5-4d75-a531-8d56cfa8df42`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page



### 🖼 Прев'ю:
![Apex Pulse](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/9b62b242-674b-4ca1-b412-b16c49fccfff.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Build a dark, cinematic drone/UAV technology landing page called **"AETHER_X"** using React + Vite + TypeScript + Tailwind CSS. The site has a scroll-driven video background and two content sections with reveal-on-scroll animations. Here is the exact specification:

---

### Font & Global Styles

- Load **Helvetica Neue Regular** via this stylesheet in `index.html`:
  ```
  https://db.onlinewebfonts.com/c/0d49fc455f4a8951a42daf952412a713?family=Helvetica+Neue+Regular
  ```
- Body: `font-family: 'Helvetica Neue Regular', 'Helvetica Neue', Helvetica, Arial, sans-serif`, background `#0a0a0a`, color `#fff`, antialiased.
- In `tailwind.config.js`, set `fontFamily.sans` and `fontFamily.mono` to `'"Flexo Soft Medium"', 'system-ui', 'sans-serif'`.
- Selection highlight: `rgba(255, 255, 255, 0.2)`.
- Page title: `AETHER_X — Where Sky Meets Machine Logic`

---

### Dependencies

Only: `react`, `react-dom`, `lucide-react`, `@supabase/supabase-js`. Tailwind + PostCSS + Autoprefixer + Vite for tooling.

---

### Architecture (5 components)

```
App.tsx
  -> ScrollVideo (fixed fullscreen background)
  -> Navbar (fixed top)
  -> main
       -> SectionOne (hero, bottom-aligned)
       -> spacer div (h-[80vh], aria-hidden)
       -> SectionTwo (full-height, justify-between)
```

---

### Component 1: `Reveal.tsx` (scroll-triggered animation wrapper)

- Props: `children`, `delay` (ms, default 0), `className`, `as` ('div' | 'span', default 'div')
- Uses `IntersectionObserver` with `threshold: 0.15`
- Animates from `translate-y-8 opacity-0` to `translate-y-0 opacity-100`
- Transition: `duration-700 ease-out will-change-transform`
- `transitionDelay` applied via inline style from `delay` prop

---

Component 2: ScrollVideo.tsx (frame-extracted scroll-synced video)
Video URL (CloudFront):

https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4
Architecture principle: The <video> element starts visible as a live fallback. The rAF loop starts immediately on mount and seeks the video on scroll. Once frame extraction finishes, the canvas becomes visible and the video is hidden -- seamless handoff with zero blank frames.
Implementation:
1. State: framesReady boolean (default false). framesRef holds extracted ImageBitmap[].
2. First useEffect (frame extraction, runs once):
    * Fetch video as blob, create object URL
    * Extract up to 120 frames at max width 1280px using createImageBitmap + sequential seek-based extraction (derive frame count from video.duration * 24, clamped between 30-120)
    * On success: store frames in framesRef.current, set framesReady = true
    * On failure or cancellation: do nothing -- the video fallback stays visible permanently
    * Cleanup: set cancelled flag, revoke object URL, close all ImageBitmaps
3. Second useEffect (rAF scroll-sync loop, deps: [framesReady]):
    * Starts immediately on mount (when framesReady is still false) -- this is critical
    * Re-runs when framesReady flips to true (cleans up old loop, starts new one with frame drawing)
    * Scroll handler: maps scrollY / (scrollHeight - innerHeight) to 0-1 progress, clamped
    * Resize handler: sets canvas dimensions to clientWidth * dpr x clientHeight * dpr (dpr capped at 2)
    * Tick function (rAF):
        * Smooth interpolation: smoothed += (targetProgress - smoothed) * 0.1
        * If frames exist (frames.length > 1): map smoothed to frame index, draw to canvas with cover-fit math
        * Else if video element exists (fallback): seek video.currentTime to smoothed * duration (with seek-lock to avoid stacking seeks)
    * Cover-fit draw: scale = max(canvasW/frameW, canvasH/frameH), center the scaled frame
4. Render structure:  <div class="fixed inset-0 -z-10 bg-[#0a0a0a]">
5.   {!framesReady && <video ... visible, muted, playsInline, preload="auto", object-cover />}
6.   <canvas ... class includes 'invisible' when !framesReady, removes it when framesReady />
7.   <div class="absolute inset-0 bg-black/20" /> (overlay)
8. </div>
9.   
Key detail: The <video> is conditionally rendered (!framesReady), so it is present and visible during loading. The canvas starts with invisible class and only becomes visible when framesReady flips. This guarantees something is always on screen -- the video during load, the canvas after extraction.



### Component 3: `Navbar.tsx`

- Fixed top, z-50, flex between, responsive padding (`px-5 py-4 sm:px-8 sm:py-5 md:px-12`)
- Left: custom SVG logo (white, 32x32, scales to 36x36 on sm+). SVG path:
  ```
  M 160 88 L 194 34 L 216 0 L 256 0 L 256 40 L 221.5 93.5 L 200 128 L 256 128 L 256 256 L 96 256 L 96 168 L 64.246 220 L 40 256 L 0 256 L 0 216 L 34 162 L 56 128 L 0 128 L 0 0 L 160 0 Z
  ```
- Right: pill button "Join The Fleet" -- `rounded-full bg-white text-black uppercase tracking-wider text-xs (sm:text-sm)`, hover: `bg-white/90 scale-105`
- Both wrapped in `<Reveal>` (logo delay 0, button delay 150)

---

### Component 4: `SectionOne.tsx` (Hero)

- Full viewport height, content at bottom (`flex-col justify-end`)
- 2-column grid on sm+, single column mobile
- **Column 1:** Large heading with 3 stacked `<Reveal as="span">` lines:
  - "Relentless." (delay 100)
  - "Sovereign." (delay 250)
  - "Unyielding." (delay 400)
  - Font size: `clamp(2.5rem, 8vw, 6rem)`, font-medium, leading-[1.05], tracking-tight, drop-shadow-lg
- **Column 2:** 3 stats in a flex-wrap row (right-aligned on sm+), delay 550:
  - `360` + degree symbol + "Sensor Array"
  - `12` + degree symbol + "Thermal Scan"
  - `98` + % + "Precision"
  - Values: `text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums`
  - Labels: `text-[10px] sm:text-xs uppercase tracking-wider text-white/50`

---

### Component 5: `SectionTwo.tsx`

- Full viewport, `flex-col justify-between`, responsive padding
- **Top-right block** (self-end, max-w-sm):
  - Heading (delay 100): "Precision / built into / every line." -- `text-3xl sm:text-4xl md:text-5xl font-semibold leading-[1.1]`
  - Stat row (delay 250, mt-8): 2-column grid `[auto_1fr]`
    - Left: "99.7%" bold + label "Fleet Ready"
    - Right: paragraph "Proven in 14,000+ sorties with unmatched operational readiness and zero downtime." -- `text-xs sm:text-sm text-white/70`

- **Bottom area** (mt-auto pt-16 sm:pt-20, 2-col grid on sm+):
  - Column 1 (delay 400): 3 stats in flex row:
    - `240 km` / "Reach"
    - `85 kg` / "Capacity"
    - `42 km/h` / "Glide Speed"
  - Column 2 (delay 550, sm:ml-auto):
    - 4 stats: `grid-cols-2 sm:flex`. First stat has `border border-white/30 rounded-lg`:
      - `160 km` / "Reach"
      - `5.8 hrs` / "Endurance"
      - `52 km/h` / "Max Pace"
      - `18 kg` / "Carry"
    - 2 pill buttons below:
      - "Schedule a Call" -- outline style (`border border-white/60 rounded-full`), hover: `border-white bg-white/10`
      - "Full Details" -- solid white, text-black, hover: `bg-white/90 scale-105`

---

### Key responsive breakpoints:
- Mobile: single column, smaller text, reduced padding
- `sm` (640px): 2-column grids activate, larger text
- `md` (768px): max padding/text sizes

### Color palette:
- Background: `#0a0a0a`
- Text: white, `white/70`, `white/60`, `white/50`
- Borders: `white/30`, `white/60`
- Overlay: `black/20`

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AETHER_X — Where Sky Meets Machine Logic</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://db.onlinewebfonts.com/c/0d49fc455f4a8951a42daf952412a713?family=Helvetica+Neue+Regular" rel="stylesheet" />
  <style>
    body {
      font-family: 'Helvetica Neue Regular', 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: #0a0a0a;
      color: #fff;
      -webkit-font-smoothing: antialiased;
      margin: 0;
    }
    ::selection {
      background-color: rgba(255, 255, 255, 0.2);
    }
    .reveal {
      transition: all 700ms cubic-bezier(0.33, 1, 0.68, 1);
      will-change: transform;
      transform: translateY(2rem);
      opacity: 0;
    }
    .reveal.visible {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <!-- Scroll Video Background -->
  <div id="video-bg" style="position:fixed;inset:0;z-index:-1;background:#0a0a0a;">
    <video
      id="fallback-video"
      src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4"
      muted
      playsinline
      preload="auto"
      style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;"
    ></video>
    <canvas
      id="scroll-canvas"
      style="position:absolute;inset:0;width:100%;height:100%;visibility:hidden;"
    ></canvas>
    <div style="position:absolute;inset:0;background:rgba(0,0,0,0.2);"></div>
  </div>

  <!-- Navbar -->
  <nav class="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-5 py-4 sm:px-8 sm:py-5 md:px-12">
    <div class="reveal">
      <a href="#" class="block" aria-label="Home">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 256 256" class="sm:h-9 sm:w-9">
          <path d="M 160 88 L 194 34 L 216 0 L 256 0 L 256 40 L 221.5 93.5 L 200 128 L 256 128 L 256 256 L 96 256 L 96 168 L 64.246 220 L 40 256 L 0 256 L 0 216 L 34 162 L 56 128 L 0 128 L 0 0 L 160 0 Z" fill="#ffffff"/>
        </svg>
      </a>
    </div>
    <div class="reveal" style="transition-delay:150ms;">
      <a href="#" class="group flex items-center gap-1.5 rounded-full bg-white px-5 py-2 text-xs font-medium uppercase tracking-wider text-black transition-all duration-300 hover:bg-white/90 hover:scale-105 sm:px-6 sm:py-2.5 sm:text-sm">
        Join The Fleet
      </a>
    </div>
  </nav>

  <!-- Main Content -->
  <main>
    <!-- Section One: Hero -->
    <section class="relative flex min-h-screen flex-col justify-end" style="min-height:100svh;">
      <div class="relative px-6 pb-10 sm:px-10 md:px-16 md:pb-16">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 sm:gap-12 items-end">
          <!-- Column 1: Heading -->
          <div>
            <h1 class="max-w-lg font-medium leading-[1.05] tracking-tight text-white drop-shadow-lg" style="font-size:clamp(2.5rem,8vw,6rem);">
              <span class="block reveal" style="transition-delay:100ms;">Relentless.</span>
              <span class="block reveal" style="transition-delay:250ms;">Sovereign.</span>
              <span class="block reveal" style="transition-delay:400ms;">Unyielding.</span>
            </h1>
          </div>
          <!-- Column 2: Stats -->
          <div class="reveal" style="transition-delay:550ms;">
            <div class="flex flex-wrap items-end gap-6 sm:gap-10 md:gap-14 sm:justify-end">
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">360<span class="text-lg text-white/70 sm:text-xl md:text-2xl">&deg;</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Sensor Array</span>
              </div>
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">12<span class="text-lg text-white/70 sm:text-xl md:text-2xl">&deg;</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Thermal Scan</span>
              </div>
              <div class="flex flex-col">
                <span class="text-2xl font-bold tabular-nums text-white sm:text-3xl md:text-4xl">98<span class="text-lg text-white/70 sm:text-xl md:text-2xl">%</span></span>
                <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50 sm:text-xs">Precision</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Spacer -->
    <div aria-hidden="true" style="height:80vh;"></div>

    <!-- Section Two -->
    <section class="relative flex min-h-screen flex-col justify-between px-6 py-10 sm:px-10 sm:py-14 md:px-16 md:py-20" style="min-height:100svh;">
      <!-- Top right area -->
      <div class="self-end w-full max-w-sm">
        <div class="reveal" style="transition-delay:100ms;">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold leading-[1.1] tracking-tight text-white">
            Precision<br/>built into<br/>every line.
          </h2>
        </div>
        <div class="reveal mt-8" style="transition-delay:250ms;">
          <div class="grid gap-3" style="grid-template-columns:auto 1fr;">
            <div class="flex flex-col">
              <span class="text-3xl sm:text-4xl font-bold text-white tabular-nums">99.7<span class="text-lg text-white/60">%</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Fleet Ready</span>
            </div>
            <div class="flex flex-col justify-center">
              <p class="text-xs sm:text-sm leading-relaxed text-white/70">Proven in 14,000+ sorties with unmatched operational readiness and zero downtime.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom area -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-8 sm:gap-12 mt-auto pt-16 sm:pt-20">
        <!-- Column 1: 3 stats -->
        <div class="reveal" style="transition-delay:400ms;">
          <div class="flex items-end gap-6 sm:gap-10">
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">240<span class="ml-0.5 text-sm sm:text-base text-white/60">km</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Reach</span>
            </div>
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">85<span class="ml-0.5 text-sm sm:text-base text-white/60">kg</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Capacity</span>
            </div>
            <div class="flex flex-col">
              <span class="text-2xl sm:text-3xl md:text-4xl font-bold tabular-nums text-white">42<span class="ml-0.5 text-sm sm:text-base text-white/60">km/h</span></span>
              <span class="mt-1 text-[10px] uppercase tracking-wider text-white/50">Glide Speed</span>
            </div>
          </div>
        </div>

        <!-- Column 2: 4 stats + buttons -->
        <div class="reveal sm:ml-auto" style="transition-delay:550ms;">
          <div class="flex flex-col gap-6">
            <!-- 4 stats -->
            <div class="grid grid-cols-2 sm:flex sm:items-stretch gap-0">
              <div class="flex flex-col px-3 sm:px-4 py-3 border border-white/30 rounded-lg">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">160<span class="ml-0.5 text-xs text-white/60">km</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Reach</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">5.8<span class="ml-0.5 text-xs text-white/60">hrs</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Endurance</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">52<span class="ml-0.5 text-xs text-white/60">km/h</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Max Pace</span>
              </div>
              <div class="flex flex-col px-3 sm:px-4 py-3">
                <span class="text-lg sm:text-xl font-bold tabular-nums text-white">18<span class="ml-0.5 text-xs text-white/60">kg</span></span>
                <span class="mt-0.5 text-[9px] uppercase tracking-wider text-white/50">Carry</span>
              </div>
            </div>
            <!-- Buttons -->
            <div class="flex items-center gap-3 mt-2">
              <a href="#" class="rounded-full border border-white/60 px-5 sm:px-6 py-2.5 text-[11px] sm:text-xs font-medium uppercase tracking-wider text-white transition-all duration-300 hover:border-white hover:bg-white/10">Schedule a Call</a>
              <a href="#" class="rounded-full bg-white px-5 sm:px-6 py-2.5 text-[11px] sm:text-xs font-medium uppercase tracking-wider text-black transition-all duration-300 hover:bg-white/90 hover:scale-105">Full Details</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    // --- Reveal Animation (IntersectionObserver) ---
    const revealEls = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach((el) => revealObserver.observe(el));

    // --- Scroll-Synced Video with Frame Extraction ---
    (function() {
      const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_230900_ef8565a6-16eb-4fe9-98e4-4b972d3f436d.mp4';
      const MAX_FRAMES = 120;
      const MAX_FRAME_WIDTH = 1280;

      const video = document.getElementById('fallback-video');
      const canvas = document.getElementById('scroll-canvas');
      const ctx = canvas.getContext('2d');

      let frames = [];
      let framesReady = false;
      let targetProgress = 0;
      let smoothed = 0;
      let lastFrameIndex = -1;
      let videoSeeking = false;

      // Scroll handler
      function onScroll() {
        const scrollable = document.documentElement.scrollHeight - window.innerHeight;
        targetProgress = scrollable > 0 ? Math.min(Math.max(window.scrollY / scrollable, 0), 1) : 0;
      }

      // Resize canvas
      function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(canvas.clientWidth * dpr);
        canvas.height = Math.round(canvas.clientHeight * dpr);
        lastFrameIndex = -1;
      }

      // Draw frame with cover-fit
      function drawCover(frame) {
        const cw = canvas.width;
        const ch = canvas.height;
        const s = Math.max(cw / frame.width, ch / frame.height);
        const dw = frame.width * s;
        const dh = frame.height * s;
        ctx.drawImage(frame, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
      }

      // Seek lock
      video.addEventListener('seeked', function() { videoSeeking = false; });

      // rAF loop - starts immediately, uses video fallback until frames ready
      function tick() {
        requestAnimationFrame(tick);
        smoothed += (targetProgress - smoothed) * 0.1;

        if (frames.length > 1) {
          const index = Math.min(Math.round(smoothed * (frames.length - 1)), frames.length - 1);
          if (index !== lastFrameIndex) {
            lastFrameIndex = index;
            drawCover(frames[index]);
          }
        } else if (video && video.duration && !videoSeeking) {
          const t = smoothed * video.duration;
          if (Math.abs(video.currentTime - t) > 0.001) {
            videoSeeking = true;
            video.currentTime = t;
          }
        }
      }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', resize);
      resize();
      onScroll();
      requestAnimationFrame(tick);

      // Frame extraction (async, runs in background)
      async function extractFrames(src) {
        const tempVideo = document.createElement('video');
        tempVideo.src = src;
        tempVideo.muted = true;
        tempVideo.playsInline = true;
        tempVideo.preload = 'auto';

        await new Promise(function(resolve, reject) {
          tempVideo.onloadedmetadata = resolve;
          tempVideo.onerror = function() { reject(new Error('video load failed')); };
        });

        const scale = Math.min(1, MAX_FRAME_WIDTH / tempVideo.videoWidth);
        const w = Math.round(tempVideo.videoWidth * scale);
        const h = Math.round(tempVideo.videoHeight * scale);
        const count = Math.min(Math.max(Math.round(tempVideo.duration * 24), 30), MAX_FRAMES);
        const extracted = [];

        for (let i = 0; i < count; i++) {
          const t = (i / (count - 1)) * Math.max(tempVideo.duration - 0.05, 0);
          await new Promise(function(resolve) {
            tempVideo.onseeked = resolve;
            tempVideo.currentTime = t;
          });
          extracted.push(await createImageBitmap(tempVideo, { resizeWidth: w, resizeHeight: h }));
        }

        tempVideo.removeAttribute('src');
        tempVideo.load();
        return extracted;
      }

      // Start extraction, switch to canvas when ready
      (async function() {
        try {
          const res = await fetch(VIDEO_URL);
          if (!res.ok) return;
          const blob = await res.blob();
          const objectUrl = URL.createObjectURL(blob);
          const extracted = await extractFrames(objectUrl);
          URL.revokeObjectURL(objectUrl);

          if (extracted.length < 2) {
            extracted.forEach(function(f) { f.close(); });
            return;
          }

          frames = extracted;
          framesReady = true;
          // Switch display: show canvas, hide video
          canvas.style.visibility = 'visible';
          video.style.display = 'none';
        } catch(e) {
          // Video fallback stays visible permanently
        }
      })();
    })();
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*