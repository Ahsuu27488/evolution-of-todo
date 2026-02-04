/**
 * Chat UI Context - React Context for chat UI state.
 *
 * Using Context instead of Zustand to avoid SSR/hydration issues with Next.js.
 * Zustand selectors that return objects cause infinite re-render loops.
 *
 * Manages client-side UI state that doesn't belong in server state:
 * - Chat panel open/close state
 * - Minimized state
 * - Current streaming message
 * - Voice input state
 */

"use client"

import { createContext, useContext, useState, useCallback, ReactNode, createElement } from "react"

// =============================================================================
// Types
// =============================================================================

export interface ChatMessage {
  id: string
  conversationId: string
  role: "user" | "assistant" | "system"
  content: string
  toolCalls?: Array<{
    tool: string
    arguments: Record<string, unknown>
  }>
  createdAt: string
}

export interface Conversation {
  id: string
  title: string
  messageCount: number
  languagePreference: "auto" | "en" | "ur"
  createdAt: string
  updatedAt: string
}

interface ChatUIState {
  // Panel state
  isOpen: boolean
  isMinimized: boolean

  // Current conversation
  conversationId: string | null
  messages: ChatMessage[]

  // Message pagination
  pagination: {
    total: number
    hasMore: boolean
    loadingMore: boolean
  }

  // Streaming state
  isStreaming: boolean
  streamedContent: string
  currentAgent: string | null
  pendingToolCalls: Array<{ tool: string; args: Record<string, unknown> }>
  agentHandoffs: Array<{ from: string; to: string; timestamp: string }>

  // Input state
  inputValue: string
  inputMode: "text" | "voice"

  // Voice state
  isRecording: boolean
  isTranscribing: boolean

  // Error state
  error: string | null

  // Conversations list
  conversations: Conversation[]

  // Language preference for Urdu support
  languagePreference: "auto" | "en" | "ur"

  // Actions
  setOpen: (open: boolean) => void
  toggleOpen: () => void
  setMinimized: (minimized: boolean) => void
  toggleMinimized: () => void

  setConversationId: (id: string | null) => void
  setMessages: (messages: ChatMessage[]) => void
  addMessage: (message: ChatMessage) => void
  prependMessages: (messages: ChatMessage[]) => void
  clearMessages: () => void

  setPagination: (pagination: { total: number; hasMore: boolean }) => void
  setLoadingMore: (loading: boolean) => void

  startStreaming: () => void
  stopStreaming: () => void
  appendStreamedContent: (content: string) => void
  setCurrentAgent: (agent: string | null) => void
  addPendingToolCall: (tool: string, args: Record<string, unknown>) => void
  addAgentHandoff: (from: string, to: string) => void
  resetStreamState: () => void

  setInputValue: (value: string) => void
  setInputMode: (mode: "text" | "voice") => void

  setRecording: (recording: boolean) => void
  setTranscribing: (transcribing: boolean) => void

  setError: (error: string | null) => void
  clearError: () => void

  setConversations: (conversations: Conversation[]) => void

  setLanguagePreference: (preference: "auto" | "en" | "ur") => void
  toggleLanguage: () => void

  reset: () => void
}

const ChatContext = createContext<ChatUIState | null>(null)

// =============================================================================
// Provider
// =============================================================================

export function ChatProvider({ children }: { children: ReactNode }) {
  // Panel state
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)

  // Current conversation
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])

  // Message pagination
  const [pagination, setPaginationState] = useState({
    total: 0,
    hasMore: false,
    loadingMore: false,
  })

  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamedContent, setStreamedContent] = useState("")
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [pendingToolCalls, setPendingToolCalls] = useState<Array<{ tool: string; args: Record<string, unknown> }>>([])
  const [agentHandoffs, setAgentHandoffs] = useState<Array<{ from: string; to: string; timestamp: string }>>([])

  // Input state
  const [inputValue, setInputValue] = useState("")
  const [inputMode, setInputModeState] = useState<"text" | "voice">("text")

  // Voice state
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)

  // Error state
  const [error, setError] = useState<string | null>(null)

  // Conversations list
  const [conversations, setConversations] = useState<Conversation[]>([])

  // Language preference
  const [languagePreference, setLanguagePreferenceState] = useState<"auto" | "en" | "ur">("auto")

  // Actions (using useCallback to maintain stable references)
  const toggleOpen = useCallback(() => setIsOpen((prev) => !prev), [])
  const setMinimized = useCallback((minimized: boolean) => setIsMinimized(minimized), [])
  const toggleMinimized = useCallback(() => setIsMinimized((prev) => !prev), [])

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message])
    setPaginationState((prev) => ({ ...prev, total: prev.total + 1 }))
  }, [])

  const prependMessages = useCallback((newMessages: ChatMessage[]) => {
    setMessages((prev) => [...newMessages, ...prev])
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
    setPaginationState({ total: 0, hasMore: false, loadingMore: false })
  }, [])

  const setPagination = useCallback((pagination: { total: number; hasMore: boolean }) => {
    setPaginationState((prev) => ({ ...prev, ...pagination }))
  }, [])

  const setLoadingMore = useCallback((loading: boolean) => {
    setPaginationState((prev) => ({ ...prev, loadingMore: loading }))
  }, [])

  const startStreaming = useCallback(() => {
    setIsStreaming(true)
    setStreamedContent("")
    setPendingToolCalls([])
    setAgentHandoffs([])
  }, [])

  const stopStreaming = useCallback(() => {
    setIsStreaming(false)
  }, [])

  const appendStreamedContent = useCallback((content: string) => {
    setStreamedContent((prev) => prev + content)
  }, [])

  const addPendingToolCall = useCallback((tool: string, args: Record<string, unknown>) => {
    setPendingToolCalls((prev) => [...prev, { tool, args }])
  }, [])

  const addAgentHandoff = useCallback((from: string, to: string) => {
    setAgentHandoffs((prev) => [...prev, { from, to, timestamp: new Date().toISOString() }])
  }, [])

  const resetStreamState = useCallback(() => {
    setIsStreaming(false)
    setStreamedContent("")
    setCurrentAgent(null)
    setPendingToolCalls([])
    setAgentHandoffs([])
  }, [])

  const setInputMode = useCallback((mode: "text" | "voice") => {
    setInputModeState(mode)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const toggleLanguage = useCallback(() => {
    setLanguagePreferenceState((prev) => {
      if (prev === "auto") return "en"
      if (prev === "en") return "ur"
      return "auto"
    })
  }, [])

  const reset = useCallback(() => {
    setIsOpen(false)
    setIsMinimized(false)
    setConversationId(null)
    setMessages([])
    setPaginationState({ total: 0, hasMore: false, loadingMore: false })
    setIsStreaming(false)
    setStreamedContent("")
    setCurrentAgent(null)
    setPendingToolCalls([])
    setAgentHandoffs([])
    setInputValue("")
    setInputModeState("text")
    setIsRecording(false)
    setIsTranscribing(false)
    setError(null)
    setConversations([])
    setLanguagePreferenceState("auto")
  }, [])

  const value: ChatUIState = {
    isOpen,
    isMinimized,
    conversationId,
    messages,
    pagination,
    isStreaming,
    streamedContent,
    currentAgent,
    pendingToolCalls,
    agentHandoffs,
    inputValue,
    inputMode,
    isRecording,
    isTranscribing,
    error,
    conversations,
    languagePreference,

    setOpen: setIsOpen,
    toggleOpen,
    setMinimized,
    toggleMinimized,

    setConversationId,
    setMessages,
    addMessage,
    prependMessages,
    clearMessages,

    setPagination,
    setLoadingMore,

    startStreaming,
    stopStreaming,
    appendStreamedContent,
    setCurrentAgent,
    addPendingToolCall,
    addAgentHandoff,
    resetStreamState,

    setInputValue,
    setInputMode,

    setRecording: setIsRecording,
    setTranscribing: setIsTranscribing,

    setError,
    clearError,

    setConversations,

    setLanguagePreference: setLanguagePreferenceState,
    toggleLanguage,

    reset,
  }

  return createElement(ChatContext.Provider, { value }, children)
}

// =============================================================================
// Hook
// =============================================================================

export function useChatStore() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error("useChatStore must be used within ChatProvider")
  }
  return context
}

// =============================================================================
// Legacy selector exports for backward compatibility
// =============================================================================

// These are deprecated - use useChatStore() directly
export const useChatPanel = () => {
  const store = useChatStore()
  return store.isOpen
}
export const useChatPanelMinimized = () => {
  const store = useChatStore()
  return store.isMinimized
}
export const useChatPanelActions = () => {
  const store = useChatStore()
  return {
    setOpen: store.setOpen,
    toggleOpen: store.toggleOpen,
    setMinimized: store.setMinimized,
    toggleMinimized: store.toggleMinimized,
  }
}

export const useChatConversationId = () => {
  const store = useChatStore()
  return store.conversationId
}
export const useChatMessages = () => {
  const store = useChatStore()
  return store.messages
}
export const useChatConversationActions = () => {
  const store = useChatStore()
  return {
    setConversationId: store.setConversationId,
    setMessages: store.setMessages,
    addMessage: store.addMessage,
    prependMessages: store.prependMessages,
    clearMessages: store.clearMessages,
  }
}

export const useChatPaginationState = () => {
  const store = useChatStore()
  return store.pagination
}
export const useChatPaginationActions = () => {
  const store = useChatStore()
  return {
    setPagination: store.setPagination,
    setLoadingMore: store.setLoadingMore,
  }
}

export const useChatStreamingState = () => {
  const store = useChatStore()
  return {
    isStreaming: store.isStreaming,
    streamedContent: store.streamedContent,
    currentAgent: store.currentAgent,
    pendingToolCalls: store.pendingToolCalls,
    agentHandoffs: store.agentHandoffs,
  }
}
export const useChatStreamingActions = () => {
  const store = useChatStore()
  return {
    startStreaming: store.startStreaming,
    stopStreaming: store.stopStreaming,
    appendStreamedContent: store.appendStreamedContent,
    setCurrentAgent: store.setCurrentAgent,
    resetStreamState: store.resetStreamState,
  }
}

export const useChatInputValue = () => {
  const store = useChatStore()
  return store.inputValue
}
export const useChatInputMode = () => {
  const store = useChatStore()
  return store.inputMode
}
export const useChatInputActions = () => {
  const store = useChatStore()
  return {
    setInputValue: store.setInputValue,
    setInputMode: store.setInputMode,
  }
}

export const useChatRecordingState = () => {
  const store = useChatStore()
  return store.isRecording
}
export const useChatTranscribingState = () => {
  const store = useChatStore()
  return store.isTranscribing
}
export const useChatVoiceActions = () => {
  const store = useChatStore()
  return {
    setRecording: store.setRecording,
    setTranscribing: store.setTranscribing,
  }
}

export const useChatErrorState = () => {
  const store = useChatStore()
  return store.error
}
export const useChatErrorActions = () => {
  const store = useChatStore()
  return {
    setError: store.setError,
    clearError: store.clearError,
  }
}

export const useChatConversationsList = () => {
  const store = useChatStore()
  return store.conversations
}
export const useChatConversationsActions = () => {
  const store = useChatStore()
  return {
    setConversations: store.setConversations,
  }
}

export const useChatLanguagePreference = () => {
  const store = useChatStore()
  return store.languagePreference
}
export const useChatLanguageActions = () => {
  const store = useChatStore()
  return {
    setLanguagePreference: store.setLanguagePreference,
    toggleLanguage: store.toggleLanguage,
  }
}

// Legacy combined selectors for backward compatibility
export const useChatInput = () => {
  const store = useChatStore()
  return {
    inputValue: store.inputValue,
    inputMode: store.inputMode,
    setInputValue: store.setInputValue,
    setInputMode: store.setInputMode,
  }
}

export const useChatStreaming = () => {
  const store = useChatStore()
  return {
    isStreaming: store.isStreaming,
    streamedContent: store.streamedContent,
    currentAgent: store.currentAgent,
    pendingToolCalls: store.pendingToolCalls,
    agentHandoffs: store.agentHandoffs,
    startStreaming: store.startStreaming,
    stopStreaming: store.stopStreaming,
    appendStreamedContent: store.appendStreamedContent,
    setCurrentAgent: store.setCurrentAgent,
    resetStreamState: store.resetStreamState,
  }
}

export const useChatLanguage = () => {
  const store = useChatStore()
  return {
    languagePreference: store.languagePreference,
    setLanguagePreference: store.setLanguagePreference,
    toggleLanguage: store.toggleLanguage,
  }
}

export const useChatConversation = () => {
  const store = useChatStore()
  return {
    conversationId: store.conversationId,
    messages: store.messages,
    setConversationId: store.setConversationId,
    setMessages: store.setMessages,
    addMessage: store.addMessage,
    prependMessages: store.prependMessages,
    clearMessages: store.clearMessages,
  }
}

export const useChatPagination = () => {
  const store = useChatStore()
  return {
    pagination: store.pagination,
    setPagination: store.setPagination,
    setLoadingMore: store.setLoadingMore,
  }
}
