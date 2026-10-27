"use client"

/**
 * <Orrery>: progressive-enhancement wrapper for the WebGL orrery.
 *
 * - Renders a static CSS poster at the same size first (no layout shift, and the
 *   whole picture when WebGL is off, slow or unwanted).
 * - Loads the three.js scene lazily, only in the browser, only when on screen.
 * - Reduced motion: a still frame. Low-power devices or no WebGL: poster only.
 * - Pauses the render loop while scrolled out of view.
 */

import dynamic from "next/dynamic"
import { useEffect, useMemo, useRef, useState, type MutableRefObject } from "react"
import { useTheme } from "next-themes"

import { cn } from "@/lib/utils"
import type { OrreryPalette, OrreryVariant } from "./orrery-scene"

const OrreryScene = dynamic(() => import("./orrery-scene"), { ssr: false })

const PALETTES: Record<"dark" | "light", OrreryPalette> = {
  dark: {
    core: "#f2b84b",
    coreHot: "#fff4d6",
    ring: "#9fc3ff",
    ringOpacity: 0.32,
    moonNear: "#ffe2a3",
    moonFar: "#cfe0ff",
    stars: "#dfe7ff",
    starsOpacity: 0.75,
  },
  light: {
    core: "#e0951c",
    coreHot: "#fff1cf",
    ring: "#2a3b66",
    ringOpacity: 0.28,
    moonNear: "#c9800f",
    moonFar: "#3c5590",
    stars: "#2a3b66",
    starsOpacity: 0.22,
  },
}

// Probed once per page load; browsers cap live WebGL contexts (~16).
let webglSupport: boolean | undefined

function canRunWebGL(): boolean {
  if (webglSupport !== undefined) return webglSupport
  const nav = navigator as Navigator & { deviceMemory?: number }
  const lowPower =
    (nav.hardwareConcurrency !== undefined && nav.hardwareConcurrency <= 2) ||
    (nav.deviceMemory !== undefined && nav.deviceMemory <= 2)
  let hasWebGL = false
  try {
    const canvas = document.createElement("canvas")
    const gl = canvas.getContext("webgl2") || canvas.getContext("webgl")
    hasWebGL = Boolean(gl)
    // Release the probe context right away instead of waiting for GC.
    gl?.getExtension("WEBGL_lose_context")?.loseContext()
  } catch {
    hasWebGL = false
  }
  webglSupport = hasWebGL && !lowPower
  return webglSupport
}

interface OrreryProps {
  variant?: OrreryVariant
  moons?: [number, number, number]
  flatten?: MutableRefObject<number>
  className?: string
}

export function Orrery({ variant = "hero", moons = [5, 7, 9], flatten, className }: OrreryProps) {
  const container = useRef<HTMLDivElement>(null)
  const { resolvedTheme } = useTheme()
  const [enabled, setEnabled] = useState(false)
  const [visible, setVisible] = useState(false)
  const [still, setStill] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setEnabled(canRunWebGL())
    const media = window.matchMedia("(prefers-reduced-motion: reduce)")
    setStill(media.matches)
    const onChange = () => setStill(media.matches)
    media.addEventListener("change", onChange)
    return () => media.removeEventListener("change", onChange)
  }, [])

  useEffect(() => {
    const el = container.current
    if (!el) return
    const io = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), {
      rootMargin: "200px",
    })
    io.observe(el)
    return () => io.disconnect()
  }, [])

  // Mount the scene the first time it comes into view, then keep it (pausing when hidden).
  const [mounted, setMounted] = useState(false)
  useEffect(() => {
    if (enabled && visible) setMounted(true)
  }, [enabled, visible])

  // Fade the canvas in a beat after mount so the first compiled frame never flashes.
  useEffect(() => {
    if (!mounted) return
    const t = setTimeout(() => setReady(true), 120)
    return () => clearTimeout(t)
  }, [mounted])

  const palette = PALETTES[resolvedTheme === "light" ? "light" : "dark"]
  const stableMoons = useMemo(() => moons, [moons])

  return (
    <div ref={container} className={cn("relative", className)} aria-hidden>
      <OrreryPoster variant={variant} className={cn("transition-opacity duration-700", ready && "opacity-0")} />
      {mounted && (
        <div className={cn("absolute inset-0 opacity-0 transition-opacity duration-1000", ready && "opacity-100")}>
          <OrreryScene
            variant={variant}
            palette={palette}
            moons={stableMoons}
            flatten={flatten}
            still={still}
            active={visible}
          />
        </div>
      )}
    </div>
  )
}

/** Static stand-in: the same composition drawn with CSS (core glow + tilted orbits). */
function OrreryPoster({ variant, className }: { variant: OrreryVariant; className?: string }) {
  const rings = variant === "mini" ? [44, 64, 86] : [38, 56, 76]
  return (
    <div className={cn("absolute inset-0 grid place-items-center overflow-hidden", className)}>
      {rings.map((size, i) => (
        <span
          key={size}
          className="absolute rounded-full border border-secondary/30"
          style={{
            width: `${size}%`,
            aspectRatio: "1",
            transform: `rotate(${[18, -26, 8][i]}deg) scaleY(${[0.36, 0.48, 0.3][i]})`,
          }}
        />
      ))}
      <span
        className="absolute rounded-full"
        style={{
          width: variant === "mini" ? "20%" : "13%",
          aspectRatio: "1",
          background:
            "radial-gradient(circle at 40% 38%, oklch(0.97 0.04 85), var(--custom-primary) 55%, color-mix(in oklch, var(--custom-primary) 40%, transparent) 70%, transparent 72%)",
          boxShadow: "0 0 80px 20px color-mix(in oklch, var(--custom-primary) 30%, transparent)",
        }}
      />
    </div>
  )
}
