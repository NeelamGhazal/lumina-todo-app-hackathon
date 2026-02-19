"use client";

import { Loader2, Bell, Trash2 } from "lucide-react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";
import { NotificationItem } from "./notification-item";
import type { Notification } from "@/types/api";

interface NotificationDropdownProps {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  onMarkRead: (id: string) => void;
  onClearAll: () => void;
}

/**
 * NotificationDropdown - Dropdown panel showing notification list
 * Shows up to 20 notifications with scroll, header with clear all
 */
export function NotificationDropdown({
  notifications,
  unreadCount,
  isLoading,
  onMarkRead,
  onClearAll,
}: NotificationDropdownProps) {
  const { resolvedTheme } = useTheme();

  // Inline styles for cross-browser consistency
  const bgStyle = { backgroundColor: resolvedTheme === 'dark' ? '#1a0033' : '#ffffff' };
  const headerBgStyle = { backgroundColor: resolvedTheme === 'dark' ? '#2e1a47' : '#f9fafb' };

  return (
    <div
      className={cn(
        "absolute right-0 top-full mt-2 w-80 sm:w-96",
        "border border-border rounded-lg",
        "shadow-xl",
        "z-50 overflow-hidden"
      )}
      style={bgStyle}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b border-border"
        style={headerBgStyle}
      >
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-sm text-foreground">Notifications</h3>
          {unreadCount > 0 && (
            <span className="text-xs bg-purple-600 dark:bg-purple-500 text-white px-2 py-0.5 rounded-full font-medium">
              {unreadCount} new
            </span>
          )}
        </div>
        {notifications.length > 0 && (
          <button
            onClick={onClearAll}
            className="text-xs text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center gap-1 transition-colors"
            aria-label="Clear all notifications"
          >
            <Trash2 className="h-3 w-3" />
            Clear all
          </button>
        )}
      </div>

      {/* Content */}
      <div
        className="max-h-[400px] overflow-y-auto"
        style={bgStyle}
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <Bell className="h-10 w-10 text-muted-foreground/50 mb-2" />
            <p className="text-sm text-muted-foreground">No notifications yet</p>
            <p className="text-xs text-muted-foreground/70 mt-1">
              We'll notify you about task deadlines
            </p>
          </div>
        ) : (
          <div className="p-2 space-y-1">
            {notifications.map((notification) => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkRead={onMarkRead}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
