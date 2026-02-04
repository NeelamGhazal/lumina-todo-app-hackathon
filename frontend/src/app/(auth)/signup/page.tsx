"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

import { SignupForm } from "@/components/auth/signup-form";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants } from "@/lib/animation-variants";

/**
 * Signup page with Lumina glassmorphism design
 * T039, T043: Glass card wrapper with fade-in animation
 */
export default function SignupPage() {
  const router = useRouter();

  function handleSuccess() {
    router.push("/tasks");
    router.refresh();
  }

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

      {/* T039: Glass card wrapper */}
      <GlassCard className="p-6 sm:p-8" blur="lg">
        <div className="space-y-2 mb-6">
          <h2 className="text-2xl font-bold">Create an account</h2>
          <p className="text-muted-foreground">
            Enter your details to get started with Lumina
          </p>
        </div>

        <SignupForm onSuccess={handleSuccess} />

        <p className="text-sm text-muted-foreground text-center mt-6">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-lumina-primary-400 hover:text-lumina-primary-300 underline-offset-4 hover:underline transition-colors"
          >
            Sign in
          </Link>
        </p>
      </GlassCard>
    </motion.div>
  );
}
