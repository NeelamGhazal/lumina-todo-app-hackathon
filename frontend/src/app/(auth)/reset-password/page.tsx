"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react";
import { toast } from "sonner";

import { ResetPasswordForm } from "@/components/auth/reset-password-form";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { AnimatedButton } from "@/components/ui/animated-button";
import { fadeUpVariants } from "@/lib/animation-variants";
import { api } from "@/lib/api/endpoints";

type PageState = "loading" | "valid" | "invalid" | "expired";

/**
 * Reset password page wrapper with Suspense boundary
 */
export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<ResetPasswordLoading />}>
      <ResetPasswordContent />
    </Suspense>
  );
}

/**
 * Loading fallback component
 */
function ResetPasswordLoading() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeUpVariants}
    >
      <div className="lg:hidden text-center mb-8">
        <GradientText as="h1" variant="primary" className="text-3xl font-bold">
          Lumina
        </GradientText>
        <p className="text-muted-foreground mt-2">
          Illuminate Your Productivity
        </p>
      </div>
      <GlassCard className="p-6 sm:p-8" blur="lg">
        <div className="flex flex-col items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-lumina-primary-400" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </GlassCard>
    </motion.div>
  );
}

/**
 * Reset password page content
 * Validates token from URL and allows password reset
 */
function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [pageState, setPageState] = useState<PageState>("loading");
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>("");

  // Verify token on mount
  useEffect(() => {
    async function verifyToken() {
      if (!token) {
        setPageState("invalid");
        setErrorMessage("No reset token provided");
        return;
      }

      try {
        const response = await api.auth.verifyResetToken(token);

        if (response.valid) {
          setPageState("valid");
          setUserEmail(response.email);
        } else {
          // Check if expired or invalid
          if (response.error?.toLowerCase().includes("expired")) {
            setPageState("expired");
            setErrorMessage(response.error || "This reset link has expired");
          } else {
            setPageState("invalid");
            setErrorMessage(response.error || "Invalid reset link");
          }
        }
      } catch (error) {
        setPageState("invalid");
        setErrorMessage("Failed to verify reset link");
      }
    }

    verifyToken();
  }, [token]);

  // Handle successful password reset
  function handleSuccess() {
    toast.success("Password reset successful!", {
      description: "Redirecting to login...",
    });
    // Redirect to login after short delay
    setTimeout(() => {
      router.push("/login");
    }, 1500);
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

      {/* Glass card wrapper */}
      <GlassCard className="p-6 sm:p-8" blur="lg">
        {/* Loading state */}
        {pageState === "loading" && (
          <div className="flex flex-col items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-lumina-primary-400" />
            <p className="mt-4 text-muted-foreground">Verifying reset link...</p>
          </div>
        )}

        {/* Valid token - show form */}
        {pageState === "valid" && token && (
          <>
            <div className="space-y-2 mb-6">
              <h2 className="text-2xl font-bold">Reset your password</h2>
              <p className="text-muted-foreground">
                {userEmail ? (
                  <>Enter a new password for <span className="font-medium">{userEmail}</span></>
                ) : (
                  "Enter your new password below"
                )}
              </p>
            </div>

            <ResetPasswordForm token={token} onSuccess={handleSuccess} />
          </>
        )}

        {/* Invalid token */}
        {pageState === "invalid" && (
          <ErrorState
            title="Invalid reset link"
            message={errorMessage}
            showRequestNew
          />
        )}

        {/* Expired token */}
        {pageState === "expired" && (
          <ErrorState
            title="Reset link expired"
            message={errorMessage}
            showRequestNew
          />
        )}
      </GlassCard>
    </motion.div>
  );
}

/**
 * Error state component for invalid/expired tokens
 */
function ErrorState({
  title,
  message,
  showRequestNew,
}: {
  title: string;
  message: string;
  showRequestNew?: boolean;
}) {
  return (
    <div className="text-center space-y-4">
      <div className="flex justify-center">
        <div className="rounded-full bg-destructive/10 p-3">
          <AlertCircle className="h-8 w-8 text-destructive" />
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      {showRequestNew && (
        <div className="pt-4 space-y-3">
          <Link href="/forgot-password">
            <AnimatedButton variant="gradient" className="w-full">
              Request new reset link
            </AnimatedButton>
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center justify-center w-full text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to login
          </Link>
        </div>
      )}
    </div>
  );
}
