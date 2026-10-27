"use client"

import { Link } from "next-view-transitions"

import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/layout/theme-toggle"
import { BrandLogo } from "@/components/layout/brand-logo"
import { UserNav } from "@/components/layout/user-nav"
import type { User } from "@/types/user"

interface HeroHeaderProps {
  user: User | null
  isLoading: boolean
}

/**
 * Landing navigation: a floating Liquid Glass pill that stays put while the
 * page scrolls underneath (the one glass layer on this page).
 */
export function HeroHeader({ user, isLoading }: HeroHeaderProps) {
  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-3 sm:px-6 sm:pt-4">
      <nav
        aria-label="Main"
        className="glass mx-auto flex h-14 max-w-6xl items-center justify-between gap-3 rounded-full pl-4 pr-2 sm:pl-5"
      >
        <BrandLogo />

        <div className="flex items-center gap-2">
          <div className="hidden sm:block">
            <ThemeToggle />
          </div>
          {!isLoading &&
            (user ? (
              <>
                <Button asChild size="sm" className="hidden rounded-full sm:inline-flex">
                  <Link href="/dashboard">Open dashboard</Link>
                </Button>
                <UserNav user={user} />
              </>
            ) : (
              <>
                <Button asChild size="sm" variant="ghost" className="rounded-full">
                  <Link href="/login">Sign in</Link>
                </Button>
                <Button asChild size="sm" className="rounded-full pressable">
                  <Link href="/signup">Get started</Link>
                </Button>
              </>
            ))}
        </div>
      </nav>
    </header>
  )
}
