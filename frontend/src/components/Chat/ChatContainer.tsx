// Task T006: ChatContainer layout component with Lumina theme
"use client";

import { useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { TypingIndicator } from "./TypingIndicator";
import { EmptyState } from "./EmptyState";
import type { Message } from "@/types/chat";

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  onSendMessage: (message: string) => void;
  onRetry?: () => void;
}

/**
 * ChatContainer - Main chat layout with Lumina Deep Purple Royal theme
 *
 * Lumina Colors:
 * - Dark BG: gradient from-[#1a0033] via-[#2e003e] to-[#120024]
 * - Light BG: gradient from-[#ede7f6] to-[#d1c4e9]
 */
export function ChatContainer({
  messages,
  isLoading,
  isTyping,
  error,
  onSendMessage,
  onRetry,
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && messagesContainerRef.current) {
      const container = messagesContainerRef.current;
      const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;

      if (isNearBottom || messages.length <= 1) {
        messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages]);

  return (
    <motion.div
      className={cn(
        "flex flex-col h-full min-h-[calc(100vh-4rem)]",
        // Lumina Deep Purple Royal background
        // Dark mode: deep purple gradient
        "bg-gradient-to-br from-[#1a0033] via-[#2e003e] to-[#120024]",
        // Light mode: soft purple gradient
        "dark:from-[#1a0033] dark:via-[#2e003e] dark:to-[#120024]",
        "light:bg-gradient-to-br light:from-[#ede7f6] light:to-[#d1c4e9]"
      )}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex-shrink-0 px-4 py-4 border-b border-white/10 dark:border-white/10">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#ce93d8] to-[#e1bee7] flex items-center justify-center">
            <span className="text-[#1a0033] font-bold text-lg">AI</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white dark:text-white">
              Todo Assistant
            </h1>
            <p className="text-sm text-[#ce93d8] dark:text-[#ce93d8]">
              Powered by AI
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <motion.div
          className="flex-shrink-0 px-4 py-3 bg-red-500/20 border-b border-red-500/30"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
        >
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <p className="text-red-200 text-sm">{error}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="text-sm text-red-200 hover:text-white underline"
              >
                Retry
              </button>
            )}
          </div>
        </motion.div>
      )}

      {/* Messages Area */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-4 py-4"
      >
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <EmptyState onPromptClick={onSendMessage} />
          ) : (
            <>
              <MessageList messages={messages} />
              {isTyping && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0 px-4 py-4 border-t border-white/10 dark:border-white/10">
        <div className="max-w-4xl mx-auto">
          <MessageInput
            onSend={onSendMessage}
            disabled={isLoading}
            placeholder="Ask me to manage your tasks..."
          />
        </div>
      </div>
    </motion.div>
  );
}
