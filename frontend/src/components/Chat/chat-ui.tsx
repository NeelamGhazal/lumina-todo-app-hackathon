"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Bot, User, Loader2, AlertCircle, CheckCircle, Sparkles } from "lucide-react";
import { chatApi, type ChatResponse } from "@/lib/api/endpoints";
import { ApiClientError } from "@/lib/api/client";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalls?: ChatResponse["tool_calls"];
  isLoading?: boolean;
  error?: string;
}

interface QuickPrompt {
  label: string;
  prompt: string;
}

const QUICK_PROMPTS: QuickPrompt[] = [
  { label: "Add task", prompt: "Add a task to buy groceries" },
  { label: "Show tasks", prompt: "Show my tasks" },
  { label: "What's pending?", prompt: "What's pending today?" },
];

export function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageText.trim(),
    };

    const loadingMessage: Message = {
      id: `assistant-${Date.now()}`,
      role: "assistant",
      content: "",
      isLoading: true,
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: messageText.trim(),
        conversation_id: conversationId || undefined,
      });

      setConversationId(response.conversation_id);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                ...msg,
                content: response.message,
                toolCalls: response.tool_calls,
                isLoading: false,
              }
            : msg
        )
      );

      // Dispatch event to refresh task list if task-related tools were used
      if (response.tool_calls?.some(tc =>
        ["add_task", "complete_task", "delete_task", "update_task"].includes(tc.tool)
      )) {
        window.dispatchEvent(new CustomEvent("tasks-updated"));
      }
    } catch (error) {
      const errorMessage =
        error instanceof ApiClientError
          ? error.message
          : "Failed to send message. Please try again.";

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMessage.id
            ? {
                ...msg,
                content: "Sorry, I encountered an error.",
                error: errorMessage,
                isLoading: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleQuickPrompt = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-[#1a0033] via-[#2e003e] to-[#120024]">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-purple-900/30">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-white">Todo Assistant</h1>
          <p className="text-xs text-purple-300/70">AI-powered task management</p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-purple-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              Welcome to Todo Assistant!
            </h2>
            <p className="text-purple-300/70 mb-6 max-w-md">
              I can help you manage your tasks. Try asking me to add, list, or complete tasks.
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {QUICK_PROMPTS.map((qp) => (
                <button
                  key={qp.label}
                  onClick={() => handleQuickPrompt(qp.prompt)}
                  className="px-4 py-2 rounded-full bg-purple-900/30 hover:bg-purple-800/40 text-purple-200 text-sm transition-colors border border-purple-700/30"
                >
                  {qp.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="px-4 pb-4">
        <form onSubmit={handleSubmit} className="relative">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            disabled={isLoading}
            className="w-full px-5 py-4 pr-14 rounded-2xl bg-purple-900/20 border border-purple-700/30 text-white placeholder-purple-400/50 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed hover:from-purple-600 hover:to-pink-600 transition-all"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
          isUser
            ? "bg-gradient-to-br from-blue-500 to-cyan-500"
            : "bg-gradient-to-br from-purple-500 to-pink-500"
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white"
            : "bg-purple-900/30 border border-purple-700/30 text-white"
        }`}
      >
        {message.isLoading ? (
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
            <span className="text-purple-300">Thinking...</span>
          </div>
        ) : (
          <>
            <p className="whitespace-pre-wrap">{message.content}</p>
            {message.error && (
              <div className="mt-2 flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{message.error}</span>
              </div>
            )}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <div className="mt-3 pt-3 border-t border-purple-700/30">
                <p className="text-xs text-purple-400 mb-2">Actions performed:</p>
                <div className="space-y-1">
                  {message.toolCalls.map((tc, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 text-sm text-purple-300"
                    >
                      {tc.success ? (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-red-400" />
                      )}
                      <span>{tc.tool}</span>
                      {tc.result_preview && (
                        <span className="text-purple-400/70 truncate max-w-[150px]">
                          - {tc.result_preview}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
