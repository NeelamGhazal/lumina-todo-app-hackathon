"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { motion } from "framer-motion";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";
import { modalOverlayVariants, modalContentVariants } from "@/lib/animation-variants";

/**
 * AdaptiveDialog - Lumina styled responsive modal
 * T072-T079: Glass effects, animations, and Lumina styling
 * Per spec US2: Modal form centered on desktop, bottom sheet on mobile
 * Per spec FR-022: Spring animation for dialog open/close
 */

interface AdaptiveDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

function AdaptiveDialog({ open, onOpenChange, children }: AdaptiveDialogProps) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      {children}
    </DialogPrimitive.Root>
  );
}

const AdaptiveDialogTrigger = DialogPrimitive.Trigger;

const AdaptiveDialogClose = DialogPrimitive.Close;

interface AdaptiveDialogContentProps
  extends Omit<React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>, "children"> {
  showCloseButton?: boolean;
  children: React.ReactNode;
}

/**
 * Animated overlay component
 */
const MotionOverlay = motion.div;

/**
 * Animated content component
 */
const MotionContent = motion.div;

const AdaptiveDialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  AdaptiveDialogContentProps
>(({ className, children, showCloseButton = true, ...props }, ref) => {
  return (
    <DialogPrimitive.Portal>
      {/* T072: Glass backdrop overlay */}
      <DialogPrimitive.Overlay asChild>
        <MotionOverlay
          key="dialog-overlay"
          variants={modalOverlayVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
        />
      </DialogPrimitive.Overlay>

      {/* T073: Glass content with animations */}
      <DialogPrimitive.Content ref={ref} asChild {...props}>
        <MotionContent
          key="dialog-content"
          variants={modalContentVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          className={cn(
            "fixed z-50 w-full",
            // Modal background via CSS class in globals.css
            "modal-content-bg",
            "shadow-glass-xl",
            "border border-zinc-200 dark:border-white/10",
            // Mobile: bottom sheet
            "inset-x-0 bottom-0 rounded-t-2xl max-h-[90vh] overflow-y-auto",
            // Desktop: centered modal
            "md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2",
            "md:max-w-lg md:rounded-xl md:max-h-[85vh]",
            // Focus styles
            "focus:outline-none",
            className
          )}
        >
          {/* Drag handle for mobile */}
          <div className="md:hidden flex justify-center pt-3 pb-1">
            <div className="w-12 h-1.5 rounded-full bg-muted-foreground/30" />
          </div>
          {children}
          {showCloseButton && (
            <DialogPrimitive.Close
              className={cn(
                "absolute right-4 top-4 p-1.5 rounded-lg",
                "bg-muted/50 hover:bg-muted",
                "opacity-70 hover:opacity-100",
                "ring-offset-background transition-all",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                "disabled:pointer-events-none"
              )}
              aria-label="Close dialog"
            >
              <X className="h-4 w-4" />
            </DialogPrimitive.Close>
          )}
        </MotionContent>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
});
AdaptiveDialogContent.displayName = "AdaptiveDialogContent";

const AdaptiveDialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col space-y-1.5 px-6 pt-4 pb-2 text-center sm:text-left",
      className
    )}
    {...props}
  />
);
AdaptiveDialogHeader.displayName = "AdaptiveDialogHeader";

const AdaptiveDialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      "flex flex-col-reverse gap-2 px-6 pb-6 pt-2 sm:flex-row sm:justify-end",
      className
    )}
    {...props}
  />
);
AdaptiveDialogFooter.displayName = "AdaptiveDialogFooter";

const AdaptiveDialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
));
AdaptiveDialogTitle.displayName = "AdaptiveDialogTitle";

const AdaptiveDialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
));
AdaptiveDialogDescription.displayName = "AdaptiveDialogDescription";

export {
  AdaptiveDialog,
  AdaptiveDialogClose,
  AdaptiveDialogTrigger,
  AdaptiveDialogContent,
  AdaptiveDialogHeader,
  AdaptiveDialogFooter,
  AdaptiveDialogTitle,
  AdaptiveDialogDescription,
};
