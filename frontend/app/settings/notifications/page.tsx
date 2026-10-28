/**
 * Notification Settings Page
 *
 * [Task]: T016, T047-T050
 * [From]: spec.md FR-033
 *
 * Push, email and in-app channels in tabs (?tab=push|email|in-app).
 */

import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Header } from "@/components/layout/header"
import { requireAuth } from "@/app/actions/auth"
import { NotificationTabs } from "@/components/notifications/notification-tabs"
import type { Metadata } from "next"

export const metadata: Metadata = { title: "Notification settings" }

export default async function NotificationSettingsPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string }>
}) {
  const session = await requireAuth()
  const params = await searchParams
  const initialTab = params.tab || "push"

  return (
    <div className="min-h-screen">
      <Header isAuthenticated user={session.user} />

      <main className="px-4 pt-24 pb-16 sm:px-6 sm:pt-28">
        <div className="mx-auto max-w-3xl">
          <Link
            href="/dashboard"
            className="mb-4 inline-flex h-10 items-center gap-1.5 rounded-full pr-3 text-sm text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            <ArrowLeft className="size-4" aria-hidden />
            My tasks
          </Link>

          <div className="mb-6">
            <h1 className="text-[length:var(--step-h1)] leading-tight font-semibold">Notifications</h1>
            <p className="mt-1 text-muted-foreground">Choose how Chronos reaches you about your tasks.</p>
          </div>

          <NotificationTabs defaultTab={initialTab} />
        </div>
      </main>
    </div>
  )
}
