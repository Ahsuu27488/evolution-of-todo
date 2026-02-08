/** Task Card Component with Deep Space Glassmorphism.
 *
 * Per spec.md:
 * - FR-037: glassmorphism visual design with backdrop-blur effects
 * - FR-039: micro-animations for state transitions (slide-in, glow, fade)
 * - FR-040: confetti particle effect on task completion
 * - T097-T099: AI task summarization with regenerate button
 *
 * Acceptance Scenarios (US4):
 * - Given a user with an incomplete task, When they click the completion checkbox,
 *   Then the task glows cyan, strikes through with animation, and confetti particles burst
 * - Given a user with a completed task, When they click the completion checkbox again,
 *   Then the task reverts to incomplete status with reverse animation
 */

"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { Check, Calendar, Tag, Repeat2, Sparkles, Loader2, RefreshCw } from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"

import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { TaskActions } from "./task-actions"
import { toggleTaskComplete } from "@/app/actions/tasks"
import { api } from "@/lib/api-client"
import { taskCompletionConfetti } from "@/components/confetti"
import { taskCard, taskComplete } from "@/lib/animations"
import { useTaskEventStore, selectHasRecentComplete } from "@/lib/stores/task-events"
import type { Task } from "@/types/task"

interface TaskCardProps {
  task: Task
  index?: number
}

const priorityColors = {
  HIGH: "border-destructive/60 shadow-[inset_3px_0_8px_-2px_rgba(239,68,68,0.35),0_0_20px_rgba(239,68,68,0.25)]",
  MEDIUM: "border-secondary/60 shadow-[inset_3px_0_8px_-2px_rgba(168,85,247,0.35),0_0_20px_rgba(168,85,247,0.25)]",
  LOW: "border-muted-foreground/40",
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
  const [isUpdating, setIsUpdating] = useState(false)
  const [optimisticCompleted, setOptimisticCompleted] = useState(task.completed)
  const [isRegeneratingSummary, setIsRegeneratingSummary] = useState(false)  // T098
  const queryClient = useQueryClient()

  // Phase 1 T013: Listen for AI-triggered task completions
  const lastMutation = useTaskEventStore((state) => state.lastMutation)
  const hasRecentComplete = useTaskEventStore(selectHasRecentComplete)

  // Trigger celebration when AI completes this specific task
  useEffect(() => {
    if (
      hasRecentComplete &&
      lastMutation &&
      lastMutation.type === "complete" &&
      lastMutation.taskId === task.id &&
      !task.completed && // Was incomplete before
      optimisticCompleted // Now completed (via cache update)
    ) {
      taskCompletionConfetti()
    }
  }, [hasRecentComplete, lastMutation, task.id, task.completed, optimisticCompleted])

  // Update local state when task prop changes (from cache updates)
  useEffect(() => {
    setOptimisticCompleted(task.completed)
  }, [task.completed])

  async function handleToggleComplete() {
    if (isUpdating) return

    const newCompleted = !optimisticCompleted

    // Trigger confetti on completion (not on uncheck)
    if (newCompleted) {
      taskCompletionConfetti()
    }

    // Optimistic update
    setOptimisticCompleted(newCompleted)
    setIsUpdating(true)

    try {
      const result = await toggleTaskComplete(task.id)
      if (!result.success) {
        // Rollback on error
        setOptimisticCompleted(task.completed)
        toast.error(result.error?.message || "Failed to update task")
      } else {
        // Invalidate TanStack Query cache to refetch tasks
        queryClient.invalidateQueries({ queryKey: ["tasks"] })
      }
    } catch {
      // Rollback on error
      setOptimisticCompleted(task.completed)
      toast.error("Failed to update task")
    } finally {
      setIsUpdating(false)
    }
  }

  // T098: Handle regenerate AI summary
  async function handleRegenerateSummary() {
    if (isRegeneratingSummary) return

    setIsRegeneratingSummary(true)

    try {
      const result = await api.regenerateTaskSummary(task.id)

      if (!result.success) {
        toast.error(result.error?.message || "Failed to regenerate summary")
        return
      }

      // Invalidate queries to get updated task
      queryClient.invalidateQueries({ queryKey: ["tasks"] })

      toast.success("Summary regenerated successfully")
    } catch (error) {
      console.error("Failed to regenerate summary:", error)
      toast.error("Failed to regenerate summary. Please try again.")
    } finally {
      setIsRegeneratingSummary(false)
    }
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
            // Priority border - thinner on mobile
            "border-l-2 sm:border-l-4",
            priorityColors[task.priority],
            // Overdue indicator - enhanced glow with inset
            isOverdue && "border-destructive shadow-[inset_3px_0_8px_-2px_rgba(239,68,68,0.4),0_0_25px_rgba(239,68,68,0.3)]",
            optimisticCompleted && "opacity-75"
          )}
        >
          <CardContent className="flex items-start gap-3 p-3 sm:gap-4 sm:p-4">
            {/* Checkbox with glow effect */}
            <motion.div
              className="pt-0.5 sm:pt-1"
              animate={optimisticCompleted ? { scale: [1, 1.2, 1] } : { scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Checkbox
                checked={optimisticCompleted}
                onCheckedChange={handleToggleComplete}
                disabled={isUpdating}
                className={cn(
                  "h-5 w-5 transition-all duration-300",
                  optimisticCompleted && "border-primary shadow-[inset_0_0_6px_rgba(0,245,255,0.4),0_0_12px_rgba(0,245,255,0.5)]"
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

              {/* T097: AI Summary display */}
              <AnimatePresence>
                {task.ai_summary && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="mt-3"
                  >
                    <div className="relative group">
                      {/* Summary label */}
                      <div className="flex items-center gap-1.5 mb-1.5">
                        <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                        <span className="text-xs font-medium text-cyan-400/90">AI Summary</span>
                        {/* T098: Regenerate button */}
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={handleRegenerateSummary}
                          disabled={isRegeneratingSummary}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-white/10 disabled:opacity-50"
                          title="Regenerate summary"
                        >
                          {isRegeneratingSummary ? (
                            <Loader2 className="h-3 w-3.5 text-cyan-400 animate-spin" />
                          ) : (
                            <RefreshCw className="h-3 w-3.5 text-cyan-400/70 hover:text-cyan-400" />
                          )}
                        </motion.button>
                      </div>

                      {/* Summary text */}
                      <p
                        className={cn(
                          "text-xs text-muted-foreground leading-relaxed p-2.5 rounded-lg border",
                          "bg-cyan-500/5 border-cyan-500/20",
                          optimisticCompleted && "line-through opacity-60"
                        )}
                      >
                        {task.ai_summary}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Tags */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
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
                    "flex items-center gap-2 text-xs mt-3 transition-colors",
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
                    "flex items-center gap-2 text-xs mt-2",
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
            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              <AnimatePresence mode="wait">
                {optimisticCompleted && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.5, x: -10 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.5, x: -10 }}
                    className="hidden sm:flex items-center gap-1 text-xs text-primary font-medium"
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
