/**
 * Better Auth Client Configuration
 *
 * This uses Better Auth's createAuthClient for client-side authentication.
 * Per Better Auth documentation from Context7:
 * - Uses authClient.signUp.email() for signup
 * - Uses authClient.signIn.email() for signin
 * - Uses authClient.useSession() for session state
 * - Session cookies are handled automatically via nextCookies plugin
 *
 * References:
 * - https://context7.com/better-auth/better-auth
 */

import { createAuthClient } from "better-auth/client"
import { inferAdditionalFields } from "better-auth/client/plugins"
import type { auth } from "./auth"

/**
 * Better Auth Client Instance
 *
 * Per Context7 docs: The client automatically handles session cookies
 * via the nextCookies plugin configured in lib/auth.ts
 */
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [
    // Infer additional fields from server configuration
    inferAdditionalFields<typeof auth>(),
  ],
})

/**
 * Session Type
 * Inferred from Better Auth client for type safety
 */
export type Session = typeof authClient.$Infer.Session

/**
 * User Type
 * Inferred from Better Auth client
 */
export type User = typeof authClient.$Infer.Session.user

/**
 * React Hook for Session
 * Per Context7: Call authClient.useSession() directly
 *
 * Usage:
 * ```tsx
 * import { authClient } from "@/lib/auth-client"
 * const { data: session, isPending, error } = authClient.useSession()
 * ```
 *
 * Note: useSession is a method on authClient, not a standalone export
 */

/**
 * Sign Up with Email and Password
 * Per Context7 docs:
 * ```ts
 * await authClient.signUp.email({
 *   email,
 *   password,
 *   name,
 *   callbackURL: "/dashboard"
 * })
 * ```
 */
export async function signUp(data: {
  email: string
  password: string
  name: string
}) {
  return authClient.signUp.email({
    ...data,
    callbackURL: "/dashboard",
  })
}

/**
 * Sign In with Email and Password
 * Per Context7 docs:
 * ```ts
 * await authClient.signIn.email({
 *   email,
 *   password,
 *   rememberMe: true,
 *   callbackURL: "/dashboard"
 * })
 * ```
 */
export async function signIn(data: {
  email: string
  password: string
  rememberMe?: boolean
}) {
  return authClient.signIn.email({
    ...data,
    callbackURL: "/dashboard",
  })
}

/**
 * Sign Out
 * Per Context7 docs:
 * ```ts
 * await authClient.signOut()
 * ```
 */
export async function signOut() {
  return authClient.signOut({
    fetchOptions: {
      onSuccess: () => {
        // Redirect to home after sign out
        if (typeof window !== "undefined") {
          window.location.href = "/"
        }
      },
    },
  })
}
