"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Mail, CheckCircle } from "lucide-react";
import { toast } from "sonner";

import { AnimatedButton } from "@/components/ui/animated-button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { forgotPasswordSchema, type ForgotPasswordFormData } from "@/lib/validations";
import { api } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";
import { ERROR_CODES } from "@/types/api";

interface ForgotPasswordFormProps {
  onSuccess?: () => void;
}

/**
 * Forgot password form component
 * Requests password reset email for the given address
 */
export function ForgotPasswordForm({ onSuccess }: ForgotPasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    mode: "onBlur",
  });

  async function onSubmit(data: ForgotPasswordFormData) {
    setIsLoading(true);

    try {
      await api.auth.forgotPassword(data);
      setSubmittedEmail(data.email);
      setIsSubmitted(true);
      toast.success("Check your email", {
        description: "If an account exists, you will receive a reset link shortly.",
      });
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        if (error.code === ERROR_CODES.RATE_LIMIT_EXCEEDED) {
          toast.error("Too many requests", {
            description: "Please wait before requesting another reset link.",
          });
        } else {
          toast.error("Request failed", {
            description: error.message,
          });
        }
      } else {
        toast.error("Something went wrong", {
          description: "Please try again later.",
        });
      }
    } finally {
      setIsLoading(false);
    }
  }

  // Show success state after submission
  if (isSubmitted) {
    return (
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="rounded-full bg-green-100 dark:bg-green-900/30 p-3">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">Check your email</h3>
          <p className="text-sm text-muted-foreground">
            If an account exists for <span className="font-medium">{submittedEmail}</span>,
            you will receive a password reset link shortly.
          </p>
        </div>
        <p className="text-xs text-muted-foreground">
          The link will expire in 15 minutes.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email address</Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            className="h-11 pl-10"
            aria-describedby={errors.email ? "email-error" : undefined}
            aria-invalid={errors.email ? "true" : "false"}
            {...register("email")}
          />
        </div>
        {errors.email && (
          <p id="email-error" className="text-sm text-destructive">
            {errors.email.message}
          </p>
        )}
      </div>

      <AnimatedButton
        type="submit"
        variant="gradient"
        className="w-full h-11"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Sending...
          </>
        ) : (
          "Send reset link"
        )}
      </AnimatedButton>
    </form>
  );
}
