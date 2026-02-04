"use client";

import {
  Briefcase,
  User,
  ShoppingCart,
  Heart,
  MoreHorizontal,
  type LucideIcon,
} from "lucide-react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { type TaskCategory, CATEGORY_LABELS } from "@/types/entities";

interface CategorySelectProps {
  value: TaskCategory;
  onChange: (category: TaskCategory) => void;
  disabled?: boolean;
}

const categoryIcons: Record<TaskCategory, LucideIcon> = {
  work: Briefcase,
  personal: User,
  shopping: ShoppingCart,
  health: Heart,
  other: MoreHorizontal,
};

const categories: TaskCategory[] = [
  "work",
  "personal",
  "shopping",
  "health",
  "other",
];

/**
 * CategorySelect component with icons
 * Per spec US2: Category selection with visual icons
 * Per spec FR-020: Category select dropdown with icons
 */
export function CategorySelect({
  value,
  onChange,
  disabled = false,
}: CategorySelectProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        Category
      </label>
      <Select
        value={value}
        onValueChange={(val) => onChange(val as TaskCategory)}
        disabled={disabled}
      >
        <SelectTrigger
          className="w-full"
          aria-label="Select task category"
        >
          <SelectValue placeholder="Select category">
            {value && (
              <CategoryOption category={value} />
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {categories.map((category) => (
            <SelectItem key={category} value={category}>
              <CategoryOption category={category} />
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function CategoryOption({ category }: { category: TaskCategory }) {
  const Icon = categoryIcons[category];
  return (
    <div className="flex items-center gap-2">
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span>{CATEGORY_LABELS[category]}</span>
    </div>
  );
}
