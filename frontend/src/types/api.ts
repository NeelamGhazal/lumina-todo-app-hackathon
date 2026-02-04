/**
 * API Contract Types for Phase II Frontend
 * Based on specs/002-phase2-todo-frontend/contracts/api-types.ts
 */

import type { User, Task, TaskPriority, TaskCategory } from "./entities";

// =============================================================================
// API Response Types
// =============================================================================

/**
 * Generic success response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

/**
 * Generic error response
 */
export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, string[]>;
  statusCode?: number;
}

/**
 * Response from registration
 */
export interface RegisterResponse {
  user: User;
  token: string;
}

/**
 * Response from login
 */
export interface LoginResponse {
  user: User;
  token: string;
}

/**
 * Response from session check
 */
export interface SessionResponse {
  user: User;
  expiresAt: string;
}

/**
 * Response from creating a task
 */
export interface CreateTaskResponse {
  task: Task;
}

/**
 * Response from updating a task
 */
export interface UpdateTaskResponse {
  task: Task;
}

/**
 * Response from listing tasks
 */
export interface ListTasksResponse {
  tasks: Task[];
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
}

/**
 * Response from toggling task completion
 */
export interface ToggleCompleteResponse {
  task: Task;
}

/**
 * Response from deleting a task
 */
export interface DeleteTaskResponse {
  success: boolean;
  taskId: string;
}

// =============================================================================
// API Request Types
// =============================================================================

/**
 * Request body for user registration
 */
export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

/**
 * Request body for user login
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Request body for creating a new task
 */
export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority: TaskPriority;
  category: TaskCategory;
  tags?: string[];
  dueDate?: string;
  dueTime?: string;
}

/**
 * Request body for updating an existing task
 */
export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  category?: TaskCategory;
  tags?: string[];
  dueDate?: string | null;
  dueTime?: string | null;
}

/**
 * Query parameters for listing tasks
 */
export interface ListTasksParams {
  status?: "all" | "pending" | "completed";
  category?: TaskCategory;
  priority?: TaskPriority;
  page?: number;
  pageSize?: number;
}

// =============================================================================
// Re-export entity types for convenience
// =============================================================================

export type { User, Task, TaskPriority, TaskCategory };

// =============================================================================
// HTTP Status Codes
// =============================================================================

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// =============================================================================
// Error Codes
// =============================================================================

export const ERROR_CODES = {
  // Authentication errors
  INVALID_CREDENTIALS: "INVALID_CREDENTIALS",
  EMAIL_ALREADY_EXISTS: "EMAIL_ALREADY_EXISTS",
  SESSION_EXPIRED: "SESSION_EXPIRED",
  UNAUTHORIZED: "UNAUTHORIZED",

  // Validation errors
  VALIDATION_ERROR: "VALIDATION_ERROR",
  INVALID_INPUT: "INVALID_INPUT",

  // Task errors
  TASK_NOT_FOUND: "TASK_NOT_FOUND",
  TASK_ACCESS_DENIED: "TASK_ACCESS_DENIED",

  // Generic errors
  INTERNAL_ERROR: "INTERNAL_ERROR",
  NETWORK_ERROR: "NETWORK_ERROR",
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];
