// Hackathon Compliance: ChatKit UI for Todo Assistant
// Uses @openai/chatkit-react with custom backend configuration
"use client";

import { useEffect, useRef } from "react";
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";

// Environment configuration for ChatKit
const CHATKIT_API_URL = process.env.NEXT_PUBLIC_CHATKIT_API_URL || "/api/chatkit";
const CHATKIT_DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "";

/**
 * ChatPage - Main chat interface using OpenAI ChatKit
 *
 * Per hackathon spec: Must use OpenAI ChatKit for frontend.
 * Configures ChatKit with custom backend URL per documentation.
 *
 * Note: ChatKit requires a domain key from OpenAI for production use.
 * For local development, you can test without the domain key.
 */
export default function ChatPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const chatKitRef = useRef(null);

  // Initialize ChatKit with custom API configuration
  const { control } = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_DOMAIN_KEY,
      // Custom fetch to add auth headers
      fetch: async (input, init) => {
        const headers = new Headers(init?.headers);
        // Add auth token if available
        const token = localStorage.getItem("auth_token");
        if (token) {
          headers.set("Authorization", `Bearer ${token}`);
        }
        return fetch(input, { ...init, headers });
      },
    },
    theme: "dark",
    header: {
      enabled: true,
      title: {
        enabled: true,
        text: "Todo Assistant",
      },
    },
    startScreen: {
      greeting: "Welcome to Todo Assistant! I can help you manage your tasks.",
      prompts: [
        { label: "Add task", prompt: "Add a task to buy groceries" },
        { label: "Show tasks", prompt: "Show my tasks" },
        { label: "Pending", prompt: "What's pending today?" },
      ],
    },
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
    <div className="h-screen flex flex-col bg-gradient-to-br from-[#1a0033] via-[#2e003e] to-[#120024]">
      <div className="flex-1 w-full">
        {/* OpenAI ChatKit Component per hackathon spec */}
        <ChatKit
          ref={chatKitRef}
          control={control}
          style={{
            width: "100%",
            height: "100%",
            colorScheme: "dark",
          }}
        />
      </div>
    </div>
  );
}
