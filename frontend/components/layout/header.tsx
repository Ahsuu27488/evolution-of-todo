"use client"

import Link from "next/link"
import { CheckSquare } from "lucide-react"
import { useSession } from "@/lib/auth-client"
import { UserNav } from "./user-nav"

export function Header() {
  const { data: session } = useSession()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <Link href="/" className="flex items-center space-x-2">
          <CheckSquare className="h-6 w-6" />
          <span className="font-bold">Todo App</span>
        </Link>
        <div className="flex flex-1 items-center justify-end space-x-4">
          {session?.user && <UserNav user={session.user} />}
        </div>
      </div>
    </header>
  )
}
