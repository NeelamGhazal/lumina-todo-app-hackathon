"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { TaskFilter } from "@/types/entities";

interface FilterTabsProps {
  activeFilter: TaskFilter;
  counts: {
    all: number;
    pending: number;
    completed: number;
  };
  onFilterChange: (filter: TaskFilter) => void;
}

const filters: { value: TaskFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
];

/**
 * FilterTabs component (All/Pending/Completed)
 * Per spec US1: Filter buttons with smooth animation, active filter highlighted
 * Per spec FR-013, FR-014: Filter by status with task count
 */
export function FilterTabs({
  activeFilter,
  counts,
  onFilterChange,
}: FilterTabsProps) {
  return (
    <div className="flex items-center gap-1 p-1 bg-muted rounded-lg">
      {filters.map((filter) => {
        const isActive = activeFilter === filter.value;
        const count = counts[filter.value];

        return (
          <button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-all duration-200",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              isActive
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-background/50"
            )}
            aria-pressed={isActive}
            aria-label={`Show ${filter.label.toLowerCase()} tasks (${count})`}
          >
            {filter.label}
            <Badge
              variant={isActive ? "default" : "secondary"}
              className={cn(
                "h-5 min-w-[20px] px-1.5 text-xs",
                !isActive && "bg-muted-foreground/20"
              )}
            >
              {count}
            </Badge>
          </button>
        );
      })}
    </div>
  );
}
