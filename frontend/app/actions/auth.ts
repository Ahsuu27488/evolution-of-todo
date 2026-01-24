"use server"

/**
 * Server Actions for Authentication
 *
 * These actions handle:
 * - Storing JWT tokens in httpOnly cookies after sign-in/sign-up
 * - Clearing cookies on sign-out
 * - Getting current session from cookies
 */

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import type { User } from "@/lib/auth-client"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const JWT_COOKIE_NAME = "auth_token"

// =============================================================================
// Types
// =============================================================================

export interface AuthResult {
  success: boolean
  error?: string
  user?: User
}

export interface Session {
  user: User
}

// =============================================================================
// Auth Actions
// =============================================================================

/**
 * Sign in action - calls backend and stores JWT in httpOnly cookie
 */
export async function signInAction(
  email: string,
  password: string
): Promise<AuthResult> {
  try {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Sign in failed" }))
      return {
        success: false,
        error: error.detail || "Invalid credentials",
      }
    }

    const data = await response.json()

    // Store JWT in httpOnly cookie
    const cookieStore = await cookies()
    cookieStore.set(JWT_COOKIE_NAME, data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
    })

    return {
      success: true,
      user: data.user,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Network error",
    }
  }
}

/**
 * [T035] Sign up action - calls backend with first_name and last_name
 */
export async function signUpAction(
  email: string,
  password: string,
  firstName: string,
  lastName?: string
): Promise<AuthResult> {
  try {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, first_name: firstName, last_name: lastName }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Sign up failed" }))
      return {
        success: false,
        error: error.detail || "Sign up failed",
      }
    }

    // After signup, automatically sign in to get JWT
    return signInAction(email, password)
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Network error",
    }
  }
}

/**
 * Sign out action - clears the auth cookie
 */
export async function signOutAction(): Promise<{ success: boolean }> {
  const cookieStore = await cookies()
  cookieStore.delete(JWT_COOKIE_NAME)
  return { success: true }
}

/**
 * Get current session from cookie
 */
export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get(JWT_COOKIE_NAME)?.value

  if (!token) {
    return null
  }

  // Verify token by calling backend
  try {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    })

    if (!response.ok) {
      return null
    }

    const user = await response.json()
    return { user }
  } catch {
    return null
  }
}

/**
 * Require authentication - redirect to login if not authenticated
 */
export async function requireAuth(): Promise<Session> {
  const session = await getSession()

  if (!session) {
    redirect("/login")
  }

  return session
}

/**
 * Update user profile
 */
export async function updateProfileAction(
  firstName?: string,
  lastName?: string,
): Promise<AuthResult> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: "Not authenticated",
    }
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/me`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authData.token}`,
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
      }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Profile update failed" }))
      return {
        success: false,
        error: error.detail || "Profile update failed",
      }
    }

    const updatedUser = await response.json()

    return {
      success: true,
      user: updatedUser,
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Network error",
    }
  }
}

/**
 * Helper to get auth data (token)
 */
async function getAuthData() {
  const cookieStore = await cookies()
  const token = cookieStore.get(JWT_COOKIE_NAME)?.value

  if (!token) {
    return null
  }

  return { token }
}
