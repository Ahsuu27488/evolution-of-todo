"use client"

/**
 * What Chronos does, shown with the product's own UI rather than icon tiles.
 * The conversation and tasks are illustrative examples and labelled as such.
 */

import { motion, useReducedMotion } from "framer-motion"
import { Bell, CalendarClock, Check, Mail, Mic, Repeat, Search, Smartphone } from "lucide-react"

import { cn } from "@/lib/utils"

const ease = [0.22, 1, 0.36, 1] as const

function Tile({
  className,
  children,
  index,
}: {
  className?: string
  children: React.ReactNode
  index: number
}) {
  const reduceMotion = useReducedMotion()
  return (
    <motion.article
      initial={reduceMotion ? false : { opacity: 0, y: 28 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, ease, delay: index * 0.06 }}
      className={cn("surface relative flex flex-col overflow-hidden rounded-[var(--radius-3xl)] p-6 sm:p-7", className)}
    >
      {children}
    </motion.article>
  )
}

function TileTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-xl font-semibold leading-snug sm:text-2xl">{children}</h3>
}

export function FeatureBento() {
  return (
    <section aria-labelledby="features-title" className="px-5 py-[clamp(4rem,10vw,8rem)] sm:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-2xl">
          <h2 id="features-title" className="text-[length:var(--step-h1)] font-semibold leading-[1.05]">
            Say what needs doing. Kairos files it.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Kairos, the assistant built into Chronos, creates, updates and finds tasks for you. You can always edit
            them by hand.
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-6 md:grid-rows-[auto_auto]">
          {/* Conversation example: the largest tile */}
          <Tile index={0} className="md:col-span-4 md:row-span-2">
            <TileTitle>Chat with your list</TileTitle>
            <p className="mt-2 max-w-md text-muted-foreground">
              Ask in plain words. Kairos picks out the date, priority and tags, then shows you the task it made.
            </p>
            <div className="mt-8 flex flex-1 flex-col justify-end gap-3" aria-label="Example conversation">
              <span className="text-xs text-muted-foreground">Example</span>
              <p className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-primary-foreground">
                Remind me to call the bank on Friday at 10, it&apos;s important
              </p>
              <div className="max-w-[90%] rounded-2xl rounded-bl-md bg-muted px-4 py-3">
                <p>Done. I added it for Friday at 10:00 with high priority.</p>
                <div className="mt-3 flex items-center gap-3 rounded-xl border border-border bg-background/60 p-3">
                  <span className="grid size-5 shrink-0 place-items-center rounded-full border-2 border-destructive" aria-hidden />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">Call the bank</p>
                    <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                      <CalendarClock className="size-3.5" aria-hidden /> Fri 10:00 · High · finance
                    </p>
                  </div>
                </div>
              </div>
              <p className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-primary-foreground">
                What&apos;s left for this week?
              </p>
            </div>
          </Tile>

          {/* Voice */}
          <Tile index={1} className="md:col-span-2">
            <div className="flex items-center gap-3">
              <span className="grid size-11 place-items-center rounded-full bg-primary text-primary-foreground" aria-hidden>
                <Mic className="size-5" />
              </span>
              <div className="flex h-8 flex-1 items-center gap-[3px]" aria-hidden>
                {[0.3, 0.7, 0.5, 1, 0.6, 0.85, 0.4, 0.75, 0.35, 0.9, 0.5, 0.65, 0.3, 0.55].map((h, i) => (
                  <span key={i} className="w-full rounded-full bg-secondary/70" style={{ height: `${h * 100}%` }} />
                ))}
              </div>
            </div>
            <div className="mt-6">
              <TileTitle>Hold to talk</TileTitle>
              <p className="mt-2 text-muted-foreground">Speak a task or a question. Whisper turns it into text in seconds.</p>
            </div>
          </Tile>

          {/* Semantic search */}
          <Tile index={2} className="md:col-span-2">
            <div className="flex items-center gap-2 rounded-full border border-border bg-background/60 px-4 py-2 text-sm">
              <Search className="size-4 text-muted-foreground" aria-hidden />
              <span>groceries</span>
            </div>
            <ul className="mt-3 space-y-1.5 text-sm" aria-label="Example results">
              <li className="flex items-center gap-2"><Check className="size-3.5 text-primary" aria-hidden /> Buy milk and eggs</li>
              <li className="flex items-center gap-2"><Check className="size-3.5 text-primary" aria-hidden /> Pick up rice for Sunday</li>
            </ul>
            <div className="mt-6">
              <TileTitle>Find by meaning</TileTitle>
              <p className="mt-2 text-muted-foreground">Search understands what you mean, not just the words you typed.</p>
            </div>
          </Tile>

          {/* Reminders */}
          <Tile index={3} className="md:col-span-3">
            <TileTitle>Reminders where you are</TileTitle>
            <p className="mt-2 text-muted-foreground">
              Get nudged in the app, as a push notification, or by email, with a daily or weekly digest if you prefer.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 text-sm">
              {[
                { icon: Bell, label: "In-app" },
                { icon: Smartphone, label: "Push" },
                { icon: Mail, label: "Email digest" },
              ].map(({ icon: Icon, label }) => (
                <span key={label} className="inline-flex items-center gap-2 rounded-full bg-muted px-3.5 py-1.5">
                  <Icon className="size-4 text-secondary" aria-hidden /> {label}
                </span>
              ))}
            </div>
          </Tile>

          {/* Recurring */}
          <Tile index={4} className="md:col-span-3">
            <div className="flex items-start justify-between gap-4">
              <div>
                <TileTitle>Tasks that come back</TileTitle>
                <p className="mt-2 text-muted-foreground">
                  Daily, weekly or monthly. Finish one and the next is already scheduled.
                </p>
              </div>
              <Repeat className="size-7 shrink-0 text-primary" aria-hidden />
            </div>
          </Tile>

          {/* Bilingual */}
          <Tile index={5} className="md:col-span-6">
            <div className="grid items-center gap-6 md:grid-cols-[1fr_auto]">
              <div>
                <TileTitle>English and Urdu</TileTitle>
                <p className="mt-2 max-w-lg text-muted-foreground">
                  Write or speak in either language. Kairos answers in the one you used and lays Urdu out right to left.
                </p>
              </div>
              <p
                lang="ur"
                dir="rtl"
                className="font-urdu text-2xl leading-[2.2] text-foreground sm:text-3xl"
                style={{ fontFamily: "var(--font-noto-nastaliq-urdu)" }}
              >
                کل صبح دس بجے بینک کو فون کرنا ہے
              </p>
            </div>
          </Tile>
        </div>
      </div>
    </section>
  )
}
