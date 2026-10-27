import Link from "next/link"

import { ChronosMark } from "@/components/layout/brand-logo"

export function SiteFooter() {
  return (
    <footer className="border-t border-border px-5 py-10 sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-foreground">
          <ChronosMark className="h-6 w-6" />
          <span className="font-display font-semibold">Chronos</span>
        </div>
        <p className="max-w-md">
          An open project built with Next.js, FastAPI, Neon Postgres and the OpenAI Agents SDK.
        </p>
        <nav aria-label="Footer" className="flex gap-5">
          <Link href="/login" className="hover:text-foreground">Sign in</Link>
          <Link href="/signup" className="hover:text-foreground">Create account</Link>
          <a
            href="https://github.com/Ahsuu27488/evolution-of-todo"
            className="hover:text-foreground"
            rel="noreferrer"
            target="_blank"
          >
            Source
          </a>
        </nav>
      </div>
    </footer>
  )
}
