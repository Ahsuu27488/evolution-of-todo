"use server"

/**
 * Server Actions for Authentication using Better Auth
 *
 * Per Context7 Better Auth documentation:
 * - Uses auth.api.getSession({ headers }) for server-side session retrieval
 * - Better Auth handles session cookies automatically via nextCookies plugin
 * - No need for manual JWT storage - Better Auth manages sessions
 *
 * References:
 * - https://context7.com/better-auth/better-auth
 */

import { headers } from "next/headers"
import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"

// =============================================================================
// Types
// =============================================================================

export interface Session {
  user: {
    id: string
    email: string
    name: string
    emailVerified: boolean
    image?: string | null
  }
}

// =============================================================================
// Auth Actions
// =============================================================================

/**
 * Get current session from Better Auth
 *
 * Per Context7: Use auth.api.getSession({ headers }) for server-side
 * session retrieval in Server Components and Server Actions.
 *
 * @returns Session with user data or null if not authenticated
 */
export async function getSession(): Promise<Session | null> {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    if (!session) {
      return null
    }

    return {
      user: {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name,
        emailVerified: session.user.emailVerified,
        image: session.user.image,
      },
    }
  } catch (error) {
    console.error("[Auth] Error getting session:", error)
    return null
  }
}

/**
 * Require authentication - redirect to login if not authenticated
 *
 * Per Context7: Use auth.api.getSession() to check auth status
 * and redirect if needed.
 */
export async function requireAuth(): Promise<Session> {
  const session = await getSession()

  if (!session) {
    redirect("/login")
  }

  return session
}

/**
 * Sign out action
 *
 * Per Context7: Use auth.api.signOut() for server-side sign out.
 * This clears the Better Auth session cookie.
 */
export async function signOutAction(): Promise<{ success: boolean }> {
  try {
    await auth.api.signOut({
      headers: await headers(),
    })
    return { success: true }
  } catch (error) {
    console.error("[Auth] Error signing out:", error)
    return { success: false }
  }
}
