/**
 * Email Preferences Component
 *
 * [Task]: T047-T050
 * [From]: spec.md FR-026, FR-033
 * [From]: contracts/api.yaml §3.1, §3.2
 *
 * Features:
 * - Per-type email notification toggles
 * - Frequency selection (Immediate, Daily, Weekly, None)
 * - Bounce status warning
 * - Deep Space glassmorphism styling
 */

"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import {
  Mail,
  AlertTriangle,
  Clock,
  Calendar,
  Zap,
  Check,
  Loader2,
  Send,
  Globe,
} from "lucide-react"

import { useEmailPreferences, useUpdateEmailPreferences } from "@/hooks/use-notifications"
import { NotificationType, EmailFrequency } from "@/types/notification"
import { Card } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { api } from "@/lib/api-client"
import { timezoneOptions, getUserBrowserTimezone, getTimezoneAbbreviation } from "@/lib/constants/timezones"

// =============================================================================
// Types
// =============================================================================

interface EmailPreferenceItem {
  type: NotificationType
  label: string
  description: string
  icon: React.ReactNode
}

// =============================================================================
// Configuration
// =============================================================================

const emailPreferenceItems: EmailPreferenceItem[] = [
  {
    type: NotificationType.TASK_DUE,
    label: "Task Due Soon",
    description: "Get notified when a task deadline is approaching",
    icon: <Clock className="h-4 w-4 text-amber-500" />,
  },
  {
    type: NotificationType.TASK_OVERDUE,
    label: "Task Overdue",
    description: "Get notified when a task is past its due date",
    icon: <AlertTriangle className="h-4 w-4 text-rose-500" />,
  },
  {
    type: NotificationType.TASK_ASSIGNED,
    label: "Task Assigned",
    description: "Get notified when a task is assigned to you",
    icon: <Zap className="h-4 w-4 text-cyan-500" />,
  },
  {
    type: NotificationType.TASK_COMPLETED,
    label: "Task Completed",
    description: "Get notified when a task is marked complete",
    icon: <Check className="h-4 w-4 text-emerald-500" />,
  },
  {
    type: NotificationType.TASK_REMINDER,
    label: "Task Reminder",
    description: "Get reminded about upcoming tasks",
    icon: <Calendar className="h-4 w-4 text-blue-500" />,
  },
]

const frequencyOptions = [
  { value: EmailFrequency.IMMEDIATE, label: "Immediate", description: "Send right away" },
  { value: EmailFrequency.DAILY, label: "Daily Digest", description: "Batched daily email" },
  { value: EmailFrequency.WEEKLY, label: "Weekly Summary", description: "Batched weekly email" },
  { value: EmailFrequency.NONE, label: "Disabled", description: "No emails sent" },
]

// =============================================================================
// Component
// =============================================================================

export function EmailPreferences() {
  const { data, isLoading, error } = useEmailPreferences()
  const updatePreferences = useUpdateEmailPreferences()
  const [hasChanges, setHasChanges] = useState(false)
  const [isTestLoading, setIsTestLoading] = useState(false)
  const [localPreferences, setLocalPreferences] = useState<
    Record<string, { enabled: boolean; frequency: string }>
  >({})

  // [Fix]: Timezone state for digest scheduling
  const [userTimezone, setUserTimezone] = useState<string>("UTC")
  const [isSavingTimezone, setIsSavingTimezone] = useState(false)
  const [browserTimezone] = useState<string>(() => getUserBrowserTimezone())

  // Fetch current user timezone on mount
  useEffect(() => {
    // Get user timezone from session/me endpoint
    fetch("/api/auth/me", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((userData) => {
        if (userData.timezone) {
          setUserTimezone(userData.timezone)
        }
      })
      .catch(() => {
        // Default to browser timezone if fetch fails
        setUserTimezone(browserTimezone)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleTimezoneChange = async (value: string) => {
    setIsSavingTimezone(true)
    try {
      const actualTimezone = value === "auto" ? browserTimezone : value

      const result = await api.updateTimezone(actualTimezone)
      if (result.success) {
        setUserTimezone(actualTimezone)
        toast.success(`Timezone updated to ${actualTimezone}`)
      } else {
        toast.error(result.error.message || "Failed to update timezone")
      }
    } catch {
      toast.error("Failed to update timezone")
    } finally {
      setIsSavingTimezone(false)
    }
  }

  const handleTestEmail = async () => {
    if (!data?.email_address) {
      toast.error("No email address configured. Please add an email address first.")
      return
    }

    setIsTestLoading(true)
    try {
      const result = await api.testEmailNotification()
      if (result.success) {
        const responseData = result.data
        if (responseData.success) {
          toast.success(`Test email sent to ${data.email_address}`)
        } else if (responseData.error === "no_email") {
          toast.error("No email address configured.")
        } else if (responseData.error === "resend_test_limitation") {
          // Special message for Resend test mode limitation
          toast.error(responseData.message, {
            duration: 8000,
          })
        } else {
          toast.error(`Failed to send: ${responseData.message || responseData.error}`)
        }
      } else {
        toast.error(result.error.message)
      }
    } catch {
      toast.error("Failed to send test email")
    } finally {
      setIsTestLoading(false)
    }
  }

  // Initialize local preferences when data loads
  if (data && !hasChanges && Object.keys(localPreferences).length === 0) {
    const prefs: Record<string, { enabled: boolean; frequency: string }> = {}
    for (const pref of data.preferences) {
      prefs[pref.notification_type] = {
        enabled: pref.enabled,
        frequency: pref.frequency,
      }
    }
    setLocalPreferences(prefs)
  }

  const handleToggle = (type: string, enabled: boolean) => {
    setLocalPreferences((prev) => ({
      ...prev,
      [type]: { ...prev[type], enabled },
    }))
    setHasChanges(true)
  }

  const handleFrequencyChange = (type: string, frequency: string) => {
    setLocalPreferences((prev) => ({
      ...prev,
      [type]: { ...prev[type], frequency },
    }))
    setHasChanges(true)

    // If frequency is "none", also disable the toggle
    if (frequency === EmailFrequency.NONE) {
      setLocalPreferences((prev) => ({
        ...prev,
        [type]: { enabled: false, frequency },
      }))
    }
  }

  const handleSave = async () => {
    const preferences = Object.entries(localPreferences).map(
      ([notification_type, pref]) => ({
        notification_type,
        enabled: pref.frequency !== EmailFrequency.NONE ? pref.enabled : false,
        frequency: pref.frequency as "immediate" | "daily" | "weekly" | "none",
      })
    )

    try {
      await updatePreferences.mutateAsync(preferences)
      setHasChanges(false)
      toast.success("Email preferences updated successfully")
    } catch {
      toast.error("Failed to update email preferences")
    }
  }

  const handleReset = () => {
    if (data) {
      const prefs: Record<string, { enabled: boolean; frequency: string }> = {}
      for (const pref of data.preferences) {
        prefs[pref.notification_type] = {
          enabled: pref.enabled,
          frequency: pref.frequency,
        }
      }
      setLocalPreferences(prefs)
      setHasChanges(false)
    }
  }

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="p-6 border-destructive/50">
        <div className="flex items-center gap-3 text-destructive">
          <AlertTriangle className="h-5 w-5" />
          <div>
            <p className="font-medium">Failed to load email preferences</p>
            <p className="text-sm text-muted-foreground mt-1">Please try again later</p>
          </div>
        </div>
      </Card>
    )
  }

  const emailAddress = data?.email_address
  const bounced = data?.bounced

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Email Status Banner */}
      {bounced && (
        <Card className="mb-4 p-4 border-rose-500/50 bg-rose-500/10">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-rose-400">Email Delivery Issues</p>
              <p className="text-sm text-muted-foreground mt-1">
                We&apos;ve been unable to deliver emails to {emailAddress || "your address"}. Please update your email address or contact support.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* [Fix]: Timezone Selector for Digest Scheduling */}
      <Card className="mb-4 p-3 sm:p-4 border-border/50 bg-gradient-to-r from-primary/5 to-secondary/5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 shrink-0">
              <Globe className="h-5 w-5 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-foreground">Digest Timezone</p>
              <p className="text-sm text-muted-foreground">
                {userTimezone === "UTC" && "Daily digests at 8 AM UTC"}
                {userTimezone !== "UTC" && `Daily digests at 8 AM ${getTimezoneAbbreviation(userTimezone)}`}
              </p>
            </div>
          </div>
          <div className="w-full sm:w-auto">
            <Select
              value={userTimezone}
              onValueChange={handleTimezoneChange}
              disabled={isSavingTimezone}
            >
              <SelectTrigger className="w-full sm:w-[280px] h-9">
                <SelectValue placeholder="Select timezone..." />
              </SelectTrigger>
              <SelectContent>
                {timezoneOptions.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    <div className="flex flex-col items-start gap-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{tz.label}</span>
                        {tz.offset && (
                          <span className="text-xs text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded">
                            {tz.offset}
                          </span>
                        )}
                      </div>
                      {tz.region !== "Auto" && (
                        <span className="text-xs text-muted-foreground">{tz.region}</span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        {isSavingTimezone && (
          <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Saving timezone...</span>
          </div>
        )}
      </Card>

      {/* Email Address Display */}
      <Card className="mb-4 p-3 sm:p-4 border-border/50">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 shrink-0">
              <Mail className="h-5 w-5 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">Email Address</p>
              <p className="text-sm text-muted-foreground truncate">
                {emailAddress || "No email address set"}
              </p>
            </div>
          </div>
          {emailAddress && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleTestEmail}
              disabled={isTestLoading}
              className="w-full sm:w-auto shrink-0"
            >
              {isTestLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send Test
                </>
              )}
            </Button>
          )}
        </div>
      </Card>

      {/* Email Preferences List */}
      <Card className="border-border/50 shadow-lg overflow-hidden">
        <div className="p-3 sm:p-4 border-b border-border/50">
          <h3 className="font-semibold text-foreground text-base sm:text-lg">Email Notification Preferences</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Choose which notifications you want to receive via email
          </p>
        </div>

        <div className="divide-y divide-border/50">
          {emailPreferenceItems.map((item) => {
            const pref = localPreferences[item.type]
            const isEnabled = pref?.enabled ?? false
            const frequency = pref?.frequency ?? EmailFrequency.NONE

            return (
              <motion.div
                key={item.type}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 sm:p-4 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start gap-3 sm:gap-4">
                  {/* Icon */}
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted/50">
                    {item.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <p className="font-medium text-foreground">{item.label}</p>
                      {frequency === EmailFrequency.IMMEDIATE && isEnabled && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                          Real-time
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{item.description}</p>

                    {/* Controls */}
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
                      {/* Toggle */}
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={isEnabled && frequency !== EmailFrequency.NONE}
                          onCheckedChange={(checked: boolean) => handleToggle(item.type, checked)}
                          disabled={updatePreferences.isPending}
                        />
                        <span className="text-sm text-muted-foreground">
                          {isEnabled && frequency !== EmailFrequency.NONE ? "Enabled" : "Disabled"}
                        </span>
                      </div>

                      {/* Frequency Selector */}
                      {isEnabled && frequency !== EmailFrequency.NONE && (
                        <div className="flex items-center gap-2 w-full sm:w-auto">
                          <span className="text-sm text-muted-foreground hidden sm:inline">Frequency:</span>
                          <Select
                            value={frequency}
                            onValueChange={(value) => handleFrequencyChange(item.type, value)}
                            disabled={updatePreferences.isPending}
                          >
                            <SelectTrigger className="w-full sm:w-[140px] h-8">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {frequencyOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  <div className="flex flex-col">
                                    <span>{option.label}</span>
                                    <span className="text-xs text-muted-foreground">
                                      {option.description}
                                    </span>
                                  </div>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      {/* Enable with frequency if currently disabled */}
                      {!isEnabled && (
                        <Select
                          value={EmailFrequency.NONE}
                          onValueChange={(value) => {
                            if (value !== EmailFrequency.NONE) {
                              handleToggle(item.type, true)
                              handleFrequencyChange(item.type, value)
                            }
                          }}
                          disabled={updatePreferences.isPending}
                        >
                          <SelectTrigger className="w-full sm:w-[140px] h-8">
                            <SelectValue placeholder="Enable..." />
                          </SelectTrigger>
                          <SelectContent>
                            {frequencyOptions.filter((o) => o.value !== EmailFrequency.NONE).map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                <div className="flex flex-col">
                                  <span>{option.label}</span>
                                  <span className="text-xs text-muted-foreground">
                                    {option.description}
                                  </span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Save/Reset Buttons */}
        {hasChanges && (
          <div className="p-3 sm:p-4 border-t border-border/50 bg-muted/30 flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              disabled={updatePreferences.isPending}
              className="w-full sm:w-auto"
            >
              Reset
            </Button>
            <Button
              size="sm"
              onClick={handleSave}
              disabled={updatePreferences.isPending}
              className="bg-primary hover:bg-primary/90 w-full sm:w-auto"
            >
              {updatePreferences.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        )}
      </Card>

      {/* Info Footer */}
      <div className="mt-4 text-center">
        <p className="text-xs text-muted-foreground">
          Immediate emails may be subject to rate limiting (3 per hour for non-urgent notifications)
        </p>
      </div>
    </motion.div>
  )
}
