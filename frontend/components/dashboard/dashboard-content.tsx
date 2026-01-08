"use client"

import { motion } from "framer-motion"
import { fadeInUp } from "@/lib/animations"
import { TaskForm } from "@/components/tasks/task-form"
import { TaskList } from "@/components/tasks/task-list"
import type { Task } from "@/types/task"

interface DashboardContentProps {
  tasks: Task[]
  pendingCount: number
  completedCount: number
}

export function DashboardContent({ tasks, pendingCount, completedCount }: DashboardContentProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="mx-auto max-w-2xl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
            My Tasks
          </h1>
          <p className="text-muted-foreground mt-1">
            {tasks.length === 0
              ? "No tasks yet. Create your first task!"
              : `${pendingCount} pending, ${completedCount} completed`}
          </p>
        </div>

        {/* Floating Action Button */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="shrink-0"
        >
          <TaskForm />
        </motion.div>
      </div>

      {/* Task List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <TaskList tasks={tasks} />
      </motion.div>
    </motion.div>
  )
}
