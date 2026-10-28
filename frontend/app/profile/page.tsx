/** Profile page: edit your name. Same frame as the dashboard: floating nav, left-aligned heading. */

import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Header } from "@/components/layout/header"
import { ProfileForm } from "@/components/auth/profile-form"
import { requireAuth } from "@/app/actions/auth"
import { getDisplayName } from "@/types/user"
import type { Metadata } from "next"

export const metadata: Metadata = { title: "Profile" }

export default async function ProfilePage() {
  // requireAuth redirects to /login when there is no session
  const session = await requireAuth()
  const memberSince = new Intl.DateTimeFormat("en", { month: "long", year: "numeric" }).format(
    new Date(session.user.created_at)
  )

  return (
    <div className="min-h-screen">
      <Header isAuthenticated user={session.user} />

      <main className="px-4 pt-24 pb-16 sm:px-6 sm:pt-28">
        <div className="mx-auto max-w-2xl">
          <Link
            href="/dashboard"
            className="mb-4 inline-flex h-10 items-center gap-1.5 rounded-full pr-3 text-sm text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
          >
            <ArrowLeft className="size-4" aria-hidden />
            My tasks
          </Link>

          <div className="mb-6">
            <h1 className="text-[length:var(--step-h1)] leading-tight font-semibold">Profile</h1>
            <p className="mt-1 text-muted-foreground">
              {getDisplayName(session.user)} · member since {memberSince}
            </p>
          </div>

          <ProfileForm user={session.user} />
        </div>
      </main>
    </div>
  )
}
