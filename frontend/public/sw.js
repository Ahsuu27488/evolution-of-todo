/**
 * Service Worker for Push Notifications.
 *
 * [Task]: T033
 * [From]: spec.md FR-018-FR-023
 * [From]: Web Push API documentation
 *
 * Features:
 * - Push event handler with notification display
 * - Notification click handler for navigation
 * - Deep Space themed notifications (icon, badge, colors)
 *
 * NOTE: This file must be plain JavaScript, not TypeScript.
 * Browsers cannot execute TypeScript in service workers.
 */

// =============================================================================
// Configuration
// =============================================================================

const NOTIFICATION_ICON = "/icon.png"
const NOTIFICATION_BADGE = "/icon.png"  // Using same icon for badge
const DEFAULT_TITLE = "Chronos Todo"

// =============================================================================
// Push Event Handler
// =============================================================================

self.addEventListener("push", (event) => {
  if (!event.data) {
    // No payload, show default notification
    self.registration.showNotification(DEFAULT_TITLE, {
      icon: NOTIFICATION_ICON,
      badge: NOTIFICATION_BADGE,
    })
    return
  }

  try {
    const data = event.data.json()
    const { title, body, icon, badge, data: notificationData } = data

    // Show notification with Deep Space theme colors
    const options = {
      body: body || "",
      icon: icon || NOTIFICATION_ICON,
      badge: badge || NOTIFICATION_BADGE,
      data: notificationData || {},
      // Silent notification (no sound) - can be customized per user preference
      silent: false,
      // Require interaction for important notifications
      requireInteraction: data.requireInteraction || false,
      // Vibration pattern for attention
      vibrate: data.urgent ? [200, 100, 200] : undefined,
      // Tag for grouping/replacing
      tag: data.tag || "default",
      // Renotify for updates to same tag
      renotify: data.renotify || false,
    }

    event.waitUntil(
      self.registration.showNotification(title || DEFAULT_TITLE, options)
    )
  } catch (error) {
    console.error("Error parsing push data:", error)
    // Fallback to simple notification
    event.waitUntil(
      self.registration.showNotification(DEFAULT_TITLE, {
        icon: NOTIFICATION_ICON,
        badge: NOTIFICATION_BADGE,
      })
    )
  }
})

// =============================================================================
// Notification Click Handler
// =============================================================================

self.addEventListener("notificationclick", (event) => {
  event.notification.close()

  const notificationData = event.notification.data || {}
  const urlToOpen = notificationData.url || "/dashboard"

  event.waitUntil(
    (async () => {
      // Check if there's already a window/tab open
      const clients = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      })

      // Focus existing window if available
      for (const client of clients) {
        const url = new URL(client.url)
        if (url.pathname === "/dashboard" || url.pathname === "/") {
          await client.focus()
          // Navigate to specific task if provided
          if (notificationData.task_id) {
            client.postMessage({
              type: "NAVIGATE_TO_TASK",
              taskId: notificationData.task_id,
            })
          }
          return
        }
      }

      // Open new window if no existing window
      if (clients.length === 0) {
        const newClient = await self.clients.openWindow(urlToOpen)
        if (newClient && notificationData.task_id) {
          newClient.postMessage({
            type: "NAVIGATE_TO_TASK",
            taskId: notificationData.task_id,
          })
        }
      }
    })()
  )
})

// =============================================================================
// Install Event - Cache Assets
// =============================================================================

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      try {
        // Cache notification icon for offline support
        const cache = await self.caches.open("notification-assets")
        await cache.add(NOTIFICATION_ICON).catch(() => {
          console.warn("[SW] Could not cache icon:", NOTIFICATION_ICON)
        })
      } catch (error) {
        console.warn("[SW] Could not cache assets:", error)
      }
    })()
  )
})

// =============================================================================
// Activate Event - Clean Up Old Caches
// =============================================================================

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      // Clean up old caches if needed
      const cacheNames = await self.caches.keys()
      await Promise.all(
        cacheNames
          .filter((name) => name.startsWith("notification-"))
          .filter((name) => name !== "notification-assets")
          .map((name) => self.caches.delete(name))
      )
    })()
  )
})
