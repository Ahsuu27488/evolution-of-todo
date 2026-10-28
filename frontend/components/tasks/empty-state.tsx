/** Empty states for the task list.
 *
 * - "first": no tasks at all. A small drawn orbit (the orrery's motif, no 3D) and the add button.
 * - "filtered": tasks exist but none match the search or filters; offers to clear them.
 */

"use client"

import { motion } from "framer-motion"
import { SearchX } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TaskForm } from "./task-form"
import { fadeInUp } from "@/lib/animations"

interface EmptyStateProps {
  variant?: "first" | "filtered"
  onClearFilters?: () => void
}

function OrbitMark() {
  return (
    <div aria-hidden className="relative mb-6 size-24">
      <div className="absolute inset-0 rounded-full border border-dashed border-foreground/15" />
      <div className="absolute inset-4 rounded-full border border-foreground/12" />
      <div className="absolute top-1/2 left-1/2 size-5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary" />
      <div className="absolute top-[18%] right-[10%] size-2.5 rounded-full bg-secondary" />
      <div className="absolute bottom-[20%] left-[18%] size-2 rounded-full bg-muted-foreground/50" />
    </div>
  )
}

export function EmptyState({ variant = "first", onClearFilters }: EmptyStateProps) {
  if (variant === "filtered") {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="surface flex flex-col items-center rounded-[var(--radius-2xl)] px-6 py-12 text-center"
      >
        <div className="mb-4 grid size-12 place-items-center rounded-full bg-muted text-muted-foreground">
          <SearchX className="size-5" aria-hidden />
        </div>
        <h2 className="font-display text-lg font-semibold">No tasks match</h2>
        <p className="mt-1 max-w-xs text-sm text-muted-foreground">
          Try another word, or clear the search and filters to see everything.
        </p>
        {onClearFilters && (
          <Button variant="outline" className="mt-5 rounded-full" onClick={onClearFilters}>
            Clear search and filters
          </Button>
        )}
      </motion.div>
    )
  }

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="surface flex flex-col items-center rounded-[var(--radius-2xl)] px-6 py-14 text-center"
    >
      <OrbitMark />
      <h2 className="font-display text-xl font-semibold">Nothing in orbit yet</h2>
      <p className="mt-1.5 mb-6 max-w-sm text-sm text-muted-foreground">
        Add your first task, or ask Kairos to plan your day. Tasks with a due date take their place on
        your orbits.
      </p>
      <TaskForm />
    </motion.div>
  )
}
