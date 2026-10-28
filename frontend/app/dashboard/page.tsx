/** Dashboard Page - Task Management Interface.
 *
 * Per spec.md:
 * - Orbit panel (live mini orrery of today / this week / later) beside the list
 * - US2: Command Center integration for voice input (Phase III foundation)
 */

import { Header } from "@/components/layout/header"
import { DashboardContent } from "@/components/dashboard/dashboard-content"
import { getSession } from "@/app/actions/auth"
import type { Metadata } from "next"

export const metadata: Metadata = { title: "My tasks" }

export default async function DashboardPage() {
  // Get session (user data) from server-side cookie
  const session = await getSession()

  // Check if authenticated
  const isAuthenticated = session !== null

  return (
    <div className="min-h-screen">
      <Header
        isAuthenticated={isAuthenticated}
        user={session?.user}
      />

      <main className="px-4 pb-28 pt-24 sm:px-6 sm:pt-28">
        <DashboardContent
          isAuthenticated={isAuthenticated}
        />
      </main>
    </div>
  )
}
