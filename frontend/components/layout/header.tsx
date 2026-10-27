"use client"

import { UserNav } from "./user-nav"
import { ThemeToggle } from "./theme-toggle"
import { BrandLogo } from "./brand-logo"
import { NotificationsClient } from "@/components/notifications/notifications-client"
import type { User } from "@/types/user"

interface HeaderProps {
  isAuthenticated?: boolean
  user?: User
}

export function Header({ isAuthenticated, user }: HeaderProps) {
  return (
    <header className="fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-6 sm:pt-4">
      <nav
        aria-label="App"
        className="glass mx-auto flex h-14 max-w-6xl items-center gap-2 rounded-full pl-4 pr-2 sm:pl-5"
      >
        <BrandLogo />
        <div className="flex flex-1 items-center justify-end gap-1.5 sm:gap-2">
          <div className="hidden sm:block">
            <ThemeToggle />
          </div>
          {isAuthenticated && <NotificationsClient />}
          {isAuthenticated && user && <UserNav user={user} />}
        </div>
      </nav>
    </header>
  )
}
