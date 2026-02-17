"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Settings, LogOut, ChevronDown } from "lucide-react";
import { useSession } from "next-auth/react";
import { cn } from "@/lib/utils";
import { GlassCard } from "@/components/ui/glass-card";
import { scaleInVariants } from "@/lib/animation-variants";

export interface UserMenuProps {
  userName?: string;
  userEmail: string;
  onLogout: () => void;
}

/**
 * OAuth provider icons for user menu indicator
 */
function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
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

/**
 * UserMenu - Dropdown menu for user actions
 * T056: User menu dropdown with settings and logout
 * T018: OAuth indicator showing login method
 */
export function UserMenu({ userName, userEmail, onLogout }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: session } = useSession();

  // Get OAuth provider from NextAuth session
  const oauthProvider = (session as { oauthProvider?: string } | null)?.oauthProvider;

  const displayName = userName || userEmail.split("@")[0] || "User";
  const initials = displayName.slice(0, 2).toUpperCase();

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg",
          "hover:bg-muted transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        )}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* Avatar */}
        <div className="avatar-circle w-8 h-8 rounded-full flex items-center justify-center">
          <span className="avatar-initials text-sm font-medium">{initials}</span>
        </div>

        {/* Name - hidden on mobile */}
        <span
          className="hidden md:block text-sm font-medium truncate max-w-[120px] username-text"
        >
          {displayName}
        </span>

        <ChevronDown
          className={cn(
            "h-4 w-4 transition-transform username-text",
            isOpen && "rotate-180"
          )}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop to close menu */}
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Dropdown menu */}
            <motion.div
              className="absolute right-0 top-full mt-2 z-50 w-56"
              variants={scaleInVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <GlassCard className="p-2" blur="lg">
                {/* User info */}
                <div className="px-3 py-2 border-b border-border/50 mb-2">
                  <p className="text-sm font-medium truncate">{displayName}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    {userEmail}
                  </p>
                  {/* T018: OAuth indicator */}
                  {oauthProvider && (
                    <div className="flex items-center gap-1.5 mt-1.5">
                      {oauthProvider === "google" && (
                        <GoogleIcon className="h-3.5 w-3.5" />
                      )}
                      {oauthProvider === "github" && (
                        <GitHubIcon className="h-3.5 w-3.5" />
                      )}
                      <span className="text-xs text-muted-foreground">
                        Signed in with {oauthProvider === "google" ? "Google" : "GitHub"}
                      </span>
                    </div>
                  )}
                </div>

                {/* Menu items */}
                <div className="space-y-1">
                  <MenuButton
                    icon={User}
                    label="Profile"
                    onClick={() => {
                      setIsOpen(false);
                      // Profile not implemented
                    }}
                  />
                  <MenuButton
                    icon={Settings}
                    label="Settings"
                    onClick={() => {
                      setIsOpen(false);
                      // Settings not implemented
                    }}
                  />
                  <div className="border-t border-border/50 my-1" />
                  <MenuButton
                    icon={LogOut}
                    label="Logout"
                    onClick={() => {
                      setIsOpen(false);
                      onLogout();
                    }}
                    variant="danger"
                  />
                </div>
              </GlassCard>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

interface MenuButtonProps {
  icon: typeof User;
  label: string;
  onClick: () => void;
  variant?: "default" | "danger";
}

function MenuButton({
  icon: Icon,
  label,
  onClick,
  variant = "default",
}: MenuButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm",
        "transition-colors",
        variant === "danger"
          ? "text-destructive hover:bg-destructive/10"
          : "text-foreground hover:bg-muted"
      )}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}
