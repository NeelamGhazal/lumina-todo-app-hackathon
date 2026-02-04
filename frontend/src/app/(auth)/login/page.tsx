"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

import { LoginForm } from "@/components/auth/login-form";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants } from "@/lib/animation-variants";

/**
 * Login page with Lumina glassmorphism design
 * T034, T043: Glass card wrapper with fade-in animation
 */
export default function LoginPage() {
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

      {/* T034: Glass card wrapper */}
      <GlassCard className="p-6 sm:p-8" blur="lg">
        <div className="space-y-2 mb-6">
          <h2 className="text-2xl font-bold">Welcome back</h2>
          <p className="text-muted-foreground">
            Enter your credentials to access your tasks
          </p>
        </div>

        <LoginForm onSuccess={handleSuccess} />

        <p className="text-sm text-muted-foreground text-center mt-6">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="font-medium text-lumina-primary-400 hover:text-lumina-primary-300 underline-offset-4 hover:underline transition-colors"
          >
            Sign up
          </Link>
        </p>
      </GlassCard>
    </motion.div>
  );
}
