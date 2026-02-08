/**
 * Common IANA timezones for user selection.
 *
 * Organized by region with UTC offset information.
 * Used in notification settings for digest email scheduling.
 */

export interface TimezoneOption {
  value: string
  label: string
  offset: string
  region: string
}

export const timezoneOptions: TimezoneOption[] = [
  // UTC
  { value: "UTC", label: "UTC (Universal Coordinated Time)", offset: "±00:00", region: "UTC" },

  // Asia
  { value: "Asia/Karachi", label: "Pakistan Time (PKT)", offset: "+05:00", region: "Asia" },
  { value: "Asia/Dubai", label: "Gulf Standard Time (GST)", offset: "+04:00", region: "Asia" },
  { value: "Asia/Riyadh", label: "Arabia Standard Time (AST)", offset: "+03:00", region: "Asia" },
  { value: "Asia/Kolkata", label: "India Standard Time (IST)", offset: "+05:30", region: "Asia" },
  { value: "Asia/Bangkok", label: "Indochina Time (ICT)", offset: "+07:00", region: "Asia" },
  { value: "Asia/Shanghai", label: "China Standard Time (CST)", offset: "+08:00", region: "Asia" },
  { value: "Asia/Tokyo", label: "Japan Standard Time (JST)", offset: "+09:00", region: "Asia" },
  { value: "Asia/Seoul", label: "Korea Standard Time (KST)", offset: "+09:00", region: "Asia" },
  { value: "Asia/Singapore", label: "Singapore Time (SGT)", offset: "+08:00", region: "Asia" },
  { value: "Asia/Jakarta", label: "Western Indonesia Time (WIB)", offset: "+07:00", region: "Asia" },
  { value: "Asia/Manila", label: "Philippines Time (PHT)", offset: "+08:00", region: "Asia" },

  // Europe
  { value: "Europe/London", label: "Greenwich Mean Time (GMT/BST)", offset: "+00:00", region: "Europe" },
  { value: "Europe/Paris", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Berlin", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Moscow", label: "Moscow Standard Time (MSK)", offset: "+03:00", region: "Europe" },
  { value: "Europe/Istanbul", label: "Turkey Time (TRT)", offset: "+03:00", region: "Europe" },
  { value: "Europe/Madrid", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Rome", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Amsterdam", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Zurich", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Stockholm", label: "Central European Time (CET)", offset: "+01:00", region: "Europe" },
  { value: "Europe/Athens", label: "Eastern European Time (EET)", offset: "+02:00", region: "Europe" },
  { value: "Europe/Helsinki", label: "Eastern European Time (EET)", offset: "+02:00", region: "Europe" },

  // Americas
  { value: "America/New_York", label: "Eastern Time (ET)", offset: "-05:00", region: "Americas" },
  { value: "America/Chicago", label: "Central Time (CT)", offset: "-06:00", region: "Americas" },
  { value: "America/Denver", label: "Mountain Time (MT)", offset: "-07:00", region: "Americas" },
  { value: "America/Los_Angeles", label: "Pacific Time (PT)", offset: "-08:00", region: "Americas" },
  { value: "America/Toronto", label: "Eastern Time (ET)", offset: "-05:00", region: "Americas" },
  { value: "America/Vancouver", label: "Pacific Time (PT)", offset: "-08:00", region: "Americas" },
  { value: "America/Mexico_City", label: "Central Time (CT)", offset: "-06:00", region: "Americas" },
  { value: "America/Sao_Paulo", label: "Brasilia Time (BRT)", offset: "-03:00", region: "Americas" },
  { value: "America/Argentina/Buenos_Aires", label: "Argentina Time (ART)", offset: "-03:00", region: "Americas" },
  { value: "America/Bogota", label: "Colombia Time (COT)", offset: "-05:00", region: "Americas" },
  { value: "America/Lima", label: "Peru Time (PET)", offset: "-05:00", region: "Americas" },
  { value: "America/Santiago", label: "Chile Time (CLT)", offset: "-04:00", region: "Americas" },

  // Oceania
  { value: "Australia/Sydney", label: "Australian Eastern Time (AET)", offset: "+10:00", region: "Oceania" },
  { value: "Australia/Melbourne", label: "Australian Eastern Time (AET)", offset: "+10:00", region: "Oceania" },
  { value: "Australia/Brisbane", label: "Australian Eastern Time (AET)", offset: "+10:00", region: "Oceania" },
  { value: "Australia/Perth", label: "Australian Western Time (AWST)", offset: "+08:00", region: "Oceania" },
  { value: "Pacific/Auckland", label: "New Zealand Time (NZST)", offset: "+12:00", region: "Oceania" },

  // Africa
  { value: "Africa/Cairo", label: "Eastern European Time (EET)", offset: "+02:00", region: "Africa" },
  { value: "Africa/Johannesburg", label: "South Africa Standard Time (SAST)", offset: "+02:00", region: "Africa" },
  { value: "Africa/Lagos", label: "West Africa Time (WAT)", offset: "+01:00", region: "Africa" },
  { value: "Africa/Nairobi", label: "East Africa Time (EAT)", offset: "+03:00", region: "Africa" },

  // Detect user's timezone
  { value: "auto", label: "Auto-detect from browser", offset: "", region: "Auto" },
]

/**
 * Get user's browser timezone using Intl API.
 *
 * @returns IANA timezone string (e.g., "Asia/Karachi")
 */
export function getUserBrowserTimezone(): string {
  if (typeof window === "undefined") return "UTC"
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
}

/**
 * Get timezone abbreviation (e.g., "PKST", "EST").
 *
 * @param timezone - IANA timezone identifier
 * @returns Timezone abbreviation
 */
export function getTimezoneAbbreviation(timezone: string): string {
  try {
    const tz = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      timeZoneName: "short",
    })
    const parts = tz.formatToParts(new Date())
    return parts.find((part) => part.type === "timeZoneName")?.value || timezone
  } catch {
    return timezone
  }
}
