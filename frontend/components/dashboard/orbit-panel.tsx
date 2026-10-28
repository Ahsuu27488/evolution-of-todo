"use client"

/**
 * "Your orbits": the dashboard's small live orrery. Moons are the user's open
 * tasks bucketed into today / this week / later (lib/orbits.ts).
 */

import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"

import { Orrery } from "@/components/three/orrery"
import { api } from "@/lib/api-client"
import { orbitCounts } from "@/lib/orbits"
import { cn } from "@/lib/utils"

const MAX_MOONS = 14

export function useOrbitCounts() {
  // Unfiltered list, shared with the task list's cache prefix so it refreshes with it.
  const { data } = useQuery({
    queryKey: ["tasks", "all", "all"],
    // Same key as useTaskFilters' unfiltered query, so it must behave the same: throw on failure
    // (a failed Result cached as data made the task list show "Nothing in orbit yet")
    queryFn: async () => {
      const result = await api.getTasks({ status: "all" })
      if (!result.success) throw new Error(result.error.message)
      return result
    },
    retry: 1,
  })
  return useMemo(
    () => orbitCounts(data?.success ? data.data.tasks ?? [] : []),
    [data]
  )
}

export function OrbitPanel({ className }: { className?: string }) {
  const counts = useOrbitCounts()
  const moons = useMemo<[number, number, number]>(
    () => [
      Math.min(counts.today, MAX_MOONS),
      Math.min(counts.week, MAX_MOONS),
      Math.min(counts.later, MAX_MOONS),
    ],
    [counts.today, counts.week, counts.later]
  )
  const open = counts.today + counts.week + counts.later
  const total = open + counts.done

  const rows = [
    { label: "Today", value: counts.today, dot: "var(--custom-primary)" },
    { label: "This week", value: counts.week, dot: "var(--custom-secondary)" },
    { label: "Later", value: counts.later, dot: "color-mix(in oklch, var(--custom-secondary) 55%, transparent)" },
  ]

  return (
    <aside
      aria-labelledby="orbits-title"
      className={cn(
        "surface grid grid-cols-[7.5rem_1fr] items-center gap-4 rounded-[var(--radius-3xl)] p-4 sm:grid-cols-[9rem_1fr] lg:grid-cols-1 lg:p-5",
        className
      )}
    >
      <Orrery variant="mini" moons={moons} className="aspect-square w-full lg:-mx-2 lg:w-[calc(100%+1rem)]" />

      <div>
        <h2 id="orbits-title" className="font-display text-lg font-semibold">
          Your orbits
        </h2>
        <dl className="mt-3 space-y-2 text-sm">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center gap-2.5">
              <span className="size-2 shrink-0 rounded-full" style={{ background: row.dot }} aria-hidden />
              <dt className="text-muted-foreground">{row.label}</dt>
              <dd className="ml-auto font-medium tabular-nums">{row.value}</dd>
            </div>
          ))}
        </dl>
        {total > 0 && (
          <div className="mt-4">
            <div
              className="h-1.5 overflow-hidden rounded-full bg-muted"
              role="progressbar"
              aria-label="Tasks done"
              aria-valuemin={0}
              aria-valuemax={total}
              aria-valuenow={counts.done}
            >
              <div
                className="h-full rounded-full bg-primary transition-[width] duration-700 ease-[var(--ease-out)]"
                style={{ width: `${(counts.done / total) * 100}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-muted-foreground tabular-nums">
              {counts.done} of {total} done
            </p>
          </div>
        )}
      </div>
    </aside>
  )
}
