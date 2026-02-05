# Feature Specification: Lumina – Deep Purple Royal Theme

**Feature Branch**: `004-lumina-theme-redesign`
**Created**: 2026-01-29
**Updated**: 2026-02-03
**Status**: Implemented (Final)
**Theme Name**: Lumina – Deep Purple Royal

---

## Overview

This specification defines the **final implemented design** for the Lumina Todo App. The theme uses a Deep Purple Royal color palette with glassmorphism effects, ensuring high contrast and visibility in both light and dark modes.

---

## Theme System

### Default Theme
- **Dark mode is enabled by default**
- Theme persists in localStorage
- Smooth transitions between themes (no flash)
- Class-based strategy using `next-themes`

---

## Light Theme Design Tokens

### Backgrounds
| Element | Value | Description |
|---------|-------|-------------|
| Page Background | `linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%)` | Light lavender gradient |
| Card Background | `#FFFFFF` with `rgba(209, 196, 233, 0.5)` border | White cards with purple border |
| Input Background | `rgba(255, 255, 255, 0.8)` | Semi-transparent white |
| Glass Effect | `rgba(255, 255, 255, 0.7)` with `backdrop-filter: blur(12px)` | Subtle glass |

### Text Colors
| Element | Value | Description |
|---------|-------|-------------|
| Primary Text | `#1a0033` (via CSS var) | Very dark purple |
| Gradient Text | `#4a148c → #5e35b1 → #7e57c2` | Dark purple gradient for headlines |
| Muted Text | `hsl(270 60% 25%)` | Dark enough for contrast |
| Link Text | `#5e35b1` | Deep purple for visibility |

### Buttons
| State | Background | Text Color |
|-------|------------|------------|
| Default (gradient) | `linear-gradient(135deg, #5e35b1 0%, #4a148c 100%)` | `#FFFFFF` (white) |
| Hover | `linear-gradient(135deg, #4a148c 0%, #311b92 100%)` | `#FFFFFF` (white) |
| Primary solid | `#5e35b1` | `#FFFFFF` (white) |
| Primary hover | `#4a148c` | `#FFFFFF` (white) |

### Borders & Focus
| Element | Value |
|---------|-------|
| Card Border | `rgba(209, 196, 233, 0.5)` / `#d1c4e9` |
| Input Border | `rgba(179, 157, 219, 0.5)` |
| Input Focus | `border: #7e57c2`, `box-shadow: 0 0 0 3px rgba(126, 87, 194, 0.15)` |
| Focus Ring | `#7e57c2` |

---

## Dark Theme Design Tokens

### Backgrounds
| Element | Value | Description |
|---------|-------|-------------|
| Page Background | `linear-gradient(135deg, #1a0033 0%, #2e003e 50%, #120024 100%)` | Deep purple gradient |
| Card Background | `rgba(255, 255, 255, 0.05)` with blur | Glassmorphism effect |
| Input Background | `rgba(255, 255, 255, 0.05)` | Dark translucent |
| Glass Effect | `rgba(255, 255, 255, 0.05)` with `backdrop-filter: blur(10px)` | Dark glass |

### Text Colors
| Element | Value | Description |
|---------|-------|-------------|
| Primary Text | `#f3e5f5` | Bright lavender |
| Gradient Text | `#e1bee7 → #ce93d8 → #f3e5f5` | Bright lavender gradient for headlines |
| Muted Text | `hsl(291 47% 80%)` | Light purple |
| Link Text | `#ce93d8` | Bright for visibility |

### Buttons
| State | Background | Text Color |
|-------|------------|------------|
| Default (gradient) | `linear-gradient(135deg, #ce93d8 0%, #e1bee7 100%)` | `#1a0033` (dark) |
| Hover | `linear-gradient(135deg, #e1bee7 0%, #f3e5f5 100%)` | `#1a0033` (dark) |
| Primary solid | `#ce93d8` | `#1a0033` (dark) |
| Primary hover | `#e1bee7` | `#1a0033` (dark) |

### Borders & Focus
| Element | Value |
|---------|-------|
| Card Border | `rgba(126, 87, 194, 0.2)` |
| Input Border | `rgba(126, 87, 194, 0.3)` |
| Input Focus | `border: #b39ddb`, `box-shadow: 0 0 0 3px rgba(179, 157, 219, 0.15)` |
| Focus Ring | `#b39ddb` |

### Glassmorphism Effects
| Property | Value |
|----------|-------|
| Glass Card BG | `rgba(255, 255, 255, 0.05)` |
| Backdrop Blur | `blur(10px)` to `blur(20px)` |
| Card Shadow | `0 8px 32px rgba(0, 0, 0, 0.24)` |
| Glow on Hover | `0 0 30px rgba(179, 157, 219, 0.3)` |

---

## Contrast & Accessibility Rules (Critical)

### Visibility Requirements
1. **Text must NEVER match or blend with background**
   - Light theme: Use dark purples (`#4a148c`, `#5e35b1`) on light backgrounds
   - Dark theme: Use bright lavenders (`#ce93d8`, `#e1bee7`, `#f3e5f5`) on dark backgrounds

2. **Buttons must always be visually distinct**
   - Light theme: Dark purple buttons with white text
   - Dark theme: Bright lavender buttons with dark text
   - Buttons must have sufficient shadow/glow for depth

3. **Hero/headline text must be readable**
   - GradientText component uses theme-aware gradients
   - Light mode: Dark gradient (`#4a148c → #7e57c2`)
   - Dark mode: Bright gradient (`#e1bee7 → #f3e5f5`)

4. **Muted text must have sufficient contrast**
   - Light theme: `hsl(270 60% 25%)` - dark purple
   - Dark theme: `hsl(291 47% 80%)` - light lavender

### WCAG Compliance
- All text combinations must pass WCAG AA (4.5:1 for normal text, 3:1 for large text)
- Touch targets minimum 44px for mobile interaction

---

## Header Logo Rules

### Logo "L" Styling
The single letter logo "L" in the header/sidebar must have a background box for visibility.

| Theme | Box Background | Text Color |
|-------|---------------|------------|
| Light | `#4a148c` (dark purple) | `#f3e5f5` (light lavender) |
| Dark | `#ede7f6` (light lavender) | `#4a148c` (dark purple) |

### Logo Constraints
- Box size: `w-8 h-8` (32px square)
- Border radius: `rounded-lg`
- Text: Bold, centered
- **No other header changes allowed** when modifying logo

---

## CSS Implementation Classes

### Theme-Aware Classes
| Class | Purpose |
|-------|---------|
| `.gradient-text-primary` | Theme-aware gradient for headlines |
| `.gradient-text-accent` | Secondary gradient text |
| `.btn-gradient` | Theme-aware gradient buttons |
| `.btn-primary` | Theme-aware solid buttons |
| `.logo-box` | Logo background container |
| `.logo-text` | Logo letter styling |
| `.glass-card` | Glassmorphism card effect |
| `.glass-input` | Glass-styled inputs |
| `.glass-button` | Glass-styled buttons |
| `.glass-sidebar` | Sidebar glass effect |

---

## Explicit Non-Goals

The following must NOT change:
- **Application structure** - Routes, layouts, component hierarchy
- **Application architecture** - State management, API integration, middleware
- **Features** - Authentication, task CRUD, filtering, statistics
- **Backend/API** - No changes to FastAPI endpoints or database
- **Business logic** - No changes to validation, data handling

---

## Component Styling Summary

### Pages Affected
| Page | Styling Applied |
|------|-----------------|
| Landing (`/`) | Hero gradient text, glass nav, floating orbs |
| Login (`/login`) | Glass card, gradient "Lumina" text |
| Signup (`/signup`) | Glass card, gradient "Lumina" text |
| Tasks (`/tasks`) | Gradient "Tasks" heading, glass cards, themed buttons |

### Components Using Theme Tokens
- `GradientText` - Headlines ("Lumina", "Tasks", etc.)
- `AnimatedButton` - All primary action buttons
- `GlassCard` - Content containers
- `ThemeToggle` - Theme switcher
- `Sidebar` - Navigation with logo
- `DashboardHeader` - Top header
- `TaskCard` - Individual task items
- `EmptyState` - No tasks message

---

## Validation Checklist

After implementation, verify:
- [ ] Light theme: All text is dark and readable
- [ ] Dark theme: All text is bright and readable
- [ ] Light theme: Buttons have dark purple background, white text
- [ ] Dark theme: Buttons have bright lavender background, dark text
- [ ] Hero "Lumina" text visible in both themes
- [ ] "/tasks" heading visible in both themes
- [ ] Logo has background box in both themes
- [ ] Logo box inverts colors between themes
- [ ] No layout changes from theme modifications
- [ ] Build passes with zero errors

---

## Color Palette Reference (Quick Reference)

### Primary Purple Scale
| Name | Hex | Usage |
|------|-----|-------|
| lumina-primary-50 | `#f3e5f5` | Lightest - dark mode text |
| lumina-primary-100 | `#e1bee7` | Light - dark mode highlights |
| lumina-primary-200 | `#ce93d8` | Medium - dark mode buttons |
| lumina-primary-300 | `#ba68c8` | Medium-dark |
| lumina-primary-400 | `#ab47bc` | Accent |
| lumina-primary-500 | `#7e57c2` | Primary (base) |
| lumina-primary-600 | `#5e35b1` | Deep - light mode buttons |
| lumina-primary-700 | `#512da8` | Deeper |
| lumina-primary-800 | `#4a148c` | Dark - light mode accents |
| lumina-primary-900 | `#311b92` | Darkest |

### Background Surfaces
| Theme | Surface | Hex/Value |
|-------|---------|-----------|
| Light | Base | `#ede7f6` |
| Light | Card | `#FFFFFF` |
| Dark | Base | `#1a0033` |
| Dark | Card | `#2e003e` (solid) or `rgba(255,255,255,0.05)` (glass) |

---

## Dependencies

- Next.js 16+ with App Router
- Tailwind CSS with custom configuration
- next-themes for theme management
- Framer Motion for animations
- Radix UI primitives (via shadcn/ui)
- Lucide React for icons

---

## Risks

| Risk | Mitigation |
|------|------------|
| Contrast issues in edge cases | CSS overrides with `!important` for critical text |
| Glassmorphism browser support | Fallback solid backgrounds for unsupported browsers |
| Theme flash on load | next-themes with class-based strategy, default dark |

---

## Modal & Dialog Tokens (Canonical)

### Add Task Modal
| Theme | Background | Text | Input BG | Input Border | Placeholder |
|-------|-----------|------|----------|--------------|-------------|
| Light | `#d1c3e9` | `#1a0033` | `#ede7f6` | `#4a148c` | `#5e35b1` (80% opacity) |
| Dark | `#4e2f83` | `#f3e5f5` | `#38206a` | `#ce93d8` | `#ce93d8` (80% opacity) |

### Delete Confirmation Dialog
| Theme | Background | Text | Muted Text |
|-------|-----------|------|------------|
| Light | `#ffffff` | `#1a0033` | `#5e35b1` |
| Dark | `#2e1a47` | `#f3e5f5` | `#ce93d8` |

### Calendar Popover
| Theme | Background | Text |
|-------|-----------|------|
| Light | `#ffffff` | `#1a1a1a` |
| Dark | `#1e1e2e` | `#f3e5f5` |

### Select Dropdown
| Theme | Background | Text |
|-------|-----------|------|
| Light | `#ffffff` | `#1a1a1a` |
| Dark | `#1e1e2e` | `#f3e5f5` |

---

## Avatar Tokens (Canonical)

| Theme | Gradient | Text |
|-------|---------|------|
| Light | `linear-gradient(135deg, #5e35b1, #7e57c2)` | `#ffffff` |
| Dark | `linear-gradient(135deg, #7e57c2, #ab47bc)` | `#ffffff` |

---

## Priority Badge Tokens (Canonical)

### Light Theme
| Priority | Background | Text |
|----------|-----------|------|
| High | `#fee2e2` | `#991b1b` |
| Medium | `#fef3c7` | `#92400e` |
| Low | `#dcfce7` | `#166534` |

### Dark Theme
| Priority | Background | Text |
|----------|-----------|------|
| High | `rgba(127, 29, 29, 0.3)` | `#f87171` |
| Medium | `rgba(120, 53, 15, 0.3)` | `#fbbf24` |
| Low | `rgba(20, 83, 45, 0.3)` | `#4ade80` |

---

## Semantic Colors (Canonical)

| Name | Default | 400 | 500 |
|------|---------|-----|-----|
| Success | `#10B981` | `#34D399` | `#10B981` |
| Warning | `#F59E0B` | `#FBBF24` | `#F59E0B` |
| Danger | `#EF4444` | `#F87171` | `#EF4444` |

---

## Custom Shadow Tokens (Canonical)

| Name | Value |
|------|-------|
| `shadow-glass` | `0 8px 32px rgba(0, 0, 0, 0.12)` |
| `shadow-glass-lg` | `0 16px 48px rgba(0, 0, 0, 0.16)` |
| `shadow-glass-xl` | `0 24px 64px rgba(0, 0, 0, 0.2)` |
| `shadow-glow` | `0 0 20px rgba(126, 87, 194, 0.3)` |
| `shadow-glow-lg` | `0 0 40px rgba(179, 157, 219, 0.4)` |

---

## Typography (Canonical)

| Property | Value |
|----------|-------|
| Primary Font | `var(--font-inter), system-ui, sans-serif` |
| Mono Font | `var(--font-jetbrains-mono), monospace` |
| Font Smoothing | `-webkit-font-smoothing: antialiased` |

---

## THEME LOCK RULES (MANDATORY)

> **This section is binding. All agents, skills, and implementations MUST obey these rules.**

### Rule 1: Canonical Status
This specification defines the **FINAL, CANONICAL** Lumina Deep Purple Royal theme. The values documented above are the **single source of truth** extracted from the live production codebase.

### Rule 2: No Color Invention
**Do NOT invent, modify, or "improve" any color values unless the user EXPLICITLY requests a specific change.** This includes:
- No "adjusting for better contrast" without being asked
- No substituting "similar" colors
- No adding new gradient stops
- No changing opacity values
- No introducing new color tokens

### Rule 3: No Theme Drift
When implementing or modifying any UI component:
- Match this spec EXACTLY
- If a color is not documented here, check `globals.css` and `tailwind.config.ts` first
- If adding a new component, derive colors from the existing palette in this spec
- Never introduce colors outside the documented palette

### Rule 4: Verification Required
After ANY UI change, verify:
1. Light theme matches all documented light values
2. Dark theme matches all documented dark values
3. Text contrast passes WCAG AA (4.5:1 normal, 3:1 large)
4. No visual regression in either theme
5. Build passes with zero errors

### Rule 5: Spec Update Protocol
If a theme change IS explicitly requested:
1. Make the code change
2. Update THIS spec.md with the new values
3. Update plan.md and tasks.md accordingly
4. Document the change reason

---

*This specification is the CANONICAL source of truth for the Lumina Deep Purple Royal theme. Any implementation that deviates from these values without explicit user request is a bug.*
