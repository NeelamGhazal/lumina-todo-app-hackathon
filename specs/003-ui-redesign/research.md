# Research: Lumina UI Redesign

**Feature**: 003-ui-redesign
**Date**: 2026-01-29
**Status**: Complete

---

## 1. Animation Library Selection

### Decision
Use **Framer Motion** for complex animations, **CSS transitions** for simple interactions.

### Rationale
- Framer Motion already installed (`framer-motion: ^11.0.0`)
- Provides spring physics, gesture support, layout animations
- Exit animations (AnimatePresence) essential for modals
- Well-documented, widely adopted in React ecosystem

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| React Spring | Similar API, spring physics | Smaller community | FM already installed |
| GSAP | Powerful, timeline control | License cost for commercial, larger bundle | Overkill for this scope |
| CSS only | No bundle impact | No spring physics, no exit animations | Modal/page transitions need FM |
| Motion One | Smaller, WAAPI-based | Less React integration | FM already installed |

### Implementation Notes
- Use FM for: page transitions, modals, stagger animations, gesture interactions
- Use CSS for: hover states, focus rings, color transitions
- Performance: stick to `transform` and `opacity` for 60fps

---

## 2. Glassmorphism Browser Support

### Decision
Use `backdrop-filter: blur()` with **solid background fallback** for unsupported browsers.

### Rationale
- [caniuse.com](https://caniuse.com/css-backdrop-filter): 96.5% global support
- Safari requires `-webkit-` prefix (handled by Tailwind)
- Only Firefox on Android has partial support issues

### Fallback Strategy
```css
/* Modern browsers */
.glass {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Fallback for unsupported */
@supports not (backdrop-filter: blur(12px)) {
  .glass {
    background: rgba(30, 41, 59, 0.95);
  }
}
```

### Performance Considerations
- Limit to 5-10 glass elements per view
- Avoid on rapidly updating elements (task lists with many items)
- Use for: navigation, modals, sidebar, hero section
- Avoid for: individual task cards (too many)

---

## 3. Font Loading Strategy

### Decision
Use **next/font/google** for Inter font with automatic optimization.

### Rationale
- Built into Next.js 13+, no extra dependencies
- Automatically self-hosts fonts (no external requests)
- Prevents layout shift (font-display: swap handled)
- Subsets automatically for smaller bundle

### Implementation
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export default function RootLayout({ children }) {
  return (
    <html className={inter.variable}>
      ...
    </html>
  );
}
```

### Alternatives Considered
| Alternative | Pros | Cons | Rejected Because |
|-------------|------|------|------------------|
| Self-hosted fonts | Full control | Manual optimization, larger bundle | Extra complexity |
| Google Fonts CDN | Simple | External request, privacy concerns | next/font is better |
| System fonts only | Zero load time | Inconsistent across OS | Brand identity needs custom font |

---

## 4. Theme System Architecture

### Decision
Use **next-themes** library with CSS variables.

### Rationale
- Already installed (`next-themes: ^0.4.4`)
- Handles localStorage persistence automatically
- Prevents flash of unstyled content (FOUC)
- Works with Tailwind's `dark:` modifier
- Supports system preference detection

### Implementation Pattern
```typescript
// providers/theme-provider.tsx
'use client';
import { ThemeProvider } from 'next-themes';

export function Providers({ children }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange={false}
    >
      {children}
    </ThemeProvider>
  );
}
```

### Color Variable Strategy
```css
/* globals.css */
:root {
  --bg-base: 248 250 252;      /* Light mode */
  --bg-surface: 255 255 255;
  --text-primary: 15 23 42;
}

.dark {
  --bg-base: 15 23 42;         /* Dark mode */
  --bg-surface: 30 41 59;
  --text-primary: 248 250 252;
}
```

---

## 5. Sidebar Navigation Patterns

### Decision
Collapsible sidebar with **240px expanded**, **64px collapsed** (icons only), **hidden on mobile** with slide-in drawer.

### Rationale
- Consistent with modern dashboard patterns (Notion, Linear, Vercel)
- Sidebar provides quick access to filters without cluttering header
- Mobile drawer prevents horizontal scroll issues

### Implementation Pattern
```typescript
// State management
const [sidebarOpen, setSidebarOpen] = useState(true);
const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

// Breakpoint detection
const isMobile = useMediaQuery('(max-width: 768px)');
```

### Responsive Behavior
| Breakpoint | Sidebar Behavior |
|------------|------------------|
| < 768px (mobile) | Hidden, hamburger menu opens drawer |
| 768px - 1024px (tablet) | Collapsed (64px, icons only) |
| > 1024px (desktop) | Expanded (240px) by default |

### Animation
- Sidebar collapse: `width` transition 200ms ease-out
- Mobile drawer: slide from left with backdrop

---

## 6. Component Architecture

### Decision
Extend **Shadcn/ui** components with custom variants rather than creating from scratch.

### Rationale
- Shadcn/ui already installed with consistent patterns
- Radix UI primitives provide accessibility for free
- Customization via Tailwind className is straightforward
- Reduces maintenance burden

### New Components to Create
| Component | Base | Customization |
|-----------|------|---------------|
| GlassCard | Card | Add `backdrop-filter`, glass border |
| GradientText | span | Add `bg-gradient-to-r bg-clip-text` |
| AnimatedButton | Button | Add Framer Motion whileHover/whileTap |
| ShimmerSkeleton | Skeleton | Add shimmer animation keyframe |
| FloatingOrbs | div | Absolute positioned blur circles |
| Sidebar | custom | New component for dashboard layout |

### Component Hierarchy
```
layout/
├── sidebar.tsx         (new - dashboard sidebar)
├── header.tsx          (modify - add glass effect)
└── footer.tsx          (new - landing page)

landing/
├── hero-section.tsx    (new)
├── features-section.tsx (new)
├── cta-section.tsx     (new)
└── floating-orbs.tsx   (new)

ui/
├── glass-card.tsx      (new - wraps Card)
├── gradient-text.tsx   (new)
├── shimmer-skeleton.tsx (new - extends Skeleton)
└── animated-button.tsx (new - wraps Button)
```

---

## 7. Performance Budget

### Decision
Maintain **Lighthouse Performance 90+** with specific budgets.

### Budget Allocation
| Resource | Budget | Current | Delta |
|----------|--------|---------|-------|
| First Load JS | < 500KB | ~380KB | +120KB headroom |
| Total CSS | < 100KB | ~50KB | +50KB headroom |
| LCP | < 2.5s | ~1.8s | OK |
| FCP | < 1.5s | ~1.2s | OK |
| CLS | < 0.1 | ~0.05 | OK |

### Framer Motion Impact
- Base bundle: ~80KB gzipped
- Already installed, no additional impact
- Use dynamic imports for heavy animations

### Optimization Strategies
1. Code split landing page animations
2. Lazy load modal content
3. Use CSS for simple transitions
4. Preload critical fonts
5. Optimize images (next/image)

---

## 8. Accessibility Compliance

### Decision
Meet **WCAG 2.1 AA** requirements for all new components.

### Key Requirements
| Requirement | Implementation |
|-------------|----------------|
| Color contrast 4.5:1 | Verify all text/background combos |
| Focus indicators | 2px solid ring, visible in both themes |
| Keyboard navigation | Tab order, Enter/Escape handlers |
| Screen reader | ARIA labels, live regions for toasts |
| Reduced motion | `prefers-reduced-motion` media query |

### Reduced Motion Support
```typescript
// hooks/use-reduced-motion.ts
import { useReducedMotion } from 'framer-motion';

export function useAnimationConfig() {
  const shouldReduceMotion = useReducedMotion();

  return {
    initial: shouldReduceMotion ? false : { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: shouldReduceMotion ? { duration: 0 } : { duration: 0.4 }
  };
}
```

---

## 9. Testing Strategy

### Decision
Focus on **visual regression** and **interaction testing** for UI redesign.

### Test Types
| Type | Tool | Scope |
|------|------|-------|
| Visual regression | Playwright screenshots | All pages, both themes |
| Interaction | Playwright | Modal open/close, sidebar toggle |
| Accessibility | axe-core | WCAG 2.1 AA compliance |
| Performance | Lighthouse CI | Score > 90 |

### Test Coverage
- Landing page renders (both themes)
- Auth pages form interaction
- Dashboard sidebar collapse
- Task card hover effects
- Modal animations
- Theme toggle persistence

---

## 10. Rollback Strategy

### Decision
Feature flag approach with **CSS-only rollback**.

### Implementation
```typescript
// Feature flag (environment variable)
const USE_NEW_UI = process.env.NEXT_PUBLIC_NEW_UI === 'true';

// Component selection
const TaskCard = USE_NEW_UI ? NewTaskCard : LegacyTaskCard;
```

### Rollback Steps
1. Set `NEXT_PUBLIC_NEW_UI=false`
2. Redeploy
3. Old UI restores immediately

### Graceful Degradation
- All functionality preserved regardless of UI
- No API changes required
- Theme preference persists across versions

---

## Summary of Decisions

| Area | Decision | Risk Level |
|------|----------|------------|
| Animation | Framer Motion + CSS | LOW |
| Glassmorphism | backdrop-filter + fallback | LOW |
| Fonts | next/font/google (Inter) | LOW |
| Theme | next-themes with CSS vars | LOW |
| Sidebar | Collapsible + mobile drawer | MEDIUM |
| Components | Extend Shadcn/ui | LOW |
| Performance | Budget 500KB JS, 90+ Lighthouse | MEDIUM |
| Accessibility | WCAG 2.1 AA | LOW |
| Testing | Visual + Interaction | LOW |
| Rollback | Feature flag | LOW |

**All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design.**
