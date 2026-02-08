// Task T016: Chat API client functions
/**
 * Chat API client for ChatKit UI
 *
 * Calls Phase II backend chat endpoints which proxy to Part 2 OpenRouter agent.
 * Uses existing apiClient for auth token handling.
 */

import { apiClient, ApiClientError } from "./client";
import type {
  ChatRequest,
  ChatResponse,
  HistoryResponse,
  ConversationsResponse,
  Message,
  ConversationSummary,
} from "@/types/chat";

/**
 * Send a message to the AI assistant
 *
 * @param message - User's message text
 * @param conversationId - Optional conversation ID to continue existing conversation
 * @returns AI response with conversation ID
 */
export async function sendMessage(
  message: string,
  conversationId?: string | null
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    conversation_id: conversationId ?? undefined,
  };

  try {
    const response = await apiClient.post<ChatResponse>("/chat", payload);
    return response;
  } catch (error) {
    if (error instanceof ApiClientError) {
      // Re-throw with more user-friendly message for specific cases
      if (error.status === 503) {
        throw new ApiClientError(
          "AI assistant is temporarily unavailable. Please try again in a moment.",
          error.code,
          error.status,
          error.details
        );
      }
      if (error.status === 504) {
        throw new ApiClientError(
          "AI assistant took too long to respond. Please try again.",
          error.code,
          error.status,
          error.details
        );
      }
    }
    throw error;
  }
}

/**
 * Get chat message history
 *
 * @param conversationId - Optional specific conversation to fetch. If not provided, gets most recent.
 * @param limit - Maximum messages to return (default 50)
 * @returns Array of messages in chronological order
 */
export async function getHistory(
  conversationId?: string | null,
  limit: number = 50
): Promise<Message[]> {
  const params: Record<string, string | number | undefined> = {
    limit,
  };

  if (conversationId) {
    params.conversation_id = conversationId;
  }

  try {
    const response = await apiClient.get<HistoryResponse>("/chat/history", params);
    return response.messages ?? [];
  } catch (error) {
    if (error instanceof ApiClientError && error.status === 404) {
      // No conversation found - return empty array
      return [];
    }
    throw error;
  }
}

/**
 * List user's conversations
 *
 * @param limit - Maximum conversations to return (default 20)
 * @returns Array of conversation summaries
 */
export async function getConversations(
  limit: number = 20
): Promise<ConversationSummary[]> {
  const response = await apiClient.get<ConversationsResponse>("/chat/conversations", {
    limit,
  });
  return response.conversations ?? [];
}

/**
 * Check if chat service is healthy
 *
 * @returns Health status including agent availability
 */
export async function checkChatHealth(): Promise<{
  status: string;
  agent_reachable: boolean;
  agent_status?: string;
}> {
  return apiClient.get("/chat/health");
}
