"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  type TaskPriority,
  PRIORITY_COLORS,
  PRIORITY_LABELS,
} from "@/types/entities";

interface PrioritySelectorProps {
  value: TaskPriority;
  onChange: (priority: TaskPriority) => void;
  disabled?: boolean;
}

const priorities: TaskPriority[] = ["high", "medium", "low"];

/**
 * PrioritySelector component with colored badges
 * Per spec US2: Priority selection with visual color coding
 * Per spec FR-019: Priority selector with colored badges
 */
export function PrioritySelector({
  value,
  onChange,
  disabled = false,
}: PrioritySelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        Priority
      </label>
      <div
        className="flex flex-wrap gap-2"
        role="radiogroup"
        aria-label="Select task priority"
      >
        {priorities.map((priority) => {
          const colors = PRIORITY_COLORS[priority];
          const isSelected = value === priority;

          return (
            <button
              key={priority}
              type="button"
              role="radio"
              aria-checked={isSelected}
              disabled={disabled}
              onClick={() => onChange(priority)}
              className={cn(
                "transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                "disabled:cursor-not-allowed disabled:opacity-50"
              )}
            >
              <Badge
                variant="outline"
                className={cn(
                  "cursor-pointer px-3 py-1.5 text-sm font-medium transition-all duration-200",
                  isSelected
                    ? cn(colors.bg, colors.text, colors.border, "ring-2 ring-offset-2 ring-current")
                    : "bg-muted/50 text-muted-foreground hover:bg-muted border-transparent"
                )}
              >
                {PRIORITY_LABELS[priority]}
              </Badge>
            </button>
          );
        })}
      </div>
    </div>
  );
}
