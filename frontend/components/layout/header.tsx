"use client"

import { useState } from "react"
import { motion, useScroll, useMotionValueEvent } from "framer-motion"
import { UserNav } from "./user-nav"
import { ThemeToggle } from "./theme-toggle"
import { BrandLogo } from "./brand-logo"
import type { User } from "@/lib/auth-client"

interface HeaderProps {
  isAuthenticated?: boolean
  user?: User
}

export function Header({ isAuthenticated, user }: HeaderProps) {
  const { scrollY } = useScroll()
  const [isVisible, setIsVisible] = useState(true)
  const [isScrolled, setIsScrolled] = useState(false)

  useMotionValueEvent(scrollY, "change", (latest) => {
    // Hide header when scrolled past ~150px, show when scrolled back above
    setIsVisible(latest < 150)
    setIsScrolled(latest > 10)
  })

  return (
    <motion.header
      initial={{ y: 0 }}
      animate={{ y: isVisible ? 0 : "-100%" }}
      transition={{ type: "spring", stiffness: 300, damping: 30, mass: 0.8 }}
      className="fixed top-0 left-0 right-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60 transition-shadow duration-300"
      style={{
        boxShadow: isScrolled ? "0 4px 20px -2px rgb(0 0 0 / 0.3)" : "none"
      }}
    >
      <div className="container flex h-16 items-center px-4 sm:px-6">
        <BrandLogo />
        <div className="flex flex-1 items-center justify-end gap-2 sm:gap-4">
          <ThemeToggle />
          {isAuthenticated && user && <UserNav user={user} />}
        </div>
      </div>
    </motion.header>
  )
}
