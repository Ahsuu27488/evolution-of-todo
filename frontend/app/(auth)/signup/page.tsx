/** Signup page. New accounts are signed in and sent to the dashboard. */

import { SignupForm } from "@/components/auth/signup-form"

export default function SignupPage() {
  return (
    <>
      <h1 className="text-[length:var(--step-h1)] font-semibold leading-tight">Create your account</h1>
      <p className="mt-2 text-muted-foreground">It takes a minute. Your first task can be the next thing you say.</p>
      <div className="mt-8">
        <SignupForm />
      </div>
    </>
  )
}
