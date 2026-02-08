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
 *
 * HYBRID APPROACH:
 * - Receives initialUser from server (no loading flash)
 * - Listens for logout events to update client state
 */

import { Button } from "@/components/ui/button"
import { Link } from "next-view-transitions"
import { motion } from "framer-motion"
import { Sparkles, Mic, Rocket, ChevronRight, ArrowRight, Bot, Search, Languages, Bell, CheckSquare } from "lucide-react"
import { fadeInUp, staggerContainer } from "@/lib/animations"
import { useEffect, useState } from "react"
import { HeroHeader } from "./hero-header"
import type { User } from "@/lib/auth-client"

interface HeroSectionProps {
  initialUser: User | null
  className?: string
}

export function HeroSection({ initialUser, className = "" }: HeroSectionProps) {
  // Initialize with server-provided user data (no flash!)
  const [user, setUser] = useState<User | null>(initialUser)
  const isLoading = false // Server has data instantly, no loading state needed

  useEffect(() => {
    // Listen for logout events (e.g., from another tab or dashboard)
    const handleLogout = () => {
      setUser(null)
    }

    // Custom event that signout action will dispatch
    window.addEventListener("auth-logout", handleLogout)

    // Also listen for storage changes (logout from another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "auth_logout" && e.newValue === "true") {
        setUser(null)
      }
    }

    return () => {
      window.removeEventListener("auth-logout", handleLogout)
      window.removeEventListener("storage", handleStorageChange)
    }
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
      <div className="container mx-auto px-4 sm:px-6 pt-20 pb-12 sm:pt-24 sm:pb-16 md:pt-32 md:pb-24">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="max-w-4xl mx-auto text-center"
        >
          {/* Badge */}
          <motion.div variants={fadeInUp} className="mb-6 sm:mb-8">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 rounded-full glass border-primary/30">
              <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-primary" />
              <span className="text-xs sm:text-sm font-medium text-foreground">
                ✨ AI-Powered Productivity Assistant
              </span>
            </div>
          </motion.div>

          {/* Hero Title */}
          <motion.h1 variants={fadeInUp} className="text-4xl sm:text-5xl md:text-7xl font-bold mb-4 sm:mb-6 leading-tight">
            <span className="block">The Evolution of</span>
            <span className="block bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-[length:200%_auto] will-change-background">
              Todo Management
            </span>
          </motion.h1>

          {/* Hero Description */}
          <motion.p
            variants={fadeInUp}
            className="text-base sm:text-lg md:text-xl lg:text-2xl text-muted-foreground mb-6 sm:mb-8 max-w-2xl mx-auto px-2"
          >
            {user
              ? `Welcome back, ${user.display_name || user.first_name || user.email}! Ready to be productive?`
              : "Meet Chronos — Your AI-powered time guardian. Manage tasks with natural language, voice commands, and semantic search in English and Urdu."}
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-center mb-12 sm:mb-16"
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
            className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mt-12 sm:mt-16"
          >
            {/* AI Chatbot */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-primary/20 hover:border-primary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-primary/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Bot className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                Chronos AI Assistant
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Conversational task management with multi-agent intelligence.
              </p>
            </motion.div>

            {/* Voice Commands */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-primary/20 hover:border-primary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-primary/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Mic className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                Voice Commands
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Record voice memos transcribed instantly via Whisper API.
              </p>
            </motion.div>

            {/* Semantic Search */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-secondary/20 hover:border-secondary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-secondary/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Search className="h-5 w-5 sm:h-6 sm:w-6 text-secondary" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                Smart Search
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Find tasks by meaning using vector embeddings, not just keywords.
              </p>
            </motion.div>

            {/* Bilingual Support */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-secondary/20 hover:border-secondary/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-secondary/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Languages className="h-5 w-5 sm:h-6 sm:w-6 text-secondary" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                English + Urdu
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Full bilingual support with RTL rendering for Urdu text.
              </p>
            </motion.div>

            {/* Multi-Channel Notifications */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-green-500/20 hover:border-green-500/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-green-500/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <Bell className="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                Multi-Channel Alerts
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Real-time notifications via in-app, push, and email.
              </p>
            </motion.div>

            {/* Task Management */}
            <motion.div
              variants={fadeInUp}
              className="glass p-4 sm:p-6 rounded-2xl border border-green-500/20 hover:border-green-500/40 transition-all duration-300 group will-change-transform"
            >
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-green-500/20 flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform will-change-transform">
                <CheckSquare className="h-5 w-5 sm:h-6 sm:w-6 text-green-400" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold mb-2 text-foreground">
                Powerful Tasks
              </h3>
              <p className="text-muted-foreground text-xs sm:text-sm">
                Priorities, tags, due dates, and recurring task patterns.
              </p>
            </motion.div>
          </motion.div>

          {/* Tagline */}
          <motion.div
            variants={fadeInUp}
            className="mt-16 sm:mt-20 text-muted-foreground text-xs sm:text-sm"
          >
            <p>Built with Next.js 15, FastAPI, and Neon PostgreSQL</p>
            <p className="mt-2">Production-ready task management</p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
