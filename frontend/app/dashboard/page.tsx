/** Dashboard Page - Task Management Interface.
 *
 * Per spec.md:
 * - FR-037: glassmorphism visual design with backdrop-blur effects
 * - FR-038: "Deep Space" color scheme with cyan/purple neon accents
 * - US2: Command Center integration for voice input (Phase III foundation)
 */

import { redirect } from "next/navigation"
import { headers } from "next/headers"
import { auth } from "@/lib/auth"
import { Header } from "@/components/layout/header"
import { DashboardContent } from "@/components/dashboard/dashboard-content"
import { getTasks } from "@/app/actions/tasks"

export default async function DashboardPage() {
  // DIAGNOSTIC: Log dashboard render attempt
  console.log("[Dashboard] Component rendering...")

  // CRITICAL: Call headers() FIRST, before any other async operation
  // This ensures headers are captured before React's async rendering
  const headersList = await headers()

  // DIAGNOSTIC: Log available cookies for debugging
  const allCookies = headersList.get("cookie") || ""
  console.log("[Dashboard] Cookie header present:", !!allCookies)
  console.log("[Dashboard] Cookie header (first 100 chars):", allCookies.substring(0, 100))

  const session = await auth.api.getSession({
    headers: headersList,
  })

  // DIAGNOSTIC: Log session status
  console.log("[Dashboard] Session:", session?.user ? `Found (user: ${session.user.email})` : "Missing")
  console.log("[Dashboard] Session object:", JSON.stringify(session, null, 2))

  if (!session?.user) {
    console.log("[Dashboard] No session - redirecting to /login")
    redirect("/login")
  }

  const result = await getTasks()
  const tasks = result.success && result.data ? result.data.tasks : []

  const pendingCount = tasks.filter((t) => !t.completed).length
  const completedCount = tasks.filter((t) => t.completed).length

  console.log("[Dashboard] Rendering with", tasks.length, "tasks")

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-6 md:py-10">
        <DashboardContent
          tasks={tasks}
          pendingCount={pendingCount}
          completedCount={completedCount}
        />
      </main>

      <style>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% center; }
          50% { background-position: 100% center; }
        }
        .animate-gradient {
          animation: gradient 4s ease infinite;
        }
      `}</style>
    </div>
  )
}
