---
title: "Mindloop"
template_id: "2f1de9f7-ee1f-4ecc-8bd4-92b53d8ca7e0"
section: "sites"
category_slug: "saas"
video_url: ""
tags:
  - site_template
  - vibe_coding
  - section_sites
---

# 🌐 Mindloop

> **Секція:** `SITES` | **Категорія:** `saas`  
> **ID шаблону:** `2f1de9f7-ee1f-4ecc-8bd4-92b53d8ca7e0`  
> **Каталог шаблонів:** [[06_Шаблоны_и_Сервисы/01_Шаблоны_Сайтов_Инструкции_и_Медиа|📑 Головний Каталог 343 Шаблонів]]

---

### ℹ️ Опис:
SaaS

### 🖼 Прев'ю:
![Mindloop](https://iuxlbrjhcbeiovgbldcy.supabase.co/storage/v1/object/public/site-template-media/thumbnail/04f1e2c6-59b7-4df0-9950-9702cba96940.gif)

### 💻 Повний промпт / код для генерації (Bolt.new / v0 / Lovable / Cursor):
```text
Create a full-screen hero section with a background video, navbar, and centered content. Use a dark theme with all white text.

Background Video:

Full-screen <video> element with autoPlay loop muted playsInline
Positioned absolute inset-0 w-full h-full object-cover z-0
Source URL: https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260324_151826_c7218672-6e92-402c-9e45-f1e0f454bdc4.mp4
Font:

Import Google Font: Instrument Serif (display) and Inter (body)
All headings use font-family: 'Instrument Serif', serif
Body text uses Inter, sans-serif
Navbar (relative z-10):

Flex row, justify-between, px-8 py-6, max-w-7xl mx-auto
Left: Brand name "Velorah®" — text-3xl tracking-tight, white, Instrument Serif. The ® is wrapped in <sup className="text-xs">
Center: Hidden on mobile (hidden md:flex), links: Home, Studio, About, Journal, Reach Us — text-sm text-white, gap-10, hover:opacity-80 transition-opacity
Right: "Begin Journey" button with liquid-glass effect, rounded-full px-6 py-2.5 text-sm, hover:scale-[1.03]
Hero Content (relative z-10):

Flex column, centered (items-center justify-center text-center), px-6 pt-32 pb-40
H1: "Focus in a Distracted World" — text-5xl sm:text-7xl md:text-8xl, leading-[0.95], tracking-[-2.46px], max-w-7xl, white, Instrument Serif, animate-fade-rise
Paragraph: "We're designing tools for deep thinkers, bold creators, and quiet rebels. Amid the chaos, we build digital spaces for sharp focus and inspired work." — text-base sm:text-lg, max-w-2xl mt-8 leading-relaxed, white, animate-fade-rise-delay
CTA Button: "Begin Journey" — liquid-glass, rounded-full px-14 py-5 text-base, white, mt-12, hover:scale-[1.03], animate-fade-rise-delay-2
Liquid Glass CSS (.liquid-glass):

.liquid-glass {
  background: rgba(255, 255, 255, 0.01);
  background-blend-mode: luminosity;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: none;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.liquid-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.4px;
  background: linear-gradient(180deg,
    rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
    rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
    rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
Animations:

@keyframes fade-rise {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-rise { animation: fade-rise 0.8s ease-out both; }
.animate-fade-rise-delay { animation: fade-rise 0.8s ease-out 0.2s both; }
.animate-fade-rise-delay-2 { animation: fade-rise 0.8s ease-out 0.4s both; }
Page background: bg-black (hsl(0,0%,0%)), section is min-h-screen overflow-hidden.
```

---
*NeuroFlow Academy Site Templates*