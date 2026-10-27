// Run with: npm test  (node --test with native TypeScript type stripping)
import { test } from "node:test"
import assert from "node:assert/strict"

import { isAuthPage, isPublicPath } from "./routes.ts"

test("landing, login and signup are public", () => {
  for (const path of ["/", "/login", "/signup", "/signup/verify"]) {
    assert.equal(isPublicPath(path), true, path)
  }
})

test("app routes are protected (regression: '/' used to match every path)", () => {
  for (const path of ["/dashboard", "/profile", "/settings/notifications", "/loginx"]) {
    assert.equal(isPublicPath(path), false, path)
  }
})

test("only the auth pages redirect signed-in users", () => {
  assert.equal(isAuthPage("/login"), true)
  assert.equal(isAuthPage("/signup"), true)
  assert.equal(isAuthPage("/dashboard"), false)
})
