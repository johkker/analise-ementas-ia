# Design System Master - Lupa Política

## Core Concept
A premium, glassmorphic dashboard for political transparency. The design must feel high-tech, trustworthy, and extremely polished ("Pro Max").

## 1. Visual Style (Premium Glassmorphism)
- **Background**: Deep Charcoal (`#0F1115`).
- **Cards**: Translucent background (`rgba(30, 32, 38, 0.7)`), 1px subtle border (`rgba(255, 255, 255, 0.1)`), Backdrop Blur (12px).
- **Shadows**: Soft, multi-layered shadows for depth over pure black background.
- **Micro-animations**: Smooth transitions (150ms) for hover states and chart interactions.

## 2. Color Palette
| Purpose | Color | Hex | Tailwind |
|---------|-------|-----|----------|
| Background | Deep Charcoal | `#0F1115` | `bg-[#0F1115]` |
| Surface | Glass Gray | `rgba(30, 32, 38, 0.7)` | `bg-white/5` |
| Primary | Emerald Green | `#00A859` | `text-[#00A859]` |
| Secondary | Royal Gold | `#FFCC00` | `text-[#FFCC00]` |
| Accent | Neon Blue | `#0097D8` | `text-[#0097D8]` |
| Danger | Crimson Red | `#FF4B4B` | `text-[#FF4B4B]` |

## 3. Typography
- **Headings**: `Outfit` (fallback: sans-serif). Use Bold (700) or ExtraBold (800).
- **Body**: `Inter`. Regular (400) for content, Medium (500) for UI labels.
- **Numbers**: `font-variant-numeric: tabular-nums` for spendings and vote counts.

## 4. Interaction Guidelines (UI-UX Pro Max)
- `cursor-pointer`: Apply to all interactive cards and rows.
- `hover-feedback`: Subtle brightness increase or border color shift (`emerald-500/50`).
- `loading-states`: skeleton screens for data fetching. No abrupt layout shifts.

## 5. Anti-patterns (Flag these)
- **No Emojis**: Use Lucide icons exclusively.
- **No Sharp Vertices**: Use `rounded-xl` (12px) or `rounded-2xl` (16px) for cards.
- **No Solid Black**: Use Charcoal/Slate-950 for better depth.
- **No user login UI**: Platform is strictly public.
