"use server"

/**
 * Server Actions for Task CRUD operations.
 *
 * These actions:
 * - Run on the server (secure)
 * - Use Better Auth JWT tokens for FastAPI authentication
 * - Return structured results with proper error handling
 * - Revalidate cached data after mutations
 *
 * Token Flow:
 * 1. User signs in via Better Auth; session cookie is set
 * 2. Server action calls /api/auth/token with cookies to get JWT
 * 3. Action sends JWT in Authorization: Bearer header to FastAPI
 * 4. FastAPI verifies JWT signature using shared BETTER_AUTH_SECRET
 */

import { revalidatePath } from "next/cache"
import { headers, cookies } from "next/headers"
import { auth } from "@/lib/auth"
import type { Task, TaskCreate, TaskUpdate } from "@/types/task"
import {
  AppError,
  ErrorCode,
  httpStatusToErrorCode,
  generateRequestId,
  logError,
} from "@/lib/errors"

// =============================================================================
// Configuration
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const APP_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"

// =============================================================================
// Types
// =============================================================================

export interface ActionResult<T> {
  success: boolean
  data?: T
  error?: {
    message: string
    code: string
    requestId?: string
  }
}

// =============================================================================
// Authentication Helpers
// =============================================================================

/**
 * Get the current authenticated user's session.
 * Returns null if not authenticated.
 */
async function getAuthSession() {
  try {
    const reqHeaders = await headers()
    const session = await auth.api.getSession({
      headers: reqHeaders,
    })
    return session
  } catch (error) {
    console.error("[Auth] Failed to get session:", error)
    return null
  }
}

/**
 * Generate a JWT token for API authentication.
 *
 * Better Auth JWT plugin exposes /api/auth/token endpoint.
 * We call this endpoint with the user's session cookies to get the JWT.
 */
async function generateJwtToken(): Promise<string | null> {
  try {
    // Get cookies to forward to the JWT endpoint
    const cookieStore = await cookies()
    const cookieHeader = cookieStore
      .getAll()
      .map((c) => `${c.name}=${c.value}`)
      .join("; ")

    // Call Better Auth JWT generation endpoint
    const APP_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"
    const response = await fetch(`${APP_URL}/api/auth/token`, {
      method: "GET",
      headers: {
        Cookie: cookieHeader,
      },
      cache: "no-store",
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error")
      console.error(
        `[Auth] JWT endpoint returned ${response.status}:`,
        errorText
      )
      return null
    }

    const data = await response.json()

    // JWT plugin returns { token: "..." }
    if (!data.token) {
      console.error("[Auth] JWT response missing 'token' field:", data)
      return null
    }

    return data.token
  } catch (error) {
    console.error("[Auth] Failed to generate JWT:", error)
    return null
  }
}

/**
 * Get authenticated user ID and JWT token.
 * Returns null if not authenticated.
 */
async function getAuthData(): Promise<{
  userId: string
  token: string
} | null> {
  // Get session first to verify user is logged in and get user ID
  const session = await getAuthSession()
  if (!session?.user?.id) {
    console.debug("[Auth] No active session")
    return null
  }

  // Generate JWT for API calls
  const token = await generateJwtToken()
  if (!token) {
    console.error("[Auth] Session exists but failed to generate JWT")
    return null
  }

  return {
    userId: session.user.id,
    token,
  }
}

// =============================================================================
// API Call Helper
// =============================================================================

interface ApiCallOptions {
  method?: string
  body?: unknown
}

/**
 * Make an authenticated API call to the FastAPI backend.
 */
async function apiCall<T>(
  endpoint: string,
  authData: { userId: string; token: string },
  options: ApiCallOptions = {}
): Promise<ActionResult<T>> {
  const requestId = generateRequestId()
  const method = options.method || "GET"
  const url = `${API_URL}${endpoint}`

  try {
    console.debug(`[API] ${method} ${endpoint} [request_id=${requestId}]`)

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authData.token}`,
        "X-Request-ID": requestId,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      cache: "no-store",
    })

    // Success
    if (response.ok) {
      const data = await response.json()
      return { success: true, data }
    }

    // Error response
    let errorMessage = `API request failed with status ${response.status}`
    let errorCode = httpStatusToErrorCode(response.status)

    try {
      const errorBody = await response.json()
      errorMessage = errorBody.detail || errorMessage
      if (errorBody.code) {
        errorCode = errorBody.code
      }
    } catch {
      // Ignore JSON parse errors
    }

    const error = new AppError(errorMessage, errorCode, response.status)
    logError(error, { endpoint, method, requestId })

    return {
      success: false,
      error: {
        message: error.getUserMessage(),
        code: errorCode,
        requestId,
      },
    }
  } catch (error) {
    // Network or other errors
    const appError =
      error instanceof TypeError
        ? new AppError(
          "Unable to reach the server. Please check if the backend is running.",
          ErrorCode.NETWORK_ERROR,
          0
        )
        : new AppError(
          error instanceof Error ? error.message : "Unknown error",
          ErrorCode.UNKNOWN,
          500
        )

    logError(appError, { endpoint, method, requestId })

    return {
      success: false,
      error: {
        message: appError.getUserMessage(),
        code: appError.code,
        requestId,
      },
    }
  }
}

// =============================================================================
// Task Actions
// =============================================================================

/**
 * Get all tasks for the current user.
 */
export async function getTasks(): Promise<ActionResult<{
  tasks: Task[]
  total: number
}>> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: {
        message: "Please sign in to view tasks",
        code: ErrorCode.UNAUTHORIZED,
      },
    }
  }

  return apiCall(`/api/tasks`, authData)
}

/**
 * Create a new task.
 */
export async function createTask(
  data: TaskCreate
): Promise<ActionResult<Task>> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: {
        message: "Please sign in to create tasks",
        code: ErrorCode.UNAUTHORIZED,
      },
    }
  }

  const result = await apiCall<Task>(`/api/tasks`, authData, {
    method: "POST",
    body: data,
  })

  if (result.success) {
    revalidatePath("/dashboard")
  }

  return result
}

/**
 * Update an existing task.
 */
export async function updateTask(
  taskId: number,
  data: TaskUpdate
): Promise<ActionResult<Task>> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: {
        message: "Please sign in to update tasks",
        code: ErrorCode.UNAUTHORIZED,
      },
    }
  }

  const result = await apiCall<Task>(
    `/api/tasks/${taskId}`,
    authData,
    {
      method: "PUT",
      body: data,
    }
  )

  if (result.success) {
    revalidatePath("/dashboard")
  }

  return result
}

/**
 * Delete a task.
 */
export async function deleteTask(
  taskId: number
): Promise<ActionResult<{ ok: boolean; message: string }>> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: {
        message: "Please sign in to delete tasks",
        code: ErrorCode.UNAUTHORIZED,
      },
    }
  }

  const result = await apiCall<{ ok: boolean; message: string }>(
    `/api/tasks/${taskId}`,
    authData,
    { method: "DELETE" }
  )

  if (result.success) {
    revalidatePath("/dashboard")
  }

  return result
}

/**
 * Toggle task completion status.
 */
export async function toggleTaskComplete(
  taskId: number
): Promise<ActionResult<Task>> {
  const authData = await getAuthData()
  if (!authData) {
    return {
      success: false,
      error: {
        message: "Please sign in to update tasks",
        code: ErrorCode.UNAUTHORIZED,
      },
    }
  }

  const result = await apiCall<Task>(
    `/api/tasks/${taskId}/complete`,
    authData,
    { method: "PATCH" }
  )

  if (result.success) {
    revalidatePath("/dashboard")
  }

  return result
}
