"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants } from "@/lib/animation-variants";

/**
 * Forgot password page with Lumina glassmorphism design
 * Allows users to request a password reset email
 */
export default function ForgotPasswordPage() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUpVariants}
    >
      {/* Mobile branding - visible only on mobile */}
      <div className="lg:hidden text-center mb-8">
        <GradientText as="h1" variant="primary" className="text-3xl font-bold">
          Lumina
        </GradientText>
        <p className="text-muted-foreground mt-2">
          Illuminate Your Productivity
        </p>
      </div>

      {/* Glass card wrapper */}
      <GlassCard className="p-6 sm:p-8" blur="lg">
        <div className="space-y-2 mb-6">
          <h2 className="text-2xl font-bold">Forgot password?</h2>
          <p className="text-muted-foreground">
            Enter your email address and we&apos;ll send you a link to reset your password.
          </p>
        </div>

        <ForgotPasswordForm />

        <div className="mt-6">
          <Link
            href="/login"
            className="inline-flex items-center text-sm font-medium text-lumina-primary-400 hover:text-lumina-primary-300 transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to login
          </Link>
        </div>
      </GlassCard>
    </motion.div>
  );
}
