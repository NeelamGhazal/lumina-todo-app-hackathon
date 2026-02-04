"use client";

import { cn } from "@/lib/utils";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface ThemeToggleProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

// T083: All sizes meet minimum 44px touch target
const sizeMap = {
  sm: { button: "h-10 w-10 min-w-[44px] min-h-[44px]", icon: 16 },
  md: { button: "h-11 w-11 min-w-[44px] min-h-[44px]", icon: 18 },
  lg: { button: "h-12 w-12", icon: 22 },
};

/**
 * ThemeToggle - Animated theme switcher with Moon/Sun icons
 * T014: Foundational component for Lumina design system
 */
function ThemeToggle({ className, size = "md" }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div
        className={cn(
          "rounded-lg bg-muted animate-pulse",
          sizeMap[size].button,
          className
        )}
      />
    );
  }

  const isDark = theme === "dark";
  const { button, icon } = sizeMap[size];

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className={cn(
        "relative inline-flex items-center justify-center rounded-lg",
        "bg-secondary hover:bg-secondary/80",
        "transition-colors duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        button,
        className
      )}
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={isDark ? "dark" : "light"}
          initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
          animate={{ opacity: 1, rotate: 0, scale: 1 }}
          exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
          transition={{ duration: 0.2 }}
        >
          {isDark ? (
            <Sun size={icon} className="text-lumina-warning-400" />
          ) : (
            <Moon size={icon} className="text-lumina-primary-500" />
          )}
        </motion.div>
      </AnimatePresence>
    </button>
  );
}

export { ThemeToggle };
