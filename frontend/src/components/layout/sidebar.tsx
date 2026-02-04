"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  LayoutDashboard,
  CheckCircle2,
  Circle,
  ListTodo,
  Briefcase,
  User,
  Heart,
  ShoppingCart,
  MoreHorizontal,
  AlertTriangle,
  ArrowUp,
  ArrowDown,
  LogOut,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { GradientText } from "@/components/ui/gradient-text";
import { SidebarItem } from "./sidebar-item";
import { sidebarVariants, sidebarItemVariants } from "@/lib/animation-variants";

export type FilterType = "all" | "active" | "completed";
export type CategoryType = "work" | "personal" | "health" | "shopping" | "other" | null;
export type PriorityType = "high" | "medium" | "low" | null;

export interface SidebarProps {
  isCollapsed: boolean;
  isMobile: boolean;
  isMobileOpen: boolean;
  currentFilter: FilterType;
  currentCategory: CategoryType;
  currentPriority: PriorityType;
  counts: {
    all: number;
    active: number;
    completed: number;
  };
  onToggle: () => void;
  onCloseMobile: () => void;
  onFilterChange: (filter: FilterType) => void;
  onCategoryChange: (category: CategoryType) => void;
  onPriorityChange: (priority: PriorityType) => void;
  onLogout: () => void;
}

/**
 * Sidebar - Main navigation sidebar with glass effect
 * T045, T048-T052, T058-T059: Full sidebar implementation
 */
export function Sidebar({
  isCollapsed,
  isMobile,
  isMobileOpen,
  currentFilter,
  currentCategory,
  currentPriority,
  counts,
  onToggle,
  onCloseMobile,
  onFilterChange,
  onCategoryChange,
  onPriorityChange,
  onLogout,
}: SidebarProps) {
  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* T048: Logo and branding - visible in both themes */}
      <div className="p-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg logo-box flex items-center justify-center flex-shrink-0">
            <span className="font-bold text-lg logo-text">L</span>
          </div>
          <AnimatePresence>
            {!isCollapsed && (
              <motion.div
                variants={sidebarItemVariants}
                initial="collapsed"
                animate="expanded"
                exit="collapsed"
              >
                <span className="text-xl font-bold text-foreground">
                  Lumina
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </Link>

        {/* Mobile close button */}
        {isMobile && (
          <button
            onClick={onCloseMobile}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        {/* Desktop collapse toggle - T058 */}
        {!isMobile && (
          <button
            onClick={onToggle}
            className="p-2 rounded-lg hover:bg-muted transition-colors"
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </button>
        )}
      </div>

      {/* Navigation sections */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        {/* T049: Filter items */}
        <div className="space-y-1">
          {!isCollapsed && (
            <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Tasks
            </p>
          )}
          <SidebarItem
            icon={ListTodo}
            label="All Tasks"
            isActive={currentFilter === "all" && !currentCategory && !currentPriority}
            isCollapsed={isCollapsed}
            count={counts.all}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(null);
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={Circle}
            label="Active"
            isActive={currentFilter === "active" && !currentCategory && !currentPriority}
            isCollapsed={isCollapsed}
            count={counts.active}
            onClick={() => {
              onFilterChange("active");
              onCategoryChange(null);
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={CheckCircle2}
            label="Completed"
            isActive={currentFilter === "completed" && !currentCategory && !currentPriority}
            isCollapsed={isCollapsed}
            count={counts.completed}
            onClick={() => {
              onFilterChange("completed");
              onCategoryChange(null);
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
        </div>

        {/* T050: Category filters */}
        <div className="space-y-1">
          {!isCollapsed && (
            <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Categories
            </p>
          )}
          <SidebarItem
            icon={Briefcase}
            label="Work"
            isActive={currentCategory === "work"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(currentCategory === "work" ? null : "work");
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={User}
            label="Personal"
            isActive={currentCategory === "personal"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(currentCategory === "personal" ? null : "personal");
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={Heart}
            label="Health"
            isActive={currentCategory === "health"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(currentCategory === "health" ? null : "health");
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={ShoppingCart}
            label="Shopping"
            isActive={currentCategory === "shopping"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(currentCategory === "shopping" ? null : "shopping");
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={MoreHorizontal}
            label="Other"
            isActive={currentCategory === "other"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(currentCategory === "other" ? null : "other");
              onPriorityChange(null);
              if (isMobile) onCloseMobile();
            }}
          />
        </div>

        {/* T051: Priority filters */}
        <div className="space-y-1">
          {!isCollapsed && (
            <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Priority
            </p>
          )}
          <SidebarItem
            icon={AlertTriangle}
            label="High"
            isActive={currentPriority === "high"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(null);
              onPriorityChange(currentPriority === "high" ? null : "high");
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={ArrowUp}
            label="Medium"
            isActive={currentPriority === "medium"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(null);
              onPriorityChange(currentPriority === "medium" ? null : "medium");
              if (isMobile) onCloseMobile();
            }}
          />
          <SidebarItem
            icon={ArrowDown}
            label="Low"
            isActive={currentPriority === "low"}
            isCollapsed={isCollapsed}
            onClick={() => {
              onFilterChange("all");
              onCategoryChange(null);
              onPriorityChange(currentPriority === "low" ? null : "low");
              if (isMobile) onCloseMobile();
            }}
          />
        </div>
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-border/50 space-y-1">
        <SidebarItem
          icon={LogOut}
          label="Logout"
          isCollapsed={isCollapsed}
          onClick={onLogout}
        />
      </div>
    </div>
  );

  // T059: Mobile drawer
  if (isMobile) {
    return (
      <AnimatePresence>
        {isMobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
            />

            {/* Drawer */}
            <motion.aside
              className="fixed inset-y-0 left-0 z-50 w-64 glass-sidebar"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    );
  }

  // Desktop sidebar
  return (
    <motion.aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 glass-sidebar hidden md:block",
        "border-r border-border/50"
      )}
      variants={sidebarVariants}
      initial={false}
      animate={isCollapsed ? "collapsed" : "expanded"}
    >
      {sidebarContent}
    </motion.aside>
  );
}
