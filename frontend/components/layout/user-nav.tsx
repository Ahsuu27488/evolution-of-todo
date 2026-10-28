"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Bell, Loader2, LogOut, UserCircle } from "lucide-react"
import { toast } from "sonner"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { signOutAction } from "@/app/actions/auth"
import type { User } from "@/types/user"

interface UserNavProps {
  user: User
}

/** "Ada Lovelace" -> "AL", "ada@x.com" -> "A" */
function initials(user: User): string {
  const name = user.display_name?.trim() || [user.first_name, user.last_name].filter(Boolean).join(" ")
  if (name) {
    const parts = name.split(/\s+/)
    return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase()
  }
  return (user.email?.[0] ?? "?").toUpperCase()
}

export function UserNav({ user }: UserNavProps) {
  const router = useRouter()
  const [isSigningOut, setIsSigningOut] = useState(false)

  async function handleSignOut() {
    setIsSigningOut(true)
    const result = await signOutAction()
    if (result.success) {
      toast.success("Signed out")

      // Dispatch logout event for cross-tab communication
      window.dispatchEvent(new CustomEvent("auth-logout"))

      // Also set storage for tabs listening to storage events
      localStorage.setItem("auth_logout", "true")
      localStorage.removeItem("auth_logout") // Clean up immediately

      router.push("/login")
    } else {
      setIsSigningOut(false)
      toast.error("Couldn't sign you out. Try again.")
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label="Account menu"
          className="group grid size-10 place-items-center rounded-full outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 active:scale-95"
        >
          <span className="grid size-8 place-items-center rounded-full bg-primary/16 font-display text-[13px] font-semibold text-primary ring-1 ring-primary/25 transition-colors group-hover:bg-primary/24 group-data-[state=open]:bg-primary group-data-[state=open]:text-primary-foreground">
            {initials(user)}
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64" align="end" sideOffset={10}>
        <DropdownMenuLabel className="flex items-center gap-3 px-2.5 py-2.5 text-foreground">
          <span aria-hidden className="grid size-9 shrink-0 place-items-center rounded-full bg-primary/16 font-display text-sm font-semibold text-primary">
            {initials(user)}
          </span>
          <span className="min-w-0">
            {/* [T036] Display display_name with fallback for legacy data */}
            <span className="block truncate text-sm font-medium">{user.display_name || user.email}</span>
            <span className="block truncate text-xs font-normal text-muted-foreground">{user.email}</span>
          </span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/profile">
            <UserCircle />
            Profile
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/settings/notifications">
            <Bell />
            Notification settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onSelect={(e) => {
            e.preventDefault()
            handleSignOut()
          }}
          disabled={isSigningOut}
        >
          {isSigningOut ? <Loader2 className="animate-spin" /> : <LogOut />}
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
