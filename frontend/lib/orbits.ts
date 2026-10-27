/**
 * Orbit buckets for the dashboard: which open tasks are due today (or overdue),
 * this week, or later. Pure and dependency-free so it runs under `node --test`.
 */

import type { Task } from "@/types/task"

export interface OrbitCounts {
  today: number
  week: number
  later: number
  done: number
}

type OrbitTask = Pick<Task, "completed" | "due_date">

function endOfDay(date: Date, plusDays = 0): number {
  const d = new Date(date)
  d.setHours(23, 59, 59, 999)
  d.setDate(d.getDate() + plusDays)
  return d.getTime()
}

export function orbitCounts(tasks: readonly OrbitTask[], now: Date = new Date()): OrbitCounts {
  const todayEnd = endOfDay(now)
  const weekEnd = endOfDay(now, 7)
  const counts: OrbitCounts = { today: 0, week: 0, later: 0, done: 0 }

  for (const task of tasks) {
    if (task.completed) {
      counts.done++
      continue
    }
    const due = task.due_date ? new Date(task.due_date).getTime() : NaN
    if (Number.isNaN(due)) counts.later++
    else if (due <= todayEnd) counts.today++
    else if (due <= weekEnd) counts.week++
    else counts.later++
  }
  return counts
}
