"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Error boundary for tasks page
 * Per spec: Handle errors gracefully with retry option
 */
export default function TasksError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error to console in development
    console.error("Tasks page error:", error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-[400px] px-4">
      <Card className="max-w-md w-full">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center text-center space-y-4">
            {/* Error icon */}
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>

            {/* Error message */}
            <div className="space-y-2">
              <h2 className="text-xl font-semibold">Something went wrong</h2>
              <p className="text-sm text-muted-foreground">
                We couldn&apos;t load your tasks. This might be a temporary issue.
              </p>
            </div>

            {/* Error details (development only) */}
            {process.env.NODE_ENV === "development" && (
              <pre className="text-xs text-left bg-muted p-3 rounded-md overflow-auto max-w-full">
                {error.message}
              </pre>
            )}

            {/* Retry button */}
            <Button onClick={reset} className="mt-4">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try again
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
