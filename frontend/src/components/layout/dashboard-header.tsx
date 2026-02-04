"use client";

import { Menu, Search, Bell } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { UserMenu } from "./user-menu";
import { Input } from "@/components/ui/input";

export interface DashboardHeaderProps {
  userName?: string;
  userEmail: string;
  isSidebarCollapsed: boolean;
  onMenuClick: () => void;
  onLogout: () => void;
}

/**
 * DashboardHeader - Top header with glass effect
 * T047, T053-T056: Header with search, theme toggle, notifications, user menu
 */
export function DashboardHeader({
  userName,
  userEmail,
  isSidebarCollapsed,
  onMenuClick,
  onLogout,
}: DashboardHeaderProps) {
  const handleSearchClick = () => {
    toast.info("Search coming soon!", {
      description: "We're working on adding search functionality.",
    });
  };

  const handleNotificationClick = () => {
    toast.info("Notifications coming soon!", {
      description: "We're working on adding notifications.",
    });
  };

  return (
    <header
      className={cn(
        "sticky top-0 z-20 h-16",
        "glass-sidebar border-b border-border/50",
        "flex items-center justify-between px-4 md:px-6"
      )}
    >
      {/* Left side: Menu button (mobile) + Search */}
      <div className="flex items-center gap-4">
        {/* T059: Mobile hamburger button - T083: min 44px touch target */}
        <button
          onClick={onMenuClick}
          className="md:hidden p-2.5 rounded-lg hover:bg-muted transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* T053: Search input (visual only) */}
        <div className="hidden sm:block relative w-64 lg:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search tasks..."
            className="pl-9 h-9 bg-muted/50"
            onClick={handleSearchClick}
            readOnly
          />
        </div>
      </div>

      {/* Right side: Actions */}
      <div className="flex items-center gap-2">
        {/* Mobile search button - T083: min 44px touch target */}
        <button
          onClick={handleSearchClick}
          className="sm:hidden p-2.5 rounded-lg hover:bg-muted transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Search"
        >
          <Search className="h-5 w-5" />
        </button>

        {/* T055: Notification bell (visual only) - T083: min 44px touch target */}
        <button
          onClick={handleNotificationClick}
          className="relative p-2.5 rounded-lg hover:bg-muted transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          {/* Notification dot */}
          <span className="absolute top-2 right-2 w-2 h-2 bg-lumina-primary-500 rounded-full" />
        </button>

        {/* T054: Theme toggle */}
        <ThemeToggle size="sm" />

        {/* T056: User menu */}
        <UserMenu
          userName={userName}
          userEmail={userEmail}
          onLogout={onLogout}
        />
      </div>
    </header>
  );
}
