/**
 * Animation Variants - Framer Motion animation presets
 * T015: Foundational animation system for Lumina design
 */

import type { Variants } from "framer-motion";

// ==========================================
// Fade Variants
// ==========================================

export const fadeInVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: "easeOut" },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.2, ease: "easeIn" },
  },
};

export const fadeUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] },
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: { duration: 0.2 },
  },
};

export const fadeDownVariants: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] },
  },
};

// ==========================================
// Scale Variants
// ==========================================

export const scaleInVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 },
  },
};

export const scaleUpVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: "spring", stiffness: 300, damping: 20 },
  },
};

// ==========================================
// Slide Variants
// ==========================================

export const slideInLeftVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: "easeOut" },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: { duration: 0.2 },
  },
};

export const slideInRightVariants: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.3, ease: "easeOut" },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: { duration: 0.2 },
  },
};

// ==========================================
// Container Variants (for stagger children)
// ==========================================

export const staggerContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const staggerFastContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.05,
    },
  },
};

// ==========================================
// Modal Variants
// ==========================================

export const modalOverlayVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.2 },
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.15, delay: 0.1 },
  },
};

export const modalContentVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 25,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
};

// ==========================================
// Sidebar Variants
// ==========================================

export const sidebarVariants: Variants = {
  collapsed: {
    width: "4.5rem",
    transition: { duration: 0.2, ease: "easeInOut" },
  },
  expanded: {
    width: "16rem",
    transition: { duration: 0.2, ease: "easeInOut" },
  },
};

export const sidebarItemVariants: Variants = {
  collapsed: {
    opacity: 0,
    width: 0,
    transition: { duration: 0.15 },
  },
  expanded: {
    opacity: 1,
    width: "auto",
    transition: { duration: 0.15, delay: 0.1 },
  },
};

// ==========================================
// Card / List Item Variants
// ==========================================

export const cardHoverVariants = {
  initial: { y: 0, boxShadow: "0 8px 32px rgba(0, 0, 0, 0.12)" },
  hover: {
    y: -4,
    boxShadow: "0 16px 48px rgba(0, 0, 0, 0.16)",
    transition: { duration: 0.2, ease: "easeOut" },
  },
};

export const listItemVariants: Variants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.2 },
  },
  exit: {
    opacity: 0,
    x: 10,
    transition: { duration: 0.15 },
  },
};

// ==========================================
// Page Transition Variants
// ==========================================

export const pageTransitionVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  enter: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: "easeOut" },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: { duration: 0.2, ease: "easeIn" },
  },
};

// ==========================================
// Utility - Reduced Motion Safe Transitions
// ==========================================

export const reducedMotionTransition = {
  duration: 0,
};

export const getTransition = (prefersReducedMotion: boolean) => {
  if (prefersReducedMotion) {
    return reducedMotionTransition;
  }
  return { duration: 0.3, ease: "easeOut" };
};
