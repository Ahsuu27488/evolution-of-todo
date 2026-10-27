/**
 * Route access rules used by middleware.ts.
 *
 * Kept free of Next.js imports so it can be unit-tested with `node --test`.
 */

/** Routes anyone can open. "/" matches only the landing page itself. */
const PUBLIC_EXACT = ["/"]
/** Route prefixes anyone can open (the route and everything below it). */
const PUBLIC_PREFIXES = ["/login", "/signup"]

export function isPublicPath(pathname: string): boolean {
  if (PUBLIC_EXACT.includes(pathname)) return true
  return PUBLIC_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  )
}

/** Auth pages a signed-in user is sent away from. */
export function isAuthPage(pathname: string): boolean {
  return pathname === "/login" || pathname === "/signup"
}
