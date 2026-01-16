import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

/**
 * Middleware for route protection.
 * Redirects unauthenticated users to login for protected routes.
 *
 * Checks for either:
 * - "auth_token" cookie (backend JWT auth)
 * - "better-auth.session_token" cookie (Better Auth)
 *
 * IMPORTANT: This middleware does NOT interfere with API routes.
 * Better Auth API routes at /api/auth/* are handled separately.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for API routes entirely - let them handle their own auth
  if (pathname.startsWith("/api")) {
    return NextResponse.next()
  }

  // Skip middleware for static files and public assets
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon.ico") ||
    pathname.includes(".")
  ) {
    return NextResponse.next()
  }

  // Public routes that don't require authentication
  const publicRoutes = ["/login", "/signup", "/"]
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route)
  )

  // Check for auth cookies - either backend auth_token or Better Auth session token
  // Backend auth stores JWT in 'auth_token' httpOnly cookie
  // Better Auth stores session in 'better-auth.session_token' cookie
  const authToken = request.cookies.get("auth_token")
  const betterAuthCookie = request.cookies.get("better-auth.session_token")
  const isAuthenticated = authToken || betterAuthCookie

  // If accessing protected route without auth, redirect to login
  if (!isPublicRoute && !isAuthenticated) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  // If authenticated user tries to access login/signup, redirect to dashboard
  if (isAuthenticated && (pathname === "/login" || pathname === "/signup")) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
