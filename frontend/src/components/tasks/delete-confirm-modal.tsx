"use client";

import { useState } from "react";
import { Trash2, AlertTriangle } from "lucide-react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

interface DeleteConfirmModalProps {
  taskTitle: string;
  onConfirm: () => void;
  trigger?: React.ReactNode;
}

/**
 * DeleteConfirmModal with danger styling
 * Per spec US5: Confirmation dialog before deleting a task
 * Per spec FR-051: Show confirmation dialog with task title
 * Per spec FR-052: Danger styling to indicate destructive action
 */
export function DeleteConfirmModal({
  taskTitle,
  onConfirm,
  trigger,
}: DeleteConfirmModalProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleConfirm = () => {
    onConfirm();
    setIsOpen(false);
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
      <AlertDialogTrigger asChild>
        {trigger ?? (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
            aria-label={`Delete "${taskTitle}"`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <div>
              <AlertDialogTitle>Delete Task</AlertDialogTitle>
              <AlertDialogDescription className="mt-1">
                Are you sure you want to delete this task? You can undo this action for 5 seconds after deletion.
              </AlertDialogDescription>
            </div>
          </div>
        </AlertDialogHeader>

        {/* Task preview */}
        <div className="my-4 rounded-lg border bg-muted/50 p-3">
          <p className="text-sm font-medium truncate">{taskTitle}</p>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Task
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
