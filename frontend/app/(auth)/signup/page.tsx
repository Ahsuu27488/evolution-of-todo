/** Signup Page with Deep Space Glassmorphism.
 *
 * Per spec.md US1: Discover and Sign Up
 * - "frictionless registration"
 * - "automatically logged in to their new task dashboard"
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SignupForm } from "@/components/auth/signup-form"
import { Sparkles } from "lucide-react"

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4 relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/10 rounded-full blur-3xl" />
      </div>

      <Card className="w-full max-w-md glass-modal border-primary/20">
        <CardHeader className="space-y-2 text-center pb-6">
          {/* Logo/Icon */}
          <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 mb-4">
            <Sparkles className="h-8 w-8 text-background" />
          </div>

          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Create an Account
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Enter your details to begin your journey
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SignupForm />
        </CardContent>

        {/* Footer text */}
        <div className="px-8 pb-6 text-center">
          <p className="text-sm text-muted-foreground">
            Part of the{" "}
            <span className="text-primary font-medium">Evolution of Todo</span>
            {" "}project
          </p>
        </div>
      </Card>
    </div>
  )
}
