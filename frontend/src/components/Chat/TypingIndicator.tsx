// Task T010: TypingIndicator component with animated dots
"use client";

import { motion } from "framer-motion";
import { Bot } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * TypingIndicator - Animated "AI is typing..." indicator
 *
 * Lumina Colors:
 * Dark:  text-[#ce93d8]
 * Light: text-[#5e35b1]
 */
export function TypingIndicator() {
  return (
    <motion.div
      className="flex items-start gap-3 mt-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      {/* AI Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-[#7e57c2] to-[#5e35b1] flex items-center justify-center">
        <Bot className="h-4 w-4 text-white" />
      </div>

      {/* Typing bubble */}
      <div
        className={cn(
          "px-4 py-3 rounded-2xl rounded-bl-md",
          "bg-white/5 backdrop-blur-[10px]",
          "border border-white/10"
        )}
      >
        <div className="flex items-center gap-2">
          {/* Animated dots */}
          <div className="flex items-center gap-1">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="w-2 h-2 rounded-full bg-[#ce93d8]"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.15,
                  ease: "easeInOut",
                }}
              />
            ))}
          </div>
          <span className="text-xs text-[#ce93d8]">AI is typing</span>
        </div>
      </div>
    </motion.div>
  );
}
