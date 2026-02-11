"use client";

import { ThemeProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";

interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Root providers for the application
 * - ThemeProvider: Dark/light mode with system preference
 * - Toaster: Toast notifications (top-center per spec)
 */
export function Providers({ children }: ProvidersProps) {
  return (
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
  );
}
