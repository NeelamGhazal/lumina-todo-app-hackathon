"use client";

import { cn } from "@/lib/utils";

export interface ShimmerSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular";
  width?: string | number;
  height?: string | number;
}

/**
 * ShimmerSkeleton - Loading skeleton with shimmer animation
 * T011: Foundational component for Lumina design system
 */
function ShimmerSkeleton({
  className,
  variant = "rectangular",
  width,
  height,
  style,
  ...props
}: ShimmerSkeletonProps) {
  const variantClasses = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-lg",
  };

  return (
    <div
      className={cn(
        "skeleton-shimmer",
        "bg-muted",
        variantClasses[variant],
        className
      )}
      style={{
        width: width,
        height: height,
        ...style,
      }}
      {...props}
    />
  );
}

/**
 * ShimmerSkeletonGroup - Container for multiple skeletons with stagger
 */
function ShimmerSkeletonGroup({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("space-y-3", className)}
      role="status"
      aria-label="Loading..."
      {...props}
    >
      {children}
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export { ShimmerSkeleton, ShimmerSkeletonGroup };
