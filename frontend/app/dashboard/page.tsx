/** Dashboard Page - Task Management Interface.
 *
 * Per spec.md:
 * - FR-037: glassmorphism visual design with backdrop-blur effects
 * - FR-038: "Deep Space" color scheme with cyan/purple neon accents
 * - US2: Command Center integration for voice input (Phase III foundation)
 */

import { Header } from "@/components/layout/header"
import { DashboardContent } from "@/components/dashboard/dashboard-content"
import { getTasks } from "@/app/actions/tasks"
import { getSession } from "@/app/actions/auth"

export default async function DashboardPage() {
  // Get session (user data) from server-side cookie
  const session = await getSession()

  // Get tasks
  const result = await getTasks()
  const tasks = result.success && result.data ? result.data.tasks : []
  const isAuthenticated = result.success && session !== null

  const pendingCount = tasks.filter((t) => !t.completed).length
  const completedCount = tasks.filter((t) => t.completed).length

  return (
    <div className="min-h-screen bg-background">
      <Header
        isAuthenticated={isAuthenticated}
        user={session?.user}
      />

      <main className="container py-6 md:py-10">
        <DashboardContent
          tasks={tasks}
          pendingCount={pendingCount}
          completedCount={completedCount}
          isAuthenticated={isAuthenticated}
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
