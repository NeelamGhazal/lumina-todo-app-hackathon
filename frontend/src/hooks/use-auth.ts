"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { api } from "@/lib/api/endpoints";
import { ApiClientError, clearAuthToken, getAuthToken } from "@/lib/api/client";
import type { User } from "@/types/entities";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

/**
 * Hook for managing authentication state
 * Per spec US6: Session management for authenticated users
 * Per Phase II spec: JWT token management
 */
export function useAuth() {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  /**
   * Check current session and update state
   */
  const checkSession = useCallback(async () => {
    // First check if we even have a token
    if (!getAuthToken()) {
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
      return;
    }

    try {
      const response = await api.auth.getSession();
      setState({
        user: response.user,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      // Token might be invalid, clear it
      clearAuthToken();
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
    }
  }, []);

  /**
   * Logout the current user
   */
  const logout = useCallback(async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      // Even if API call fails, clear local state
      console.error("Logout API error:", error);
    }

    // Always clear local state and token
    clearAuthToken();
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
    });

    toast.success("Logged out", {
      description: "You have been logged out successfully.",
    });

    router.push("/login");
    router.refresh();
  }, [router]);

  /**
   * Refresh authentication state
   */
  const refresh = useCallback(() => {
    setState((prev) => ({ ...prev, isLoading: true }));
    checkSession();
  }, [checkSession]);

  // Check session on mount
  useEffect(() => {
    checkSession();
  }, [checkSession]);

  return {
    ...state,
    logout,
    refresh,
  };
}
