"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import type { FilterType, CategoryType, PriorityType } from "@/components/layout/sidebar";

interface TaskCounts {
  all: number;
  active: number;
  completed: number;
}

interface FilterContextValue {
  filter: FilterType;
  category: CategoryType;
  priority: PriorityType;
  counts: TaskCounts;
  setFilter: (filter: FilterType) => void;
  setCategory: (category: CategoryType) => void;
  setPriority: (priority: PriorityType) => void;
  setCounts: (counts: TaskCounts) => void;
  resetFilters: () => void;
}

const FilterContext = createContext<FilterContextValue | null>(null);

interface FilterProviderProps {
  children: ReactNode;
}

/**
 * FilterProvider - Provides filter state to dashboard components
 * Shares filter state between sidebar and tasks page
 */
export function FilterProvider({ children }: FilterProviderProps) {
  const [filter, setFilterState] = useState<FilterType>("all");
  const [category, setCategoryState] = useState<CategoryType>(null);
  const [priority, setPriorityState] = useState<PriorityType>(null);
  const [counts, setCountsState] = useState<TaskCounts>({ all: 0, active: 0, completed: 0 });

  const setFilter = useCallback((newFilter: FilterType) => {
    setFilterState(newFilter);
  }, []);

  const setCategory = useCallback((newCategory: CategoryType) => {
    setCategoryState(newCategory);
  }, []);

  const setPriority = useCallback((newPriority: PriorityType) => {
    setPriorityState(newPriority);
  }, []);

  const setCounts = useCallback((newCounts: TaskCounts) => {
    setCountsState(newCounts);
  }, []);

  const resetFilters = useCallback(() => {
    setFilterState("all");
    setCategoryState(null);
    setPriorityState(null);
  }, []);

  return (
    <FilterContext.Provider
      value={{
        filter,
        category,
        priority,
        counts,
        setFilter,
        setCategory,
        setPriority,
        setCounts,
        resetFilters,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

/**
 * useFilter - Hook to access filter state
 * Must be used within FilterProvider
 */
export function useFilter(): FilterContextValue {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useFilter must be used within a FilterProvider");
  }
  return context;
}
