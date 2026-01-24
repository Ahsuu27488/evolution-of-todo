/**
 * User Schema Type Definitions
 *
 * Generated from OpenAPI specification for authentication endpoints
 * Feature: 010-loading-states-user-profile
 *
 * This file defines TypeScript interfaces for User entity with first/last name support
 */

/**
 * User creation request payload
 */
export interface UserCreateRequest {
  email: string
  password: string
  firstName: string
  lastName?: string | null
}

/**
 * User public profile (returned by API)
 */
export interface UserPublic {
  id: string
  email: string
  firstName: string | null
  lastName: string | null
  displayName: string
  createdAt: string
}

/**
 * Authentication response
 */
export interface AuthResponse {
  access_token: string
  token_type: 'bearer'
  user: UserPublic
}

/**
 * Validation error response
 */
export interface ValidationError {
  detail: string
  errors?: ValidationErrorField[]
}

export interface ValidationErrorField {
  field: string
  message: string
}

/**
 * Generic error response
 */
export interface ErrorResponse {
  detail: string
}

/**
 * Sign in request payload
 */
export interface SignInRequest {
  email: string
  password: string
}

/**
 * Token response (from /api/auth/token)
 */
export interface TokenResponse {
  token: string
  user: UserPublic
}

/**
 * User type for frontend use
 * Combines API types with display helpers
 */
export interface User extends UserPublic {
  // Additional computed properties can be added here
}

/**
 * Helper function to get display name with fallbacks
 *
 * Priority:
 * 1. displayName (computed by backend)
 * 2. firstName + lastName
 * 3. firstName
 * 4. email
 *
 * @param user - User object
 * @returns Display name string
 */
export function getDisplayName(user: UserPublic): string {
  if (user.displayName) {
    return user.displayName
  }

  if (user.firstName && user.lastName) {
    return `${user.firstName} ${user.lastName}`
  }

  if (user.firstName) {
    return user.firstName
  }

  return user.email
}

/**
 * Validate user input on frontend
 *
 * @param data - Partial user data
 * @returns Validation result
 */
export interface ValidationResult {
  valid: boolean
  errors: Record<string, string>
}

export function validateUserInput(data: Partial<UserCreateRequest>): ValidationResult {
  const errors: Record<string, string> = {}

  // Email validation
  if (data.email !== undefined) {
    if (!data.email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      errors.email = 'Invalid email format'
    } else if (data.email.length > 255) {
      errors.email = 'Email must be 255 characters or less'
    }
  }

  // Password validation
  if (data.password !== undefined) {
    if (!data.password) {
      errors.password = 'Password is required'
    } else if (data.password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    } else if (data.password.length > 100) {
      errors.password = 'Password must be 100 characters or less'
    }
  }

  // First name validation
  if (data.firstName !== undefined) {
    if (!data.firstName) {
      errors.firstName = 'First name is required'
    } else if (data.firstName.length === 0) {
      errors.firstName = 'First name cannot be empty'
    } else if (data.firstName.length > 50) {
      errors.firstName = 'First name must be 50 characters or less'
    } else if (/<[^>]*>/.test(data.firstName)) {
      errors.firstName = 'Invalid characters detected'
    } else if (data.firstName !== data.firstName.trim()) {
      errors.firstName = 'First name cannot start or end with spaces'
    }
  }

  // Last name validation (optional)
  if (data.lastName !== undefined && data.lastName !== null) {
    if (data.lastName.length > 50) {
      errors.lastName = 'Last name must be 50 characters or less'
    } else if (/<[^>]*>/.test(data.lastName)) {
      errors.lastName = 'Invalid characters detected'
    } else if (data.lastName !== data.lastName.trim()) {
      errors.lastName = 'Last name cannot start or end with spaces'
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  }
}

/**
 * Type guard to check if error is validation error
 */
export function isValidationError(error: unknown): error is ValidationError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    ('errors' in error || !('detail' in error))
  )
}

/**
 * API client error type
 */
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public detail: string,
    public errors?: ValidationErrorField[]
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

/**
 * Type for signup form state
 */
export interface SignupFormState {
  email: string
  password: string
  confirmPassword: string
  firstName: string
  lastName: string
  errors: Record<string, string>
  isLoading: boolean
}

/**
 * Type for login form state
 */
export interface LoginFormState {
  email: string
  password: string
  error: string | null
  isLoading: boolean
}

/**
 * Loading state for dashboard
 */
export interface DashboardLoadingState {
  isLoadingTasks: boolean
  isInitialLoad: boolean
  minimumDisplayElapsed: boolean
  error: string | null
  retryCount: number
}

/**
 * User context type
 */
export interface UserContextValue {
  user: UserPublic | null
  isLoading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (data: UserCreateRequest) => Promise<void>
  signOut: () => Promise<void>
  refresh: () => Promise<void>
}
