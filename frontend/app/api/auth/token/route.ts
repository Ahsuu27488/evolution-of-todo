/**
 * GET /api/auth/token
 *
 * JWT Token Endpoint for FastAPI Backend Authentication
 *
 * This endpoint returns the JWT token from the backend auth system.
 * The token is stored in the 'auth_token' httpOnly cookie after login.
 *
 * Usage:
 *   fetch('/api/auth/token', {
 *     credentials: 'include'  // Include session cookies
 *   }).then(r => r.json()).then(({token}) => {...})
 */

import { headers } from "next/headers"
import { NextResponse } from "next/server"

/**
 * GET handler for JWT token retrieval
 *
 * Returns:
 *   200 - { token: "eyJhbG..." } - JWT from backend auth
 *   401 - { error: "No active session" } - No auth_token cookie
 *   500 - { error: "Failed to retrieve token" } - Server error
 */
export async function GET() {
  try {
    const cookies = (await headers()).get("cookie") || ""

    // Parse the auth_token cookie from the Cookie header
    const authTokenMatch = cookies.match(/auth_token=([^;]+)/)

    if (!authTokenMatch) {
      return NextResponse.json(
        { error: "No active session" },
        { status: 401 }
      )
    }

    const token = decodeURIComponent(authTokenMatch[1])

    // Return the JWT token from the backend auth system
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
