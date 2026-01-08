/** Task List Component with Staggered Animations.
 *
 * Per spec.md FR-039: micro-animations for state transitions (slide-in, glow, fade)
 *
 * Displays tasks with staggered entrance animations and supports
 * smooth reordering when items are added or removed.
 */

"use client"

import { motion, AnimatePresence } from "framer-motion"
import { TaskCard } from "./task-card"
import { EmptyState } from "./empty-state"
import { staggerContainer } from "@/lib/animations"
import type { Task } from "@/types/task"

interface TaskListProps {
  tasks: Task[]
}

export function TaskList({ tasks }: TaskListProps) {
  if (tasks.length === 0) {
    return <EmptyState />
  }

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-3"
    >
      <AnimatePresence mode="popLayout">
        {tasks.map((task, index) => (
          <TaskCard key={task.id} task={task} index={index} />
        ))}
      </AnimatePresence>
    </motion.div>
  )
}
