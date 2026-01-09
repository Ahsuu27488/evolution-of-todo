/**
 * GET /api/auth/token
 *
 * JWT Token Endpoint for FastAPI Backend Authentication
 *
 * This endpoint:
 * - Retrieves the current Better Auth session
 * - Returns the JWT token from the session (when JWT plugin is enabled)
 * - Requires an active Better Auth session (via httpOnly cookie)
 *
 * Usage:
 *   fetch('/api/auth/token', {
 *     credentials: 'include'  // Include session cookies
 *   }).then(r => r.json()).then(({token}) => {...})
 *
 * Per T005 in tasks.md - Critical for all API client operations
 */

import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

/**
 * GET handler for JWT token retrieval
 *
 * Returns:
 *   200 - { token: "eyJhbG..." } - Active session with JWT
 *   401 - { error: "No active session" } - No session cookie
 *   401 - { error: "No token in session" } - Session exists but no JWT
 *   500 - { error: "Failed to retrieve token" } - Server error
 */
export async function GET() {
  try {
    // Get the session using Better Auth's API method
    // This reads the session cookie from the request headers
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    // No active session - user is not logged in
    if (!session) {
      return NextResponse.json(
        { error: "No active session" },
        { status: 401 }
      )
    }

    // Better Auth JWT plugin stores the token in the session
    // The token may be at session.token or in session.data depending on version
    // We check both locations for maximum compatibility
    const token =
      (session as unknown as { token?: string }).token ||
      (session as unknown as { jwt?: string }).jwt ||
      null

    if (!token) {
      return NextResponse.json(
        { error: "No token in session" },
        { status: 401 }
      )
    }

    // Return the JWT token
    return NextResponse.json({ token })
  } catch (error) {
    // Log error for debugging (development only)
    if (process.env.NODE_ENV === "development") {
      console.error("[JWT Token Endpoint] Error:", error)
    }

    return NextResponse.json(
      { error: "Failed to retrieve token" },
      { status: 500 }
    )
  }
}
