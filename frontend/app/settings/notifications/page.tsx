/**
 * Notification Settings Page
 *
 * [Task]: T016, T047-T050
 * [From]: spec.md FR-033
 * [From]: contracts/api.yaml §4.1, §4.2
 *
 * Features:
 * - Tabbed interface for different notification settings
 * - Push notification settings
 * - Email notification preferences
 * - In-app notification settings (always enabled)
 */

import { Header } from "@/components/layout/header"
import { requireAuth } from "@/app/actions/auth"
import { NotificationTabs } from "@/components/notifications/notification-tabs"

export default async function NotificationSettingsPage({
  searchParams,
}: {
  searchParams: Promise<{ tab?: string }>
}) {
  const session = await requireAuth()
  const params = await searchParams
  const initialTab = params.tab || "push"

  return (
    <div className="min-h-screen bg-background">
      <Header
        isAuthenticated={true}
        user={session.user}
      />

      <main className="container px-4 sm:px-6 pt-20 pb-6 sm:pt-24 sm:pb-10">
        <div className="max-w-3xl mx-auto">
          {/* Page Header */}
          <div className="mb-6 sm:mb-8 text-center">
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-2 bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
              Notification Settings
            </h1>
            <p className="text-sm sm:text-base text-muted-foreground px-2">
              Manage how and when you receive notifications
            </p>
          </div>

          {/* Settings Tabs */}
          <NotificationTabs defaultTab={initialTab} />
        </div>
      </main>
    </div>
  )
}
