/**
 * Auth layout (login, signup): the form on a solid surface, and on wide
 * screens a calm orrery beside it. Phones get the form alone.
 */

import { BrandLogo } from "@/components/layout/brand-logo"
import { Orrery } from "@/components/three/orrery"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="grid min-h-svh lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
      <div className="flex flex-col px-5 py-6 sm:px-10">
        <BrandLogo className="self-start" />
        <main className="flex flex-1 items-center justify-center py-10">
          <div className="w-full max-w-sm">{children}</div>
        </main>
        <p className="text-sm text-muted-foreground">
          Part of the Evolution of Todo project.
        </p>
      </div>

      <aside className="relative hidden overflow-hidden border-l border-border lg:block" aria-hidden>
        <Orrery variant="calm" moons={[3, 5, 6]} className="absolute inset-0" />
        <p className="absolute inset-x-0 bottom-10 mx-auto max-w-sm px-6 text-center font-display text-2xl font-medium leading-snug text-foreground/90">
          Today, this week, later. Everything you have to do, in view.
        </p>
      </aside>
    </div>
  )
}
