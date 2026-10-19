---
title: "Datacore SaaS Hero"
template_id: "4e7ef818-22b8-4fed-91f5-86e4429f5d8e"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Datacore SaaS Hero

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `4e7ef818-22b8-4fed-91f5-86e4429f5d8e`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![Datacore SaaS Hero](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/45dfb28b-3645-47fa-b0d6-5c8ce6cf7132.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Build a high-fidelity, production-ready Hero section for a SaaS product called "Datacore" using React, Tailwind CSS, and Lucide Icons.

### Design Style
- **Theme:** Dark mode, modern, clean, "Linear-style" aesthetic.
- **Background:** Full-screen background video with a black overlay (`bg-black/60`) for text readability.
- **Responsiveness:** Fully responsive for mobile (with a hamburger menu) and desktop.

### Tech Stack Requirements
- Use **React** with **Tailwind CSS**.
- Use **lucide-react** for icons.
- Use **hls.js** to handle the background video streaming (.m3u8) to ensure it works on Chrome/Firefox, while using native HLS for Safari.
- Import these Google Fonts via CSS: 'Inter', 'Manrope', 'Cabin', and 'Instrument Serif'.

### Assets
- **Video Source:** `https://stream.mux.com/4IMYGcL01xjs7ek5ANO17JC4VQVUTsojZlnw4fXzwSxc.m3u8`
- **Video Poster/Thumbnail:** `https://customer-cbeadsgr09pnsezs.cloudflarestream.com/257c7359efd4b4aaebcc03aa8fc78a36/thumbnails/thumbnail.jpg`

### Typography & Colors
- **Global Font:** 'Manrope'
- **Headings:** 'Inter'
- **Buttons/Badges:** 'Cabin'
- **Italic Accent:** 'Instrument Serif'
- **Colors:**
  - Primary Purple: `#7b39fc` (Hover: `#6a2ce0`)
  - Secondary Dark: `#2b2344` (Hover: `#352b54`)
  - Accent Orange: `#f87b52`
  - Glass Border: `rgba(164,132,215,0.5)`
  - Glass Background: `rgba(85,80,110,0.4)`

### Layout & Components

1. **Background Video Component:**
   - Create a robust component that handles HLS streams.
   - It must auto-play, loop, mute, and play inline.
   - It must handle the poster image fading out once the video actually starts playing to prevent black flashes.

2. **Navbar:**
   - **Left:** Logo (Use a white square container with the `Command` icon inside).
   - **Center (Desktop):** Links for "Home", "Services" (with a `ChevronDown` icon), "Reviews", "Contact us".
   - **Right (Desktop):** "Sign In" (Glass effect button) and "Get Started" (Purple button).
   - **Mobile:** Show a Menu toggle button that opens a full-screen black overlay with vertical links.

3. **Hero Content (Centered):**
   - **Badge:** A glassmorphism pill shape containing:
     - A small orange tag: "New"
     - Text: "Say Hello to Datacore v3.2"
   - **Headline (Large, ~76px on desktop):**
     - Line 1: "Your Networks."
     - Line 2: "One Rapid [Italic Serif Font: Interface]."
   - **Subtext:** "Platform helps admins control access, logs, and servers with purpose."
   - **CTA Buttons:**
     - Primary: "Book a Free Demo" (Purple)
     - Secondary: "Get Started Now" (Dark Navy)

Please ensure the code is production-ready, clean, and handles the video loading state gracefully.
```

---
*NeuroFlow Academy Site Templates*