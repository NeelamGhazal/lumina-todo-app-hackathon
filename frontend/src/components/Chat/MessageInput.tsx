// Task T009: MessageInput component with Lumina glassmorphism
"use client";

import { useState, useRef, useCallback, KeyboardEvent, ChangeEvent } from "react";
import { motion } from "framer-motion";
import { Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

/**
 * MessageInput - Chat input with Lumina Deep Purple Royal theme
 *
 * Lumina Colors:
 * Dark:  bg-white/5 border-[#7e57c2]/30 text-[#f3e5f5] placeholder-[#ce93d8]/80
 * Light: bg-white/80 border-[#b39ddb]/50 text-[#1a0033] placeholder-[#5e35b1]/80
 * Focus Dark:  focus:border-[#b39ddb] focus:ring-[#b39ddb]/15
 * Focus Light: focus:border-[#7e57c2] focus:ring-[#7e57c2]/15
 */
export function MessageInput({
  onSend,
  disabled = false,
  placeholder = "Type a message...",
  maxLength = 500,
}: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      // Max 4 lines (approx 96px with line-height)
      const maxHeight = 96;
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  }, []);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
      adjustHeight();
    }
  };

  const handleSend = useCallback(() => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  }, [message, disabled, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends, Shift+Enter adds newline
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isNearLimit = message.length >= maxLength - 50;
  const isEmpty = message.trim().length === 0;

  return (
    <motion.div
      className={cn(
        "relative flex items-end gap-2 p-3 rounded-2xl",
        // Lumina glassmorphism - Dark mode
        "bg-white/5 backdrop-blur-[10px]",
        "border border-[#7e57c2]/30",
        // Focus within styling
        "focus-within:border-[#b39ddb] focus-within:ring-2 focus-within:ring-[#b39ddb]/15",
        "transition-all duration-200"
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className={cn(
          "flex-1 resize-none bg-transparent",
          "text-[#f3e5f5] placeholder-[#ce93d8]/60",
          "text-sm leading-6",
          "focus:outline-none",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          // Prevent iOS zoom on focus
          "text-base md:text-sm"
        )}
        style={{ minHeight: "24px" }}
        aria-label="Chat message input"
      />

      {/* Character counter (shows when near limit) */}
      {isNearLimit && (
        <motion.span
          className={cn(
            "absolute -top-6 right-0 text-xs",
            message.length >= maxLength ? "text-red-400" : "text-[#ce93d8]/60"
          )}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {message.length}/{maxLength}
        </motion.span>
      )}

      {/* Send Button */}
      <motion.button
        onClick={handleSend}
        disabled={disabled || isEmpty}
        className={cn(
          "flex-shrink-0 p-2.5 rounded-xl",
          // Lumina gradient button
          "bg-gradient-to-br from-[#ce93d8] to-[#e1bee7]",
          "text-[#1a0033]",
          "disabled:opacity-40 disabled:cursor-not-allowed",
          "hover:shadow-lg hover:shadow-[#ce93d8]/25",
          "active:scale-95",
          "transition-all duration-200"
        )}
        whileHover={{ scale: disabled || isEmpty ? 1 : 1.05 }}
        whileTap={{ scale: disabled || isEmpty ? 1 : 0.95 }}
        aria-label="Send message"
      >
        {disabled ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </motion.button>
    </motion.div>
  );
}
