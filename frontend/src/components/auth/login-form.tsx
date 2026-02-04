"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { AnimatedButton } from "@/components/ui/animated-button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/auth/password-input";
import { SocialLoginButtons } from "@/components/auth/social-login-buttons";
import { loginSchema, type LoginFormData } from "@/lib/validations";
import { api } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";

interface LoginFormProps {
  onSuccess?: () => void;
}

/**
 * Login form component with Lumina styling
 * T035-T038: Styled inputs, password toggle, social buttons
 */
export function LoginForm({ onSuccess }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: "onBlur",
  });

  async function onSubmit(data: LoginFormData) {
    setIsLoading(true);

    try {
      await api.auth.login(data);
      toast.success("Welcome back!", {
        description: "You have been logged in successfully.",
      });
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        if (error.isAuthError()) {
          toast.error("Invalid credentials", {
            description: "Please check your email and password.",
          });
        } else {
          toast.error("Login failed", {
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
        {/* T036: Password visibility toggle */}
        <PasswordInput
          id="password"
          placeholder="••••••••"
          autoComplete="current-password"
          className="h-11"
          aria-describedby={errors.password ? "password-error" : undefined}
          aria-invalid={errors.password ? "true" : "false"}
          {...register("password")}
        />
        {errors.password && (
          <p id="password-error" className="text-sm text-destructive">
            {errors.password.message}
          </p>
        )}
      </div>

      {/* T037: Submit button with loading state */}
      <AnimatedButton
        type="submit"
        variant="gradient"
        className="w-full h-11"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Signing in...
          </>
        ) : (
          "Sign in"
        )}
      </AnimatedButton>

      {/* T038: Social login buttons */}
      <SocialLoginButtons />
    </form>
  );
}
