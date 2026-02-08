/**
 * Chat Skeleton - Loading placeholder for chat messages.
 *
 * Features:
 * - YouTube-style shimmer animation
 * - Matches message bubble design
 * - Smooth fade-out transition when content loads
 * - Configurable count and variant (user/assistant)
 *
 * Per User Story 5 (FR-020 through FR-023): Loading skeleton states.
 */

"use client"

import { motion } from "framer-motion"

// =============================================================================
// Types
// =============================================================================

export interface ChatSkeletonProps {
  /** Number of skeleton items to display */
  count?: number
  /** Variant type - affects layout */
  variant?: "user" | "assistant" | "mixed"
}

// =============================================================================
// Animation Variants
// =============================================================================

const shimmerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
}

// =============================================================================
// Shimmer Animation Component
// =============================================================================

/**
 * Shimmer effect using CSS gradient animation.
 * YouTube-style loading pattern.
 */
function Shimmer({ className }: { className?: string }) {
  return (
    <div
      className={`shimmer ${className || ""}`}
      style={{
        background: "linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%)",
        backgroundSize: "200% 100%",
        animation: "shimmer 1.5s infinite",
      }}
    />
  )
}

// =============================================================================
// Skeleton Item Components
// =============================================================================

/**
 * Single user message skeleton.
 * Matches the user message bubble design.
 */
function UserMessageSkeleton() {
  return (
    <motion.div
      variants={shimmerVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="flex gap-3 flex-row-reverse"
    >
      {/* Avatar */}
      <div
        className="flex-shrink-0 w-8 h-8 rounded-full"
        style={{
          background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 180, 216, 0.2) 100%)",
        }}
      />

      {/* Message bubble */}
      <div className="flex flex-col items-end max-w-[80%]">
        <div
          className="px-4 py-2.5 rounded-2xl rounded-tr-sm"
          style={{
            background: "linear-gradient(135deg, rgba(0, 245, 255, 0.2) 0%, rgba(0, 180, 216, 0.2) 100%)",
            minWidth: "120px",
            height: "44px",
          }}
        >
          <Shimmer className="w-full h-full rounded-xl" />
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Single assistant message skeleton.
 * Matches the assistant message bubble design.
 */
function AssistantMessageSkeleton() {
  return (
    <motion.div
      variants={shimmerVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={{ delay: 0.1 }}
      className="flex gap-3"
    >
      {/* Avatar */}
      <div
        className="flex-shrink-0 w-8 h-8 rounded-full"
        style={{
          background: "linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)",
        }}
      />

      {/* Message bubble */}
      <div className="flex flex-col items-start max-w-[80%]">
        <div
          className="px-4 py-2.5 rounded-2xl rounded-tl-sm"
          style={{
            background: "rgba(255, 255, 255, 0.05)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            minWidth: "160px",
            height: "44px",
          }}
        >
          <Shimmer className="w-full h-full rounded-xl" />
        </div>

        {/* Timestamp skeleton */}
        <div
          className="mt-1 px-1 rounded"
          style={{ width: "60px", height: "12px" }}
        >
          <Shimmer className="w-full h-full rounded" />
        </div>
      </div>
    </motion.div>
  )
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Chat Skeleton component for loading state.
 *
 * Displays placeholder message bubbles while conversation loads.
 *
 * @example
 * ```tsx
 * <ChatSkeleton count={3} variant="mixed" />
 * ```
 */
export function ChatSkeleton({
  count = 3,
  variant = "mixed"
}: ChatSkeletonProps) {
  // Generate skeleton items based on variant
  const skeletons = Array.from({ length: count }, (_, i) => {
    if (variant === "user") return "user"
    if (variant === "assistant") return "assistant"
    // Mixed pattern: alternate user/assistant
    return i % 2 === 0 ? "assistant" : "user"
  })

  return (
    <>
      {/* CSS animation keyframes */}
      <style jsx>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>

      <div className="space-y-4 py-4">
        {skeletons.map((type, index) => (
          <div key={`skeleton-${index}`}>
            {type === "user" ? <UserMessageSkeleton /> : <AssistantMessageSkeleton />}
          </div>
        ))}
      </div>
    </>
  )
}

/**
 * Compact skeleton for conversation history items.
 * Used in the conversation history sidebar.
 */
export function ConversationItemSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex items-center gap-2 p-2 rounded-lg"
      style={{
        background: "rgba(255, 255, 255, 0.02)",
        minWidth: "200px",
      }}
    >
      {/* Avatar placeholder */}
      <div
        className="w-6 h-6 rounded-full flex-shrink-0"
        style={{
          background: "rgba(255, 255, 255, 0.1)",
        }}
      >
        <Shimmer className="w-full h-full rounded-full" />
      </div>

      {/* Title placeholder */}
      <div className="flex-1">
        <div
          className="h-3 rounded"
          style={{
            width: "70%",
            background: "rgba(255, 255, 255, 0.05)",
          }}
        >
          <Shimmer className="w-full h-full rounded" />
        </div>
      </div>
    </motion.div>
  )
}

/**
 * Inline loading indicator for message stream.
 * Small, compact skeleton for streaming messages.
 */
export function StreamingMessageSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex gap-3"
    >
      {/* Avatar */}
      <div
        className="flex-shrink-0 w-8 h-8 rounded-full"
        style={{
          background: "linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)",
        }}
      />

      {/* Message bubble */}
      <div className="flex flex-col items-start max-w-[80%]">
        <div
          className="px-4 py-2.5 rounded-2xl rounded-tl-sm"
          style={{
            background: "rgba(255, 255, 255, 0.05)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            minWidth: "60px",
            height: "32px",
          }}
        >
          <Shimmer className="w-full h-full rounded-xl" />
        </div>
      </div>
    </motion.div>
  )
}
