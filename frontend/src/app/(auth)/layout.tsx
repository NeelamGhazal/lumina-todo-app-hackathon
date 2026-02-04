import type { Metadata } from "next";
import { AuthBrandPanel } from "@/components/auth/auth-brand-panel";

export const metadata: Metadata = {
  title: "Authentication - Lumina",
  description: "Sign in or create an account",
};

interface AuthLayoutProps {
  children: React.ReactNode;
}

/**
 * Auth route group layout
 * T031: Split design with brand panel (gradient) on left, form on right
 * Responsive: single column on mobile, split on desktop
 */
export default function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex">
      {/* T031: Left brand panel - hidden on mobile */}
      <AuthBrandPanel />

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center bg-background p-4 sm:p-8">
        <div className="w-full max-w-md">
          <main id="main-content">{children}</main>
        </div>
      </div>
    </div>
  );
}
