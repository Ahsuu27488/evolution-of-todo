"use server"

/**
 * Server Actions for Task CRUD operations.
 *
 * Updated to use backend-centric authentication:
 * - Frontend calls backend /api/auth/* for sign-in/up
 * - Backend returns JWT token
 * - Frontend stores token in localStorage
 * - Server Actions read token from cookies and forward to backend
 *
 * Token Flow:
 * 1. User signs in via frontend → backend returns JWT
 * 2. Frontend stores JWT in httpOnly cookie via server action
 * 3. Server Actions read JWT from cookie
 * 4. Server Actions call backend with JWT in Authorization header
 */

import { revalidatePath } from "next/cache"
import { cookies } from "next/headers"
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
const JWT_COOKIE_NAME = "auth_token"

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
 * Get the JWT token from the httpOnly cookie.
 * Returns null if not authenticated.
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get(JWT_COOKIE_NAME)?.value
    return token || null
  } catch (error) {
    logError(
      error instanceof Error ? new AppError(error.message, ErrorCode.UNKNOWN, 500) : new AppError("Unknown auth error", ErrorCode.UNKNOWN, 500),
      { context: "getAuthToken" }
    )
    return null
  }
}

/**
 * Get authenticated user data from backend.
 * Returns null if not authenticated.
 */
async function getAuthData(): Promise<{
  userId: string
  token: string
} | null> {
  const token = await getAuthToken()
  if (!token) {
    return null
  }

  // Optionally verify token by calling /api/auth/me
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
    return {
      userId: user.id,
      token,
    }
  } catch {
    return null
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
