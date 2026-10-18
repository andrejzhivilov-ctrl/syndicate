---
title: "Unwind Hero"
template_id: "3de30350-1073-4237-a73f-46b14fbfa01f"
section: "sites"
category_slug: "hero"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Unwind Hero

> **Секція:** `SITES` | **Категорія:** `hero`  
> **ID шаблону:** `3de30350-1073-4237-a73f-46b14fbfa01f`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Hero



### 🖼 Прев'ю:
![Unwind Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/ace51579-e1f0-4761-be02-d5f548b5401a.webp)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
PROMPT:
Recreate the WoodNest hero section exactly as a React + Tailwind CSS + Framer Motion component.

Use font family "PP Mori" for the entire hero. Define @font-face for PP Mori normal weight 400 and semibold weight 600 using the existing embedded WOFF/WOFF2 data from src/styles/fonts.css. Set base html font size to 16px.

The page is a full viewport hero:
- Root wrapper: relative, min-height: 100vh, width: 100%, overflow hidden, font PP Mori, font weight 400.
- Background: absolute full-screen video, inset 0, width/height 100%, object-cover.
- Video attributes: autoPlay, muted, playsInline. Do not loop unless explicitly requested.
- Exact video URL:
https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260620_140846_aef8cb19-5ec8-4b45-974b-020aed20f297.mp4

Header:
- Position relative, z-index 20.
- Display flex, align center, justify-between.
- Desktop padding: top 60px, left/right 65px.
- Tablet/mobile padding: px 32px / 16px, top 45px / 30px.
- Left: exact WoodNest SVG logo, 142px wide, 50px tall, white wordmark with warm yellow/orange mark (#FFB33F) and 0.6 opacity gradient details.
- Center/right desktop nav hidden below md.
- Nav items: Locations, Rooms, Experiences, Contact.
- Nav gap desktop 44px, text white, PP Mori normal, 16px, line-height 24px.
- Nav hover animation: opacity to 0.6, tap scale 0.96, duration 0.15.
- Book Now button: white background, black text, PP Mori semibold 16px/24px, padding 12px 32px, border-radius 10px.
- Button hover: scale 1.04 and background #f0f0f0. Tap scale 0.97. Transition duration 0.18 easeOut.
- Mobile: show Menu/X icon button in white, 24px. Open menu is absolute below header, left/right 0, margin x 16px, margin-top 8px, background #2a3349, border-radius 16px, padding 24px, flex column gap 16px, shadow-xl, z-index 50.

Hero main:
- Position relative, z-index 10.
- Padding desktop: 64px 65px 60px.
- Padding tablet/mobile: top 40px/24px, x 32px/16px, bottom 56px/40px.
- min-height: calc(100vh - 110px).
- Display flex column.
- Inner layout: flex-1, flex column on mobile, flex row on lg, lg align-stretch, gap 40px mobile, 0 desktop.

Left content:
- Flex column, justify-between, flex-1.
- H1: PP Mori normal, white, tracking-tight.
- Font size: clamp(52px, 9vw, 128px).
- Line height: 0.82.
- Three block lines:
  1. "Nature's" in white
  2. "Perfect" in white at 50% opacity
  3. "Hideaways" in white
- Animate each line with fade-up:
  initial opacity 0, y 28
  animate opacity 1, y 0
  transition duration 0.7, ease [0.22, 1, 0.36, 1]
  delays: 0.2, 0.35, 0.5

Bottom left row:
- margin-top 40px on small screens, 0 on lg.
- Flex column on mobile, row on sm/lg.
- align-start, gap 32px; desktop lg gap 0.
- Description paragraph:
  text: "Discover handpicked luxury cabins in breathtaking locations. Unplug, unwind, and reconnect with what matters most."
  PP Mori normal, color white/80, line-height 24px.
  Width 300px on sm/lg, full width on mobile.
  Font size clamp(15px, 1.3vw, 18px).
  Fade-up delay 0.65.
- Rating block:
  flex column gap 8px.
  sm margin-left 32px, lg margin-left 140px.
  First row flex align-center gap 4px.
  Star icon: 28px square, fill #FFB33F, use the same star SVG path from the existing component.
  Rating text "4.7": white, PP Mori normal, 36px, line-height 34px.
  Caption text: " from 1,800+ stays", white, PP Mori normal, 20px, line-height 24px.
  Fade-up delay 0.75.

Right reserve card:
- Wrapper animates from right:
  initial opacity 0, x 40
  animate opacity 1, x 0
  transition duration 0.8, ease [0.22, 1, 0.36, 1], delay 0.4
- Layout wrapper: flex; on lg flex-col justify-end; lg padding-left 40px, xl padding-left 64px.
- Card: relative, width 100%, max-width 410px, border-radius 35px, padding 30px, flex column, gap 30px.
- Add two absolute inset layers inside card:
  1. backdrop blur layer: inset 0, backdrop-filter blur(12.5px), border-radius 35px, pointer-events none.
  2. tint layer: inset 0, background rgba(0,0,0,0.25), mix-blend-mode soft-light, border-radius 35px, pointer-events none.

Reserve card content:
- Title row: relative flex, align-start, justify-between, gap 16px.
- Cabin title: PP Mori normal, white, 32px, line-height 36px, width 280px, two lines:
  "Evergreen "
  "Pine Family Lodge"
- Edit icon circle: background rgba(0,0,0,0.35), size 40px, border-radius 9999px, centered. Icon is 20px, stroke #BDC6C7 at 40% opacity using the existing SVG paths.
- Date row:
  Two equal pills in a flex row gap 10px.
  Each pill button: width 100%, background rgba(0,0,0,0.35), display flex, gap 6px, align center, padding 16px, border-radius 10px.
  Text: white, PP Mori normal, 16px/24px, flex-1, text-left.
  Values: "Feb 11" and "Mar 25".
  Calendar icon 20px, stroke #515C62. Chevron icon 16px, stroke #515C62.
  Hover: background rgba(0,0,0,0.5), scale 1.02. Tap scale 0.97. Duration 0.18 easeOut.
  When open, add ring 1px white/20 and rotate chevron 180deg over 0.2s.
- Dropdown calendar:
  absolute top calc(100% + 8px), left/right 0, z-index 50, border-radius 16px, overflow hidden, padding 16px.
  Background rgba(30,38,60,0.97), backdrop-filter blur(16px).
  Month label centered, white/60, 13px/20px, margin-bottom 12px, tracking-wide.
  Grid 7 columns, vertical gap 4px. Weekday labels white/30, 11px/20px.
  Day buttons 13px/20px, height 28px, border-radius 8px. Selected day white background, text #34405c, semibold.
  Calendar months: February 2025, 28 days, starts after 6 blanks; March 2025, 31 days, starts after 6 blanks.
- Time info box:
  background rgba(0,0,0,0.35), height 73px, border-radius 10px, overflow hidden, position relative.
  Left label: "Check-in", x 16px, top 16px, PP Mori normal, 14px/16px, color #bdc6c7, opacity .4.
  Left value: "After 2:00 PM", x 16px, top 34px, white, 16px/24px.
  Right label: "Check-out", right 16px, top 16px, same label style.
  Right value: "Until 12:00 PM", right 16px, top 34px, white, 16px/24px.
  Center divider: vertical line, height 44px, width 1px, background #515C62, opacity .4, centered horizontally.
- Price row:
  flex column gap 24px.
  Price/guest line: flex align-end justify-between, no wrapping.
  Price: "$359" white, 32px, line-height 28px; "/night" color #515c62, 20px.
  Guest text: "2-5 guests", white, 14px/16px.
- Reserve button:
  width 100%, height 48px, background white, border-radius 10px, centered.
  Text "Reserve", PP Mori semibold, black, 16px/24px.
  Hover scale 1.03 and background #f0f0f0. Tap scale 0.97. Duration 0.18 easeOut.

Global animation helpers:
fadeUp(delay):
initial { opacity: 0, y: 28 }
animate { opacity: 1, y: 0 }
transition { duration: 0.7, ease: [0.22, 1, 0.36, 1], delay }

fadeDown(delay):
initial { opacity: 0, y: -20 }
animate { opacity: 1, y: 0 }
transition { duration: 0.6, ease: [0.22, 1, 0.36, 1], delay }

fadeRight(delay):
initial { opacity: 0, x: 40 }
animate { opacity: 1, x: 0 }
transition { duration: 0.8, ease: [0.22, 1, 0.36, 1], delay }

At a 1545x997 viewport, the rendered desktop geometry should approximately be:
- Header: x 0, y 0, w 1545, h 110, padding 60px 65px 0.
- Main: x 0, y 110, w 1545, h 887, padding 64px 65px 60px.
- H1: x 65, y 174, w about 955, h 315. Font 128px, line-height 104.96px.
- Description: x 65, y 841, w 300, h 96.
- Rating value row: x 505, y 841.
- Reserve card: x about 1084, y 502, w about 396 rendered at this viewport, h 436, padding 30px, radius 35px.

Do not add extra overlays, gradients, cards, marketing sections, or explanatory text. The hero should be the first screen and match this exact composition.

SOURCE CODE:
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WoodNest | Nature's Perfect Hideaways</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html { font-size: 16px; }

    body {
      font-family: 'PP Mori', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-weight: 400;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
    }

    /* Hero wrapper */
    .hero {
      position: relative;
      min-height: 100vh;
      width: 100%;
      overflow: hidden;
    }

    .hero-video {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    /* Header */
    .header {
      position: relative;
      z-index: 20;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 60px 65px 0;
      opacity: 0;
      transform: translateY(-20px);
      animation: fadeDown 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0s forwards;
    }

    .nav { display: flex; align-items: center; gap: 44px; }
    .nav a {
      color: white;
      text-decoration: none;
      font-size: 16px;
      line-height: 24px;
      transition: opacity 0.15s;
    }
    .nav a:hover { opacity: 0.6; }

    .btn-book {
      background: white;
      color: black;
      font-weight: 600;
      font-size: 16px;
      line-height: 24px;
      padding: 12px 32px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      transition: transform 0.18s ease-out, background 0.18s ease-out;
    }
    .btn-book:hover { transform: scale(1.04); background: #f0f0f0; }
    .btn-book:active { transform: scale(0.97); }

    .mobile-menu-btn {
      display: none;
      background: none;
      border: none;
      color: white;
      cursor: pointer;
    }

    /* Main */
    .hero-main {
      position: relative;
      z-index: 10;
      padding: 64px 65px 60px;
      min-height: calc(100vh - 110px);
    }

    .hero-inner {
      display: flex;
      flex-direction: row;
      align-items: stretch;
      gap: 0;
      min-height: calc(100vh - 234px);
    }

    /* Left content */
    .hero-left {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .hero-title {
      font-weight: 400;
      color: white;
      letter-spacing: -0.02em;
      font-size: clamp(52px, 9vw, 128px);
      line-height: 0.82;
    }

    .hero-title span {
      display: block;
      opacity: 0;
      transform: translateY(28px);
    }
    .hero-title span:nth-child(1) { animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.2s forwards; }
    .hero-title span:nth-child(2) { animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.35s forwards; }
    .hero-title span:nth-child(3) { animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.5s forwards; }
    .hero-title .dim { opacity: 0; }
    .hero-title .dim.animated { opacity: 0.5 !important; }

    .hero-bottom {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
      gap: 0;
    }

    .hero-desc {
      color: rgba(255,255,255,0.8);
      line-height: 24px;
      font-size: clamp(15px, 1.3vw, 18px);
      width: 300px;
      opacity: 0;
      transform: translateY(28px);
      animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.65s forwards;
    }

    .hero-rating {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-left: 140px;
      opacity: 0;
      transform: translateY(28px);
      animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.75s forwards;
    }

    .rating-row { display: flex; align-items: center; gap: 4px; }
    .rating-value { color: white; font-size: 36px; line-height: 34px; }
    .rating-caption { color: white; font-size: 20px; line-height: 24px; }

    /* Right reserve card */
    .card-wrapper {
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding-left: 40px;
      opacity: 0;
      transform: translateX(40px);
      animation: fadeRight 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.4s forwards;
    }

    .reserve-card {
      position: relative;
      width: 100%;
      max-width: 410px;
      border-radius: 35px;
      padding: 30px;
      display: flex;
      flex-direction: column;
      gap: 30px;
    }

    .card-blur {
      position: absolute;
      inset: 0;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      background: rgba(255,255,255,0.06);
      border-radius: 35px;
      pointer-events: none;
    }

    .card-tint {
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0.25);
      border-radius: 35px;
      pointer-events: none;
    }

    /* Card content */
    .card-header {
      position: relative;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
    }

    .cabin-title {
      color: white;
      font-size: 32px;
      line-height: 36px;
      width: 280px;
      font-weight: 400;
    }

    .edit-icon {
      width: 40px;
      height: 40px;
      border-radius: 9999px;
      background: rgba(0,0,0,0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .date-row {
      position: relative;
      display: flex;
      gap: 10px;
    }

    .date-pill {
      flex: 1;
      position: relative;
    }

    .date-btn {
      width: 100%;
      background: rgba(0,0,0,0.35);
      display: flex;
      gap: 6px;
      align-items: center;
      padding: 16px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      transition: background 0.18s ease-out, transform 0.18s ease-out;
    }
    .date-btn:hover { background: rgba(0,0,0,0.5); transform: scale(1.02); }
    .date-btn:active { transform: scale(0.97); }
    .date-btn.open { box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2); }

    .date-btn span {
      color: white;
      font-size: 16px;
      line-height: 24px;
      flex: 1;
      text-align: left;
    }

    .chevron {
      transition: transform 0.2s;
    }
    .chevron.rotated { transform: rotate(180deg); }

    /* Calendar dropdown */
    .calendar-dropdown {
      position: absolute;
      top: calc(100% + 8px);
      left: 0;
      right: 0;
      z-index: 50;
      border-radius: 16px;
      overflow: hidden;
      padding: 16px;
      background: rgba(30,38,60,0.97);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      display: none;
      animation: dropIn 0.2s ease forwards;
    }
    .calendar-dropdown.visible { display: block; }

    .cal-month {
      text-align: center;
      color: rgba(255,255,255,0.6);
      font-size: 13px;
      line-height: 20px;
      margin-bottom: 12px;
      letter-spacing: 0.05em;
    }

    .cal-grid {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      row-gap: 4px;
    }

    .cal-weekday {
      text-align: center;
      color: rgba(255,255,255,0.3);
      font-size: 11px;
      line-height: 20px;
    }

    .cal-day {
      text-align: center;
      font-size: 13px;
      line-height: 20px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      color: white;
      border: none;
      background: none;
      cursor: pointer;
    }
    .cal-day:hover { background: rgba(255,255,255,0.1); }
    .cal-day.selected {
      background: white;
      color: #34405c;
      font-weight: 600;
    }

    /* Time info */
    .time-info {
      position: relative;
      background: rgba(0,0,0,0.35);
      height: 73px;
      border-radius: 10px;
      overflow: hidden;
    }

    .time-label {
      position: absolute;
      top: 16px;
      font-size: 14px;
      line-height: 16px;
      color: #bdc6c7;
      opacity: 0.4;
    }
    .time-label.left { left: 16px; }
    .time-label.right { right: 16px; }

    .time-value {
      position: absolute;
      top: 34px;
      color: white;
      font-size: 16px;
      line-height: 24px;
    }
    .time-value.left { left: 16px; }
    .time-value.right { right: 16px; }

    .time-divider {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 1px;
      height: 44px;
      background: #515C62;
      opacity: 0.4;
    }

    /* Price */
    .price-section {
      position: relative;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .price-row {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: nowrap;
    }

    .price-amount { color: white; font-size: 32px; line-height: 28px; }
    .price-unit { color: #515c62; font-size: 20px; }
    .price-guests { color: white; font-size: 14px; line-height: 16px; }

    .btn-reserve {
      width: 100%;
      height: 48px;
      background: white;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      font-weight: 600;
      font-size: 16px;
      line-height: 24px;
      color: black;
      transition: transform 0.18s ease-out, background 0.18s ease-out;
    }
    .btn-reserve:hover { transform: scale(1.03); background: #f0f0f0; }
    .btn-reserve:active { transform: scale(0.97); }

    /* Animations */
    @keyframes fadeUp {
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeDown {
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeRight {
      to { opacity: 1; transform: translateX(0); }
    }
    @keyframes dropIn {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Responsive */
    @media (max-width: 1023px) {
      .hero-inner { flex-direction: column; gap: 40px; }
      .card-wrapper { padding-left: 0; }
      .hero-bottom { flex-direction: column; gap: 32px; }
      .hero-rating { margin-left: 0; }
      .hero-desc { width: 100%; }
    }

    @media (max-width: 767px) {
      .header { padding: 30px 16px 0; }
      .nav { display: none; }
      .mobile-menu-btn { display: block; }
      .hero-main { padding: 24px 16px 40px; }
    }

    @media (min-width: 768px) and (max-width: 1023px) {
      .header { padding: 45px 32px 0; }
      .hero-main { padding: 40px 32px 56px; }
    }

    @media (min-width: 640px) and (max-width: 1023px) {
      .hero-bottom { flex-direction: row; gap: 32px; }
      .hero-rating { margin-left: 32px; }
      .hero-desc { width: 300px; }
    }

    @media (min-width: 1280px) {
      .card-wrapper { padding-left: 64px; }
    }

    /* Mobile menu */
    .mobile-nav {
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin: 8px 16px 0;
      background: #2a3349;
      border-radius: 16px;
      padding: 24px;
      flex-direction: column;
      gap: 16px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.3);
      z-index: 50;
    }
    .mobile-nav.open { display: flex; }
    .mobile-nav a {
      color: white;
      text-decoration: none;
      font-size: 16px;
      line-height: 24px;
    }
    .mobile-nav button {
      width: 100%;
      background: white;
      color: black;
      font-weight: 600;
      font-size: 16px;
      padding: 12px 32px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="hero">
    <video class="hero-video" autoplay muted playsinline>
      <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260620_140846_aef8cb19-5ec8-4b45-974b-020aed20f297.mp4" type="video/mp4" />
    </video>

    <!-- Header -->
    <header class="header">
      <svg width="142" height="50" viewBox="0 0 142 50" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="25" r="14" fill="#FFB33F"/>
        <circle cx="20" cy="25" r="8" fill="#FFB33F" fill-opacity="0.6"/>
        <path d="M20 11 L20 39" stroke="white" stroke-width="2" stroke-linecap="round"/>
        <path d="M14 18 L20 25 L26 18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12 25 L20 33 L28 25" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>
        <text x="42" y="32" fill="white" font-family="PP Mori, sans-serif" font-size="22" font-weight="400" letter-spacing="-0.5">WoodNest</text>
      </svg>

      <nav class="nav">
        <a href="#">Locations</a>
        <a href="#">Rooms</a>
        <a href="#">Experiences</a>
        <a href="#">Contact</a>
        <button class="btn-book">Book Now</button>
      </nav>

      <button class="mobile-menu-btn" onclick="toggleMenu()">
        <svg id="menu-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
        <svg id="close-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>

      <div class="mobile-nav" id="mobile-nav">
        <a href="#">Locations</a>
        <a href="#">Rooms</a>
        <a href="#">Experiences</a>
        <a href="#">Contact</a>
        <button>Book Now</button>
      </div>
    </header>

    <!-- Main -->
    <main class="hero-main">
      <div class="hero-inner">
        <!-- Left -->
        <div class="hero-left">
          <h1 class="hero-title">
            <span>Nature's</span>
            <span class="dim">Perfect</span>
            <span>Hideaways</span>
          </h1>

          <div class="hero-bottom">
            <p class="hero-desc">Discover handpicked luxury cabins in breathtaking locations. Unplug, unwind, and reconnect with what matters most.</p>

            <div class="hero-rating">
              <div class="rating-row">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="#FFB33F"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                <span class="rating-value">4.7</span>
              </div>
              <span class="rating-caption"> from 1,800+ stays</span>
            </div>
          </div>
        </div>

        <!-- Right card -->
        <div class="card-wrapper">
          <div class="reserve-card">
            <div class="card-blur"></div>
            <div class="card-tint"></div>

            <div class="card-header">
              <h2 class="cabin-title">Evergreen<br>Pine Family Lodge</h2>
              <div class="edit-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#BDC6C7" stroke-opacity="0.4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </div>
            </div>

            <div class="date-row">
              <div class="date-pill">
                <button class="date-btn" id="checkin-btn" onclick="toggleCalendar('checkin')">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#515C62" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  <span>Feb 11</span>
                  <svg class="chevron" id="chevron-checkin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#515C62" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                </button>
                <div class="calendar-dropdown" id="cal-checkin">
                  <p class="cal-month">FEBRUARY 2025</p>
                  <div class="cal-grid" id="cal-grid-checkin"></div>
                </div>
              </div>

              <div class="date-pill">
                <button class="date-btn" id="checkout-btn" onclick="toggleCalendar('checkout')">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#515C62" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  <span>Mar 25</span>
                  <svg class="chevron" id="chevron-checkout" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#515C62" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                </button>
                <div class="calendar-dropdown" id="cal-checkout">
                  <p class="cal-month">MARCH 2025</p>
                  <div class="cal-grid" id="cal-grid-checkout"></div>
                </div>
              </div>
            </div>

            <div class="time-info">
              <span class="time-label left">Check-in</span>
              <span class="time-value left">After 2:00 PM</span>
              <div class="time-divider"></div>
              <span class="time-label right">Check-out</span>
              <span class="time-value right">Until 12:00 PM</span>
            </div>

            <div class="price-section">
              <div class="price-row">
                <div>
                  <span class="price-amount">$359</span>
                  <span class="price-unit">/night</span>
                </div>
                <span class="price-guests">2-5 guests</span>
              </div>
              <button class="btn-reserve">Reserve</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <script>
    // Animate dim line to 0.5 opacity after fadeUp completes
    setTimeout(() => {
      document.querySelector('.hero-title .dim').classList.add('animated');
    }, 1050);

    // Mobile menu toggle
    function toggleMenu() {
      const nav = document.getElementById('mobile-nav');
      const menuIcon = document.getElementById('menu-icon');
      const closeIcon = document.getElementById('close-icon');
      const isOpen = nav.classList.contains('open');
      nav.classList.toggle('open');
      menuIcon.style.display = isOpen ? 'block' : 'none';
      closeIcon.style.display = isOpen ? 'none' : 'block';
    }

    // Calendar logic
    const weekdays = ['Su','Mo','Tu','We','Th','Fr','Sa'];
    const calendars = {
      checkin: { days: 28, startBlanks: 6, selectedDay: 11 },
      checkout: { days: 31, startBlanks: 6, selectedDay: 25 }
    };

    function buildCalendar(type) {
      const grid = document.getElementById('cal-grid-' + type);
      const config = calendars[type];
      grid.innerHTML = '';

      weekdays.forEach(d => {
        const span = document.createElement('span');
        span.className = 'cal-weekday';
        span.textContent = d;
        grid.appendChild(span);
      });

      for (let i = 0; i < config.startBlanks; i++) {
        grid.appendChild(document.createElement('span'));
      }

      for (let day = 1; day <= config.days; day++) {
        const btn = document.createElement('button');
        btn.className = 'cal-day' + (day === config.selectedDay ? ' selected' : '');
        btn.textContent = day;
        grid.appendChild(btn);
      }
    }

    buildCalendar('checkin');
    buildCalendar('checkout');

    let openCalendar = null;

    function toggleCalendar(type) {
      const cal = document.getElementById('cal-' + type);
      const btn = document.getElementById(type + '-btn');
      const chevron = document.getElementById('chevron-' + type);

      if (openCalendar === type) {
        cal.classList.remove('visible');
        btn.classList.remove('open');
        chevron.classList.remove('rotated');
        openCalendar = null;
      } else {
        // Close other
        if (openCalendar) {
          document.getElementById('cal-' + openCalendar).classList.remove('visible');
          document.getElementById(openCalendar + '-btn').classList.remove('open');
          document.getElementById('chevron-' + openCalendar).classList.remove('rotated');
        }
        cal.classList.add('visible');
        btn.classList.add('open');
        chevron.classList.add('rotated');
        openCalendar = type;
      }
    }
  </script>
</body>
</html>
```

---
*NeuroFlow Academy Site Templates*