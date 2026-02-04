"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

type OrbVariant = "hero" | "auth" | "subtle";

export interface FloatingOrbsProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: OrbVariant;
}

interface OrbConfig {
  size: string;
  color: string;
  position: { top?: string; bottom?: string; left?: string; right?: string };
  blur: string;
  opacity: number;
  delay: number;
}

// LUMINA Orange orb configurations
const orbConfigs: Record<OrbVariant, OrbConfig[]> = {
  hero: [
    {
      size: "w-96 h-96",
      color: "bg-lumina-primary-500",
      position: { top: "10%", right: "10%" },
      blur: "blur-[80px]",
      opacity: 0.2,
      delay: 0,
    },
    {
      size: "w-72 h-72",
      color: "bg-lumina-primary-300",
      position: { bottom: "20%", left: "5%" },
      blur: "blur-[80px]",
      opacity: 0.15,
      delay: 2,
    },
    {
      size: "w-64 h-64",
      color: "bg-lumina-primary-400",
      position: { top: "60%", right: "25%" },
      blur: "blur-[60px]",
      opacity: 0.1,
      delay: 4,
    },
  ],
  auth: [
    {
      size: "w-80 h-80",
      color: "bg-lumina-primary-500",
      position: { top: "20%", left: "10%" },
      blur: "blur-[100px]",
      opacity: 0.25,
      delay: 0,
    },
    {
      size: "w-64 h-64",
      color: "bg-lumina-primary-300",
      position: { bottom: "10%", right: "20%" },
      blur: "blur-[80px]",
      opacity: 0.2,
      delay: 3,
    },
  ],
  subtle: [
    {
      size: "w-48 h-48",
      color: "bg-lumina-primary-500",
      position: { top: "30%", right: "20%" },
      blur: "blur-[60px]",
      opacity: 0.08,
      delay: 0,
    },
    {
      size: "w-36 h-36",
      color: "bg-lumina-primary-300",
      position: { bottom: "40%", left: "15%" },
      blur: "blur-[50px]",
      opacity: 0.06,
      delay: 2,
    },
  ],
};

/**
 * FloatingOrbs - Animated background orbs for Lumina aesthetic
 * T013: Foundational component for Lumina design system
 */
function FloatingOrbs({ variant = "hero", className, ...props }: FloatingOrbsProps) {
  const orbs = orbConfigs[variant];

  return (
    <div
      className={cn(
        "absolute inset-0 overflow-hidden pointer-events-none",
        className
      )}
      aria-hidden="true"
      {...props}
    >
      {orbs.map((orb, index) => (
        <motion.div
          key={index}
          className={cn(
            "absolute rounded-full",
            orb.size,
            orb.color,
            orb.blur
          )}
          style={{
            ...orb.position,
            opacity: orb.opacity,
          }}
          animate={{
            y: [0, -20, 0],
            scale: [1, 1.05, 1],
          }}
          transition={{
            duration: 6,
            ease: "easeInOut",
            repeat: Infinity,
            delay: orb.delay,
          }}
        />
      ))}
    </div>
  );
}

export { FloatingOrbs };
