import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { isAuthPage, isPublicPath } from "@/lib/routes"

/**
 * Middleware for route protection.
 * Redirects unauthenticated users to login for protected routes.
 *
 * Signed-in means the "auth_token" httpOnly cookie (backend JWT) is present;
 * the pages themselves verify it against the backend.
 *
 * IMPORTANT: This middleware does NOT interfere with API routes.
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

  const isAuthenticated = Boolean(request.cookies.get("auth_token"))

  // If accessing protected route without auth, redirect to login
  if (!isPublicPath(pathname) && !isAuthenticated) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(loginUrl)
  }

  // If authenticated user tries to access login/signup, redirect to dashboard
  if (isAuthenticated && isAuthPage(pathname)) {
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
