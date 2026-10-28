import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { AlertTriangle, CheckCircle2, Info, OctagonAlert } from "lucide-react"

import { cn } from "@/lib/utils"

/**
 * Inline message for status, warnings and errors inside content (not a toast).
 * Tinted from the status tokens so it reads in both themes; the icon carries the tone.
 */
const calloutVariants = cva(
  "flex items-start gap-3 rounded-[var(--radius-lg)] border px-4 py-3 text-sm [&>svg]:mt-0.5 [&>svg]:size-4 [&>svg]:shrink-0",
  {
    variants: {
      tone: {
        info: "border-secondary/25 bg-secondary/10 [&>svg]:text-secondary",
        success: "border-success/25 bg-success/10 [&>svg]:text-success",
        warning: "border-warning/30 bg-warning/10 [&>svg]:text-warning",
        danger: "border-destructive/30 bg-destructive/10 [&>svg]:text-destructive",
      },
    },
    defaultVariants: { tone: "info" },
  }
)

const icons = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: OctagonAlert,
}

interface CalloutProps
  extends Omit<React.ComponentProps<"div">, "title">,
    VariantProps<typeof calloutVariants> {
  title?: React.ReactNode
  /** Buttons or links shown under the text */
  action?: React.ReactNode
}

function Callout({ tone = "info", title, action, className, children, ...props }: CalloutProps) {
  const Icon = icons[tone ?? "info"]
  return (
    <div
      data-slot="callout"
      role={tone === "danger" || tone === "warning" ? "alert" : "status"}
      className={cn(calloutVariants({ tone }), className)}
      {...props}
    >
      <Icon aria-hidden />
      <div className="min-w-0 flex-1 space-y-1">
        {title && <p className="font-medium text-foreground">{title}</p>}
        {children && <div className="text-muted-foreground [&_a]:underline [&_a]:underline-offset-2">{children}</div>}
        {action && <div className="flex flex-wrap gap-2 pt-1.5">{action}</div>}
      </div>
    </div>
  )
}

export { Callout, calloutVariants }
