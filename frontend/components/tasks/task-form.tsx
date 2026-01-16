/** Task Form Component with Deep Space Glassmorphism Modal.
 *
 * Per spec.md FR-037: glassmorphism visual design with backdrop-blur effects
 * Per spec.md US3: "stunning glassmorphism modal slides in from bottom"
 * Per US1 (008-dashboard-ui-overhaul): Enhanced with due date, tags, and recurrence pattern
 *
 * Acceptance Scenarios (US3):
 * - Given an authenticated user on dashboard, When they click "+" FAB,
 *   Then a glassmorphism modal slides in from bottom with backdrop blur
 * - Given a user creating task, When they enter title and select priority,
 *   Then task is saved with priority indicator and appears with slide-in animation
 *
 * New Acceptance Scenarios (US1):
 * - Given a user creating task, When they select a due date using the datetime picker,
 *   Then the selected date is formatted and saved with the task
 * - Given a user creating task, When they add tags by typing and pressing Enter,
 *   Then colored tag chips appear and can be removed by clicking their × icon
 * - Given a user creating task, When they select a recurrence pattern (DAILY, WEEKLY, MONTHLY),
 *   Then a recurrence icon appears on the saved task card
 */

"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { Loader2, Plus, Sparkles, Repeat2 } from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { taskCreateSchema, type TaskCreateInput } from "@/lib/validations/task"
import { createTask, updateTask } from "@/app/actions/tasks"
import { slideInBottom } from "@/lib/animations"
import { TagInput } from "@/components/tags/tag-input"
import { DueDatePicker } from "@/components/tasks/due-date-picker"
import type { Task } from "@/types/task"

interface TaskFormProps {
  task?: Task
  trigger?: React.ReactNode
  onSuccess?: () => void
}

const priorities = [
  { value: "HIGH", label: "High", color: "text-destructive" },
  { value: "MEDIUM", label: "Medium", color: "text-secondary" },
  { value: "LOW", label: "Low", color: "text-muted-foreground" },
]

const recurrencePatterns = [
  { value: "DAILY", label: "Daily", description: "Repeats every day" },
  { value: "WEEKLY", label: "Weekly", description: "Repeats every week" },
  { value: "MONTHLY", label: "Monthly", description: "Repeats every month" },
]

export function TaskForm({ task, trigger, onSuccess }: TaskFormProps) {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const isEditing = !!task
  const queryClient = useQueryClient()

  const form = useForm<TaskCreateInput>({
    resolver: zodResolver(taskCreateSchema),
    defaultValues: {
      title: task?.title || "",
      description: task?.description ?? undefined,
      priority: task?.priority || "MEDIUM",
      tags: task?.tags ?? [],
      due_date: task?.due_date || undefined,
      recurrence_pattern: task?.recurrence_pattern || undefined,
    },
  })

  async function onSubmit(values: TaskCreateInput) {
    setIsLoading(true)

    try {
      const result = isEditing
        ? await updateTask(task.id, values)
        : await createTask(values)

      if (!result.success) {
        toast.error(result.error?.message || `Failed to ${isEditing ? "update" : "create"} task`)
        return
      }

      // Invalidate TanStack Query cache to refetch tasks
      queryClient.invalidateQueries({ queryKey: ["tasks"] })

      toast.success(isEditing ? "Task updated" : "Task created")
      form.reset()
      setOpen(false)
      onSuccess?.()
    } catch {
      toast.error("Something went wrong")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              size="lg"
              className="gap-2 shadow-lg shadow-primary/20"
            >
              <Plus className="h-5 w-5" />
              <span className="hidden sm:inline">Add Task</span>
            </Button>
          </motion.div>
        )}
      </DialogTrigger>
      <DialogContent className="glass-modal sm:max-w-[500px]">
        <motion.div
          variants={slideInBottom}
          initial="hidden"
          animate="visible"
          exit="hidden"
        >
          <DialogHeader>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <DialogTitle className="text-xl">
                {isEditing ? (
                  "Edit Task"
                ) : (
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    Create New Task
                  </span>
                )}
              </DialogTitle>
            </motion.div>
            <DialogDescription className="text-muted-foreground">
              {isEditing
                ? "Make changes to your task below."
                : "Add a new task to your list. Fill in the details."}
            </DialogDescription>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
              {/* Title */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 }}
              >
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-foreground">Title</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="What needs to be done?"
                          disabled={isLoading}
                          className="bg-background/50 border-border/50"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Description */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-foreground">Description (optional)</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Add more details..."
                          className="resize-none bg-background/50 border-border/50"
                          rows={3}
                          disabled={isLoading}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Priority */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
              >
                <FormField
                  control={form.control}
                  name="priority"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-foreground">Priority</FormLabel>
                      <Select
                        value={field.value}
                        onValueChange={field.onChange}
                      >
                        <FormControl>
                          <SelectTrigger className="bg-background/50 border-border/50">
                            <SelectValue placeholder="Select priority" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="glass-strong">
                          {priorities.map((p) => (
                            <SelectItem
                              key={p.value}
                              value={p.value}
                              className={p.color}
                            >
                              {p.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Due Date */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <FormField
                  control={form.control}
                  name="due_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <DueDatePicker
                          value={field.value ?? null}
                          onChange={field.onChange}
                          disabled={isLoading}
                          label="Due Date (optional)"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Tags */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 }}
              >
                <FormField
                  control={form.control}
                  name="tags"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-foreground">Tags (optional)</FormLabel>
                      <FormControl>
                        <TagInput
                          value={field.value ?? []}
                          onChange={field.onChange}
                          disabled={isLoading}
                          maxTags={10}
                          placeholder="Type and press Enter to add tags"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Recurrence Pattern */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
              >
                <FormField
                  control={form.control}
                  name="recurrence_pattern"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-foreground flex items-center gap-2">
                        <Repeat2 className="h-4 w-4" />
                        Recurrence (optional)
                      </FormLabel>
                      <Select
                        value={field.value || undefined}
                        onValueChange={field.onChange}
                      >
                        <FormControl>
                          <SelectTrigger className="bg-background/50 border-border/50">
                            <SelectValue placeholder="No recurrence" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="glass-strong">
                          {recurrencePatterns.map((rp) => (
                            <SelectItem key={rp.value} value={rp.value}>
                              <div className="flex flex-col">
                                <span>{rp.label}</span>
                                <span className="text-xs text-muted-foreground">
                                  {rp.description}
                                </span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </motion.div>

              {/* Actions */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <DialogFooter className="gap-2 sm:gap-0">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setOpen(false)}
                    disabled={isLoading}
                    className="bg-background/50"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="gap-2"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {isEditing ? "Saving..." : "Creating..."}
                      </>
                    ) : (
                      <>
                        {isEditing ? (
                          "Save changes"
                        ) : (
                          <>
                            <Plus className="h-4 w-4" />
                            Create task
                          </>
                        )}
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </motion.div>
            </form>
          </Form>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}
