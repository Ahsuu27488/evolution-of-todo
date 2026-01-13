"use client"

/**
 * Hero Section - Client Component with framer-motion animations.
 *
 * This component contains all the animated elements using framer-motion.
 * It's a client component because framer-motion requires browser APIs.
 *
 * Shows different content based on authentication state:
 * - Logged out: "Start Your Journey" and "Sign In" buttons
 * - Logged in: "Welcome back" message and "Go to Dashboard" button
 */

import { Button } from "@/components/ui/button"
import { Link } from "next-view-transitions"
import { motion } from "framer-motion"
import { Sparkles, Mic, Zap, Shield, Rocket, ChevronRight, ArrowRight } from "lucide-react"
import { fadeInUp, staggerContainer } from "@/lib/animations"
import { useEffect, useState } from "react"
import { getCurrentUser } from "@/lib/auth-client"
import type { User } from "@/lib/auth-client"
import { HeroHeader } from "./hero-header"

interface HeroSectionProps {
  className?: string
}

export function HeroSection({ className = "" }: HeroSectionProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check auth state on mount
    const currentUser = getCurrentUser()
    setUser(currentUser)
    setIsLoading(false)

    // Listen for storage changes (e.g., logout from another tab)
    const handleStorageChange = () => {
      setUser(getCurrentUser())
    }

    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [])
  return (
    <div className={`min-h-screen relative overflow-hidden ${className}`}>
      {/* Unified header with logo, theme toggle, and sign in */}
      <HeroHeader user={user} isLoading={isLoading} />

      {/* Background effects */}
      <div className="fixed inset-0 -z-10">
        {/* Deep space base */}
        <div className="absolute inset-0 bg-background" />

        {/* Animated gradient orbs */}
        <motion.div
          animate={{
            scale: 1.2,
            opacity: 0.4,
          }}
          initial={{
            scale: 1,
            opacity: 0.2,
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl will-change-transform will-change-opacity"
        />
        <motion.div
          animate={{
            scale: 1,
            opacity: 0.3,
          }}
          initial={{
            scale: 1.2,
            opacity: 0.2,
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "easeInOut",
          }}
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-3xl will-change-transform will-change-opacity"
        />

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,currentColor_1px,transparent_1px),linear-gradient(to_bottom,currentColor_1px,transparent_1px)] bg-[length:50px_50px]" />
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 pt-24 pb-16 md:pt-32 md:pb-24">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="max-w-4xl mx-auto text-center"
        >
          {/* Badge */}
          <motion.div variants={fadeInUp} className="mb-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass border-primary/30">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-foreground">
                Phase II: Chronos Professional Web App
              </span>
            </div>
          </motion.div>

          {/* Hero Title */}
          <motion.h1 variants={fadeInUp} className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="block">The Evolution of</span>
            <span className="block bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto] will-change-background">
              Todo Management
            </span>
          </motion.h1>

          {/* Hero Description */}
          <motion.p
            variants={fadeInUp}
            className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto"
          >
            {user
              ? `Welcome back, ${user.name.split(" ")[0]}! Ready to be productive?`
              : "Experience the future of productivity with our stunning deep space interface. Voice commands coming soon in Phase III."}
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16"
          >
            {isLoading ? (
              // Loading state
              <div className="h-14" />
            ) : user ? (
              // Logged in: Show dashboard button
              <>
                <Button
                  asChild
                  size="lg"
                  className="gap-2 shadow-lg shadow-primary/20"
                >
                  <Link href="/dashboard">
                    Go to Dashboard
                    <ArrowRight className="h-5 w-5" />
                  </Link>
                </Button>
              </>
            ) : (
              // Logged out: Show signup/signin buttons
              <>
                <Button
                  asChild
                  size="lg"
                  className="gap-2 shadow-lg shadow-primary/20"
                >
                  <Link href="/signup">
                    Start Your Journey
                    <Rocket className="h-5 w-5" />
                  </Link>
                </Button>
                <Button
                  asChild
                  variant="outline"
                  size="lg"
                  className="gap-2 glass"
                >
                  <Link href="/login">
                    Sign In
                    <ChevronRight className="h-5 w-5" />
                  </Link>
                </Button>
              </>
            )}
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            variants={staggerContainer}
            className="grid md:grid-cols-3 gap-6 mt-16"
          >
            {/* Voice Commands (Coming Soon) */}
            <motion.div
              variants={fadeInUp}
              className="glass p-6 rounded-2xl border border-primary/20 hover:border-primary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Mic className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Voice Commands
              </h3>
              <p className="text-muted-foreground text-sm">
                Coming in Phase III: Manage tasks with natural language voice input.
              </p>
            </motion.div>

            {/* Advanced Features */}
            <motion.div
              variants={fadeInUp}
              className="glass p-6 rounded-2xl border border-secondary/20 hover:border-secondary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-12 h-12 rounded-xl bg-secondary/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Zap className="h-6 w-6 text-secondary" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Advanced Features
              </h3>
              <p className="text-muted-foreground text-sm">
                Priorities, tags, due dates, recurring tasks, and intelligent search.
              </p>
            </motion.div>

            {/* Secure & Private */}
            <motion.div
              variants={fadeInUp}
              className="glass p-6 rounded-2xl border border-green-500/20 hover:border-green-500/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Shield className="h-6 w-6 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Secure & Private
              </h3>
              <p className="text-muted-foreground text-sm">
                Your data is encrypted and stored securely. We value your privacy.
              </p>
            </motion.div>
          </motion.div>

          {/* Tagline */}
          <motion.div
            variants={fadeInUp}
            className="mt-20 text-muted-foreground text-sm"
          >
            <p>Built with Next.js 16, FastAPI, and Neon PostgreSQL</p>
            <p className="mt-2">Part of the AI-Driven Development Hackathon Series</p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
