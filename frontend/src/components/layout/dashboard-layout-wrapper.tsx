"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { useSidebar } from "@/hooks/use-sidebar";
import { useFilter, FilterProvider } from "@/contexts/filter-context";
import { Sidebar, type FilterType, type CategoryType, type PriorityType } from "./sidebar";
import { DashboardHeader } from "./dashboard-header";

interface DashboardLayoutWrapperProps {
  children: React.ReactNode;
}

/**
 * Inner component that uses the filter context
 */
function DashboardLayoutInner({ children }: DashboardLayoutWrapperProps) {
  const router = useRouter();
  const { user, logout } = useAuth();
  const {
    isCollapsed,
    isMobile,
    isMobileOpen,
    toggle,
    toggleMobile,
    closeMobile,
  } = useSidebar();

  // Get filter state and counts from context
  const {
    filter: currentFilter,
    category: currentCategory,
    priority: currentPriority,
    counts: taskCounts,
    setFilter,
    setCategory,
    setPriority,
  } = useFilter();

  const handleLogout = useCallback(async () => {
    await logout();
    router.push("/login");
  }, [logout, router]);

  const handleFilterChange = useCallback((filter: FilterType) => {
    setFilter(filter);
  }, [setFilter]);

  const handleCategoryChange = useCallback((category: CategoryType) => {
    setCategory(category);
  }, [setCategory]);

  const handlePriorityChange = useCallback((priority: PriorityType) => {
    setPriority(priority);
  }, [setPriority]);

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        isMobile={isMobile}
        isMobileOpen={isMobileOpen}
        currentFilter={currentFilter}
        currentCategory={currentCategory}
        currentPriority={currentPriority}
        counts={taskCounts}
        onToggle={toggle}
        onCloseMobile={closeMobile}
        onFilterChange={handleFilterChange}
        onCategoryChange={handleCategoryChange}
        onPriorityChange={handlePriorityChange}
        onLogout={handleLogout}
      />

      {/* Main content area - offset by sidebar width */}
      <div
        className={cn(
          "flex flex-col min-h-screen transition-all duration-200",
          !isMobile && (isCollapsed ? "md:pl-[4.5rem]" : "md:pl-64")
        )}
      >
        {/* Header */}
        <DashboardHeader
          userName={user?.name}
          userEmail={user?.email || ""}
          isSidebarCollapsed={isCollapsed}
          onMenuClick={toggleMobile}
          onLogout={handleLogout}
        />

        {/* Main content */}
        <main
          id="main-content"
          className="flex-1 p-4 md:p-6 lg:p-8"
        >
          {children}
        </main>
      </div>
    </div>
  );
}

/**
 * DashboardLayoutWrapper - Client-side wrapper for dashboard with sidebar
 * T057: Dashboard layout with sidebar navigation
 * Wraps children in FilterProvider for shared filter state
 */
export function DashboardLayoutWrapper({ children }: DashboardLayoutWrapperProps) {
  return (
    <FilterProvider>
      <DashboardLayoutInner>{children}</DashboardLayoutInner>
    </FilterProvider>
  );
}
