// Task T008: MessageBubble component with Lumina gradients
"use client";

import { memo } from "react";
import { motion } from "framer-motion";
import { User, Bot, AlertCircle, RefreshCw } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import type { Message } from "@/types/chat";

interface MessageBubbleProps {
  message: Message;
  isConsecutive?: boolean;
  onRetry?: () => void;
}

/**
 * MessageBubble - Individual chat message with Lumina Deep Purple Royal theme
 *
 * Lumina Colors:
 * User Dark:  bg-gradient-to-br from-[#ce93d8] to-[#e1bee7] text-[#1a0033]
 * User Light: bg-gradient-to-br from-[#5e35b1] to-[#4a148c] text-white
 * AI Dark:    bg-white/5 backdrop-blur-[10px] text-[#f3e5f5]
 * AI Light:   bg-white border border-[#d1c4e9]/50 text-[#1a0033]
 */
export const MessageBubble = memo(function MessageBubble({
  message,
  isConsecutive = false,
  onRetry,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isError = message.status === "error";
  const isSending = message.status === "sending";

  // Format timestamp
  const timestamp = message.created_at
    ? formatDistanceToNow(new Date(message.created_at), { addSuffix: true })
    : "Just now";

  return (
    <motion.div
      className={cn(
        "flex gap-3",
        isUser ? "flex-row-reverse" : "flex-row",
        !isConsecutive && "mt-4",
        isConsecutive && "mt-1"
      )}
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      layout
    >
      {/* Avatar */}
      {!isConsecutive && (
        <div
          className={cn(
            "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
            isUser
              ? // User avatar - Lumina gradient
                "bg-gradient-to-br from-[#ce93d8] to-[#e1bee7] dark:from-[#ce93d8] dark:to-[#e1bee7]"
              : // AI avatar - Deep purple
                "bg-gradient-to-br from-[#7e57c2] to-[#5e35b1]"
          )}
        >
          {isUser ? (
            <User className="h-4 w-4 text-[#1a0033]" />
          ) : (
            <Bot className="h-4 w-4 text-white" />
          )}
        </div>
      )}

      {/* Spacer for consecutive messages */}
      {isConsecutive && <div className="w-8 flex-shrink-0" />}

      {/* Message Content */}
      <div
        className={cn(
          "flex flex-col max-w-[75%] md:max-w-[65%]",
          isUser ? "items-end" : "items-start"
        )}
      >
        {/* Bubble */}
        <div
          className={cn(
            "px-4 py-2.5 rounded-2xl",
            isUser
              ? // User message - Lumina gradient
                cn(
                  // Dark mode
                  "bg-gradient-to-br from-[#ce93d8] to-[#e1bee7] text-[#1a0033]",
                  // Light mode (same gradient works in both for user)
                  "dark:from-[#ce93d8] dark:to-[#e1bee7] dark:text-[#1a0033]",
                  // Rounded corners (left rounded, right more rounded for user)
                  "rounded-br-md"
                )
              : // AI message - Glass effect (dark) / White card (light)
                cn(
                  // Dark mode - Glassmorphism
                  "bg-white/5 backdrop-blur-[10px] text-[#f3e5f5]",
                  // Light mode would use different classes but we're in dark by default
                  "border border-white/10",
                  // Rounded corners (right rounded, left more rounded for AI)
                  "rounded-bl-md"
                ),
            // Error state
            isError && "border-2 border-red-500/50",
            // Sending state
            isSending && "opacity-70"
          )}
        >
          {/* Message text with markdown support */}
          <div
            className={cn(
              "text-sm leading-relaxed whitespace-pre-wrap break-words",
              // Prose styling for AI messages with lists, code, etc.
              !isUser && "prose prose-sm prose-invert max-w-none",
              !isUser && "prose-p:my-1 prose-ul:my-1 prose-ol:my-1",
              !isUser && "prose-code:bg-white/10 prose-code:px-1 prose-code:rounded",
              !isUser && "prose-strong:text-[#f3e5f5]"
            )}
            // Simple markdown rendering (bold, code, lists)
            dangerouslySetInnerHTML={{
              __html: !isUser ? formatMarkdown(message.content) : escapeHtml(message.content),
            }}
          />
        </div>

        {/* Error state with retry */}
        {isError && (
          <div className="flex items-center gap-2 mt-1 text-red-400 text-xs">
            <AlertCircle className="h-3 w-3" />
            <span>Failed to send</span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="flex items-center gap-1 text-red-300 hover:text-white underline"
              >
                <RefreshCw className="h-3 w-3" />
                Retry
              </button>
            )}
          </div>
        )}

        {/* Timestamp */}
        <span
          className={cn(
            "text-[10px] mt-1 px-1",
            isUser ? "text-[#ce93d8]/70" : "text-white/40"
          )}
        >
          {isSending ? "Sending..." : timestamp}
        </span>
      </div>
    </motion.div>
  );
});

/**
 * Simple markdown formatting for AI responses
 * Supports: **bold**, `code`, lists
 */
function formatMarkdown(text: string): string {
  let html = escapeHtml(text);

  // Bold: **text**
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Inline code: `code`
  html = html.replace(/`([^`]+)`/g, '<code class="bg-white/10 px-1 rounded text-[#e1bee7]">$1</code>');

  // Unordered lists: - item or * item
  html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li class="ml-4">$1</li>');
  html = html.replace(/(<li.*<\/li>\n?)+/g, '<ul class="list-disc list-inside my-1">$&</ul>');

  // Ordered lists: 1. item
  html = html.replace(/^\d+\.\s+(.+)$/gm, '<li class="ml-4">$1</li>');

  // Line breaks
  html = html.replace(/\n/g, "<br />");

  return html;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text: string): string {
  const div = typeof document !== "undefined" ? document.createElement("div") : null;
  if (div) {
    div.textContent = text;
    return div.innerHTML;
  }
  // Fallback for SSR
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
