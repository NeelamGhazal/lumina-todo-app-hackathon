"use client";

import { motion } from "framer-motion";
import { ClipboardList, Plus, CheckCircle2, Circle } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { AnimatedButton } from "@/components/ui/animated-button";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants, staggerContainerVariants } from "@/lib/animation-variants";

interface EmptyStateProps {
  onAddTask?: () => void;
}

/**
 * EmptyState - Lumina styled empty state with icon placeholder
 * T067: Empty state with glassmorphism and animations
 */
export function EmptyState({ onAddTask }: EmptyStateProps) {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-16 px-4"
      variants={staggerContainerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={fadeUpVariants}>
        <GlassCard className="p-8 text-center max-w-md">
          {/* Illustration */}
          <div className="relative mb-6 mx-auto w-24 h-24">
            <div className="w-24 h-24 rounded-full bg-lumina-primary-500/10 flex items-center justify-center">
              <ClipboardList className="w-12 h-12 text-lumina-primary-400" />
            </div>
            {/* Decorative elements */}
            <motion.div
              className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-lumina-primary-500/20"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <motion.div
              className="absolute -bottom-1 -left-3 w-4 h-4 rounded-full bg-lumina-primary-300/20"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2.5, repeat: Infinity, delay: 0.5 }}
            />
          </div>

          {/* Text */}
          <h3 className="text-xl font-semibold mb-2">
            No tasks yet
          </h3>
          <p className="text-muted-foreground mb-6">
            Get started by creating your first task. Stay organized and illuminate your productivity with{" "}
            <GradientText variant="primary">Lumina</GradientText>.
          </p>

          {/* CTA Button */}
          {onAddTask && (
            <AnimatedButton variant="gradient" size="lg" onClick={onAddTask}>
              <Plus className="w-4 h-4 mr-2" />
              Add your first task
            </AnimatedButton>
          )}
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}

/**
 * Empty state for filtered results
 */
export function EmptyFilterState({ filter }: { filter: string }) {
  const isCompleted = filter === "completed";

  return (
    <motion.div
      className="flex flex-col items-center justify-center py-16 px-4"
      variants={fadeUpVariants}
      initial="hidden"
      animate="visible"
    >
      <GlassCard className="p-6 text-center max-w-sm">
        <div className="w-16 h-16 rounded-full bg-lumina-primary-500/10 flex items-center justify-center mb-4 mx-auto">
          {isCompleted ? (
            <CheckCircle2 className="w-8 h-8 text-lumina-success-400" />
          ) : (
            <Circle className="w-8 h-8 text-lumina-primary-400" />
          )}
        </div>
        <h3 className="text-lg font-medium mb-1">No {filter} tasks</h3>
        <p className="text-sm text-muted-foreground">
          {isCompleted
            ? "You haven't completed any tasks yet. Keep going!"
            : "All caught up! No pending tasks."}
        </p>
      </GlassCard>
    </motion.div>
  );
}
