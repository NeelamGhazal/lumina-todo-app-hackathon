"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";
import type { Task, TaskFilter, TaskCategory, TaskPriority, OptimisticTask } from "@/types/entities";
import type { CreateTaskRequest, UpdateTaskRequest } from "@/types/api";
import { generateId } from "@/lib/utils";

interface UseTasksState {
  tasks: OptimisticTask[];
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
  isLoading: boolean;
  error: string | null;
}

interface UseTasksReturn extends UseTasksState {
  filter: TaskFilter;
  setFilter: (filter: TaskFilter) => void;
  categoryFilter: TaskCategory | null;
  setCategoryFilter: (category: TaskCategory | null) => void;
  priorityFilter: TaskPriority | null;
  setPriorityFilter: (priority: TaskPriority | null) => void;
  filteredTasks: OptimisticTask[];
  createTask: (data: CreateTaskRequest) => Promise<void>;
  updateTask: (id: string, data: UpdateTaskRequest) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  toggleComplete: (id: string) => Promise<void>;
  refresh: () => Promise<void>;
}

/**
 * Hook for managing tasks with optimistic updates
 * Per spec FR-027, FR-034, FR-043, FR-054: Optimistic UI updates
 */
export function useTasks(): UseTasksReturn {
  const [state, setState] = useState<UseTasksState>({
    tasks: [],
    counts: { all: 0, pending: 0, completed: 0 },
    isLoading: true,
    error: null,
  });
  const [filter, setFilter] = useState<TaskFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<TaskCategory | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | null>(null);

  /**
   * Fetch tasks from API
   */
  const fetchTasks = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      const response = await api.tasks.list();
      setState({
        tasks: response.tasks,
        counts: response.counts,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const message =
        error instanceof ApiClientError
          ? error.message
          : "Failed to load tasks";
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: message,
      }));
      toast.error("Failed to load tasks", {
        description: message,
        action: {
          label: "Retry",
          onClick: () => fetchTasks(),
        },
      });
    }
  }, []);

  /**
   * Create a new task with optimistic update
   */
  const createTask = useCallback(async (data: CreateTaskRequest) => {
    const optimisticId = generateId();
    const optimisticTask: OptimisticTask = {
      id: optimisticId,
      userId: "",
      ...data,
      tags: data.tags ?? [],
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      _optimistic: true,
    };

    // Optimistic update
    setState((prev) => ({
      ...prev,
      tasks: [optimisticTask, ...prev.tasks],
      counts: {
        ...prev.counts,
        all: prev.counts.all + 1,
        pending: prev.counts.pending + 1,
      },
    }));

    try {
      const response = await api.tasks.create(data);
      // Replace optimistic task with real one
      setState((prev) => ({
        ...prev,
        tasks: prev.tasks.map((t) =>
          t.id === optimisticId ? response.task : t
        ),
      }));
      toast.success("Task created!", {
        description: `"${data.title}" has been added.`,
      });
    } catch (error) {
      // Revert optimistic update
      setState((prev) => ({
        ...prev,
        tasks: prev.tasks.filter((t) => t.id !== optimisticId),
        counts: {
          ...prev.counts,
          all: prev.counts.all - 1,
          pending: prev.counts.pending - 1,
        },
      }));
      const message =
        error instanceof ApiClientError
          ? error.message
          : "Failed to create task";
      toast.error("Failed to create task", {
        description: message,
        action: {
          label: "Retry",
          onClick: () => createTask(data),
        },
      });
    }
  }, []);

  /**
   * Update an existing task with optimistic update
   */
  const updateTask = useCallback(
    async (id: string, data: UpdateTaskRequest) => {
      const previousTask = state.tasks.find((t) => t.id === id);
      if (!previousTask) return;

      // Clean data: convert null to undefined for Task type compatibility
      const cleanedData = Object.fromEntries(
        Object.entries(data).map(([key, value]) => [key, value === null ? undefined : value])
      ) as Partial<Task>;

      // Optimistic update
      setState((prev) => ({
        ...prev,
        tasks: prev.tasks.map((t) =>
          t.id === id
            ? { ...t, ...cleanedData, _optimistic: true, _previousState: previousTask }
            : t
        ),
      }));

      try {
        const response = await api.tasks.update(id, data);
        setState((prev) => ({
          ...prev,
          tasks: prev.tasks.map((t) => (t.id === id ? response.task : t)),
        }));
        toast.success("Task updated!", {
          description: "Your changes have been saved.",
        });
      } catch (error) {
        // Revert optimistic update
        setState((prev) => ({
          ...prev,
          tasks: prev.tasks.map((t) => (t.id === id ? previousTask : t)),
        }));
        const message =
          error instanceof ApiClientError
            ? error.message
            : "Failed to update task";
        toast.error("Failed to update task", {
          description: message,
          action: {
            label: "Retry",
            onClick: () => updateTask(id, data),
          },
        });
      }
    },
    [state.tasks]
  );

  /**
   * Delete a task with optimistic update and undo support
   */
  const deleteTask = useCallback(
    async (id: string) => {
      const taskToDelete = state.tasks.find((t) => t.id === id);
      if (!taskToDelete) return;

      // Optimistic update
      setState((prev) => ({
        ...prev,
        tasks: prev.tasks.filter((t) => t.id !== id),
        counts: {
          ...prev.counts,
          all: prev.counts.all - 1,
          pending: taskToDelete.completed
            ? prev.counts.pending
            : prev.counts.pending - 1,
          completed: taskToDelete.completed
            ? prev.counts.completed - 1
            : prev.counts.completed,
        },
      }));

      // Store for undo
      let undone = false;
      const undoDelete = () => {
        undone = true;
        setState((prev) => ({
          ...prev,
          tasks: [...prev.tasks, taskToDelete],
          counts: {
            ...prev.counts,
            all: prev.counts.all + 1,
            pending: taskToDelete.completed
              ? prev.counts.pending
              : prev.counts.pending + 1,
            completed: taskToDelete.completed
              ? prev.counts.completed + 1
              : prev.counts.completed,
          },
        }));
        toast.success("Task restored", {
          description: `"${taskToDelete.title}" has been restored.`,
        });
      };

      toast.success("Task deleted", {
        description: `"${taskToDelete.title}" has been removed.`,
        action: {
          label: "Undo",
          onClick: undoDelete,
        },
        duration: 5000,
      });

      // Delay API call to allow undo
      setTimeout(async () => {
        if (undone) return;

        try {
          await api.tasks.delete(id);
        } catch (error) {
          // Revert if API fails
          setState((prev) => ({
            ...prev,
            tasks: [...prev.tasks, taskToDelete],
            counts: {
              ...prev.counts,
              all: prev.counts.all + 1,
              pending: taskToDelete.completed
                ? prev.counts.pending
                : prev.counts.pending + 1,
              completed: taskToDelete.completed
                ? prev.counts.completed + 1
                : prev.counts.completed,
            },
          }));
          const message =
            error instanceof ApiClientError
              ? error.message
              : "Failed to delete task";
          toast.error("Failed to delete task", {
            description: message,
          });
        }
      }, 5000);
    },
    [state.tasks]
  );

  /**
   * Toggle task completion with optimistic update
   */
  const toggleComplete = useCallback(
    async (id: string) => {
      const task = state.tasks.find((t) => t.id === id);
      if (!task) return;

      const newCompleted = !task.completed;

      // Optimistic update
      setState((prev) => ({
        ...prev,
        tasks: prev.tasks.map((t) =>
          t.id === id
            ? {
                ...t,
                completed: newCompleted,
                completedAt: newCompleted ? new Date().toISOString() : undefined,
                _optimistic: true,
              }
            : t
        ),
        counts: {
          ...prev.counts,
          pending: newCompleted
            ? prev.counts.pending - 1
            : prev.counts.pending + 1,
          completed: newCompleted
            ? prev.counts.completed + 1
            : prev.counts.completed - 1,
        },
      }));

      try {
        const response = await api.tasks.toggleComplete(id);
        setState((prev) => ({
          ...prev,
          tasks: prev.tasks.map((t) => (t.id === id ? response.task : t)),
        }));
        toast.success(
          newCompleted ? "Task completed! 🎉" : "Task marked as pending"
        );
      } catch (error) {
        // Revert optimistic update
        setState((prev) => ({
          ...prev,
          tasks: prev.tasks.map((t) =>
            t.id === id
              ? { ...t, completed: !newCompleted, completedAt: task.completedAt }
              : t
          ),
          counts: {
            ...prev.counts,
            pending: newCompleted
              ? prev.counts.pending + 1
              : prev.counts.pending - 1,
            completed: newCompleted
              ? prev.counts.completed - 1
              : prev.counts.completed + 1,
          },
        }));
        const message =
          error instanceof ApiClientError
            ? error.message
            : "Failed to update task";
        toast.error("Failed to update task", {
          description: message,
          action: {
            label: "Retry",
            onClick: () => toggleComplete(id),
          },
        });
      }
    },
    [state.tasks]
  );

  /**
   * Filter tasks based on current filters (status, category, priority)
   * Supports composable filtering - multiple filters can be active
   */
  const filteredTasks = useMemo(() => {
    let result = state.tasks;

    // Filter by completion status
    switch (filter) {
      case "pending":
        result = result.filter((t) => !t.completed);
        break;
      case "completed":
        result = result.filter((t) => t.completed);
        break;
      // "all" - no status filtering
    }

    // Filter by category (graceful no-op if category doesn't exist on task)
    if (categoryFilter) {
      result = result.filter((t) => {
        // Handle potential mismatch between sidebar categories and task categories
        // Sidebar uses: work, personal, home
        // Task model uses: work, personal, shopping, health, other
        if (!t.category) return false;
        return t.category.toLowerCase() === categoryFilter.toLowerCase();
      });
    }

    // Filter by priority
    if (priorityFilter) {
      result = result.filter((t) => {
        if (!t.priority) return false;
        return t.priority.toLowerCase() === priorityFilter.toLowerCase();
      });
    }

    return result;
  }, [state.tasks, filter, categoryFilter, priorityFilter]);

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    ...state,
    filter,
    setFilter,
    categoryFilter,
    setCategoryFilter,
    priorityFilter,
    setPriorityFilter,
    filteredTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    refresh: fetchTasks,
  };
}
