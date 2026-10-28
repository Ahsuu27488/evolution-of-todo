"use client"

/**
 * Profile Form Component
 *
 * Edit first and last name (the email is shown read-only). Save stays disabled until something
 * changes; after saving, the page refreshes so the header and menus show the new name.
 */

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { updateProfileAction } from "@/app/actions/auth"
import type { User } from "@/types/user"

// Validation schema for profile update
const profileSchema = z.object({
  firstName: z.string().trim().min(1, "Add your first name").max(50, "Keep it under 50 characters"),
  lastName: z.string().trim().max(50, "Keep it under 50 characters").optional(),
})

type ProfileFormData = z.infer<typeof profileSchema>

interface ProfileFormProps {
  user: User
}

export function ProfileForm({ user }: ProfileFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: user.first_name || "",
      lastName: user.last_name || "",
    },
  })

  async function onSubmit(data: ProfileFormData) {
    setIsLoading(true)

    try {
      const result = await updateProfileAction(data.firstName, data.lastName)

      if (result.error) {
        toast.error(result.error)
        return
      }

      toast.success("Profile saved")
      form.reset(data)
      router.refresh()
    } catch (error) {
      console.error("Profile update error:", error)
      toast.error("Something went wrong. Try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const isDirty = form.formState.isDirty

  return (
    <section className="surface rounded-[var(--radius-2xl)]" aria-labelledby="profile-name-title">
      <header className="px-5 pt-5 pb-1 sm:px-6 sm:pt-6">
        <h2 id="profile-name-title" className="font-display text-lg font-semibold">
          Your name
        </h2>
        <p className="mt-0.5 text-sm text-muted-foreground">Shown in your account menu.</p>
      </header>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} aria-busy={isLoading}>
          <div className="grid gap-5 px-5 py-5 sm:grid-cols-2 sm:px-6">
            <FormField
              control={form.control}
              name="firstName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>First name</FormLabel>
                  <FormControl>
                    <Input autoComplete="given-name" disabled={isLoading} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="lastName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Last name <span className="font-normal text-muted-foreground">(optional)</span>
                  </FormLabel>
                  <FormControl>
                    <Input autoComplete="family-name" disabled={isLoading} {...field} value={field.value ?? ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid gap-2 sm:col-span-2">
              <Label htmlFor="profile-email">Email</Label>
              <Input id="profile-email" value={user.email} readOnly disabled className="disabled:opacity-70" />
              <p className="text-[13px] text-muted-foreground">Your sign-in address. It can&apos;t be changed here.</p>
            </div>
          </div>

          <footer className="flex flex-col-reverse gap-2 border-t border-border px-5 py-4 sm:flex-row sm:justify-end sm:px-6">
            <Button type="button" variant="ghost" asChild>
              <Link href="/dashboard">Back to tasks</Link>
            </Button>
            <Button type="submit" disabled={isLoading || !isDirty} aria-busy={isLoading} className="min-w-32">
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" />
                  Saving
                </>
              ) : (
                "Save changes"
              )}
            </Button>
          </footer>
        </form>
      </Form>
    </section>
  )
}
