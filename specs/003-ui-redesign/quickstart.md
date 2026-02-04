# Quickstart Guide: Lumina UI Redesign

**Feature**: 003-ui-redesign
**Date**: 2026-01-29
**Prerequisites**: Phase II frontend completed and working

---

## Quick Reference

### Key Files to Modify

```bash
# Configuration
frontend/tailwind.config.ts       # Custom theme
frontend/src/app/globals.css      # CSS variables
frontend/src/app/layout.tsx       # Font + ThemeProvider

# New Components
frontend/src/components/ui/glass-card.tsx
frontend/src/components/ui/gradient-text.tsx
frontend/src/components/landing/hero-section.tsx
frontend/src/components/layout/sidebar.tsx
```

### Design Tokens Quick Copy

```css
/* Add to globals.css */
:root {
  --bg-base: 248 250 252;
  --bg-surface: 255 255 255;
  --bg-elevated: 241 245 249;
  --text-primary: 15 23 42;
  --text-secondary: 71 85 105;
}

.dark {
  --bg-base: 15 23 42;
  --bg-surface: 30 41 59;
  --bg-elevated: 51 65 85;
  --text-primary: 248 250 252;
  --text-secondary: 203 213 225;
}
```

---

## Step-by-Step Setup

### 1. Configure Fonts (5 min)

```typescript
// frontend/src/app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  );
}
```

### 2. Set Up Theme Provider (5 min)

```typescript
// frontend/src/providers/theme-provider.tsx
'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange={false}
    >
      {children}
    </NextThemesProvider>
  );
}
```

Wrap in layout.tsx:

```typescript
import { ThemeProvider } from '@/providers/theme-provider';

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

### 3. Create GlassCard Component (10 min)

```typescript
// frontend/src/components/ui/glass-card.tsx
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  blur?: 'sm' | 'md' | 'lg';
}

export function GlassCard({ children, className, blur = 'md' }: GlassCardProps) {
  const blurMap = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
  };

  return (
    <div
      className={cn(
        'rounded-xl border border-white/10',
        'bg-white/5 dark:bg-slate-800/50',
        blurMap[blur],
        'shadow-glass',
        className
      )}
    >
      {children}
    </div>
  );
}
```

### 4. Create GradientText Component (5 min)

```typescript
// frontend/src/components/ui/gradient-text.tsx
import { cn } from '@/lib/utils';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'span';
}

export function GradientText({
  children,
  className,
  as: Component = 'span'
}: GradientTextProps) {
  return (
    <Component
      className={cn(
        'bg-gradient-to-r from-violet-500 to-indigo-500',
        'bg-clip-text text-transparent',
        className
      )}
    >
      {children}
    </Component>
  );
}
```

### 5. Animation Variants (5 min)

```typescript
// frontend/src/lib/animation-variants.ts
export const fadeUpVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
  },
};

export const staggerContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const hoverLiftVariants = {
  whileHover: { y: -4, scale: 1.02 },
  transition: { duration: 0.2 },
};

export const modalVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};
```

### 6. Extend Tailwind Config (10 min)

```typescript
// frontend/tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
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
          },
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      },
      animation: {
        shimmer: 'shimmer 1.5s infinite',
        float: 'float 6s ease-in-out infinite',
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
      },
      boxShadow: {
        glass: '0 8px 32px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
};

export default config;
```

---

## Common Patterns

### Glass Card with Hover

```tsx
<motion.div
  whileHover={{ y: -4, scale: 1.02 }}
  transition={{ duration: 0.2 }}
>
  <GlassCard className="p-6">
    <h3>Card Title</h3>
    <p>Card content...</p>
  </GlassCard>
</motion.div>
```

### Stagger Animation

```tsx
<motion.div
  variants={staggerContainerVariants}
  initial="hidden"
  animate="visible"
>
  {items.map((item) => (
    <motion.div key={item.id} variants={fadeUpVariants}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

### Theme Toggle

```tsx
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
    >
      {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
}
```

### Floating Orbs

```tsx
export function FloatingOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        className="absolute w-96 h-96 rounded-full blur-[80px] opacity-20"
        style={{
          background: 'rgba(139, 92, 246, 0.3)',
          top: '10%',
          right: '10%',
        }}
      />
      <div
        className="absolute w-72 h-72 rounded-full blur-[80px] opacity-15"
        style={{
          background: 'rgba(6, 182, 212, 0.3)',
          bottom: '20%',
          left: '5%',
        }}
      />
    </div>
  );
}
```

---

## Checklist

- [ ] Tailwind config extended with custom colors
- [ ] Inter font loaded via next/font
- [ ] ThemeProvider wrapping app
- [ ] CSS variables in globals.css
- [ ] GlassCard component created
- [ ] Animation variants file created
- [ ] Theme toggle working

---

## Troubleshooting

### Theme flashing on load
Ensure ThemeProvider has `disableTransitionOnChange={false}` and the html element has `suppressHydrationWarning`.

### Backdrop-filter not working
Check browser support. Add fallback:
```css
@supports not (backdrop-filter: blur(12px)) {
  .glass { background: rgba(30, 41, 59, 0.95); }
}
```

### Animations janky
Use only `transform` and `opacity`. Avoid animating `width`, `height`, `top`, `left`.

### Font not loading
Ensure `variable: '--font-inter'` is set and the class is on the html element.

---

## Resources

- [Framer Motion Docs](https://www.framer.com/motion/)
- [next-themes](https://github.com/pacocoursey/next-themes)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/ui](https://ui.shadcn.com/)
