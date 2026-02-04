"use client";

import { motion } from "framer-motion";
import { pageTransitionVariants } from "@/lib/animation-variants";

/**
 * Template - Page transition wrapper
 * T087: Add page transition animations
 *
 * This template wraps all pages with a subtle fade animation.
 * Using transform/opacity only for smooth 60fps performance.
 */
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={pageTransitionVariants}
      initial="initial"
      animate="enter"
      exit="exit"
    >
      {children}
    </motion.div>
  );
}
