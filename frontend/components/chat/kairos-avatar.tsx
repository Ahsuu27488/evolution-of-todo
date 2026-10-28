import { cn } from "@/lib/utils"

/**
 * Kairos, the chat assistant ("the right moment" to Chronos's clock time).
 * Its mark: a sun-gold disc crossed by a thin orbit, a sibling of the Chronos mark.
 */
export function KairosAvatar({ className, thinking = false }: { className?: string; thinking?: boolean }) {
  return (
    <span
      className={cn("relative inline-grid size-9 shrink-0 place-items-center rounded-full bg-primary", className)}
      aria-hidden
    >
      <svg viewBox="0 0 32 32" className={cn("size-[78%]", thinking && "motion-safe:animate-[spin_3s_linear_infinite]")}>
        <ellipse
          cx="16"
          cy="16"
          rx="13.5"
          ry="5"
          transform="rotate(-28 16 16)"
          fill="none"
          stroke="var(--custom-primary-foreground)"
          strokeOpacity="0.55"
          strokeWidth="1.8"
        />
        <circle cx="27" cy="10.2" r="2.3" fill="var(--custom-primary-foreground)" />
      </svg>
    </span>
  )
}
