/**
 * Authentication token utilities.
 *
 * Handles fetching JWT tokens from Better Auth session for API requests.
 */

/**
 * Fetch the current JWT token from the Better Auth session.
 *
 * The token is stored in an httpOnly cookie and accessed via the
 * /api/auth/token endpoint which extracts it from the session.
 *
 * @returns The JWT token string or null if not authenticated
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const response = await fetch("/api/auth/token", {
      credentials: "include",
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.token || null;
  } catch {
    return null;
  }
}
