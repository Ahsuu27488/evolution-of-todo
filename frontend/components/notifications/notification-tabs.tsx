/**
 * Notification Settings Tabs Component
 *
 * [Task]: T016, T047-T050
 * [From]: spec.md FR-033
 * [From]: contracts/api.yaml §4.1, §4.2
 *
 * Features:
 * - Tabbed interface for notification channels
 * - Push notification settings
 * - Email notification preferences
 * - In-app notification status (always enabled)
 */

"use client"

import { useState } from "react"
import { Bell, Mail, MessageSquare } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PushSettings } from "./push-settings"
import { EmailPreferences } from "./email-preferences"
import { Card } from "@/components/ui/card"

// =============================================================================
// Tab Transition Component
// =============================================================================

interface TabTransitionProps {
  children: React.ReactNode
  className?: string
}

function TabTransition({ children, className }: TabTransitionProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={children?.toString() || "tab-content"}
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -10 }}
        transition={{ duration: 0.2 }}
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

// =============================================================================
// In-App Settings Component
// =============================================================================

function InAppSettings() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="p-6 border-border/50">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <MessageSquare className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-foreground">In-App Notifications</h3>
            <p className="text-sm text-muted-foreground">
              Real-time notifications in the app
            </p>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/50">
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 shrink-0 mt-0.5">
              <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="font-medium text-emerald-400">Always Enabled</p>
              <p className="text-sm text-muted-foreground mt-1">
                In-app notifications are essential for keeping you updated about your tasks. They appear in real-time in the notification bell icon in the header.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 space-y-2 text-sm text-muted-foreground">
          <p className="font-medium text-foreground mb-2">You&apos;ll receive in-app notifications for:</p>
          <ul className="space-y-1 ml-4 list-disc">
            <li>Tasks due soon or overdue</li>
            <li>Tasks assigned to you</li>
            <li>Task completion updates</li>
            <li>System announcements</li>
          </ul>
        </div>
      </Card>

      <Card className="mt-4 p-4 border-border/50 bg-muted/20">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 shrink-0">
            <MessageSquare className="h-4 w-4 text-primary" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">About In-App Notifications</p>
            <p className="text-xs text-muted-foreground mt-1">
              In-app notifications appear in the bell icon at the top of your screen. They update in real-time and include unread count badges.
            </p>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}

// =============================================================================
// Component
// =============================================================================

export function NotificationTabs() {
  const [activeTab, setActiveTab] = useState("push")

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="w-full justify-start mb-6 bg-muted/50 p-1">
        <TabsTrigger
          value="push"
          className="data-[state=active]:bg-background data-[state=active]:shadow-sm gap-2"
        >
          <Bell className="h-4 w-4" />
          Push
        </TabsTrigger>
        <TabsTrigger
          value="email"
          className="data-[state=active]:bg-background data-[state=active]:shadow-sm gap-2"
        >
          <Mail className="h-4 w-4" />
          Email
        </TabsTrigger>
        <TabsTrigger
          value="in-app"
          className="data-[state=active]:bg-background data-[state=active]:shadow-sm gap-2"
        >
          <MessageSquare className="h-4 w-4" />
          In-App
        </TabsTrigger>
      </TabsList>

      <TabsContent value="push" className="mt-0">
        <TabTransition>
          <PushSettings />
        </TabTransition>
      </TabsContent>

      <TabsContent value="email" className="mt-0">
        <TabTransition>
          <EmailPreferences />
        </TabTransition>
      </TabsContent>

      <TabsContent value="in-app" className="mt-0">
        <TabTransition>
          <InAppSettings />
        </TabTransition>
      </TabsContent>
    </Tabs>
  )
}
