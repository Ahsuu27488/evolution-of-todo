"use client"

/**
 * Landing page (client part).
 *
 * Signature moment: the orrery. The hero is a tall section with a sticky stage;
 * scrolling through it swings the tilted orbits into a flat dial (`flatten`)
 * and reveals what each orbit means. Native sticky scroll, no scroll-jacking.
 *
 * Auth state comes from the server (no loading flash) and drops to signed-out
 * when another tab signs out.
 */

import { useEffect, useRef, useState } from "react"
import { Link } from "next-view-transitions"
import { motion, useMotionValueEvent, useReducedMotion, useScroll, useTransform } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Orrery } from "@/components/three/orrery"
import { HeroHeader } from "./hero-header"
import { FeatureBento } from "./feature-bento"
import { SiteFooter } from "./site-footer"
import { getDisplayName, type User } from "@/types/user"

interface HeroSectionProps {
  initialUser: User | null
  className?: string
}

const ease = [0.22, 1, 0.36, 1] as const

const ORBIT_LEGEND = [
  { name: "Today", detail: "Due today or overdue. The inner orbit moves fastest." },
  { name: "This week", detail: "Due in the next seven days." },
  { name: "Later", detail: "Everything else, still in view." },
]

export function HeroSection({ initialUser, className = "" }: HeroSectionProps) {
  const [user, setUser] = useState<User | null>(initialUser)
  const reduceMotion = useReducedMotion()

  useEffect(() => {
    const handleLogout = () => setUser(null)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "auth_logout" && e.newValue === "true") setUser(null)
    }
    window.addEventListener("auth-logout", handleLogout)
    window.addEventListener("storage", handleStorageChange)
    return () => {
      window.removeEventListener("auth-logout", handleLogout)
      window.removeEventListener("storage", handleStorageChange)
    }
  }, [])

  // Scroll-linked stage: 0 at the top of the hero, 1 when its end reaches the top.
  const stage = useRef<HTMLElement>(null)
  const flatten = useRef(0)
  const { scrollYProgress } = useScroll({ target: stage, offset: ["start start", "end start"] })
  useMotionValueEvent(scrollYProgress, "change", (p) => {
    // Orbits flatten over the first 60% of the stage scroll.
    flatten.current = reduceMotion ? 0 : Math.min(1, p / 0.6)
  })
  const introOpacity = useTransform(scrollYProgress, [0, 0.28], [1, 0])
  const introY = useTransform(scrollYProgress, [0, 0.28], [0, -40])
  const legendOpacity = useTransform(scrollYProgress, [0.38, 0.55], [0, 1])
  const legendY = useTransform(scrollYProgress, [0.38, 0.55], [24, 0])

  return (
    <div className={`relative ${className}`}>
      <HeroHeader user={user} isLoading={false} />

      <main id="main">
        {/* Stage: 220svh of scroll, the first screen stays pinned */}
        <section ref={stage} aria-labelledby="hero-title" className="relative h-[220svh]">
          <div className="sticky top-0 h-svh overflow-hidden">
            {/* The orrery: right half on desktop, upper half on phones */}
            <Orrery
              variant="hero"
              flatten={flatten}
              className="absolute inset-x-0 top-[4.5rem] h-[52svh] [mask-image:linear-gradient(to_bottom,black_70%,transparent)] md:inset-y-0 md:left-[30%] md:right-[-10%] md:top-0 md:h-auto md:[mask-image:linear-gradient(to_right,transparent,black_32%)]"
            />

            {/* Intro copy */}
            <motion.div
              style={reduceMotion ? undefined : { opacity: introOpacity, y: introY }}
              className="relative mx-auto flex h-full max-w-6xl flex-col justify-end px-5 pb-[max(3rem,8svh)] sm:px-8 md:justify-center md:pb-0"
            >
              <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.9, ease }}
                className="max-w-xl"
              >
                <h1 id="hero-title" className="text-display">
                  {user ? `Welcome back, ${getDisplayName(user)}.` : "Every task in its orbit."}
                </h1>
                <p className="mt-5 max-w-md text-lg leading-relaxed text-muted-foreground sm:text-xl">
                  {user
                    ? "Your orbits are where you left them. Pick up today's tasks or ask Chronos what's next."
                    : "Chronos is a to-do list you can talk to. Add, plan and find tasks by typing or speaking, in English or Urdu."}
                </p>
                <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                  {user ? (
                    <Button asChild size="lg" className="h-12 rounded-full px-7 text-base pressable">
                      <Link href="/dashboard">Open dashboard</Link>
                    </Button>
                  ) : (
                    <>
                      <Button asChild size="lg" className="h-12 rounded-full px-7 text-base pressable">
                        <Link href="/signup">Create free account</Link>
                      </Button>
                      <Button asChild size="lg" variant="ghost" className="h-12 rounded-full px-6 text-base">
                        <Link href="/login">Sign in</Link>
                      </Button>
                    </>
                  )}
                </div>
              </motion.div>
            </motion.div>

            {/* Revealed once the orbits lie flat: what each orbit means */}
            <motion.div
              style={reduceMotion ? { opacity: 0 } : { opacity: legendOpacity, y: legendY }}
              className="pointer-events-none absolute inset-x-0 bottom-0 mx-auto max-w-6xl px-5 pb-10 sm:px-8 md:inset-y-0 md:flex md:items-center md:pb-0"
            >
              <div className="max-w-sm">
                <h2 className="text-[length:var(--step-h2)] font-semibold leading-tight">
                  Three orbits, one glance.
                </h2>
                <ol className="mt-6 space-y-4">
                  {ORBIT_LEGEND.map((orbit, i) => (
                    <li key={orbit.name} className="flex gap-3">
                      <span
                        className="mt-1.5 size-2.5 shrink-0 rounded-full"
                        style={{ background: i === 0 ? "var(--custom-primary)" : "var(--custom-secondary)", opacity: 1 - i * 0.22 }}
                        aria-hidden
                      />
                      <p>
                        <span className="font-medium">{orbit.name}.</span>{" "}
                        <span className="text-muted-foreground">{orbit.detail}</span>
                      </p>
                    </li>
                  ))}
                </ol>
              </div>
            </motion.div>

            {/* Scroll cue */}
            {!reduceMotion && (
              <motion.div
                style={{ opacity: introOpacity }}
                className="absolute bottom-5 left-1/2 hidden -translate-x-1/2 md:block"
                aria-hidden
              >
                <span className="block h-9 w-5 rounded-full border border-foreground/25 p-1">
                  <motion.span
                    className="block size-1.5 rounded-full bg-foreground/60 mx-auto"
                    animate={{ y: [0, 14, 0] }}
                    transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
                  />
                </span>
              </motion.div>
            )}
          </div>
        </section>

        <FeatureBento />

        {/* Closing call to action */}
        <section className="px-5 pb-[clamp(4rem,10vw,8rem)] sm:px-8" aria-labelledby="cta-title">
          <div className="surface mx-auto flex max-w-6xl flex-col items-start gap-6 rounded-[var(--radius-4xl)] p-8 sm:flex-row sm:items-center sm:justify-between sm:p-12">
            <div>
              <h2 id="cta-title" className="text-[length:var(--step-h1)] font-semibold leading-tight">
                Start with one task.
              </h2>
              <p className="mt-2 text-muted-foreground">
                Type it, say it, or ask Chronos to plan your week.
              </p>
            </div>
            <Button asChild size="lg" className="h-12 shrink-0 rounded-full px-7 text-base pressable">
              <Link href={user ? "/dashboard" : "/signup"}>{user ? "Open dashboard" : "Create free account"}</Link>
            </Button>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  )
}
