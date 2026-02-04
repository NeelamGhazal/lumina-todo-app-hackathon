/**
 * API Client with JWT handling and error management
 * Per Phase II spec: JWT token in Authorization: Bearer <token> header
 */

import type { ApiError } from "@/types/api";
import { ERROR_CODES, HTTP_STATUS } from "@/types/api";

// =============================================================================
// Configuration
// =============================================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// Token cookie name - must match middleware.ts
const TOKEN_COOKIE_NAME = "auth_token";

// =============================================================================
// Token Management
// =============================================================================

/**
 * Get stored auth token from cookie.
 * Works both client-side (for API calls) and is readable by middleware (server-side).
 */
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${TOKEN_COOKIE_NAME}=([^;]*)`));
  const value = match?.[1];
  return value ? decodeURIComponent(value) : null;
}

/**
 * Store auth token as a cookie.
 * Uses a non-httpOnly cookie so both client JS and Next.js middleware can read it.
 * The actual security comes from JWT signature verification on the backend.
 */
export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  // Set cookie with 24h expiry, accessible to JS and middleware
  const maxAge = 60 * 60 * 24; // 24 hours in seconds
  document.cookie = `${TOKEN_COOKIE_NAME}=${encodeURIComponent(token)}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

/**
 * Clear auth token cookie.
 */
export function clearAuthToken(): void {
  if (typeof window === "undefined") return;
  document.cookie = `${TOKEN_COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax`;
}

// =============================================================================
// Types
// =============================================================================

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

// =============================================================================
// API Client Class
// =============================================================================

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Build URL with query parameters
   */
  private buildUrl(
    endpoint: string,
    params?: Record<string, string | number | boolean | undefined>
  ): string {
    const url = new URL(`${this.baseUrl}${endpoint}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    return url.toString();
  }

  /**
   * Make an HTTP request
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { body, params, ...fetchOptions } = options;

    const url = this.buildUrl(endpoint, params);

    // Build headers with auth token if available
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...fetchOptions.headers,
    };

    // Add Authorization header if token exists
    const token = getAuthToken();
    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    let response: Response;

    try {
      response = await fetch(url, {
        ...fetchOptions,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        credentials: "include", // Also include cookies as fallback
      });
    } catch (error) {
      // Handle network errors (connection refused, offline, etc.)
      const isOffline = typeof navigator !== "undefined" && !navigator.onLine;
      const message = isOffline
        ? "You appear to be offline. Please check your internet connection."
        : "Unable to connect to the server. Please ensure the backend is running.";

      throw new ApiClientError(
        message,
        ERROR_CODES.NETWORK_ERROR,
        0, // No HTTP status for network errors
        undefined
      );
    }

    // Handle no content response
    if (response.status === HTTP_STATUS.NO_CONTENT) {
      return {} as T;
    }

    // Parse response
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      throw new ApiClientError(
        "Invalid response from server",
        ERROR_CODES.INTERNAL_ERROR,
        response.status,
        undefined
      );
    }

    // Handle error responses
    if (!response.ok) {
      const error = data as ApiError;

      // Clear token on auth errors
      if (response.status === HTTP_STATUS.UNAUTHORIZED) {
        clearAuthToken();
      }

      throw new ApiClientError(
        error.message || "An error occurred",
        error.error || ERROR_CODES.INTERNAL_ERROR,
        response.status,
        error.details
      );
    }

    return data as T;
  }

  /**
   * GET request
   */
  async get<T>(
    endpoint: string,
    params?: Record<string, string | number | boolean | undefined>
  ): Promise<T> {
    return this.request<T>(endpoint, { method: "GET", params });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: "POST", body });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: "PUT", body });
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: "PATCH", body });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

// =============================================================================
// Custom Error Class
// =============================================================================

export class ApiClientError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
    public details?: Record<string, string[]>
  ) {
    super(message);
    this.name = "ApiClientError";
  }

  /**
   * Check if error is authentication related
   */
  isAuthError(): boolean {
    return (
      this.status === HTTP_STATUS.UNAUTHORIZED ||
      this.code === ERROR_CODES.SESSION_EXPIRED ||
      this.code === ERROR_CODES.UNAUTHORIZED
    );
  }

  /**
   * Check if error is validation related
   */
  isValidationError(): boolean {
    return (
      this.status === HTTP_STATUS.UNPROCESSABLE_ENTITY ||
      this.code === ERROR_CODES.VALIDATION_ERROR
    );
  }

  /**
   * Check if error is not found
   */
  isNotFound(): boolean {
    return this.status === HTTP_STATUS.NOT_FOUND;
  }

  /**
   * Check if error is a network/connection error
   */
  isNetworkError(): boolean {
    return this.code === ERROR_CODES.NETWORK_ERROR || this.status === 0;
  }
}

// =============================================================================
// Export singleton instance
// =============================================================================

export const apiClient = new ApiClient(API_BASE_URL);

export default apiClient;
