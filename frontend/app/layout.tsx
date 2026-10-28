import type { Metadata, Viewport } from "next"
import { Funnel_Display, Geist_Mono, Hanken_Grotesk, Noto_Nastaliq_Urdu } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { ViewTransitions } from "next-view-transitions"
import { ServiceWorkerRegistrar } from "./service-worker-registrar"

// UI text
const hanken = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
  display: "swap",
})

// Headlines
const funnel = Funnel_Display({
  variable: "--font-funnel",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  display: "swap",
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "optional",
  preload: false,
})

// Urdu font for Phase III: AI Chatbot bilingual support (T076)
// Noto Nastaliq Urdu is a Nastaliq-style font for Urdu text rendering
const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  variable: "--font-noto-nastaliq-urdu",
  subsets: ["arabic"],
  display: "swap",
  weight: ["400", "700"],
  preload: false, // only needed once Urdu text appears
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: {
    default: "Chronos: every task in its orbit",
    template: "%s | Chronos",
  },
  description: "A to-do list you can talk to. Add, plan and find tasks by typing or speaking, in English or Urdu.",
  applicationName: "Chronos",
  keywords: ["to-do list", "task manager", "AI assistant", "voice tasks", "Urdu", "productivity", "Chronos"],
  authors: [{ name: "Muhammad Ahsan", url: "https://github.com/Ahsuu27488" }],
  creator: "Muhammad Ahsan",

  // Share cards. The image comes from app/opengraph-image.tsx; X falls back to it.
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "/",
    siteName: "Chronos",
    title: "Chronos: every task in its orbit",
    description: "A to-do list you can talk to, in English or Urdu.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Chronos: every task in its orbit",
    description: "A to-do list you can talk to, in English or Urdu.",
  },

  // Icons come from files: app/favicon.ico, app/icon.svg, app/apple-icon.png (scripts/make-icons.py);
  // the manifest from app/manifest.ts.
  appleWebApp: { capable: true, title: "Chronos", statusBarStyle: "black-translucent" },

  robots: {
    index: true,
    follow: true,
  },
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  // Resize the layout when the on-screen keyboard opens so inputs stay visible (iOS Safari)
  interactiveWidget: "resizes-content",
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#0E1424" },
    { media: "(prefers-color-scheme: light)", color: "#F3F5FA" },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ViewTransitions>
      <html lang="en" suppressHydrationWarning>
        <body
          className={`${hanken.variable} ${funnel.variable} ${geistMono.variable} ${notoNastaliqUrdu.variable} antialiased min-h-screen`}
        >
          <Providers>{children}</Providers>
          {/* Register service worker for push notifications */}
          <ServiceWorkerRegistrar />
        </body>
      </html>
    </ViewTransitions>
  )
}
