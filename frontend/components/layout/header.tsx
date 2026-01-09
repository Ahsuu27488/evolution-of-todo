"use client"

import { UserNav } from "./user-nav"
import { ThemeToggle } from "./theme-toggle"
import { BrandLogo } from "./brand-logo"

interface User {
  id: string
  email: string
  name: string
}

interface HeaderProps {
  isAuthenticated?: boolean
  user?: User
}

export function Header({ isAuthenticated, user }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="container flex h-20 items-center">
        <BrandLogo />
        <div className="flex flex-1 items-center justify-end gap-4">
          <ThemeToggle />
          {isAuthenticated && user && <UserNav user={user} />}
        </div>
      </div>
    </header>
  )
}
