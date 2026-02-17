"use client";

import { useState, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Check, X } from "lucide-react";
import { toast } from "sonner";

import { AnimatedButton } from "@/components/ui/animated-button";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/auth/password-input";
import {
  resetPasswordSchema,
  checkPasswordRequirements,
  type ResetPasswordFormData,
} from "@/lib/validations";
import { api } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";
import { ERROR_CODES } from "@/types/api";

interface ResetPasswordFormProps {
  token: string;
  onSuccess?: () => void;
}

/**
 * Reset password form component
 * Allows users to set a new password with validation requirements
 */
export function ResetPasswordForm({ token, onSuccess }: ResetPasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    mode: "onChange",
  });

  const password = watch("password", "");

  // Check password requirements in real-time
  const requirements = useMemo(
    () => checkPasswordRequirements(password),
    [password]
  );

  async function onSubmit(data: ResetPasswordFormData) {
    setIsLoading(true);

    try {
      await api.auth.resetPassword({
        token,
        password: data.password,
        password_confirm: data.confirmPassword,
      });
      toast.success("Password reset successful!", {
        description: "You can now log in with your new password.",
      });
      onSuccess?.();
    } catch (error) {
      if (error instanceof ApiClientError) {
        switch (error.code) {
          case ERROR_CODES.INVALID_TOKEN:
            toast.error("Invalid reset link", {
              description: "Please request a new password reset.",
            });
            break;
          case ERROR_CODES.TOKEN_EXPIRED:
            toast.error("Reset link expired", {
              description: "Please request a new password reset.",
            });
            break;
          case ERROR_CODES.PASSWORD_MISMATCH:
            toast.error("Passwords do not match", {
              description: "Please ensure both passwords are the same.",
            });
            break;
          case ERROR_CODES.INVALID_PASSWORD:
            toast.error("Invalid password", {
              description: "Password does not meet requirements.",
            });
            break;
          default:
            toast.error("Reset failed", {
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
        <Label htmlFor="password">New password</Label>
        <PasswordInput
          id="password"
          placeholder="Enter new password"
          autoComplete="new-password"
          className="h-11"
          aria-describedby={errors.password ? "password-error" : "password-requirements"}
          aria-invalid={errors.password ? "true" : "false"}
          {...register("password")}
        />
        {errors.password && (
          <p id="password-error" className="text-sm text-destructive">
            {errors.password.message}
          </p>
        )}
      </div>

      {/* Password requirements checklist */}
      <div
        id="password-requirements"
        className="rounded-lg bg-muted/50 p-3 space-y-2"
      >
        <p className="text-xs font-medium text-muted-foreground">
          Password requirements:
        </p>
        <ul className="space-y-1">
          <RequirementItem
            met={requirements.minLength}
            text="At least 8 characters"
          />
          <RequirementItem
            met={requirements.hasUppercase}
            text="At least 1 uppercase letter"
          />
          <RequirementItem
            met={requirements.hasNumber}
            text="At least 1 number"
          />
        </ul>
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm new password</Label>
        <PasswordInput
          id="confirmPassword"
          placeholder="Confirm new password"
          autoComplete="new-password"
          className="h-11"
          aria-describedby={errors.confirmPassword ? "confirm-error" : undefined}
          aria-invalid={errors.confirmPassword ? "true" : "false"}
          {...register("confirmPassword")}
        />
        {errors.confirmPassword && (
          <p id="confirm-error" className="text-sm text-destructive">
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
            Resetting password...
          </>
        ) : (
          "Reset password"
        )}
      </AnimatedButton>
    </form>
  );
}

/**
 * Password requirement indicator item
 */
function RequirementItem({ met, text }: { met: boolean; text: string }) {
  return (
    <li className="flex items-center gap-2 text-xs">
      {met ? (
        <Check className="h-3.5 w-3.5 text-green-500" />
      ) : (
        <X className="h-3.5 w-3.5 text-muted-foreground" />
      )}
      <span className={met ? "text-green-600 dark:text-green-400" : "text-muted-foreground"}>
        {text}
      </span>
    </li>
  );
}
