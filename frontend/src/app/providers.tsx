"use client";

import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";
import { OAuthSessionSync } from "@/components/auth/oauth-session-sync";

interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Root providers for the application
 * - SessionProvider: NextAuth.js v5 session management for OAuth
 * - OAuthSessionSync: Syncs OAuth session token to existing cookie storage
 * - ThemeProvider: Dark/light mode with system preference
 * - Toaster: Toast notifications (top-center per spec)
 */
export function Providers({ children }: ProvidersProps) {
  return (
    <SessionProvider>
      <OAuthSessionSync />
      <ThemeProvider
        attribute={["class", "data-theme"]}
        defaultTheme="dark"
        enableSystem={false}
        disableTransitionOnChange={false}
      >
        {children}
        <Toaster
          position="top-center"
          expand={false}
          richColors
          closeButton
          duration={4000}
        />
      </ThemeProvider>
    </SessionProvider>
  );
}
