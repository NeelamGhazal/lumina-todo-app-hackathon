"use client";

import { useForm, Controller } from "react-hook-form";
import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarIcon, Clock } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { taskSchema, type TaskFormData } from "@/lib/validations";
import { Button } from "@/components/ui/button";
import { AnimatedButton } from "@/components/ui/animated-button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { PrioritySelector } from "./priority-selector";
import { CategorySelect } from "./category-select";
import { TagInput } from "./tag-input";
import type { Task, TaskPriority, TaskCategory } from "@/types/entities";

interface TaskFormProps {
  initialData?: Partial<Task>;
  onSubmit: (data: TaskFormData) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
  submitLabel?: string;
  onDirtyChange?: (isDirty: boolean) => void;
}

/**
 * TaskForm component with all fields
 * Per spec US2: Task form with title, description, priority, category, tags, due date/time
 * Per spec FR-023, FR-024, FR-025, FR-026: Form validation with real-time feedback
 */
export function TaskForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitLabel = "Create Task",
  onDirtyChange,
}: TaskFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialData?.title ?? "",
      description: initialData?.description ?? "",
      priority: initialData?.priority ?? "medium",
      category: initialData?.category ?? "personal",
      tags: initialData?.tags ?? [],
      dueDate: initialData?.dueDate ?? "",
      dueTime: initialData?.dueTime ?? "",
    },
    mode: "onBlur",
  });

  // Notify parent when dirty state changes
  useEffect(() => {
    onDirtyChange?.(isDirty);
  }, [isDirty, onDirtyChange]);

  const handleFormSubmit = async (data: TaskFormData) => {
    // Clean up empty optional fields
    const cleanedData: TaskFormData = {
      ...data,
      description: data.description || undefined,
      dueDate: data.dueDate || undefined,
      dueTime: data.dueTime || undefined,
      tags: data.tags ?? [],
    };
    await onSubmit(cleanedData);
  };

  return (
    <form
      onSubmit={handleSubmit(handleFormSubmit)}
      className="space-y-6 px-6 py-4"
    >
      {/* Title */}
      <div className="space-y-2">
        <label
          htmlFor="title"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Title <span className="text-destructive">*</span>
        </label>
        <Input
          id="title"
          type="text"
          placeholder="What needs to be done?"
          autoComplete="off"
          disabled={isSubmitting}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? "title-error" : undefined}
          className="modal-light-input dark:!bg-[#2d1d4a] dark:!border-[#5a4a7a] dark:!text-[#f3e5f5] dark:placeholder:!text-[#9d8bb5]"
          {...register("title")}
        />
        {errors.title && (
          <p id="title-error" className="text-sm text-destructive">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Description */}
      <div className="space-y-2">
        <label
          htmlFor="description"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Description
        </label>
        <Textarea
          id="description"
          placeholder="Add more details (optional)"
          rows={3}
          disabled={isSubmitting}
          aria-invalid={!!errors.description}
          aria-describedby={errors.description ? "description-error" : undefined}
          className="modal-light-input dark:!bg-[#2d1d4a] dark:!border-[#5a4a7a] dark:!text-[#f3e5f5] dark:placeholder:!text-[#9d8bb5]"
          {...register("description")}
        />
        {errors.description && (
          <p id="description-error" className="text-sm text-destructive">
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Priority and Category - Side by side on larger screens */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Controller
          name="priority"
          control={control}
          render={({ field }) => (
            <PrioritySelector
              value={field.value as TaskPriority}
              onChange={field.onChange}
              disabled={isSubmitting}
            />
          )}
        />

        <Controller
          name="category"
          control={control}
          render={({ field }) => (
            <CategorySelect
              value={field.value as TaskCategory}
              onChange={field.onChange}
              disabled={isSubmitting}
            />
          )}
        />
      </div>

      {/* Tags */}
      <Controller
        name="tags"
        control={control}
        render={({ field }) => (
          <TagInput
            value={field.value ?? []}
            onChange={field.onChange}
            disabled={isSubmitting}
          />
        )}
      />

      {/* Due Date and Time - Side by side */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Due Date with Calendar Popover */}
        <Controller
          name="dueDate"
          control={control}
          render={({ field }) => (
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none">
                Due Date
              </label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={isSubmitting}
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !field.value && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {field.value
                      ? format(new Date(field.value), "PPP")
                      : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={field.value ? new Date(field.value) : undefined}
                    onSelect={(date) => {
                      field.onChange(
                        date ? format(date, "yyyy-MM-dd") : ""
                      );
                    }}
                    disabled={(date) =>
                      date < new Date(new Date().setHours(0, 0, 0, 0))
                    }
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              {errors.dueDate && (
                <p className="text-sm text-destructive">
                  {errors.dueDate.message}
                </p>
              )}
            </div>
          )}
        />

        {/* Due Time */}
        <div className="space-y-2">
          <label
            htmlFor="dueTime"
            className="text-sm font-medium leading-none"
          >
            Due Time
          </label>
          <div className="relative">
            <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="dueTime"
              type="time"
              disabled={isSubmitting}
              className="pl-10 dark:!bg-[#2d1d4a] dark:!border-[#5a4a7a] dark:!text-[#f3e5f5]"
              aria-invalid={!!errors.dueTime}
              {...register("dueTime")}
            />
          </div>
          {errors.dueTime && (
            <p className="text-sm text-destructive">
              {errors.dueTime.message}
            </p>
          )}
        </div>
      </div>

      {/* Form Actions - T077: Styled buttons with loading state */}
      <div className="flex flex-col-reverse gap-2 pt-4 sm:flex-row sm:justify-end">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
          className="border-border/50 hover:border-lumina-primary-500/30"
        >
          Cancel
        </Button>
        <AnimatedButton
          type="submit"
          variant="gradient"
          disabled={isSubmitting}
          isLoading={isSubmitting}
        >
          {submitLabel}
        </AnimatedButton>
      </div>
    </form>
  );
}
