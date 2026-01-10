/**
 * Backend-centric Auth Client
 *
 * This client handles authentication by calling the FastAPI backend endpoints.
 * All auth operations (signup, signin, signout) flow through the backend.
 *
 * Architecture:
 * - Frontend calls backend /api/auth/* endpoints
 * - Backend manages users in database and issues JWT tokens
 * - Frontend stores JWT for subsequent API calls
 *
 * JWT Flow:
 * 1. POST /api/auth/signup → Creates user, returns JWT
 * 2. POST /api/auth/signin → Validates credentials, returns JWT
 * 3. Frontend stores JWT in localStorage
 * 4. All API calls include: Authorization: Bearer <JWT>
 */

// =============================================================================
// Configuration
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// =============================================================================
// Types
// =============================================================================

export interface User {
  id: string
  email: string
  name: string
  created_at: string
}

export interface Session {
  user: User
  token: string
}

export interface SignInCredentials {
  email: string
  password: string
}

export interface SignUpCredentials extends SignInCredentials {
  name: string
}

export interface AuthResult {
  success: boolean
  data?: Session
  error?: string
}

// =============================================================================
// Local Storage Helpers
// =============================================================================

const SESSION_KEY = "auth_session"
const TOKEN_KEY = "auth_token"

function saveSession(session: Session): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))
    localStorage.setItem(TOKEN_KEY, session.token)
  }
}

function getSession(): Session | null {
  if (typeof window !== "undefined") {
    const data = localStorage.getItem(SESSION_KEY)
    if (data) {
      try {
        return JSON.parse(data)
      } catch {
        return null
      }
    }
  }
  return null
}

function clearSession(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(SESSION_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }
}

// =============================================================================
// Auth Client
// =============================================================================

/**
 * Sign up a new user
 */
export async function signUp(credentials: SignUpCredentials): Promise<AuthResult> {
  try {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Signup failed" }))
      return {
        success: false,
        error: error.detail || error.message || "Signup failed",
      }
    }

    await response.json() // Parse user data but use signIn response instead

    // After signup, automatically sign in to get token
    return signIn({ email: credentials.email, password: credentials.password })
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Network error",
    }
  }
}

/**
 * Sign in with email and password
 */
export async function signIn(credentials: SignInCredentials): Promise<AuthResult> {
  try {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Sign in failed" }))
      return {
        success: false,
        error: error.detail || error.message || "Invalid credentials",
      }
    }

    const data = await response.json()
    const session: Session = {
      user: data.user,
      token: data.access_token,
    }

    saveSession(session)
    return { success: true, data: session }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Network error",
    }
  }
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  try {
    const session = getSession()
    if (session) {
      await fetch(`${API_URL}/api/auth/signout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.token}`,
        },
      })
    }
  } catch {
    // Ignore signout API errors
  } finally {
    clearSession()
  }
}

/**
 * Get current session
 */
export function getClientSession(): Session | null {
  return getSession()
}

/**
 * Get current user
 */
export function getCurrentUser(): User | null {
  const session = getSession()
  return session?.user || null
}

/**
 * Get JWT token for API calls
 */
export function getAuthToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_KEY)
  }
  return null
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getSession() !== null
}

// =============================================================================
// React Hook (for backward compatibility)
// =============================================================================

/**
 * Simple session hook for React components
 * Note: This won't auto-update like Better Auth's hook
 */
export function useSession() {
  const session = getSession()

  return {
    data: session,
    isPending: false,
    error: null,
  }
}
