/* eslint-disable @typescript-eslint/no-unused-vars */
/**
 * Chat Panel - Main AI chatbot interface.
 *
 * Features:
 * - Floating FAB to open/close
 * - Glassmorphism design
 * - Animated transitions
 * - Message list with typing indicators
 * - Voice input button
 * - Minimize/maximize support
 *
 * Per spec.md FR-001 through FR-010, frontend design guidelines.
 */

"use client";

import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageSquare, X, Minimize2, Maximize2, Send, Loader2, Languages } from "lucide-react";
import { toast } from "sonner";
import type { Task } from "@/types/task";

import {
  useChatPanel,
  useChatPanelMinimized,
  useChatPanelActions,
  useChatMessages,
  useChatConversationId,
  useChatConversationActions,
  useChatStreamingState,
  useChatStreamingActions,
  useChatInputValue,
  useChatInputActions,
  useChatLanguagePreference,
  useChatLanguageActions,
  useChatPaginationState,
  useChatPaginationActions,
} from "@/lib/stores/chat-store";

import { useSendMessage } from "@/hooks/use-chat";
import { api } from "@/lib/api-client";
import * as chatApi from "@/lib/api/chat";

import { ChatMessage } from "./chat-message";

// =============================================================================
// Animation Variants
// =============================================================================

const panelVariants = {
  closed: {
    opacity: 0,
    scale: 0.9,
    y: 20,
  },
  open: {
    opacity: 1,
    scale: 1,
    y: 0,
  },
};

const messageVariants = {
  hidden: {
    opacity: 0,
    y: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
  },
};

// =============================================================================
// Main Component
// =============================================================================

export function ChatPanel() {
  // Panel state
  const isOpen = useChatPanel();
  const isMinimized = useChatPanelMinimized();
  const { toggleOpen, toggleMinimized } = useChatPanelActions();

  // Conversation state
  const messages = useChatMessages();
  const conversationId = useChatConversationId();
  const { addMessage, prependMessages } = useChatConversationActions();

  // Streaming state
  const { isStreaming, streamedContent } = useChatStreamingState();
  const { resetStreamState: resetStream, appendStreamedContent, startStreaming } = useChatStreamingActions();

  // Input state
  const inputValue = useChatInputValue();
  const { setInputValue } = useChatInputActions();

  // Language state
  const languagePreference = useChatLanguagePreference();
  const { toggleLanguage } = useChatLanguageActions();

  // Pagination state
  const pagination = useChatPaginationState();
  const { setPagination, setLoadingMore } = useChatPaginationActions();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = useSendMessage();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedContent]);

  const handleSend = async () => {
    if (!inputValue.trim() || isStreaming) return;

    const message = inputValue;
    setInputValue("");

    // Add user message immediately
    addMessage({
      id: `temp-${Date.now()}`,
      conversationId: conversationId || "temp",
      role: "user",
      content: message,
      createdAt: new Date().toISOString(),
    });

    // Start streaming
    startStreaming();

    await sendMessage.mutateAsync({
      message,
      conversationId: null,
      onToken: (content) => {
        appendStreamedContent(content);
      },
      onToolCall: (tool, args) => {
        console.log("Tool called:", tool, args);
      },
      onAgentHandoff: (from, to) => {
        console.log("Agent handoff:", from, "->", to);
      },
      onDone: (output, _agent) => {
        // Add the final assistant message
        addMessage({
          id: `assistant-${Date.now()}`,
          conversationId: conversationId || "temp",
          role: "assistant",
          content: output,
          createdAt: new Date().toISOString(),
        });
        resetStream();
      },
      onError: (_error) => {
        resetStream();
      },
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle task actions from inline task cards (T116, T117)
  const handleTaskAction = async (action: "complete" | "delete" | "edit", task: Task) => {
    try {
      switch (action) {
        case "complete": {
          const result = await api.updateTask(task.id, { completed: !task.completed });
          if (result.success) {
            toast.success(task.completed ? "Task reinstated" : "Task completed!");
          } else {
            toast.error(result.error.message);
          }
          break;
        }
        case "delete": {
          const result = await api.deleteTask(task.id);
          if (result.success) {
            toast.success("Task deleted");
          } else {
            toast.error(result.error.message);
          }
          break;
        }
        case "edit": {
          // For edit, we could open a modal or prompt user
          // For now, just notify that full editing is available in main UI
          toast.info("Full task editing available in the main task view");
          break;
        }
      }
    } catch (_error) {
      toast.error("Failed to perform action on task");
    }
  };

  // Load more messages (T118: conversation pagination)
  const loadMoreMessages = async () => {
    if (!conversationId || pagination.loadingMore || !pagination.hasMore) return;

    setLoadingMore(true);
    try {
      const result = await chatApi.getConversation(
        conversationId,
        50, // limit
        messages.length, // current offset
      );

      if (result.success) {
        const { data } = result;
        // Convert API messages to store format
        const newMessages: typeof messages = data.messages.map((m) => ({
          id: m.id,
          conversationId: m.conversationId,
          role: m.role,
          content: m.content,
          toolCalls: m.toolCalls,
          createdAt: m.createdAt,
        }));

        prependMessages(newMessages);
        setPagination({
          total: data.pagination.total,
          hasMore: data.pagination.has_more,
        });
      } else {
        toast.error("Failed to load more messages");
      }
    } catch (_error) {
      toast.error("Failed to load more messages");
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <>
      {/* FAB Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            transition={{ duration: 0.4, ease: [0.175, 0.885, 0.32, 1.275] }}
            onClick={toggleOpen}
            className="fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-lg hover:shadow-xl transition-shadow"
            style={{
              background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
            }}
          >
            <MessageSquare className="w-6 h-6 text-white" strokeWidth={2.5} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={panelVariants}
            initial="closed"
            animate="open"
            exit="closed"
            className="fixed bottom-6 right-6 z-50 w-[400px] h-[600px] rounded-2xl shadow-2xl flex flex-col overflow-hidden"
            style={{
              background: "rgba(15, 23, 42, 0.95)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(168, 85, 247, 0.2)",
            }}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-4 py-3"
              style={{
                background: "linear-gradient(90deg, rgba(168, 85, 247, 0.1) 0%, rgba(0, 245, 255, 0.1) 100%)",
                borderBottom: "1px solid rgba(168, 85, 247, 0.2)",
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{
                    background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
                  }}
                >
                  <MessageSquare className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-white font-semibold text-sm">AI Assistant</h2>
                  <p className="text-xs" style={{ color: "rgba(255,255,255,0.6)" }}>
                    Ask me to add tasks, plan your week...
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {/* Language toggle button (T079) */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleLanguage}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
                  title={`Language: ${languagePreference === "auto" ? "Auto-detect" : languagePreference === "en" ? "English" : "اردو"}`}
                >
                  <Languages className="w-4 h-4 text-white/70" />
                  {/* Language indicator badge */}
                  <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-3.5 h-3.5 text-[8px] font-bold rounded-full"
                    style={{
                      background: languagePreference === "auto"
                        ? "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)"
                        : languagePreference === "en"
                          ? "rgba(0, 245, 255, 0.8)"
                          : "rgba(168, 85, 247, 0.8)",
                      }}
                  >
                    {languagePreference === "auto" ? "A" : languagePreference === "en" ? "E" : "U"}
                  </span>
                </motion.button>
                <button
                  onClick={toggleMinimized}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  {isMinimized ? (
                    <Maximize2 className="w-4 h-4 text-white/70" />
                  ) : (
                    <Minimize2 className="w-4 h-4 text-white/70" />
                  )}
                </button>
                <button
                  onClick={toggleOpen}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <X className="w-4 h-4 text-white/70" />
                </button>
              </div>
            </div>

            {/* Messages Area */}
            {!isMinimized && (
              <>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {/* Load more messages button (T118) */}
                  {pagination.hasMore && messages.length > 0 && (
                    <div className="flex justify-center">
                      <button
                        onClick={loadMoreMessages}
                        disabled={pagination.loadingMore}
                        className="px-4 py-2 rounded-full text-xs font-medium transition-all disabled:opacity-50"
                        style={{
                          background: "rgba(255, 255, 255, 0.05)",
                          border: "1px solid rgba(255, 255, 255, 0.1)",
                          color: "rgba(255, 255, 255, 0.7)",
                        }}
                      >
                        {pagination.loadingMore ? (
                          <span className="flex items-center gap-2">
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Loading...
                          </span>
                        ) : (
                          `Load older messages (${pagination.total - messages.length} remaining)`
                        )}
                      </button>
                    </div>
                  )}

                  {/* Welcome message */}
                  {messages.length === 0 && !isStreaming && (
                    <motion.div
                      variants={messageVariants}
                      initial="hidden"
                      animate="visible"
                      className="text-center py-8"
                    >
                      <div
                        className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
                        style={{
                          background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)",
                        }}
                      >
                        <MessageSquare className="w-8 h-8" style={{ color: "#00f5ff" }} />
                      </div>
                      <h3 className="text-white font-semibold mb-2">
                        Welcome to Todo AI
                      </h3>
                      <p className="text-sm text-white/60 mb-4">
                        I can help you manage your tasks naturally:
                      </p>
                      <div className="text-left max-w-xs mx-auto space-y-2">
                        {[
                          '"Add a high priority task to buy groceries tomorrow"',
                          '"Show me my tasks for this week"',
                          '"Mark task 5 as complete"',
                        ].map((example, i) => (
                          <div
                            key={i}
                            className="px-3 py-2 rounded-lg text-sm text-white/80"
                            style={{
                              background: "rgba(255,255,255,0.05)",
                              border: "1px solid rgba(255,255,255,0.1)",
                            }}
                          >
                            {example}
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Messages */}
                  <AnimatePresence mode="popLayout">
                    {messages.map((message) => (
                      <ChatMessage
                        key={message.id}
                        message={message}
                        onTaskAction={handleTaskAction}
                      />
                    ))}
                  </AnimatePresence>

                  {/* Streaming indicator */}
                  {isStreaming && streamedContent && (
                    <ChatMessage
                      message={{
                        id: "streaming",
                        role: "assistant",
                        content: streamedContent,
                        createdAt: new Date().toISOString(),
                      }}
                      isStreaming
                      onTaskAction={handleTaskAction}
                    />
                  )}

                  {/* Typing indicator */}
                  {isStreaming && !streamedContent && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-2 text-white/50"
                    >
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">AI is thinking...</span>
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div
                  className="p-4"
                  style={{
                    borderTop: "1px solid rgba(168, 85, 247, 0.2)",
                  }}
                >
                  <div
                    className="flex items-center gap-2 px-4 py-3 rounded-xl"
                    style={{
                      background: "rgba(255, 255, 255, 0.05)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                    }}
                  >
                    <textarea
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask me anything..."
                      disabled={isStreaming}
                      className="flex-1 bg-transparent text-white placeholder-white/40 text-sm resize-none outline-none"
                      style={{
                        fieldSizing: "content",
                        minHeight: "24px",
                        maxHeight: "120px",
                      }}
                      rows={1}
                    />
                    <button
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isStreaming}
                      className="p-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      style={{
                        background: inputValue.trim() && !isStreaming
                          ? "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)"
                          : "rgba(255,255,255,0.1)",
                      }}
                    >
                      {isStreaming ? (
                        <Loader2 className="w-4 h-4 text-white animate-spin" />
                      ) : (
                        <Send className="w-4 h-4 text-white" />
                      )}
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
