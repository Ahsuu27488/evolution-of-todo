/**
 * Better Auth API route handler.
 * This catch-all route handles all authentication endpoints.
 *
 * Better Auth requires all HTTP methods to be exported for proper operation.
 * The toNextJsHandler utility creates handlers that work with Next.js App Router.
 */

import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

// Export all HTTP methods that Better Auth might use
// Including OPTIONS for CORS preflight requests
export const { GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD } = toNextJsHandler(auth)
