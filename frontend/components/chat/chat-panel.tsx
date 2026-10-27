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
import { ArrowDown, ArrowUp, History, Loader2, Plus, Square, Trash2, X } from "lucide-react";
import { useVisualViewport } from "@/hooks/use-visual-viewport";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
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
  useChatConversationsActions,
} from "@/lib/stores/chat-store";

import { useSendMessage, useConversations, useDeleteConversation as useDeleteConversationApi } from "@/hooks/use-chat";
import { api } from "@/lib/api-client";
import * as chatApi from "@/lib/api/chat";
import { useResponsive, type Breakpoint } from "@/lib/utils/responsive";
import { showToastForAIMutation } from "@/lib/utils/toast";
import { parseToolResult } from "@/lib/utils/sse";

import { ChatMessage } from "./chat-message";
import { VoiceRecorder } from "./voice-recorder";
import { ChatSkeleton, ConversationItemSkeleton, StreamingMessageSkeleton } from "./chat-skeleton";
import { AgentIntro } from "./agent-intro";
import { KairosAvatar } from "./kairos-avatar";

/** Turn backend error strings into something a person can act on. */
function friendlyChatError(error?: string): string {
  if (!error) return "something went wrong. Try again in a moment.";
  if (/auth|sign in|401/i.test(error)) return "your session ended. Sign in again.";
  if (/rate|limit|429/i.test(error)) return "too many messages at once. Wait a minute and try again.";
  if (/network|fetch|failed to fetch/i.test(error)) return "the server can't be reached. Check your connection.";
  return error.replace(/^Sorry,\s*/i, "").replace(/\.$/, "") + ".";
}

// Backend rejects longer messages (MAX_MESSAGE_LENGTH); keep the composer in step.
const MAX_MESSAGE_LENGTH = Number(process.env.NEXT_PUBLIC_CHAT_MAX_MESSAGE_LENGTH) || 5000;

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
 * - Mobile (< 640px): full-screen layout with keyboard handling
 * - Tablet (640px - 1024px): centered modal
 * - Desktop (> 1024px): floating panel bottom-right
 *
 * Mobile keyboard handling uses 100dvh (Dynamic Viewport Height):
 * - dvh automatically adjusts when keyboard opens/closes on iOS
 * - interactive-widget=resizes-content in viewport meta tag enables this
 * - The browser handles scroll position automatically
 */
const getResponsivePanelStyles = (
  breakpoint: Breakpoint,
  safeAreaBottom?: number
) => {
  switch (breakpoint) {
    case "mobile":
      // Full-screen on mobile using dvh (dynamic viewport height)
      // This works with interactive-widget=resizes-content to handle keyboard
      return {
        className: "fixed left-0 right-0 bottom-0 z-50 w-full rounded-none flex flex-col",
        style: {
          height: safeAreaBottom ? `calc(100dvh - ${safeAreaBottom}px)` : '100dvh',
          maxHeight: safeAreaBottom ? `calc(100dvh - ${safeAreaBottom}px)` : '100dvh',
          background: "var(--custom-popover)",
          backdropFilter: "blur(20px)",
          border: "none",
        },
      }
    case "tablet":
      // Centered modal on tablet
      return {
        className: "fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-[600px] max-w-[90vw] h-[80vh] rounded-2xl flex flex-col",
        style: {
          background: "var(--custom-popover)",
          backdropFilter: "blur(20px)",
          border: "1px solid var(--custom-border)",
        },
      }
    case "desktop":
    default:
      // Floating panel on desktop
      return {
        className: "glass-modal fixed bottom-6 right-6 z-50 w-[400px] h-[600px] rounded-[var(--radius-3xl)] flex flex-col",
        style: {
          background: "var(--custom-popover)",
          backdropFilter: "blur(20px)",
          border: "1px solid var(--custom-border)",
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

  // Visual viewport tracking for mobile keyboard handling
  // This ensures the input field stays visible when the keyboard opens
  const visualViewport = useVisualViewport()

  // Query client for task cache updates
  const queryClient = useQueryClient()

  // Panel state
  const isOpen = useChatPanel();
  const isMinimized = useChatPanelMinimized();
  const { toggleOpen, toggleMinimized } = useChatPanelActions();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _unusedToggleMinimized = toggleMinimized; // Reserved for future minimize functionality

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

  // Language state (auto-detect by default)
  const languagePreference = useChatLanguagePreference();

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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isLoadingOlderMessages, setIsLoadingOlderMessages] = useState(false);

  // T054: AbortController for cancelling conversation requests
  const abortControllerRef = useRef<AbortController | null>(null);

  // Stick to the bottom only while the user is there; scrolling up to read stays put.
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const isAtBottomRef = useRef(true);
  const [isAtBottom, setIsAtBottom] = useState(true);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = "auto") => {
    const el = scrollAreaRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior });
  }, []);

  const handleMessagesScroll = useCallback(() => {
    const el = scrollAreaRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 48;
    isAtBottomRef.current = atBottom;
    setIsAtBottom(atBottom);
  }, []);

  useEffect(() => {
    if (isAtBottomRef.current) scrollToBottom(streamedContent ? "auto" : "smooth");
  }, [messages, streamedContent, scrollToBottom]);

  // Focus the composer when the panel opens; Esc closes it.
  useEffect(() => {
    if (!isOpen) return;
    const t = setTimeout(() => inputRef.current?.focus({ preventScroll: true }), 250);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") toggleOpen();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      clearTimeout(t);
      window.removeEventListener("keydown", onKey);
    };
  }, [isOpen, toggleOpen]);

  // Ctrl/Cmd+K opens or closes Kairos from anywhere on the page.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        toggleOpen();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggleOpen]);

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

  const handleSend = async (override?: string) => {
    const message = (override ?? inputValue).trim();
    if (!message || isStreaming) return;
    isAtBottomRef.current = true; // the user's own message always scrolls into view

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
        onToolResult: (tool, output) => {
          console.log("Tool result:", tool, output);
          // Parse task mutations from tool results and update cache
          // This enables real-time dashboard updates when AI performs task actions
          try {
            const parsedOutput = typeof output === 'string' ? JSON.parse(output) : output;
            const mutation = parseToolResult(tool, parsedOutput);
            if (mutation) {
              // Update TanStack Query cache for immediate UI updates
              chatApi.updateTaskCache(queryClient, mutation);
              // Show toast notification for AI actions
              showToastForAIMutation(mutation);
            }
          } catch {
            console.debug("Could not parse tool result as JSON:", output);
          }
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
          // Show the failure where the user is looking, not only in a toast that fades
          addMessage({
            id: `error-${Date.now()}`,
            conversationId: conversationId || "temp",
            role: "system",
            content: `Kairos couldn't reply: ${friendlyChatError(error)}`,
            createdAt: new Date().toISOString(),
          });
          resetStream();
        },
      });
    } catch (error) {
      console.error("Send message error:", error);
      resetStream();
    }
  };

  // Stop the reply; keep whatever arrived so far.
  const handleStop = () => {
    sendMessage.stop();
    if (streamedContent.trim()) {
      addMessage({
        id: `assistant-stopped-${Date.now()}`,
        conversationId: conversationId || "temp",
        role: "assistant",
        content: streamedContent,
        createdAt: new Date().toISOString(),
      });
    }
    resetStream();
    inputRef.current?.focus();
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
        onToolResult: (tool, output) => {
          console.log("Tool result:", tool, output);
          // Parse task mutations from tool results and update cache
          // This enables real-time dashboard updates when AI performs task actions
          try {
            const parsedOutput = typeof output === 'string' ? JSON.parse(output) : output;
            const mutation = parseToolResult(tool, parsedOutput);
            if (mutation) {
              // Update TanStack Query cache for immediate UI updates
              chatApi.updateTaskCache(queryClient, mutation);
              // Show toast notification for AI actions
              showToastForAIMutation(mutation);
            }
          } catch {
            console.debug("Could not parse tool result as JSON:", output);
          }
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
          // Show the failure where the user is looking, not only in a toast that fades
          addMessage({
            id: `error-${Date.now()}`,
            conversationId: conversationId || "temp",
            role: "system",
            content: `Kairos couldn't reply: ${friendlyChatError(error)}`,
            createdAt: new Date().toISOString(),
          });
          resetStream();
        },
      });
    } catch (error) {
      console.error("Send voice message error:", error);
      resetStream();
    }
  }, [isStreaming, conversationId, addMessage, startStreaming, sendMessage, languagePreference,
      setStoreConversationId, appendStreamedContent, resetStream, queryClient]);

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
            aria-label="Ask Kairos (Ctrl+K)"
            className={`${getFABPosition(breakpoint)} flex items-center gap-2 rounded-full bg-primary py-3.5 pl-4 pr-5 font-medium text-primary-foreground shadow-[0_10px_30px_-8px_color-mix(in_oklch,var(--custom-primary)_60%,transparent)] transition-transform active:scale-[0.97]`}
          >
            <KairosAvatar className="size-6 bg-transparent" />
            <span className="hidden sm:inline">Ask Kairos</span>
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
            role="dialog"
            aria-labelledby="kairos-title"
            className={`${getResponsivePanelStyles(breakpoint, visualViewport.safeAreaBottom).className} shadow-2xl overflow-hidden`}
            style={getResponsivePanelStyles(breakpoint, visualViewport.safeAreaBottom).style}
          >
            {/* Header */}
            <div className="flex items-center justify-between gap-2 border-b border-border px-3 py-2.5 sm:px-4">
              <div className="flex min-w-0 items-center gap-3">
                <KairosAvatar thinking={isStreaming} />
                <div className="min-w-0">
                  <h2 id="kairos-title" className="font-display text-base font-semibold leading-tight text-foreground">
                    Kairos
                  </h2>
                  <p className="flex items-center gap-1.5 text-xs text-muted-foreground" aria-live="polite">
                    <span
                      className={`size-1.5 rounded-full ${isStreaming ? "bg-primary motion-safe:animate-pulse" : "bg-chart-3"}`}
                      aria-hidden
                    />
                    {isStreaming ? "Thinking…" : "Your task assistant"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-0.5">
                <button
                  type="button"
                  onClick={handleNewConversation}
                  className="grid size-10 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                  aria-label="New conversation"
                  title="New conversation"
                >
                  <Plus className="size-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowHistory(!showHistory)}
                  className={`relative grid size-10 place-items-center rounded-full transition-colors hover:bg-accent hover:text-foreground ${showHistory ? "bg-accent text-foreground" : "text-muted-foreground"}`}
                  aria-label="Conversation history"
                  aria-expanded={showHistory}
                  title="Conversation history"
                >
                  <History className="size-4" />
                  {conversationsData?.conversations && conversationsData.conversations.length > 0 && (
                    <span className="absolute right-1 top-1 grid h-4 min-w-4 place-items-center rounded-full bg-primary px-1 text-[10px] font-semibold tabular-nums text-primary-foreground">
                      {conversationsData.conversations.length}
                    </span>
                  )}
                </button>
                <button
                  type="button"
                  onClick={toggleOpen}
                  className="grid size-10 place-items-center rounded-full text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                  aria-label="Close chat"
                  title="Close (Esc)"
                >
                  <X className="size-4" />
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
                    borderBottom: "1px solid var(--custom-border)",
                  }}
                >
                  <div className="p-3">
                    <p className="mb-2 text-xs font-medium text-muted-foreground">Recent conversations</p>
                    <div className="chat-scroll -mr-1 max-h-44 space-y-1 overflow-y-auto pr-1">
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
                            className="flex items-center gap-2 p-2 rounded-lg hover:bg-foreground/5 transition-colors group cursor-pointer"
                            style={{
                              background: conv.id === conversationId ? "color-mix(in oklch, var(--custom-primary) 10%, transparent)" : undefined,
                            }}
                          >
                            <button
                              onClick={() => handleLoadConversation(conv as Conversation)}
                              className="flex-1 text-left text-sm text-foreground/80 truncate"
                            >
                              {formatConversationTitle(conv as Conversation)}
                            </button>
                            <button
                              onClick={() => handleDeleteConversation(conv.id)}
                              className="grid size-8 place-items-center rounded-full text-muted-foreground opacity-0 transition-opacity hover:bg-destructive/15 hover:text-destructive focus-visible:opacity-100 group-hover:opacity-100"
                              aria-label="Delete conversation"
                              title="Delete conversation"
                            >
                              <Trash2 className="size-3.5" />
                            </button>
                          </div>
                        ))
                      ) : (
                        <p className="py-2 text-center text-xs text-muted-foreground">No conversations yet. Your chats will show up here.</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Messages Area */}
            {!isMinimized && (
              <>
                <div className="relative flex min-h-0 flex-1 flex-col">
                <div
                  ref={scrollAreaRef}
                  onScroll={handleMessagesScroll}
                  className="chat-scroll chat-scroll-fade flex-1 space-y-4 overflow-y-auto px-4 py-5"
                  id="chat-messages-area"
                  role="log"
                  aria-label="Conversation with Kairos"
                  aria-live="polite"
                >
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
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs text-foreground/60"
                          style={{
                            background: "color-mix(in oklch, var(--custom-foreground) 5%, transparent)",
                            border: "1px solid var(--custom-border)",
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
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-all bg-primary text-primary-foreground"
                          >
                            Retry loading
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
                          <p className="text-foreground/70 mb-2">Taking longer than expected...</p>
                          <button
                            onClick={() => {
                              setConversationLoadTimeout(false);
                              if (conversationId) {
                                handleLoadConversation({ id: conversationId } as Conversation);
                              }
                            }}
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-all bg-primary text-primary-foreground"
                          >
                            Retry loading
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
                          onExampleClick={(promptText) => handleSend(promptText)}
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

                {/* Jump back down when the user has scrolled up and new content arrives */}
                <AnimatePresence>
                  {!isAtBottom && (messages.length > 0 || isStreaming) && (
                    <motion.button
                      type="button"
                      initial={{ opacity: 0, y: 8, scale: 0.96 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.96 }}
                      transition={{ duration: 0.18 }}
                      onClick={() => scrollToBottom("smooth")}
                      className="glass absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-medium text-foreground"
                    >
                      <ArrowDown className="size-3.5" /> Jump to latest
                    </motion.button>
                  )}
                </AnimatePresence>
                </div>

                {/* Composer */}
                <div
                  className="border-t border-border p-3 sm:p-4"
                  style={{
                    paddingBottom: breakpoint === "mobile"
                      ? `calc(0.75rem + ${visualViewport.safeAreaBottom}px)`
                      : undefined,
                  }}
                >
                  <div className="flex items-end gap-1.5 rounded-[var(--radius-2xl)] border border-border bg-background/70 p-1.5 transition-[border-color,box-shadow] duration-200 focus-within:border-primary/60 focus-within:shadow-[0_0_0_3px_color-mix(in_oklch,var(--custom-primary)_18%,transparent)]">
                    <div className="grid size-11 shrink-0 place-items-center">
                      <VoiceRecorder
                        onTranscript={handleTranscript}
                        onVoiceMessageSend={handleVoiceMessageSend}
                        disabled={isStreaming}
                      />
                    </div>

                    <label htmlFor="kairos-input" className="sr-only">Message Kairos</label>
                    <textarea
                      id="kairos-input"
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value.slice(0, MAX_MESSAGE_LENGTH))}
                      onKeyDown={handleKeyDown}
                      placeholder="Message Kairos"
                      disabled={isStreaming}
                      dir="auto"
                      className="chat-scroll flex-1 resize-none bg-transparent px-1 py-2.5 text-foreground outline-none placeholder:text-muted-foreground disabled:opacity-60"
                      style={{
                        fieldSizing: "content",
                        minHeight: "44px",
                        maxHeight: "140px",
                        fontSize: "16px", // Prevents iOS auto-zoom on focus (T044)
                      }}
                      rows={1}
                    />

                    {isStreaming ? (
                      <button
                        type="button"
                        onClick={handleStop}
                        className="grid size-11 shrink-0 place-items-center rounded-full bg-foreground text-background transition-transform active:scale-95"
                        aria-label="Stop generating"
                        title="Stop"
                      >
                        <Square className="size-3.5 fill-current" />
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleSend()}
                        disabled={!inputValue.trim()}
                        className="grid size-11 shrink-0 place-items-center rounded-full bg-primary text-primary-foreground transition-[transform,opacity] active:scale-95 disabled:bg-muted disabled:text-muted-foreground"
                        aria-label="Send message"
                      >
                        <ArrowUp className="size-4" strokeWidth={2.5} />
                      </button>
                    )}
                  </div>
                  <div className="mt-1.5 flex items-center justify-between px-2 text-[11px] text-muted-foreground">
                    <span className="hidden sm:inline">Enter to send, Shift+Enter for a new line</span>
                    {inputValue.length > MAX_MESSAGE_LENGTH * 0.9 && (
                      <span className="ml-auto tabular-nums" aria-live="polite">
                        {inputValue.length} / {MAX_MESSAGE_LENGTH}
                      </span>
                    )}
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
