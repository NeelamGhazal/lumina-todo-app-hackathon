"use client";

import { Suspense, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { toast } from "sonner";

import { LoginForm } from "@/components/auth/login-form";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { fadeUpVariants } from "@/lib/animation-variants";

/**
 * OAuth error messages mapped to user-friendly text
 * Per specs/010-oauth-social-login/tasks.md T015
 */
const OAUTH_ERROR_MESSAGES: Record<string, { title: string; description: string }> = {
  OAuthSignin: {
    title: "Sign in failed",
    description: "Could not start the sign in process. Please try again.",
  },
  OAuthCallback: {
    title: "Sign in failed",
    description: "Could not complete the sign in. Please try again.",
  },
  OAuthAccountNotLinked: {
    title: "Account not linked",
    description: "This email is already registered. Please sign in with your password.",
  },
  AccessDenied: {
    title: "Login cancelled",
    description: "You cancelled the sign in process.",
  },
  Default: {
    title: "Authentication error",
    description: "An error occurred during sign in. Please try again.",
  },
};

/**
 * Component to handle OAuth errors from URL params
 * Must be wrapped in Suspense for useSearchParams
 */
function OAuthErrorHandler() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const error = searchParams.get("error");
    if (error) {
      const errorInfo = OAUTH_ERROR_MESSAGES[error] ?? OAUTH_ERROR_MESSAGES.Default;
      toast.error(errorInfo?.title ?? "Authentication error", {
        description: errorInfo?.description ?? "An error occurred during sign in.",
      });
      // Clean up URL by removing error param
      const url = new URL(window.location.href);
      url.searchParams.delete("error");
      window.history.replaceState({}, "", url.toString());
    }
  }, [searchParams]);

  return null;
}

/**
 * Login page with Lumina glassmorphism design
 * T034, T043: Glass card wrapper with fade-in animation
 * T015: OAuth error handling via URL params
 */
export default function LoginPage() {
  const router = useRouter();

  function handleSuccess() {
    router.push("/tasks");
    router.refresh();
  }

  return (
    <>
      {/* OAuth error handler wrapped in Suspense for useSearchParams */}
      <Suspense fallback={null}>
        <OAuthErrorHandler />
      </Suspense>

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

          <div className="text-center mt-4">
            <Link
              href="/forgot-password"
              className="text-sm font-medium text-lumina-primary-400 hover:text-lumina-primary-300 underline-offset-4 hover:underline transition-colors"
            >
              Forgot your password?
            </Link>
          </div>

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
    </>
  );
}
