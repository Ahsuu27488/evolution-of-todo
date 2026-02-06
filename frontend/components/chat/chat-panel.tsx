/**
 * Chat Panel - Main AI chatbot interface.
 *
 * Features:
 * - Floating FAB to open/close
 * - Glassmorphism design
 * - Animated transitions
 * - Message list with typing indicators
 * - Voice input button with Whisper API
 * - Conversation history management
 * - Minimize/maximize support
 *
 * Per spec.md FR-001 through FR-010, frontend design guidelines.
 */

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { MessageSquare, X, Minimize2, Maximize2, Send, Loader2, Languages, History, Plus, Trash2 } from "lucide-react";
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
  useChatConversationsList,
  useChatConversationsActions,
} from "@/lib/stores/chat-store";

import { useSendMessage, useConversations, useDeleteConversation as useDeleteConversationApi } from "@/hooks/use-chat";
import { api } from "@/lib/api-client";
import * as chatApi from "@/lib/api/chat";

import { ChatMessage } from "./chat-message";
import { VoiceRecorder } from "./voice-recorder";

// =============================================================================
// Types
// =============================================================================

interface Conversation {
  id: string;
  title: string;
  messageCount: number;
  languagePreference: "auto" | "en" | "ur";
  createdAt: string;
  updatedAt: string;
}

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
  const { addMessage, prependMessages, setConversationId: setStoreConversationId, clearMessages } = useChatConversationActions();
  const { setConversations: setStoreConversations } = useChatConversationsActions();

  // Streaming state
  const { isStreaming, streamedContent } = useChatStreamingState();
  const { resetStreamState: resetStream, appendStreamedContent, startStreaming, stopStreaming } = useChatStreamingActions();

  // Input state
  const inputValue = useChatInputValue();
  const { setInputValue } = useChatInputActions();

  // Language state
  const languagePreference = useChatLanguagePreference();
  const { toggleLanguage, setLanguagePreference } = useChatLanguageActions();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // API hooks
  const sendMessage = useSendMessage();
  const { data: conversationsData, refetch: refetchConversations } = useConversations();
  const deleteConversationApi = useDeleteConversationApi();

  // Local state for conversation history sidebar
  const [showHistory, setShowHistory] = useState(false);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedContent]);

  // Load conversations when panel opens
  useEffect(() => {
    if (isOpen) {
      refetchConversations();
    }
  }, [isOpen, refetchConversations]);

  // Sync conversations from API to store
  useEffect(() => {
    if (conversationsData?.conversations) {
      setStoreConversations(conversationsData.conversations);
    }
  }, [conversationsData, setStoreConversations]);

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

    try {
      // Track the actual conversation ID (may be updated by onMessageStart)
      let actualConversationId = conversationId;

      // Send message with current conversationId (or null for new conversation)
      await sendMessage.mutateAsync({
        message,
        conversationId: conversationId, // ← FIXED: Use actual conversationId, not null!
        languagePreference, // ← Send language preference per message
        onMessageStart: (newConversationId) => {
          // Update store when backend creates a new conversation
          if (!conversationId && newConversationId) {
            actualConversationId = newConversationId;
            setStoreConversationId(newConversationId);
            console.log("New conversation created:", newConversationId);
          }
        },
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
          // Use actualConversationId which may have been updated by onMessageStart
          addMessage({
            id: `assistant-${Date.now()}`,
            conversationId: actualConversationId || "temp",
            role: "assistant",
            content: output,
            createdAt: new Date().toISOString(),
          });
          resetStream();
        },
        onError: (error, newConversationId) => {
          console.error("Chat error:", error, newConversationId);
          // Even on error, if we received a conversation_id, update the store
          // This fixes the bug where errors cause new conversations on each message
          if (!conversationId && newConversationId) {
            setStoreConversationId(newConversationId);
            console.log("Error but received conversation_id:", newConversationId);
          }
          toast.error(error || "Failed to send message");
          resetStream();
        },
      });
    } catch (error) {
      console.error("Send message error:", error);
      resetStream();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Start a new conversation
  const handleNewConversation = useCallback(() => {
    clearMessages();
    setStoreConversationId(null);
    setShowHistory(false);
  }, [clearMessages, setStoreConversationId]);

  // Load an existing conversation
  const handleLoadConversation = useCallback(async (conv: Conversation) => {
    try {
      console.log("[DEBUG] Loading conversation:", conv.id, conv.title);
      const result = await chatApi.getConversation(conv.id);
      console.log("[DEBUG] API result success:", result.success);
      if (result.success && result.data) {
        console.log("[DEBUG] Raw messages from API:", result.data.messages.length, result.data.messages);
        // Log first message's structure to diagnose timestamp issue
        if (result.data.messages.length > 0) {
          const firstMsg = result.data.messages[0] as any;
          console.log("[DEBUG] First message structure:", {
            id: firstMsg.id,
            role: firstMsg.role,
            createdAt: firstMsg.createdAt,
            created_at: (firstMsg as any).created_at,
            allKeys: Object.keys(firstMsg),
          });
        }
        setStoreConversationId(conv.id);
        // Convert API messages to store format, filtering out tool messages
        // Tool messages are used for context but shouldn't be displayed to users
        const loadedMessages = result.data.messages
          .filter((m) => m.role !== "tool")
          .map((m) => ({
            id: m.id,
            conversationId: m.conversationId,
            role: m.role,
            content: m.content,
            toolCalls: m.toolCalls,
            createdAt: m.createdAt ?? (m as any).created_at ?? new Date().toISOString(),
          }));
        console.log("[DEBUG] Filtered messages (non-tool):", loadedMessages.length, loadedMessages);
        // Clear and set messages (reverse to show newest at bottom)
        clearMessages();
        loadedMessages.forEach((msg) => {
          console.log("[DEBUG] Adding message:", msg.role, msg.content?.substring(0, 50));
          addMessage(msg);
        });
        setShowHistory(false);
      }
    } catch (error) {
      console.error("Failed to load conversation:", error);
      toast.error("Failed to load conversation");
    }
  }, [addMessage, clearMessages, setStoreConversationId]);

  // Delete a conversation
  const handleDeleteConversation = useCallback(async (convId: string) => {
    try {
      const result = await deleteConversationApi.mutateAsync(convId);
      if (result) {
        toast.success("Conversation deleted");
        refetchConversations();
        // If deleted current conversation, start fresh
        if (convId === conversationId) {
          handleNewConversation();
        }
      }
    } catch (error) {
      console.error("Failed to delete conversation:", error);
      toast.error("Failed to delete conversation");
    }
  }, [conversationId, deleteConversationApi, handleNewConversation, refetchConversations]);

  // Handle transcript from voice recording
  const handleTranscript = useCallback((text: string, _language?: string) => {
    // Transcription is independent of language mode
    // Just append the transcribed text to input
    setInputValue(inputValue ? `${inputValue} ${text}` : text);
  }, [inputValue, setInputValue]);

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
          toast.info("Full task editing available in the main task view");
          break;
        }
      }
    } catch (_error) {
      toast.error("Failed to perform action on task");
    }
  };

  // Format conversation title
  const formatConversationTitle = (conv: Conversation) => {
    if (conv.title && conv.title !== "New Chat") return conv.title;
    const date = new Date(conv.createdAt);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
                    {conversationId ? "Continue chatting..." : "Start a new conversation"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {/* History button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowHistory(!showHistory)}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
                  title="Conversation history"
                >
                  <History className="w-4 h-4 text-white/70" />
                  {conversationsData?.conversations && conversationsData.conversations.length > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-3.5 h-3.5 text-[8px] font-bold rounded-full bg-cyan-500">
                      {conversationsData.conversations.length}
                    </span>
                  )}
                </motion.button>

                {/* Language toggle button (T079) */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleLanguage}
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
                  title={`Language: ${languagePreference === "auto" ? "Auto-detect" : languagePreference === "en" ? "English" : "اردو"}`}
                >
                  <Languages className="w-4 h-4 text-white/70" />
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

            {/* Conversation History Sidebar */}
            <AnimatePresence>
              {showHistory && !isMinimized && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                  style={{
                    borderBottom: "1px solid rgba(168, 85, 247, 0.2)",
                  }}
                >
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-white/70">Conversations</span>
                      <button
                        onClick={handleNewConversation}
                        className="p-1 rounded hover:bg-white/10 transition-colors"
                        title="New conversation"
                      >
                        <Plus className="w-4 h-4 text-cyan-400" />
                      </button>
                    </div>
                    <div className="space-y-1 max-h-40 overflow-y-auto">
                      {conversationsData?.conversations && conversationsData.conversations.length > 0 ? (
                        conversationsData.conversations.map((conv) => (
                          <div
                            key={conv.id}
                            className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors group cursor-pointer"
                            style={{
                              background: conv.id === conversationId ? "rgba(0, 245, 255, 0.1)" : undefined,
                            }}
                          >
                            <button
                              onClick={() => handleLoadConversation(conv as Conversation)}
                              className="flex-1 text-left text-sm text-white/80 truncate"
                            >
                              {formatConversationTitle(conv as Conversation)}
                            </button>
                            <button
                              onClick={() => handleDeleteConversation(conv.id)}
                              className="p-1 rounded hover:bg-red-500/20 opacity-0 group-hover:opacity-100 transition-opacity"
                              title="Delete conversation"
                            >
                              <Trash2 className="w-3 h-3 text-red-400" />
                            </button>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-white/40 text-center py-2">No conversations yet</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Messages Area */}
            {!isMinimized && (
              <>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
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
                        conversationId: conversationId || "temp",
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
                    className="flex items-end gap-2 px-4 py-3 rounded-xl"
                    style={{
                      background: "rgba(255, 255, 255, 0.05)",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                    }}
                  >
                    {/* Voice Input Button with Whisper API (T086-T091) */}
                    <VoiceRecorder
                      onTranscript={handleTranscript}
                      disabled={isStreaming}
                    />

                    {/* Text Input */}
                    <textarea
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask me anything..."
                      disabled={isStreaming}
                      className="flex-1 bg-transparent text-white placeholder-white/40 text-sm resize-none outline-none py-3"
                      style={{
                        fieldSizing: "content",
                        minHeight: "24px",
                        maxHeight: "120px",
                      }}
                      rows={1}
                    />

                    {/* Send Button */}
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isStreaming}
                      className="flex-shrink-0 p-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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
                    </motion.button>
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
