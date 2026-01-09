# Neon PostgreSQL Mastery Guide

## Overview
Neon is a serverless PostgreSQL platform that separates storage and compute, offering autoscaling, branching, and instant restore. This skill provides expert-level guidance for connecting to, troubleshooting, and optimizing Neon database connections in Node.js, TypeScript, and serverless environments.

## Driver Selection Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NEON DRIVER DECISION TREE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐                          │
│  │ Serverless/Edge  │    │ Long-running     │                          │
│  │ Functions?       │───▶│ Server (Node.js) │                          │
│  │ Vercel/Cloudflare│    │ Docker/Bare metal│                          │
│  └────────┬─────────┘    └────────┬─────────┘                          │
│           │                       │                                     │
│           ▼                       ▼                                     │
│  ┌──────────────────┐    ┌──────────────────┐                          │
│  │ @neondatabase/   │    │  pg (node-       │                          │
│  │ serverless       │    │  postgres)       │                          │
│  │ (WebSocket/HTTP) │    │  (TCP connection)│                          │
│  └──────────────────┘    └──────────────────┘                          │
│                                                                         │
│  WebSocket/HTTP Pooler:                                                 │
│  • HTTP fetch: Stateless, single queries, lowest latency (~1ms)         │
│  • WebSocket: Sessions, transactions, multi-query operations            │
│                                                                         │
│  TCP (pg):                                                              │
│  • Requires PgBouncer pooling enabled                                   │
│  • Better for persistent connections                                    │
│  • Standard PostgreSQL protocol                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### When to Use Each Driver

| Use Case | Recommended Driver | Why |
|----------|-------------------|-----|
| Vercel Edge Functions, Cloudflare Workers | `@neondatabase/serverless` (HTTP fetch) | No TCP support, sub-10ms cold starts |
| Next.js Server Actions/Route Handlers | `@neondatabase/serverless` (WebSocket Pool) | Serverless-friendly, session support |
| Long-running Node.js servers, FastAPI backend | `pg` with PgBouncer | Persistent connections, battle-tested |
| Lambda/Functions requiring transactions | `@neondatabase/serverless` (Client/Pool) | WebSocket maintains session state |

## Connection String Formats

```
# Direct connection (NO pooling - avoid for serverless)
postgresql://user:pass@ep-xxx.aws.neon.tech/dbname?sslmode=require

# Pooled connection (REQUIRED for serverless, using pg driver)
postgresql://user:pass@ep-xxx-pooler.aws.neon.tech/dbname?sslmode=require&channel_binding=require

# Serverless driver (uses HTTP/WebSocket automatically)
postgresql://user:pass@ep-xxx.aws.neon.tech/dbname
```

**Critical:** The `-pooler` suffix in the hostname indicates connection pooling via PgBouncer.

## SSL/TLS Configuration

### For `pg` Driver
```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false, // Only for local dev
    // For production: omit entirely, let connection string params handle it
  },
  connectionTimeoutMillis: 10000,
});
```

### For `@neondatabase/serverless` Driver
```typescript
import { neon, neonConfig } from '@neondatabase/serverless';
import ws from 'ws';

// REQUIRED for Node.js v21 and earlier
neonConfig.webSocketConstructor = ws;

// HTTP fetch for single queries (lowest latency)
const sql = neon(process.env.DATABASE_URL);

// WebSocket for sessions/transactions
import { Pool } from '@neondatabase/serverless';
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
```

## Common Connection Errors & Solutions

### Error: `ETIMEDOUT`

**Symptoms:** Connection hangs, then times out after several seconds.

**Root Causes:**
1. **Connection pooling disabled** in Neon console
2. **Wrong endpoint** (using direct instead of pooler with `pg` driver)
3. **Firewall/ISP blocking** PostgreSQL-over-TLS (port 5432)
4. **SSL handshake failure** due to incompatible `ssl` config

**Diagnostic Steps:**
```bash
# Test raw TCP connectivity
nc -zv ep-xxx.aws.neon.tech 5432

# If succeeds but Node.js times out → SSL/TLS issue
# If fails → Network/firewall issue
```

**Solutions (in order):**
```typescript
// 1. Enable connection pooling in Neon Console → Connection Details
// 2. Use pooler endpoint with pgbouncer parameter
DATABASE_URL="postgresql://user:pass@ep-xxx-pooler.aws.neon.tech/dbname?pgbouncer=true&sslmode=require"

// 3. For serverless: switch to @neondatabase/serverless driver
```

### Error: `ECONNREFUSED`

**Symptoms:** Immediate connection refusal.

**Root Causes:**
1. Wrong hostname or port
2. Neon compute autosuspended (cold start)
3. IP not in allowlist (if IP restriction enabled)

**Solutions:**
- Verify hostname from Neon Console
- Allow 30-60 seconds for compute wake-up
- Check IP allowlist settings

### Error: `password authentication failed`

**Symptoms:** Auth fails even with correct credentials.

**Root Cause:** Driver doesn't support Server Name Indication (SNI).

**Solution:** Embed endpoint ID in password:
```typescript
// Format: endpoint=<endpoint_id>;<password>
const connectionString = `postgresql://user:endpoint=${endpointId};${password}@${host}/db?sslmode=require&channel_binding=require`;
```

## PgBouncer Configuration (Neon Default)

```ini
[pgbouncer]
pool_mode = transaction      # Each transaction gets a connection
max_client_conn = 10000      # Maximum concurrent clients
default_pool_size = 0.9 * max_connections
max_prepared_statements = 1000
query_wait_timeout = 120     # Seconds before queued query times out
```

**Implications:**
- Transaction mode: Connections returned after each transaction
- `query_wait_timeout`: Long queries (>120s) will be dropped
- Use batch operations for bulk inserts/updates

## Connection Retry with Exponential Backoff

```typescript
import { Pool } from 'pg';
import retry from 'retry';

const connectionString = process.env.DATABASE_URL;

function connectWithRetry(): Promise<Pool> {
  return new Promise((resolve, reject) => {
    const operation = retry.operation({
      retries: 5,
      minTimeout: 4000,
      maxTimeout: 30000,
      randomize: true,
    });

    operation.attempt(async (currentAttempt) => {
      try {
        const pool = new Pool({
          connectionString,
          connectionTimeoutMillis: 10000,
        });

        // Test connection
        const client = await pool.connect();
        await client.query('SELECT NOW()');
        client.release();

        console.log(`Connected on attempt ${currentAttempt}`);
        resolve(pool);
      } catch (err) {
        if (operation.retry(err as Error)) {
          console.warn(`Connection failed, retrying... (${currentAttempt})`);
          return;
        }
        reject(new Error(`Connection failed after ${currentAttempt} attempts`));
      }
    });
  });
}
```

## Serverless Best Practices

1. **Always use connection pooling** for `pg` driver
2. **Prefer `@neondatabase/serverless`** for true serverless (Edge, Lambda)
3. **Limit max connections** in your pool (5-10 is usually sufficient)
4. **Release connections promptly** - use `try/finally`
5. **Set appropriate timeouts** - don't wait indefinitely
6. **Use HTTP fetch mode** (`neon()`) for single queries in edge functions

## Example: Next.js Server Action with Better Auth

```typescript
// lib/auth.ts - Better Auth configuration for Neon
import { betterAuth } from "better-auth";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {}, // Let Neon's SSL params in connection string handle it
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
});

export const auth = betterAuth({
  database: pool,
  secret: process.env.BETTER_AUTH_SECRET,
  // ... rest of config
});
```

## Troubleshooting Checklist

- [ ] Connection pooling enabled in Neon Console?
- [ ] Using pooler endpoint (`-pooler` suffix) for `pg` driver?
- [ ] Connection string has `?sslmode=require&channel_binding=require`?
- [ ] For Node.js ≤ v21: configured `neonConfig.webSocketConstructor`?
- [ ] Firewall allows outbound PostgreSQL (port 5432)?
- [ ] Not exceeding PgBouncer's `query_wait_timeout` (120s)?
- [ ] Using appropriate driver for your deployment target?

## Key Takeaways

1. **Serverless requires pooling** - Neon's PgBouncer is mandatory for non-serverless driver
2. **`@neondatabase/serverless` bypasses TCP** - Uses HTTP/WebSocket, avoiding pooler requirement
3. **ETIMEDOUT usually means pooling disabled** - Check Neon Console first
4. **SSL is mandatory** - Neon requires TLS; use `sslmode=require`
5. **Cold starts are normal** - First connection after idleness takes longer
