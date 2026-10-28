/** Card frame shared by the notification settings tabs: title, description, optional aside, rows. */

export function SettingsSection({
  title,
  description,
  aside,
  children,
  className,
}: {
  title: string
  description?: string
  aside?: React.ReactNode
  children?: React.ReactNode
  className?: string
}) {
  return (
    <section className={`surface overflow-hidden rounded-[var(--radius-2xl)] ${className ?? ""}`}>
      <header className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2 px-4 pt-4 pb-3 sm:px-5 sm:pt-5">
        <div className="min-w-0 flex-1 basis-56">
          <h2 className="font-display text-lg font-semibold">{title}</h2>
          {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
        </div>
        {aside && <div className="shrink-0">{aside}</div>}
      </header>
      {children}
    </section>
  )
}

/** One setting: icon, label and hint on the left, the control on the right; stacks on phones */
export function SettingsRow({
  icon,
  label,
  hint,
  children,
}: {
  icon?: React.ReactNode
  label: React.ReactNode
  hint?: React.ReactNode
  children?: React.ReactNode
}) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-3 border-t border-border px-4 py-3.5 sm:px-5">
      <div className="flex min-w-0 flex-1 basis-52 items-start gap-3">
        {icon && (
          <div aria-hidden className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-full bg-muted text-muted-foreground [&_svg]:size-4">
            {icon}
          </div>
        )}
        <div className="min-w-0">
          <div className="text-sm font-medium">{label}</div>
          {hint && <div className="mt-0.5 text-[13px] text-muted-foreground">{hint}</div>}
        </div>
      </div>
      {children && <div className="ml-auto flex shrink-0 items-center gap-3">{children}</div>}
    </div>
  )
}
