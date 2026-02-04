"use client";

import { motion } from "framer-motion";
import {
  LandingNav,
  HeroSection,
  FeaturesSection,
  CTASection,
  Footer,
} from "@/components/landing";
import { pageTransitionVariants } from "@/lib/animation-variants";

/**
 * Landing Page - Lumina home page with glassmorphism design
 * T027, T028: Assembled landing page with Framer Motion animations
 */
export default function Home() {
  return (
    <motion.div
      className="min-h-screen bg-background"
      initial="initial"
      animate="enter"
      exit="exit"
      variants={pageTransitionVariants}
    >
      {/* Navigation */}
      <LandingNav />

      {/* Main content with padding for fixed nav */}
      <main className="pt-20">
        {/* Hero Section */}
        <HeroSection />

        {/* Features Grid */}
        <FeaturesSection />

        {/* Final CTA */}
        <CTASection />
      </main>

      {/* Footer */}
      <Footer />
    </motion.div>
  );
}
