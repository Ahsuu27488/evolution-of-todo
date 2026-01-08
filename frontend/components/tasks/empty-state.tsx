"use client"

import { ClipboardList } from "lucide-react"
import { TaskForm } from "./task-form"

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <ClipboardList className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">No tasks yet</h3>
      <p className="text-muted-foreground mt-1 mb-4 max-w-sm">
        Get started by creating your first task. Stay organized and track your
        progress.
      </p>
      <TaskForm />
    </div>
  )
}
