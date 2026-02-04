"use client";

import { useEffect, useState } from "react";

export interface AnimationConfig {
  /** Whether user prefers reduced motion */
  prefersReducedMotion: boolean;
  /** Duration multiplier (0 for reduced motion, 1 otherwise) */
  durationMultiplier: number;
  /** Spring stiffness for Framer Motion */
  springStiffness: number;
  /** Spring damping for Framer Motion */
  springDamping: number;
  /** Default transition for simple animations */
  defaultTransition: {
    duration: number;
    ease: string | number[];
  };
  /** Spring transition for bouncy animations */
  springTransition: {
    type: "spring";
    stiffness: number;
    damping: number;
  };
}

const REDUCED_MOTION_CONFIG: AnimationConfig = {
  prefersReducedMotion: true,
  durationMultiplier: 0,
  springStiffness: 1000,
  springDamping: 1000,
  defaultTransition: {
    duration: 0,
    ease: "linear",
  },
  springTransition: {
    type: "spring",
    stiffness: 1000,
    damping: 1000,
  },
};

const FULL_MOTION_CONFIG: AnimationConfig = {
  prefersReducedMotion: false,
  durationMultiplier: 1,
  springStiffness: 300,
  springDamping: 25,
  defaultTransition: {
    duration: 0.3,
    ease: [0.4, 0, 0.2, 1],
  },
  springTransition: {
    type: "spring",
    stiffness: 300,
    damping: 25,
  },
};

/**
 * useAnimationConfig - Hook for respecting reduced motion preferences
 * T017: Foundational hook for Lumina accessibility
 *
 * Returns animation configuration that respects prefers-reduced-motion.
 * Use this to conditionally apply animations based on user preference.
 *
 * @example
 * ```tsx
 * const { prefersReducedMotion, springTransition } = useAnimationConfig();
 *
 * <motion.div
 *   animate={{ scale: 1 }}
 *   transition={springTransition}
 * />
 * ```
 */
export function useAnimationConfig(): AnimationConfig {
  const [config, setConfig] = useState<AnimationConfig>(FULL_MOTION_CONFIG);

  useEffect(() => {
    // Check initial preference
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

    const updateConfig = (matches: boolean) => {
      setConfig(matches ? REDUCED_MOTION_CONFIG : FULL_MOTION_CONFIG);
    };

    // Set initial value
    updateConfig(mediaQuery.matches);

    // Listen for changes
    const handler = (event: MediaQueryListEvent) => {
      updateConfig(event.matches);
    };

    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  return config;
}

/**
 * Utility function to get duration based on reduced motion preference
 */
export function getAnimationDuration(
  baseDuration: number,
  prefersReducedMotion: boolean
): number {
  return prefersReducedMotion ? 0 : baseDuration;
}
