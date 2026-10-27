/** Login page. Layout and artwork come from app/(auth)/layout.tsx. */

import { LoginForm } from "@/components/auth/login-form"

export default function LoginPage() {
  return (
    <>
      <h1 className="text-[length:var(--step-h1)] font-semibold leading-tight">Welcome back</h1>
      <p className="mt-2 text-muted-foreground">Sign in to see your tasks.</p>
      <div className="mt-8">
        <LoginForm />
      </div>
    </>
  )
}
