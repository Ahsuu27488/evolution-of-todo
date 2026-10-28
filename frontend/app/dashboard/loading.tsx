import { Skeleton } from "@/components/ui/skeleton"

/** Mirrors the dashboard layout (floating nav, orbit panel, heading, toolbar, cards) so nothing jumps */
export default function DashboardLoading() {
  return (
    <div className="min-h-screen" aria-busy="true" aria-label="Loading your tasks">
      <div className="fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-6 sm:pt-4">
        <div className="glass mx-auto flex h-14 max-w-6xl items-center gap-2 rounded-full pr-2 pl-4 sm:pl-5">
          <Skeleton className="h-6 w-28 rounded-full" />
          <div className="flex-1" />
          <Skeleton className="size-10 rounded-full" />
          <Skeleton className="size-10 rounded-full" />
        </div>
      </div>

      <main className="px-4 pt-24 pb-28 sm:px-6 sm:pt-28">
        <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[minmax(0,17.5rem)_minmax(0,1fr)] lg:gap-10">
          <div className="surface grid grid-cols-[7.5rem_1fr] items-center gap-4 rounded-[var(--radius-3xl)] p-4 sm:grid-cols-[9rem_1fr] lg:grid-cols-1 lg:p-5">
            <Skeleton className="aspect-square w-full rounded-full" />
            <div className="space-y-3">
              <Skeleton className="h-5 w-28" />
              <Skeleton className="h-3.5 w-full" />
              <Skeleton className="h-3.5 w-full" />
              <Skeleton className="h-3.5 w-3/4" />
            </div>
          </div>

          <div className="min-w-0">
            <div className="mb-5 flex items-end justify-between gap-3">
              <div className="space-y-2">
                <Skeleton className="h-4 w-36" />
                <Skeleton className="h-10 w-44" />
              </div>
              <Skeleton className="h-11 w-11 rounded-full sm:w-32" />
            </div>
            <Skeleton className="mb-2 h-10 w-full rounded-full" />
            <div className="mb-6 flex gap-2">
              <Skeleton className="h-10 w-56 rounded-full" />
              <Skeleton className="h-10 flex-1 rounded-full sm:w-36 sm:flex-none" />
            </div>

            <div className="space-y-3">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="surface flex items-start gap-3 rounded-[var(--radius-xl)] px-4 py-3.5">
                  <Skeleton className="mt-0.5 size-5 rounded-[6px]" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-2/3" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                  <Skeleton className="size-10 rounded-full" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
