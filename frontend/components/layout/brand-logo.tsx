"use client"

import Link from "next/link"
import { motion } from "framer-motion"

/**
 * Brand Logo Component - Text-based gradient logo.
 *
 * Uses the same animated gradient effect as the hero section's "Todo Management"
 * text for a cohesive, modern branding approach.
 */
export function BrandLogo() {
  return (
    <Link href="/" className="group relative flex items-center">
      {/* Background glow effect */}
      <motion.div
        animate={{
          scale: 1.05,
          opacity: 0.4,
        }}
        initial={{
          scale: 1,
          opacity: 0.3,
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatType: "reverse",
          ease: "easeInOut",
        }}
        className="absolute -inset-x-4 -inset-y-2 bg-linear-to-r from-primary/20 via-secondary/20 to-primary/20 rounded-full blur-xl"
      />

      {/* Logo text */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.2 }}
        className="relative px-2"
      >
        <span className="text-2xl md:text-3xl font-bold bg-linear-to-r from-primary via-secondary to-primary bg-clip-text text-transparent animate-gradient bg-size-[200%_auto] will-change-background">
          Chronos
          <span className="text-primary">.</span>
        </span>
      </motion.div>
    </Link>
  )
}
