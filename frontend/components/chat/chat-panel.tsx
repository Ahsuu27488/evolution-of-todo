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
 * - Responsive design (mobile/tablet/desktop)
 *
 * Per spec.md FR-001 through FR-010, frontend design guidelines.
 * Per User Story 3 (FR-009 through FR-014): Mobile-first responsive design.
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
  useChatConversationsActions,
} from "@/lib/stores/chat-store";

import { useSendMessage, useConversations, useDeleteConversation as useDeleteConversationApi } from "@/hooks/use-chat";
import { api } from "@/lib/api-client";
import * as chatApi from "@/lib/api/chat";
import { useResponsive, type Breakpoint } from "@/lib/utils/responsive";

import { ChatMessage } from "./chat-message";
import { VoiceRecorder } from "./voice-recorder";
import { ChatSkeleton, ConversationItemSkeleton, StreamingMessageSkeleton } from "./chat-skeleton";
import { AgentIntro } from "./agent-intro";

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

/**
 * Responsive panel variants for different screen sizes.
 * Per User Story 3 (FR-009 through FR-011):
 * - Mobile (< 640px): full-screen layout
 * - Tablet (640px - 1024px): centered modal
 * - Desktop (> 1024px): floating panel bottom-right
 */
const getResponsivePanelStyles = (breakpoint: Breakpoint) => {
  switch (breakpoint) {
    case "mobile":
      // Full-screen on mobile
      return {
        className: "fixed inset-0 z-50 w-screen h-screen rounded-none",
        style: {
          background: "rgba(15, 23, 42, 0.98)",
          backdropFilter: "blur(20px)",
          border: "none",
        },
      }
    case "tablet":
      // Centered modal on tablet
      return {
        className: "fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-[600px] max-w-[90vw] h-[80vh] rounded-2xl",
        style: {
          background: "rgba(15, 23, 42, 0.95)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(168, 85, 247, 0.2)",
        },
      }
    case "desktop":
    default:
      // Floating panel on desktop
      return {
        className: "fixed bottom-6 right-6 z-50 w-[400px] h-[600px] rounded-2xl",
        style: {
          background: "rgba(15, 23, 42, 0.95)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(168, 85, 247, 0.2)",
        },
      }
  }
}

/**
 * FAB position variants for different screen sizes.
 * FAB is positioned differently on mobile vs desktop/tablet.
 */
const getFABPosition = (breakpoint: Breakpoint) => {
  switch (breakpoint) {
    case "mobile":
      return "fixed bottom-4 right-4 z-50"
    case "tablet":
      return "fixed bottom-6 right-6 z-50"
    case "desktop":
    default:
      return "fixed bottom-6 right-6 z-50"
  }
}

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

// =============================================================================
// Main Component
// =============================================================================

export function ChatPanel() {
  // Responsive breakpoint detection (User Story 3, T021)
  const { breakpoint } = useResponsive()

  // Panel state
  const isOpen = useChatPanel();
  const isMinimized = useChatPanelMinimized();
  const { toggleOpen, toggleMinimized } = useChatPanelActions();

  // Conversation state
  const messages = useChatMessages();
  const conversationId = useChatConversationId();
  const { addMessage, setConversationId: setStoreConversationId, clearMessages } = useChatConversationActions();
  const { setConversations: setStoreConversations } = useChatConversationsActions();

  // Streaming state
  const { isStreaming, streamedContent } = useChatStreamingState();
  const { resetStreamState: resetStream, appendStreamedContent, startStreaming } = useChatStreamingActions();

  // Input state
  const inputValue = useChatInputValue();
  const { setInputValue } = useChatInputActions();

  // Language state
  const languagePreference = useChatLanguagePreference();
  const { toggleLanguage } = useChatLanguageActions();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // API hooks
  const sendMessage = useSendMessage();
  const { data: conversationsData, refetch: refetchConversations, isLoading: isLoadingConversations } = useConversations();
  const deleteConversationApi = useDeleteConversationApi();

  // Local state for conversation history sidebar
  const [showHistory, setShowHistory] = useState(false);

  // T034, T035, T051: Loading states for conversation and messages
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [conversationLoadTimeout, setConversationLoadTimeout] = useState(false);
  const [conversationLoadError, setConversationLoadError] = useState<string | null>(null);

  // T052: Older messages loading state (pagination)
  const [isLoadingOlderMessages, setIsLoadingOlderMessages] = useState(false);

  // T054: AbortController for cancelling conversation requests
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamedContent]);

  // T052: Scroll handler for loading older messages (pagination)
  // Detects when user scrolls near top of messages and triggers loading
  useEffect(() => {
    const messagesArea = document.getElementById('chat-messages-area');
    if (!messagesArea || !conversationId || isLoadingConversation || isLoadingOlderMessages) {
      return;
    }

    const handleScroll = () => {
      // Check if scrolled near top (within 100px)
      if (messagesArea.scrollTop < 100 && messages.length > 0) {
        // TODO: Implement actual pagination API call
        // For now, this is a placeholder for when pagination is added
        console.log('[DEBUG] Near top - would load older messages for conversation:', conversationId);
        // setIsLoadingOlderMessages(true);
        // await loadOlderMessages(conversationId);
        // setIsLoadingOlderMessages(false);
      }
    };

    messagesArea.addEventListener('scroll', handleScroll);
    return () => messagesArea.removeEventListener('scroll', handleScroll);
  }, [conversationId, messages.length, isLoadingConversation, isLoadingOlderMessages]);

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

  // T054: Cleanup - abort any pending conversation load on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

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
        messageType: "text", // Regular text message
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
        onDone: (output) => {
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

  // Load an existing conversation (T034, T035: with loading state and timeout)
  // T051: Enhanced to show skeleton during conversation switch
  // T053: Error state with retry
  // T054: Request cancellation support
  const handleLoadConversation = useCallback(async (conv: Conversation) => {
    // T054: Cancel any pending conversation load request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    setIsLoadingConversation(true);
    setConversationLoadTimeout(false);
    setConversationLoadError(null);

    // T035: 15 second timeout with retry option
    const timeoutId = setTimeout(() => {
      setConversationLoadTimeout(true);
      setIsLoadingConversation(false);
      setConversationLoadError("Loading timed out. Please try again.");
    }, 15000);

    try {
      console.log("[DEBUG] Loading conversation:", conv.id, conv.title);
      // T054: Pass abort signal to getConversation
      const result = await chatApi.getConversation(conv.id, 50, 0, abortControllerRef.current.signal);
      clearTimeout(timeoutId);
      console.log("[DEBUG] API result success:", result.success);

      if (result.success && result.data) {
        console.log("[DEBUG] Raw messages from API:", result.data.messages.length, result.data.messages);
        // Log first message's structure to diagnose timestamp issue
        if (result.data.messages.length > 0) {
          const firstMsg = result.data.messages[0];
          console.log("[DEBUG] First message structure:", {
            id: firstMsg.id,
            role: firstMsg.role,
            createdAt: firstMsg.createdAt,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
            messageType: m.messageType,  // Preserve message type from API
            toolCalls: m.toolCalls,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
        setConversationLoadTimeout(false);
      } else {
        // T053: Handle API error response - use type narrowing
        if (!result.success) {
          throw new Error(result.error.message || "Failed to load conversation");
        }
      }
    } catch (error) {
      console.error("Failed to load conversation:", error);
      clearTimeout(timeoutId);

      // T053: Check if error is from abort (user switched conversations)
      if (error instanceof Error && error.name === 'AbortError') {
        console.log("[DEBUG] Conversation load cancelled (user switched)");
        return; // Don't show error for cancelled requests
      }

      const errorMessage = error instanceof Error ? error.message : "Failed to load conversation";
      setConversationLoadError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoadingConversation(false);
      abortControllerRef.current = null;
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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleTranscript = useCallback((text: string, _language?: string) => {
    // Transcription is independent of language mode
    // Just append the transcribed text to input
    setInputValue(inputValue ? `${inputValue} ${text}` : text);
  }, [inputValue, setInputValue]);

  // Handle voice message auto-send (transcribed text sent directly to agent)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleVoiceMessageSend = useCallback(async (text: string, _language?: string) => {
    if (!text.trim() || isStreaming) return;

    // Add user message immediately with messageType: "voice"
    addMessage({
      id: `temp-${Date.now()}`,
      conversationId: conversationId || "temp",
      role: "user",
      content: text,
      messageType: "voice",  // Mark as voice message - UI will show indicator instead of text
      createdAt: new Date().toISOString(),
    });

    // Start streaming
    startStreaming();

    try {
      // Track the actual conversation ID (may be updated by onMessageStart)
      let actualConversationId = conversationId;

      // Send message with current conversationId (or null for new conversation)
      await sendMessage.mutateAsync({
        message: text,
        conversationId: conversationId,
        languagePreference,
        messageType: "voice",  // Mark as voice message so backend stores it
        onMessageStart: (newConversationId) => {
          // Update store when backend creates a new conversation
          if (!conversationId && newConversationId) {
            actualConversationId = newConversationId;
            setStoreConversationId(newConversationId);
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
        onDone: (output) => {
          // Add the final assistant message
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
          if (!conversationId && newConversationId) {
            setStoreConversationId(newConversationId);
          }
          toast.error(error || "Failed to send message");
          resetStream();
        },
      });
    } catch (error) {
      console.error("Send voice message error:", error);
      resetStream();
    }
  }, [isStreaming, conversationId, addMessage, startStreaming, sendMessage, languagePreference,
      setStoreConversationId, appendStreamedContent, resetStream]);

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
    } catch {
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
      {/* FAB Button - Responsive positioning (T019, T022) */}
      <AnimatePresence mode="wait">
        {!isOpen && (
          <motion.button
            key={`fab-${breakpoint}`}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 180 }}
            transition={{ duration: 0.4, ease: [0.175, 0.885, 0.32, 1.275] }}
            onClick={toggleOpen}
            className={`${getFABPosition(breakpoint)} p-4 rounded-full shadow-lg hover:shadow-xl transition-shadow`}
            style={{
              background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
            }}
          >
            <MessageSquare className="w-6 h-6 text-white" strokeWidth={2.5} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Panel - Responsive layout with AnimatePresence (T019, T020, T021, T022) */}
      <AnimatePresence mode="wait">
        {isOpen && (
          <motion.div
            key={`panel-${breakpoint}`}
            variants={panelVariants}
            initial="closed"
            animate="open"
            exit="closed"
            transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            className={`${getResponsivePanelStyles(breakpoint).className} shadow-2xl flex flex-col overflow-hidden`}
            style={getResponsivePanelStyles(breakpoint).style}
          >
            {/* Header - Touch targets meet 44px minimum (T023) */}
            <div
              className="flex items-center justify-between px-4 py-3"
              style={{
                background: "linear-gradient(90deg, rgba(168, 85, 247, 0.1) 0%, rgba(0, 245, 255, 0.1) 100%)",
                borderBottom: "1px solid rgba(168, 85, 247, 0.2)",
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 min-h-[44px] min-w-[44px] rounded-full flex items-center justify-center"
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
                {/* History button - 44px touch target (T023) */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowHistory(!showHistory)}
                  className="min-h-[44px] min-w-[44px] p-2 rounded-lg hover:bg-white/10 transition-colors relative flex items-center justify-center"
                  title="Conversation history"
                >
                  <History className="w-4 h-4 text-white/70" />
                  {conversationsData?.conversations && conversationsData.conversations.length > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-3.5 h-3.5 text-[8px] font-bold rounded-full bg-cyan-500">
                      {conversationsData.conversations.length}
                    </span>
                  )}
                </motion.button>

                {/* Language toggle button - 44px touch target (T023, T079) */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleLanguage}
                  className="min-h-[44px] min-w-[44px] p-2 rounded-lg hover:bg-white/10 transition-colors relative flex items-center justify-center"
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
                {/* Minimize button - 44px touch target (T023) */}
                <button
                  onClick={toggleMinimized}
                  className="min-h-[44px] min-w-[44px] p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center justify-center"
                >
                  {isMinimized ? (
                    <Maximize2 className="w-4 h-4 text-white/70" />
                  ) : (
                    <Minimize2 className="w-4 h-4 text-white/70" />
                  )}
                </button>
                {/* Close button - 44px touch target (T023) */}
                <button
                  onClick={toggleOpen}
                  className="min-h-[44px] min-w-[44px] p-2 rounded-lg hover:bg-white/10 transition-colors flex items-center justify-center"
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
                      {/* T034: Conversation list skeleton while loading */}
                      {isLoadingConversations ? (
                        <>
                          <ConversationItemSkeleton />
                          <ConversationItemSkeleton />
                          <ConversationItemSkeleton />
                        </>
                      ) : conversationsData?.conversations && conversationsData.conversations.length > 0 ? (
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
                <div className="flex-1 overflow-y-auto p-4 space-y-4" id="chat-messages-area">
                  {/* T051: Skeleton when loading conversation (shows instead of old messages during switch) */}
                  <AnimatePresence>
                    {isLoadingConversation && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-4"
                      >
                        <ChatSkeleton count={4} variant="mixed" />
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* T052: Older messages loading indicator (shows at top when scrolling up for pagination) */}
                  <AnimatePresence>
                    {isLoadingOlderMessages && !isLoadingConversation && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex justify-center py-2"
                      >
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs text-white/60"
                          style={{
                            background: "rgba(255, 255, 255, 0.05)",
                            border: "1px solid rgba(168, 85, 247, 0.2)",
                          }}
                        >
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span>Loading older messages...</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* T053: Loading error state with retry */}
                  <AnimatePresence>
                    {conversationLoadError && !isLoadingConversation && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="flex flex-col items-center gap-4 py-8"
                      >
                        <div className="text-center">
                          <p className="text-red-400 mb-2 flex items-center gap-2">
                            <X className="w-4 h-4" />
                            {conversationLoadError}
                          </p>
                          <button
                            onClick={() => {
                              setConversationLoadError(null);
                              if (conversationId) {
                                handleLoadConversation({ id: conversationId } as Conversation);
                              }
                            }}
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                            style={{
                              background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
                            }}
                          >
                            Retry Loading
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* T035: Timeout fallback with retry option */}
                  <AnimatePresence>
                    {conversationLoadTimeout && !conversationLoadError && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="flex flex-col items-center gap-4 py-8"
                      >
                        <div className="text-center">
                          <p className="text-white/70 mb-2">Taking longer than expected...</p>
                          <button
                            onClick={() => {
                              setConversationLoadTimeout(false);
                              if (conversationId) {
                                handleLoadConversation({ id: conversationId } as Conversation);
                              }
                            }}
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                            style={{
                              background: "linear-gradient(135deg, #00f5ff 0%, #a855f7 100%)",
                            }}
                          >
                            Retry Loading
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* T051: Messages only show when not loading conversation (to avoid flicker) */}
                  {!isLoadingConversation && (
                    <>
                      {/* Agent Introduction Screen (T036-T040) */}
                      {messages.length === 0 && !isStreaming && !conversationLoadTimeout && !conversationLoadError && (
                        <AgentIntro
                          onExampleClick={(promptText) => {
                            setInputValue(promptText)
                            // Optional: auto-send the message immediately
                            // handleSend()
                          }}
                        />
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

                      {/* Typing indicator - with streaming skeleton (T033, T034) */}
                      <AnimatePresence>
                        {isStreaming && !streamedContent && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 10 }}
                          >
                            <StreamingMessageSkeleton />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area - Touch targets meet 44px minimum (T023) */}
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
                    {/* Voice Input Button with Whisper API (T086-T091) - 44px touch target */}
                    <div className="min-h-[44px] min-w-[44px] flex items-center justify-center">
                      <VoiceRecorder
                        onTranscript={handleTranscript}
                        onVoiceMessageSend={handleVoiceMessageSend}
                        disabled={isStreaming}
                      />
                    </div>

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
                        minHeight: "44px",
                        maxHeight: "120px",
                      }}
                      rows={1}
                    />

                    {/* Send Button - 44px touch target (T023) */}
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isStreaming}
                      className="flex-shrink-0 min-h-[44px] min-w-[44px] p-2 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
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
