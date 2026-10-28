/** Landing Page - orrery hero, product bento, closing call to action.
 *
 * Per spec.md US1: Discover and Sign Up
 * - (original spec asked for a "deep space glassmorphism" look; superseded by D-007)
 * - "compelling call-to-action"
 * - "learn about upcoming voice features"
 *
 * Visual direction: "night observatory" (D-007, docs/design/README.md)
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
