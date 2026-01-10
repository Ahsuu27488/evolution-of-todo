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
 * This is a Server Component that renders the Client Component (HeroSection).
 *
 * Authenticated users can now view the landing page and will see
 * personalized content with a "Go to Dashboard" option.
 */

import { HeroSection } from "@/components/landing/hero-section"

/**
 * Landing page - shows hero section to all visitors.
 * Auth state is checked client-side for personalized content.
 */
export default function HomePage() {
  return <HeroSection />
}
