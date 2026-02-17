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
// Password Reset Types
// =============================================================================

/**
 * Request body for forgot password
 */
export interface ForgotPasswordRequest {
  email: string;
}

/**
 * Response from forgot password
 */
export interface ForgotPasswordResponse {
  message: string;
}

/**
 * Response from verify reset token
 */
export interface VerifyTokenResponse {
  valid: boolean;
  email: string | null;
  error?: string;
}

/**
 * Request body for reset password
 */
export interface ResetPasswordRequest {
  token: string;
  password: string;
  password_confirm: string;
}

/**
 * Response from reset password
 */
export interface ResetPasswordResponse {
  success: boolean;
  message: string;
}

// =============================================================================
// Notification Types
// =============================================================================

/**
 * Notification type enum
 */
export type NotificationType = "TASK_DUE_SOON" | "TASK_OVERDUE" | "TASK_COMPLETED";

/**
 * Notification entity
 */
export interface Notification {
  id: string;
  userId: string;
  taskId?: string | null;
  type: NotificationType;
  message: string;
  isRead: boolean;
  createdAt: string;
}

/**
 * Response from listing notifications
 */
export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unreadCount: number;
}

/**
 * Response from getting unread count
 */
export interface UnreadCountResponse {
  count: number;
}

/**
 * Response from clearing notifications
 */
export interface ClearNotificationsResponse {
  success: boolean;
  deletedCount: number;
}

/**
 * Response from triggering notification job
 */
export interface TriggerJobResponse {
  dueSoonCount: number;
  overdueCount: number;
}

// =============================================================================
// OAuth Types (specs/010-oauth-social-login)
// =============================================================================

/**
 * OAuth provider type
 */
export type OAuthProvider = "google" | "github";

/**
 * Request body for OAuth login
 */
export interface OAuthLoginRequest {
  provider: OAuthProvider;
  provider_id: string;
  email: string;
  name?: string | null;
  image_url?: string | null;
}

/**
 * OAuth user info in response
 */
export interface OAuthUser {
  id: string;
  email: string;
  name?: string | null;
  is_new_user: boolean;
}

/**
 * Response from OAuth login
 */
export interface OAuthLoginResponse {
  access_token: string;
  token_type: "bearer";
  user: OAuthUser;
}

// =============================================================================
// Error Codes
// =============================================================================

export const ERROR_CODES = {
  // Authentication errors
  INVALID_CREDENTIALS: "INVALID_CREDENTIALS",
  EMAIL_ALREADY_EXISTS: "EMAIL_ALREADY_EXISTS",
  SESSION_EXPIRED: "SESSION_EXPIRED",
  UNAUTHORIZED: "UNAUTHORIZED",
  OAUTH_ACCOUNT: "OAUTH_ACCOUNT",
  INVALID_PROVIDER: "INVALID_PROVIDER",

  // Password reset errors
  RATE_LIMIT_EXCEEDED: "RATE_LIMIT_EXCEEDED",
  INVALID_TOKEN: "INVALID_TOKEN",
  TOKEN_EXPIRED: "TOKEN_EXPIRED",
  TOKEN_USED: "TOKEN_USED",
  PASSWORD_MISMATCH: "PASSWORD_MISMATCH",
  INVALID_PASSWORD: "INVALID_PASSWORD",

  // HTTP Status codes as error codes
  TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",

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
