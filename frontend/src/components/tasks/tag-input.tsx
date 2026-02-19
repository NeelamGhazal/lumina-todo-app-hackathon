"use client";

import { useState, useCallback, KeyboardEvent } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
  maxTags?: number;
}

/**
 * TagInput component for comma-separated tags
 * Per spec US2: Tag input that accepts comma-separated values
 * Per spec FR-021: Tag input with badge display
 */
export function TagInput({
  value,
  onChange,
  disabled = false,
  placeholder = "Add tags (press Enter or comma)",
  maxTags = 10,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");

  const addTag = useCallback(
    (tag: string) => {
      const trimmedTag = tag.trim().toLowerCase();
      if (
        trimmedTag &&
        !value.includes(trimmedTag) &&
        value.length < maxTags
      ) {
        onChange([...value, trimmedTag]);
      }
    },
    [value, onChange, maxTags]
  );

  const removeTag = useCallback(
    (tagToRemove: string) => {
      onChange(value.filter((tag) => tag !== tagToRemove));
    },
    [value, onChange]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" || e.key === ",") {
        e.preventDefault();
        addTag(inputValue);
        setInputValue("");
      } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
        const lastTag = value[value.length - 1];
        if (lastTag) removeTag(lastTag);
      }
    },
    [inputValue, value, addTag, removeTag]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      // Handle comma in input (split and add tags)
      if (newValue.includes(",")) {
        const tags = newValue.split(",");
        tags.forEach((tag, index) => {
          if (index < tags.length - 1) {
            addTag(tag);
          } else {
            setInputValue(tag);
          }
        });
      } else {
        setInputValue(newValue);
      }
    },
    [addTag]
  );

  const handleBlur = useCallback(() => {
    if (inputValue.trim()) {
      addTag(inputValue);
      setInputValue("");
    }
  }, [inputValue, addTag]);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        Tags
        {value.length > 0 && (
          <span className="ml-2 text-xs text-muted-foreground">
            ({value.length}/{maxTags})
          </span>
        )}
      </label>
      <div
        className={cn(
          "tags-input-box flex flex-wrap items-center gap-2 px-4 py-4 min-h-[52px] rounded-md bg-transparent border border-purple-200 dark:border-purple-800",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        {value.map((tag) => (
          <Badge
            key={tag}
            variant="secondary"
            className="flex items-center gap-1 px-2 py-1"
          >
            {tag}
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1 rounded-full hover:bg-muted-foreground/20 p-0.5"
                aria-label={`Remove tag ${tag}`}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </Badge>
        ))}
        {value.length < maxTags && (
          <Input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onBlur={handleBlur}
            disabled={disabled}
            placeholder={value.length === 0 ? placeholder : ""}
            className="tags-input-field flex-1 min-w-[120px] h-auto bg-transparent border-none !text-gray-900 placeholder-gray-400 dark:!bg-transparent dark:!border-none dark:!text-white dark:placeholder-purple-300"
            aria-label="Add tag"
          />
        )}
      </div>
      <p className="text-xs text-muted-foreground">
        Press Enter or comma to add a tag
      </p>
    </div>
  );
}
