"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { Loader2 } from "lucide-react";
import { AnimatedButton } from "@/components/ui/animated-button";

/**
 * SocialLoginButtons - OAuth login button for GitHub
 * Per specs/010-oauth-social-login/tasks.md T012
 *
 * Note: Currently GitHub only. Google OAuth requires billing setup.
 *
 * Uses NextAuth.js v5 signIn for OAuth flow.
 * After OAuth success, backend JWT is stored and user redirects to /tasks.
 */
export function SocialLoginButtons() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGitHubLogin = async () => {
    setIsLoading(true);
    try {
      // NextAuth signIn will redirect to GitHub
      // After success, the callback will call our backend and redirect to /tasks
      await signIn("github", { callbackUrl: "/tasks" });
    } catch (error) {
      console.error("OAuth GitHub error:", error);
      setIsLoading(false);
    }
    // Note: setIsLoading won't be called after redirect
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-card px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <AnimatedButton
        variant="outline"
        type="button"
        onClick={handleGitHubLogin}
        className="w-full h-10"
        disabled={isLoading}
      >
        {isLoading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <GitHubIcon className="mr-2 h-4 w-4" />
        )}
        Continue with GitHub
      </AnimatedButton>
    </div>
  );
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path
        fillRule="evenodd"
        d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}
