/**
 * Push Notification Settings Component
 *
 * [Task]: T028-T031
 * [From]: spec.md FR-013, FR-018, FR-019
 * [From]: contracts/api.yaml §2.1, §2.2, §2.3
 *
 * Features:
 * - Permission status display
 * - Subscribe/unsubscribe controls
 * - Device info display
 * - Browser compatibility warnings
 */

"use client"

import { useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { motion } from "framer-motion"
import {
  Bell,
  BellOff,
  Check,
  AlertTriangle,
  Loader2,
  Monitor,
  RefreshCw,
  RotateCcw,
  Send,
} from "lucide-react"

import { usePushSubscription, type PermissionStatus, pushKeys } from "@/hooks/use-push-subscription"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api-client"

// =============================================================================
// Permission Status Display
// =============================================================================

interface PermissionStatusBadgeProps {
  status: PermissionStatus
}

function PermissionStatusBadge({ status }: PermissionStatusBadgeProps) {
  const config = {
    granted: {
      label: "Enabled",
      className: "bg-emerald-500/10 text-emerald-500 border-emerald-500/50",
      icon: <Check className="h-3 w-3" />,
    },
    denied: {
      label: "Blocked",
      className: "bg-rose-500/10 text-rose-500 border-rose-500/50",
      icon: <BellOff className="h-3 w-3" />,
    },
    default: {
      label: "Not Requested",
      className: "bg-muted/50 text-muted-foreground border-border/50",
      icon: <Bell className="h-3 w-3" />,
    },
    unsupported: {
      label: "Not Supported",
      className: "bg-amber-500/10 text-amber-500 border-amber-500/50",
      icon: <AlertTriangle className="h-3 w-3" />,
    },
  }

  const { label, className, icon } = config[status] || config.default

  return (
    <div className={cn(
      "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border",
      className
    )}>
      {icon}
      <span>{label}</span>
    </div>
  )
}

// =============================================================================
// Browser Support Warning
// =============================================================================

interface BrowserSupportWarningProps {
  isSupported: boolean
}

function BrowserSupportWarning({ isSupported }: BrowserSupportWarningProps) {
  if (isSupported) return null

  return (
    <Card className="p-4 border-amber-500/50 bg-amber-500/10 mb-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="font-medium text-amber-400">Browser Not Supported</p>
          <p className="text-sm text-muted-foreground mt-1">
            Push notifications are not supported in your browser. Please try using a modern browser like Chrome, Firefox, Safari, or Edge.
          </p>
        </div>
      </div>
    </Card>
  )
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

  const handleToggle = async (enabled: boolean) => {
    if (enabled) {
      if (permissionStatus === "denied") {
        toast.error(
          "Push notifications are blocked in your browser settings. Please enable them in your browser settings.",
          { duration: 5000 }
        )
        return
      }

      if (permissionStatus === "granted") {
        toast.promise(
          subscribe(),
          {
            loading: "Subscribing to push notifications...",
            success: "Push notifications enabled!",
            error: "Failed to enable push notifications",
          }
        )
      } else {
        toast.promise(
          requestPermission(),
          {
            loading: "Requesting permission...",
            success: "Permission granted! Enabling push notifications...",
            error: "Permission denied. Push notifications will not work.",
          }
        )
      }
    } else {
      toast.promise(
        unsubscribe(),
        {
          loading: "Unsubscribing from push notifications...",
          success: "Push notifications disabled",
          error: "Failed to disable push notifications",
        }
      )
    }
  }

  const handleRefresh = () => {
    refreshPermission()
    toast.success("Permission status refreshed")
  }

  const handleReset = async () => {
    // Reset: unsubscribe from all and clear local state
    // Useful for fixing expired subscriptions
    try {
      await api.unsubscribePush() // This clears all subscriptions
      toast.success("Reset complete. Please enable push notifications again.")
      // Invalidate queries to refresh status
      queryClient.invalidateQueries({ queryKey: pushKeys.status })
    } catch {
      toast.error("Failed to reset push subscriptions")
    }
  }

  const handleTest = async () => {
    setIsTestLoading(true)
    try {
      const result = await api.testPushNotification()
      if (result.success) {
        const data = result.data
        if (data.success) {
          toast.success(`Test notification sent! (sent to ${data.sent}/${data.total} devices)`)
        } else if (data.error === "no_subscription") {
          toast.error("No subscription found. Please enable push notifications first.")
        } else if (data.error === "rate_limit_exceeded") {
          toast.error("Rate limit exceeded. Maximum 3 push notifications per hour.")
        } else if (data.error === "config_error") {
          toast.error("Push notifications not configured. Please contact support.")
        } else if (data.error === "send_failed") {
          toast.error(data.error || "Failed to send push notification")
        } else {
          toast.error(`Failed to send: ${data.error || "Unknown error"}`)
        }
      } else {
        toast.error(result.error.message || "Failed to send test notification")
      }
    } catch (err) {
      console.error("Push test error:", err)
      toast.error("Failed to send test notification")
    } finally {
      setIsTestLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Browser Support Warning */}
      <BrowserSupportWarning isSupported={isSupported} />

      {/* Main Settings Card */}
      <Card className="border-border/50 shadow-lg overflow-hidden">
        <div className="p-4 border-b border-border/50">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-foreground">Push Notifications</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Receive notifications even when your browser is closed
              </p>
            </div>
            <PermissionStatusBadge status={permissionStatus} />
          </div>
        </div>

        <div className="p-4">
          {/* Toggle */}
          <div className="flex items-center justify-between py-3 border-b border-border/50">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                {isSubscribed ? (
                  <Bell className="h-5 w-5 text-primary" />
                ) : (
                  <BellOff className="h-5 w-5 text-muted-foreground" />
                )}
              </div>
              <div>
                <p className="font-medium text-foreground">
                  {isSubscribed ? "Push Notifications Enabled" : "Push Notifications Disabled"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {isSubscribed
                    ? "You'll receive notifications for task updates"
                    : "Enable to receive notifications on this device"}
                </p>
              </div>
            </div>
            <Switch
              checked={isSubscribed}
              onCheckedChange={handleToggle}
              disabled={!isSupported || permissionStatus === "denied" || isLoading}
            />
          </div>

          {/* Permission Blocked Message */}
          {permissionStatus === "denied" && (
            <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/50">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-rose-500 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-rose-400">Notifications Blocked</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    You&apos;ve blocked push notifications in your browser. To enable them:
                  </p>
                  <ol className="text-sm text-muted-foreground mt-2 space-y-1 list-decimal list-inside">
                    <li>Click the lock/info icon in your browser&apos;s address bar</li>
                    <li>Find &quot;Notifications&quot; and set it to &quot;Allow&quot;</li>
                    <li>Refresh this page and try again</li>
                  </ol>
                </div>
              </div>
            </div>
          )}

          {/* Device Info */}
          {isSubscribed && (
            <div className="mt-4 p-3 rounded-lg bg-muted/30">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Monitor className="h-4 w-4" />
                <span>This device is subscribed to push notifications</span>
              </div>
            </div>
          )}

          {/* Refresh Button */}
          <div className="mt-4 flex items-center justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              className="text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Status
            </Button>
            {isSubscribed && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReset}
                  className="text-muted-foreground"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleTest}
                  disabled={isTestLoading || isLoading}
                >
                  {isTestLoading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4 mr-2" />
                  )}
                  Send Test
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      {/* Info Card */}
      <Card className="mt-4 p-4 border-border/50 bg-muted/20">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 shrink-0">
            <Bell className="h-4 w-4 text-primary" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-foreground">About Push Notifications</p>
            <ul className="text-xs text-muted-foreground mt-2 space-y-1">
              <li>• Works even when the browser is minimized or closed</li>
              <li>• Requires permission from your browser</li>
              <li>• Subject to rate limiting (3 per hour for non-urgent notifications)</li>
              <li>• Only available on this device - each device needs separate setup</li>
            </ul>
          </div>
        </div>
      </Card>
    </motion.div>
  )
}
