import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

/**
 * Middleware for route protection.
 * Redirects unauthenticated users to login for protected routes.
 *
 * IMPORTANT: This middleware does NOT interfere with API routes.
 * Better Auth API routes at /api/auth/* are handled separately.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // DIAGNOSTIC: Log all requests
  console.log("[Middleware] Checking:", pathname)

  // Skip middleware for API routes entirely - let them handle their own auth
  if (pathname.startsWith("/api")) {
    console.log("[Middleware] API route - allowing through")
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
  const isPublicRoute = publicRoutes.some((route) => pathname === route || pathname.startsWith(route))

  // Check for Better Auth session cookie
  // Better Auth uses "better-auth.session_token" or custom name based on config
  const authCookie = request.cookies.get("better-auth.session_token") ||
                     request.cookies.get("session")

  console.log("[Middleware] Auth cookie present:", !!authCookie, "Public route:", isPublicRoute)

  // If accessing protected route without auth, redirect to login
  if (!isPublicRoute && !authCookie) {
    console.log("[Middleware] PROTECTED route, no auth - redirecting to /login")
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  // If authenticated user tries to access login/signup, redirect to dashboard
  if (authCookie && (pathname === "/login" || pathname === "/signup")) {
    console.log("[Middleware] Authenticated user on auth page - redirecting to /dashboard")
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  console.log("[Middleware] Allow through to:", pathname)
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
