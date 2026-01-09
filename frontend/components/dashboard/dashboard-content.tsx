"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { fadeInUp } from "@/lib/animations"
import { TaskForm } from "@/components/tasks/task-form"
import { TaskList } from "@/components/tasks/task-list"
import { Button } from "@/components/ui/button"
import type { Task } from "@/types/task"

interface DashboardContentProps {
  tasks: Task[]
  pendingCount: number
  completedCount: number
  isAuthenticated?: boolean
}

export function DashboardContent({
  tasks,
  pendingCount,
  completedCount,
  isAuthenticated = false
}: DashboardContentProps) {
  // Show login prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="mx-auto max-w-md text-center py-12"
      >
        <h2 className="text-2xl font-bold mb-4">Welcome to Todo App</h2>
        <p className="text-muted-foreground mb-6">
          Please sign in to manage your tasks.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <Button>Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button variant="outline">Sign Up</Button>
          </Link>
        </div>
      </motion.div>
    )
  }

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
          <h1 className="text-3xl font-bold bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
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
