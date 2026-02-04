/**
 * Zod Validation Schemas for Phase II Frontend
 * Based on specs/002-phase2-todo-frontend/data-model.md
 */

import { z } from "zod";

// =============================================================================
// Task Schemas
// =============================================================================

/**
 * Task creation/update form schema
 */
export const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be under 200 characters"),
  description: z
    .string()
    .max(1000, "Description must be under 1000 characters")
    .optional()
    .or(z.literal("")),
  priority: z.enum(["high", "medium", "low"], {
    errorMap: () => ({ message: "Priority is required" }),
  }),
  category: z.enum(["work", "personal", "shopping", "health", "other"], {
    errorMap: () => ({ message: "Category is required" }),
  }),
  tags: z.array(z.string()).optional().default([]),
  dueDate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date format")
    .optional()
    .or(z.literal("")),
  dueTime: z
    .string()
    .regex(/^\d{2}:\d{2}$/, "Invalid time format")
    .optional()
    .or(z.literal("")),
});

export type TaskFormData = z.infer<typeof taskSchema>;

// =============================================================================
// Auth Schemas
// =============================================================================

/**
 * Login form schema
 */
export const loginSchema = z.object({
  email: z.string().email("Invalid email format"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Signup form schema
 */
export const signupSchema = z
  .object({
    email: z.string().email("Invalid email format"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
    name: z.string().optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

export type SignupFormData = z.infer<typeof signupSchema>;

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Parse tags from comma-separated string
 */
export function parseTags(tagsString: string): string[] {
  return tagsString
    .split(",")
    .map((tag) => tag.trim())
    .filter((tag) => tag.length > 0);
}

/**
 * Format tags to comma-separated string
 */
export function formatTags(tags: string[]): string {
  return tags.join(", ");
}
