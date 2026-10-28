/** Task List Component with Staggered Animations.
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
  /** True when the user has tasks but the search or filters hide them all */
  isFiltered?: boolean
  onClearFilters?: () => void
}

export function TaskList({ tasks, isFiltered = false, onClearFilters }: TaskListProps) {
  if (tasks.length === 0) {
    return <EmptyState variant={isFiltered ? "filtered" : "first"} onClearFilters={onClearFilters} />
  }

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-3"
    >
      {/* Cards are direct children so AnimatePresence can play their exit */}
      <AnimatePresence mode="popLayout">
        {tasks.map((task, index) => (
          <TaskCard key={task.id} task={task} index={index} />
        ))}
      </AnimatePresence>
    </motion.div>
  )
}
