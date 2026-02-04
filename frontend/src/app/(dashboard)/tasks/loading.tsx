import { Skeleton } from "@/components/ui/skeleton";
import { SkeletonCardGrid } from "@/components/tasks/skeleton-card";

/**
 * Loading state for tasks page
 * Per spec FR-011: Show skeleton loading states while fetching data
 */
export default function TasksLoading() {
  return (
    <div className="space-y-6">
      {/* Page header skeleton */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-2">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-5 w-48" />
        </div>
        <Skeleton className="h-10 w-28" />
      </div>

      {/* Filter tabs skeleton */}
      <div className="flex gap-2">
        <Skeleton className="h-10 w-20 rounded-lg" />
        <Skeleton className="h-10 w-24 rounded-lg" />
        <Skeleton className="h-10 w-28 rounded-lg" />
      </div>

      {/* Task cards skeleton */}
      <SkeletonCardGrid count={6} />
    </div>
  );
}
