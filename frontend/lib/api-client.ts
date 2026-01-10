/**
 * API client for FastAPI backend communication.
 *
 * Features:
 * - Automatic JWT token retrieval from Better Auth session
 * - Comprehensive error handling with typed errors
 * - Automatic retry for transient failures
 * - Request timeout handling
 * - Request ID tracking for debugging
 *
 * Per T007-T015: Refactored to remove userId parameters (inferred from JWT)
 * and add automatic token fetching via /api/auth/token endpoint.
 */

import type { Task, TaskCreate, TaskList, TaskUpdate } from "@/types/task"
import {
  ApiError,
  ErrorCode,
  httpStatusToErrorCode,
  generateRequestId,
  logError,
  type Result,
  ok,
  err,
} from "./errors"

// =============================================================================
// Configuration
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
const APP_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"
const REQUEST_TIMEOUT = 15000 // 15 seconds
const MAX_RETRIES = 2
const RETRY_DELAY_MS = 500

// =============================================================================
// Types
// =============================================================================

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown
  timeout?: number
  retries?: number
}

interface ApiResponse<T> {
  data: T
  requestId: string
}

// =============================================================================
// API Client Class
// =============================================================================

class ApiClient {
  private baseUrl: string
  private appUrl: string

  constructor(baseUrl: string, appUrl: string) {
    this.baseUrl = baseUrl
    this.appUrl = appUrl
  }

  /**
   * Get JWT token from Better Auth session.
   *
   * Calls /api/auth/token endpoint which:
   * 1. Reads the session cookie from the request
   * 2. Returns the JWT token from the session
   *
   * Per T007 - Private method for automatic token retrieval
   *
   * @returns JWT token or null if not authenticated
   */
  private async getAuthToken(): Promise<string | null> {
    try {
      const response = await fetch(`${this.appUrl}/api/auth/token`, {
        method: "GET",
        credentials: "include", // Include cookies
        cache: "no-store",
      })

      if (!response.ok) {
        return null
      }

      const data = await response.json()
      return data.token || null
    } catch {
      return null
    }
  }

  /**
   * Make an authenticated API request with error handling and retries.
   *
   * Per T015: Auto-fetches token instead of requiring it as parameter.
   *
   * @param endpoint - API endpoint path (e.g., "/api/tasks")
   * @param options - Request options (method, body, timeout, retries)
   * @returns Result<T> with data or error
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<Result<ApiResponse<T>>> {
    const requestId = generateRequestId()
    const method = options.method || "GET"
    const url = `${this.baseUrl}${endpoint}`
    const timeout = options.timeout || REQUEST_TIMEOUT
    const maxRetries = options.retries ?? MAX_RETRIES

    // Get JWT token for authentication
    const token = await this.getAuthToken()

    if (!token) {
      return err(
        new ApiError(
          "No active session. Please sign in.",
          ErrorCode.UNAUTHORIZED,
          401,
          endpoint,
          method,
          requestId
        )
      )
    }

    let lastError: ApiError | null = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      try {
        if (attempt > 0) {
          // Exponential backoff for retries
          const delay = RETRY_DELAY_MS * Math.pow(2, attempt - 1)
          await new Promise((resolve) => setTimeout(resolve, delay))
        }

        const response = await fetch(url, {
          ...options,
          method,
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            "X-Request-ID": requestId,
            ...options.headers,
          },
          body: options.body ? JSON.stringify(options.body) : undefined,
        })

        clearTimeout(timeoutId)

        // Success response
        if (response.ok) {
          const data = await response.json()
          return ok({ data, requestId })
        }

        // Error response - parse error details
        let errorMessage = `Request failed with status ${response.status}`
        let errorCode = httpStatusToErrorCode(response.status)
        let serverRequestId = response.headers.get("X-Request-ID") || requestId

        try {
          const errorBody = await response.json()
          errorMessage = errorBody.detail || errorMessage
          if (errorBody.code) {
            errorCode = errorBody.code as typeof ErrorCode[keyof typeof ErrorCode]
          }
          if (errorBody.request_id) {
            serverRequestId = errorBody.request_id
          }
        } catch {
          // Ignore JSON parse errors, use defaults
        }

        lastError = new ApiError(
          errorMessage,
          errorCode,
          response.status,
          endpoint,
          method,
          serverRequestId
        )

        // Don't retry client errors (4xx) except timeouts
        if (response.status >= 400 && response.status < 500 && response.status !== 408) {
          break
        }
      } catch (error) {
        clearTimeout(timeoutId)

        // Handle network errors and timeouts
        if (error instanceof DOMException && error.name === "AbortError") {
          lastError = new ApiError(
            "Request timed out",
            ErrorCode.TIMEOUT,
            408,
            endpoint,
            method,
            requestId
          )
        } else if (error instanceof TypeError) {
          lastError = new ApiError(
            "Network error: Unable to reach server",
            ErrorCode.NETWORK_ERROR,
            0,
            endpoint,
            method,
            requestId
          )
          // Network errors are retryable
          continue
        } else {
          lastError = new ApiError(
            error instanceof Error ? error.message : "Unknown error",
            ErrorCode.UNKNOWN,
            500,
            endpoint,
            method,
            requestId
          )
          break
        }
      }
    }

    // All retries exhausted
    if (lastError) {
      logError(lastError, { endpoint, method, attempts: maxRetries + 1 })
      return err(lastError)
    }

    // Should never reach here
    return err(
      new ApiError("Request failed", ErrorCode.UNKNOWN, 500, endpoint, method, requestId)
    )
  }

  // ===========================================================================
  // Task API Methods
  //
  // Per T008-T013: Removed userId parameter - inferred from JWT token
  // ===========================================================================

  /**
   * Get all tasks for the current user.
   *
   * Per T008: userId parameter removed
   */
  async getTasks(filters?: {
    status?: "all" | "pending" | "completed"
    priority?: "HIGH" | "MEDIUM" | "LOW"
    page?: number
    per_page?: number
  }): Promise<Result<TaskList>> {
    const params = new URLSearchParams()
    if (filters?.status && filters.status !== "all") {
      params.set("status", filters.status)
    }
    if (filters?.priority) {
      params.set("priority", filters.priority)
    }
    if (filters?.page) {
      params.set("page", String(filters.page))
    }
    if (filters?.per_page) {
      params.set("per_page", String(filters.per_page))
    }

    const query = params.toString()
    const endpoint = `/api/tasks${query ? `?${query}` : ""}`

    const result = await this.request<TaskList>(endpoint)
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Get a single task by ID.
   *
   * Per T009: userId parameter removed
   */
  async getTask(taskId: number): Promise<Result<Task>> {
    const result = await this.request<Task>(`/api/tasks/${taskId}`)
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Create a new task.
   *
   * Per T010: userId parameter removed
   */
  async createTask(data: TaskCreate): Promise<Result<Task>> {
    const result = await this.request<Task>(`/api/tasks`, {
      method: "POST",
      body: data,
    })
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Update an existing task.
   *
   * Per T011: userId parameter removed
   */
  async updateTask(
    taskId: number,
    data: TaskUpdate
  ): Promise<Result<Task>> {
    const result = await this.request<Task>(`/api/tasks/${taskId}`, {
      method: "PUT",
      body: data,
    })
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Delete a task.
   *
   * Per T012: userId parameter removed
   */
  async deleteTask(
    taskId: number
  ): Promise<Result<{ ok: boolean; message: string }>> {
    const result = await this.request<{ ok: boolean; message: string }>(
      `/api/tasks/${taskId}`,
      { method: "DELETE" }
    )
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Toggle task completion status.
   *
   * Per T013: userId parameter removed
   */
  async toggleTaskComplete(
    taskId: number
  ): Promise<Result<Task>> {
    const result = await this.request<Task>(
      `/api/tasks/${taskId}/complete`,
      { method: "PATCH" }
    )
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Search tasks by query string.
   */
  async searchTasks(query: string): Promise<Result<TaskList>> {
    const result = await this.request<TaskList>(
      `/api/tasks/search?q=${encodeURIComponent(query)}`
    )
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Get task audit logs.
   */
  async getTaskLogs(taskId: number): Promise<Result<Array<{
    id: number
    task_id: number
    user_id: string
    action: string
    changed_fields: Record<string, unknown>
    created_at: string
  }>>> {
    const result = await this.request<Array<{
      id: number
      task_id: number
      user_id: string
      action: string
      changed_fields: Record<string, unknown>
      created_at: string
    }>>(`/api/tasks/${taskId}/logs`)
    if (!result.success) return result
    return ok(result.data.data)
  }

  /**
   * Health check endpoint.
   *
   * Per T014: Changed from /health to /api/health to match backend
   */
  async healthCheck(): Promise<Result<{ status: string; timestamp: string; version: string }>> {
    const requestId = generateRequestId()
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        headers: { "X-Request-ID": requestId },
      })

      if (response.ok) {
        const data = await response.json()
        return ok(data)
      }

      return err(
        new ApiError(
          "Health check failed",
          ErrorCode.SERVER_ERROR,
          response.status,
          "/api/health",
          "GET",
          requestId
        )
      )
    } catch {
      return err(
        new ApiError(
          "Cannot reach backend server",
          ErrorCode.CONNECTION_REFUSED,
          0,
          "/api/health",
          "GET",
          requestId
        )
      )
    }
  }
}

// =============================================================================
// Singleton Export
// =============================================================================

export const api = new ApiClient(API_URL, APP_URL)

// =============================================================================
// Re-export types for convenience
// =============================================================================

export type { Task, TaskCreate, TaskList, TaskUpdate }

// =============================================================================
// JWT Expiry Handler (T021)
// =============================================================================

/**
 * Handle JWT expiry by redirecting to login with "Session expired" message.
 *
 * @param error - The API error that occurred
 * @returns void - Redirects to login if token expired
 */
export function handleJwtExpiry(error: ApiError): void {
  if (
    error.code === ErrorCode.SESSION_EXPIRED ||
    error.code === ErrorCode.UNAUTHORIZED ||
    error.statusCode === 401
  ) {
    // Store the session expired message for the login page to display
    if (typeof window !== "undefined") {
      sessionStorage.setItem("sessionMessage", "Session expired. Please sign in again.")
      // Redirect to login page
      window.location.href = "/login?reason=session_expired"
    }
  }
}

/**
 * Get and clear the session message (e.g., "Session expired").
 * Used by the login page to display context-specific messages.
 *
 * Per T022 - Session message utility for login page context
 *
 * @returns The session message or null
 */
export function getSessionMessage(): string | null {
  if (typeof window === "undefined") return null

  const message = sessionStorage.getItem("sessionMessage")
  if (message) {
    sessionStorage.removeItem("sessionMessage")
    return message
  }
  return null
}
