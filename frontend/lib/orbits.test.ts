import { test } from "node:test"
import assert from "node:assert/strict"

import { orbitCounts } from "./orbits.ts"

const now = new Date(2026, 9, 27, 12, 0) // Tue 27 Oct 2026, noon local time
const at = (days: number, hour = 10) => new Date(2026, 9, 27 + days, hour).toISOString()

test("buckets open tasks by due date and counts completed ones", () => {
  const counts = orbitCounts(
    [
      { completed: false, due_date: at(0, 9) }, // earlier today
      { completed: false, due_date: at(0, 23) }, // later today
      { completed: false, due_date: at(-3) }, // overdue counts as today
      { completed: false, due_date: at(1) }, // tomorrow
      { completed: false, due_date: at(7) }, // seventh day still this week
      { completed: false, due_date: at(8) }, // beyond the week
      { completed: false, due_date: null }, // no date
      { completed: true, due_date: at(0) },
    ],
    now
  )
  assert.deepEqual(counts, { today: 3, week: 2, later: 2, done: 1 })
})

test("empty list", () => {
  assert.deepEqual(orbitCounts([], now), { today: 0, week: 0, later: 0, done: 0 })
})
