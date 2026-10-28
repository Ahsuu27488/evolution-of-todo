/**
 * Push Notification Settings Component
 *
 * [Task]: T028-T031
 * [From]: spec.md FR-013, FR-018, FR-019
 * [From]: contracts/api.yaml §2.1, §2.2, §2.3
 *
 * Permission status, the on/off switch for this device, a test send, and help when the browser
 * blocks or doesn't support push.
 */

"use client"

import { useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { Loader2, RefreshCw, RotateCcw, Send, Smartphone } from "lucide-react"

import { usePushSubscription, type PermissionStatus, pushKeys } from "@/hooks/use-push-subscription"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Callout } from "@/components/ui/callout"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"
import { api } from "@/lib/api-client"
import { SettingsRow, SettingsSection } from "./settings-section"

// =============================================================================
// Permission Status Display
// =============================================================================

const permissionBadge: Record<PermissionStatus, { label: string; variant: "success" | "danger" | "muted" | "warning" }> = {
  granted: { label: "Allowed", variant: "success" },
  denied: { label: "Blocked", variant: "danger" },
  default: { label: "Not asked yet", variant: "muted" },
  unsupported: { label: "Not supported", variant: "warning" },
}

// =============================================================================
// Component
// =============================================================================

export function PushSettings() {
  const queryClient = useQueryClient()

  const {
    permissionStatus,
    isSupported,
    isSubscribed,
    isLoading,
    requestPermission,
    subscribe,
    unsubscribe,
    refreshPermission,
  } = usePushSubscription()

  const [isTestLoading, setIsTestLoading] = useState(false)
  const [isResetting, setIsResetting] = useState(false)

  const handleToggle = async (enabled: boolean) => {
    if (enabled) {
      if (permissionStatus === "denied") {
        toast.error("Notifications are blocked for this site", {
          description: "Allow them in your browser's site settings, then try again.",
        })
        return
      }

      const turnOn: Promise<unknown> = permissionStatus === "granted" ? subscribe() : requestPermission()
      toast.promise(turnOn, {
        loading: "Turning on push notifications",
        success: "Push notifications are on for this device",
        error: "Push notifications couldn't be turned on",
      })
    } else {
      toast.promise(unsubscribe(), {
        loading: "Turning off push notifications",
        success: "Push notifications are off for this device",
        error: "Push notifications couldn't be turned off",
      })
    }
  }

  const handleRefresh = () => {
    refreshPermission()
    toast.success("Permission status updated")
  }

  const handleReset = async () => {
    // Clears every subscription for this account; useful when one has expired
    setIsResetting(true)
    try {
      await api.unsubscribePush()
      toast.success("Subscriptions cleared", { description: "Turn push back on to subscribe this device again." })
      queryClient.invalidateQueries({ queryKey: pushKeys.status })
    } catch {
      toast.error("Subscriptions couldn't be cleared")
    } finally {
      setIsResetting(false)
    }
  }

  const handleTest = async () => {
    setIsTestLoading(true)
    try {
      const result = await api.testPushNotification()
      if (result.success) {
        const data = result.data
        if (data.success) {
          toast.success("Test notification sent", { description: `Delivered to ${data.sent} of ${data.total} devices.` })
        } else if (data.error === "no_subscription") {
          toast.error("This device isn't subscribed yet", { description: "Turn push notifications on first." })
        } else if (data.error === "rate_limit_exceeded") {
          toast.error("Too many tests", { description: "You can send 3 push notifications an hour." })
        } else if (data.error === "config_error") {
          toast.error("Push isn't set up on the server yet")
        } else {
          toast.error("The test notification wasn't sent", { description: data.error || undefined })
        }
      } else {
        toast.error(result.error.message || "The test notification wasn't sent")
      }
    } catch (err) {
      console.error("Push test error:", err)
      toast.error("The test notification wasn't sent")
    } finally {
      setIsTestLoading(false)
    }
  }

  const badge = permissionBadge[permissionStatus] ?? permissionBadge.default

  return (
    <div className="grid gap-4">
      {!isSupported && (
        <Callout tone="warning" title="This browser can't receive push notifications">
          Try a current version of Chrome, Edge, Firefox or Safari. On iPhone, add Chronos to your Home Screen first.
        </Callout>
      )}

      <SettingsSection
        title="Push notifications"
        description="Reminders that reach you even when Chronos is closed."
        aside={<Badge variant={badge.variant}>{badge.label}</Badge>}
      >
        <SettingsRow
          icon={<Smartphone />}
          label="This device"
          hint={isSubscribed ? "Receiving notifications for your tasks" : "Not receiving notifications"}
        >
          {isLoading && <Loader2 className="size-4 animate-spin text-muted-foreground" aria-hidden />}
          <Switch
            checked={isSubscribed}
            onCheckedChange={handleToggle}
            disabled={!isSupported || permissionStatus === "denied" || isLoading}
            aria-label="Push notifications on this device"
          />
        </SettingsRow>

        {permissionStatus === "denied" && (
          <div className="border-t border-border px-4 py-4 sm:px-5">
            <Callout tone="danger" title="Notifications are blocked for this site">
              <ol className="mt-1 list-decimal space-y-1 pl-4">
                <li>Click the lock or settings icon in the address bar.</li>
                <li>Set Notifications to Allow.</li>
                <li>Reload this page and turn push on.</li>
              </ol>
            </Callout>
          </div>
        )}

        <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border px-4 py-3 sm:px-5">
          <Button variant="ghost" size="sm" onClick={handleRefresh} className="rounded-full text-muted-foreground">
            <RefreshCw aria-hidden />
            Check permission
          </Button>
          {isSubscribed && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                disabled={isResetting}
                aria-busy={isResetting}
                className="rounded-full"
              >
                {isResetting ? <Loader2 className="animate-spin" /> : <RotateCcw aria-hidden />}
                Reset subscriptions
              </Button>
              <Button
                size="sm"
                onClick={handleTest}
                disabled={isTestLoading || isLoading}
                aria-busy={isTestLoading}
                className="rounded-full"
              >
                {isTestLoading ? <Loader2 className="animate-spin" /> : <Send aria-hidden />}
                Send a test
              </Button>
            </>
          )}
        </div>
      </SettingsSection>

      <Callout tone="info" title="Good to know">
        <ul className="mt-0.5 space-y-1">
          <li>Each device and browser is set up on its own.</li>
          <li>Non-urgent pushes are limited to 3 an hour.</li>
        </ul>
      </Callout>
    </div>
  )
}
