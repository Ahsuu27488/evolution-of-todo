#!/usr/bin/env node
/**
 * Database Connection Diagnostic Script - Multiple SSL Modes
 * Tests different SSL configurations to find one that works with pg + Neon.
 */

import fs from 'fs';
import path from 'path';
import { Pool } from 'pg';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read .env.local file manually
const envPath = path.join(__dirname, '..', '.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');

// Parse DATABASE_URL from .env.local
let DATABASE_URL = '';
for (const line of envContent.split('\n')) {
  if (line.startsWith('DATABASE_URL=')) {
    DATABASE_URL = line.split('=')[1].trim();
    break;
  }
}

// Remove sslmode from URL - we'll configure it in code
const DB_URL_NO_SSL = DATABASE_URL.split('?')[0];

// Parse DATABASE_URL to show just the host (for safety)
const hostMatch = DATABASE_URL.match(/@([^:/?]+)/);
const host = hostMatch ? hostMatch[1] : 'unknown';

console.log('='.repeat(50));
console.log('  🔗 Database Connection Test - Frontend (pg)');
console.log('='.repeat(50));
console.log('Host:', host);
console.log('Testing multiple SSL configurations...');
console.log('');

// Test different SSL configurations
const sslConfigs = [
  { name: 'ssl: {} (auto)', ssl: {} },
  { name: 'ssl: { rejectUnauthorized: false }', ssl: { rejectUnauthorized: false } },
  { name: 'ssl: { rejectUnauthorized: false, requestCert: false }', ssl: { rejectUnauthorized: false, requestCert: false } },
];

for (const config of sslConfigs) {
  console.log(`\n🔧 Testing: ${config.name}`);

  const pool = new Pool({
    connectionString: DB_URL_NO_SSL,
    ssl: config.ssl,
    connectionTimeoutMillis: 40000,
  });

  try {
    const client = await pool.connect();
    const res = await client.query('SELECT NOW() as current_time');
    console.log(`   ✅ SUCCESS! Server time:`, res.rows[0].current_time);
    client.release();
    await pool.end();

    console.log('\n' + '='.repeat(50));
    console.log('  ✅ Found working SSL configuration!');
    console.log('='.repeat(50));
    console.log('\n💡 Update lib/auth.ts to use:');
    console.log(`   ssl: ${JSON.stringify(config.ssl)}`);
    process.exit(0);
  } catch (err) {
    console.log(`   ❌ Failed: ${err.code || err.message}`);
    await pool.end();
  }
}

console.log('\n' + '='.repeat(50));
console.log('  ❌ All SSL configurations failed');
console.log('='.repeat(50));
console.log('\n💡 This may be a network/firewall issue. The backend works because it uses asyncpg.');
console.log('   Consider: 1) Using the backend as a proxy for auth, 2) Check if port 5432 is blocked');
process.exit(1);
