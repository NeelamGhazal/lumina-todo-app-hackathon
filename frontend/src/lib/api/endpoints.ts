/**
 * API Endpoint Functions for Phase II Frontend
 * Per Phase II spec: JWT token stored and sent with every request
 */

import { apiClient, setAuthToken, clearAuthToken, getAuthToken } from "./client";
import type {
  CreateTaskRequest,
  CreateTaskResponse,
  DeleteTaskResponse,
  ListTasksParams,
  ListTasksResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  SessionResponse,
  ToggleCompleteResponse,
  UpdateTaskRequest,
  UpdateTaskResponse,
} from "@/types/api";

// =============================================================================
// Authentication Endpoints
// =============================================================================

export const authApi = {
  /**
   * Register a new user
   * Stores JWT token on success
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>("/auth/register", data);
    // Store token for subsequent requests
    if (response.token) {
      setAuthToken(response.token);
    }
    return response;
  },

  /**
   * Login user
   * Stores JWT token on success
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>("/auth/login", data);
    // Store token for subsequent requests
    if (response.token) {
      setAuthToken(response.token);
    }
    return response;
  },

  /**
   * Logout current user
   * Clears stored JWT token
   */
  logout: async (): Promise<{ success: boolean }> => {
    const response = await apiClient.post<{ success: boolean }>("/auth/logout");
    // Clear stored token
    clearAuthToken();
    return response;
  },

  /**
   * Get current session
   */
  getSession: async (): Promise<SessionResponse> => {
    return apiClient.get<SessionResponse>("/auth/session");
  },

  /**
   * Check if user has a stored token
   */
  hasToken: (): boolean => {
    return getAuthToken() !== null;
  },
};

// =============================================================================
// Task Endpoints
// =============================================================================

export const tasksApi = {
  /**
   * List all tasks for the authenticated user
   */
  list: async (params?: ListTasksParams): Promise<ListTasksResponse> => {
    return apiClient.get<ListTasksResponse>(
      "/tasks",
      params as Record<string, string | number | boolean | undefined>
    );
  },

  /**
   * Get a single task by ID
   */
  get: async (id: string): Promise<{ task: import("@/types").Task }> => {
    return apiClient.get<{ task: import("@/types").Task }>(`/tasks/${id}`);
  },

  /**
   * Create a new task
   */
  create: async (data: CreateTaskRequest): Promise<CreateTaskResponse> => {
    return apiClient.post<CreateTaskResponse>("/tasks", data);
  },

  /**
   * Update an existing task
   */
  update: async (
    id: string,
    data: UpdateTaskRequest
  ): Promise<UpdateTaskResponse> => {
    return apiClient.put<UpdateTaskResponse>(`/tasks/${id}`, data);
  },

  /**
   * Delete a task
   */
  delete: async (id: string): Promise<DeleteTaskResponse> => {
    return apiClient.delete<DeleteTaskResponse>(`/tasks/${id}`);
  },

  /**
   * Toggle task completion status
   */
  toggleComplete: async (id: string): Promise<ToggleCompleteResponse> => {
    return apiClient.patch<ToggleCompleteResponse>(`/tasks/${id}/complete`);
  },
};

// =============================================================================
// Export all APIs
// =============================================================================

export const api = {
  auth: authApi,
  tasks: tasksApi,
};

export default api;
