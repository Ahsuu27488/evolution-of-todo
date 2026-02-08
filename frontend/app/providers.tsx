"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Toaster } from "@/components/ui/sonner"
import { ThemeProvider } from "next-themes"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AdBlockWarning } from "@/components/layout/adblock-warning"
import { ChatProvider } from "@/lib/stores/chat-store"

// Dynamically import ConditionalChatPanel with SSR disabled to prevent hydration issues
// Per spec.md User Story 2 (FR-005 through FR-008): FAB only visible on dashboard page
const ConditionalChatPanel = dynamic(() => import("@/components/chat/conditional-chat-panel").then(m => ({ default: m.ConditionalChatPanel })), {
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
        {/* T044: Responsive positioning for toasts - top-center on mobile, bottom-right on desktop */}
        <Toaster position="bottom-right" richColors closeButton gap={8} expand={false} toastOptions={{
          duration: 3000,
          classNames: {
            // Mobile-responsive positioning
            toast: "mobile:max-w-[calc(100vw-2rem)]",
          },
        }} />
        <AdBlockWarning />
        {/* Phase III: AI Chatbot */}
        <ChatProvider>
          <ConditionalChatPanel />
        </ChatProvider>
      </ThemeProvider>
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}
