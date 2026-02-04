# Quickstart Guide: Phase II Frontend

**Feature**: `002-phase2-todo-frontend`
**Date**: 2026-01-27

## Prerequisites

- Node.js 20+ (LTS recommended)
- pnpm 8+ (or npm/yarn)
- Git

## Quick Setup

### 1. Initialize Project

```bash
# From repository root
cd /mnt/e/evolution-todo

# Create frontend directory
mkdir -p frontend
cd frontend

# Initialize Next.js 16 with TypeScript
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Answer prompts:
# ✓ Would you like to use TypeScript? Yes
# ✓ Would you like to use ESLint? Yes
# ✓ Would you like to use Tailwind CSS? Yes
# ✓ Would you like to use `src/` directory? Yes
# ✓ Would you like to use App Router? Yes
# ✓ Would you like to customize the default import alias? No
```

### 2. Install Dependencies

```bash
# Core dependencies
pnpm add framer-motion react-hook-form @hookform/resolvers zod
pnpm add lucide-react sonner clsx tailwind-merge date-fns

# Better Auth
pnpm add better-auth @better-auth/nextjs

# Shadcn/ui setup
pnpm dlx shadcn@latest init

# Answer shadcn prompts:
# ✓ Which style would you like to use? Default
# ✓ Which color would you like to use as base color? Slate
# ✓ Would you like to use CSS variables? Yes

# Install needed shadcn components
pnpm dlx shadcn@latest add button input card dialog checkbox select calendar badge skeleton
```

### 3. Development Dependencies

```bash
# Testing
pnpm add -D vitest @testing-library/react @testing-library/jest-dom
pnpm add -D @playwright/test

# Type checking
pnpm add -D @types/node @types/react @types/react-dom
```

### 4. Environment Setup

```bash
# Create environment file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
BETTER_AUTH_SECRET=your-32-character-secret-here
BETTER_AUTH_URL=http://localhost:3000
EOF

# Create example for version control
cat > .env.example << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
BETTER_AUTH_SECRET=<generate-32-char-secret>
BETTER_AUTH_URL=http://localhost:3000
EOF
```

### 5. Configure TypeScript Strict Mode

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true,
    // ... rest of config
  }
}
```

### 6. Configure Tailwind Theme

Update `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary gradient
        primary: {
          DEFAULT: '#8B5CF6',
          50: '#F5F3FF',
          100: '#EDE9FE',
          // ... full scale
          900: '#4C1D95',
        },
        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Poppins', 'sans-serif'],
      },
      animation: {
        'shimmer': 'shimmer 1.5s infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

### 7. Run Development Server

```bash
pnpm dev
```

Visit http://localhost:3000

---

## Project Structure Overview

After setup, your structure should look like:

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/           # Public routes
│   │   ├── (dashboard)/      # Protected routes
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Home page
│   ├── components/
│   │   ├── ui/               # Shadcn components
│   │   ├── tasks/            # Task components
│   │   ├── auth/             # Auth components
│   │   └── layout/           # Layout components
│   ├── lib/
│   │   ├── api/              # API client
│   │   ├── auth.ts           # Better Auth config
│   │   ├── utils.ts          # Utilities
│   │   └── validations.ts    # Zod schemas
│   ├── hooks/                # Custom hooks
│   └── types/                # TypeScript types
├── tests/
├── public/
├── .env.local
├── .env.example
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm start` | Start production server |
| `pnpm lint` | Run ESLint |
| `pnpm test` | Run unit tests |
| `pnpm test:e2e` | Run E2E tests |

---

## Common Tasks

### Add a new Shadcn component

```bash
pnpm dlx shadcn@latest add [component-name]
```

### Generate Better Auth types

```bash
# After configuring auth, generate types
pnpm better-auth generate
```

### Run Lighthouse audit

```bash
pnpm build && pnpm start
# Then use Chrome DevTools Lighthouse tab
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
```

### Tailwind classes not working

Check that `content` paths in `tailwind.config.ts` include your component directories.

### Better Auth session issues

Ensure `BETTER_AUTH_SECRET` is at least 32 characters and consistent between `.env.local` and production.

---

## Next Steps

1. Read through `plan.md` for implementation phases
2. Review `data-model.md` for TypeScript interfaces
3. Check `contracts/api-types.ts` for API contract
4. Run `/sp.tasks` to generate atomic task breakdown
5. Begin Phase 1 implementation

---

**Quickstart Version**: 1.0.0 | **Created**: 2026-01-27
