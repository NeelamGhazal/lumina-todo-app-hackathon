"use client";

import { useState } from "react";

import {
  AdaptiveDialog,
  AdaptiveDialogContent,
  AdaptiveDialogHeader,
  AdaptiveDialogTitle,
  AdaptiveDialogDescription,
} from "@/components/ui/adaptive-dialog";
import { TaskForm } from "./task-form";
import type { TaskFormData } from "@/lib/validations";

interface AddTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: TaskFormData) => Promise<void>;
}

/**
 * AddTaskModal with spring animation
 * Per spec US2: Modal for creating new tasks with form validation
 * Per spec FR-022: Spring animation for modal open/close
 * Per spec FR-027: Optimistic UI update on task creation
 */
export function AddTaskModal({
  isOpen,
  onClose,
  onSubmit,
}: AddTaskModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
      onClose();
    } catch {
      // Error handling is done in parent via toast
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open && !isSubmitting) {
      onClose();
    }
  };

  return (
    <AdaptiveDialog open={isOpen} onOpenChange={handleOpenChange}>
      <AdaptiveDialogContent showCloseButton={!isSubmitting}>
        <AdaptiveDialogHeader>
          <AdaptiveDialogTitle>Create New Task</AdaptiveDialogTitle>
          <AdaptiveDialogDescription>
            Add a new task to your list. Fill in the details below.
          </AdaptiveDialogDescription>
        </AdaptiveDialogHeader>

        <TaskForm
          onSubmit={handleSubmit}
          onCancel={onClose}
          isSubmitting={isSubmitting}
          submitLabel="Create Task"
        />
      </AdaptiveDialogContent>
    </AdaptiveDialog>
  );
}
