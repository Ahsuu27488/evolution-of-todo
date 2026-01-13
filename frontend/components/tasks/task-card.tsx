/** Task Card Component with Deep Space Glassmorphism.
 *
 * Per spec.md:
 * - FR-037: glassmorphism visual design with backdrop-blur effects
 * - FR-039: micro-animations for state transitions (slide-in, glow, fade)
 * - FR-040: confetti particle effect on task completion
 *
 * Acceptance Scenarios (US4):
 * - Given a user with an incomplete task, When they click the completion checkbox,
 *   Then the task glows cyan, strikes through with animation, and confetti particles burst
 * - Given a user with a completed task, When they click the completion checkbox again,
 *   Then the task reverts to incomplete status with reverse animation
 */

"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Check, Calendar, Tag, Repeat2 } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { TaskActions } from "./task-actions"
import { useToggleTaskComplete } from "@/lib/hooks/use-task-mutations"
import { taskCompletionConfetti } from "@/components/confetti"
import { taskCard, taskComplete } from "@/lib/animations"
import type { Task } from "@/types/task"

interface TaskCardProps {
  task: Task
  index?: number
}

const priorityColors = {
  HIGH: "border-destructive/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]",
  MEDIUM: "border-secondary/50 shadow-[0_0_15px_rgba(168,85,247,0.2)]",
  LOW: "border-muted-foreground/30",
}

const priorityLabels = {
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
}

const priorityBadgeColors = {
  HIGH: "bg-destructive/20 text-destructive border-destructive/50",
  MEDIUM: "bg-secondary/20 text-secondary border-secondary/50",
  LOW: "bg-muted/50 text-muted-foreground border-muted-foreground/30",
}

export function TaskCard({ task, index = 0 }: TaskCardProps) {
  const [optimisticCompleted, setOptimisticCompleted] = useState(task.completed)

  const toggleMutation = useToggleTaskComplete()
  const isUpdating = toggleMutation.isPending

  function handleToggleComplete() {
    if (isUpdating) return

    const newCompleted = !optimisticCompleted

    // Trigger confetti on completion (not on uncheck)
    if (newCompleted) {
      taskCompletionConfetti()
    }

    // Optimistic update
    setOptimisticCompleted(newCompleted)

    toggleMutation.mutate(task.id, {
      onError: () => {
        // Rollback on error
        setOptimisticCompleted(task.completed)
      }
    })
  }

  const dueDate = task.due_date ? new Date(task.due_date) : null
  const isOverdue = dueDate && dueDate < new Date() && !optimisticCompleted

  return (
    <motion.div
      variants={taskCard}
      initial="hidden"
      animate="visible"
      exit="hidden"
      transition={{ delay: index * 0.05 }}
      className="will-animate"
    >
      <motion.div
        variants={taskComplete}
        animate={optimisticCompleted ? "glow" : "normal"}
        className="transition-all duration-300"
      >
        <Card
          className={cn(
            // Glassmorphism effect
            "glass transition-all duration-300 hover:scale-[1.01]",
            // Priority border
            "border-l-4",
            priorityColors[task.priority],
            // Overdue indicator
            isOverdue && "border-destructive shadow-[0_0_20px_rgba(239,68,68,0.3)]",
            optimisticCompleted && "opacity-75"
          )}
        >
          <CardContent className="flex items-start gap-4 p-4">
            {/* Checkbox with glow effect */}
            <motion.div
              className="pt-1"
              animate={optimisticCompleted ? { scale: [1, 1.2, 1] } : { scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Checkbox
                checked={optimisticCompleted}
                onCheckedChange={handleToggleComplete}
                disabled={isUpdating}
                className={cn(
                  "h-5 w-5 transition-all duration-300",
                  optimisticCompleted && "border-primary shadow-[0_0_10px_rgba(0,245,255,0.5)]"
                )}
                aria-label={optimisticCompleted ? "Mark as incomplete" : "Mark as complete"}
              />
            </motion.div>

            {/* Task content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start gap-2">
                <h3
                  className={cn(
                    "font-medium leading-snug transition-all duration-300",
                    optimisticCompleted && "line-through text-muted-foreground"
                  )}
                >
                  {task.title}
                </h3>

                {/* Priority badge */}
                <Badge
                  variant="outline"
                  className={cn("text-xs shrink-0", priorityBadgeColors[task.priority])}
                >
                  {priorityLabels[task.priority]}
                </Badge>
              </div>

              {/* Description */}
              {task.description && (
                <p
                  className={cn(
                    "text-sm text-muted-foreground mt-2 line-clamp-2 transition-all duration-300",
                    optimisticCompleted && "line-through opacity-60"
                  )}
                >
                  {task.description}
                </p>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-3">
                  {task.tags.map((tag, idx) => (
                    <motion.span
                      key={idx}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 + idx * 0.05 }}
                      className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
                      style={{
                        backgroundColor: `${tag.color}20`,
                        color: tag.color,
                        border: `1px solid ${tag.color}40`,
                      }}
                    >
                      <Tag className="h-3 w-3" />
                      {tag.name}
                    </motion.span>
                  ))}
                </div>
              )}

              {/* Due date */}
              {dueDate && (
                <div
                  className={cn(
                    "flex items-center gap-1.5 text-xs mt-3 transition-colors",
                    isOverdue
                      ? "text-destructive"
                      : optimisticCompleted
                        ? "text-muted-foreground"
                        : "text-muted-foreground"
                  )}
                >
                  <Calendar className="h-3.5 w-3.5" />
                  <span>
                    {isOverdue && "Overdue: "}
                    {dueDate.toLocaleDateString()}
                  </span>
                </div>
              )}

              {/* Recurrence indicator */}
              {task.recurrence_pattern && (
                <div
                  className={cn(
                    "flex items-center gap-1.5 text-xs mt-2",
                    "text-secondary"
                  )}
                  title={`Repeats: ${task.recurrence_pattern.toLowerCase()}`}
                >
                  <Repeat2 className="h-3.5 w-3.5" />
                  <span className="capitalize">{task.recurrence_pattern.toLowerCase()}</span>
                </div>
              )}
            </div>

            {/* Actions and completion indicator */}
            <div className="flex items-center gap-2">
              <AnimatePresence mode="wait">
                {optimisticCompleted && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5, x: -10 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.5, x: -10 }}
                    className="flex items-center gap-1 text-xs text-primary font-medium"
                  >
                    <Check className="h-4 w-4" />
                    Done
                  </motion.div>
                )}
              </AnimatePresence>
              <TaskActions task={task} />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
