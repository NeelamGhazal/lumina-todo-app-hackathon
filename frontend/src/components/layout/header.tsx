"use client";

import Link from "next/link";
import { CheckSquare } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { LogoutModal } from "@/components/auth/logout-modal";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Header component with navigation and theme toggle
 * Per spec: Header with theme toggle and auth state display
 */
export function Header() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between px-4 md:px-6">
        {/* Logo */}
        <Link
          href={isAuthenticated ? "/tasks" : "/"}
          className="flex items-center space-x-2"
        >
          <CheckSquare className="h-6 w-6" />
          <span className="font-bold hidden sm:inline-block">
            Evolution Todo
          </span>
        </Link>

        {/* Right side: Theme toggle + Auth */}
        <div className="flex items-center space-x-2">
          <ThemeToggle />

          {isLoading ? (
            <Skeleton className="h-9 w-20" />
          ) : isAuthenticated && user ? (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground hidden md:inline-block">
                {user.email}
              </span>
              <LogoutModal onConfirm={logout} />
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/login">Sign in</Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/signup">Sign up</Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
