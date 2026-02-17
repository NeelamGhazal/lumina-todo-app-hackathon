/**
 * API Endpoint Functions for Phase II Frontend
 * Per Phase II spec: JWT token stored and sent with every request
 */

import { apiClient, setAuthToken, clearAuthToken, getAuthToken } from "./client";
import type {
  ClearNotificationsResponse,
  CreateTaskRequest,
  CreateTaskResponse,
  DeleteTaskResponse,
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  ListTasksParams,
  ListTasksResponse,
  LoginRequest,
  LoginResponse,
  Notification,
  NotificationListResponse,
  OAuthLoginRequest,
  OAuthLoginResponse,
  RegisterRequest,
  RegisterResponse,
  ResetPasswordRequest,
  ResetPasswordResponse,
  SessionResponse,
  ToggleCompleteResponse,
  TriggerJobResponse,
  UnreadCountResponse,
  UpdateTaskRequest,
  UpdateTaskResponse,
  VerifyTokenResponse,
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

  /**
   * Request password reset email
   * Always returns same response to prevent email enumeration
   */
  forgotPassword: async (data: ForgotPasswordRequest): Promise<ForgotPasswordResponse> => {
    return apiClient.post<ForgotPasswordResponse>("/auth/forgot-password", data);
  },

  /**
   * Verify reset token validity
   * Returns token status and user email if valid
   */
  verifyResetToken: async (token: string): Promise<VerifyTokenResponse> => {
    return apiClient.get<VerifyTokenResponse>(`/auth/verify-reset-token/${token}`);
  },

  /**
   * Reset password with valid token
   * Sets new password and invalidates token
   */
  resetPassword: async (data: ResetPasswordRequest): Promise<ResetPasswordResponse> => {
    return apiClient.post<ResetPasswordResponse>("/auth/reset-password", data);
  },

  /**
   * OAuth login/signup
   * Creates new user or links OAuth provider to existing account
   * Called by NextAuth after successful OAuth flow
   * Per specs/010-oauth-social-login/contracts/oauth-api.yaml
   */
  oauthLogin: async (data: OAuthLoginRequest): Promise<OAuthLoginResponse> => {
    const response = await apiClient.post<OAuthLoginResponse>("/auth/oauth", data);
    // Store token for subsequent requests
    if (response.access_token) {
      setAuthToken(response.access_token);
    }
    return response;
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
// Chat Endpoints (Phase III - AI Assistant)
// =============================================================================

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: Array<{
    tool: string;
    success: boolean;
    result_preview?: string;
  }>;
}

export const chatApi = {
  /**
   * Send a message to the AI assistant
   * Proxies through Phase II API to Part 2 agent
   */
  sendMessage: async (data: ChatMessage): Promise<ChatResponse> => {
    return apiClient.post<ChatResponse>("/chat", data);
  },

  /**
   * Get conversation history
   */
  getHistory: async (conversationId?: string): Promise<{ messages: Array<{ id: string; role: string; content: string; created_at: string }> }> => {
    const params: Record<string, string> = {};
    if (conversationId) {
      params.conversation_id = conversationId;
    }
    return apiClient.get<{ messages: Array<{ id: string; role: string; content: string; created_at: string }> }>("/chat/history", params);
  },

  /**
   * Check chat health
   */
  health: async (): Promise<{ status: string; agent_reachable: boolean }> => {
    return apiClient.get<{ status: string; agent_reachable: boolean }>("/chat/health");
  },
};

// =============================================================================
// Notification Endpoints
// =============================================================================

export const notificationsApi = {
  /**
   * List notifications for the authenticated user
   * Returns notifications sorted by created_at DESC (newest first)
   */
  list: async (limit?: number, unreadOnly?: boolean): Promise<NotificationListResponse> => {
    const params: Record<string, string | number | boolean> = {};
    if (limit !== undefined) params.limit = limit;
    if (unreadOnly !== undefined) params.unreadOnly = unreadOnly;
    return apiClient.get<NotificationListResponse>("/notifications", params);
  },

  /**
   * Get unread notification count (lightweight endpoint for polling)
   */
  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    return apiClient.get<UnreadCountResponse>("/notifications/unread-count");
  },

  /**
   * Mark a single notification as read
   */
  markAsRead: async (id: string): Promise<Notification> => {
    return apiClient.patch<Notification>(`/notifications/${id}/read`);
  },

  /**
   * Clear all notifications for the current user
   */
  clearAll: async (): Promise<ClearNotificationsResponse> => {
    return apiClient.delete<ClearNotificationsResponse>("/notifications");
  },

  /**
   * Manually trigger the notification generation job (for testing)
   */
  triggerJob: async (): Promise<TriggerJobResponse> => {
    return apiClient.post<TriggerJobResponse>("/notifications/trigger-job");
  },
};

// =============================================================================
// Export all APIs
// =============================================================================

export const api = {
  auth: authApi,
  tasks: tasksApi,
  chat: chatApi,
  notifications: notificationsApi,
};

export default api;
