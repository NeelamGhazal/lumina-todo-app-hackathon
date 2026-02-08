// Task T013: Chat page route
"use client";

import { useEffect, useState, useCallback } from "react";
import { ChatContainer } from "@/components/Chat";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import type { Message } from "@/types/chat";

/**
 * ChatPage - Main chat interface for Todo Assistant
 *
 * Protected route that requires authentication.
 * Integrates with Phase II backend chat API.
 */
export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Chat state (will be replaced by useChat hook in Phase 3C)
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  // Mock send message (will be replaced by API integration in Phase 3C)
  const handleSendMessage = useCallback(async (content: string) => {
    // Create user message with optimistic UI
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      status: "sending",
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setIsTyping(true);
    setError(null);

    // Simulate API call (will be replaced with real API in Phase 3C)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Update user message status
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, status: "sent" } : msg
        )
      );

      // Add mock AI response
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: `I received your message: "${content}"\n\nThis is a mock response. The real AI integration will be added in Phase 3C.`,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch {
      setError("Failed to send message. Please try again.");
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id ? { ...msg, status: "error" } : msg
        )
      );
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    setError(null);
    // Could retry last failed message here
  }, []);

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
      onSendMessage={handleSendMessage}
      onRetry={handleRetry}
    />
  );
}
