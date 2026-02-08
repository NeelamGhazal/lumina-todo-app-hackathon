// Phase III Part 3: Chat UI for Todo Assistant
// Uses custom ChatUI component compatible with our backend
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ChatUI } from "@/components/chat/chat-ui";

/**
 * ChatPage - Main chat interface for AI Todo Assistant
 *
 * Per hackathon spec: Provides ChatKit-like experience
 * connecting to Phase II API which proxies to Part 2 agent.
 */
export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-[#1a0033] via-[#2e003e] to-[#120024]">
        <div className="w-8 h-8 border-2 border-[#ce93d8] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatUI />
    </div>
  );
}
