// Task T014: SidebarLink component for navigation links
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

export interface SidebarLinkProps {
  href: string;
  icon: LucideIcon;
  label: string;
  isCollapsed?: boolean;
  onClick?: () => void;
}

/**
 * SidebarLink - Navigation link for sidebar
 * Task T014: Chat link component with active state styling
 */
export function SidebarLink({
  href,
  icon: Icon,
  label,
  isCollapsed = false,
  onClick,
}: SidebarLinkProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link href={href} onClick={onClick}>
      <motion.div
        className={cn(
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
          <span className="flex-1 text-left truncate">{label}</span>
        )}
      </motion.div>
    </Link>
  );
}
