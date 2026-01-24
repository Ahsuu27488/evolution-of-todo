/** Profile Page - Edit User Information.

Allows users to update their first name and last name.
Useful for existing users who signed up before name fields were added.
Per spec.md: User profile personalization.
*/

import { Header } from "@/components/layout/header"
import { ProfileForm } from "@/components/auth/profile-form"
import { requireAuth } from "@/app/actions/auth"

export default async function ProfilePage() {
  // Get session (user data) from server-side cookie
  const session = await requireAuth()

  // requireAuth guarantees session exists and redirects if not
  const isAuthenticated = true

  return (
    <div className="min-h-screen bg-background">
      <Header
        isAuthenticated={isAuthenticated}
        user={session.user}
      />

      <main className="container px-6 pt-24 pb-6 md:pt-28 md:pb-10">
        <div className="max-w-2xl mx-auto">
          {/* Page Header */}
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold mb-2 bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
              Your Profile
            </h1>
            <p className="text-muted-foreground">
              Manage your personal information
            </p>
          </div>

          {/* Profile Form */}
          <ProfileForm user={session.user} />
        </div>
      </main>
    </div>
  )
}
