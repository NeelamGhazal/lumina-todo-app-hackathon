# Specification: Lumina - World-Class Todo Interface

**Feature ID**: 003-ui-redesign
**Version**: 1.1.0
**Status**: Clarified
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Author**: Claude Code

---

## 1. Executive Summary

### 1.1 Purpose
Transform the existing functional Todo application into **Lumina** - a visually stunning, internationally competitive interface that matches Dribbble/Awwwards-level quality while preserving all existing functionality.

### 1.2 Brand Identity
**App Name**: Lumina
**Tagline**: "Illuminate Your Productivity"

### 1.3 Target Audience
- International users
- Hackathon judges
- Potential investors and employers
- Design-conscious professionals

---

## 2. Design Decisions (Clarified)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **App Name** | Lumina | Fresh branding, evokes light/clarity |
| **Default Theme** | Dark mode | Modern preference, reduces eye strain |
| **Task Layout** | Grid only | Cleaner UI, no view toggle needed |
| **Social Login** | Visual only | Styled buttons show "Coming soon" |
| **Empty States** | Icon placeholders | Simple icons + text, faster to implement |
| **Loading States** | Skeleton screens | Animated placeholders matching layout |
| **Search** | Visual only | Search input styled, shows "Coming soon" |
| **Navigation** | Sidebar nav | Vertical sidebar with filters, collapsible |

---

### 2.2 Scope
- **IN SCOPE**: Visual design, animations, theming, responsive polish, glassmorphism effects
- **OUT OF SCOPE**: Backend changes, authentication logic, CRUD operations, API modifications

### 2.3 Success Metrics
| Metric | Target |
|--------|--------|
| Visual Appeal | 10/10 (judges impressed) |
| Animation Performance | 60fps constant |
| Lighthouse Performance | 90+ |
| First Contentful Paint | < 1.5s |
| Mobile Responsiveness | Perfect on all devices |
| Theme Toggle | Instant, smooth transition |

---

## 3. Current State Analysis

### 3.1 Landing Page Issues
```
Current:
- Generic text "Evolution Todo - A world-class task management application"
- No sign in/sign up buttons on home page
- Users must manually navigate to /tasks to sign in
- Plain background, no visual interest
```

### 3.2 Design Quality Assessment
| Aspect | Current State | Target State |
|--------|--------------|--------------|
| Visual Appeal | Basic, generic | Stunning, professional |
| Animations | Present but minimal | Smooth, delightful micro-interactions |
| Glassmorphism | Not implemented | Full glassmorphic effects |
| Gradients | Basic dark/light | Dynamic radial gradients with orbs |
| Typography | Single scale | Clear hierarchy with modern fonts |
| Spacing | Inconsistent | 4px/8px grid system |

### 3.3 Existing Foundation (Preserve)
- Next.js 16+ App Router - working
- Tailwind CSS theme system - working
- Framer Motion animations - working
- Shadcn/ui components - working
- Authentication flow - working
- CRUD operations - working
- Dark/light mode toggle - working

---

## 4. Design System Specification

### 4.1 Color Palette

> **⚠️ OBSOLETE — ALL COLOR VALUES IN THIS SECTION ARE DEPRECATED**
>
> The color palette below (orange `#FF9B51` / slate gray `#25343F`) was **replaced entirely** by the Deep Purple Royal theme in Phase 4.
>
> **For all active color values, see: `specs/004-lumina-theme-redesign/spec.md`**
>
> The Phase 4 spec is the ONLY canonical source of truth for colors, gradients, buttons, text, and backgrounds.

<details>
<summary>📦 Archived: Original Phase 3 Color Values (DO NOT USE)</summary>

##### Light Theme (OBSOLETE)
```css
/* ⚠️ OBSOLETE — replaced by Phase 4 Deep Purple Royal theme */
--background: #EAEFEF;        /* REPLACED → #ede7f6 gradient */
--card: #FFFFFF;              /* REPLACED → #FFFFFF (same) */
--border: #BFC9D1;            /* REPLACED → hsl(261 46% 84%) */
--foreground: #25343F;        /* REPLACED → #1a0033 */
--muted-foreground: #3D4D5C;  /* REPLACED → hsl(270 60% 25%) */
--primary: #FF9B51;           /* REPLACED → #5e35b1 (deep purple) */
--ring: #FF9B51;              /* REPLACED → #7e57c2 */
```

##### Dark Theme (OBSOLETE)
```css
/* ⚠️ OBSOLETE — replaced by Phase 4 Deep Purple Royal theme */
--background: #25343F;        /* REPLACED → #1a0033 gradient */
--card: #1A242C;              /* REPLACED → hsl(270 100% 12%) */
--border: #3D4D5C;            /* REPLACED → hsl(262 47% 35%) */
--foreground: #EAEFEF;        /* REPLACED → #f3e5f5 */
--muted-foreground: #BFC9D1;  /* REPLACED → hsl(291 47% 80%) */
--primary: #FF9B51;           /* REPLACED → #ce93d8 (bright lavender) */
--ring: #FF9B51;              /* REPLACED → #b39ddb */
```

##### Button States (OBSOLETE)
```css
/* ⚠️ OBSOLETE — see Phase 4 spec for .btn-gradient and .btn-primary */
```

##### Input States (OBSOLETE)
```css
/* ⚠️ OBSOLETE — see Phase 4 spec for .glass-input */
```

##### Card Contrast Rules (OBSOLETE)
```css
/* ⚠️ OBSOLETE — see Phase 4 spec for glass-card contrast rules */
```

</details>

#### Semantic Colors (Status) — STILL ACTIVE
```css
/* These values are unchanged between Phase 3 and Phase 4 */
--success: #10B981;
--warning: #F59E0B;
--danger: #EF4444;
```

#### ❌ REMOVED / DEPRECATED
The following colors are NO LONGER USED:
- ~~Violet/Purple gradients~~ (Phase 3 early iteration)
- ~~Cyan/Teal accents~~ (Phase 3 early iteration)
- ~~lumina-accent-*~~ (Phase 3 early iteration)
- ~~Any yellow/brown variants~~ (Phase 3 early iteration)
- ~~Orange accent `#FF9B51`~~ (entire Phase 3 palette — replaced by Phase 4 Deep Purple Royal)
- ~~Slate grays `#25343F`, `#1A242C`, `#3D4D5C`~~ (replaced by deep purples in Phase 4)

### 4.2 Typography

#### Font Stack
```css
/* Primary (Headings + Body) */
font-family: 'Inter', system-ui, -apple-system, sans-serif;

/* Code/Mono */
font-family: 'JetBrains Mono', 'Fira Code', monospace;
```

#### Type Scale
| Token | Size | Weight | Line Height | Use Case |
|-------|------|--------|-------------|----------|
| display-xl | 60px | 800 | 1.1 | Hero headlines |
| display-lg | 48px | 700 | 1.15 | Page titles |
| heading-lg | 36px | 700 | 1.2 | Section headers |
| heading-md | 30px | 600 | 1.25 | Card titles |
| heading-sm | 24px | 600 | 1.3 | Subsection titles |
| body-lg | 18px | 400 | 1.6 | Lead text |
| body-md | 16px | 400 | 1.5 | Body text |
| body-sm | 14px | 400 | 1.5 | Secondary text |
| caption | 12px | 500 | 1.4 | Labels, hints |

### 4.3 Spacing System
```
Base: 4px (0.25rem)

Scale:
- 1:   4px   (0.25rem)
- 2:   8px   (0.5rem)
- 3:  12px   (0.75rem)
- 4:  16px   (1rem)
- 5:  20px   (1.25rem)
- 6:  24px   (1.5rem)
- 8:  32px   (2rem)
- 10: 40px   (2.5rem)
- 12: 48px   (3rem)
- 16: 64px   (4rem)
- 20: 80px   (5rem)
- 24: 96px   (6rem)
```

### 4.4 Border Radius
| Token | Value | Use Case |
|-------|-------|----------|
| radius-sm | 8px | Buttons, badges, inputs |
| radius-md | 12px | Cards, dropdowns |
| radius-lg | 16px | Modals, dialogs |
| radius-xl | 24px | Hero sections, panels |
| radius-2xl | 32px | Large hero elements |
| radius-full | 9999px | Pills, avatars |

### 4.5 Shadows
```css
/* Small - buttons, badges */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Medium - cards, dropdowns */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -2px rgba(0, 0, 0, 0.1);

/* Large - modals, popovers */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -4px rgba(0, 0, 0, 0.1);

/* XL - elevated panels */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 8px 10px -6px rgba(0, 0, 0, 0.1);

/* Glass shadow */
--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.12);
```

### 4.6 Glassmorphism Effects
```css
/* Glass Card - Dark Mode */
.glass-dark {
  background: rgba(26, 36, 44, 0.8);     /* #1A242C with opacity */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(61, 77, 92, 0.5); /* #3D4D5C */
}

/* Glass Card - Light Mode */
.glass-light {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(191, 201, 209, 0.5); /* #BFC9D1 */
}

/* Glass Overlay (Modal backdrop) */
.glass-overlay {
  background: rgba(37, 52, 63, 0.5);     /* #25343F with opacity */
  backdrop-filter: blur(4px);
}
```

### 4.7 Background Effects (Optional Subtle Orbs)
```css
/* NOTE: Orbs use the ACCENT color only - NO violet/cyan */

/* Subtle glow - accent orange */
.glow-accent {
  background: radial-gradient(
    circle at 50% 50%,
    rgba(255, 155, 81, 0.08) 0%,        /* #FF9B51 */
    transparent 70%
  );
}

/* Floating orb - uses accent color ONLY */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}

.orb-accent {
  width: 300px;
  height: 300px;
  background: rgba(255, 155, 81, 0.1);   /* #FF9B51 - subtle */
}

/* ❌ DO NOT USE gradient text - use solid accent color instead */
/* ❌ DO NOT USE violet/cyan orbs */
```

---

## 5. Animation Specifications

### 5.1 Timing & Easing
```css
/* Duration tokens */
--duration-instant: 100ms;   /* Micro-interactions */
--duration-fast: 200ms;      /* Button states, toggles */
--duration-normal: 300ms;    /* Standard transitions */
--duration-slow: 400ms;      /* Page transitions */
--duration-slower: 500ms;    /* Complex animations */

/* Easing curves */
--ease-default: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

### 5.2 Animation Patterns

#### Fade Up (Page Elements)
```javascript
// Framer Motion
initial: { opacity: 0, y: 20 }
animate: { opacity: 1, y: 0 }
transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
```

#### Stagger Children
```javascript
// Container
staggerChildren: 0.1
delayChildren: 0.1

// Children
initial: { opacity: 0, y: 20 }
animate: { opacity: 1, y: 0 }
```

#### Hover Lift
```javascript
whileHover: {
  y: -4,
  scale: 1.02,
  boxShadow: "0 20px 40px rgba(0,0,0,0.15)"
}
transition: { duration: 0.2 }
```

#### Modal/Dialog
```javascript
// Overlay
initial: { opacity: 0 }
animate: { opacity: 1 }
exit: { opacity: 0 }

// Content
initial: { opacity: 0, scale: 0.95, y: 10 }
animate: { opacity: 1, scale: 1, y: 0 }
exit: { opacity: 0, scale: 0.95, y: 10 }
transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
```

#### Checkbox Check
```javascript
// SVG path animation
initial: { pathLength: 0 }
animate: { pathLength: 1 }
transition: {
  type: "spring",
  stiffness: 300,
  damping: 20
}
```

#### Shimmer Loading
```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.shimmer {
  background: linear-gradient(
    90deg,
    var(--bg-surface) 25%,
    var(--bg-elevated) 50%,
    var(--bg-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

## 6. Page Specifications

### 6.1 Landing Page (/)

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ [Navigation Bar - Glass]                                     │
│   Lumina  [Features] [About]     [Sign In] [Get Started →]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Floating Orb - Primary, top-right]                        │
│  [Floating Orb - Accent, bottom-left]                       │
│                                                              │
│                     HERO SECTION                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Gradient Text Headline                              │   │
│   │  "Illuminate Your Productivity"                      │   │
│   │                                                       │   │
│   │  Subheadline (muted text)                            │   │
│   │                                                       │   │
│   │  [Get Started Free ⚡] [Watch Demo ▶]                │   │
│   │                                                       │   │
│   │  "Free forever • No credit card required"            │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              [Dashboard Preview - Glass Card]         │   │
│   │                                                       │   │
│   │    ┌─────┐ ┌─────┐ ┌─────┐                          │   │
│   │    │Task │ │Task │ │Task │  ← Animated task cards   │   │
│   │    └─────┘ └─────┘ └─────┘                          │   │
│   │                                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                    FEATURES SECTION                          │
│   "Everything you need to stay organized"                    │
│                                                              │
│   ┌────────┐  ┌────────┐  ┌────────┐                        │
│   │Feature │  │Feature │  │Feature │                        │
│   │  Card  │  │  Card  │  │  Card  │  ← Glass cards         │
│   │   1    │  │   2    │  │   3    │                        │
│   └────────┘  └────────┘  └────────┘                        │
│                                                              │
│   ┌────────┐  ┌────────┐  ┌────────┐                        │
│   │Feature │  │Feature │  │Feature │                        │
│   │  Card  │  │  Card  │  │  Card  │                        │
│   │   4    │  │   5    │  │   6    │                        │
│   └────────┘  └────────┘  └────────┘                        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                       CTA SECTION                            │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  "Ready to get organized?"                           │   │
│   │                                                       │   │
│   │           [Start for Free →]                         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                         FOOTER                               │
│   Lumina   Links   Social   © 2026 Lumina                    │
└─────────────────────────────────────────────────────────────┘
```

#### Feature Cards Content
1. **Task Management** - CheckSquare icon - "Create, organize, and complete tasks"
2. **Priority Levels** - Flag icon - "Set high, medium, or low priority"
3. **Categories** - FolderOpen icon - "Organize by work, personal, shopping"
4. **Due Dates** - Calendar icon - "Never miss a deadline"
5. **Dark Mode** - Moon icon - "Beautiful day and night themes"
6. **Responsive** - Smartphone icon - "Works on any device"

### 6.2 Sign In Page (/login)

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│                    SPLIT LAYOUT (Desktop)                    │
├───────────────────────────┬─────────────────────────────────┤
│                           │                                  │
│  LEFT PANEL (50%)         │   RIGHT PANEL (50%)             │
│  [Gradient Background]    │   [Glass Card Form]             │
│                           │                                  │
│  [Floating Orbs]          │   ┌───────────────────────┐     │
│                           │   │  Logo                  │     │
│  ┌─────────────────┐     │   │                        │     │
│  │ Brand Visual    │     │   │  "Welcome back"        │     │
│  │                 │     │   │  subtitle              │     │
│  │ Tagline         │     │   │                        │     │
│  │                 │     │   │  [Email Input]         │     │
│  └─────────────────┘     │   │                        │     │
│                           │   │  [Password Input] 👁   │     │
│  "Join 10,000+ users"     │   │                        │     │
│  (social proof)           │   │  ☐ Remember me         │     │
│                           │   │                        │     │
│                           │   │  [Sign In Button]      │     │
│                           │   │                        │     │
│                           │   │  ─── or continue ───   │     │
│                           │   │                        │     │
│                           │   │  [Google] [GitHub]     │     │
│                           │   │  (Visual only, shows   │     │
│                           │   │   "Coming soon" toast) │     │
│                           │   │                        │     │
│                           │   │  Don't have account?   │     │
│                           │   │  [Sign up →]           │     │
│                           │   └───────────────────────┘     │
│                           │                                  │
└───────────────────────────┴─────────────────────────────────┘

Mobile: Single column, glass card centered over gradient background
```

### 6.3 Sign Up Page (/signup)

Similar to Sign In with additional fields:
- Name input
- Password confirmation input
- Password strength indicator
- Terms checkbox
- "Already have account? Sign in" link

### 6.4 Tasks Dashboard (/tasks)

#### Layout Structure (Sidebar Navigation)
```
┌─────────────────────────────────────────────────────────────────────┐
│ [HEADER - Glass, Sticky, spans full width]                          │
│  Lumina Logo    [Search... 🔍 "Coming soon"]    [🌙] [🔔] [Avatar]  │
├────────────────┬────────────────────────────────────────────────────┤
│                │                                                     │
│  SIDEBAR       │  MAIN CONTENT                                      │
│  [Glass Panel] │                                                     │
│                │  [Orb - Primary, top-right corner, subtle]         │
│  ┌──────────┐  │                                                     │
│  │ 📋 All   │  │  PAGE HEADER                                       │
│  │    (12)  │  │  ┌─────────────────────────────────────────────┐  │
│  ├──────────┤  │  │  "My Tasks"  (12 total)        [+ Add Task] │  │
│  │ ○ Active │  │  └─────────────────────────────────────────────┘  │
│  │    (8)   │  │                                                     │
│  ├──────────┤  │  TASK GRID (Responsive: 1/2/3 columns)            │
│  │ ✓ Done   │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │    (4)   │  │  │ [Glass Card]  │ │ [Glass Card]  │ │ [Glass Card]  ││
│  └──────────┘  │  │ ▌ Priority   │ │ ▌             │ │ ▌             ││
│                │  │ ☐ Task Title │ │ ☐ Task Title │ │ ☐ Task Title ││
│  CATEGORIES    │  │ Description..│ │ Description..│ │ Description..││
│  ┌──────────┐  │  │ 🏷 Tags      │ │ 🏷 Tags      │ │ 🏷 Tags      ││
│  │ 💼 Work  │  │  │ 📅 Due Today │ │ 📅 Due Tmrw  │ │ 📅 Due Fri   ││
│  │ 🏠 Home  │  │  │    [✏️] [🗑️] │ │    [✏️] [🗑️] │ │    [✏️] [🗑️] ││
│  │ 🛒 Shop  │  │  └──────────────┘ └──────────────┘ └──────────────┘│
│  └──────────┘  │                                                     │
│                │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  PRIORITY      │  │ [Glass Card]  │ │ [Glass Card]  │ │ [Glass Card]  ││
│  ┌──────────┐  │  │ ...          │ │ ...          │ │ ...          ││
│  │ 🔴 High  │  │  └──────────────┘ └──────────────┘ └──────────────┘│
│  │ 🟡 Medium│  │                                                     │
│  │ 🟢 Low   │  │  EMPTY STATE (when no tasks)                       │
│  └──────────┘  │  ┌─────────────────────────────────────────────┐  │
│                │  │              [Icon Placeholder]               │  │
│  ────────────  │  │          "No tasks yet"                      │  │
│  [⚙️ Settings] │  │     "Create your first task to get started"  │  │
│  [🚪 Logout]   │  │              [+ Add Your First Task]         │  │
│                │  └─────────────────────────────────────────────┘  │
│                │                                                     │
├────────────────┴────────────────────────────────────────────────────┤
│  FLOATING ACTION BUTTON (Mobile only)              [+] ← Bottom-right│
└─────────────────────────────────────────────────────────────────────┘

Sidebar Details:
- Width: 240px (desktop), collapsible to 64px (icons only)
- Mobile: Hidden, slides in from left on hamburger tap
- Glass effect with subtle border
- Active filter highlighted with primary gradient
```

#### Task Card Specifications
```
┌──────────────────────────────────────┐
│▌                                      │ ← Priority bar (left edge)
│▌ ☐ Task Title Here                   │ ← Animated checkbox
│▌                                      │
│▌ Brief description text that can     │ ← Max 2 lines, truncate
│▌ span multiple lines...              │
│▌                                      │
│▌ [🏷 tag1] [🏷 tag2]                  │ ← Tag pills
│▌                                      │
│▌ 📅 Due: Today at 5:00 PM            │ ← Due date with icon
│▌                                      │
│▌              [✏️ Edit] [🗑️ Delete]   │ ← Actions (hover reveal)
└──────────────────────────────────────┘

Priority colors:
- High: Red bar (#EF4444)
- Medium: Amber bar (#F59E0B)
- Low: Green bar (#10B981)

Completed state:
- Checkbox checked with animation
- Title has strike-through
- Card opacity reduced to 0.6
- Subtle green tint
```

### 6.5 Add/Edit Task Modal

```
┌────────────────────────────────────────────────────────────┐
│  [BACKDROP - Glass blur, dark overlay]                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  [MODAL - Glass Card, max-w-lg, centered]           │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  ✏️ Add New Task                      [✕]    │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  Title *                                             │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Enter task title...                    45/200 │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  Description                                         │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ Optional description...                       │  │    │
│  │  │                                               │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  Priority                          Category          │    │
│  │  ┌──────────────────┐  ┌──────────────────────┐    │    │
│  │  │ 🔴 High          │  │ 💼 Work              │    │    │
│  │  │ 🟡 Medium ✓      │  │ 🏠 Personal          │    │    │
│  │  │ 🟢 Low           │  │ 🛒 Shopping ✓        │    │    │
│  │  └──────────────────┘  └──────────────────────┘    │    │
│  │                                                      │    │
│  │  Tags (comma-separated)                              │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ [urgent ✕] [review ✕] + Add tag...          │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  Due Date                    Due Time                │    │
│  │  ┌──────────────────┐  ┌──────────────────────┐    │    │
│  │  │ 📅 Pick date...  │  │ 🕐 --:--             │    │    │
│  │  └──────────────────┘  └──────────────────────┘    │    │
│  │                                                      │    │
│  │  ┌────────────────┐  ┌────────────────────────┐    │    │
│  │  │    Cancel      │  │  ✓ Create Task         │    │    │
│  │  └────────────────┘  └────────────────────────┘    │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 7. Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile (xs) | 320-640px | Single column, bottom sheet modals, FAB |
| Tablet (md) | 641-1024px | 2-column grid, side-by-side auth |
| Desktop (lg) | 1025px+ | 3-column grid, full features, side panels |

### Mobile-Specific Adaptations
- Navigation collapses to hamburger menu
- Task grid becomes single column
- Add Task modal becomes bottom sheet
- Touch targets minimum 44px
- Floating action button for add task
- Swipe gestures for task actions

---

## 8. Accessibility Requirements

### WCAG 2.1 AA Compliance
- Color contrast ratios: 4.5:1 minimum for text
- Focus indicators visible on all interactive elements
- Skip to main content link
- ARIA labels on all interactive elements
- Keyboard navigation (Tab, Enter, Escape, Arrow keys)
- Screen reader announcements for dynamic content
- Reduced motion preference respected

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| Tab | Navigate between elements |
| Enter | Activate buttons, submit forms |
| Escape | Close modals, cancel actions |
| N | New task (when on tasks page) |
| / | Focus search |

---

## 9. Performance Requirements

| Metric | Target | Priority |
|--------|--------|----------|
| Lighthouse Performance | 90+ | P0 |
| First Contentful Paint | < 1.5s | P0 |
| Largest Contentful Paint | < 2.5s | P0 |
| Cumulative Layout Shift | < 0.1 | P0 |
| Total Blocking Time | < 200ms | P1 |
| Bundle Size (First Load JS) | < 500KB | P1 |
| Animation Frame Rate | 60fps | P0 |

---

## 10. Files to Modify

### 10.1 New Files to Create
```
frontend/src/components/
├── landing/
│   ├── hero-section.tsx
│   ├── features-section.tsx
│   ├── cta-section.tsx
│   ├── footer.tsx
│   └── floating-orbs.tsx
├── layout/
│   ├── sidebar.tsx              ← New sidebar navigation
│   └── sidebar-item.tsx
├── ui/
│   ├── glass-card.tsx
│   ├── gradient-text.tsx
│   ├── animated-button.tsx
│   └── shimmer-skeleton.tsx
```

### 10.2 Files to Modify
```
frontend/src/app/
├── page.tsx              ← Complete redesign
├── (auth)/
│   ├── layout.tsx        ← Split layout
│   ├── login/page.tsx    ← Glass form
│   └── signup/page.tsx   ← Glass form
├── (dashboard)/
│   ├── layout.tsx        ← Glass header
│   └── tasks/page.tsx    ← Enhanced grid
├── globals.css           ← New CSS variables, glass effects
└── layout.tsx            ← Add fonts

frontend/src/components/
├── layout/
│   └── header.tsx        ← Glass effect, new nav
├── tasks/
│   ├── task-card.tsx     ← Glass, hover effects
│   ├── task-list.tsx     ← Enhanced animations
│   ├── add-task-modal.tsx ← Glass modal
│   ├── edit-task-modal.tsx
│   ├── empty-state.tsx   ← Illustration
│   └── skeleton-card.tsx ← Shimmer effect

frontend/tailwind.config.ts ← New tokens, animations
```

---

## 11. Implementation Priority

### Phase 1: Foundation (P0) - 2 hours
1. Update CSS variables and design tokens in globals.css
2. Update Tailwind config with new colors, animations
3. Create glass-card and gradient-text components
4. Create floating-orbs background component

### Phase 2: Landing Page (P0) - 2 hours
1. Redesign hero section with animations
2. Add features grid with glass cards
3. Add CTA section
4. Add professional footer
5. Add navigation with sign in/sign up buttons

### Phase 3: Auth Pages (P0) - 1.5 hours
1. Update auth layout with split design
2. Redesign login form with glass card
3. Redesign signup form with glass card
4. Add animations and micro-interactions

### Phase 4: Dashboard (P0) - 2 hours
1. Update header with glass effect
2. Redesign task cards with glassmorphism
3. Update filter tabs styling
4. Enhanced empty state
5. Improve loading skeletons

### Phase 5: Modals & Polish (P1) - 1.5 hours
1. Update add/edit task modals
2. Add all micro-interactions
3. Verify responsive behavior
4. Performance optimization
5. Accessibility audit

---

## 12. Acceptance Criteria

### Must Have
- [X] Landing page has prominent Sign In / Get Started buttons
- [X] All pages use glassmorphism effects
- [X] Smooth fade-up animations on all elements
- [X] Dark mode is default, light mode is polished
- [X] Theme toggle is instant and smooth
- [X] Task cards have hover lift effect
- [X] All interactions have micro-animations
- [X] Mobile responsive with 44px touch targets
- [X] Loading states use shimmer skeletons
- [ ] Lighthouse Performance score 90+ (requires manual testing)

### Should Have
- [X] Floating gradient orbs on landing/auth pages
- [X] Gradient text on hero headline
- [X] Features section with 6 glass cards
- [X] Password visibility toggle
- [ ] Character counter on inputs (deferred - not critical)
- [X] Tag chip UI with remove buttons

### Nice to Have
- [ ] Dashboard preview mockup on landing (deferred)
- [X] Social login button styling ("Coming soon" toast)
- [ ] Testimonials section (deferred)
- [X] Activity animations on task completion (🎉 toast)

---

## 13. Constraints

### Technology Constraints
- **Framework**: Next.js 16+ (App Router) - no changes
- **Styling**: Tailwind CSS only - no external CSS libraries
- **Components**: Shadcn/ui - already installed, extend only
- **Animations**: Framer Motion + Tailwind transitions only
- **Icons**: Lucide React only
- **No new dependencies** except fonts (Inter, if not present)

### Functionality Constraints
- **NO changes to**:
  - Authentication logic
  - API endpoints
  - CRUD operations
  - Database schemas
  - Routing logic
  - Form validation logic

- **ONLY modify**:
  - Visual styling
  - Animations
  - Layout structure
  - Component appearance
  - CSS/Tailwind classes

---

## 14. Appendix

### A. Color Palette Reference (OFFICIAL)

```
═══════════════════════════════════════
LUMINA OFFICIAL COLOR THEME
═══════════════════════════════════════

LIGHT THEME:
├── Background:     #EAEFEF
├── Card:           #FFFFFF
├── Border:         #BFC9D1
├── Text Primary:   #25343F
├── Text Secondary: #3D4D5C
├── Accent:         #FF9B51
└── Accent Hover:   #E88A42

DARK THEME (Default):
├── Background:     #25343F
├── Card:           #1A242C
├── Border:         #3D4D5C
├── Text Primary:   #EAEFEF
├── Text Secondary: #BFC9D1
├── Accent:         #FF9B51
└── Accent Hover:   #FFB070

SEMANTIC:
├── Success:        #10B981
├── Warning:        #F59E0B
└── Danger:         #EF4444

❌ DEPRECATED (DO NOT USE):
├── #8B5CF6 (old violet)
├── #6366F1 (old indigo)
├── #06B6D4 (old cyan)
├── #0F172A, #1E293B (old slate)
└── Any gradient combinations
```

### B. Icon Reference (Lucide)
```
Navigation: Home, CheckSquare, Settings, LogOut, User
Tasks: Plus, Edit, Trash2, CheckCircle, Circle
Priority: Flag, AlertCircle
Categories: Briefcase, Home, ShoppingCart, Heart, MoreHorizontal
UI: Search, Moon, Sun, X, ChevronDown, ChevronRight
Features: Zap, Shield, Clock, Smartphone, Palette, Layout
```

### C. Animation Presets (Framer Motion)
```javascript
// Fade up with stagger
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

export const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
  }
};

// Hover lift
export const hoverLift = {
  whileHover: { y: -4, scale: 1.02 },
  transition: { duration: 0.2 }
};

// Modal
export const modalVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 }
};
```

---

**End of Specification**

*This specification preserves all existing functionality while transforming the visual design to international quality standards.*
