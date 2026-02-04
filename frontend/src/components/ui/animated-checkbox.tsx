"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface AnimatedCheckboxProps {
  checked: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
  "aria-label"?: string;
}

/**
 * AnimatedCheckbox with SVG draw effect
 * Per spec US3: Checkmark draws with smooth animation (200ms with bounce)
 * Per spec FR-031: Animate completion toggle with checkmark draw effect
 */
export function AnimatedCheckbox({
  checked,
  onChange,
  disabled = false,
  className,
  "aria-label": ariaLabel,
}: AnimatedCheckboxProps) {
  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      aria-label={ariaLabel}
      disabled={disabled}
      onClick={() => onChange?.(!checked)}
      className={cn(
        "relative flex items-center justify-center",
        "h-5 w-5 shrink-0 rounded-md border-2 transition-colors duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50",
        checked
          ? "border-green-500 bg-green-500"
          : "border-muted-foreground/50 bg-transparent hover:border-muted-foreground",
        className
      )}
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        className="h-3.5 w-3.5"
        aria-hidden="true"
      >
        <motion.path
          d="M5 12.5L10 17.5L19 6.5"
          stroke="white"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={false}
          animate={{
            pathLength: checked ? 1 : 0,
            opacity: checked ? 1 : 0,
          }}
          transition={{
            pathLength: {
              type: "spring",
              stiffness: 300,
              damping: 20,
              duration: 0.2,
            },
            opacity: { duration: 0.1 },
          }}
        />
      </svg>

      {/* Ripple effect on check */}
      {checked && (
        <motion.span
          className="absolute inset-0 rounded-md bg-green-500"
          initial={{ scale: 0.8, opacity: 0.5 }}
          animate={{ scale: 1.2, opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      )}
    </button>
  );
}
