"use client"

/**
 * Orrery scene (WebGL, React Three Fiber).
 *
 * A glowing "now" core with three tilted orbits (today / this week / later)
 * and tasks as moons lit by the core. `flatten` (0..1, read every frame)
 * swings the orbits from a tilted orrery into one flat dial facing the camera.
 *
 * Always load through <Orrery>, which lazy-loads this module, provides the
 * static poster and decides whether WebGL runs at all.
 */

import { useEffect, useMemo, useRef, type MutableRefObject } from "react"
import { Canvas, useFrame, useThree } from "@react-three/fiber"
import * as THREE from "three"

export type OrreryVariant = "hero" | "calm" | "mini"

export interface OrreryPalette {
  core: string
  coreHot: string
  ring: string
  ringOpacity: number
  moonNear: string
  moonFar: string
  stars: string
  starsOpacity: number
}

export interface OrrerySceneProps {
  variant: OrreryVariant
  palette: OrreryPalette
  /** Moons per orbit, inner to outer. */
  moons: [number, number, number]
  /** 0 = tilted orrery, 1 = flat dial. Read each frame, so a ref avoids re-renders. */
  flatten?: MutableRefObject<number>
  /** Freeze motion (reduced motion): render a still frame. */
  still?: boolean
  /** Pause the render loop while off-screen. */
  active?: boolean
}

const ORBITS = [
  { radius: 1.45, tilt: [1.2, 0.0, 0.35], speed: 0.32 },
  { radius: 2.15, tilt: [1.05, 0.0, -0.5], speed: 0.2 },
  { radius: 2.95, tilt: [1.32, 0.0, 0.15], speed: 0.12 },
] as const

const CORE_VERTEX = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vNormal = normalize(normalMatrix * normal);
    vView = normalize(-mv.xyz);
    gl_Position = projectionMatrix * mv;
  }
`

const CORE_FRAGMENT = /* glsl */ `
  uniform vec3 uCore;
  uniform vec3 uHot;
  uniform float uTime;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    float facing = clamp(dot(vNormal, vView), 0.0, 1.0);
    float rim = pow(1.0 - facing, 1.6);
    // faint, slow granulation so the surface feels alive without reading as a pattern
    float grain = sin(vNormal.x * 23.0 + uTime * 0.4) * sin(vNormal.y * 19.0 - uTime * 0.3) * sin(vNormal.z * 17.0 + uTime * 0.2);
    vec3 color = mix(uHot, uCore, smoothstep(0.0, 1.0, rim) + grain * 0.035);
    color += uCore * pow(rim, 3.0) * 0.6;
    gl_FragColor = vec4(color, 1.0);
  }
`

function useHaloTexture() {
  return useMemo(() => {
    const size = 256
    const canvas = document.createElement("canvas")
    canvas.width = canvas.height = size
    const ctx = canvas.getContext("2d")!
    const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
    g.addColorStop(0, "rgba(255,255,255,0.9)")
    g.addColorStop(0.18, "rgba(255,255,255,0.35)")
    g.addColorStop(0.5, "rgba(255,255,255,0.08)")
    g.addColorStop(1, "rgba(255,255,255,0)")
    ctx.fillStyle = g
    ctx.fillRect(0, 0, size, size)
    const texture = new THREE.CanvasTexture(canvas)
    texture.colorSpace = THREE.SRGBColorSpace
    return texture
  }, [])
}

function Core({ palette, still }: { palette: OrreryPalette; still?: boolean }) {
  const material = useRef<THREE.ShaderMaterial>(null)
  const halo = useHaloTexture()
  const uniforms = useMemo(
    () => ({
      uCore: { value: new THREE.Color(palette.core) },
      uHot: { value: new THREE.Color(palette.coreHot) },
      uTime: { value: 0 },
    }),
    // palette changes are applied in the effect below
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )

  useEffect(() => {
    uniforms.uCore.value.set(palette.core)
    uniforms.uHot.value.set(palette.coreHot)
  }, [palette.core, palette.coreHot, uniforms])

  useFrame((_, delta) => {
    if (!still && material.current) material.current.uniforms.uTime.value += delta
  })

  return (
    <group>
      <mesh>
        <sphereGeometry args={[0.55, 64, 64]} />
        <shaderMaterial
          ref={material}
          uniforms={uniforms}
          vertexShader={CORE_VERTEX}
          fragmentShader={CORE_FRAGMENT}
        />
      </mesh>
      <sprite scale={[3.4, 3.4, 1]}>
        <spriteMaterial
          map={halo}
          color={palette.core}
          transparent
          opacity={0.55}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </sprite>
      <pointLight color={palette.core} intensity={22} distance={12} decay={1.6} />
    </group>
  )
}

function Orbit({
  index,
  count,
  palette,
  flatten,
  still,
  moonScale = 1,
}: {
  index: number
  count: number
  palette: OrreryPalette
  flatten?: MutableRefObject<number>
  still?: boolean
  moonScale?: number
}) {
  const { radius, tilt, speed } = ORBITS[index]
  const group = useRef<THREE.Group>(null)
  const moons = useRef<THREE.InstancedMesh>(null)
  const phase = useRef(index * 1.7)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  const capacity = Math.max(count, 1)

  // Stable per-moon offsets and sizes
  const layout = useMemo(
    () =>
      Array.from({ length: capacity }, (_, i) => ({
        angle: (i / capacity) * Math.PI * 2 + ((i * 7919) % 100) / 100 * 0.6,
        size: 0.045 + (((i * 104729) % 100) / 100) * 0.04 + (index === 0 ? 0.015 : 0),
      })),
    [capacity, index]
  )

  useEffect(() => {
    const mesh = moons.current
    if (!mesh) return
    const color = new THREE.Color()
    for (let i = 0; i < capacity; i++) {
      color.set(index === 0 ? palette.moonNear : palette.moonFar)
      mesh.setColorAt(i, color)
    }
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true
  }, [capacity, index, palette.moonNear, palette.moonFar])

  useFrame((_, delta) => {
    const g = group.current
    const mesh = moons.current
    if (!g || !mesh) return

    const f = flatten?.current ?? 0
    // Tilted orrery -> flat dial (torus lies in XY, facing the camera at rotation 0)
    g.rotation.x = THREE.MathUtils.lerp(tilt[0], 0, f)
    g.rotation.z = THREE.MathUtils.lerp(tilt[2], 0, f)

    if (!still) phase.current += delta * speed
    for (let i = 0; i < capacity; i++) {
      const a = layout[i].angle + phase.current
      dummy.position.set(Math.cos(a) * radius, Math.sin(a) * radius, 0)
      dummy.scale.setScalar(count === 0 ? 0 : layout[i].size * moonScale)
      dummy.updateMatrix()
      mesh.setMatrixAt(i, dummy.matrix)
    }
    mesh.instanceMatrix.needsUpdate = true
  })

  return (
    <group ref={group} rotation={[tilt[0], tilt[1], tilt[2]]}>
      <mesh>
        <torusGeometry args={[radius, 0.0055, 8, 320]} />
        <meshBasicMaterial
          color={palette.ring}
          transparent
          opacity={palette.ringOpacity}
          depthWrite={false}
        />
      </mesh>
      {index === 2 && <HourTicks radius={radius} palette={palette} />}
      <instancedMesh ref={moons} args={[undefined, undefined, capacity]}>
        <sphereGeometry args={[1, 24, 24]} />
        <meshStandardMaterial roughness={0.55} metalness={0.1} />
      </instancedMesh>
    </group>
  )
}

/** Twelve hour marks on the outer orbit: the orrery doubles as a clock face. */
function HourTicks({ radius, palette }: { radius: number; palette: OrreryPalette }) {
  const ref = useRef<THREE.InstancedMesh>(null)
  useEffect(() => {
    const mesh = ref.current
    if (!mesh) return
    const dummy = new THREE.Object3D()
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2
      dummy.position.set(Math.cos(a) * (radius + 0.12), Math.sin(a) * (radius + 0.12), 0)
      dummy.rotation.set(0, 0, a)
      dummy.scale.set(i % 3 === 0 ? 0.16 : 0.08, 0.012, 0.012)
      dummy.updateMatrix()
      mesh.setMatrixAt(i, dummy.matrix)
    }
    mesh.instanceMatrix.needsUpdate = true
  }, [radius])
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, 12]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshBasicMaterial color={palette.ring} transparent opacity={Math.min(1, palette.ringOpacity * 1.8)} />
    </instancedMesh>
  )
}

function Stars({ palette, count }: { palette: OrreryPalette; count: number }) {
  const geometry = useMemo(() => {
    const positions = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      // deterministic pseudo-random shell between r=9 and r=26
      const u = ((i * 9301 + 49297) % 233280) / 233280
      const v = ((i * 4253 + 1234) % 233280) / 233280
      const w = ((i * 7177 + 9876) % 233280) / 233280
      const theta = u * Math.PI * 2
      const phi = Math.acos(2 * v - 1)
      const r = 9 + w * 17
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = r * Math.cos(phi) - 6
    }
    const g = new THREE.BufferGeometry()
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3))
    return g
  }, [count])

  return (
    <points geometry={geometry}>
      <pointsMaterial
        color={palette.stars}
        size={0.055}
        sizeAttenuation
        transparent
        opacity={palette.starsOpacity}
        depthWrite={false}
      />
    </points>
  )
}

/** Pointer parallax for the whole rig (fine pointers only), with lerped inertia. */
function Rig({
  children,
  still,
  variant,
  flatten,
}: {
  children: React.ReactNode
  still?: boolean
  variant: OrreryVariant
  flatten?: MutableRefObject<number>
}) {
  const rig = useRef<THREE.Group>(null)
  const target = useRef({ x: 0, y: 0 })
  const { gl, camera, size } = useThree()
  const baseZ = useRef(camera.position.z)

  useEffect(() => {
    if (still || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return
    const onMove = (e: PointerEvent) => {
      target.current.x = (e.clientX / window.innerWidth) * 2 - 1
      target.current.y = (e.clientY / window.innerHeight) * 2 - 1
    }
    window.addEventListener("pointermove", onMove, { passive: true })
    return () => window.removeEventListener("pointermove", onMove)
  }, [still, gl])

  useFrame((_, delta) => {
    const r = rig.current
    if (!r) return
    const strength = variant === "mini" ? 0.12 : 0.28
    const k = 1 - Math.pow(0.002, delta) // frame-rate independent lerp (~0.1 at 60fps)
    r.rotation.y += (target.current.x * strength - r.rotation.y) * k
    r.rotation.x += (target.current.y * strength * 0.6 - r.rotation.x) * k
    if (!still) r.rotation.z += delta * 0.015
    // Fit narrow (portrait) canvases, and pull back as the orbits flatten so the
    // full dial stays in frame
    const aspect = size.width / Math.max(size.height, 1)
    const fit = Math.min(Math.max(1, 1.15 / aspect), 1.8)
    camera.position.z = baseZ.current * fit * (1 + 0.3 * (flatten?.current ?? 0))
  })

  return <group ref={rig}>{children}</group>
}

// The mini dashboard orrery sits partly open so its orbits read at small sizes.
const MINI_TILT = { current: 0.45 }

export default function OrreryScene({
  variant,
  palette,
  moons,
  flatten,
  still,
  active = true,
}: OrrerySceneProps) {
  const isMini = variant === "mini"
  const tilt = flatten ?? (isMini ? MINI_TILT : undefined)
  return (
    <Canvas
      dpr={isMini ? [1, 1.5] : [1, 1.75]}
      frameloop={active && !still ? "always" : "demand"}
      camera={{ position: [0, 0, isMini ? 6.6 : 8.4], fov: 42 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      aria-hidden
    >
      <ambientLight intensity={0.35} />
      <Rig still={still} variant={variant} flatten={tilt}>
        <Core palette={palette} still={still} />
        {ORBITS.map((_, i) => (
          <Orbit
            key={i}
            index={i}
            count={moons[i]}
            palette={palette}
            flatten={tilt}
            still={still}
            moonScale={isMini ? 1.7 : 1}
          />
        ))}
      </Rig>
      {!isMini && <Stars palette={palette} count={variant === "hero" ? 1400 : 700} />}
    </Canvas>
  )
}
