import Link from "next/link"

import { cn } from "@/lib/utils"

/** The Chronos mark: a "now" core on a tilted orbit, drawn in SVG. */
export function ChronosMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={cn("h-7 w-7", className)} aria-hidden>
      <ellipse
        cx="16"
        cy="16"
        rx="13"
        ry="5.5"
        transform="rotate(-24 16 16)"
        fill="none"
        stroke="currentColor"
        strokeOpacity="0.45"
        strokeWidth="1.4"
      />
      <circle cx="16" cy="16" r="5.2" fill="var(--custom-primary)" />
      <circle cx="27.2" cy="10.8" r="1.9" fill="currentColor" />
    </svg>
  )
}

/** Brand logo: mark + wordmark, links home. */
export function BrandLogo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn(
        "group flex items-center gap-2 rounded-full pr-1 text-foreground outline-offset-4",
        className
      )}
      aria-label="Chronos home"
    >
      <ChronosMark className="transition-transform duration-500 ease-[var(--ease-out)] group-hover:rotate-[30deg]" />
      <span className="font-display text-xl font-semibold tracking-[-0.03em]">Chronos</span>
    </Link>
  )
}
