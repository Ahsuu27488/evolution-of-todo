"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Link } from "next-view-transitions"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { signupSchema, type SignupInput } from "@/lib/validations/auth"
import { signUp } from "@/lib/auth-client"

/**
 * Signup Form using Better Auth
 *
 * Per Context7 documentation:
 * - Uses authClient.signUp.email() for registration
 * - Session cookies are handled automatically
 * - Redirects to dashboard on success via callbackURL
 */
export function SignupForm() {
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<SignupInput>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  async function onSubmit(data: SignupInput) {
    setIsLoading(true)

    try {
      console.log("Submitting signup for:", data.email)

      // Use Better Auth's signUp.email() method
      // Per Context7: authClient.signUp.email({ email, password, name, callbackURL })
      const result = await signUp({
        email: data.email,
        password: data.password,
        name: data.email.split("@")[0], // Use email prefix as name
      })

      console.log("SignUp result:", result)

      if (result.error) {
        // Handle specific error cases
        const errorMessage = result.error.message || result.error.toString()
        if (errorMessage.toLowerCase().includes("already") ||
            errorMessage.toLowerCase().includes("exists") ||
            errorMessage.toLowerCase().includes("registered")) {
          toast.error("An account with this email already exists")
        } else {
          toast.error(errorMessage || "Failed to create account")
        }
        setIsLoading(false)
        return
      }

      // Success - Better Auth handles redirect via callbackURL
      // But we show a toast for feedback
      toast.success("Account created successfully!")

      // Manual redirect as backup (Better Auth should handle via callbackURL)
      setTimeout(() => {
        window.location.href = "/dashboard"
      }, 500)
    } catch (error) {
      console.error("Signup error:", error)
      toast.error("Something went wrong. Please try again.")
      setIsLoading(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="name@example.com"
                  autoComplete="email"
                  disabled={isLoading}
                  className="bg-background/50 border-border/50"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Create a password"
                  autoComplete="new-password"
                  disabled={isLoading}
                  className="bg-background/50 border-border/50"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                  disabled={isLoading}
                  className="bg-background/50 border-border/50"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button
          type="submit"
          className="w-full shadow-lg shadow-primary/20"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating account...
            </>
          ) : (
            "Create account"
          )}
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Sign in
          </Link>
        </p>
      </form>
    </Form>
  )
}
