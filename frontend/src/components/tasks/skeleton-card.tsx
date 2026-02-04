"use client";

import { GlassCard } from "@/components/ui/glass-card";
import { ShimmerSkeleton } from "@/components/ui/shimmer-skeleton";

/**
 * SkeletonCard - Lumina styled loading skeleton
 * T068: Skeleton card with shimmer effect
 */
export function SkeletonCard() {
  return (
    <GlassCard className="overflow-hidden">
      {/* Priority bar skeleton */}
      <div className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl bg-muted animate-pulse" />

      <div className="p-4 pl-5">
        <div className="flex items-start gap-3">
          {/* Checkbox skeleton */}
          <ShimmerSkeleton variant="circular" width={20} height={20} />

          <div className="flex-1 space-y-3">
            {/* Title skeleton */}
            <ShimmerSkeleton variant="text" className="h-5 w-3/4" />

            {/* Description skeleton */}
            <ShimmerSkeleton variant="text" className="h-4 w-full" />
            <ShimmerSkeleton variant="text" className="h-4 w-2/3" />

            {/* Metadata row skeleton */}
            <div className="flex gap-2 pt-1">
              <ShimmerSkeleton variant="rectangular" className="h-5 w-16 rounded-full" />
              <ShimmerSkeleton variant="rectangular" className="h-5 w-20 rounded" />
              <ShimmerSkeleton variant="rectangular" className="h-5 w-24 rounded" />
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

/**
 * Grid of skeleton cards for loading state
 */
export function SkeletonCardGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
