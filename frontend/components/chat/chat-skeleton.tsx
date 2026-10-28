/**
 * Chat Skeleton - Loading placeholders shaped like the Kairos chat messages.
 *
 * Assistant rows: avatar circle + muted bubble (left). User rows: gold-tinted bubble (right).
 * Pulse only (no shimmer sweep); still for reduced motion.
 *
 * Per User Story 5 (FR-020 through FR-023): Loading skeleton states.
 */

"use client"

import { motion } from "framer-motion"
import { Skeleton } from "@/components/ui/skeleton"

export interface ChatSkeletonProps {
  /** Number of skeleton items to display */
  count?: number
  /** Variant type - affects layout */
  variant?: "user" | "assistant" | "mixed"
}

const fade = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

function UserMessageSkeleton({ width }: { width: string }) {
  return (
    <motion.div {...fade} className="flex justify-end">
      <div className="h-11 animate-pulse rounded-2xl rounded-tr-sm bg-primary/20 motion-reduce:animate-none" style={{ width }} />
    </motion.div>
  )
}

function AssistantMessageSkeleton({ width }: { width: string }) {
  return (
    <motion.div {...fade} className="flex gap-3">
      <Skeleton className="size-8 shrink-0 rounded-full" />
      <div className="flex flex-col gap-1.5" style={{ width }}>
        <div className="h-16 animate-pulse rounded-2xl rounded-tl-sm bg-foreground/8 motion-reduce:animate-none" />
        <Skeleton className="h-2.5 w-14" />
      </div>
    </motion.div>
  )
}

const widths = ["70%", "45%", "60%", "38%", "66%", "50%"]

export function ChatSkeleton({ count = 3, variant = "mixed" }: ChatSkeletonProps) {
  const rows = Array.from({ length: count }, (_, i) => {
    if (variant === "user") return "user"
    if (variant === "assistant") return "assistant"
    return i % 2 === 0 ? "assistant" : "user"
  })

  return (
    <div className="space-y-4 py-4" role="status" aria-label="Loading conversation">
      {rows.map((type, index) =>
        type === "user" ? (
          <UserMessageSkeleton key={index} width={widths[index % widths.length]} />
        ) : (
          <AssistantMessageSkeleton key={index} width={widths[index % widths.length]} />
        )
      )}
    </div>
  )
}

/** Placeholder for a conversation in the history list */
export function ConversationItemSkeleton() {
  return (
    <motion.div {...fade} className="flex min-w-[200px] items-center gap-2.5 rounded-[var(--radius-md)] p-2">
      <Skeleton className="size-6 shrink-0 rounded-full" />
      <Skeleton className="h-3 w-[70%]" />
    </motion.div>
  )
}

/** Small placeholder while a reply starts streaming */
export function StreamingMessageSkeleton() {
  return (
    <motion.div {...fade} className="flex gap-3">
      <Skeleton className="size-8 shrink-0 rounded-full" />
      <div className="h-8 w-16 animate-pulse rounded-2xl rounded-tl-sm bg-foreground/8 motion-reduce:animate-none" />
    </motion.div>
  )
}
