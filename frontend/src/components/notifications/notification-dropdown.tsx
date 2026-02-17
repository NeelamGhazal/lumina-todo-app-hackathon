"use client";

import { Loader2, Bell, Trash2 } from "lucide-react";
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
  return (
    <div
      className={cn(
        "absolute right-0 top-full mt-2 w-80 sm:w-96",
        // ISSUE 1 FIX: Solid background for both themes with backdrop blur
        "bg-white dark:bg-[#1a0033] border border-border rounded-lg",
        "shadow-xl backdrop-blur-md",
        "z-50 overflow-hidden"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30 dark:bg-white/5">
        <div className="flex items-center gap-2">
          {/* ISSUE 2 FIX: Ensure title has proper contrast */}
          <h3 className="font-semibold text-sm text-foreground">Notifications</h3>
          {unreadCount > 0 && (
            // ISSUE 2 FIX: Badge with proper contrast for both themes
            <span className="text-xs bg-purple-600 dark:bg-purple-500 text-white px-2 py-0.5 rounded-full font-medium">
              {unreadCount} new
            </span>
          )}
        </div>
        {notifications.length > 0 && (
          <button
            onClick={onClearAll}
            // ISSUE 2 FIX: Clear all text with proper contrast
            className="text-xs text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white flex items-center gap-1 transition-colors"
            aria-label="Clear all notifications"
          >
            <Trash2 className="h-3 w-3" />
            Clear all
          </button>
        )}
      </div>

      {/* Content */}
      <div className="max-h-[400px] overflow-y-auto">
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
