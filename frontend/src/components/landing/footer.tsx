"use client";

import Link from "next/link";
import { GradientText } from "@/components/ui/gradient-text";

/**
 * Footer - Landing page footer with links and branding
 * T021: Footer component
 */
export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border/50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo and tagline */}
          <div className="text-center md:text-left">
            <Link href="/" className="inline-block">
              <GradientText
                as="span"
                variant="primary"
                className="text-2xl font-bold"
              >
                Lumina
              </GradientText>
            </Link>
            <p className="text-sm text-muted-foreground mt-1">
              Illuminate Your Productivity
            </p>
          </div>

          {/* Links - FR-055: Privacy, Terms, Contact links */}
          <nav className="flex flex-wrap items-center justify-center gap-6 text-sm">
            <Link
              href="/login"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="#"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Privacy
            </Link>
            <Link
              href="#"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Terms
            </Link>
            <Link
              href="#"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Contact
            </Link>
          </nav>

          {/* Copyright */}
          <p className="text-sm text-muted-foreground text-center md:text-right">
            © {currentYear} Lumina. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
