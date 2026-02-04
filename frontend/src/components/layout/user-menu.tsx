"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Settings, LogOut, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { GlassCard } from "@/components/ui/glass-card";
import { scaleInVariants } from "@/lib/animation-variants";

export interface UserMenuProps {
  userName?: string;
  userEmail: string;
  onLogout: () => void;
}

/**
 * UserMenu - Dropdown menu for user actions
 * T056: User menu dropdown with settings and logout
 */
export function UserMenu({ userName, userEmail, onLogout }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

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
