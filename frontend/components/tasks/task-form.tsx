/** Task form: the "New task" / "Edit task" dialog.
 *
 * Fields: title, notes, priority (one-tap segmented control), due date, repeat, tags.
 * The dialog is the floating layer (glass); everything inside is solid so text stays crisp.
 */

"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { Loader2, Plus } from "lucide-react"
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
import { cn } from "@/lib/utils"
import { taskCreateSchema, type TaskCreateInput } from "@/lib/validations/task"
import { createTask, updateTask } from "@/app/actions/tasks"
import { TagInput } from "@/components/tags/tag-input"
import { DueDatePicker } from "@/components/tasks/due-date-picker"
import type { Task } from "@/types/task"

interface TaskFormProps {
  task?: Task
  trigger?: React.ReactNode
  onSuccess?: () => void
  /** Controlled open state for external dialog control (e.g., from Edit button) */
  open?: boolean
  /** Callback when open state changes */
  onOpenChange?: (open: boolean) => void
}

const priorities = [
  { value: "HIGH", label: "High", dot: "bg-destructive" },
  { value: "MEDIUM", label: "Medium", dot: "bg-primary" },
  { value: "LOW", label: "Low", dot: "bg-muted-foreground/60" },
] as const

const NO_REPEAT = "NONE"
const recurrencePatterns = [
  { value: NO_REPEAT, label: "Doesn't repeat" },
  { value: "DAILY", label: "Every day" },
  { value: "WEEKLY", label: "Every week" },
  { value: "MONTHLY", label: "Every month" },
]

export function TaskForm({ task, trigger, onSuccess, open: controlledOpen, onOpenChange }: TaskFormProps) {
  // Use internal state unless controlled externally
  const [internalOpen, setInternalOpen] = useState(false)
  const open = controlledOpen ?? internalOpen
  const setOpen = onOpenChange ?? setInternalOpen

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

  // Reset form when dialog opens with a task (for editing)
  useEffect(() => {
    if (open && task) {
      form.reset({
        title: task.title,
        description: task.description ?? undefined,
        priority: task.priority,
        tags: task.tags ?? [],
        due_date: task.due_date ?? undefined,
        recurrence_pattern: task.recurrence_pattern ?? undefined,
      })
    }
    // Only reset when open or task changes, not when form reference changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, task])

  async function onSubmit(values: TaskCreateInput) {
    setIsLoading(true)
    // The form uses null for "cleared"; the API takes absent fields
    const payload = {
      ...values,
      due_date: values.due_date ?? undefined,
      recurrence_pattern: values.recurrence_pattern ?? undefined,
    }

    try {
      const result = isEditing
        ? await updateTask(task.id, payload)
        : await createTask(payload)

      if (!result.success) {
        toast.error(result.error?.message || `Couldn't ${isEditing ? "save" : "create"} the task`)
        return
      }

      // Invalidate TanStack Query cache to refetch tasks
      queryClient.invalidateQueries({ queryKey: ["tasks"] })

      toast.success(isEditing ? "Task saved" : "Task added")
      form.reset()
      setOpen(false)
      onSuccess?.()
    } catch {
      toast.error("Something went wrong. Try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(next) => !isLoading && setOpen(next)}>
      {/* Only render trigger when not controlled externally (i.e., not editing from dropdown) */}
      {controlledOpen === undefined && (
        <DialogTrigger asChild>
          {trigger || (
            <Button size="lg" className="gap-2 rounded-full px-4 sm:px-5" aria-label="Add task">
              <Plus className="h-5 w-5" />
              <span className="hidden sm:inline">Add task</span>
            </Button>
          )}
        </DialogTrigger>
      )}
      <DialogContent className="sm:max-w-[34rem]">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit task" : "New task"}</DialogTitle>
          <DialogDescription className={cn(isEditing && "truncate")}>
            {isEditing ? task.title : "Only the title is required."}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="grid gap-5" aria-busy={isLoading}>
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="What needs to be done?"
                      autoComplete="off"
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Notes <span className="font-normal text-muted-foreground">(optional)</span>
                  </FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Details, links, anything that helps"
                      className="min-h-20 resize-none"
                      rows={3}
                      disabled={isLoading}
                      {...field}
                      value={field.value ?? ""}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel id="priority-label">Priority</FormLabel>
                  <div
                    role="radiogroup"
                    aria-labelledby="priority-label"
                    className="grid grid-cols-3 gap-1 rounded-full border border-input p-1"
                  >
                    {priorities.map((p) => {
                      const checked = field.value === p.value
                      return (
                        <button
                          key={p.value}
                          type="button"
                          role="radio"
                          aria-checked={checked}
                          disabled={isLoading}
                          onClick={() => field.onChange(p.value)}
                          onKeyDown={(e) => {
                            // Arrow keys move through the group like a native radio set
                            if (!["ArrowLeft", "ArrowRight"].includes(e.key)) return
                            e.preventDefault()
                            const i = priorities.findIndex((x) => x.value === field.value)
                            const next = priorities[(i + (e.key === "ArrowRight" ? 1 : 2)) % 3]
                            field.onChange(next.value)
                          }}
                          tabIndex={checked ? 0 : -1}
                          className={cn(
                            "inline-flex h-9 items-center justify-center gap-2 rounded-full text-sm font-medium outline-none transition-colors duration-150",
                            "focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-[0.97] disabled:opacity-50",
                            checked
                              ? "bg-accent text-foreground shadow-[inset_0_0_0_1px_var(--custom-border)]"
                              : "text-muted-foreground hover:text-foreground"
                          )}
                        >
                          <span className={cn("size-2 rounded-full", p.dot)} aria-hidden />
                          {p.label}
                        </button>
                      )
                    })}
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid gap-5 sm:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] sm:gap-3">
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
                        label="Due"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="recurrence_pattern"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Repeat</FormLabel>
                    <Select
                      value={field.value ?? NO_REPEAT}
                      onValueChange={(v) => field.onChange(v === NO_REPEAT ? null : v)}
                      disabled={isLoading}
                    >
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {recurrencePatterns.map((rp) => (
                          <SelectItem key={rp.value} value={rp.value}>
                            {rp.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="tags"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Tags <span className="font-normal text-muted-foreground">(optional)</span>
                  </FormLabel>
                  <FormControl>
                    <TagInput
                      value={field.value ?? []}
                      onChange={field.onChange}
                      disabled={isLoading}
                      maxTags={10}
                      placeholder="Type a tag, then Enter"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setOpen(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading} aria-busy={isLoading} className="min-w-32">
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    {isEditing ? "Saving" : "Adding"}
                  </>
                ) : isEditing ? (
                  "Save changes"
                ) : (
                  "Add task"
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
