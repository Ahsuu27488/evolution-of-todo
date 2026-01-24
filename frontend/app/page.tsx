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
 * This is a Server Component that fetches session server-side and passes it
 * to the Client Component (HeroSection) for personalized content.
 *
 * Hybrid approach: Server-side auth check + Client-side interactivity
 */

import { HeroSection } from "@/components/landing/hero-section"
import { getSession } from "@/app/actions/auth"

/**
 * Landing page - shows hero section to all visitors.
 * Auth state is checked server-side for instant personalized content (no flash).
 */
export default async function HomePage() {
  // Fetch session server-side - checks httpOnly cookie
  const session = await getSession()

  // Pass user data to client component for personalized content
  return <HeroSection initialUser={session?.user ?? null} />
}
