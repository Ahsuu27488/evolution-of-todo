/**
 * Notification Settings Tabs Component
 *
 * [Task]: T016, T047-T050
 * [From]: spec.md FR-033
 *
 * Push, email and in-app channels as a segmented control. The selected tab is kept in the URL
 * (?tab=) so a reload or a shared link opens the same tab.
 */

"use client"

import { useState } from "react"
import { usePathname, useRouter } from "next/navigation"
import { Bell, Mail, MessageSquare } from "lucide-react"
import { motion } from "framer-motion"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { PushSettings } from "./push-settings"
import { EmailPreferences } from "./email-preferences"
import { SettingsSection } from "./settings-section"

// =============================================================================
// In-App Settings Component
// =============================================================================

const inAppEvents = ["Tasks due soon or overdue", "Tasks assigned to you", "Task completion updates", "Announcements about Chronos"]

function InAppSettings() {
  return (
    <SettingsSection
      title="In-app notifications"
      description="Shown under the bell in the header, live while Chronos is open."
      aside={<Badge variant="success">Always on</Badge>}
    >
      <div className="border-t border-border px-4 py-4 sm:px-5">
        <p className="text-sm font-medium">You&apos;ll see a notification for</p>
        <ul className="mt-2.5 grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
          {inAppEvents.map((item) => (
            <li key={item} className="flex items-center gap-2.5">
              <span className="size-1.5 shrink-0 rounded-full bg-primary" aria-hidden />
              {item}
            </li>
          ))}
        </ul>
        <p className="mt-4 text-[13px] text-muted-foreground">
          In-app notifications can&apos;t be turned off: they are how Chronos tells you about your tasks.
          Use push or email to choose what reaches you elsewhere.
        </p>
      </div>
    </SettingsSection>
  )
}

// =============================================================================
// Component
// =============================================================================

export interface NotificationTabsProps {
  /** Initial tab to display (default: "push") */
  defaultTab?: string
}

const tabs = [
  { value: "push", label: "Push", icon: Bell },
  { value: "email", label: "Email", icon: Mail },
  { value: "in-app", label: "In-app", icon: MessageSquare },
]

export function NotificationTabs({ defaultTab = "push" }: NotificationTabsProps) {
  const [activeTab, setActiveTab] = useState(tabs.some((t) => t.value === defaultTab) ? defaultTab : "push")
  const router = useRouter()
  const pathname = usePathname()

  const handleChange = (value: string) => {
    setActiveTab(value)
    router.replace(`${pathname}?tab=${value}`, { scroll: false })
  }

  return (
    <Tabs value={activeTab} onValueChange={handleChange} className="w-full gap-5">
      <TabsList className="w-full sm:w-auto sm:self-start">
        {tabs.map(({ value, label, icon: Icon }) => (
          <TabsTrigger key={value} value={value} className="flex-1 sm:flex-initial">
            <Icon aria-hidden />
            {label}
          </TabsTrigger>
        ))}
      </TabsList>

      {tabs.map(({ value }) => (
        <TabsContent key={value} value={value} className="mt-0">
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            {value === "push" ? <PushSettings /> : value === "email" ? <EmailPreferences /> : <InAppSettings />}
          </motion.div>
        </TabsContent>
      ))}
    </Tabs>
  )
}
