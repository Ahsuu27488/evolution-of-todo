/**
 * Better Auth server configuration.
 * This file configures the auth server with Neon PostgreSQL and JWT support.
 *
 * The JWT plugin enables Better Auth to issue JWT tokens that can be
 * verified by the FastAPI backend for API authentication.
 *
 * References:
 * - better-auth-jwt-plugin.md in project root
 * - better-auth-nextjs.md in project root
 * - better-auth-postgres-neondb.md in project root
 */

import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"
import { nextCookies } from "better-auth/next-js"
import { Pool, neonConfig } from "@neondatabase/serverless"
import ws from "ws"

// =============================================================================
// Neon Serverless Driver Configuration
// =============================================================================

/**
 * Configure WebSocket constructor for Node.js environments.
 * Required for Node.js v21 and earlier.
 *
 * The @neondatabase/serverless driver uses WebSocket connections instead of
 * TCP, bypassing the SSL/TLS handshake issues that occur with the pg driver
 * in certain Node.js versions (particularly v24+).
 */
neonConfig.webSocketConstructor = ws

// =============================================================================
// Environment Validation
// =============================================================================

if (!process.env.DATABASE_URL) {
  throw new Error(
    "[Auth Config Error] DATABASE_URL environment variable is not set. " +
    "Get your connection string from https://console.neon.tech"
  )
}

if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error(
    "[Auth Config Error] BETTER_AUTH_SECRET environment variable is not set. " +
    "Generate one with: openssl rand -base64 32"
  )
}

// =============================================================================
// Database Configuration
// =============================================================================

/**
 * PostgreSQL connection pool using @neondatabase/serverless driver.
 *
 * The serverless driver uses WebSocket connections (wss://) instead of TCP,
 * which bypasses the SSL/TLS handshake issues that occur with the pg driver
 * in certain Node.js versions.
 *
 * Key differences from pg driver:
 * - No ssl configuration needed (WebSocket is always encrypted)
 * - Connection pooling via Neon's PgBouncer is NOT required
 * - Lower latency for serverless/edge environments
 */
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // No SSL config needed - WebSocket (wss://) is always encrypted
  // Connection pool settings optimized for serverless
  max: 10, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000, // Close idle connections after 30s
  connectionTimeoutMillis: 40000, // Wait up to 40s for connection (Neon cold start can be slow)
  application_name: "evolution-of-todo",
})

// =============================================================================
// Better Auth Instance
// =============================================================================

/**
 * Application URL for JWT issuer claim
 */
const APP_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"

/**
 * Backend API URL for JWT audience claim
 */
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const auth = betterAuth({
  /**
   * Application name shown in emails and auth UI
   */
  appName: "Evolution of Todo",

  /**
   * Base URL for auth endpoints - used for redirects and email links
   */
  baseURL: APP_URL,

  /**
   * Secret for signing sessions and tokens.
   * MUST match BETTER_AUTH_SECRET in FastAPI backend for JWT verification.
   */
  secret: process.env.BETTER_AUTH_SECRET,

  /**
   * Database adapter using pg Pool for Neon PostgreSQL
   */
  database: pool,

  /**
   * Email/Password authentication configuration
   */
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },

  /**
   * Session configuration with httpOnly cookies for XSS protection.
   * Per Session 2026-01-06 clarifications: JWT stored in httpOnly cookies.
   */
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    // httpOnly cookies for XSS protection (T014, T054)
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  /**
   * Plugins for extended functionality
   */
  plugins: [
    /**
     * Next.js cookies plugin - required for session persistence in Server Actions
     */
    nextCookies(),

    /**
     * JWT plugin for generating tokens for API authentication.
     *
     * IMPORTANT: Using HS256 algorithm with shared BETTER_AUTH_SECRET
     * to match the FastAPI backend configuration. Both services MUST use
     * the same secret for JWT signing and verification.
     */
    jwt({
      jwt: {
        expirationTime: "7d",  // Token expiration (7 days to match session)
        issuer: APP_URL,       // Issuer claim - identifies who issued the token
        audience: [API_URL],   // Audience claim - intended recipients (FastAPI backend)
      },
    }),
  ],

  // Note: Debug logging can be enabled via environment variables if needed
})

// =============================================================================
// Type Exports
// =============================================================================

export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.Session.user
