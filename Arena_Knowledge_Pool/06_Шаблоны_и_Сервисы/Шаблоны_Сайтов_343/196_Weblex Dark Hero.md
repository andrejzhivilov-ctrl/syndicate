---
title: "Weblex Dark Hero"
template_id: "6a551ca9-6df9-4ddf-89ad-0060a68f48cd"
section: "sites"
category_slug: "landing"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Weblex Dark Hero

> **Секція:** `SITES` | **Категорія:** `landing`  
> **ID шаблону:** `6a551ca9-6df9-4ddf-89ad-0060a68f48cd`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
Landing Page

### 🖼 Прев'ю:
![Weblex Dark Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/62d1860e-4fcc-4fad-a7f0-a70d42e44ee6.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a dark, full-screen hero section with a background video and a transparent navbar.

Navbar:

Fixed at the top, fully transparent (no blur, no border, no background)

Left: Brand name "Weblex." with a green dot accent using the primary color

Center (desktop): Navigation links — Home, Features, Pricing, About — in muted foreground color, small text

Right (desktop): "Get Started" button — primary color background, dark text, rounded-full, small text

Mobile: Hamburger menu icon that toggles a dropdown with the same links and button

Hero Section:

Full viewport height (h-screen)

Background video playing on autoplay, loop, muted, playsInline, covering the full section with object-cover

Video URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260221_085953_8463b46e-ba85-4bb7-912a-1feaf346e970.mp4

Video has a seamless loop transition: fades out to black starting 1.5 seconds before the end (reaching opacity 0 by 0.3s before the end), then fades back in over the first 1 second when the video restarts. Use requestAnimationFrame for smooth opacity updates.

No dark overlay on the video — full opacity

Content is aligned to the bottom of the screen with 100px bottom padding, centered horizontally, max-width 603px

Hero Content (bottom-aligned, centered):

Badge: A small pill/badge that says "Introducing Smart Website Builder" — styled with a border, rounded-full, small text, muted foreground color

Heading: "Turn your big idea into a stunning website" — 62px font size, font-medium, centered, line-height 1.1. Responsive: 48px on medium, 36px on small screens

Paragraph: "Fintech is its potential to promote financial inclusion. In many parts of the world, millions of people lack access to traditional banking services." — muted foreground color, centered, max-width 520px

Two buttons side by side:

"Get Started Now" — primary color background, dark text, rounded-full, with an ArrowUpRight icon on the left, 18px text, hover brightness effect

"See Pricing" — secondary (white) background, dark text, rounded-full, 18px text

Color Theme (dark mode only, HSL values in CSS variables):

--background: 240 67% 1% (near-black)

--foreground: 0 0% 100% (white)

--primary: 73 98% 57% (bright lime green)

--primary-foreground: 240 67% 1% (dark)

--secondary: 0 0% 100% (white)

--secondary-foreground: 240 67% 1% (dark)

--muted: 240 10% 12%

--muted-foreground: 0 0% 82% / 0.8

--border: 0 0% 100% / 0.1

Tech: React, TypeScript, Tailwind CSS, Lucide icons for ArrowUpRight and Menu/X icons.
```

---
*NeuroFlow Academy Site Templates*