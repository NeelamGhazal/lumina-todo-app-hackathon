"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

export interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  isActive?: boolean;
  isCollapsed?: boolean;
  count?: number;
  onClick?: () => void;
}

/**
 * SidebarItem - Navigation item for sidebar
 * T046: Individual sidebar navigation item with icon, label, and optional count
 */
export function SidebarItem({
  icon: Icon,
  label,
  isActive = false,
  isCollapsed = false,
  count,
  onClick,
}: SidebarItemProps) {
  return (
    <motion.button
      onClick={onClick}
      className={cn(
        // T083: min-h-[44px] ensures touch target compliance
        "w-full flex items-center gap-3 px-3 py-3 rounded-lg min-h-[44px]",
        "text-sm font-medium transition-colors",
        "hover:bg-lumina-primary-500/10",
        isActive
          ? "bg-lumina-primary-500/15 text-lumina-primary-400"
          : "text-muted-foreground hover:text-foreground"
      )}
      whileHover={{ x: 2 }}
      whileTap={{ scale: 0.98 }}
    >
      <Icon
        className={cn(
          "h-5 w-5 flex-shrink-0",
          isActive ? "text-lumina-primary-400" : "text-muted-foreground"
        )}
      />

      {!isCollapsed && (
        <>
          <span className="flex-1 text-left truncate">{label}</span>
          {count !== undefined && (
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded-full",
                isActive
                  ? "bg-lumina-primary-500/20 text-lumina-primary-400"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {count}
            </span>
          )}
        </>
      )}
    </motion.button>
  );
}
