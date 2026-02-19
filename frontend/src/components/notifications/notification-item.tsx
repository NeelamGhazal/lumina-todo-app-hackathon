"use client";

import { Clock, AlertTriangle, CheckCircle, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Notification, NotificationType } from "@/types/api";

interface NotificationItemProps {
  notification: Notification;
  onMarkRead: (id: string) => void;
}

const typeIcons: Record<NotificationType, React.ReactNode> = {
  TASK_DUE_SOON: <Clock className="h-4 w-4 text-amber-500" />,
  TASK_OVERDUE: <AlertTriangle className="h-4 w-4 text-red-500" />,
  TASK_COMPLETED: <CheckCircle className="h-4 w-4 text-green-500" />,
};

const typeLabels: Record<NotificationType, string> = {
  TASK_DUE_SOON: "Due Soon",
  TASK_OVERDUE: "Overdue",
  TASK_COMPLETED: "Completed",
};

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

/**
 * NotificationItem - Single notification display
 * Shows type icon, message, timestamp, and mark-as-read button
 */
export function NotificationItem({ notification, onMarkRead }: NotificationItemProps) {
  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg transition-colors",
        notification.isRead
          ? "bg-white dark:!bg-[#1a0033] opacity-60"
          : "bg-purple-50 dark:!bg-[#2d1b4e] hover:bg-purple-100 dark:hover:!bg-[#3d2a5e]"
      )}
    >
      {/* Type icon */}
      <div className="flex-shrink-0 mt-0.5">
        {typeIcons[notification.type]}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p
          className={cn(
            "text-sm leading-snug",
            notification.isRead ? "text-muted-foreground" : "text-foreground font-medium"
          )}
        >
          {notification.message}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-muted-foreground">
            {typeLabels[notification.type]}
          </span>
          <span className="text-xs text-muted-foreground">
            {formatRelativeTime(notification.createdAt)}
          </span>
          {/* T030: Show indicator if task was deleted */}
          {!notification.taskId && notification.type !== "TASK_COMPLETED" && (
            <span className="text-xs text-muted-foreground/70 italic">
              (task removed)
            </span>
          )}
        </div>
      </div>

      {/* Mark as read button */}
      {!notification.isRead && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onMarkRead(notification.id);
          }}
          className="flex-shrink-0 p-1.5 rounded-md hover:bg-purple-100 dark:hover:!bg-[#3d2a5e] transition-colors"
          aria-label="Mark as read"
          title="Mark as read"
        >
          <Check className="h-4 w-4 text-muted-foreground hover:text-foreground" />
        </button>
      )}
    </div>
  );
}
