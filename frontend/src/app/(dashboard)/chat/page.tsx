// Task T013 + T018: Chat page route with useChat integration
"use client";

import { useEffect } from "react";
import { ChatContainer } from "@/components/Chat";
import { useChat } from "@/hooks/use-chat";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";

/**
 * ChatPage - Main chat interface for Todo Assistant
 *
 * Protected route that requires authentication.
 * Uses useChat hook for state management and API integration.
 */
export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Chat state from useChat hook
  const {
    messages,
    isLoading,
    isTyping,
    error,
    sendMessage,
    retryLastFailed,
    clearError,
  } = useChat({
    autoLoadHistory: true,
    enablePolling: true,
  });

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
    <ChatContainer
      messages={messages}
      isLoading={isLoading}
      isTyping={isTyping}
      error={error}
      onSendMessage={sendMessage}
      onRetry={() => {
        clearError();
        retryLastFailed();
      }}
    />
  );
}
