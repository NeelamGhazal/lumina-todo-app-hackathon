"use client";

import { forwardRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

export interface PasswordInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  showStrength?: boolean;
  value?: string;
}

/**
 * PasswordInput - Input with visibility toggle
 * T036, T041: Password visibility toggle for auth forms
 */
const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, showStrength = false, value, onChange, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);

    return (
      <div className="relative">
        <Input
          ref={ref}
          type={showPassword ? "text" : "password"}
          className={cn("pr-10", className)}
          value={value}
          onChange={onChange}
          {...props}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          aria-label={showPassword ? "Hide password" : "Show password"}
        >
          {showPassword ? (
            <EyeOff className="h-4 w-4" />
          ) : (
            <Eye className="h-4 w-4" />
          )}
        </button>
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";

/**
 * PasswordStrengthIndicator - Visual password strength meter
 * T042: Password strength indicator for signup
 */
export function PasswordStrengthIndicator({ password }: { password: string }) {
  const strength = calculateStrength(password);

  const strengthConfig = {
    0: { label: "Too weak", color: "bg-red-500", width: "w-0" },
    1: { label: "Weak", color: "bg-red-500", width: "w-1/4" },
    2: { label: "Fair", color: "bg-orange-500", width: "w-2/4" },
    3: { label: "Good", color: "bg-yellow-500", width: "w-3/4" },
    4: { label: "Strong", color: "bg-green-500", width: "w-full" },
  };

  const config = strengthConfig[strength as keyof typeof strengthConfig];

  if (!password) return null;

  return (
    <div className="space-y-1">
      <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            "h-full transition-all duration-300",
            config.color,
            config.width
          )}
        />
      </div>
      <p className="text-xs text-muted-foreground">
        Password strength: <span className="font-medium">{config.label}</span>
      </p>
    </div>
  );
}

function calculateStrength(password: string): number {
  if (!password) return 0;

  let strength = 0;

  // Length check
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;

  // Character variety
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
  if (/\d/.test(password)) strength++;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

  return Math.min(4, strength);
}

export { PasswordInput };
