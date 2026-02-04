"use client";

import { cn } from "@/lib/utils";
import { forwardRef } from "react";

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  blur?: "sm" | "md" | "lg" | "xl";
  hover?: boolean;
  glow?: boolean;
}

/**
 * GlassCard - Glassmorphism card component with configurable blur and effects
 * T009: Foundational component for Lumina design system
 */
const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, children, blur = "md", hover = false, glow = false, ...props }, ref) => {
    const blurMap = {
      sm: "backdrop-blur-sm",
      md: "backdrop-blur-md",
      lg: "backdrop-blur-lg",
      xl: "backdrop-blur-xl",
    };

    return (
      <div
        ref={ref}
        className={cn(
          // Base glass styling
          "rounded-xl border",
          "bg-card/70 dark:bg-card/80",
          "border-border/30 dark:border-border/20",
          blurMap[blur],
          // Shadows
          "shadow-glass",
          // Hover effects
          hover && [
            "transition-all duration-300 ease-out",
            "hover:-translate-y-1",
            "hover:shadow-glass-lg",
          ],
          // Glow effect
          glow && [
            "hover:shadow-glow",
            "dark:hover:shadow-glow-lg",
          ],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = "GlassCard";

export { GlassCard };
