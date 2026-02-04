"use client";

import { cn } from "@/lib/utils";
import { forwardRef } from "react";

export type GradientVariant = "primary" | "accent" | "success" | "warm";

export interface GradientTextProps extends React.HTMLAttributes<HTMLElement> {
  as?: "h1" | "h2" | "h3" | "h4" | "span" | "p";
  variant?: GradientVariant;
  animate?: boolean;
}

// LUMINA gradient variants - uses CSS custom properties for theme-awareness
// Light mode: dark purples for visibility
// Dark mode: bright purples/lavenders for visibility
const gradientMap: Record<GradientVariant, string> = {
  primary: "gradient-text-primary",
  accent: "gradient-text-accent",
  success: "from-lumina-success-400 to-lumina-success-500",
  warm: "from-lumina-warning-400 via-lumina-primary-500 to-lumina-primary-600",
};

/**
 * GradientText - Text component with gradient backgrounds
 * T010: Foundational component for Lumina design system
 */
const GradientText = forwardRef<HTMLElement, GradientTextProps>(
  ({ as: Component = "span", variant = "primary", animate = false, className, children, ...props }, ref) => {
    return (
      <Component
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        ref={ref as any}
        className={cn(
          "bg-gradient-to-r bg-clip-text text-transparent",
          gradientMap[variant],
          animate && "animate-shimmer bg-[length:200%_100%]",
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

GradientText.displayName = "GradientText";

export { GradientText };
