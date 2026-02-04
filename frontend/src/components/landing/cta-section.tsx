"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedButton } from "@/components/ui/animated-button";
import { FloatingOrbs } from "@/components/ui/floating-orbs";
import { fadeUpVariants, staggerContainerVariants } from "@/lib/animation-variants";

/**
 * CTASection - Final call-to-action section with glass card
 * T020: CTA section with gradient styling
 */
export function CTASection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Subtle background orbs */}
      <FloatingOrbs variant="subtle" />

      <div className="max-w-4xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={staggerContainerVariants}
        >
          <GlassCard className="p-8 sm:p-12 text-center relative overflow-hidden">
            {/* Gradient border effect */}
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-lumina-primary-500/20 via-transparent to-lumina-primary-300/20 pointer-events-none" />

            <motion.h2
              variants={fadeUpVariants}
              className="text-3xl sm:text-4xl font-bold mb-4"
            >
              Ready to{" "}
              <GradientText variant="primary">illuminate</GradientText> your
              productivity?
            </motion.h2>

            <motion.p
              variants={fadeUpVariants}
              className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto"
            >
              Join thousands of users who have transformed the way they manage
              tasks. Start your journey today.
            </motion.p>

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
                  Start for Free
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </AnimatedButton>

              <AnimatedButton
                variant="ghost"
                size="lg"
                asChild
              >
                <Link href="/login">Already have an account?</Link>
              </AnimatedButton>
            </motion.div>
          </GlassCard>
        </motion.div>
      </div>
    </section>
  );
}
