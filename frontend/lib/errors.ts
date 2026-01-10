/**
 * Centralized error handling utilities for the frontend.
 *
 * Provides:
 * - Typed error classes for different error scenarios
 * - Error formatting for user-friendly messages
 * - Request ID tracking for debugging
 * - Error logging with context
 */

// =============================================================================
// Error Types
// =============================================================================

/**
 * Error codes for programmatic handling
 */
export const ErrorCode = {
    // Authentication errors
    UNAUTHORIZED: "UNAUTHORIZED",
    SESSION_EXPIRED: "SESSION_EXPIRED",
    INVALID_CREDENTIALS: "INVALID_CREDENTIALS",

    // Authorization errors
    FORBIDDEN: "FORBIDDEN",
    NOT_OWNER: "NOT_OWNER",

    // Resource errors
    NOT_FOUND: "NOT_FOUND",
    ALREADY_EXISTS: "ALREADY_EXISTS",

    // Validation errors
    VALIDATION_ERROR: "VALIDATION_ERROR",
    INVALID_INPUT: "INVALID_INPUT",

    // Server errors
    SERVER_ERROR: "SERVER_ERROR",
    SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",

    // Network errors
    NETWORK_ERROR: "NETWORK_ERROR",
    TIMEOUT: "TIMEOUT",
    CONNECTION_REFUSED: "CONNECTION_REFUSED",

    // Unknown
    UNKNOWN: "UNKNOWN",
} as const

export type ErrorCodeType = (typeof ErrorCode)[keyof typeof ErrorCode]

// =============================================================================
// Custom Error Classes
// =============================================================================

/**
 * Base application error with code and context
 */
export class AppError extends Error {
    public readonly code: ErrorCodeType
    public readonly statusCode: number
    public readonly context?: Record<string, unknown>
    public readonly requestId?: string
    public readonly timestamp: Date

    constructor(
        message: string,
        code: ErrorCodeType = ErrorCode.UNKNOWN,
        statusCode: number = 500,
        context?: Record<string, unknown>,
        requestId?: string
    ) {
        super(message)
        this.name = "AppError"
        this.code = code
        this.statusCode = statusCode
        this.context = context
        this.requestId = requestId
        this.timestamp = new Date()

        // Maintains proper stack trace for where error was thrown
        Error.captureStackTrace?.(this, AppError)
    }

    /**
     * Convert to a plain object for logging/serialization
     */
    toJSON(): Record<string, unknown> {
        return {
            name: this.name,
            message: this.message,
            code: this.code,
            statusCode: this.statusCode,
            context: this.context,
            requestId: this.requestId,
            timestamp: this.timestamp.toISOString(),
        }
    }

    /**
     * Get a user-friendly error message
     */
    getUserMessage(): string {
        return getUserFriendlyMessage(this.code, this.message)
    }
}

/**
 * API-specific error for backend communication failures
 */
export class ApiError extends AppError {
    public readonly endpoint: string
    public readonly method: string

    constructor(
        message: string,
        code: ErrorCodeType,
        statusCode: number,
        endpoint: string,
        method: string,
        requestId?: string
    ) {
        super(message, code, statusCode, { endpoint, method }, requestId)
        this.name = "ApiError"
        this.endpoint = endpoint
        this.method = method
    }
}

/**
 * Authentication error for auth-related failures
 */
export class AuthError extends AppError {
    constructor(message: string, code: ErrorCodeType = ErrorCode.UNAUTHORIZED) {
        super(message, code, 401)
        this.name = "AuthError"
    }
}

// =============================================================================
// Error Mapping
// =============================================================================

/**
 * Map HTTP status codes to error codes
 */
export function httpStatusToErrorCode(status: number): ErrorCodeType {
    switch (status) {
        case 400:
            return ErrorCode.VALIDATION_ERROR
        case 401:
            return ErrorCode.UNAUTHORIZED
        case 403:
            return ErrorCode.FORBIDDEN
        case 404:
            return ErrorCode.NOT_FOUND
        case 408:
            return ErrorCode.TIMEOUT
        case 409:
            return ErrorCode.ALREADY_EXISTS
        case 422:
            return ErrorCode.INVALID_INPUT
        case 429:
            return ErrorCode.SERVICE_UNAVAILABLE
        case 500:
        case 502:
        case 503:
        case 504:
            return ErrorCode.SERVER_ERROR
        default:
            return ErrorCode.UNKNOWN
    }
}

/**
 * Get user-friendly error messages
 */
export function getUserFriendlyMessage(
    code: ErrorCodeType,
    fallback?: string
): string {
    const messages: Record<ErrorCodeType, string> = {
        [ErrorCode.UNAUTHORIZED]: "Please sign in to continue",
        [ErrorCode.SESSION_EXPIRED]: "Your session has expired. Please sign in again",
        [ErrorCode.INVALID_CREDENTIALS]: "Invalid email or password",
        [ErrorCode.FORBIDDEN]: "You don't have permission to do this",
        [ErrorCode.NOT_OWNER]: "This resource belongs to another user",
        [ErrorCode.NOT_FOUND]: "The requested item was not found",
        [ErrorCode.ALREADY_EXISTS]: "This item already exists",
        [ErrorCode.VALIDATION_ERROR]: "Please check your input and try again",
        [ErrorCode.INVALID_INPUT]: "The provided data is invalid",
        [ErrorCode.SERVER_ERROR]: "Something went wrong. Please try again later",
        [ErrorCode.SERVICE_UNAVAILABLE]: "Service is temporarily unavailable",
        [ErrorCode.NETWORK_ERROR]: "Unable to connect. Please check your internet connection",
        [ErrorCode.TIMEOUT]: "Request timed out. Please try again",
        [ErrorCode.CONNECTION_REFUSED]: "Could not reach the server",
        [ErrorCode.UNKNOWN]: fallback || "An unexpected error occurred",
    }

    return messages[code] || fallback || messages[ErrorCode.UNKNOWN]
}

// =============================================================================
// Error Parsing
// =============================================================================

/**
 * Parse error response from FastAPI backend
 */
export interface BackendErrorResponse {
    detail: string
    code?: string
    request_id?: string
}

/**
 * Parse an error from various sources into an AppError
 */
export function parseError(
    error: unknown,
    context?: { endpoint?: string; method?: string }
): AppError {
    // Already an AppError
    if (error instanceof AppError) {
        return error
    }

    // Network/fetch errors
    if (error instanceof TypeError) {
        // Typically network errors like "Failed to fetch"
        return new ApiError(
            "Network error: Unable to reach the server",
            ErrorCode.NETWORK_ERROR,
            0,
            context?.endpoint || "unknown",
            context?.method || "unknown"
        )
    }

    // DOMException for aborted requests
    if (error instanceof DOMException && error.name === "AbortError") {
        return new ApiError(
            "Request was cancelled",
            ErrorCode.TIMEOUT,
            408,
            context?.endpoint || "unknown",
            context?.method || "unknown"
        )
    }

    // Generic Error
    if (error instanceof Error) {
        return new AppError(error.message, ErrorCode.UNKNOWN, 500)
    }

    // String error
    if (typeof error === "string") {
        return new AppError(error, ErrorCode.UNKNOWN, 500)
    }

    // Unknown error type
    return new AppError("An unexpected error occurred", ErrorCode.UNKNOWN, 500)
}

// =============================================================================
// Request ID Utilities
// =============================================================================

/**
 * Generate a unique request ID for tracking
 */
export function generateRequestId(): string {
    const timestamp = Date.now().toString(36)
    const random = Math.random().toString(36).substring(2, 8)
    return `req_${timestamp}_${random}`
}

// =============================================================================
// Logging Utilities
// =============================================================================

/**
 * Log an error with full context
 */
export function logError(error: AppError | Error, additionalContext?: Record<string, unknown>): void {
    const isAppError = error instanceof AppError

    const logData = {
        name: error.name,
        message: error.message,
        code: isAppError ? (error as AppError).code : "UNKNOWN",
        statusCode: isAppError ? (error as AppError).statusCode : undefined,
        requestId: isAppError ? (error as AppError).requestId : undefined,
        context: isAppError ? (error as AppError).context : undefined,
        additionalContext,
        stack: process.env.NODE_ENV === "development" ? error.stack : undefined,
        timestamp: new Date().toISOString(),
    }

    // In development, log full error
    if (process.env.NODE_ENV === "development") {
        console.error("[Error]", JSON.stringify(logData, null, 2))
    } else {
        // In production, log minimal info
        console.error(`[Error] ${logData.code}: ${logData.message} (${logData.requestId || "no-request-id"})`)
    }
}

// =============================================================================
// Result Type for Operations
// =============================================================================

/**
 * Result type for operations that can fail
 * Provides a clean way to handle success/error states
 */
export type Result<T, E = AppError> =
    | { success: true; data: T; error?: never }
    | { success: false; data?: never; error: E }

/**
 * Create a success result
 */
export function ok<T>(data: T): Result<T> {
    return { success: true, data }
}

/**
 * Create an error result
 */
export function err<E extends AppError>(error: E): Result<never, E> {
    return { success: false, error }
}
