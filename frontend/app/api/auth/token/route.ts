/**
 * GET /api/auth/token
 *
 * JWT Token Endpoint for FastAPI Backend Authentication
 *
 * This endpoint generates a JWT token for the current session that can be
 * used to authenticate with the FastAPI backend.
 *
 * Usage:
 *   fetch('/api/auth/token', {
 *     credentials: 'include'  // Include session cookies
 *   }).then(r => r.json()).then(({token}) => {...})
 */

import { createHmac } from "node:crypto"
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { NextResponse } from "next/server"

const SECRET_KEY = process.env.BETTER_AUTH_SECRET!

/**
 * Simple base64url encoding without padding (RFC 7519)
 */
function base64urlEncode(data: string): string {
  const base64 = Buffer.from(data).toString("base64")
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "")
}

/**
 * Create JWT header and payload, then sign with HMAC-SHA256
 */
async function createJWT(payload: Record<string, unknown>, secret: string): Promise<string> {
  const header = { alg: "HS256", typ: "JWT" }

  const encodedHeader = base64urlEncode(JSON.stringify(header))
  const encodedPayload = base64urlEncode(JSON.stringify(payload))
  const data = `${encodedHeader}.${encodedPayload}`

  // Sign with HMAC-SHA256
  const signature = createHmac("sha256", secret)
    .update(data)
    .digest("base64url")

  return `${data}.${signature}`
}

/**
 * GET handler for JWT token generation
 *
 * Returns:
 *   200 - { token: "eyJhbG..." } - Generated JWT for current user
 *   401 - { error: "No active session" } - No session cookie
 *   500 - { error: "Failed to generate token" } - Server error
 */
export async function GET() {
  try {
    // Get the session using Better Auth's API method
    const session = await auth.api.getSession({
      headers: await headers(),
    })

    // No active session - user is not logged in
    if (!session || !session.user) {
      return NextResponse.json(
        { error: "No active session" },
        { status: 401 }
      )
    }

    // Get session ID - Better Auth stores it in different places depending on version
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const sessionId = (session as any).session?.id || (session as any).id || session.user.id

    // Calculate expiration (7 days from now)
    const now = Math.floor(Date.now() / 1000)
    const exp = now + 7 * 24 * 60 * 60

    // Generate JWT token with the same secret as Better Auth
    const token = await createJWT({
      sub: session.user.id,        // User ID (subject) - REQUIRED by backend
      email: session.user.email,   // User email
      name: session.user.name,     // User name
      sid: sessionId,              // Session ID
      iat: now,                    // Issued at
      exp,                        // Expiration (7 days)
    }, SECRET_KEY)

    // Return the JWT token
    return NextResponse.json({ token })
  } catch (error) {
    // Log error for debugging (development only)
    if (process.env.NODE_ENV === "development") {
      console.error("[JWT Token Endpoint] Error:", error)
    }

    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    )
  }
}
