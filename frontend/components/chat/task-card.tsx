/**
 * TaskCard - Display task in chat with quick actions.
 *
 * Features:
 * - Compact task display for chat context
 * - Quick actions: complete, delete, edit
 * - Priority badge colors
 * - Deep Space theme styling
 * - Glassmorphism effect
 *
 * Per spec.md T115, T116, T117.
 */

"use client"

import { motion } from "framer-motion"
import { Check, Trash2, Edit2, Calendar, Tag } from "lucide-react"
import { useState } from "react"
import type { Task, Priority } from "@/types/task"
import { api } from "@/lib/api-client"
import { toast } from "sonner"

// =============================================================================
// Types
// =============================================================================

interface TaskCardProps {
  task: Task
  onComplete?: (taskId: number) => void
  onDelete?: (taskId: number) => void
  onEdit?: (task: Task) => void
  compact?: boolean
}

interface EditingState {
  isEditing: boolean
  title: string
}

// =============================================================================
// Priority Styling
// =============================================================================

const priorityConfig: Record<
  Priority,
  { bg: string; border: string; text: string; glow: string }
> = {
  HIGH: {
    bg: "rgba(239, 68, 68, 0.15)",
    border: "rgba(239, 68, 68, 0.4)",
    text: "text-red-300",
    glow: "shadow-[0_0_15px_rgba(239,68,68,0.2)]",
  },
  MEDIUM: {
    bg: "rgba(251, 191, 36, 0.15)",
    border: "rgba(251, 191, 36, 0.4)",
    text: "text-yellow-300",
    glow: "shadow-[0_0_15px_rgba(251,191,36,0.2)]",
  },
  LOW: {
    bg: "rgba(34, 197, 94, 0.15)",
    border: "rgba(34, 197, 94, 0.4)",
    text: "text-green-300",
    glow: "shadow-[0_0_15px_rgba(34,197,94,0.2)]",
  },
}

// =============================================================================
// Component
// =============================================================================

export function TaskCard({ task, onComplete, onDelete, onEdit, compact = false }: TaskCardProps) {
  const [editing, setEditing] = useState<EditingState>({
    isEditing: false,
    title: task.title,
  })
  const [isProcessing, setIsProcessing] = useState(false)

  const priority = priorityConfig[task.priority]

  // Handle complete toggle
  const handleComplete = async () => {
    if (isProcessing) return
    setIsProcessing(true)

    try {
      const result = await api.updateTask(task.id, { completed: !task.completed })

      if (result.success) {
        onComplete?.(task.id)
        toast.success(task.completed ? "Task reinstated" : "Task completed!")
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Failed to update task")
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle delete
  const handleDelete = async () => {
    if (isProcessing) return

    // Confirm before delete
    if (!confirm("Are you sure you want to delete this task?")) return

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
      toast.error("Failed to delete task")
    } finally {
      setIsProcessing(false)
    }
  }

  // Handle edit save
  const handleSaveEdit = async () => {
    if (!editing.title.trim() || isProcessing) return

    setIsProcessing(true)

    try {
      const result = await api.updateTask(task.id, { title: editing.title })

      if (result.success) {
        setEditing({ isEditing: false, title: result.data.title })
        onEdit?.(result.data)
        toast.success("Task updated")
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Failed to update task")
    } finally {
      setIsProcessing(false)
    }
  }

  // Format due date
  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null
    const date = new Date(dateStr)
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    }).format(date)
  }

  const dueDate = formatDueDate(task.due_date)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`
        relative overflow-hidden rounded-xl border backdrop-blur-md
        transition-all duration-200 hover:scale-[1.01]
        ${compact ? "p-3" : "p-4"}
      `}
      style={{
        background: "rgba(20, 20, 26, 0.6)",
        borderColor: "rgba(255, 255, 255, 0.1)",
      }}
    >
      {/* Priority indicator bar */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1"
        style={{
          background:
            task.priority === "HIGH"
              ? "linear-gradient(180deg, #ef4444 0%, #dc2626 100%)"
              : task.priority === "MEDIUM"
                ? "linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%)"
                : "linear-gradient(180deg, #22c55e 0%, #16a34a 100%)",
        }}
      />

      <div className="flex items-start gap-3">
        {/* Complete checkbox */}
        <button
          onClick={handleComplete}
          disabled={isProcessing}
          className={`
            flex-shrink-0 w-5 h-5 rounded-md border-2 flex items-center justify-center
            transition-all duration-200 mt-0.5
            ${task.completed
              ? "bg-gradient-to-br from-cyan-400 to-cyan-500 border-cyan-400"
              : "border-white/30 hover:border-cyan-400 hover:bg-cyan-400/10"
            }
            ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          `}
          title={task.completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.completed && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <Check className="w-3 h-3 text-white" strokeWidth={3} />
            </motion.div>
          )}
        </button>

        {/* Task content */}
        <div className="flex-1 min-w-0">
          {editing.isEditing ? (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={editing.title}
                onChange={(e) => setEditing({ ...editing, title: e.target.value })}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSaveEdit()
                  if (e.key === "Escape") setEditing({ isEditing: false, title: task.title })
                }}
                className={`
                  flex-1 px-2 py-1 rounded bg-white/10 border border-white/20
                  text-sm text-white outline-none focus:border-cyan-400
                  ${task.completed ? "line-through opacity-60" : ""}
                `}
                autoFocus
              />
              <div className="flex gap-1">
                <button
                  onClick={handleSaveEdit}
                  disabled={isProcessing || !editing.title.trim()}
                  className="p-1 rounded hover:bg-green-500/20 text-green-400"
                  title="Save"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setEditing({ isEditing: false, title: task.title })}
                  className="p-1 rounded hover:bg-red-500/20 text-red-400"
                  title="Cancel"
                >
                  ✕
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-start justify-between gap-2">
                <p
                  className={`text-sm break-words ${
                    task.completed ? "line-through opacity-50" : ""
                  }`}
                  style={{
                    color: task.completed ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.9)",
                  }}
                >
                  {task.title}
                </p>

                {/* Quick actions */}
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => setEditing({ isEditing: true, title: task.title })}
                    className="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors"
                    title="Edit task"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={isProcessing}
                    className="p-1.5 rounded-lg hover:bg-red-500/20 text-white/50 hover:text-red-400 transition-colors"
                    title="Delete task"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Metadata: priority, due date, tags */}
              <div className="flex flex-wrap items-center gap-2 mt-2">
                {/* Priority badge */}
                <span
                  className={`
                    px-2 py-0.5 rounded-md text-xs font-medium border
                    ${priority.text}
                  `}
                  style={{
                    background: priority.bg,
                    borderColor: priority.border,
                  }}
                >
                  {task.priority}
                </span>

                {/* Due date */}
                {dueDate && (
                  <span className="flex items-center gap-1 text-xs text-white/50">
                    <Calendar className="w-3 h-3" />
                    <span>{dueDate}</span>
                  </span>
                )}

                {/* Tags */}
                {task.tags && task.tags.length > 0 && (
                  <div className="flex items-center gap-1">
                    {task.tags.slice(0, 2).map((tag) => (
                      <span
                        key={tag.name}
                        className="flex items-center gap-1 px-2 py-0.5 rounded-md text-xs"
                        style={{
                          background: `${tag.color}20`,
                          border: `1px solid ${tag.color}40`,
                          color: tag.color,
                        }}
                      >
                        <Tag className="w-3 h-3" />
                        {tag.name}
                      </span>
                    ))}
                    {task.tags.length > 2 && (
                      <span className="text-xs text-white/40">
                        +{task.tags.length - 2}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Processing overlay */}
      {isProcessing && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm rounded-xl"
          style={{ background: "rgba(0,0,0,0.2)" }}
        >
          <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
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

/**
 * Compact inline version for embedding within chat messages.
 * Displays task without full editing capabilities.
 */
export function InlineTaskCard({ task, onAction }: InlineTaskCardProps) {
  const priority = priorityConfig[task.priority]

  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null
    const date = new Date(dateStr)
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
    }).format(date)
  }

  const dueDate = formatDueDate(task.due_date)

  return (
    <div
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border"
      style={{
        background: "rgba(20, 20, 26, 0.8)",
        borderColor: "rgba(255, 255, 255, 0.15)",
      }}
    >
      {/* Status icon */}
      <div
        className={`w-4 h-4 rounded flex items-center justify-center ${
          task.completed ? "bg-cyan-500" : "border-2 border-white/30"
        }`}
      >
        {task.completed && <Check className="w-2.5 h-2.5 text-white" strokeWidth={3} />}
      </div>

      {/* Title */}
      <span
        className={`text-sm ${task.completed ? "line-through opacity-50" : ""}`}
        style={{ color: "rgba(255,255,255,0.9)" }}
      >
        {task.title}
      </span>

      {/* Priority */}
      <span
        className={`px-1.5 py-0.5 rounded text-xs ${priority.text}`}
        style={{ background: priority.bg }}
      >
        {task.priority}
      </span>

      {/* Due date */}
      {dueDate && (
        <span className="text-xs text-white/50">{dueDate}</span>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1 ml-1 pl-2 border-l border-white/10">
        <button
          onClick={() => onAction?.("complete", task)}
          className="p-1 rounded hover:bg-cyan-500/20 text-cyan-400 transition-colors"
          title={task.completed ? "Mark incomplete" : "Mark complete"}
        >
          <Check className="w-3 h-3" />
        </button>
        <button
          onClick={() => onAction?.("delete", task)}
          className="p-1 rounded hover:bg-red-500/20 text-red-400 transition-colors"
          title="Delete"
        >
          <Trash2 className="w-3 h-3" />
        </button>
      </div>
    </div>
  )
}
