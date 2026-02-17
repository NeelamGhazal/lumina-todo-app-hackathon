"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Bell } from "lucide-react";
import { cn } from "@/lib/utils";
import { NotificationDropdown } from "./notification-dropdown";
import { useNotifications } from "@/hooks/use-notifications";

/**
 * NotificationBell - Bell icon with badge and dropdown
 * T025: Uses useNotifications hook for state management
 * T026: Polling automatically stops on logout via hook
 * T031: Badge displays "99+" for counts > 99
 */
export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const {
    notifications,
    unreadCount,
    isLoading,
    markAsRead,
    clearAll,
    fetchNotifications,
  } = useNotifications();

  // T031: Format badge count (99+ for large numbers)
  const displayCount = unreadCount > 99 ? "99+" : unreadCount.toString();

  // Toggle dropdown and fetch notifications when opening
  const toggleDropdown = useCallback(() => {
    setIsOpen((prev) => {
      const newState = !prev;
      if (newState) {
        fetchNotifications();
      }
      return newState;
    });
  }, [fetchNotifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  return (
    <div ref={dropdownRef} className="relative">
      {/* Bell button */}
      <button
        onClick={toggleDropdown}
        className={cn(
          "relative p-2.5 rounded-lg transition-colors",
          "min-w-[44px] min-h-[44px] flex items-center justify-center",
          isOpen ? "bg-muted" : "hover:bg-muted"
        )}
        aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ""}`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <Bell className="h-5 w-5" />

        {/* Badge - T031: Shows 99+ for large counts */}
        {unreadCount > 0 && (
          <span
            className={cn(
              "absolute flex items-center justify-center",
              "bg-lumina-primary-500 text-white text-[10px] font-medium",
              "rounded-full min-w-[18px] h-[18px] px-1",
              "top-1 right-1"
            )}
          >
            {displayCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <NotificationDropdown
          notifications={notifications}
          unreadCount={unreadCount}
          isLoading={isLoading}
          onMarkRead={markAsRead}
          onClearAll={clearAll}
        />
      )}
    </div>
  );
}
