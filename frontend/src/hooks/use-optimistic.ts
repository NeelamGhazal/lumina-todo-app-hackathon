"use client";

import { useState, useCallback, useRef } from "react";

interface OptimisticState<T> {
  data: T;
  isLoading: boolean;
  error: string | null;
}

interface OptimisticOptions<T> {
  /** Initial data value */
  initialData: T;
  /** Called when mutation succeeds */
  onSuccess?: (data: T) => void;
  /** Called when mutation fails */
  onError?: (error: Error, rollbackData: T) => void;
}

interface UseOptimisticReturn<T> {
  data: T;
  isLoading: boolean;
  error: string | null;
  /** Execute optimistic mutation */
  mutate: <R>(
    optimisticData: T,
    mutationFn: () => Promise<R>,
    options?: {
      onSuccess?: (result: R) => T;
      rollbackDelay?: number;
    }
  ) => Promise<R | undefined>;
  /** Reset to initial state */
  reset: () => void;
  /** Manually set data */
  setData: (data: T) => void;
}

/**
 * Generic hook for optimistic UI updates
 * Per spec FR-027, FR-034, FR-043, FR-054: Optimistic UI updates with rollback
 *
 * @example
 * ```tsx
 * const { data, mutate } = useOptimistic({ initialData: [] });
 *
 * const addItem = async (newItem) => {
 *   await mutate(
 *     [...data, { ...newItem, _optimistic: true }],
 *     () => api.createItem(newItem),
 *     { onSuccess: (result) => [...data, result.item] }
 *   );
 * };
 * ```
 */
export function useOptimistic<T>({
  initialData,
  onSuccess,
  onError,
}: OptimisticOptions<T>): UseOptimisticReturn<T> {
  const [state, setState] = useState<OptimisticState<T>>({
    data: initialData,
    isLoading: false,
    error: null,
  });

  // Keep track of the previous data for rollback
  const previousDataRef = useRef<T>(initialData);

  const setData = useCallback((data: T) => {
    setState((prev) => ({ ...prev, data }));
  }, []);

  const reset = useCallback(() => {
    setState({
      data: initialData,
      isLoading: false,
      error: null,
    });
    previousDataRef.current = initialData;
  }, [initialData]);

  const mutate = useCallback(
    async <R>(
      optimisticData: T,
      mutationFn: () => Promise<R>,
      options?: {
        onSuccess?: (result: R) => T;
        rollbackDelay?: number;
      }
    ): Promise<R | undefined> => {
      // Store previous data for potential rollback
      previousDataRef.current = state.data;

      // Apply optimistic update immediately
      setState((prev) => ({
        ...prev,
        data: optimisticData,
        isLoading: true,
        error: null,
      }));

      try {
        // Execute the actual mutation
        const result = await mutationFn();

        // Get final data (either from onSuccess transform or keep optimistic)
        const finalData = options?.onSuccess
          ? options.onSuccess(result)
          : optimisticData;

        setState((prev) => ({
          ...prev,
          data: finalData,
          isLoading: false,
        }));

        onSuccess?.(finalData);
        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "An error occurred";

        // Rollback to previous data
        const rollbackData = previousDataRef.current;

        if (options?.rollbackDelay) {
          // Delayed rollback (useful for undo operations)
          setTimeout(() => {
            setState((prev) => ({
              ...prev,
              data: rollbackData,
              isLoading: false,
              error: errorMessage,
            }));
          }, options.rollbackDelay);
        } else {
          // Immediate rollback
          setState((prev) => ({
            ...prev,
            data: rollbackData,
            isLoading: false,
            error: errorMessage,
          }));
        }

        onError?.(error instanceof Error ? error : new Error(errorMessage), rollbackData);
        return undefined;
      }
    },
    [state.data, onSuccess, onError]
  );

  return {
    data: state.data,
    isLoading: state.isLoading,
    error: state.error,
    mutate,
    reset,
    setData,
  };
}

/**
 * Helper type for optimistic items with tracking flag
 */
export interface OptimisticItem {
  _optimistic?: boolean;
  _previousState?: unknown;
}

/**
 * Generate a temporary ID for optimistic items
 */
export function generateOptimisticId(): string {
  return `optimistic-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
