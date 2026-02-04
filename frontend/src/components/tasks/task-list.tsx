"use client";

import { AnimatePresence, motion, LayoutGroup } from "framer-motion";

import { TaskCard } from "./task-card";
import { EmptyState, EmptyFilterState } from "./empty-state";
import { SkeletonCardGrid } from "./skeleton-card";
import { staggerContainerVariants } from "@/lib/animation-variants";
import type { Task, TaskFilter } from "@/types/entities";

interface TaskListProps {
  tasks: Task[];
  filter: TaskFilter;
  isLoading?: boolean;
  onToggleComplete?: (id: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (id: string) => void;
  onAddTask?: () => void;
}

/**
 * TaskList - Lumina styled task list with stagger animation
 * T066: Stagger animation for task cards
 */
export function TaskList({
  tasks,
  filter,
  isLoading,
  onToggleComplete,
  onEdit,
  onDelete,
  onAddTask,
}: TaskListProps) {
  // Show skeleton while loading
  if (isLoading) {
    return <SkeletonCardGrid count={6} />;
  }

  // Show empty state if no tasks at all
  if (tasks.length === 0 && filter === "all") {
    return <EmptyState onAddTask={onAddTask} />;
  }

  // Show filtered empty state if filter has no results
  if (tasks.length === 0) {
    return <EmptyFilterState filter={filter} />;
  }

  // Sort tasks: pending first, then completed
  const sortedTasks = [...tasks].sort((a, b) => {
    if (a.completed === b.completed) {
      // Sort by creation date within same completion status
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    }
    return a.completed ? 1 : -1;
  });

  return (
    <LayoutGroup>
      {/* T066: Stagger animation container */}
      <motion.div
        className="grid grid-cols-1 gap-4"
        variants={staggerContainerVariants}
        initial="hidden"
        animate="visible"
      >
        <AnimatePresence mode="popLayout">
          {sortedTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </AnimatePresence>
      </motion.div>
    </LayoutGroup>
  );
}
