"use client"

import { useState } from "react"
import { motion, useScroll, useMotionValueEvent } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Link } from "next-view-transitions"
import { ThemeToggle } from "@/components/layout/theme-toggle"
import { BrandLogo } from "@/components/layout/brand-logo"
import { UserNav } from "@/components/layout/user-nav"
import { ChevronRight } from "lucide-react"
import type { User } from "./hero-section"

interface HeroHeaderProps {
  user: User | null
  isLoading: boolean
}

/**
 * Hero Header Component - Unified header for the landing/hero page.
 *
 * Shows:
 * - Logo (Chronos.) on the left
 * - Theme toggle
 * - "Sign In" button for logged-out users
 * - No extra button for logged-in users (hero already has "Go to Dashboard" CTA)
 *
 * Smart scroll behavior: stays fixed until hero content reaches it, then slides away.
 */
export function HeroHeader({ user, isLoading }: HeroHeaderProps) {
  const { scrollY } = useScroll()
  const [isVisible, setIsVisible] = useState(true)
  const [isScrolled, setIsScrolled] = useState(false)

  useMotionValueEvent(scrollY, "change", (latest) => {
    // Hide header when scrolled past ~200px (when "The Evolution of" text reaches header area)
    // Show when scrolled back above that threshold
    setIsVisible(latest < 200)
    setIsScrolled(latest > 10)
  })

  return (
    <motion.header
      initial={{ y: 0 }}
      animate={{ y: isVisible ? 0 : "-100%" }}
      transition={{ type: "spring", stiffness: 300, damping: 30, mass: 0.8 }}
      className="fixed top-0 left-0 right-0 z-50 w-full border-b bg-background/80 backdrop-blur supports-backdrop-filter:bg-background/60 transition-shadow duration-300"
      style={{
        boxShadow: isScrolled ? "0 4px 20px -2px rgb(0 0 0 / 0.3)" : "none"
      }}
    >
      <div className="container flex h-16 items-center justify-between px-6">
        {/* Logo */}
        <BrandLogo />

        {/* Right side: Theme toggle + Sign In (logged out) or UserNav (logged in) */}
        <div className="flex items-center gap-3 px-2">
          <ThemeToggle />

          {!isLoading && (
            <>
              {user ? (
                // Logged in: Show profile icon with dropdown
                <UserNav user={user} />
              ) : (
                // Logged out: Show Sign In button
                <Button asChild size="sm" variant="outline" className="glass">
                  <Link href="/login">
                    Sign In
                    <ChevronRight className="h-4 w-5 ml-1" />
                  </Link>
                </Button>
              )}
            </>
          )}
        </div>
      </div>
    </motion.header>
  )
}
