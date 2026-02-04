# Data Model: Lumina UI Redesign

**Feature**: 003-ui-redesign
**Date**: 2026-01-29
**Type**: Frontend-Only (No backend changes)

---

## Overview

This feature is **UI-only** - no changes to database schema or API contracts. All data models remain unchanged from Phase II.

---

## 1. Design Token Model

### Color Tokens (CSS Variables)

```typescript
// types/design-tokens.ts

export interface ColorTokens {
  // Primary
  primary: {
    gradient: string;      // 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)'
    500: string;           // '#8B5CF6'
    600: string;           // '#7C3AED'
    700: string;           // '#6D28D9'
  };

  // Accent
  accent: {
    400: string;           // '#22D3EE'
    500: string;           // '#06B6D4'
  };

  // Semantic
  success: { 400: string; 500: string };
  warning: { 400: string; 500: string };
  danger: { 400: string; 500: string };

  // Background (theme-dependent)
  bg: {
    base: string;          // Dark: '#0F172A', Light: '#F8FAFC'
    surface: string;       // Dark: '#1E293B', Light: '#FFFFFF'
    elevated: string;      // Dark: '#334155', Light: '#F1F5F9'
    overlay: string;       // Dark: 'rgba(15,23,42,0.8)', Light: 'rgba(255,255,255,0.8)'
  };

  // Text (theme-dependent)
  text: {
    primary: string;       // Dark: '#F8FAFC', Light: '#0F172A'
    secondary: string;     // Dark: '#CBD5E1', Light: '#475569'
    muted: string;         // Dark: '#64748B', Light: '#94A3B8'
  };
}
```

### Animation Tokens

```typescript
// types/animation-tokens.ts

export interface AnimationTokens {
  duration: {
    instant: string;       // '100ms'
    fast: string;          // '200ms'
    normal: string;        // '300ms'
    slow: string;          // '400ms'
    slower: string;        // '500ms'
  };

  easing: {
    default: number[];     // [0.4, 0, 0.2, 1]
    in: number[];          // [0.4, 0, 1, 1]
    out: number[];         // [0, 0, 0.2, 1]
    inOut: number[];       // [0.4, 0, 0.2, 1]
    spring: number[];      // [0.34, 1.56, 0.64, 1]
  };
}
```

### Spacing Tokens

```typescript
// types/spacing-tokens.ts

export interface SpacingTokens {
  1: string;   // '4px' / '0.25rem'
  2: string;   // '8px' / '0.5rem'
  3: string;   // '12px' / '0.75rem'
  4: string;   // '16px' / '1rem'
  5: string;   // '20px' / '1.25rem'
  6: string;   // '24px' / '1.5rem'
  8: string;   // '32px' / '2rem'
  10: string;  // '40px' / '2.5rem'
  12: string;  // '48px' / '3rem'
  16: string;  // '64px' / '4rem'
  20: string;  // '80px' / '5rem'
  24: string;  // '96px' / '6rem'
}
```

---

## 2. Component Props Models

### GlassCard Props

```typescript
// components/ui/glass-card.tsx

export interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'overlay';
  blur?: 'sm' | 'md' | 'lg';        // 8px | 12px | 16px
  border?: boolean;                  // Show glass border
  hoverEffect?: boolean;             // Enable lift on hover
  animate?: boolean;                 // Enable fade-in animation
}
```

### GradientText Props

```typescript
// components/ui/gradient-text.tsx

export interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'accent' | 'custom';
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'span' | 'p';
  animate?: boolean;                 // Enable shimmer animation
}
```

### AnimatedButton Props

```typescript
// components/ui/animated-button.tsx

export interface AnimatedButtonProps extends ButtonProps {
  hoverScale?: number;               // Default: 1.02
  hoverY?: number;                   // Default: -2
  tapScale?: number;                 // Default: 0.98
  loading?: boolean;                 // Show loading spinner
  loadingText?: string;              // Text during loading
}
```

### Sidebar Props

```typescript
// components/layout/sidebar.tsx

export interface SidebarProps {
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
  mobileOpen?: boolean;
  onMobileOpenChange?: (open: boolean) => void;
}

export interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  badge?: number | string;
  collapsed?: boolean;
}
```

### FloatingOrbs Props

```typescript
// components/landing/floating-orbs.tsx

export interface FloatingOrbsProps {
  variant?: 'hero' | 'auth' | 'subtle';
  animate?: boolean;
  className?: string;
}

export interface OrbConfig {
  size: number;                      // px
  color: string;                     // rgba color
  position: { x: string; y: string }; // percentage
  blur: number;                      // px
  animation?: {
    duration: number;
    delay: number;
  };
}
```

### ShimmerSkeleton Props

```typescript
// components/ui/shimmer-skeleton.tsx

export interface ShimmerSkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  lines?: number;                    // For text variant
  animate?: boolean;                 // Enable shimmer
}
```

---

## 3. State Models

### Theme State

```typescript
// Already handled by next-themes
// Access via useTheme() hook

interface ThemeState {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: string) => void;
  resolvedTheme: 'light' | 'dark';
}
```

### Sidebar State

```typescript
// hooks/use-sidebar.ts

interface SidebarState {
  isCollapsed: boolean;
  isMobileOpen: boolean;
  toggle: () => void;
  collapse: () => void;
  expand: () => void;
  openMobile: () => void;
  closeMobile: () => void;
}
```

### Animation Preferences

```typescript
// hooks/use-animation-preferences.ts

interface AnimationPreferences {
  reducedMotion: boolean;            // From prefers-reduced-motion
  animationsEnabled: boolean;        // User preference (localStorage)
  getAnimationProps: (defaultProps: object) => object;
}
```

---

## 4. Existing Models (Unchanged)

### Task Model (No Changes)

```typescript
// types/entities.ts - UNCHANGED
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  category?: string;
  tags?: string[];
  due_date?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}
```

### User Model (No Changes)

```typescript
// types/entities.ts - UNCHANGED
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}
```

---

## 5. Tailwind Configuration Model

```typescript
// tailwind.config.ts extension

const config = {
  theme: {
    extend: {
      colors: {
        // Custom Lumina palette
        lumina: {
          primary: {
            DEFAULT: '#8B5CF6',
            500: '#8B5CF6',
            600: '#7C3AED',
            700: '#6D28D9',
          },
          accent: {
            DEFAULT: '#06B6D4',
            400: '#22D3EE',
            500: '#06B6D4',
          },
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      },
      animation: {
        'shimmer': 'shimmer 1.5s infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { opacity: '0.5' },
          '100%': { opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.12)',
        'glass-lg': '0 16px 48px rgba(0, 0, 0, 0.16)',
      },
    },
  },
};
```

---

## Summary

| Model Type | Status | Notes |
|------------|--------|-------|
| Design Tokens | NEW | CSS variables, TypeScript types |
| Component Props | NEW | GlassCard, GradientText, Sidebar, etc. |
| State Models | NEW | Sidebar state, animation preferences |
| Existing Models | UNCHANGED | Task, User, API types |
| Tailwind Config | EXTENDED | Colors, animations, shadows |

**No database migrations required. No API contract changes.**
