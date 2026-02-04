/**
 * API Contract Types for Phase II Frontend
 *
 * This file defines the TypeScript interfaces for all API interactions
 * between the frontend and backend. These types serve as the contract
 * that both teams agree upon.
 *
 * @module contracts/api-types
 * @version 1.0.0
 */

// =============================================================================
// Core Entity Types
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
 * Task priority levels with visual color coding
 */
export type TaskPriority = 'high' | 'medium' | 'low';

/**
 * Task category types with associated icons
 */
export type TaskCategory = 'work' | 'personal' | 'shopping' | 'health' | 'other';

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
  dueDate?: string;      // ISO 8601 date: YYYY-MM-DD
  dueTime?: string;      // 24h format: HH:mm
  completed: boolean;
  completedAt?: string;  // ISO 8601 datetime
  createdAt: string;     // ISO 8601 datetime
  updatedAt: string;     // ISO 8601 datetime
}

// =============================================================================
// API Request Types
// =============================================================================

/**
 * Request body for user registration
 * POST /api/auth/register
 */
export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
}

/**
 * Request body for user login
 * POST /api/auth/login
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Request body for creating a new task
 * POST /api/tasks
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
 * PUT /api/tasks/{id}
 */
export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  category?: TaskCategory;
  tags?: string[];
  dueDate?: string | null;  // null to clear
  dueTime?: string | null;  // null to clear
}

/**
 * Query parameters for listing tasks
 * GET /api/tasks
 */
export interface ListTasksParams {
  status?: 'all' | 'pending' | 'completed';
  category?: TaskCategory;
  priority?: TaskPriority;
  page?: number;
  pageSize?: number;
}

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
 * POST /api/auth/register
 */
export interface RegisterResponse {
  user: User;
  token: string;
}

/**
 * Response from login
 * POST /api/auth/login
 */
export interface LoginResponse {
  user: User;
  token: string;
}

/**
 * Response from session check
 * GET /api/auth/session
 */
export interface SessionResponse {
  user: User;
  expiresAt: string;
}

/**
 * Response from creating a task
 * POST /api/tasks
 */
export interface CreateTaskResponse {
  task: Task;
}

/**
 * Response from updating a task
 * PUT /api/tasks/{id}
 */
export interface UpdateTaskResponse {
  task: Task;
}

/**
 * Response from listing tasks
 * GET /api/tasks
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
 * PATCH /api/tasks/{id}/complete
 */
export interface ToggleCompleteResponse {
  task: Task;
}

/**
 * Response from deleting a task
 * DELETE /api/tasks/{id}
 */
export interface DeleteTaskResponse {
  success: boolean;
  taskId: string;
}

// =============================================================================
// API Endpoint Definitions
// =============================================================================

/**
 * API Endpoint definitions for documentation
 */
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    register: {
      method: 'POST',
      path: '/api/auth/register',
      request: 'RegisterRequest',
      response: 'RegisterResponse',
      description: 'Create a new user account',
    },
    login: {
      method: 'POST',
      path: '/api/auth/login',
      request: 'LoginRequest',
      response: 'LoginResponse',
      description: 'Authenticate user and receive JWT',
    },
    logout: {
      method: 'POST',
      path: '/api/auth/logout',
      request: null,
      response: '{ success: boolean }',
      description: 'Invalidate current session',
    },
    session: {
      method: 'GET',
      path: '/api/auth/session',
      request: null,
      response: 'SessionResponse',
      description: 'Get current session info',
    },
  },

  // Tasks
  tasks: {
    list: {
      method: 'GET',
      path: '/api/tasks',
      request: 'ListTasksParams (query)',
      response: 'ListTasksResponse',
      description: 'List all tasks for authenticated user',
    },
    create: {
      method: 'POST',
      path: '/api/tasks',
      request: 'CreateTaskRequest',
      response: 'CreateTaskResponse',
      description: 'Create a new task',
    },
    get: {
      method: 'GET',
      path: '/api/tasks/{id}',
      request: null,
      response: '{ task: Task }',
      description: 'Get a single task by ID',
    },
    update: {
      method: 'PUT',
      path: '/api/tasks/{id}',
      request: 'UpdateTaskRequest',
      response: 'UpdateTaskResponse',
      description: 'Update an existing task',
    },
    delete: {
      method: 'DELETE',
      path: '/api/tasks/{id}',
      request: null,
      response: 'DeleteTaskResponse',
      description: 'Delete a task',
    },
    toggleComplete: {
      method: 'PATCH',
      path: '/api/tasks/{id}/complete',
      request: null,
      response: 'ToggleCompleteResponse',
      description: 'Toggle task completion status',
    },
  },
} as const;

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
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  EMAIL_ALREADY_EXISTS: 'EMAIL_ALREADY_EXISTS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',
  UNAUTHORIZED: 'UNAUTHORIZED',

  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',

  // Task errors
  TASK_NOT_FOUND: 'TASK_NOT_FOUND',
  TASK_ACCESS_DENIED: 'TASK_ACCESS_DENIED',

  // Generic errors
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];
