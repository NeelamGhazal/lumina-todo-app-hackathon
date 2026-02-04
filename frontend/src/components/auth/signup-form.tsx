"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { AnimatedButton } from "@/components/ui/animated-button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput, PasswordStrengthIndicator } from "@/components/auth/password-input";
import { SocialLoginButtons } from "@/components/auth/social-login-buttons";
import { signupSchema, type SignupFormData } from "@/lib/validations";
import { api } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";
import { ERROR_CODES } from "@/types/api";

interface SignupFormProps {
  onSuccess?: () => void;
}

/**
 * Signup form component with Lumina styling
 * T040-T042: Styled inputs, password toggle, strength indicator
 */
export function SignupForm({ onSuccess }: SignupFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    mode: "onBlur",
  });

  const passwordValue = watch("password", "");

  async function onSubmit(data: SignupFormData) {
    setIsLoading(true);

    try {
      await api.auth.register({
        email: data.email,
        password: data.password,
        name: data.name,
      });
      toast.success("Account created!", {
        description: "Welcome to Lumina.",
      });
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        if (error.code === ERROR_CODES.EMAIL_ALREADY_EXISTS) {
          toast.error("Email already exists", {
            description: "Please use a different email or sign in.",
          });
        } else if (error.isValidationError()) {
          toast.error("Validation error", {
            description: error.message,
          });
        } else {
          toast.error("Registration failed", {
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

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Name (optional)</Label>
        <Input
          id="name"
          type="text"
          placeholder="Your name"
          autoComplete="name"
          className="h-11"
          {...register("name")}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          className="h-11"
          aria-describedby={errors.email ? "email-error" : undefined}
          aria-invalid={errors.email ? "true" : "false"}
          {...register("email")}
        />
        {errors.email && (
          <p id="email-error" className="text-sm text-destructive">
            {errors.email.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        {/* T041: Password visibility toggle */}
        <PasswordInput
          id="password"
          placeholder="••••••••"
          autoComplete="new-password"
          className="h-11"
          aria-describedby={errors.password ? "password-error" : undefined}
          aria-invalid={errors.password ? "true" : "false"}
          {...register("password")}
        />
        {/* T042: Password strength indicator */}
        <PasswordStrengthIndicator password={passwordValue} />
        {errors.password && (
          <p id="password-error" className="text-sm text-destructive">
            {errors.password.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm Password</Label>
        <PasswordInput
          id="confirmPassword"
          placeholder="••••••••"
          autoComplete="new-password"
          className="h-11"
          aria-describedby={
            errors.confirmPassword ? "confirm-password-error" : undefined
          }
          aria-invalid={errors.confirmPassword ? "true" : "false"}
          {...register("confirmPassword")}
        />
        {errors.confirmPassword && (
          <p id="confirm-password-error" className="text-sm text-destructive">
            {errors.confirmPassword.message}
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
            Creating account...
          </>
        ) : (
          "Create account"
        )}
      </AnimatedButton>

      <SocialLoginButtons />
    </form>
  );
}
