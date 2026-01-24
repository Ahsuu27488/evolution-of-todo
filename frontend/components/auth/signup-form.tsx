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
import { signUpAction } from "@/app/actions/auth"

export function SignupForm() {
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<SignupInput>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      firstName: "",
      lastName: "",
    },
  })

  async function onSubmit(data: SignupInput) {
    setIsLoading(true)

    try {
      // [T035] Updated to pass firstName and lastName
      const result = await signUpAction(
        data.email,
        data.password,
        data.firstName,
        data.lastName
      )

      if (result.error) {
        // Handle specific error cases
        const errorMessage = String(result.error)
        if (errorMessage.toLowerCase().includes("already") ||
            errorMessage.toLowerCase().includes("registered")) {
          toast.error("An account with this email already exists")
        } else {
          toast.error(errorMessage || "Failed to create account")
        }
        setIsLoading(false)
        return
      }

      toast.success("Account created successfully!")
      // Use window.location.href for a hard redirect
      window.location.href = "/dashboard"
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
        {/* [T030] First name field (required) */}
        <FormField
          control={form.control}
          name="firstName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>First Name <span className="text-destructive">*</span></FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="John"
                  autoComplete="given-name"
                  disabled={isLoading}
                  className="bg-background/50 border-border/50"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* [T030] Last name field (optional) */}
        <FormField
          control={form.control}
          name="lastName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Last Name <span className="text-muted-foreground text-xs">(optional)</span></FormLabel>
              <FormControl>
                <Input
                  type="text"
                  placeholder="Doe"
                  autoComplete="family-name"
                  disabled={isLoading}
                  className="bg-background/50 border-border/50"
                  {...field}
                  value={field.value || ""}
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
