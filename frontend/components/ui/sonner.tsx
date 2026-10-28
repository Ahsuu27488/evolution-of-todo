"use client"

import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { useTheme } from "next-themes"
import { Toaster as Sonner, type ToasterProps } from "sonner"

/**
 * Toasts on the solid floating surface. The status shows in the icon colour only,
 * so a stack of toasts stays calm (no full red or green fills).
 */
const Toaster = ({ ...props }: ToasterProps) => {
  const { resolvedTheme } = useTheme()

  return (
    <Sonner
      theme={(resolvedTheme as ToasterProps["theme"]) ?? "dark"}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-[18px] text-success" />,
        info: <InfoIcon className="size-[18px] text-secondary" />,
        warning: <TriangleAlertIcon className="size-[18px] text-warning" />,
        error: <OctagonXIcon className="size-[18px] text-destructive" />,
        loading: <Loader2Icon className="size-[18px] animate-spin text-muted-foreground" />,
      }}
      toastOptions={{
        classNames: {
          toast:
            "surface-pop !rounded-[var(--radius-xl)] !border-border !px-4 !py-3.5 !gap-3 font-sans !text-popover-foreground",
          title: "!font-medium !text-sm",
          description: "!text-muted-foreground !text-[13px]",
          actionButton: "!bg-primary !text-primary-foreground !rounded-full !h-8 !px-3 !font-medium",
          cancelButton: "!bg-muted !text-foreground !rounded-full !h-8 !px-3",
          closeButton:
            "!bg-popover !text-muted-foreground !border-border hover:!text-foreground hover:!bg-accent",
        },
      }}
      style={
        {
          "--normal-bg": "var(--color-popover)",
          "--normal-text": "var(--color-popover-foreground)",
          "--normal-border": "var(--color-border)",
          "--border-radius": "calc(var(--radius) + 4px)",
          "--width": "min(380px, calc(100vw - 2rem))",
        } as React.CSSProperties
      }
      {...props}
    />
  )
}

export { Toaster }
