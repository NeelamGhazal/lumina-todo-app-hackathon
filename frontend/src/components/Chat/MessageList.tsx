// Task T007: MessageList scrollable component
"use client";

import { memo } from "react";
import { AnimatePresence } from "framer-motion";
import { MessageBubble } from "./MessageBubble";
import type { Message } from "@/types/chat";

interface MessageListProps {
  messages: Message[];
}

/**
 * MessageList - Scrollable container for chat messages
 *
 * Features:
 * - Animated entry for new messages
 * - Groups consecutive messages from same sender
 * - Handles empty state check
 */
export const MessageList = memo(function MessageList({ messages }: MessageListProps) {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {messages.map((message, index) => {
          // Check if this is a consecutive message from same sender
          const previousMessage = index > 0 ? messages[index - 1] : null;
          const isConsecutive = previousMessage?.role === message.role;

          return (
            <MessageBubble
              key={message.id}
              message={message}
              isConsecutive={isConsecutive}
            />
          );
        })}
      </AnimatePresence>
    </div>
  );
});
