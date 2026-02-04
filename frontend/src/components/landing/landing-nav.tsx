"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedButton } from "@/components/ui/animated-button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { fadeUpVariants } from "@/lib/animation-variants";

/**
 * LandingNav - Landing page navigation with logo and auth buttons
 * T022: Navigation component
 */
export function LandingNav() {
  return (
    <motion.header
      className="fixed top-0 left-0 right-0 z-50"
      initial="hidden"
      animate="visible"
      variants={fadeUpVariants}
    >
      <nav className="glass-sidebar mx-4 mt-4 rounded-2xl px-4 sm:px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          {/* Logo - visible in both themes */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg logo-box flex items-center justify-center">
              <span className="font-bold text-lg logo-text">L</span>
            </div>
            <span className="text-xl font-bold hidden sm:inline text-foreground">
              Lumina
            </span>
          </Link>

          {/* Right side: Theme toggle and auth buttons */}
          <div className="flex items-center gap-3">
            <ThemeToggle size="sm" />

            <AnimatedButton
              variant="ghost"
              size="sm"
              asChild
            >
              <Link href="/login">Sign In</Link>
            </AnimatedButton>

            <AnimatedButton
              variant="gradient"
              size="sm"
              asChild
            >
              <Link href="/signup">Get Started</Link>
            </AnimatedButton>
          </div>
        </div>
      </nav>
    </motion.header>
  );
}
