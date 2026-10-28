/**
 * User types shared by the auth server actions and the UI.
 *
 * Auth flow: the `signInAction` / `signUpAction` server actions call the
 * FastAPI backend and store its JWT in the httpOnly `auth_token` cookie.
 * Client code reads the token through `/api/auth/token` (see lib/auth/token.ts).
 */

/** Matches the backend UserPublic schema (snake_case). */
export interface User {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
  display_name: string // Computed by backend
  created_at: string
}

/** Display name with fallbacks for legacy rows. */
export function getDisplayName(user: User): string {
  if (user.display_name) return user.display_name
  if (user.first_name && user.last_name) return `${user.first_name} ${user.last_name}`
  if (user.first_name) return user.first_name
  return user.email
}
