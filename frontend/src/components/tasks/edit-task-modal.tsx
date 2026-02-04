"use client";

import { useState, useCallback } from "react";

import {
  AdaptiveDialog,
  AdaptiveDialogContent,
  AdaptiveDialogHeader,
  AdaptiveDialogTitle,
  AdaptiveDialogDescription,
} from "@/components/ui/adaptive-dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { TaskForm } from "./task-form";
import type { Task } from "@/types/entities";
import type { TaskFormData } from "@/lib/validations";

interface EditTaskModalProps {
  task: Task | null;
  onClose: () => void;
  onSubmit: (id: string, data: TaskFormData) => Promise<void>;
}

/**
 * EditTaskModal with pre-filled values and unsaved changes detection
 * Per spec US4: Modal for editing existing tasks with form validation
 * Per spec FR-041: Pre-fill form with existing task data
 * Per spec FR-042: Detect unsaved changes and show warning dialog
 */
export function EditTaskModal({
  task,
  onClose,
  onSubmit,
}: EditTaskModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [showDiscardWarning, setShowDiscardWarning] = useState(false);

  const handleSubmit = async (data: TaskFormData) => {
    if (!task) return;

    setIsSubmitting(true);
    try {
      await onSubmit(task.id, data);
      onClose();
    } catch {
      // Error handling is done in parent via toast
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDirtyChange = useCallback((dirty: boolean) => {
    setIsDirty(dirty);
  }, []);

  const handleRequestClose = useCallback(() => {
    if (isDirty && !isSubmitting) {
      setShowDiscardWarning(true);
    } else {
      onClose();
    }
  }, [isDirty, isSubmitting, onClose]);

  const handleOpenChange = (open: boolean) => {
    if (!open && !isSubmitting) {
      handleRequestClose();
    }
  };

  const handleDiscardChanges = () => {
    setShowDiscardWarning(false);
    setIsDirty(false);
    onClose();
  };

  const handleContinueEditing = () => {
    setShowDiscardWarning(false);
  };

  if (!task) return null;

  return (
    <>
      <AdaptiveDialog open={!!task} onOpenChange={handleOpenChange}>
        <AdaptiveDialogContent showCloseButton={!isSubmitting}>
          <AdaptiveDialogHeader>
            <AdaptiveDialogTitle>Edit Task</AdaptiveDialogTitle>
            <AdaptiveDialogDescription>
              Make changes to your task. Click save when you&apos;re done.
            </AdaptiveDialogDescription>
          </AdaptiveDialogHeader>

          <TaskForm
            initialData={task}
            onSubmit={handleSubmit}
            onCancel={handleRequestClose}
            isSubmitting={isSubmitting}
            submitLabel="Save Changes"
            onDirtyChange={handleDirtyChange}
          />
        </AdaptiveDialogContent>
      </AdaptiveDialog>

      {/* Unsaved changes warning dialog */}
      <AlertDialog open={showDiscardWarning} onOpenChange={setShowDiscardWarning}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Discard changes?</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes. Are you sure you want to discard them?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleContinueEditing}>
              Continue Editing
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDiscardChanges}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Discard Changes
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
