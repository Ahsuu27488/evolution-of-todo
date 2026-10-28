/**
 * Task cards inside the Kairos chat.
 *
 * - TaskCard: a task with quick actions (complete, rename, delete), for panels that list tasks.
 * - InlineTaskCard: a compact chip embedded in a message.
 *
 * Both sit on the solid muted surface used by assistant messages (the chat panel is the glass
 * layer; nothing inside it is glass). Priority is a coloured dot, matching the dashboard.
 */

"use client"

import { motion } from "framer-motion"
import { Calendar, Check, Loader2, Pencil, Trash2, X } from "lucide-react"
import { useState } from "react"
import type { Task, Priority } from "@/types/task"
import { api } from "@/lib/api-client"
import { cn } from "@/lib/utils"
import { toast } from "sonner"

// =============================================================================
// Shared bits
// =============================================================================

interface TaskCardProps {
  task: Task
  onComplete?: (taskId: number) => void
  onDelete?: (taskId: number) => void
  onEdit?: (task: Task) => void
  compact?: boolean
}

const priorityStyle: Record<Priority, { label: string; dot: string; edge: string }> = {
  HIGH: { label: "High", dot: "bg-destructive", edge: "border-l-destructive" },
  MEDIUM: { label: "Medium", dot: "bg-primary", edge: "border-l-primary" },
  LOW: { label: "Low", dot: "bg-muted-foreground/60", edge: "border-l-muted-foreground/40" },
}

const iconButton =
  "relative grid size-8 place-items-center rounded-full text-muted-foreground outline-none transition-colors after:absolute after:-inset-1 hover:bg-accent hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-50"

function formatDue(dateStr: string | null, withTime: boolean) {
  if (!dateStr) return null
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
    ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}),
  }).format(new Date(dateStr))
}

// =============================================================================
// Task card
// =============================================================================

export function TaskCard({ task, onComplete, onDelete, onEdit, compact = false }: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState(task.title)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const priority = priorityStyle[task.priority]
  const dueDate = formatDue(task.due_date, true)

  const handleComplete = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    try {
      const result = await api.updateTask(task.id, { completed: !task.completed })
      if (result.success) {
        onComplete?.(task.id)
        toast.success(task.completed ? "Moved back to open" : "Task done")
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Couldn't update the task")
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDelete = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    try {
      const result = await api.deleteTask(task.id)
      if (result.success) {
        onDelete?.(task.id)
        toast.success("Task deleted")
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Couldn't delete the task")
    } finally {
      setIsProcessing(false)
      setConfirmDelete(false)
    }
  }

  const handleSaveEdit = async () => {
    if (!title.trim() || isProcessing) return
    setIsProcessing(true)
    try {
      const result = await api.updateTask(task.id, { title })
      if (result.success) {
        setIsEditing(false)
        setTitle(result.data.title)
        onEdit?.(result.data)
        toast.success("Task renamed")
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Couldn't rename the task")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
      aria-busy={isProcessing}
      className={cn(
        "group relative rounded-[var(--radius-lg)] border border-border border-l-[3px] bg-muted",
        priority.edge,
        compact ? "p-3" : "p-3.5"
      )}
    >
      <div className="flex items-start gap-3">
        <button
          type="button"
          role="checkbox"
          aria-checked={task.completed}
          aria-label={task.completed ? "Mark as not done" : "Mark as done"}
          onClick={handleComplete}
          disabled={isProcessing}
          className={cn(
            "relative mt-0.5 grid size-5 shrink-0 place-items-center rounded-[6px] border-[1.5px] outline-none transition-colors after:absolute after:-inset-2.5",
            "focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-50",
            task.completed ? "border-primary bg-primary text-primary-foreground" : "border-foreground/30 hover:border-primary"
          )}
        >
          {isProcessing ? (
            <Loader2 className="size-3 animate-spin" aria-hidden />
          ) : (
            task.completed && <Check className="size-3" strokeWidth={3} aria-hidden />
          )}
        </button>

        <div className="min-w-0 flex-1">
          {isEditing ? (
            <div className="flex items-center gap-1">
              <input
                type="text"
                value={title}
                aria-label="Task title"
                onChange={(e) => setTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSaveEdit()
                  if (e.key === "Escape") {
                    setIsEditing(false)
                    setTitle(task.title)
                  }
                }}
                className="h-9 min-w-0 flex-1 rounded-[var(--radius-md)] border border-input bg-card px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50"
                autoFocus
              />
              <button type="button" onClick={handleSaveEdit} disabled={isProcessing || !title.trim()} className={cn(iconButton, "text-success")} aria-label="Save title">
                <Check className="size-4" aria-hidden />
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false)
                  setTitle(task.title)
                }}
                className={iconButton}
                aria-label="Cancel rename"
              >
                <X className="size-4" aria-hidden />
              </button>
            </div>
          ) : (
            <div className="flex items-start justify-between gap-2">
              <p className={cn("text-sm leading-snug break-words", task.completed && "text-muted-foreground line-through")}>
                {task.title}
              </p>
              <div className="-mt-1 -mr-1 flex items-center opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100">
                {confirmDelete ? (
                  <>
                    <button
                      type="button"
                      onClick={handleDelete}
                      disabled={isProcessing}
                      className="h-8 rounded-full bg-destructive px-3 text-xs font-medium text-destructive-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
                    >
                      Delete
                    </button>
                    <button type="button" onClick={() => setConfirmDelete(false)} className={iconButton} aria-label="Keep task">
                      <X className="size-4" aria-hidden />
                    </button>
                  </>
                ) : (
                  <>
                    <button type="button" onClick={() => setIsEditing(true)} className={iconButton} aria-label="Rename task">
                      <Pencil className="size-3.5" aria-hidden />
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmDelete(true)}
                      disabled={isProcessing}
                      className={cn(iconButton, "hover:bg-destructive/12 hover:text-destructive")}
                      aria-label="Delete task"
                    >
                      <Trash2 className="size-3.5" aria-hidden />
                    </button>
                  </>
                )}
              </div>
            </div>
          )}

          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <span className={cn("size-2 rounded-full", priority.dot)} aria-hidden />
              {priority.label}
            </span>
            {dueDate && (
              <span className="inline-flex items-center gap-1 tabular-nums">
                <Calendar className="size-3" aria-hidden />
                {dueDate}
              </span>
            )}
            {task.tags?.slice(0, 3).map((tag) => (
              <span key={tag.name} className="inline-flex items-center gap-1.5 rounded-full bg-card px-2 py-0.5">
                <span className="size-1.5 rounded-full" style={{ backgroundColor: tag.color }} aria-hidden />
                {tag.name}
              </span>
            ))}
            {task.tags && task.tags.length > 3 && <span>+{task.tags.length - 3}</span>}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// =============================================================================
// Inline Task Card (for message content)
// =============================================================================

interface InlineTaskCardProps {
  task: Task
  onAction?: (action: "complete" | "delete" | "edit", task: Task) => void
}

/** Compact chip for a task mentioned inside a chat message */
export function InlineTaskCard({ task, onAction }: InlineTaskCardProps) {
  const priority = priorityStyle[task.priority]
  const dueDate = formatDue(task.due_date, false)

  return (
    <div className="inline-flex max-w-full items-center gap-2.5 rounded-full border border-border bg-card py-1 pr-1 pl-3 align-middle text-sm">
      <span className={cn("size-2 shrink-0 rounded-full", priority.dot)} aria-label={`${priority.label} priority`} />
      <span className={cn("min-w-0 truncate", task.completed && "text-muted-foreground line-through")}>{task.title}</span>
      {dueDate && <span className="shrink-0 text-xs text-muted-foreground tabular-nums">{dueDate}</span>}

      {onAction && (
        <span className="flex shrink-0 items-center border-l border-border pl-1">
          <button
            type="button"
            onClick={() => onAction("complete", task)}
            className={cn(iconButton, "hover:text-success")}
            aria-label={task.completed ? `Mark "${task.title}" as not done` : `Mark "${task.title}" as done`}
          >
            <Check className="size-3.5" aria-hidden />
          </button>
          <button
            type="button"
            onClick={() => onAction("delete", task)}
            className={cn(iconButton, "hover:bg-destructive/12 hover:text-destructive")}
            aria-label={`Delete "${task.title}"`}
          >
            <Trash2 className="size-3.5" aria-hidden />
          </button>
        </span>
      )}
    </div>
  )
}
