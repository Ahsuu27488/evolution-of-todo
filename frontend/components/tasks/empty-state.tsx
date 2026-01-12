/** Empty State Component with Deep Space Glassmorphism.
 *
 * Per spec.md US4 edge case: "when a user has no tasks, the dashboard displays
 * an empty state with a call-to-action to create the first task, using the
 * glassmorphism style."
 *
 * Per spec.md FR-037: glassmorphism visual design with backdrop-blur effects
 */

"use client"

import { motion } from "framer-motion"
import { ClipboardList, Sparkles } from "lucide-react"
import { TaskForm } from "./task-form"
import { fadeInUp } from "@/lib/animations"

export function EmptyState() {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      {/* Icon with glow effect */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
        className="relative mb-6"
      >
        <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
        <div className="glass relative rounded-full p-6">
          <ClipboardList className="h-10 w-10 text-primary" />
        </div>
      </motion.div>

      {/* Title */}
      <motion.h3
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-xl font-semibold mb-2"
      >
        No tasks yet
      </motion.h3>

      {/* Description */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-muted-foreground mb-6 max-w-sm"
      >
        Get started by creating your first task. Stay organized and track your
        progress.
      </motion.p>

      {/* CTA Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <TaskForm />
      </motion.div>

      {/* Decorative elements */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        transition={{ delay: 0.6, duration: 1 }}
        className="mt-12 flex items-center gap-2 text-xs text-muted-foreground"
      >
        <Sparkles className="h-3 w-3" />
        <span>Tip: You can add due dates, tags, and recurrence patterns</span>
      </motion.div>
    </motion.div>
  )
}
