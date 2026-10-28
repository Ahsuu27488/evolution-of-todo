"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"

interface ErrorBoundaryProps {
  error: Error & { digest?: string }
  reset: () => void
}

/** Route-level error screen: a calm card on the sky background, retry plus a way home */
export function ErrorBoundary({ error, reset }: ErrorBoundaryProps) {
  const [retrying, setRetrying] = useState(false)

  useEffect(() => {
    console.error("Error:", error)
  }, [error])

  return (
    <main className="grid min-h-dvh place-items-center px-4 py-16">
      <div className="surface w-full max-w-md rounded-[var(--radius-3xl)] p-6 text-center sm:p-8" role="alert">
        {/* A small orbit knocked off course */}
        <div aria-hidden className="relative mx-auto mb-6 size-20">
          <div className="absolute inset-0 rounded-full border border-dashed border-foreground/15" />
          <div className="absolute top-1/2 left-1/2 size-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary" />
          <div className="absolute -top-0.5 right-1 size-3 rounded-full bg-destructive" />
        </div>

        <h1 className="font-display text-2xl font-semibold">Something went wrong</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          This page hit an error it couldn&apos;t recover from. Your tasks are safe. Try again, or go back to
          your list.
        </p>

        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-center">
          <Button variant="ghost" asChild>
            <Link href="/dashboard">Go to my tasks</Link>
          </Button>
          <Button
            onClick={() => {
              setRetrying(true)
              reset()
            }}
            disabled={retrying}
            aria-busy={retrying}
          >
            <RefreshCw className={retrying ? "animate-spin" : undefined} aria-hidden />
            Try again
          </Button>
        </div>

        {error.digest && (
          <p className="mt-6 text-xs text-muted-foreground">
            Error reference <code className="font-mono">{error.digest}</code>
          </p>
        )}
      </div>
    </main>
  )
}
