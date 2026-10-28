/**
 * Email Preferences Component
 *
 * [Task]: T047-T050
 * [From]: spec.md FR-026, FR-033
 * [From]: contracts/api.yaml §3.1, §3.2
 *
 * Per-type email switches with a frequency (immediately, daily digest, weekly summary), the
 * digest time zone, the address with a test send, and a bounce warning. Changes collect in a
 * save bar so several switches can be flipped before saving.
 */

"use client"

import { useState, useEffect } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { AlertTriangle, Bell, Calendar, Check, Clock, Globe, Loader2, Mail, Send, Sparkles } from "lucide-react"

import { useEmailPreferences, useUpdateEmailPreferences } from "@/hooks/use-notifications"
import { NotificationType, EmailFrequency } from "@/types/notification"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Callout } from "@/components/ui/callout"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { api } from "@/lib/api-client"
import { API_URL } from "@/lib/config/api"
import { getAuthToken } from "@/lib/auth/token"
import { timezoneOptions, getUserBrowserTimezone, getTimezoneAbbreviation } from "@/lib/constants/timezones"
import { SettingsRow, SettingsSection } from "./settings-section"

// =============================================================================
// Configuration
// =============================================================================

const emailPreferenceItems = [
  { type: NotificationType.TASK_DUE, label: "Due soon", description: "A task's due time is getting close", icon: <Clock /> },
  { type: NotificationType.TASK_OVERDUE, label: "Overdue", description: "A task has passed its due time", icon: <AlertTriangle /> },
  { type: NotificationType.TASK_ASSIGNED, label: "New task for you", description: "A task is assigned to you", icon: <Sparkles /> },
  { type: NotificationType.TASK_COMPLETED, label: "Completed", description: "A task is marked done", icon: <Check /> },
  { type: NotificationType.TASK_REMINDER, label: "Reminders", description: "Nudges about upcoming tasks", icon: <Calendar /> },
]

const frequencyOptions = [
  { value: EmailFrequency.IMMEDIATE, label: "Right away", description: "One email per event" },
  { value: EmailFrequency.DAILY, label: "Daily digest", description: "One email each morning" },
  { value: EmailFrequency.WEEKLY, label: "Weekly summary", description: "One email each week" },
]

type Prefs = Record<string, { enabled: boolean; frequency: string }>

// =============================================================================
// Component
// =============================================================================

export function EmailPreferences() {
  const { data, isLoading, error, refetch, isFetching } = useEmailPreferences()
  const updatePreferences = useUpdateEmailPreferences()
  const [hasChanges, setHasChanges] = useState(false)
  const [isTestLoading, setIsTestLoading] = useState(false)
  const [localPreferences, setLocalPreferences] = useState<Prefs>({})

  // Digest time zone
  const [userTimezone, setUserTimezone] = useState<string>("UTC")
  const [isSavingTimezone, setIsSavingTimezone] = useState(false)
  const [browserTimezone] = useState<string>(() => getUserBrowserTimezone())

  useEffect(() => {
    getAuthToken()
      .then((token) => {
        if (!token) throw new Error("Not authenticated")
        return fetch(`${API_URL}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
      })
      .then((res) => res.json())
      .then((userData) => {
        if (userData.timezone) {
          setUserTimezone(userData.timezone)
        }
      })
      .catch(() => {
        setUserTimezone(browserTimezone)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fromServer = (): Prefs => {
    const prefs: Prefs = {}
    for (const pref of data?.preferences ?? []) {
      prefs[pref.notification_type] = { enabled: pref.enabled, frequency: pref.frequency }
    }
    return prefs
  }

  // Initialize local preferences when data loads
  if (data && !hasChanges && Object.keys(localPreferences).length === 0 && data.preferences.length > 0) {
    setLocalPreferences(fromServer())
  }

  const handleTimezoneChange = async (value: string) => {
    setIsSavingTimezone(true)
    try {
      const actualTimezone = value === "auto" ? browserTimezone : value
      const result = await api.updateTimezone(actualTimezone)
      if (result.success) {
        setUserTimezone(actualTimezone)
        toast.success("Time zone saved", { description: actualTimezone })
      } else {
        toast.error(result.error.message || "The time zone wasn't saved")
      }
    } catch {
      toast.error("The time zone wasn't saved")
    } finally {
      setIsSavingTimezone(false)
    }
  }

  const handleTestEmail = async () => {
    if (!data?.email_address) {
      toast.error("There's no email address on your account")
      return
    }

    setIsTestLoading(true)
    try {
      const result = await api.testEmailNotification()
      if (result.success) {
        const responseData = result.data
        if (responseData.success) {
          toast.success("Test email sent", { description: data.email_address })
        } else if (responseData.error === "no_email") {
          toast.error("There's no email address on your account")
        } else if (responseData.error === "resend_test_limitation") {
          toast.error(responseData.message, { duration: 8000 })
        } else {
          toast.error("The test email wasn't sent", { description: responseData.message || responseData.error })
        }
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("The test email wasn't sent")
    } finally {
      setIsTestLoading(false)
    }
  }

  const handleToggle = (type: string, enabled: boolean) => {
    setLocalPreferences((prev) => {
      const current = prev[type]?.frequency
      // Turning on from "none" starts with "right away"
      const frequency = enabled && (!current || current === EmailFrequency.NONE) ? EmailFrequency.IMMEDIATE : current
      return { ...prev, [type]: { enabled, frequency: frequency ?? EmailFrequency.IMMEDIATE } }
    })
    setHasChanges(true)
  }

  const handleFrequencyChange = (type: string, frequency: string) => {
    setLocalPreferences((prev) => ({ ...prev, [type]: { enabled: true, frequency } }))
    setHasChanges(true)
  }

  const handleSave = async () => {
    const preferences = Object.entries(localPreferences).map(([notification_type, pref]) => ({
      notification_type,
      enabled: pref.frequency !== EmailFrequency.NONE ? pref.enabled : false,
      frequency: pref.frequency as "immediate" | "daily" | "weekly" | "none",
    }))

    try {
      await updatePreferences.mutateAsync(preferences)
      setHasChanges(false)
      toast.success("Email preferences saved")
    } catch {
      toast.error("Email preferences weren't saved")
    }
  }

  const handleReset = () => {
    setLocalPreferences(fromServer())
    setHasChanges(false)
  }

  if (isLoading) {
    return (
      <div className="surface grid gap-4 rounded-[var(--radius-2xl)] p-5" role="status" aria-label="Loading email preferences">
        <Skeleton className="h-6 w-48" />
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-3">
            <Skeleton className="size-9 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3.5 w-1/3" />
              <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="h-[26px] w-11 rounded-full" />
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <Callout
        tone="danger"
        title="Email preferences didn't load"
        action={
          <Button variant="outline" size="sm" className="rounded-full" onClick={() => refetch()} disabled={isFetching}>
            {isFetching && <Loader2 className="animate-spin" />}
            Try again
          </Button>
        }
      >
        Check your connection, then try again.
      </Callout>
    )
  }

  const emailAddress = data?.email_address
  const tzOffsetLabel = userTimezone === "UTC" ? "UTC" : getTimezoneAbbreviation(userTimezone)

  return (
    <div className="grid gap-4 pb-20">
      {data?.bounced && (
        <Callout tone="danger" title="Emails to this address are bouncing">
          We couldn&apos;t deliver to {emailAddress || "your address"}. Check that it&apos;s correct, or use another one.
        </Callout>
      )}

      <SettingsSection title="Email" description="Where emails go and when digests arrive.">
        <SettingsRow icon={<Mail />} label="Address" hint={<span className="break-all">{emailAddress || "No email address set"}</span>}>
          {emailAddress && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleTestEmail}
              disabled={isTestLoading}
              aria-busy={isTestLoading}
              className="rounded-full"
            >
              {isTestLoading ? <Loader2 className="animate-spin" /> : <Send aria-hidden />}
              Send a test
            </Button>
          )}
        </SettingsRow>
        <SettingsRow icon={<Globe />} label="Digest time zone" hint={`Daily digests arrive at 08:00 ${tzOffsetLabel}`}>
          {isSavingTimezone && <Loader2 className="size-4 animate-spin text-muted-foreground" aria-label="Saving" />}
          <Select value={userTimezone} onValueChange={handleTimezoneChange} disabled={isSavingTimezone}>
            <SelectTrigger aria-label="Digest time zone" className="w-full sm:w-64">
              <SelectValue placeholder="Choose a time zone" />
            </SelectTrigger>
            <SelectContent align="end" className="max-h-80">
              {timezoneOptions.map((tz) => (
                <SelectItem key={tz.value} value={tz.value} description={tz.offset ? `${tz.region} · ${tz.offset}` : undefined}>
                  {tz.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </SettingsRow>
      </SettingsSection>

      <SettingsSection title="What to email you about" description="Turn each one on or off, and pick how often.">
        {emailPreferenceItems.map((item) => {
          const pref = localPreferences[item.type]
          const frequency = pref?.frequency ?? EmailFrequency.NONE
          const isOn = (pref?.enabled ?? false) && frequency !== EmailFrequency.NONE
          const switchId = `email-${item.type}`

          return (
            <SettingsRow key={item.type} icon={item.icon} label={<label htmlFor={switchId}>{item.label}</label>} hint={item.description}>
              <Select
                value={isOn ? frequency : EmailFrequency.IMMEDIATE}
                onValueChange={(value) => handleFrequencyChange(item.type, value)}
                disabled={!isOn || updatePreferences.isPending}
              >
                <SelectTrigger size="sm" aria-label={`${item.label}: how often`} className="w-40 rounded-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent align="end">
                  {frequencyOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value} description={option.description}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Switch
                id={switchId}
                checked={isOn}
                onCheckedChange={(checked: boolean) => handleToggle(item.type, checked)}
                disabled={updatePreferences.isPending}
              />
            </SettingsRow>
          )
        })}
      </SettingsSection>

      <p className="flex items-center gap-2 px-1 text-[13px] text-muted-foreground">
        <Bell className="size-3.5 shrink-0" aria-hidden />
        &ldquo;Right away&rdquo; emails are limited to 3 an hour for non-urgent events.
      </p>

      {/* Save bar: floats at the bottom while there are unsaved changes */}
      <AnimatePresence>
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="glass fixed inset-x-3 bottom-4 z-40 mx-auto flex max-w-xl items-center justify-between gap-3 rounded-full py-2 pr-2 pl-5 sm:bottom-6"
            role="region"
            aria-label="Unsaved changes"
          >
            <span className="text-sm">Unsaved changes</span>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={handleReset} disabled={updatePreferences.isPending} className="rounded-full">
                Discard
              </Button>
              <Button size="sm" onClick={handleSave} disabled={updatePreferences.isPending} aria-busy={updatePreferences.isPending} className="rounded-full">
                {updatePreferences.isPending && <Loader2 className="animate-spin" />}
                Save
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
