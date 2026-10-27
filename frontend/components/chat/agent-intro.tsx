"use client"

/**
 * Empty-conversation screen: who Kairos is, and suggestions that send on click.
 */

import { motion } from "framer-motion"

import { KairosAvatar } from "./kairos-avatar"

interface AgentIntroProps {
  /** Called with the suggestion's text; the panel sends it right away. */
  onExampleClick: (prompt: string) => void
}

const SUGGESTIONS: { text: string; lang?: "ur" }[] = [
  { text: "What's due today?" },
  { text: "Plan my week around my high-priority tasks" },
  { text: "Add \"Call the bank\" for Friday at 10, high priority" },
  { text: "Find everything about groceries" },
  { text: "کل کے کام دکھائیں", lang: "ur" },
]

const ease = [0.22, 1, 0.36, 1] as const

export function AgentIntro({ onExampleClick }: AgentIntroProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease }}
      className="flex min-h-full flex-col justify-end gap-6 pb-2"
    >
      <div>
        <KairosAvatar className="size-12" />
        <h3 className="mt-4 font-display text-2xl font-semibold leading-tight">Hi, I&apos;m Kairos.</h3>
        <p className="mt-2 max-w-[34ch] text-sm leading-relaxed text-muted-foreground">
          I look after your list. Tell me what needs doing, ask what&apos;s next, or have me plan your week. English
          or Urdu, typed or spoken.
        </p>
      </div>

      <div>
        <p className="mb-2 text-xs text-muted-foreground">Try one</p>
        <ul className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <li key={s.text}>
              <button
                type="button"
                onClick={() => onExampleClick(s.text)}
                lang={s.lang}
                dir={s.lang === "ur" ? "rtl" : undefined}
                className="rounded-full border border-border bg-background/60 px-3.5 py-2 text-left text-sm text-foreground transition-colors duration-150 hover:border-primary/50 hover:bg-accent active:scale-[0.98]"
                style={s.lang === "ur" ? { fontFamily: "var(--font-noto-nastaliq-urdu)" } : undefined}
              >
                {s.text}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}
