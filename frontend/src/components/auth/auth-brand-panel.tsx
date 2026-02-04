"use client";

import { motion } from "framer-motion";
import { GradientText } from "@/components/ui/gradient-text";
import { FloatingOrbs } from "@/components/ui/floating-orbs";
import { fadeUpVariants, staggerContainerVariants } from "@/lib/animation-variants";

/**
 * AuthBrandPanel - Left side branding panel for auth pages
 * T032, T033: Brand panel with floating orbs
 */
export function AuthBrandPanel() {
  return (
    <div className="hidden lg:flex lg:flex-1 relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* T033: Floating orbs background */}
      <FloatingOrbs variant="auth" />

      {/* Content */}
      <motion.div
        className="relative z-10 flex flex-col justify-center px-12 xl:px-16"
        variants={staggerContainerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={fadeUpVariants}>
          <GradientText
            as="h1"
            variant="primary"
            className="text-4xl xl:text-5xl font-bold mb-4"
          >
            Lumina
          </GradientText>
        </motion.div>

        <motion.p
          variants={fadeUpVariants}
          className="text-xl text-slate-300 mb-8"
        >
          Illuminate Your Productivity
        </motion.p>

        <motion.div variants={fadeUpVariants} className="space-y-4">
          <FeatureItem
            emoji="✨"
            text="Beautiful, modern task management"
          />
          <FeatureItem
            emoji="🚀"
            text="Lightning fast and responsive"
          />
          <FeatureItem
            emoji="🌙"
            text="Stunning dark mode experience"
          />
          <FeatureItem
            emoji="📱"
            text="Works on any device"
          />
        </motion.div>
      </motion.div>

      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/50 to-transparent pointer-events-none" />
    </div>
  );
}

function FeatureItem({ emoji, text }: { emoji: string; text: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xl">{emoji}</span>
      <span className="text-slate-300">{text}</span>
    </div>
  );
}
