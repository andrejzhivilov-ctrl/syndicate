---
title: "AI Meeting Notes"
template_id: "a89f104d-2558-4400-a9e2-ae2081e66371"
section: "sites"
category_slug: "saas"
video_url: "https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/e9537cfe-5ff9-40b5-ae45-462c131fceed.mp4"
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 AI Meeting Notes

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `a89f104d-2558-4400-a9e2-ae2081e66371`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🎬 Відео-демонстрація:
- [Дивитися MP4 демонстрацію](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/video/e9537cfe-5ff9-40b5-ae45-462c131fceed.mp4)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
**Build a single-page landing page for "Livo AI" — an AI meeting analysis product. Use React + Vite + TypeScript + Tailwind CSS + Framer Motion + Lucide React. Font: Google Fonts "Inter" (weights 400, 500, 600, 700). The page has 4 full-screen sections wrapped in a `ScaledSection` component. Background color for sections 1 & 2: `rgb(254, 241, 238)`. Section 3 is a full-bleed image section. Section 4 background is white.**

---

### GLOBAL SETUP

- **Font:** `Inter` from Google Fonts, loaded via `<link>` in `index.html` with preconnect to `fonts.googleapis.com` and `fonts.gstatic.com`
- **Tailwind config:** extend animation with `'spin-slow': 'spin 3s linear infinite'`
- **Dependencies:** `framer-motion`, `lucide-react`, `react`, `react-dom`
- **CSS:** Only `@tailwind base; @tailwind components; @tailwind utilities;` in `index.css`

---

### SCALED SECTION WRAPPER COMPONENT

A wrapper component that applies a CSS `zoom` based on viewport dimensions. Design width: 1440px, design height: 900px, min-width breakpoint: 1024px. Below `minWidth`, zoom = 1 (no scaling). Above, zoom = `min(vw/1440, vh/900)` clamped to minimum 0.5. Applied via inline `style={{ zoom, width: '100%' }}`. If zoom === 1, render children directly without wrapper.

---

### SECTION 1: HERO

**Background:** `rgb(254, 241, 238)`, full viewport height, flex column centered.

#### Navbar
- Max-width 1440px, centered, `px-16` (desktop), flex row space-between.
- **Left:** App icon — 60x60px (md), rounded-[20px], with `box-shadow: 15px 25px 45px rgba(0,0,0,0.25)`. Image URL: `https://framerusercontent.com/images/sXJWPys5DXyez95t6axrD3kbJkc.png`
- **Center:** 5 nav links: "How it works", "Use cases", "Features", "Pricing", "FAQ". Font: Inter 16px, weight 500, tracking 0em, color black. Hidden on mobile (below lg).
- **Right:** Two 50x50px buttons, rounded-[16px], border `1px solid rgba(0,0,0,0.18)`. First has right arrow entity `&rarr;` (24px), second has Lucide `User` icon (24px, strokeWidth 1.5). Hidden on mobile.
- **Mobile:** Hamburger button (Lucide `Menu`), opens full-screen overlay with AnimatePresence. Mobile menu slides in with `initial={{ opacity: 0, y: -20 }}`, shows all nav links staggered, close button uses Lucide `X`.

#### Hero Content Area
- Max-width 1440px, flex row (desktop), column (mobile). Padding: `100px 64px 80px` (desktop).
- **Left column (max-width 520px):**
  - **Heading:** 82px (lg), 64px (md), 44px (mobile), weight 500, tracking `-0.05em`, line-height 1.1.
    - Line 1: "AI analysis" with gradient text: `linear-gradient(100deg, rgb(115,34,237) 0%, rgb(253,135,61) 100%)` applied via `-webkit-background-clip: text; -webkit-text-fill-color: transparent`.
    - Line 2: "for real-time discussions" in solid black.
    - **Animation:** Each word fades in individually with spring animation (stiffness 163, damping 40, mass 1). Initial: `opacity: 0, y: 10, filter: blur(10px)`. Stagger: 0.05s per word. Line 2 starts with 0.15s delay offset.
  - **Paragraph:** "Livo AI records your meetings, recognizes who's speaking, and provides real-time insights and live recommendations -- all without taking manual notes." Font: 18px (lg), 17px (md), 16px (mobile), weight 500, tracking `-0.02em`, color black, `text-wrap: balance`. Word animation with 0.4s delay offset, 0.02s stagger.
  - **CTA Buttons (flex row, gap 14px):**
    - **Primary "Start for free":** Wrapped in 5px padding container. Outer animated spinning conic gradient border: `conic-gradient(from 0deg, rgb(122,50,227) 0%, rgb(253,135,61) 25%, rgb(236,72,153) 50%, rgb(122,50,227) 75%, rgb(253,135,61) 100%)` — absolute positioned -200% top, -250% left, 600% width/height, `animation: spin 3s linear infinite`. Inner fill gap: `absolute inset-[2px] rounded-[21px] bg-[rgb(254,241,238)]`. Button itself: height 60px (md), padding 30px horizontal, rounded-[18px], gradient bg: `linear-gradient(135deg, rgba(122,50,227,1) 0%, rgba(236,72,153,0.9) 50%, rgba(253,135,61,1) 100%)`. White text 18px weight 500 tracking -0.02em. Has circle icon (28px, 1.5px white border) with right arrow SVG. Hover: scale 1.03, gradient overlay shifts to brighter colors, shadow `0 8px 32px rgba(122,50,227,0.35), 0 4px 16px rgba(253,135,61,0.25)`.
    - **Secondary "Contact us":** Height 60px, padding 32px, rounded-[20px], border `1px solid rgba(0,0,0,0.25)`, transparent bg, black text 18px weight 500. Hover: white bg, shadow, scale 1.03.
  - **Trust notes:** Flex row gap-6: "31-day free trial", "No credit card required", "Cancel anytime". Each prefixed with bullet, font 14px weight 500 tracking -0.02em black.
  - **Entire left column:** Framer Motion `initial={{ opacity: 0, y: 24 }}`, animates in on inView with duration 0.7s, ease `[0.25, 0.46, 0.45, 0.94]`.

- **Right column (hero image):**
  - Width 788px (desktop), aspect-ratio 3/2, rounded-2xl overflow hidden.
  - Image URL: `https://framerusercontent.com/images/b4pOG23X1MeuH63d5Dmm4HFLVA.png`
  - Framer Motion: `initial={{ opacity: 0, x: 40 }}`, animates on inView, duration 0.7s, delay 0.1s.

#### Offer Strip (bottom of hero)
- Full width, bg `rgba(255,255,255,0.82)`, flex column centered, gap 18px, padding `52px 40px 32px` (desktop).
- **Text row:** "Enjoy 50% off premium features for first 3 months -- 21 days remaining" (16px, weight 500, black) + "Start 14 days trial" link (16px, weight 500, color `rgb(122,50,227)`).
- **Logo ticker:** Height 85px, overflow hidden. Mask: `linear-gradient(270deg, transparent 0%, black 4.7%, black 95.3%, transparent 100%)`. Track: Framer Motion infinite linear scroll animation, 3x repeated logo set, gap 30px. Speed = totalWidth / 80 duration.
  - Logo images (all height 70px):
    1. `https://framerusercontent.com/images/Qo4XNTbEsI5VNAtleec5o3fWg.png` (width 210)
    2. `https://framerusercontent.com/images/t6BIfZjwwbbizLquISVq96n6EGc.png` (width 210)
    3. `https://framerusercontent.com/images/blfT46mvLdPrSwL7JUMxh1mUVI.png` (width 210)
    4. `https://framerusercontent.com/images/zDwbpG7hVs2UTJsIh3Fwr3eX4E.png` (width 164)
    5. `https://framerusercontent.com/images/F2VMPPEvVSp3zSIiTC7dXDzw.png` (width 210)

---

### SECTION 2: SCENARIOS / TALENT HIRING

**Background:** `rgb(254, 241, 238)`, min-height 100vh, centered content, padding `48px 64px`.

**Layout:** Flex row (desktop), max-width 1440px, gap 60px.

#### Left Column (540px wide, height 830px, flex column justify-between)
- **"Scenarios" label:** 28px (lg), weight 500, tracking -0.05em, gradient text `from-purple-600 to-pink-500`. Framer Motion fade in.
- **Heading container:** Fixed height 130px (lg). AnimatePresence mode="wait". Heading: 78px (lg), weight 500, tracking -0.05em, black. Slides: `initial={{ opacity: 0, y: 24 }}`, exit `{{ opacity: 0, y: -20 }}`, duration 0.55s. Each word animated individually (spring stiffness 160, damping 38, 0.04s stagger).
- **Paragraph container:** Fixed height 130px (lg). 21px (lg), line-height 1.55, tracking -0.02em, `rgba(0,0,0,0.75)`. AnimatePresence transitions.
- **Feature cards container:** Fixed height 248px (lg). 3 cards per slide (or 2 for some). Each card: flex row, gap 16px, bg white, rounded-[18px], height 72px, px-6, shadow `0 2px 8px rgba(0,0,0,0.04)`. Left icon: 36px circle, gradient `from-purple-100 to-pink-100`, Lucide `Check` 18px purple-600. Text: 18px weight 500 `rgba(0,0,0,0.8)`. Cards stagger in: delay `0.12 + i * 0.09`.
- **Pagination (bottom, desktop only):** 4 circular buttons, 44px each, gap 12px.
  - **Active:** SVG circle progress ring. Background circle: fill white, stroke `rgba(0,0,0,0.06)` strokeWidth 2.5. Progress circle: no fill, stroke gradient (purple #9333ea to pink #ec4899), strokeWidth 2.5, strokeLinecap round. Dash array: `progress * 125.66 / 125.66`. Rotated -90deg. Number label: 16px font-semibold black.
  - **Inactive:** Full circle border `1px solid rgba(0,0,0,0.2)`, number in `rgba(0,0,0,0.3)` weight 500.

#### Slide Data (4 slides, auto-advances every 5000ms):
1. **Talent & Hiring:** "Run interviews more efficiently by capturing candidate answers automatically and to turn them into clear, useful insights." Features: "Structured interviews with standardized questions", "Clear insights and hiring recommendations", "Automatic recording and transcription". Image: `https://framerusercontent.com/images/J8MYD2sMAbepbr2MiuyxCmAYEgk.png`
2. **Commercial Teams:** "Record all customer interactions to ensure precise follow-ups and use insights to accelerate deal progression." Features: "Track every customer touchpoint", "Leverage insights to drive deals", "Enable accurate follow-ups". Image: `https://polo-pecan-73837341.figma.site/_assets/v11/56974c2f2a0bcc77e6331ef7df0ebdd1d7d4d377.png`
3. **Management & Teams:** "Capture decisions with speaker-tagged transcripts and receive automated summaries. Broadcast live sessions so everyone stays updated in real time." Features: "Generate instant reports from the transcripts.", "Keep the team updated in real time." Image: `https://polo-pecan-73837341.figma.site/_assets/v11/b1bded3078219cd54a5a2fef5cb4919c68e7c261.png`
4. **Remote Team Members:** "Remain focused during meetings as Livo AI provides real-time transcription. Quickly act on key points with clear summaries." Features: "Capture every word instantly without manual note-taking.", "Get concise, actionable insights from discussions." Image: `https://polo-pecan-73837341.figma.site/_assets/v11/1c14b7ac2dcdea9ad19040e054b91f33dd4ed3ec.png`

#### Right Column (flex-1, height 830px)
- Rounded-2xl overflow hidden container. AnimatePresence mode="wait" for image transitions: `initial={{ opacity: 0, x: 80, scale: 0.97 }}`, exit `{{ opacity: 0, x: -50, scale: 0.97 }}`, duration 0.7s, ease `[0.44, 0, 0.56, 1]`. Image fills height, auto width.

---

### SECTION 3: APP ADVERT / AI ANALYSIS

**Layout:** Full viewport height, relative positioned, overflow hidden, flex center.

#### Background
- Two alternating full-bleed background images with AnimatePresence crossfade (duration 0.6s):
  1. `https://framerusercontent.com/images/qnyDJGivgHQMm5JaWxQxdKn3q0.png`
  2. `https://polo-pecan-73837341.figma.site/_assets/v11/f71ca5dd250ff31df02f32da412dc606df352cc5.png?w=2191`
- **Overlay:** `bg-gradient-to-r from-black/60 via-black/30 to-transparent` (desktop: from-black/40 via-black/15).

#### Content (z-10, full height, flex center, px-16 desktop)
- Max-width 1440px container.
- **App icon:** 110px (lg), rounded-[28px], shadow-2xl. Same icon URL as navbar. Spring animation on inView.
- **Heading:** 78px (lg), weight 500, tracking -0.05em, white. AnimatePresence mode="wait", word-by-word animation.
- **Paragraph:** 22px (lg), line-height 30px, weight 500, tracking -0.03em, `rgba(255,255,255,0.9)`. AnimatePresence with word animation.
- **CTA "Download App":** Height 66px (lg), rounded-[20px], gradient `linear-gradient(165deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%)`. Lucide `ArrowDownCircle` icon (32px, white, strokeWidth 1.5) + text 19px white weight 500. Hover: scale 1.04, shadow `0 8px 30px rgba(122,50,227,0.3)`.

#### Slide Data (2 slides, auto-advances every 7000ms):
1. Heading: "AI analysis", Paragraph: "Record meetings wherever you are with the Livo AI mobile app. From video calls to in-person conversations, effortlessly capture audio, generate live transcripts, and review actionable insights right from your phone."
2. Heading: "In real-time mode", Paragraph: "Start using Livo AI to seamlessly capture your meetings, turn conversations into clear understanding, and easily share key takeaways with your team."

---

### SECTION 4: PRICING PLANS

**Background:** White, min-height 100vh, flex center, padding `80px 0`.

#### Header
- **Title:** "Plans" — 58px (lg), weight 500, tracking -0.05em, black, centered. Word animation.
- **Billing toggle (gap 20px, centered):**
  - "Yearly" label (left, 16px weight 500, opacity 1 when active / 0.4 when inactive)
  - Toggle track: 52px x 32px, rounded-full, 3px padding, gradient bg `linear-gradient(135deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%)`. Thumb: 26px white circle, spring animated x position (0 for yearly, 20 for monthly).
  - "Monthly" label (right, same styling, inverse opacity)

#### Pricing Cards (flex row desktop, gap 24px, margin-top 72px)
Three cards, each `flex-1`, rounded-[30px], overflow hidden.

**Card 1 — Individual (light theme):**
- Top section: bg `rgb(254, 241, 238)`, min-height 400px, padding `64px 48px 40px`, centered column, gap 28px.
  - Name: "Individual" — 56px weight 500 tracking -0.05em black
  - Description: "Well suited for beginning without any expenses." — 18px weight 500 `rgba(0,0,0,0.8)`
  - Price: "0EUR" (yearly) / "0EUR" (monthly) — 38px weight 500 `rgba(0,0,0,0.5)`
  - CTA: "Free forever" — full-width, height 66px, rounded-[20px], black bg. Circle icon (30px, 1.5px white/60 border) with Lucide `ArrowUpRight` (15px white). Text 19px white.
  - Subtext: "0EUR per month" — 14px weight 500 `rgba(0,0,0,0.5)`
- Bottom section: bg `rgb(252, 225, 224)`, padding `40px 48px`.
  - Features with check circles (28px, `bg-black/5`, Check icon `rgba(0,0,0,0.7)`): "Mobile application", "Auto transcript", "Unlimited sessions", "Unlimited contacts"

**Card 2 — Advanced (dark theme, has ribbon):**
- **Ribbon:** Absolute top-[24px] right-[-32px], rotated 45deg. Inner: gradient bg, padding `7px 40px`. Text: "Top choice" 13px white.
- Top section: bg `#000`.
  - Name: "Advanced" — white
  - Description: "Unlimited premium tools" — `rgba(255,255,255,0.8)`
  - Price: Shows strikethrough "165EUR" (`rgba(255,255,255,0.5)`) + "132EUR" (white) when yearly. Just "165EUR" when monthly.
  - CTA: "Free 14 days trial" — gradient bg `linear-gradient(165deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%)`. Same circle+arrow style.
  - Subtext: "132EUR per month, paid annually" (yearly) / "165EUR per month" (monthly) — `rgba(255,255,255,0.5)`
- Bottom section: bg `rgb(24, 24, 24)`.
  - Features with check circles (`bg-white/10`, white Check): "Prompt modes", "Team collaboration", "Advanced summaries", "Live time history"

**Card 3 — Business (light theme):**
- Top section: bg `rgb(254, 241, 238)`.
  - Name: "Business"
  - Description: "Tailored or self-managed solutions"
  - Price: "Contact us" — 38px weight 500 black (not dimmed)
  - CTA: "Request pricing" — black bg
  - Subtext: "Schedule a short call -- we'll set everything up for you."
- Bottom: bg `rgb(252, 225, 224)`.
  - Features: "Self-hosted options", "HIPAA support", "Custom LLMs", "Priority support"

**Card animations:** Each card: `initial={{ opacity: 0, y: 36 }}`, spring animation on inView, staggered delay `index * 0.1`. Features stagger at `i * 0.06` delay. Price changes use AnimatePresence with blur transition.

---

### ANIMATION DETAILS

- **Word-by-word text animation (used everywhere):** Spring type, stiffness ~160, damping ~38, mass 1. Initial state: opacity 0, y 10-12px, filter blur(8-10px). Triggered by `useInView` with `once: true`, margin `-40px` to `-60px`. Words are `inline-block` spans separated by `\u00A0`.
- **Section entrance:** Framer Motion `useInView` triggers. Smooth ease: `[0.25, 0.46, 0.45, 0.94]`. Snappy ease: `[0.44, 0, 0.56, 1]`.
- **Slider transitions:** AnimatePresence mode="wait". Headings slide vertically, images slide horizontally with scale.
- **Hover interactions:** `whileHover={{ scale: 1.03-1.04 }}`, `whileTap={{ scale: 0.97 }}`, spring stiffness 300-400, damping 20-25.
- **Logo ticker:** Continuous linear scroll via Framer Motion `animate={{ x: [0, -totalWidth] }}` with `repeat: Infinity`.

---

### KEY TECHNICAL NOTES

- No CloudFront video URLs are used — all media are static images from `framerusercontent.com` and `polo-pecan-73837341.figma.site`.
- All font styling explicitly sets `fontFamily: 'Inter, sans-serif'` inline.
- All sections use `useInView` from Framer Motion with `once: true` to trigger entrance animations.
- Mobile menu uses `AnimatePresence` for smooth open/close.
- Scenarios and App Advert sections use `setInterval` for auto-advancing with cleanup in `useEffect`.
- The ScaledSection wrapper ensures the 1440px design scales down proportionally on smaller (but still desktop-sized) viewports.


SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Livo AI - AI Analysis for Real-Time Discussions</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; overflow-x: hidden; }
    a { text-decoration: none; color: inherit; }
    button { border: none; background: none; font-family: inherit; }
    img { display: block; max-width: 100%; }

    /* ===== ANIMATIONS ===== */
    @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes ticker-scroll { from { transform: translateX(0); } to { transform: translateX(-33.333%); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); filter: blur(8px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }
    @keyframes fadeInRight { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideInFromRight { from { opacity: 0; transform: translateX(80px) scale(0.97); } to { opacity: 1; transform: translateX(0) scale(1); } }

    .animate-word { display: inline-block; opacity: 0; transform: translateY(10px); filter: blur(10px); animation: fadeInUp 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }
    .animate-fade-in-up { opacity: 0; transform: translateY(24px); animation: fadeInUp 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; }
    .animate-fade-in-right { opacity: 0; animation: fadeInRight 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards; animation-delay: 0.1s; }
    .animate-fade-in { opacity: 0; animation: fadeIn 0.5s ease forwards; }

    /* ===== SECTION 1: HERO ===== */
    .hero-section { position: relative; width: 100%; min-height: 100vh; overflow: hidden; display: flex; flex-direction: column; align-items: center; background-color: rgb(254, 241, 238); }
    .hero-inner { width: 100%; display: flex; flex-direction: column; align-items: center; padding-top: 32px; flex: 1; }

    /* Navbar */
    .navbar { width: 100%; max-width: 1440px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 64px; }
    .navbar-logo { width: 60px; height: 60px; border-radius: 20px; overflow: hidden; flex-shrink: 0; box-shadow: 15px 25px 45px rgba(0,0,0,0.25); }
    .navbar-logo img { width: 100%; height: 100%; object-fit: cover; }
    .navbar-links { display: flex; align-items: center; gap: 54px; }
    .navbar-links a { font-size: 16px; line-height: 16px; font-weight: 500; letter-spacing: 0em; color: #000; transition: opacity 0.2s; }
    .navbar-links a:hover { opacity: 0.7; }
    .navbar-actions { display: flex; align-items: center; gap: 12px; }
    .navbar-btn { width: 50px; height: 50px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.18); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s; }
    .navbar-btn:hover { background: rgba(0,0,0,0.05); }
    .navbar-btn svg { width: 24px; height: 24px; stroke: #000; fill: none; stroke-width: 1.5; }

    /* Hero Content */
    .hero-content { width: 100%; max-width: 1440px; margin: 0 auto; display: flex; flex-direction: row; align-items: center; justify-content: space-between; padding: 100px 64px 80px; gap: 32px; flex: 1; }
    .hero-left { max-width: 520px; display: flex; flex-direction: column; gap: 40px; }
    .hero-heading { font-size: 82px; line-height: 1.1; font-weight: 500; letter-spacing: -0.05em; }
    .hero-heading-line1 { display: block; position: relative; z-index: 1; background: linear-gradient(100deg, rgb(115,34,237) 0%, rgb(253,135,61) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .hero-heading-line2 { display: block; color: #000; }
    .hero-paragraph { font-size: 18px; line-height: 28px; font-weight: 500; letter-spacing: -0.02em; color: #000; text-wrap: balance; }
    .hero-ctas { display: flex; align-items: center; gap: 14px; }

    /* Primary CTA */
    .cta-primary-wrapper { position: relative; padding: 5px; }
    .cta-primary-border { position: absolute; inset: 0; border-radius: 23px; overflow: hidden; }
    .cta-primary-border-inner { position: absolute; top: -200%; left: -250%; width: 600%; height: 600%; background: conic-gradient(from 0deg, rgb(122,50,227) 0%, rgb(253,135,61) 25%, rgb(236,72,153) 50%, rgb(122,50,227) 75%, rgb(253,135,61) 100%); animation: spin-slow 3s linear infinite; }
    .cta-primary-bg { position: absolute; inset: 2px; border-radius: 21px; background: rgb(254,241,238); }
    .cta-primary { position: relative; height: 60px; padding: 0 30px; border-radius: 18px; color: #fff; font-weight: 500; font-size: 18px; line-height: 18px; letter-spacing: -0.02em; cursor: pointer; overflow: hidden; display: flex; align-items: center; gap: 12px; background: linear-gradient(135deg, rgba(122,50,227,1) 0%, rgba(236,72,153,0.9) 50%, rgba(253,135,61,1) 100%); transition: transform 0.2s, box-shadow 0.3s; }
    .cta-primary:hover { transform: scale(1.03); box-shadow: 0 8px 32px rgba(122,50,227,0.35), 0 4px 16px rgba(253,135,61,0.25); }
    .cta-primary:active { transform: scale(0.97); }
    .cta-primary-circle { width: 28px; height: 28px; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.8); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .cta-primary-circle svg { width: 14px; height: 14px; margin-left: 1px; }

    /* Secondary CTA */
    .cta-secondary { height: 60px; padding: 0 32px; border-radius: 20px; border: 1px solid rgba(0,0,0,0.25); background: transparent; color: #000; font-weight: 500; font-size: 18px; line-height: 18px; letter-spacing: -0.02em; cursor: pointer; transition: all 0.3s; }
    .cta-secondary:hover { background: #fff; border-color: rgba(0,0,0,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.08); transform: scale(1.03); }
    .cta-secondary:active { transform: scale(0.97); }

    /* Trust Notes */
    .trust-notes { display: flex; flex-wrap: wrap; align-items: center; gap: 24px; }
    .trust-notes span { font-size: 14px; line-height: 14px; font-weight: 500; letter-spacing: -0.02em; color: #000; white-space: nowrap; }

    /* Hero Image */
    .hero-right { width: 788px; flex-shrink: 0; }
    .hero-image-container { width: 100%; aspect-ratio: 3/2; border-radius: 16px; overflow: hidden; }
    .hero-image-container img { width: 100%; height: 100%; object-fit: cover; }

    /* Offer Strip */
    .offer-strip { width: 100%; background: rgba(255,255,255,0.82); display: flex; flex-direction: column; align-items: center; gap: 18px; padding: 52px 40px 32px; }
    .offer-text { display: flex; align-items: center; gap: 18px; text-align: center; }
    .offer-text span { font-size: 16px; line-height: 16px; font-weight: 500; letter-spacing: -0.02em; color: #000; }
    .offer-text a { font-size: 16px; line-height: 16px; font-weight: 500; letter-spacing: -0.02em; color: rgb(122,50,227); transition: opacity 0.2s; }
    .offer-text a:hover { opacity: 0.7; }

    /* Logo Ticker */
    .logo-ticker { width: 100%; height: 85px; overflow: hidden; position: relative; }
    .logo-ticker-mask { position: absolute; inset: 0; z-index: 10; pointer-events: none; mask-image: linear-gradient(270deg, transparent 0%, black 4.7%, black 95.3%, transparent 100%); -webkit-mask-image: linear-gradient(270deg, transparent 0%, black 4.7%, black 95.3%, transparent 100%); }
    .logo-ticker-track { display: flex; align-items: center; gap: 30px; height: 100%; position: absolute; animation: ticker-scroll 15s linear infinite; }
    .logo-ticker-track img { height: 70px; flex-shrink: 0; object-fit: contain; }

    /* ===== SECTION 2: SCENARIOS ===== */
    .scenarios-section { width: 100%; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 48px 64px; background-color: rgb(254, 241, 238); }
    .scenarios-inner { width: 100%; max-width: 1440px; margin: 0 auto; display: flex; flex-direction: row; align-items: flex-start; gap: 60px; }
    .scenarios-left { width: 540px; flex-shrink: 0; display: flex; flex-direction: column; justify-content: space-between; height: 830px; }
    .scenarios-left-content { display: flex; flex-direction: column; gap: 36px; }
    .scenarios-label { font-size: 28px; font-weight: 500; line-height: 28px; letter-spacing: -0.05em; background: linear-gradient(to right, #9333ea, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .scenarios-heading-container { height: 130px; overflow: visible; }
    .scenarios-heading { font-size: 78px; font-weight: 500; line-height: 1.05; letter-spacing: -0.05em; color: #000; transition: opacity 0.5s, transform 0.5s; }
    .scenarios-paragraph-container { height: 130px; }
    .scenarios-paragraph { font-size: 21px; line-height: 1.55; letter-spacing: -0.02em; color: rgba(0,0,0,0.75); max-width: 560px; transition: opacity 0.45s, transform 0.45s; }
    .scenarios-features { height: 248px; display: flex; flex-direction: column; gap: 16px; margin-top: 4px; }
    .scenario-feature-card { display: flex; align-items: center; gap: 16px; background: #fff; border-radius: 18px; height: 72px; padding: 0 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); opacity: 0; transform: translateY(14px); transition: opacity 0.5s, transform 0.5s; }
    .scenario-feature-card.visible { opacity: 1; transform: translateY(0); }
    .scenario-feature-icon { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(to bottom right, #f3e8ff, #fce7f3); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .scenario-feature-icon svg { width: 18px; height: 18px; stroke: #9333ea; stroke-width: 2.5; fill: none; }
    .scenario-feature-text { font-size: 18px; font-weight: 500; line-height: 22px; color: rgba(0,0,0,0.8); }

    /* Pagination */
    .scenarios-pagination { display: flex; align-items: center; gap: 12px; }
    .pagination-btn { position: relative; width: 44px; height: 44px; cursor: pointer; border-radius: 50%; }
    .pagination-btn-inactive { width: 100%; height: 100%; border-radius: 50%; border: 1px solid rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; transition: border-color 0.2s; }
    .pagination-btn-inactive:hover { border-color: rgba(0,0,0,0.4); }
    .pagination-btn-inactive span { font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.3); letter-spacing: -0.05em; }
    .pagination-btn-active { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
    .pagination-btn-active span { font-size: 16px; font-weight: 600; color: #000; letter-spacing: -0.05em; z-index: 1; }
    .pagination-btn svg { position: absolute; inset: 0; width: 100%; height: 100%; transform: rotate(-90deg); }
    .pagination-btn circle.bg { fill: white; stroke: rgba(0,0,0,0.06); stroke-width: 2.5; }
    .pagination-btn circle.progress { fill: none; stroke: url(#progressGrad); stroke-width: 2.5; stroke-linecap: round; transition: stroke-dasharray 0.03s linear; }

    /* Scenarios Right */
    .scenarios-right { flex: 1; flex-shrink: 0; display: flex; align-items: center; height: 830px; }
    .scenarios-image-container { position: relative; width: 100%; height: 100%; overflow: hidden; border-radius: 16px; }
    .scenarios-image { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; transition: opacity 0.7s cubic-bezier(0.44,0,0.56,1), transform 0.7s cubic-bezier(0.44,0,0.56,1); }
    .scenarios-image img { height: 100%; width: auto; max-width: none; }
    .scenarios-image.entering { opacity: 0; transform: translateX(80px) scale(0.97); }
    .scenarios-image.active { opacity: 1; transform: translateX(0) scale(1); }
    .scenarios-image.exiting { opacity: 0; transform: translateX(-50px) scale(0.97); }

    /* ===== SECTION 3: APP ADVERT ===== */
    .app-advert-section { position: relative; width: 100%; height: 100vh; overflow: hidden; display: flex; align-items: center; }
    .app-advert-bg { position: absolute; inset: 0; background-size: cover; background-position: center; transition: opacity 0.6s ease-in-out; }
    .app-advert-overlay { position: absolute; inset: 0; background: linear-gradient(to right, rgba(0,0,0,0.6), rgba(0,0,0,0.3), transparent); }
    .app-advert-content { position: relative; z-index: 10; width: 100%; height: 100%; display: flex; align-items: center; padding: 64px; }
    .app-advert-inner { width: 100%; max-width: 1440px; margin: 0 auto; }
    .app-advert-text { display: flex; flex-direction: column; gap: 48px; max-width: 580px; }
    .app-advert-icon { width: 110px; height: 110px; border-radius: 28px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
    .app-advert-icon img { width: 100%; height: 100%; object-fit: cover; }
    .app-advert-heading-group { display: flex; flex-direction: column; gap: 36px; }
    .app-advert-heading { font-size: 78px; line-height: 82px; font-weight: 500; letter-spacing: -0.05em; color: #fff; transition: opacity 0.6s, transform 0.6s; }
    .app-advert-paragraph { font-size: 22px; line-height: 30px; font-weight: 500; letter-spacing: -0.03em; color: rgba(255,255,255,0.9); transition: opacity 0.5s 0.1s, transform 0.5s 0.1s; }
    .app-advert-cta { display: flex; align-items: center; gap: 8px; height: 66px; padding: 0 28px; border-radius: 20px; width: fit-content; cursor: pointer; background: linear-gradient(165deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%); transition: transform 0.2s, box-shadow 0.3s; }
    .app-advert-cta:hover { transform: scale(1.04); box-shadow: 0 8px 30px rgba(122,50,227,0.3); }
    .app-advert-cta:active { transform: scale(0.97); }
    .app-advert-cta svg { width: 32px; height: 32px; stroke: #fff; fill: none; stroke-width: 1.5; }
    .app-advert-cta span { font-size: 19px; line-height: 19px; font-weight: 500; letter-spacing: -0.02em; color: #fff; }

    /* ===== SECTION 4: PRICING ===== */
    .pricing-section { width: 100%; min-height: 100vh; background: #fff; display: flex; align-items: center; padding: 80px 0; }
    .pricing-inner { width: 100%; max-width: 1440px; margin: 0 auto; padding: 0 64px; }
    .pricing-header { display: flex; flex-direction: column; align-items: center; gap: 40px; }
    .pricing-title { font-size: 58px; font-weight: 500; line-height: 1; letter-spacing: -0.05em; color: #000; text-align: center; }

    /* Billing Toggle */
    .billing-toggle { display: flex; align-items: center; gap: 20px; justify-content: center; }
    .billing-toggle-label { font-size: 16px; font-weight: 500; line-height: 16px; color: #000; transition: opacity 0.3s; }
    .billing-toggle-label.active { opacity: 1; }
    .billing-toggle-label.inactive { opacity: 0.4; }
    .billing-toggle-track { position: relative; width: 52px; height: 32px; border-radius: 999px; padding: 3px; cursor: pointer; flex-shrink: 0; background: linear-gradient(135deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%); transition: box-shadow 0.2s; }
    .billing-toggle-track:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
    .billing-toggle-thumb { width: 26px; height: 26px; border-radius: 50%; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .billing-toggle-thumb.monthly { transform: translateX(20px); }

    /* Pricing Cards */
    .pricing-cards { margin-top: 72px; display: flex; flex-direction: row; gap: 24px; align-items: stretch; }
    .pricing-card { flex: 1; border-radius: 30px; overflow: hidden; display: flex; flex-direction: column; opacity: 0; transform: translateY(36px); transition: opacity 0.6s cubic-bezier(0.25,0.46,0.45,0.94), transform 0.6s cubic-bezier(0.25,0.46,0.45,0.94); }
    .pricing-card.visible { opacity: 1; transform: translateY(0); }
    .pricing-card-top { position: relative; display: flex; flex-direction: column; align-items: center; padding: 64px 48px 40px; gap: 28px; min-height: 400px; }
    .pricing-card-top.light { background-color: rgb(254, 241, 238); }
    .pricing-card-top.dark { background-color: #000; }
    .pricing-card-bottom { display: flex; flex-direction: column; padding: 40px 48px; flex: 1; }
    .pricing-card-bottom.light { background-color: rgb(252, 225, 224); }
    .pricing-card-bottom.dark { background-color: rgb(24, 24, 24); }

    /* Ribbon */
    .ribbon { position: absolute; top: 24px; right: -32px; z-index: 10; transform: rotate(45deg); }
    .ribbon-inner { padding: 7px 40px; text-align: center; background: linear-gradient(135deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%); }
    .ribbon-inner span { font-size: 13px; font-weight: 500; color: #fff; white-space: nowrap; }

    .pricing-plan-name { font-size: 56px; font-weight: 500; line-height: 1; letter-spacing: -0.05em; text-align: center; }
    .pricing-plan-name.light { color: #000; }
    .pricing-plan-name.dark { color: #fff; }
    .pricing-description { font-size: 18px; font-weight: 500; line-height: 22px; letter-spacing: -0.02em; text-align: center; }
    .pricing-description.light { color: rgba(0,0,0,0.8); }
    .pricing-description.dark { color: rgba(255,255,255,0.8); }

    .pricing-price { display: flex; align-items: center; gap: 12px; }
    .pricing-price-old { font-size: 38px; font-weight: 500; line-height: 30px; letter-spacing: -0.05em; text-decoration: line-through; }
    .pricing-price-old.dark { color: rgba(255,255,255,0.5); }
    .pricing-price-current { font-size: 38px; font-weight: 500; line-height: 30px; letter-spacing: -0.05em; transition: opacity 0.4s, transform 0.4s; }
    .pricing-price-current.light { color: rgba(0,0,0,0.5); }
    .pricing-price-current.light.contact { color: #000; }
    .pricing-price-current.dark { color: #fff; }
    .pricing-price-current.dark.discounted { color: #fff; }
    .pricing-price-current.dark.no-discount { color: rgba(255,255,255,0.5); }

    /* Pricing CTA buttons */
    .pricing-cta { display: flex; align-items: center; justify-content: center; gap: 10px; height: 66px; width: 100%; border-radius: 20px; padding: 0 28px; cursor: pointer; transition: transform 0.2s, box-shadow 0.3s; }
    .pricing-cta:hover { transform: scale(1.03); }
    .pricing-cta:active { transform: scale(0.97); }
    .pricing-cta.black { background: #000; }
    .pricing-cta.black:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
    .pricing-cta.gradient { background: linear-gradient(165deg, rgba(122,50,227,1) 0%, rgba(253,135,61,1) 100%); }
    .pricing-cta.gradient:hover { box-shadow: 0 8px 30px rgba(122,50,227,0.25); }
    .pricing-cta-circle { width: 30px; height: 30px; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.6); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .pricing-cta-circle svg { width: 15px; height: 15px; stroke: #fff; stroke-width: 2; fill: none; }
    .pricing-cta span { font-size: 19px; font-weight: 500; line-height: 19px; letter-spacing: -0.02em; color: #fff; }

    .pricing-subtext { font-size: 14px; font-weight: 500; line-height: 14px; text-align: center; transition: opacity 0.4s; }
    .pricing-subtext.light { color: rgba(0,0,0,0.5); }
    .pricing-subtext.dark { color: rgba(255,255,255,0.5); }

    /* Features list */
    .feature-list { display: flex; flex-direction: column; gap: 16px; }
    .feature-item { display: flex; align-items: center; gap: 14px; }
    .feature-check { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .feature-check.light { background: rgba(0,0,0,0.05); }
    .feature-check.dark { background: rgba(255,255,255,0.1); }
    .feature-check svg { width: 16px; height: 16px; stroke-width: 2.5; fill: none; }
    .feature-check.light svg { stroke: rgba(0,0,0,0.7); }
    .feature-check.dark svg { stroke: #fff; }
    .feature-text { font-size: 18px; font-weight: 500; line-height: 22px; letter-spacing: -0.02em; }
    .feature-text.light { color: rgba(0,0,0,0.8); }
    .feature-text.dark { color: #fff; }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
      .navbar { padding: 0 40px; }
      .navbar-links { display: none; }
      .navbar-actions { display: none; }
      .hero-content { flex-direction: column; padding: 80px 40px 80px; gap: 48px; }
      .hero-left { max-width: 100%; }
      .hero-heading { font-size: 64px; }
      .hero-right { width: 100%; }
      .scenarios-section { padding: 48px 40px; }
      .scenarios-inner { flex-direction: column; }
      .scenarios-left { width: 100%; height: auto; }
      .scenarios-right { height: 440px; width: 100%; }
      .scenarios-heading { font-size: 62px; }
      .scenarios-heading-container { height: 100px; }
      .scenarios-paragraph { font-size: 19px; }
      .scenarios-paragraph-container { height: 100px; }
      .app-advert-content { padding: 40px; }
      .app-advert-heading { font-size: 66px; line-height: 70px; }
      .app-advert-paragraph { font-size: 19px; line-height: 27px; }
      .pricing-inner { padding: 0 40px; }
      .pricing-cards { flex-direction: column; }
    }
    @media (max-width: 768px) {
      .navbar { padding: 0 20px; }
      .navbar-logo { width: 50px; height: 50px; border-radius: 16px; }
      .hero-content { padding: 64px 20px 64px; }
      .hero-heading { font-size: 44px; }
      .hero-paragraph { font-size: 16px; line-height: 24px; }
      .hero-ctas { flex-direction: column; align-items: flex-start; gap: 12px; }
      .cta-primary { height: 56px; padding: 0 24px; font-size: 17px; }
      .cta-secondary { height: 56px; padding: 0 28px; font-size: 17px; }
      .offer-strip { padding: 32px 20px; }
      .offer-text { flex-direction: column; gap: 12px; }
      .scenarios-section { padding: 40px 20px; }
      .scenarios-heading { font-size: 44px; }
      .scenarios-heading-container { height: 110px; }
      .scenarios-paragraph { font-size: 17px; }
      .scenarios-paragraph-container { height: 120px; }
      .scenarios-right { height: 320px; }
      .app-advert-content { padding: 24px; }
      .app-advert-icon { width: 80px; height: 80px; border-radius: 22px; }
      .app-advert-heading { font-size: 52px; line-height: 56px; }
      .app-advert-paragraph { font-size: 17px; line-height: 24px; }
      .app-advert-cta { height: 56px; padding: 0 24px; }
      .app-advert-cta svg { width: 28px; height: 28px; }
      .app-advert-cta span { font-size: 17px; }
      .pricing-inner { padding: 0 20px; }
      .pricing-title { font-size: 46px; }
      .pricing-card-top { padding: 56px 28px 40px; }
      .pricing-card-bottom { padding: 36px 28px; }
      .pricing-plan-name { font-size: 42px; }
    }
  </style>
</head>
<body>

  <!-- ===== SECTION 1: HERO ===== -->
  <section class="hero-section">
    <div class="hero-inner">
      <!-- Navbar -->
      <nav class="navbar">
        <div class="navbar-logo">
          <img src="https://framerusercontent.com/images/sXJWPys5DXyez95t6axrD3kbJkc.png" alt="Livo" />
        </div>
        <div class="navbar-links">
          <a href="#">How it works</a>
          <a href="#">Use cases</a>
          <a href="#">Features</a>
          <a href="#">Pricing</a>
          <a href="#">FAQ</a>
        </div>
        <div class="navbar-actions">
          <button class="navbar-btn">
            <svg viewBox="0 0 24 24"><path d="M5 12h14m0 0l-4-4m4 4l-4 4" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <button class="navbar-btn">
            <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </nav>

      <!-- Hero Content -->
      <div class="hero-content">
        <div class="hero-left animate-fade-in-up">
          <h1 class="hero-heading">
            <span class="hero-heading-line1" id="heroLine1"></span>
            <span class="hero-heading-line2" id="heroLine2"></span>
          </h1>
          <p class="hero-paragraph" id="heroParagraph"></p>
          <div class="hero-ctas">
            <div class="cta-primary-wrapper">
              <div class="cta-primary-border"><div class="cta-primary-border-inner"></div></div>
              <div class="cta-primary-bg"></div>
              <button class="cta-primary">
                <span class="cta-primary-circle">
                  <svg viewBox="0 0 14 14" fill="none"><path d="M3 7h8m0 0L8 4m3 3L8 10" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <span>Start for free</span>
              </button>
            </div>
            <button class="cta-secondary">Contact us</button>
          </div>
          <div class="trust-notes">
            <span>&bull; 31-day free trial</span>
            <span>&bull; No credit card required</span>
            <span>&bull; Cancel anytime</span>
          </div>
        </div>
        <div class="hero-right animate-fade-in-right">
          <div class="hero-image-container">
            <img src="https://framerusercontent.com/images/b4pOG23X1MeuH63d5Dmm4HFLVA.png" alt="Livo AI interface" />
          </div>
        </div>
      </div>

      <!-- Offer Strip -->
      <div class="offer-strip">
        <div class="offer-text">
          <span>Enjoy 50% off premium features for first 3 months — 21 days remaining</span>
          <a href="#">Start 14 days trial</a>
        </div>
        <div class="logo-ticker">
          <div class="logo-ticker-mask"></div>
          <div class="logo-ticker-track" id="logoTrack"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== SECTION 2: SCENARIOS ===== -->
  <section class="scenarios-section" id="scenariosSection">
    <div class="scenarios-inner">
      <div class="scenarios-left">
        <div class="scenarios-left-content">
          <span class="scenarios-label animate-fade-in">Scenarios</span>
          <div class="scenarios-heading-container">
            <h2 class="scenarios-heading" id="scenariosHeading"></h2>
          </div>
          <div class="scenarios-paragraph-container">
            <p class="scenarios-paragraph" id="scenariosParagraph"></p>
          </div>
          <div class="scenarios-features" id="scenariosFeatures"></div>
        </div>
        <div class="scenarios-pagination" id="scenariosPagination"></div>
      </div>
      <div class="scenarios-right">
        <div class="scenarios-image-container" id="scenariosImageContainer"></div>
      </div>
    </div>
  </section>

  <!-- ===== SECTION 3: APP ADVERT ===== -->
  <section class="app-advert-section" id="appAdvertSection">
    <div class="app-advert-bg" id="appAdvertBg1" style="background-image: url('https://framerusercontent.com/images/qnyDJGivgHQMm5JaWxQxdKn3q0.png'); opacity: 1;"></div>
    <div class="app-advert-bg" id="appAdvertBg2" style="background-image: url('https://polo-pecan-73837341.figma.site/_assets/v11/f71ca5dd250ff31df02f32da412dc606df352cc5.png?w=2191'); opacity: 0;"></div>
    <div class="app-advert-overlay"></div>
    <div class="app-advert-content">
      <div class="app-advert-inner">
        <div class="app-advert-text">
          <div class="app-advert-icon">
            <img src="https://framerusercontent.com/images/sXJWPys5DXyez95t6axrD3kbJkc.png" alt="Livo" />
          </div>
          <div class="app-advert-heading-group">
            <h2 class="app-advert-heading" id="appAdvertHeading">AI analysis</h2>
            <p class="app-advert-paragraph" id="appAdvertParagraph">Record meetings wherever you are with the Livo AI mobile app. From video calls to in-person conversations, effortlessly capture audio, generate live transcripts, and review actionable insights right from your phone.</p>
          </div>
          <button class="app-advert-cta">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 12l4 4 4-4M12 8v8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>Download App</span>
          </button>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== SECTION 4: PRICING ===== -->
  <section class="pricing-section" id="pricingSection">
    <div class="pricing-inner">
      <div class="pricing-header">
        <h2 class="pricing-title">Plans</h2>
        <div class="billing-toggle">
          <span class="billing-toggle-label active" id="yearlyLabel">Yearly</span>
          <div class="billing-toggle-track" id="billingToggle" onclick="toggleBilling()">
            <div class="billing-toggle-thumb" id="billingThumb"></div>
          </div>
          <span class="billing-toggle-label inactive" id="monthlyLabel">Monthly</span>
        </div>
      </div>
      <div class="pricing-cards" id="pricingCards"></div>
    </div>
  </section>

  <!-- SVG Defs for gradients -->
  <svg width="0" height="0" style="position:absolute">
    <defs>
      <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#9333ea"/>
        <stop offset="100%" stop-color="#ec4899"/>
      </linearGradient>
    </defs>
  </svg>

  <script>
    // ===== ANIMATED WORDS HELPER =====
    function animateWords(container, text, baseDelay = 0, staggerDelay = 0.05) {
      container.innerHTML = '';
      const words = text.split(' ');
      words.forEach((word, i) => {
        const span = document.createElement('span');
        span.className = 'animate-word';
        span.textContent = word + (i < words.length - 1 ? '\u00A0' : '');
        span.style.animationDelay = (baseDelay + i * staggerDelay) + 's';
        container.appendChild(span);
      });
    }

    // ===== HERO ANIMATED TEXT =====
    animateWords(document.getElementById('heroLine1'), 'AI analysis', 0.1, 0.05);
    animateWords(document.getElementById('heroLine2'), 'for real-time discussions', 0.25, 0.05);
    animateWords(document.getElementById('heroParagraph'), "Livo AI records your meetings, recognizes who's speaking, and provides real-time insights and live recommendations — all without taking manual notes.", 0.5, 0.02);

    // ===== LOGO TICKER =====
    const LOGOS = [
      { src: 'https://framerusercontent.com/images/Qo4XNTbEsI5VNAtleec5o3fWg.png', width: 210 },
      { src: 'https://framerusercontent.com/images/t6BIfZjwwbbizLquISVq96n6EGc.png', width: 210 },
      { src: 'https://framerusercontent.com/images/blfT46mvLdPrSwL7JUMxh1mUVI.png', width: 210 },
      { src: 'https://framerusercontent.com/images/zDwbpG7hVs2UTJsIh3Fwr3eX4E.png', width: 164 },
      { src: 'https://framerusercontent.com/images/F2VMPPEvVSp3zSIiTC7dXDzw.png', width: 210 },
    ];
    const logoTrack = document.getElementById('logoTrack');
    for (let r = 0; r < 3; r++) {
      LOGOS.forEach(logo => {
        const img = document.createElement('img');
        img.src = logo.src;
        img.style.width = logo.width + 'px';
        img.alt = '';
        logoTrack.appendChild(img);
      });
    }

    // ===== SECTION 2: SCENARIOS SLIDER =====
    const SCENARIO_SLIDES = [
      {
        heading: 'Talent & Hiring',
        paragraph: 'Run interviews more efficiently by capturing candidate answers automatically and to turn them into clear, useful insights.',
        features: ['Structured interviews with standardized questions', 'Clear insights and hiring recommendations', 'Automatic recording and transcription'],
        image: 'https://framerusercontent.com/images/J8MYD2sMAbepbr2MiuyxCmAYEgk.png',
      },
      {
        heading: 'Commercial Teams',
        paragraph: 'Record all customer interactions to ensure precise follow-ups and use insights to accelerate deal progression.',
        features: ['Track every customer touchpoint', 'Leverage insights to drive deals', 'Enable accurate follow-ups'],
        image: 'https://polo-pecan-73837341.figma.site/_assets/v11/56974c2f2a0bcc77e6331ef7df0ebdd1d7d4d377.png',
      },
      {
        heading: 'Management & Teams',
        paragraph: 'Capture decisions with speaker-tagged transcripts and receive automated summaries. Broadcast live sessions so everyone stays updated in real time.',
        features: ['Generate instant reports from the transcripts.', 'Keep the team updated in real time.'],
        image: 'https://polo-pecan-73837341.figma.site/_assets/v11/b1bded3078219cd54a5a2fef5cb4919c68e7c261.png',
      },
      {
        heading: 'Remote Team Members',
        paragraph: 'Remain focused during meetings as Livo AI provides real-time transcription. Quickly act on key points with clear summaries.',
        features: ['Capture every word instantly without manual note-taking.', 'Get concise, actionable insights from discussions.'],
        image: 'https://polo-pecan-73837341.figma.site/_assets/v11/1c14b7ac2dcdea9ad19040e054b91f33dd4ed3ec.png',
      },
    ];

    let scenarioActive = 0;
    let scenarioProgress = 0;
    let scenarioStartTime = Date.now();
    const SCENARIO_DURATION = 5000;

    function renderScenarioSlide(index) {
      const slide = SCENARIO_SLIDES[index];
      const headingEl = document.getElementById('scenariosHeading');
      const paragraphEl = document.getElementById('scenariosParagraph');
      const featuresEl = document.getElementById('scenariosFeatures');
      const imageContainer = document.getElementById('scenariosImageContainer');

      headingEl.style.opacity = '0';
      headingEl.style.transform = 'translateY(20px)';
      paragraphEl.style.opacity = '0';
      paragraphEl.style.transform = 'translateY(14px)';

      setTimeout(() => {
        headingEl.textContent = slide.heading;
        headingEl.style.opacity = '1';
        headingEl.style.transform = 'translateY(0)';
      }, 50);

      setTimeout(() => {
        paragraphEl.textContent = slide.paragraph;
        paragraphEl.style.opacity = '1';
        paragraphEl.style.transform = 'translateY(0)';
      }, 130);

      featuresEl.innerHTML = '';
      slide.features.forEach((feature, i) => {
        const card = document.createElement('div');
        card.className = 'scenario-feature-card';
        card.innerHTML = `
          <div class="scenario-feature-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <span class="scenario-feature-text">${feature}</span>
        `;
        featuresEl.appendChild(card);
        setTimeout(() => card.classList.add('visible'), 200 + i * 90);
      });

      // Image transition
      const existingImg = imageContainer.querySelector('.scenarios-image');
      if (existingImg) {
        existingImg.classList.remove('active');
        existingImg.classList.add('exiting');
        setTimeout(() => existingImg.remove(), 700);
      }
      const newImg = document.createElement('div');
      newImg.className = 'scenarios-image entering';
      newImg.innerHTML = `<img src="${slide.image}" alt="${slide.heading}" />`;
      imageContainer.appendChild(newImg);
      setTimeout(() => { newImg.classList.remove('entering'); newImg.classList.add('active'); }, 50);
    }

    function renderScenarioPagination() {
      const container = document.getElementById('scenariosPagination');
      container.innerHTML = '';
      SCENARIO_SLIDES.forEach((_, i) => {
        const btn = document.createElement('button');
        btn.className = 'pagination-btn';
        const label = String(i + 1).padStart(2, '0');
        if (i === scenarioActive) {
          btn.innerHTML = `
            <svg viewBox="0 0 44 44">
              <circle class="bg" cx="22" cy="22" r="20"/>
              <circle class="progress" cx="22" cy="22" r="20" stroke-dasharray="0 125.66" id="progressCircle${i}"/>
            </svg>
            <div class="pagination-btn-active"><span>${label}</span></div>
          `;
        } else {
          btn.innerHTML = `<div class="pagination-btn-inactive"><span>${label}</span></div>`;
        }
        btn.onclick = () => goToScenarioSlide(i);
        container.appendChild(btn);
      });
    }

    function goToScenarioSlide(index) {
      scenarioActive = index;
      scenarioProgress = 0;
      scenarioStartTime = Date.now();
      renderScenarioSlide(index);
      renderScenarioPagination();
    }

    // Init scenarios
    renderScenarioSlide(0);
    renderScenarioPagination();

    // Scenarios timer
    setInterval(() => {
      const elapsed = Date.now() - scenarioStartTime;
      scenarioProgress = Math.min(elapsed / SCENARIO_DURATION, 1);
      const circle = document.getElementById('progressCircle' + scenarioActive);
      if (circle) {
        circle.setAttribute('stroke-dasharray', `${scenarioProgress * 125.66} 125.66`);
      }
      if (scenarioProgress >= 1) {
        goToScenarioSlide((scenarioActive + 1) % SCENARIO_SLIDES.length);
      }
    }, 30);

    // ===== SECTION 3: APP ADVERT SLIDER =====
    const APP_ADVERT_SLIDES = [
      {
        bg: 'https://framerusercontent.com/images/qnyDJGivgHQMm5JaWxQxdKn3q0.png',
        heading: 'AI analysis',
        paragraph: 'Record meetings wherever you are with the Livo AI mobile app. From video calls to in-person conversations, effortlessly capture audio, generate live transcripts, and review actionable insights right from your phone.',
      },
      {
        bg: 'https://polo-pecan-73837341.figma.site/_assets/v11/f71ca5dd250ff31df02f32da412dc606df352cc5.png?w=2191',
        heading: 'In real-time mode',
        paragraph: 'Start using Livo AI to seamlessly capture your meetings, turn conversations into clear understanding, and easily share key takeaways with your team.',
      },
    ];

    let appAdvertActive = 0;
    const bg1 = document.getElementById('appAdvertBg1');
    const bg2 = document.getElementById('appAdvertBg2');
    const advertHeading = document.getElementById('appAdvertHeading');
    const advertParagraph = document.getElementById('appAdvertParagraph');

    function switchAppAdvertSlide() {
      appAdvertActive = (appAdvertActive + 1) % APP_ADVERT_SLIDES.length;
      const slide = APP_ADVERT_SLIDES[appAdvertActive];

      if (appAdvertActive === 0) {
        bg1.style.opacity = '1';
        bg2.style.opacity = '0';
      } else {
        bg1.style.opacity = '0';
        bg2.style.opacity = '1';
      }

      advertHeading.style.opacity = '0';
      advertHeading.style.transform = 'translateY(20px)';
      advertParagraph.style.opacity = '0';
      advertParagraph.style.transform = 'translateY(14px)';

      setTimeout(() => {
        advertHeading.textContent = slide.heading;
        advertHeading.style.opacity = '1';
        advertHeading.style.transform = 'translateY(0)';
      }, 150);
      setTimeout(() => {
        advertParagraph.textContent = slide.paragraph;
        advertParagraph.style.opacity = '1';
        advertParagraph.style.transform = 'translateY(0)';
      }, 250);
    }
    setInterval(switchAppAdvertSlide, 7000);

    // ===== SECTION 4: PRICING =====
    let isYearly = true;

    const PLANS = [
      {
        name: 'Individual',
        description: 'Well suited for beginning without any expenses.',
        price: '0\u20AC', monthlyPrice: '0\u20AC',
        oldPrice: null,
        cta: 'Free forever', variant: 'black',
        subtext: '0\u20AC per month', monthlySubtext: '0\u20AC per month',
        features: ['Mobile application', 'Auto transcript', 'Unlimited sessions', 'Unlimited contacts'],
        dark: false, ribbon: false,
      },
      {
        name: 'Advanced',
        description: 'Unlimited premium tools',
        price: '132\u20AC', monthlyPrice: '165\u20AC',
        oldPrice: '165\u20AC',
        cta: 'Free 14 days trial', variant: 'gradient',
        subtext: '132\u20AC per month, paid annually', monthlySubtext: '165\u20AC per month',
        features: ['Prompt modes', 'Team collaboration', 'Advanced summaries', 'Live time history'],
        dark: true, ribbon: true,
      },
      {
        name: 'Business',
        description: 'Tailored or self-managed solutions',
        price: 'Contact us', monthlyPrice: 'Contact us',
        oldPrice: null,
        cta: 'Request pricing', variant: 'black',
        subtext: "Schedule a short call \u2014 we'll set everything up for you.",
        monthlySubtext: "Schedule a short call \u2014 we'll set everything up for you.",
        features: ['Self-hosted options', 'HIPAA support', 'Custom LLMs', 'Priority support'],
        dark: false, ribbon: false,
      },
    ];

    function renderPricingCards() {
      const container = document.getElementById('pricingCards');
      container.innerHTML = '';
      PLANS.forEach((plan, i) => {
        const theme = plan.dark ? 'dark' : 'light';
        const displayPrice = isYearly ? plan.price : plan.monthlyPrice;
        const displaySubtext = isYearly ? plan.subtext : plan.monthlySubtext;
        const showOldPrice = isYearly && plan.oldPrice;

        let priceClass = `pricing-price-current ${theme}`;
        if (plan.dark && showOldPrice) priceClass += ' discounted';
        else if (plan.dark && !showOldPrice) priceClass += ' no-discount';
        if (!plan.dark && plan.price === 'Contact us') priceClass += ' contact';

        const card = document.createElement('div');
        card.className = 'pricing-card';
        card.style.transitionDelay = (i * 0.1) + 's';
        card.innerHTML = `
          <div class="pricing-card-top ${theme}">
            ${plan.ribbon ? '<div class="ribbon"><div class="ribbon-inner"><span>Top choice</span></div></div>' : ''}
            <h3 class="pricing-plan-name ${theme}">${plan.name}</h3>
            <p class="pricing-description ${theme}">${plan.description}</p>
            <div class="pricing-price">
              ${showOldPrice ? `<span class="pricing-price-old ${theme}">${plan.oldPrice}</span>` : ''}
              <span class="${priceClass}">${displayPrice}</span>
            </div>
            <button class="pricing-cta ${plan.variant}">
              <div class="pricing-cta-circle">
                <svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H7M17 7V17" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              <span>${plan.cta}</span>
            </button>
            <span class="pricing-subtext ${theme}">${displaySubtext}</span>
          </div>
          <div class="pricing-card-bottom ${theme}">
            <div class="feature-list">
              ${plan.features.map(f => `
                <div class="feature-item">
                  <div class="feature-check ${theme}">
                    <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </div>
                  <span class="feature-text ${theme}">${f}</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
        container.appendChild(card);
        setTimeout(() => card.classList.add('visible'), 100 + i * 100);
      });
    }

    function toggleBilling() {
      isYearly = !isYearly;
      const thumb = document.getElementById('billingThumb');
      const yearlyLabel = document.getElementById('yearlyLabel');
      const monthlyLabel = document.getElementById('monthlyLabel');

      if (isYearly) {
        thumb.classList.remove('monthly');
        yearlyLabel.classList.add('active');
        yearlyLabel.classList.remove('inactive');
        monthlyLabel.classList.add('inactive');
        monthlyLabel.classList.remove('active');
      } else {
        thumb.classList.add('monthly');
        yearlyLabel.classList.add('inactive');
        yearlyLabel.classList.remove('active');
        monthlyLabel.classList.add('active');
        monthlyLabel.classList.remove('inactive');
      }
      renderPricingCards();
    }

    renderPricingCards();

    // ===== INTERSECTION OBSERVER FOR SCROLL ANIMATIONS =====
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1, rootMargin: '-40px' });

    document.querySelectorAll('.pricing-card').forEach(el => observer.observe(el));
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*