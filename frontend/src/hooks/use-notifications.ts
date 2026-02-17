"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { toast } from "sonner";

import { notificationsApi } from "@/lib/api/endpoints";
import { getAuthToken } from "@/lib/api/client";
import type { Notification } from "@/types/api";

const POLLING_INTERVAL = 30000; // 30 seconds per spec

interface UseNotificationsState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: Error | null;
}

interface UseNotificationsReturn extends UseNotificationsState {
  markAsRead: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
  refetch: () => Promise<void>;
  fetchNotifications: () => Promise<void>;
}

/**
 * Hook for managing notifications with 30-second polling
 * T024: Polls unread count every 30 seconds
 * T026: Stops polling when not authenticated
 */
export function useNotifications(): UseNotificationsReturn {
  const [state, setState] = useState<UseNotificationsState>({
    notifications: [],
    unreadCount: 0,
    isLoading: false,
    error: null,
  });

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef(true);

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = useCallback((): boolean => {
    return getAuthToken() !== null;
  }, []);

  /**
   * Fetch unread count only (lightweight polling)
   */
  const fetchUnreadCount = useCallback(async () => {
    if (!isAuthenticated() || !isMountedRef.current) return;

    try {
      const response = await notificationsApi.getUnreadCount();
      if (isMountedRef.current) {
        setState((prev) => ({ ...prev, unreadCount: response.count, error: null }));
      }
    } catch (error) {
      // Silent failure for polling - don't show errors to user
      console.debug("Polling error:", error);
    }
  }, [isAuthenticated]);

  /**
   * Fetch full notification list
   */
  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated()) return;

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      const response = await notificationsApi.list(20);
      if (isMountedRef.current) {
        setState({
          notifications: response.notifications,
          unreadCount: response.unreadCount,
          isLoading: false,
          error: null,
        });
      }
    } catch (error) {
      if (isMountedRef.current) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error : new Error("Failed to fetch notifications"),
        }));
      }
      toast.error("Failed to load notifications");
    }
  }, [isAuthenticated]);

  /**
   * Mark a notification as read (optimistic update)
   * T032: Optimistic UI update
   */
  const markAsRead = useCallback(async (id: string) => {
    // Optimistic update
    setState((prev) => ({
      ...prev,
      notifications: prev.notifications.map((n) =>
        n.id === id ? { ...n, isRead: true } : n
      ),
      unreadCount: Math.max(0, prev.unreadCount - 1),
    }));

    try {
      await notificationsApi.markAsRead(id);
    } catch (error) {
      // Revert on failure
      setState((prev) => ({
        ...prev,
        notifications: prev.notifications.map((n) =>
          n.id === id ? { ...n, isRead: false } : n
        ),
        unreadCount: prev.unreadCount + 1,
      }));
      toast.error("Failed to mark notification as read");
    }
  }, []);

  /**
   * Clear all notifications
   */
  const clearAll = useCallback(async () => {
    const previousState = state;

    // Optimistic update
    setState((prev) => ({
      ...prev,
      notifications: [],
      unreadCount: 0,
    }));

    try {
      await notificationsApi.clearAll();
      toast.success("All notifications cleared");
    } catch (error) {
      // Revert on failure
      setState(previousState);
      toast.error("Failed to clear notifications");
    }
  }, [state]);

  /**
   * Refetch notifications (manual refresh)
   */
  const refetch = useCallback(async () => {
    await fetchNotifications();
  }, [fetchNotifications]);

  /**
   * Start polling for unread count
   */
  const startPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Initial fetch
    fetchUnreadCount();

    // Start interval
    pollingIntervalRef.current = setInterval(fetchUnreadCount, POLLING_INTERVAL);
  }, [fetchUnreadCount]);

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  /**
   * Clear notifications state (on logout)
   */
  const clearState = useCallback(() => {
    setState({
      notifications: [],
      unreadCount: 0,
      isLoading: false,
      error: null,
    });
  }, []);

  // Effect: Start/stop polling based on auth state
  useEffect(() => {
    isMountedRef.current = true;

    if (isAuthenticated()) {
      startPolling();
    } else {
      stopPolling();
      clearState();
    }

    return () => {
      isMountedRef.current = false;
      stopPolling();
    };
  }, [isAuthenticated, startPolling, stopPolling, clearState]);

  // Effect: Listen for auth changes (storage event for cross-tab sync)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "auth_token") {
        if (e.newValue === null) {
          // Token removed - stop polling and clear state
          stopPolling();
          clearState();
        } else if (e.oldValue === null) {
          // Token added - start polling
          startPolling();
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [startPolling, stopPolling, clearState]);

  return {
    ...state,
    markAsRead,
    clearAll,
    refetch,
    fetchNotifications,
  };
}
