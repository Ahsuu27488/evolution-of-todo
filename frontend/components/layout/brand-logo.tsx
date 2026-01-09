"use client"

import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

export function BrandLogo() {
  const { theme, systemTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch by waiting for mount
  // This setState is intentional to prevent hydration mismatch and is safe here.
  useEffect(() => {
    setMounted(true)
  }, [])

  const currentTheme = theme === "system" ? systemTheme : theme
  const isDark = mounted ? currentTheme === "dark" : true // Default to dark while loading

  return (
    <Link href="/" className="group relative flex items-center justify-center">
      {/* Background glow orb - Adjusted for rectangular shape */}
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
        // Widened the glow to match the logo text width
        className="absolute -inset-x-4 -inset-y-2 bg-linear-to-r from-primary/20 via-secondary/20 to-primary/20 rounded-full blur-xl"
      />

      {/* Logo container - Preserves 410x134 aspect ratio (~3.06) */}
      <motion.div
        whileHover={{ scale: 1.05 }}
        transition={{ duration: 0.2 }}
        className="relative h-12 w-[147px]" 
      >
        {/* Using the file names from your code snippet */}
        <Image
          src={isDark ? "/logo for dark mode.png" : "/logo for light mode.png"}
          alt="Chronos Logo"
          fill
          className="object-contain" // Ensures the entire logo is visible
          priority
          sizes="(max-width: 768px) 120px, 147px"
        />
      </motion.div>
    </Link>
  )
}