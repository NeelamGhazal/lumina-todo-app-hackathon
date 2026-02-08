// Task T015: TypeScript types for chat
/**
 * Chat type definitions for ChatKit UI
 * Based on contracts/frontend-api.yaml and data-model.md
 */

/**
 * Message role type
 */
export type MessageRole = "user" | "assistant";

/**
 * Message status for optimistic updates
 */
export type MessageStatus = "sending" | "sent" | "error";

/**
 * Individual chat message
 */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  created_at: string; // ISO 8601 datetime
  status?: MessageStatus; // UI-only, not persisted
}

/**
 * Summary of a tool call made by the AI
 */
export interface ToolCallSummary {
  tool: string;
  success: boolean;
  result_preview?: string | null;
}

/**
 * Response from POST /api/chat
 */
export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: ToolCallSummary[] | null;
}

/**
 * Conversation summary for list view
 */
export interface ConversationSummary {
  id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  preview?: string | null;
}

/**
 * Chat state for useChat hook
 */
export interface ChatState {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  isSending: boolean;
  isTyping: boolean;
  error: string | null;
}

/**
 * API request to send a chat message
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

/**
 * API response for message history
 */
export interface HistoryResponse {
  messages: Message[];
}

/**
 * API response for conversations list
 */
export interface ConversationsResponse {
  conversations: ConversationSummary[];
}
