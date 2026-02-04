"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Plus } from "lucide-react";

import { useTasks } from "@/hooks/use-tasks";
import { useFilter } from "@/contexts/filter-context";
import { TaskList } from "@/components/tasks/task-list";
import { FilterTabs } from "@/components/tasks/filter-tabs";
import { AddTaskModal } from "@/components/tasks/add-task-modal";
import { EditTaskModal } from "@/components/tasks/edit-task-modal";
import { AnimatedButton } from "@/components/ui/animated-button";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants } from "@/lib/animation-variants";
import type { Task, TaskFilter } from "@/types/entities";
import type { TaskFormData } from "@/lib/validations";
import type { UpdateTaskRequest } from "@/types/api";

/**
 * Tasks page - Lumina styled dashboard
 * T069, T070: Gradient Add Task button, responsive grid layout
 * Now syncs with sidebar filters via FilterContext
 */
export default function TasksPage() {
  // Get sidebar filter state from context
  const {
    filter: sidebarFilter,
    category: sidebarCategory,
    priority: sidebarPriority,
    setFilter: setSidebarFilter,
    setCounts,
  } = useFilter();

  const {
    filteredTasks,
    filter,
    setFilter,
    categoryFilter,
    setCategoryFilter,
    priorityFilter,
    setPriorityFilter,
    counts,
    isLoading,
    createTask,
    updateTask,
    toggleComplete,
    deleteTask,
  } = useTasks();

  // Sync sidebar filters to useTasks
  useEffect(() => {
    // Map sidebar filter type to task filter type
    // Sidebar uses "all" | "active" | "completed"
    // useTasks uses "all" | "pending" | "completed"
    const taskFilter: TaskFilter = sidebarFilter === "active" ? "pending" : sidebarFilter;
    setFilter(taskFilter);
  }, [sidebarFilter, setFilter]);

  // Sync category filter
  useEffect(() => {
    // sidebarCategory is "work" | "personal" | "home" | null
    // Task category is "work" | "personal" | "shopping" | "health" | "other"
    // Direct mapping for work/personal, home has no match (will show no results)
    setCategoryFilter(sidebarCategory as typeof categoryFilter);
  }, [sidebarCategory, setCategoryFilter]);

  // Sync priority filter
  useEffect(() => {
    setPriorityFilter(sidebarPriority);
  }, [sidebarPriority, setPriorityFilter]);

  // Update sidebar counts when task counts change
  useEffect(() => {
    setCounts({
      all: counts.all,
      active: counts.pending,
      completed: counts.completed,
    });
  }, [counts, setCounts]);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  function handleAddTask() {
    setIsAddModalOpen(true);
  }

  function handleCloseAddModal() {
    setIsAddModalOpen(false);
  }

  async function handleCreateTask(data: TaskFormData) {
    await createTask({
      title: data.title,
      description: data.description,
      priority: data.priority,
      category: data.category,
      tags: data.tags,
      dueDate: data.dueDate,
      dueTime: data.dueTime,
    });
  }

  function handleEditTask(task: Task) {
    setEditingTask(task);
  }

  function handleCloseEditModal() {
    setEditingTask(null);
  }

  async function handleUpdateTask(id: string, data: TaskFormData) {
    const updateData: UpdateTaskRequest = {
      title: data.title,
      description: data.description,
      priority: data.priority,
      category: data.category,
      tags: data.tags,
      dueDate: data.dueDate,
      dueTime: data.dueTime,
    };
    await updateTask(id, updateData);
  }

  return (
    <motion.div
      className="space-y-6"
      variants={fadeUpVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            <GradientText variant="primary">Tasks</GradientText>
          </h1>
          <p className="text-muted-foreground">
            Manage your tasks and illuminate your productivity
          </p>
        </div>

        {/* T069: Gradient Add Task button */}
        <AnimatedButton variant="gradient" onClick={handleAddTask}>
          <Plus className="h-4 w-4 mr-2" />
          Add Task
        </AnimatedButton>
      </div>

      {/* Filter tabs - sync with sidebar */}
      <FilterTabs
        activeFilter={filter}
        counts={counts}
        onFilterChange={(newFilter) => {
          setFilter(newFilter);
          // Also update sidebar - map pending back to active
          const sidebarFilterValue = newFilter === "pending" ? "active" : newFilter;
          setSidebarFilter(sidebarFilterValue as typeof sidebarFilter);
        }}
      />

      {/* T070: Task list with responsive grid (1/2/3 columns) */}
      <TaskList
        tasks={filteredTasks}
        filter={filter}
        isLoading={isLoading}
        onToggleComplete={toggleComplete}
        onEdit={handleEditTask}
        onDelete={deleteTask}
        onAddTask={handleAddTask}
      />

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={isAddModalOpen}
        onClose={handleCloseAddModal}
        onSubmit={handleCreateTask}
      />

      {/* Edit Task Modal */}
      <EditTaskModal
        task={editingTask}
        onClose={handleCloseEditModal}
        onSubmit={handleUpdateTask}
      />
    </motion.div>
  );
}
