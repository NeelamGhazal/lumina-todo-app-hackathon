"use client";

import { memo } from "react";
import { motion } from "framer-motion";
import { Calendar, Clock, Trash2 } from "lucide-react";

import { cn } from "@/lib/utils";
import { formatDate, formatTime } from "@/lib/utils";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AnimatedCheckbox } from "@/components/ui/animated-checkbox";
import { DeleteConfirmModal } from "./delete-confirm-modal";
import type { Task, TaskCategory, TaskPriority } from "@/types/entities";
import { CATEGORY_LABELS } from "@/types/entities";
import {
  Briefcase,
  User,
  ShoppingCart,
  Heart,
  MoreHorizontal,
} from "lucide-react";

/**
 * Category icon mapping
 */
const CATEGORY_ICONS: Record<TaskCategory, React.ComponentType<{ className?: string }>> = {
  work: Briefcase,
  personal: User,
  shopping: ShoppingCart,
  health: Heart,
  other: MoreHorizontal,
};

/**
 * T062: Priority color mapping for left bar
 */
const PRIORITY_BAR_COLORS: Record<TaskPriority, string> = {
  high: "bg-lumina-danger-500",
  medium: "bg-lumina-warning-500",
  low: "bg-lumina-success-500",
};

interface TaskCardProps {
  task: Task;
  onToggleComplete?: (id: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (id: string) => void;
}

/**
 * TaskCard - Lumina styled task card with glassmorphism
 * T061-T065: Glass effect, priority bar, animated checkbox, hover lift, completed state
 */
export const TaskCard = memo(function TaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskCardProps) {
  const CategoryIcon = CATEGORY_ICONS[task.category];

  return (
    <motion.div
      layout="position"
      layoutId={task.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.15 } }}
      transition={{
        layout: { type: "spring", stiffness: 300, damping: 30 },
        opacity: { duration: 0.2 },
      }}
      // T064: Hover lift effect
      whileHover={{ y: -4, scale: 1.01 }}
    >
      {/* T061: Glass card wrapper */}
      <GlassCard
        className={cn(
          "group relative cursor-pointer overflow-hidden",
          // T065: Completed styling
          task.completed && "opacity-75"
        )}
        hover={false} // We handle hover via Framer Motion
        onClick={() => onEdit?.(task)}
      >
        {/* T062: Priority color bar (left edge) */}
        <div
          className={cn(
            "absolute left-0 top-0 bottom-0 w-1 rounded-l-xl",
            task.completed ? "bg-lumina-success-500" : PRIORITY_BAR_COLORS[task.priority]
          )}
        />

        <div className="p-4 pl-5">
          {/* Header: Checkbox + Title + Delete */}
          <div className="flex items-start gap-3">
            {/* T063: Animated checkbox */}
            <div
              onClick={(e) => {
                e.stopPropagation();
              }}
              className="pt-0.5"
            >
              <AnimatedCheckbox
                checked={task.completed}
                onChange={() => onToggleComplete?.(task.id)}
                aria-label={`Mark "${task.title}" as ${task.completed ? "incomplete" : "complete"}`}
              />
            </div>

            <div className="flex-1 min-w-0">
              {/* T065: Title with animated strike-through */}
              <motion.h3
                className={cn(
                  "font-medium text-base leading-tight",
                  task.completed && "text-muted-foreground"
                )}
                initial={false}
                animate={{
                  opacity: task.completed ? 0.7 : 1,
                }}
              >
                <span className="relative">
                  {task.title}
                  {/* Animated strike-through line */}
                  <motion.span
                    className="absolute left-0 top-1/2 h-[2px] bg-muted-foreground/60 rounded"
                    initial={false}
                    animate={{
                      width: task.completed ? "100%" : "0%",
                    }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  />
                </span>
              </motion.h3>

              {/* Description preview */}
              {task.description && (
                <p
                  className={cn(
                    "text-sm text-muted-foreground mt-1 line-clamp-2",
                    task.completed && "opacity-60"
                  )}
                >
                  {task.description}
                </p>
              )}

              {/* Metadata row */}
              <div
                className={cn(
                  "flex flex-wrap items-center gap-2 mt-3",
                  task.completed && "opacity-60"
                )}
              >
                {/* Priority badge */}
                <Badge variant={task.priority} className="text-xs">
                  {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                </Badge>

                {/* Category with icon */}
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <CategoryIcon className="h-3 w-3" />
                  <span>{CATEGORY_LABELS[task.category]}</span>
                </div>

                {/* Due date */}
                {task.dueDate && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(task.dueDate)}</span>
                  </div>
                )}

                {/* Due time */}
                {task.dueTime && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>{formatTime(task.dueTime)}</span>
                  </div>
                )}
              </div>

              {/* Tags */}
              {task.tags.length > 0 && (
                <div
                  className={cn(
                    "flex flex-wrap gap-1 mt-2",
                    task.completed && "opacity-60"
                  )}
                >
                  {task.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-0.5 rounded-full bg-lumina-primary-500/10 text-lumina-primary-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Delete button with confirmation modal */}
            <div
              onClick={(e) => e.stopPropagation()}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <DeleteConfirmModal
                taskTitle={task.title}
                onConfirm={() => onDelete?.(task.id)}
                trigger={
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    aria-label={`Delete "${task.title}"`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                }
              />
            </div>
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
});
