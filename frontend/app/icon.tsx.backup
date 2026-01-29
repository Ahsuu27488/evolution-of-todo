import { ImageResponse } from "next/og"

export const size = {
  width: 32,
  height: 32,
}

export const contentType = "image/png"

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 24,
          background: "hsl(263.4, 70%, 50%)",
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "50%",
        }}
      >
        <span
          style={{
            color: "white",
            fontFamily: "monospace",
            fontWeight: "600",
          }}
        >
          C
        </span>
        <span
          style={{
            color: "hsl(46.2, 100%, 63%)",
            fontSize: 12,
            marginLeft: "2px",
          }}
        >
          •
        </span>
      </div>
    ),
    {
      ...size,
    }
  )
}
