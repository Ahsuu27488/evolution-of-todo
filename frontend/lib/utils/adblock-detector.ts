/**
 * Ad Blocker Detection Utility
 *
 * Detects if ad blocker extensions are blocking Portal-rendered components.
 * Uses a "bait" element that mimics the characteristics of popup ads.
 */

/**
 * Detects if an ad blocker is active
 *
 * @returns true if an ad blocker is detected, false otherwise
 *
 * Technique:
 * 1. Create a "bait" element with ad-like class names
 * 2. Append it to the DOM
 * 3. Check if the browser has blocked/hid it
 * 4. Remove the bait element
 */
export function detectAdBlocker(): boolean {
  // Skip in non-browser environments
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return false
  }

  try {
    // Create a bait element that mimics common ad patterns
    const bait = document.createElement('div')
    bait.innerHTML = '&nbsp;'
    bait.className = 'ad-banner adsbox ad-placement ad-ad banner-ad'
    bait.style.cssText = `
      position: absolute;
      top: -1000px;
      left: -1000px;
      width: 1px;
      height: 1px;
      pointer-events: none;
    `

    // Append to document body
    document.body.appendChild(bait)

    // Check if the element was hidden or blocked
    const isBlocked =
      bait.offsetHeight === 0 ||
      window.getComputedStyle(bait).display === 'none' ||
      window.getComputedStyle(bait).visibility === 'hidden' ||
      !document.body.contains(bait)

    // Clean up
    document.body.removeChild(bait)

    return isBlocked
  } catch {
    // If detection fails, assume no ad blocker
    return false
  }
}

/**
 * Check if running in Chrome/Chromium browser
 * Chrome users are most likely to have ad blockers that interfere
 */
export function isChromeBrowser(): boolean {
  if (typeof navigator === 'undefined') {
    return false
  }

  const userAgent = navigator.userAgent
  return /Chrome/.test(userAgent) && !/Edg|OPR|Brave|SamsungBrowser/.test(userAgent)
}
