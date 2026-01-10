/**
 * Better Auth API route handler.
 * This catch-all route handles all authentication endpoints.
 *
 * Better Auth requires all HTTP methods to be exported for proper operation.
 * The toNextJsHandler utility creates handlers that work with Next.js App Router.
 */

import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

// Export only the HTTP methods that Better Auth provides
const handler = toNextJsHandler(auth)
export const { GET, POST, PUT, DELETE, PATCH } = handler
