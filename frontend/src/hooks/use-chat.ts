// Task T017: useChat hook for chat state management
"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { sendMessage as sendChatMessage, getHistory } from "@/lib/api/chat";
import { ApiClientError } from "@/lib/api/client";
import type { Message, ChatState, ChatResponse } from "@/types/chat";

// Task-related tool names that should trigger a task list refresh
const TASK_TOOLS = ["add_task", "delete_task", "update_task", "complete_task"];

/**
 * Check if chat response contains successful task-related tool calls
 */
function hasTaskToolCalls(response: ChatResponse): boolean {
  if (!response.tool_calls || response.tool_calls.length === 0) {
    return false;
  }
  return response.tool_calls.some(
    (tc) => TASK_TOOLS.includes(tc.tool) && tc.success
  );
}

/**
 * Dispatch event to notify task list to refresh
 */
function notifyTasksUpdated(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("tasks-updated"));
  }
}

const POLLING_INTERVAL = 3000; // 3 seconds

interface UseChatOptions {
  /** Initial conversation ID to load */
  conversationId?: string | null;
  /** Whether to auto-load history on mount */
  autoLoadHistory?: boolean;
  /** Whether to enable polling for new messages */
  enablePolling?: boolean;
}

interface UseChatReturn extends ChatState {
  /** Send a message to the AI */
  sendMessage: (content: string) => Promise<void>;
  /** Manually load/reload history */
  loadHistory: () => Promise<void>;
  /** Retry last failed message */
  retryLastFailed: () => Promise<void>;
  /** Clear error state */
  clearError: () => void;
}

/**
 * useChat - Hook for managing chat state and API interactions
 *
 * Features:
 * - Optimistic UI updates for instant feedback
 * - Polling for new messages (pauses when tab hidden)
 * - Error handling with retry capability
 * - Conversation ID persistence across messages
 */
export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const {
    conversationId: initialConversationId = null,
    autoLoadHistory = true,
    enablePolling = true,
  } = options;

  // State
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(initialConversationId);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs for polling
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const lastFailedMessageRef = useRef<string | null>(null);

  /**
   * Load conversation history
   */
  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const history = await getHistory(conversationId);
      setMessages(history);

      // If we got messages, extract conversation ID from first one
      if (history.length > 0 && !conversationId) {
        // The conversation ID comes from the chat response, not history
        // We'll get it on the next message send
      }
    } catch (err) {
      if (err instanceof ApiClientError && err.isAuthError()) {
        setError("Please log in to view chat history.");
      } else if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError("Failed to load chat history.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  /**
   * Send a message with optimistic updates
   */
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isSending) return;

    const trimmedContent = content.trim();
    lastFailedMessageRef.current = trimmedContent;

    // Create optimistic user message
    const tempId = `temp-${Date.now()}`;
    const userMessage: Message = {
      id: tempId,
      role: "user",
      content: trimmedContent,
      created_at: new Date().toISOString(),
      status: "sending",
    };

    // Add to messages immediately (optimistic)
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    setIsTyping(true);
    setError(null);

    try {
      // Send to API
      const response = await sendChatMessage(trimmedContent, conversationId);

      // Update conversation ID if new
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Update user message status to sent
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === tempId
            ? { ...msg, status: "sent" as const }
            : msg
        )
      );

      // Add AI response
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: response.message,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      lastFailedMessageRef.current = null;

      // If AI performed task operations, notify task list to refresh
      // DEBUG: Log response to verify tool_calls are received
      console.log("[ChatKit] Response received:", JSON.stringify(response));
      console.log("[ChatKit] tool_calls:", response.tool_calls);
      console.log("[ChatKit] hasTaskToolCalls:", hasTaskToolCalls(response));

      if (hasTaskToolCalls(response)) {
        console.log("[ChatKit] Dispatching tasks-updated event");
        notifyTasksUpdated();
      }
    } catch (err) {
      // Mark message as failed
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === tempId
            ? { ...msg, status: "error" as const }
            : msg
        )
      );

      if (err instanceof ApiClientError) {
        if (err.isAuthError()) {
          setError("Please log in to send messages.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Failed to send message. Please try again.");
      }
    } finally {
      setIsSending(false);
      setIsTyping(false);
    }
  }, [conversationId, isSending]);

  /**
   * Retry last failed message
   */
  const retryLastFailed = useCallback(async () => {
    if (!lastFailedMessageRef.current) return;

    // Remove the failed message
    setMessages((prev) =>
      prev.filter((msg) => msg.status !== "error")
    );

    // Retry sending
    await sendMessage(lastFailedMessageRef.current);
  }, [sendMessage]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Polling for new messages
   */
  useEffect(() => {
    if (!enablePolling || !conversationId) return;

    const poll = async () => {
      // Only poll if page is visible
      if (document.visibilityState !== "visible") return;

      try {
        const history = await getHistory(conversationId);

        // Only update if we have new messages
        if (history.length > messages.length) {
          // Merge new messages, preserving any pending/error states
          setMessages((prev) => {
            const pendingMessages = prev.filter(
              (msg) => msg.status === "sending" || msg.status === "error"
            );
            const serverMessages = history.filter(
              (msg) => !msg.id.startsWith("temp-") && !msg.id.startsWith("ai-")
            );
            return [...serverMessages, ...pendingMessages];
          });
        }
      } catch {
        // Silently fail polling - don't show error for background updates
      }
    };

    // Start polling
    pollingRef.current = setInterval(poll, POLLING_INTERVAL);

    // Cleanup
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [enablePolling, conversationId, messages.length]);

  /**
   * Handle visibility change - pause/resume polling
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && enablePolling && conversationId) {
        // Immediately poll when becoming visible
        getHistory(conversationId)
          .then((history) => {
            if (history.length > messages.length) {
              setMessages(history);
            }
          })
          .catch(() => {});
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [enablePolling, conversationId, messages.length]);

  /**
   * Auto-load history on mount
   */
  useEffect(() => {
    if (autoLoadHistory) {
      loadHistory();
    }
  }, [autoLoadHistory, loadHistory]);

  return {
    messages,
    conversationId,
    isLoading,
    isSending,
    isTyping,
    error,
    sendMessage,
    loadHistory,
    retryLastFailed,
    clearError,
  };
}
