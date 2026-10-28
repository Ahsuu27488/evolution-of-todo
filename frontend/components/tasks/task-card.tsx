/** Task card: solid surface, priority as a slim left edge, completion with confetti.
 *
 * Per spec.md:
 * - FR-039: micro-animations for state transitions (slide-in, settle, fade)
 * - FR-040: confetti particle effect on task completion
 * - T097-T099: AI task summarization with regenerate button
 *
 * Acceptance Scenarios (US4):
 * - Given a user with an incomplete task, When they click the completion checkbox,
 *   Then the task strikes through with animation and confetti particles burst
 * - Given a user with a completed task, When they click the completion checkbox again,
 *   Then the task reverts to incomplete status with reverse animation
 */

"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { toast } from "sonner"
import { Check, Calendar, Repeat2, Sparkles, Loader2, RefreshCw } from "lucide-react"
import { format, isToday, isTomorrow, isYesterday, differenceInCalendarDays } from "date-fns"
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
  HIGH: "border-l-destructive",
  MEDIUM: "border-l-primary",
  LOW: "border-l-muted-foreground/40",
}

/** "Today 10:00", "Tomorrow", "Fri 30 Oct", "Overdue: Mon 26 Oct" */
function formatDue(date: Date, overdue: boolean): string {
  const hasTime = date.getHours() !== 0 || date.getMinutes() !== 0
  const time = hasTime ? ` ${format(date, "HH:mm")}` : ""
  let day: string
  if (isToday(date)) day = "Today"
  else if (isTomorrow(date)) day = "Tomorrow"
  else if (isYesterday(date)) day = "Yesterday"
  else if (Math.abs(differenceInCalendarDays(date, new Date())) < 7) day = format(date, "EEEE")
  else day = format(date, "EEE d MMM")
  return `${overdue ? "Overdue: " : ""}${day}${time}`
}

const priorityLabels = {
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
}

const priorityBadgeColors = {
  HIGH: "bg-destructive/15 text-destructive border-transparent",
  MEDIUM: "bg-primary/15 text-primary border-transparent",
  LOW: "bg-muted text-muted-foreground border-transparent",
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
        animate={optimisticCompleted ? "settle" : "normal"}
        className="transition-all duration-300"
      >
        <Card
          className={cn(
            // Solid content surface; priority shows as a slim left edge
            "surface gap-0 py-0 rounded-[var(--radius-xl)] border-l-[3px]",
            "transition-[transform,border-color,opacity] duration-200 ease-[var(--ease-out)] hover:-translate-y-px hover:border-foreground/15",
            priorityColors[task.priority],
            isOverdue && "border-l-destructive",
            optimisticCompleted && "opacity-60"
          )}
        >
          <CardContent className="flex items-start gap-3 px-4 py-3.5 sm:gap-4">
            {/* Completion checkbox */}
            <motion.div
              className="pt-0.5 sm:pt-1"
              animate={optimisticCompleted ? { scale: [1, 1.2, 1] } : { scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Checkbox
                checked={optimisticCompleted}
                onCheckedChange={handleToggleComplete}
                disabled={isUpdating}
                className="size-5"
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
                        <Sparkles className="h-3.5 w-3.5 text-primary" />
                        <span className="text-xs font-medium text-primary">AI summary</span>
                        {/* T098: Regenerate button */}
                        <button
                          type="button"
                          onClick={handleRegenerateSummary}
                          disabled={isRegeneratingSummary}
                          className="relative grid size-7 place-items-center rounded-full text-primary/70 outline-none transition-[opacity,background-color,color] after:absolute after:-inset-1.5 hover:bg-accent hover:text-primary focus-visible:opacity-100 focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-50 sm:opacity-0 sm:group-hover:opacity-100 [@media(hover:none)]:opacity-100"
                          aria-label="Regenerate summary"
                          title="Regenerate summary"
                        >
                          {isRegeneratingSummary ? (
                            <Loader2 className="size-3.5 animate-spin" aria-hidden />
                          ) : (
                            <RefreshCw className="size-3.5" aria-hidden />
                          )}
                        </button>
                      </div>

                      {/* Summary text */}
                      <p
                        className={cn(
                          "text-xs text-muted-foreground leading-relaxed p-2.5 rounded-lg border",
                          "bg-primary/6 border-primary/18",
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
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {task.tags.map((tag, idx) => (
                    <motion.span
                      key={idx}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 + idx * 0.05 }}
                      className="inline-flex items-center gap-1.5 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                    >
                      <span className="size-1.5 rounded-full" style={{ backgroundColor: tag.color }} aria-hidden />
                      {tag.name}
                    </motion.span>
                  ))}
                </div>
              )}

              {/* Due date */}
              {dueDate && (
                <div
                  className={cn(
                    "flex items-center gap-1.5 text-xs mt-2 tabular-nums transition-colors",
                    isOverdue ? "text-destructive" : "text-muted-foreground"
                  )}
                >
                  <Calendar className="h-3.5 w-3.5" />
                  <time dateTime={task.due_date ?? undefined}>{formatDue(dueDate, Boolean(isOverdue))}</time>
                </div>
              )}

              {/* Recurrence indicator */}
              {task.recurrence_pattern && (
                <div
                  className={cn(
                    "flex items-center gap-1.5 text-xs mt-1.5",
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
