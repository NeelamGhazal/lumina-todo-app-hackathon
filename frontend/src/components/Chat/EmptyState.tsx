// Task T011: EmptyState component with suggested prompts
"use client";

import { motion } from "framer-motion";
import { MessageCircle, Plus, ListTodo, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  onPromptClick: (prompt: string) => void;
}

const SUGGESTED_PROMPTS = [
  {
    icon: Plus,
    label: "Add task...",
    prompt: "Add task: ",
  },
  {
    icon: ListTodo,
    label: "Show my tasks",
    prompt: "Show my tasks",
  },
  {
    icon: Calendar,
    label: "What's pending today?",
    prompt: "What tasks are pending today?",
  },
];

/**
 * EmptyState - Welcome message and suggested prompts for new users
 *
 * Lumina gradient buttons with stagger animation
 */
export function EmptyState({ onPromptClick }: EmptyStateProps) {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-12 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* AI Icon */}
      <motion.div
        className={cn(
          "w-20 h-20 rounded-full mb-6",
          "bg-gradient-to-br from-[#7e57c2] to-[#5e35b1]",
          "flex items-center justify-center",
          "shadow-lg shadow-[#7e57c2]/30"
        )}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <MessageCircle className="w-10 h-10 text-white" />
      </motion.div>

      {/* Welcome Text */}
      <motion.h2
        className="text-2xl font-semibold text-white mb-2 text-center"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        Welcome to Todo Assistant!
      </motion.h2>

      <motion.p
        className="text-[#ce93d8]/80 text-center mb-8 max-w-sm"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        I can help you manage your tasks using natural language.
        Try one of these prompts to get started:
      </motion.p>

      {/* Suggested Prompts */}
      <motion.div
        className="flex flex-col sm:flex-row gap-3 w-full max-w-lg"
        initial="hidden"
        animate="visible"
        variants={{
          visible: {
            transition: {
              staggerChildren: 0.1,
              delayChildren: 0.4,
            },
          },
        }}
      >
        {SUGGESTED_PROMPTS.map((item) => (
          <motion.button
            key={item.label}
            onClick={() => onPromptClick(item.prompt)}
            className={cn(
              "flex-1 flex items-center justify-center gap-2",
              "px-4 py-3 rounded-xl",
              // Lumina gradient button
              "bg-gradient-to-br from-[#ce93d8]/20 to-[#e1bee7]/20",
              "border border-[#ce93d8]/30",
              "text-[#f3e5f5] text-sm font-medium",
              "hover:from-[#ce93d8]/30 hover:to-[#e1bee7]/30",
              "hover:border-[#ce93d8]/50",
              "transition-all duration-200",
              "active:scale-95"
            )}
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <item.icon className="w-4 h-4 text-[#ce93d8]" />
            <span>{item.label}</span>
          </motion.button>
        ))}
      </motion.div>

      {/* Keyboard hint */}
      <motion.p
        className="text-xs text-white/30 mt-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        Press <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-white/50">Enter</kbd> to send,{" "}
        <kbd className="px-1.5 py-0.5 rounded bg-white/10 text-white/50">Shift+Enter</kbd> for new line
      </motion.p>
    </motion.div>
  );
}
