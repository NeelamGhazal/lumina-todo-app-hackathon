/**
 * Core Entity Types for Phase II Frontend
 * Based on specs/002-phase2-todo-frontend/data-model.md
 */

// =============================================================================
// Enums
// =============================================================================

/**
 * Task priority levels with visual color coding
 */
export type TaskPriority = "high" | "medium" | "low";

/**
 * Task category types with associated icons
 */
export type TaskCategory = "work" | "personal" | "shopping" | "health" | "other";

/**
 * Task filter options
 */
export type TaskFilter = "all" | "pending" | "completed";

// =============================================================================
// Core Entities
// =============================================================================

/**
 * Represents an authenticated user
 */
export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Represents a to-do task
 */
export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  category: TaskCategory;
  tags: string[];
  dueDate?: string;
  dueTime?: string;
  completed: boolean;
  completedAt?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Authentication session
 */
export interface Session {
  user: User;
  token: string;
  expiresAt: string;
}

// =============================================================================
// Derived Types
// =============================================================================

/**
 * Task with optimistic update flags
 */
export interface OptimisticTask extends Task {
  _optimistic?: boolean;
  _previousState?: Task;
}

/**
 * Task filter state with counts
 */
export interface TaskFilterState {
  filter: TaskFilter;
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
}

// =============================================================================
// UI State Types
// =============================================================================

/**
 * Modal state for task operations
 */
export interface ModalState {
  isOpen: boolean;
  mode: "create" | "edit" | "delete";
  taskId?: string;
}

/**
 * Form state for validation
 */
export interface FormState {
  isDirty: boolean;
  isSubmitting: boolean;
  errors: Record<string, string>;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Priority colors for UI
 */
export const PRIORITY_COLORS = {
  high: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    border: "border-red-200 dark:border-red-800",
  },
  medium: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    border: "border-yellow-200 dark:border-yellow-800",
  },
  low: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    border: "border-green-200 dark:border-green-800",
  },
} as const;

/**
 * Category labels for UI
 */
export const CATEGORY_LABELS = {
  work: "Work",
  personal: "Personal",
  shopping: "Shopping",
  health: "Health",
  other: "Other",
} as const;

/**
 * Priority labels for UI
 */
export const PRIORITY_LABELS = {
  high: "High",
  medium: "Medium",
  low: "Low",
} as const;
