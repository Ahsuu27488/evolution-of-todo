import type { MetadataRoute } from "next"

// Web app manifest: installable app, home-screen icon and splash colours.
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Chronos",
    short_name: "Chronos",
    description: "A to-do list you can talk to. Add, plan and find tasks by typing or speaking, in English or Urdu.",
    start_url: "/dashboard",
    display: "standalone",
    background_color: "#0E1424",
    theme_color: "#0E1424",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  }
}
