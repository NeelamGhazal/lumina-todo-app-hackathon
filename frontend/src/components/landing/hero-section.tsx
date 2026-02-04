"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedButton } from "@/components/ui/animated-button";
import { FloatingOrbs } from "@/components/ui/floating-orbs";
import { fadeUpVariants, staggerContainerVariants } from "@/lib/animation-variants";

/**
 * HeroSection - Landing page hero with glassmorphism and animations
 * T018, T023, T024, T025: Hero section with gradient text, orbs, and styled CTAs
 */
export function HeroSection() {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
      {/* T024: Floating orbs background */}
      <FloatingOrbs variant="hero" />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background pointer-events-none" />

      <motion.div
        className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center"
        variants={staggerContainerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Badge */}
        <motion.div variants={fadeUpVariants} className="mb-6">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-lumina-primary-500/10 border border-lumina-primary-500/20 text-sm font-medium text-lumina-primary-400">
            <Sparkles className="w-4 h-4" />
            Illuminate Your Productivity
          </span>
        </motion.div>

        {/* T023: Main headline with gradient text */}
        <motion.h1
          variants={fadeUpVariants}
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6"
        >
          <span className="block text-foreground">Organize Your Life with</span>
          <GradientText as="span" variant="primary" className="block mt-2">
            Lumina
          </GradientText>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          variants={fadeUpVariants}
          className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
        >
          A beautiful, modern task management app that helps you stay focused
          and accomplish more. Experience the future of productivity.
        </motion.p>

        {/* T025: CTA Buttons with gradient and hover effects */}
        <motion.div
          variants={fadeUpVariants}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <AnimatedButton
            variant="gradient"
            size="xl"
            asChild
          >
            <Link href="/signup" className="group">
              Get Started Free
              <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
            </Link>
          </AnimatedButton>

          <AnimatedButton
            variant="outline"
            size="xl"
            asChild
          >
            <Link href="/login">
              Sign In
            </Link>
          </AnimatedButton>
        </motion.div>

        {/* Trust indicators */}
        <motion.p
          variants={fadeUpVariants}
          className="mt-8 text-sm text-muted-foreground"
        >
          Free forever • No credit card required • Get started in seconds
        </motion.p>
      </motion.div>
    </section>
  );
}
