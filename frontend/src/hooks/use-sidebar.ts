"use client";

import { useCallback, useEffect, useState } from "react";

const SIDEBAR_STORAGE_KEY = "lumina-sidebar-collapsed";
const MOBILE_BREAKPOINT = 768;

export interface UseSidebarReturn {
  isCollapsed: boolean;
  isMobile: boolean;
  isMobileOpen: boolean;
  toggle: () => void;
  collapse: () => void;
  expand: () => void;
  toggleMobile: () => void;
  closeMobile: () => void;
}

/**
 * useSidebar - Hook for managing sidebar state
 * T016: Foundational hook for Lumina design system
 *
 * Features:
 * - Persists collapsed state to localStorage
 * - Handles mobile drawer state separately
 * - Responds to window resize
 */
export function useSidebar(): UseSidebarReturn {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Initialize from localStorage and detect mobile
  useEffect(() => {
    // Check if mobile
    const checkMobile = () => {
      const mobile = window.innerWidth < MOBILE_BREAKPOINT;
      setIsMobile(mobile);
      // Auto-close mobile drawer on resize to desktop
      if (!mobile) {
        setIsMobileOpen(false);
      }
    };

    // Load persisted state
    const stored = localStorage.getItem(SIDEBAR_STORAGE_KEY);
    if (stored !== null) {
      setIsCollapsed(stored === "true");
    }

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Persist collapsed state
  const persistState = useCallback((collapsed: boolean) => {
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(collapsed));
  }, []);

  const toggle = useCallback(() => {
    setIsCollapsed((prev) => {
      const next = !prev;
      persistState(next);
      return next;
    });
  }, [persistState]);

  const collapse = useCallback(() => {
    setIsCollapsed(true);
    persistState(true);
  }, [persistState]);

  const expand = useCallback(() => {
    setIsCollapsed(false);
    persistState(false);
  }, [persistState]);

  const toggleMobile = useCallback(() => {
    setIsMobileOpen((prev) => !prev);
  }, []);

  const closeMobile = useCallback(() => {
    setIsMobileOpen(false);
  }, []);

  return {
    isCollapsed,
    isMobile,
    isMobileOpen,
    toggle,
    collapse,
    expand,
    toggleMobile,
    closeMobile,
  };
}
