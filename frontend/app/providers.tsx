"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Toaster } from "@/components/ui/sonner"
import { ThemeProvider } from "next-themes"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AdBlockWarning } from "@/components/layout/adblock-warning"
import { ChatProvider } from "@/lib/stores/chat-store"

// Dynamically import ChatPanel with SSR disabled to prevent hydration issues
const ChatPanel = dynamic(() => import("@/components/chat").then(m => ({ default: m.ChatPanel })), {
  ssr: false,
})

/**
 * React Query DevTools - only in development
 */
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes - consider data fresh
            gcTime: 1000 * 60 * 10, // 10 minutes (was cacheTime in v4)
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider
        attribute="class"
        defaultTheme="dark"
        enableSystem
        disableTransitionOnChange
      >
        {children}
        <Toaster position="bottom-right" richColors closeButton />
        <AdBlockWarning />
        {/* Phase III: AI Chatbot */}
        <ChatProvider>
          <ChatPanel />
        </ChatProvider>
      </ThemeProvider>
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}
