# Research: Phase II Frontend - Todo Web Application

**Feature**: `002-phase2-todo-frontend`
**Date**: 2026-01-27
**Status**: Complete

## Research Summary

All technical decisions have been researched and resolved. No NEEDS CLARIFICATION items remain.

---

## 1. Next.js 16 App Router Best Practices

### Decision
Use App Router with Server Components as default, Client Components only for interactivity.

### Rationale
- Server Components reduce JavaScript bundle sent to client
- Built-in `loading.tsx` and `error.tsx` conventions
- Improved SEO through server-side rendering
- Native support for streaming and Suspense
- Route groups `(auth)` and `(dashboard)` for layout separation

### Key Patterns
```typescript
// Server Component (default) - for data fetching
async function TasksPage() {
  const tasks = await fetchTasks();
  return <TaskList initialTasks={tasks} />;
}

// Client Component - for interactivity
'use client';
function TaskCard({ task }: { task: Task }) {
  const [isComplete, setIsComplete] = useState(task.completed);
  // ...
}
```

### Alternatives Considered
- Pages Router: Legacy, not recommended for new projects
- Remix: Good alternative but constitution mandates Next.js

---

## 2. Better Auth Integration with Next.js 16

### Decision
Use Better Auth with `@better-auth/nextjs` package for App Router integration.

### Rationale
- Constitution mandates Better Auth
- Native App Router support
- JWT in httpOnly cookies (more secure than localStorage)
- Middleware support for protected routes

### Implementation Pattern
```typescript
// lib/auth.ts
import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  emailAndPassword: { enabled: true },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,     // 1 day
  },
});

// middleware.ts
import { authMiddleware } from '@better-auth/nextjs';

export default authMiddleware({
  publicRoutes: ['/login', '/signup'],
});
```

### Alternatives Considered
- NextAuth.js: Popular but constitution mandates Better Auth
- Clerk: Third-party hosted, not needed

---

## 3. Optimistic Updates Strategy

### Decision
Custom hook with rollback on failure, error toast with retry button.

### Rationale
- Per clarification session: "Revert UI silently + show error toast with retry button"
- Simpler than TanStack Query for this scope
- Full control over rollback behavior

### Implementation Pattern
```typescript
// hooks/use-optimistic.ts
function useOptimisticMutation<T, R>({
  mutationFn,
  onSuccess,
  onError,
}: OptimisticOptions<T, R>) {
  const [pending, setPending] = useState<T | null>(null);

  const mutate = async (data: T) => {
    const previousState = /* capture current state */;
    setPending(data); // Optimistic update

    try {
      const result = await mutationFn(data);
      onSuccess?.(result);
    } catch (error) {
      // Revert silently
      setPending(null);
      onError?.(error, () => mutate(data)); // Pass retry function
      toast.error('Operation failed', {
        action: { label: 'Retry', onClick: () => mutate(data) }
      });
    }
  };

  return { mutate, pending };
}
```

### Alternatives Considered
- TanStack Query: More features but adds dependency
- SWR: Good but optimistic updates less intuitive

---

## 4. Framer Motion Animation Patterns

### Decision
Framer Motion for complex animations (layout, exit), CSS for simple ones (hover, transitions).

### Rationale
- ~25KB bundle cost justified by animation quality
- Layout prop essential for task reordering
- AnimatePresence for exit animations
- Spring physics for natural feel

### Animation Specifications

| Animation | Implementation | Duration | Easing |
|-----------|----------------|----------|--------|
| Modal open | `scale: [0.95, 1], opacity: [0, 1]` | 300ms | spring |
| Modal close | `scale: [1, 0.95], opacity: [1, 0]` | 200ms | ease-out |
| Card entrance | `y: [20, 0], opacity: [0, 1]` | 300ms | ease-out |
| Card stagger | `staggerChildren: 0.08` | 80ms/item | - |
| Task reorder | `layout` prop | 300ms | spring |
| Checkbox | SVG pathLength animation | 200ms | spring |

### Alternatives Considered
- React Spring: Similar capabilities, less popular
- CSS only: Insufficient for layout animations
- GSAP: Overkill, larger bundle

---

## 5. Shadcn/ui Component Strategy

### Decision
Install only needed components, customize with Tailwind.

### Components Needed
| Component | Purpose |
|-----------|---------|
| button | Actions throughout |
| input | Form fields |
| card | Task cards |
| dialog | Modal base |
| checkbox | Task completion |
| select | Category, priority |
| calendar | Date picker |
| badge | Priority, status |
| skeleton | Loading states |

### Custom Components Required
| Component | Reason |
|-----------|--------|
| bottom-sheet | Mobile modal variant |
| animated-checkbox | Checkmark draw effect |
| tag-input | Comma-separated tags |
| task-card | Complex composition |

### Alternatives Considered
- Chakra UI: Larger bundle, runtime CSS
- MUI: Conflicts with Tailwind, larger
- Build from scratch: Too time-consuming

---

## 6. Form Validation Strategy

### Decision
React Hook Form + Zod with validation on blur and submit.

### Rationale
- Per clarification: "On blur + on submit attempt (balanced approach)"
- Zod schemas reusable for API type checking
- Minimal re-renders with RHF

### Validation Schemas
```typescript
// lib/validations.ts
import { z } from 'zod';

export const taskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be under 200 characters'),
  description: z.string()
    .max(1000, 'Description must be under 1000 characters')
    .optional(),
  priority: z.enum(['high', 'medium', 'low']),
  category: z.enum(['work', 'personal', 'shopping', 'health', 'other']),
  tags: z.array(z.string()).optional(),
  dueDate: z.string().optional(),
  dueTime: z.string().optional(),
});

export const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});
```

---

## 7. Dark Mode Implementation

### Decision
CSS variables with system preference detection and localStorage persistence.

### Rationale
- Per clarification: "Respect system preference initially, allow manual override that persists"
- CSS variables enable smooth transitions
- No FOUC with `suppressHydrationWarning`

### Implementation Pattern
```typescript
// hooks/use-theme.ts
export function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    if (stored) {
      setTheme(stored as 'light' | 'dark');
    } else {
      // Use system preference
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', systemDark);
    }
  }, []);

  const toggle = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return { theme, toggle };
}
```

---

## 8. Responsive Modal Strategy

### Decision
Center modal on desktop (>640px), bottom sheet on mobile (<=640px).

### Rationale
- Per clarification: "Center modal on desktop, bottom sheet on mobile (adaptive)"
- Uses CSS media query with Radix Dialog base
- Better mobile UX with thumb-reachable bottom sheet

### Implementation Pattern
```typescript
// components/ui/adaptive-dialog.tsx
'use client';
import * as Dialog from '@radix-ui/react-dialog';
import { motion } from 'framer-motion';

export function AdaptiveDialog({ children, ...props }) {
  return (
    <Dialog.Root {...props}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className={cn(
          // Mobile: bottom sheet
          "fixed inset-x-0 bottom-0 rounded-t-2xl",
          // Desktop: center modal
          "md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:rounded-xl"
        )}>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

---

## 9. Toast Notification System

### Decision
Sonner library with top-center positioning.

### Rationale
- Per clarification: "Top-center (high visibility, modern pattern)"
- Sonner is lightweight (~5KB) and accessible
- Built-in action support for retry/undo

### Implementation Pattern
```typescript
// app/providers.tsx
import { Toaster } from 'sonner';

export function Providers({ children }) {
  return (
    <>
      {children}
      <Toaster position="top-center" richColors />
    </>
  );
}

// Usage
import { toast } from 'sonner';

// Success
toast.success('Task created!');

// Error with retry
toast.error('Failed to create task', {
  action: {
    label: 'Retry',
    onClick: () => createTask(data),
  },
});

// Undo (5 second window)
toast('Task deleted', {
  action: {
    label: 'Undo',
    onClick: () => restoreTask(taskId),
  },
  duration: 5000,
});
```

---

## 10. Testing Strategy

### Decision
Vitest for unit/integration, Playwright for E2E.

### Rationale
- Vitest: Faster than Jest, native ESM support
- Playwright: Reliable cross-browser E2E
- Testing Library: Component testing best practices

### Test Structure
```
tests/
├── unit/
│   ├── validations.test.ts    # Zod schemas
│   ├── utils.test.ts          # Utility functions
│   └── hooks.test.ts          # Custom hooks
├── integration/
│   ├── auth.test.tsx          # Auth flow
│   └── tasks.test.tsx         # CRUD operations
└── e2e/
    ├── auth.spec.ts           # Login/signup flows
    ├── tasks.spec.ts          # Task operations
    └── accessibility.spec.ts  # A11y checks
```

### Coverage Targets
| Area | Target |
|------|--------|
| Validations | 95% |
| Utils | 95% |
| Hooks | 85% |
| Components | 75% |
| E2E critical paths | 100% |

---

## Conclusion

All research items resolved. No NEEDS CLARIFICATION markers remain. Ready to proceed with data model and contracts generation.

---

**Research Version**: 1.0.0 | **Completed**: 2026-01-27
