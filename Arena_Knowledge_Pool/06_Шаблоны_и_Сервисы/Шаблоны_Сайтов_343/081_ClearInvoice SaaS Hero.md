---
title: "ClearInvoice SaaS Hero"
template_id: "8e9956fa-ae56-4515-b94d-7bc7b204d915"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 ClearInvoice SaaS Hero

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `8e9956fa-ae56-4515-b94d-7bc7b204d915`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![ClearInvoice SaaS Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/f1d8b54d-c373-4e3e-947c-d1b216e33e3a.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a high-fidelity, dark-mode Hero section for a SaaS product called "ClearInvoice" using React and Tailwind CSS.

Tech Stack:
Framework: React (Vite)
Styling: Tailwind CSS
Animation: motion/react (Framer Motion)
Icons: lucide-react
Video: Native HTML5 <video> with hls.js for streaming (Do NOT use react-player).

1. Background Video (Crucial):
Source: https://stream.mux.com/hUT6X11m1Vkw1QMxPOLgI761x2cfpi9bHFbi5cNg4014.m3u8
Behavior: Autoplay, Loop, Muted, PlaysInline.
Opacity: 100% (No dark overlay).
Implementation: Create a memoized BackgroundVideo component using hls.js to handle the .m3u8 stream natively. Ensure it cleans up properly on unmount to prevent "AbortError".
Z-Index: It must sit behind all content (-z-10).

2. Layout & Styling:
Font Family:
Headings: "Switzer" (Medium weight, tight tracking).
Body: "Geist" (Clean, legible).

Top Bar: A 5px high gradient bar at the very top: from-[#ccf] via-[#e7d04c] to-[#31fb78].
Navbar:
Logo on left.
Links (Features, Pricing, Reviews) centered.
Auth buttons (Sign In, Sign Up) on right.
Mobile: Hamburger menu that opens a full-width dropdown.

3. Hero Content:
Headline: "Manage your online store while save 3x operating cost" (Large text: text-6xl, tight leading).
Subhead: "ClearInvoice takes the hassle out of billing with easy-to-use tools." (White/90).
Animations: Use motion/react to stagger the entrance of the Text, Buttons, and Social Proof (Fade Up + Slide).

4. Button Styles (Exact Recreation):
Primary Button:
Background: Gradient from-[#FF3300] to-[#EE7926].
Glow: An absolute positioned div behind the button with bg-orange-600 blur-lg opacity-20.
Inner Stroke: A 1.5px border overlay (border-white/20) inside the button for a "glassy" edge.
Hover: scale: 1.05, glow increases to opacity-60, and an Arrow icon slides in from the left.

Secondary Button:
Background: bg-white/90 backdrop blur.
Inner Stroke: 1.5px border (border-black/5).
Hover: scale: 1.05, background becomes solid white.

5. Social Proof:
Row of 3 user avatars (overlapping borders).
Text: "Trusted by 210k+ stores worldwide".
```

---
*NeuroFlow Academy Site Templates*