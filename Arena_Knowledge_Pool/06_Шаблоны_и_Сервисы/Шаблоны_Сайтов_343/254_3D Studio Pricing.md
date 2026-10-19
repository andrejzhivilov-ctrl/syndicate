---
title: "3D Studio Pricing"
template_id: "fbf89fc4-ee59-451f-be55-a71d3e9fa2eb"
section: "sections"
category_slug: "general"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/008e20b4-9e82-4d96-b6a9-f9fed4f05318.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sections
---

# 🌐 3D Studio Pricing

> **Секція:** `SECTIONS` | **Категорія:** `general`  
> **ID шаблону:** `fbf89fc4-ee59-451f-be55-a71d3e9fa2eb`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Pricing

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/008e20b4-9e82-4d96-b6a9-f9fed4f05318.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Create a full-screen hero section with a looping video background and a pricing card overlay. Use React with Tailwind CSS and Lucide React icons. The font is "Geist" loaded from Google Fonts.

**Video Background:**
- Full-screen `<video>` element, autoplaying, looped, muted, playsInline
- Covers the entire viewport with `object-cover`, positioned `object-right` on mobile, `object-center` on md+
- Video URL: `https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260702_102608_5fa1187d-9ac6-44fb-82ab-54376200abc0.mp4`

**Layout:**
- Section is `relative min-h-screen w-full overflow-hidden`, uses `font-geist` (custom Tailwind font family mapped to 'Geist')
- Content sits at `z-10`, arranged as a flex column filling min-h-screen
- Top area has generous padding (`pt-10 sm:pt-16 md:pt-24 px-5 sm:px-8 md:px-16 lg:px-24`)
- A flex-1 spacer pushes the bottom card down
- Bottom area has padding `px-4 sm:px-8 md:px-16 lg:px-24 pb-8 sm:pb-12 md:pb-20`

**Heading (top-left):**
- Text: "Studio" on line 1, "rate" on line 2
- Size: `text-[clamp(2.5rem,12vw,10rem)]`
- Weight: `font-light`, line-height: `leading-[0.9]`, tracking: `tracking-[-0.03em]`, color: white

**Pricing Card (bottom):**
- Outer container: full-width, `border border-white/10 rounded-2xl bg-black/70 backdrop-blur-md`, padding `p-3 sm:p-4 md:p-5`, fixed height `h-[280px] sm:h-[310px] md:h-[340px]`, flex column
- Inside: a 3-column grid (`grid-cols-1 md:grid-cols-3 gap-4 md:gap-5 items-stretch flex-1 min-h-0`)

**Column 1 - Toggle card:**
- `bg-[#11120F]/60 backdrop-blur-xl border border-white/10 rounded-xl p-5 sm:p-6`, flex column justify-between
- Heading: "Want cinematic fidelity?" - white, `text-base sm:text-lg font-medium mb-2`, left-aligned
- Description: "Activate photorealistic global illumination with sub-surface scattering and volumetric atmosphere depth." - `text-white/60 text-sm leading-relaxed`, left-aligned
- Bottom row: price "+$520" (`text-white text-lg font-light`) on left, custom toggle on right
- Toggle: `w-14 h-7 rounded-full`, active color `bg-[#B2D770]`, inactive `bg-white/20`, with a `w-5 h-5` black circle thumb that translates left/right. Uses React state.

**Column 2 - Price display:**
- `flex flex-col justify-between py-3 sm:py-4 md:py-5`
- Main price: "$3,180" at `text-4xl sm:text-5xl md:text-5xl lg:text-7xl font-light text-white tracking-tight`
- Suffix: "/deliver" in `text-white/50 text-sm sm:text-base ml-1`
- Bottom row: "Rush-mode" (`text-white/50 text-sm`) left, "12-36 hours" (`text-white/80 text-sm font-medium`) right

**Column 3 - Features + CTA:**
- `flex flex-col justify-between py-3 sm:py-4 md:py-5`
- 4 feature items with `CheckCircle2` icon (from lucide-react) in `text-[#B2D770] w-4 h-4 sm:w-5 sm:h-5` and label in `text-white/70 text-sm`:
  1. "Boundless iterations"
  2. "Cinema 8K mastergrade"
  3. "Bespoke 3D materials"
  4. "Dedicated render engineer 24/7"
- CTA button: split into two segments with `gap-[3px]`, both `bg-[#B2D770] text-black rounded-lg py-2.5`
  - Left: "Start a brief" with `text-sm font-medium px-4 sm:px-5`
  - Right: `ArrowUpRight` icon (lucide-react), `w-10` square-ish

**Accent Color:** `#B2D770` (lime green) used for toggle active state, checkmark icons, and CTA button.

**Global CSS (index.css):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Geist', sans-serif;
  background: #000;
  color: #fff;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

**Tailwind Config:**
- Extends `fontFamily` with `geist: ['Geist', 'sans-serif']`

**Google Font (in index.html head):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
```

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Studio Rate</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Geist', sans-serif;
      background: #000;
      color: #fff;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    .section {
      position: relative;
      min-height: 100vh;
      width: 100%;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: between;
    }

    .video-bg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: right;
    }

    .content {
      position: relative;
      z-index: 10;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-height: 100vh;
    }

    .heading-area {
      padding: 40px 20px 0;
    }

    .heading {
      font-size: clamp(2.5rem, 12vw, 10rem);
      font-weight: 300;
      line-height: 0.9;
      letter-spacing: -0.03em;
      color: #fff;
    }

    .spacer {
      flex: 1;
      min-height: 40px;
    }

    .card-area {
      padding: 0 16px 32px;
    }

    .outer-card {
      width: 100%;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 12px;
      height: 280px;
      display: flex;
      flex-direction: column;
    }

    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 16px;
      align-items: stretch;
      flex: 1;
      min-height: 0;
    }

    .col-1 {
      background: rgba(17, 18, 15, 0.6);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .col-1 h3 {
      color: #fff;
      font-size: 1rem;
      font-weight: 500;
      margin-bottom: 8px;
      text-align: left;
    }

    .col-1 p {
      color: rgba(255, 255, 255, 0.6);
      font-size: 0.875rem;
      line-height: 1.625;
      text-align: left;
    }

    .toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 24px;
    }

    .price-addon {
      color: #fff;
      font-size: 1.125rem;
      font-weight: 300;
    }

    .toggle {
      position: relative;
      width: 56px;
      height: 28px;
      border-radius: 9999px;
      background: #B2D770;
      cursor: pointer;
      border: none;
      transition: background 0.2s;
    }

    .toggle.off {
      background: rgba(255, 255, 255, 0.2);
    }

    .toggle-thumb {
      position: absolute;
      top: 4px;
      left: 32px;
      width: 20px;
      height: 20px;
      border-radius: 9999px;
      background: #000;
      transition: transform 0.2s;
    }

    .toggle.off .toggle-thumb {
      left: 4px;
    }

    .col-2 {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 12px 0;
    }

    .main-price {
      display: flex;
      align-items: baseline;
    }

    .main-price .amount {
      font-size: 2.25rem;
      font-weight: 300;
      color: #fff;
      letter-spacing: -0.025em;
    }

    .main-price .suffix {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.875rem;
      margin-left: 4px;
    }

    .rush-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 16px;
    }

    .rush-row .label {
      color: rgba(255, 255, 255, 0.5);
      font-size: 0.875rem;
    }

    .rush-row .value {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.875rem;
      font-weight: 500;
    }

    .col-3 {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 12px 0;
    }

    .features {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .feature-item svg {
      width: 16px;
      height: 16px;
      color: #B2D770;
      flex-shrink: 0;
    }

    .feature-item span {
      color: rgba(255, 255, 255, 0.7);
      font-size: 0.875rem;
    }

    .cta-group {
      display: flex;
      align-items: stretch;
      gap: 3px;
      margin-top: 16px;
    }

    .cta-text {
      background: #B2D770;
      color: #000;
      font-size: 0.875rem;
      font-weight: 500;
      padding: 10px 16px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      text-decoration: none;
    }

    .cta-icon {
      background: #B2D770;
      color: #000;
      width: 40px;
      padding: 10px 0;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .cta-icon svg {
      width: 16px;
      height: 16px;
    }

    /* Responsive */
    @media (min-width: 640px) {
      .heading-area {
        padding: 64px 32px 0;
      }
      .card-area {
        padding: 0 32px 48px;
      }
      .outer-card {
        padding: 16px;
        height: 310px;
      }
      .col-1 {
        padding: 24px;
      }
      .col-1 h3 {
        font-size: 1.125rem;
      }
      .toggle-row {
        margin-top: 32px;
      }
      .main-price .amount {
        font-size: 3rem;
      }
      .main-price .suffix {
        font-size: 1rem;
      }
      .col-2 {
        padding: 16px 0;
      }
      .col-3 {
        padding: 16px 0;
      }
      .features {
        gap: 10px;
      }
      .feature-item svg {
        width: 20px;
        height: 20px;
      }
      .cta-text {
        padding: 10px 20px;
      }
    }

    @media (min-width: 768px) {
      .video-bg {
        object-position: center;
      }
      .heading-area {
        padding: 96px 64px 0;
      }
      .card-area {
        padding: 0 64px 80px;
      }
      .outer-card {
        padding: 20px;
        height: 340px;
      }
      .grid {
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
      }
      .main-price .amount {
        font-size: 3rem;
      }
      .col-2 {
        padding: 20px 0;
      }
      .col-3 {
        padding: 20px 0;
      }
    }

    @media (min-width: 1024px) {
      .heading-area {
        padding: 96px 96px 0;
      }
      .card-area {
        padding: 0 96px 80px;
      }
      .main-price .amount {
        font-size: 4.5rem;
      }
    }
  </style>
</head>
<body>
  <section class="section">
    <!-- Video Background -->
    <video autoplay loop muted playsinline class="video-bg">
      <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260702_102608_5fa1187d-9ac6-44fb-82ab-54376200abc0.mp4" type="video/mp4" />
    </video>

    <!-- Content -->
    <div class="content">
      <!-- Top: Large heading -->
      <div class="heading-area">
        <h1 class="heading">Studio<br>rate</h1>
      </div>

      <!-- Spacer -->
      <div class="spacer"></div>

      <!-- Bottom: Pricing card -->
      <div class="card-area">
        <div class="outer-card">
          <div class="grid">
            <!-- Column 1 - Toggle card -->
            <div class="col-1">
              <div>
                <h3>Want cinematic fidelity?</h3>
                <p>Activate photorealistic global illumination with sub-surface scattering and volumetric atmosphere depth.</p>
              </div>
              <div class="toggle-row">
                <span class="price-addon">+$520</span>
                <button class="toggle" id="toggleBtn" onclick="toggleUhd()">
                  <span class="toggle-thumb"></span>
                </button>
              </div>
            </div>

            <!-- Column 2 - Price and stats -->
            <div class="col-2">
              <div class="main-price">
                <span class="amount">$3,180</span>
                <span class="suffix">/deliver</span>
              </div>
              <div class="rush-row">
                <span class="label">Rush-mode</span>
                <span class="value">12-36 hours</span>
              </div>
            </div>

            <!-- Column 3 - Features and CTA -->
            <div class="col-3">
              <div class="features">
                <div class="feature-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  <span>Boundless iterations</span>
                </div>
                <div class="feature-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  <span>Cinema 8K mastergrade</span>
                </div>
                <div class="feature-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  <span>Bespoke 3D materials</span>
                </div>
                <div class="feature-item">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  <span>Dedicated render engineer 24/7</span>
                </div>
              </div>
              <div class="cta-group">
                <a href="#" class="cta-text">Start a brief</a>
                <span class="cta-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <script>
    function toggleUhd() {
      const btn = document.getElementById('toggleBtn');
      btn.classList.toggle('off');
    }
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*