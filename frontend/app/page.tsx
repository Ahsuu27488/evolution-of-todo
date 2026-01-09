/** Landing Page - Hero Section with Deep Space Theme.
 *
 * Per spec.md US1: Discover and Sign Up
 * - "futuristic deep space glassmorphism design"
 * - "compelling call-to-action"
 * - "learn about upcoming voice features"
 *
 * Per spec.md FR-038: "Deep Space" color scheme with cyan/purple neon accents
 * Per spec.md FR-037: glassmorphism visual design with backdrop-blur effects
 *
 * This is a Server Component that:
 * 1. Checks authentication status via Better Auth
 * 2. Redirects authenticated users to dashboard
 * 3. Renders the Client Component (HeroSection) for animations
 */

import { redirect } from "next/navigation"
import { headers } from "next/headers"
import { auth } from "@/lib/auth"
import { HeroSection } from "@/components/landing/hero-section"

/**
 * Landing page - redirects authenticated users to dashboard,
 * shows hero section to visitors.
 *
 * Server Component responsibilities:
 * - Auth check and redirect logic
 * - Client Component delegation for animations
 */
export default async function HomePage() {
  // CRITICAL: Call headers() FIRST, before any other async operation
  const headersList = await headers()

  const session = await auth.api.getSession({
    headers: headersList,
  })

  // Redirect authenticated users to dashboard
  if (session?.user) {
    redirect("/dashboard")
  }

  // Render the animated landing page (Client Component)
  return <HeroSection />
}
