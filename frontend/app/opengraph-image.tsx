import { ImageResponse } from "next/og"

// Social share card (Open Graph + Twitter). Rendered at build time.
export const alt = "Chronos: every task in its orbit"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

const INK = "#0E1424"
const STARLIGHT = "#E9ECF5"
const MUTED = "#9AA3BA"
const GOLD = "#F2B84B"

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          backgroundColor: INK,
          backgroundImage: "radial-gradient(circle at 78% 50%, rgba(242,184,75,0.18), rgba(242,184,75,0) 55%)",
          color: STARLIGHT,
          fontFamily: "sans-serif",
          position: "relative",
        }}
      >
        {/* Orrery: three tilted orbits around the "now" core */}
        <svg width="760" height="630" viewBox="0 0 760 630" style={{ position: "absolute", right: -120, top: 0 }}>
          <g transform="translate(380 315)">
            <ellipse rx="170" ry="64" fill="none" stroke={STARLIGHT} strokeOpacity="0.35" strokeWidth="2" transform="rotate(-18)" />
            <ellipse rx="255" ry="98" fill="none" stroke={STARLIGHT} strokeOpacity="0.28" strokeWidth="2" transform="rotate(14)" />
            <ellipse rx="345" ry="120" fill="none" stroke={STARLIGHT} strokeOpacity="0.2" strokeWidth="2" transform="rotate(-6)" />
            <circle r="96" fill={GOLD} opacity="0.18" />
            <circle r="66" fill={GOLD} />
            <circle cx="150" cy="-70" r="11" fill="#FFE2A3" />
            <circle cx="-120" cy="58" r="9" fill="#FFE2A3" />
            <circle cx="232" cy="64" r="10" fill="#CFE0FF" />
            <circle cx="-246" cy="-40" r="8" fill="#CFE0FF" />
            <circle cx="300" cy="-90" r="9" fill="#CFE0FF" />
            <circle cx="-330" cy="40" r="7" fill="#CFE0FF" />
          </g>
        </svg>

        <div style={{ display: "flex", flexDirection: "column", justifyContent: "space-between", padding: "72px 80px", width: 680 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 34, fontWeight: 600 }}>
            <svg width="44" height="44" viewBox="0 0 32 32">
              <ellipse cx="16" cy="16" rx="13" ry="5.5" transform="rotate(-24 16 16)" fill="none" stroke={STARLIGHT} strokeOpacity="0.55" strokeWidth="1.6" />
              <circle cx="16" cy="16" r="5.4" fill={GOLD} />
              <circle cx="27.2" cy="10.8" r="2" fill={STARLIGHT} />
            </svg>
            Chronos
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <div style={{ fontSize: 84, fontWeight: 700, lineHeight: 1.02, letterSpacing: "-0.04em" }}>
              Every task in its orbit.
            </div>
            <div style={{ fontSize: 30, color: MUTED, marginTop: 28, lineHeight: 1.35 }}>
              A to-do list you can talk to, in English or Urdu.
            </div>
          </div>
        </div>
      </div>
    ),
    size
  )
}
