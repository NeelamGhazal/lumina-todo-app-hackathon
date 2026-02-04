# Data Model: Phase II Frontend - Todo Web Application

**Feature**: `002-phase2-todo-frontend`
**Date**: 2026-01-27

## Overview

This document defines the TypeScript interfaces and data structures for the Phase II Frontend. These types are used throughout the application for type safety and API contract validation.

---

## Core Entities

### User

Represents an authenticated user in the system.

```typescript
interface User {
  id: string;           // UUID
  email: string;        // Valid email format
  name?: string;        // Optional display name
  createdAt: string;    // ISO 8601 timestamp
  updatedAt: string;    // ISO 8601 timestamp
}
```

**Validation Rules**:
- `email`: Valid email format, required
- `id`: UUID format, auto-generated

**State Transitions**: N/A (managed by auth system)

---

### Task

The primary entity representing a to-do item.

```typescript
interface Task {
  id: string;                           // UUID
  userId: string;                       // Owner reference
  title: string;                        // 1-200 characters, required
  description?: string;                 // 0-1000 characters, optional
  priority: 'high' | 'medium' | 'low';  // Required, visual color coding
  category: TaskCategory;               // Required, with icon
  tags: string[];                       // Array of tag strings
  dueDate?: string;                     // ISO 8601 date (YYYY-MM-DD)
  dueTime?: string;                     // 24h time format (HH:mm)
  completed: boolean;                   // Completion status
  completedAt?: string;                 // ISO 8601 timestamp when completed
  createdAt: string;                    // ISO 8601 timestamp
  updatedAt: string;                    // ISO 8601 timestamp
}

type TaskCategory = 'work' | 'personal' | 'shopping' | 'health' | 'other';

type TaskPriority = 'high' | 'medium' | 'low';
```

**Validation Rules**:
| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, 1-200 chars | "Title is required" / "Title must be under 200 characters" |
| description | Optional, max 1000 chars | "Description must be under 1000 characters" |
| priority | Required, enum value | "Priority is required" |
| category | Required, enum value | "Category is required" |
| tags | Array, each item string | N/A |
| dueDate | Optional, valid date | "Invalid date format" |
| dueTime | Optional, valid time | "Invalid time format" |

**State Transitions**:
```
┌──────────┐         complete()         ┌───────────┐
│  pending │ ──────────────────────────▶│ completed │
│          │◀────────────────────────── │           │
└──────────┘        uncomplete()        └───────────┘
```

---

### Session

Authentication state tracked in httpOnly cookie (managed by Better Auth).

```typescript
interface Session {
  user: User;
  token: string;        // JWT
  expiresAt: string;    // ISO 8601 timestamp
}
```

**Note**: Session is managed by Better Auth. Frontend accesses user data through auth hooks.

---

## Derived Types

### Task Creation Input

Used when creating a new task.

```typescript
interface CreateTaskInput {
  title: string;
  description?: string;
  priority: TaskPriority;
  category: TaskCategory;
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
}
```

### Task Update Input

Used when updating an existing task (partial update).

```typescript
interface UpdateTaskInput {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  category?: TaskCategory;
  tags?: string[];
  dueDate?: string | null;  // null to clear
  dueTime?: string | null;  // null to clear
}
```

### Task Filter State

Used for filtering the task list.

```typescript
type TaskFilter = 'all' | 'pending' | 'completed';

interface TaskFilterState {
  filter: TaskFilter;
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
}
```

---

## API Response Types

### Success Response

```typescript
interface ApiResponse<T> {
  data: T;
  message?: string;
}
```

### Error Response

```typescript
interface ApiError {
  error: string;
  message: string;
  details?: Record<string, string[]>;  // Field-level errors
}
```

### Paginated Response (Future)

```typescript
interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
}
```

---

## UI State Types

### Modal State

```typescript
interface ModalState {
  isOpen: boolean;
  mode: 'create' | 'edit' | 'delete';
  taskId?: string;  // For edit/delete modes
}
```

### Form State

```typescript
interface FormState {
  isDirty: boolean;
  isSubmitting: boolean;
  errors: Record<string, string>;
}
```

### Optimistic State

```typescript
interface OptimisticTask extends Task {
  _optimistic?: boolean;  // Flag for pending tasks
  _previousState?: Task;  // For rollback
}
```

---

## Zod Schemas

### Task Schema

```typescript
import { z } from 'zod';

export const taskSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be under 200 characters'),
  description: z
    .string()
    .max(1000, 'Description must be under 1000 characters')
    .optional()
    .or(z.literal('')),
  priority: z.enum(['high', 'medium', 'low'], {
    errorMap: () => ({ message: 'Priority is required' }),
  }),
  category: z.enum(['work', 'personal', 'shopping', 'health', 'other'], {
    errorMap: () => ({ message: 'Category is required' }),
  }),
  tags: z.array(z.string()).optional().default([]),
  dueDate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format')
    .optional()
    .or(z.literal('')),
  dueTime: z
    .string()
    .regex(/^\d{2}:\d{2}$/, 'Invalid time format')
    .optional()
    .or(z.literal('')),
});

export type TaskFormData = z.infer<typeof taskSchema>;
```

### Auth Schemas

```typescript
export const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const signupSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type SignupFormData = z.infer<typeof signupSchema>;
```

---

## Constants

### Priority Colors

```typescript
export const PRIORITY_COLORS = {
  high: {
    bg: 'bg-red-100 dark:bg-red-900/30',
    text: 'text-red-700 dark:text-red-400',
    border: 'border-red-200 dark:border-red-800',
  },
  medium: {
    bg: 'bg-yellow-100 dark:bg-yellow-900/30',
    text: 'text-yellow-700 dark:text-yellow-400',
    border: 'border-yellow-200 dark:border-yellow-800',
  },
  low: {
    bg: 'bg-green-100 dark:bg-green-900/30',
    text: 'text-green-700 dark:text-green-400',
    border: 'border-green-200 dark:border-green-800',
  },
} as const;
```

### Category Icons

```typescript
import { Briefcase, User, ShoppingCart, Heart, MoreHorizontal } from 'lucide-react';

export const CATEGORY_ICONS = {
  work: Briefcase,
  personal: User,
  shopping: ShoppingCart,
  health: Heart,
  other: MoreHorizontal,
} as const;

export const CATEGORY_LABELS = {
  work: 'Work',
  personal: 'Personal',
  shopping: 'Shopping',
  health: 'Health',
  other: 'Other',
} as const;
```

---

## Entity Relationships

```
┌──────────┐
│   User   │
├──────────┤
│ id (PK)  │
│ email    │
└────┬─────┘
     │
     │ 1:N (owns)
     │
     ▼
┌──────────────┐
│     Task     │
├──────────────┤
│ id (PK)      │
│ userId (FK)  │
│ title        │
│ description  │
│ priority     │
│ category     │
│ tags[]       │
│ dueDate      │
│ dueTime      │
│ completed    │
│ completedAt  │
│ createdAt    │
│ updatedAt    │
└──────────────┘
```

---

**Data Model Version**: 1.0.0 | **Created**: 2026-01-27
