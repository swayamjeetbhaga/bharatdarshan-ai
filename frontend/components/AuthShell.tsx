import type { ReactNode } from "react";

export default function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="relative flex flex-1 items-center justify-center overflow-hidden px-4 py-12">
      <div
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(circle at 15% 20%, color-mix(in srgb, var(--primary) 18%, transparent), transparent 45%), radial-gradient(circle at 85% 80%, color-mix(in srgb, var(--secondary) 22%, transparent), transparent 50%)",
        }}
      />
      <svg
        className="pointer-events-none absolute inset-0 -z-10 h-full w-full opacity-[0.07]"
        aria-hidden="true"
      >
        <pattern id="auth-dots" width="28" height="28" patternUnits="userSpaceOnUse">
          <circle cx="2" cy="2" r="1.6" fill="var(--secondary)" />
        </pattern>
        <rect width="100%" height="100%" fill="url(#auth-dots)" />
      </svg>

      <div className="w-full max-w-md">
        <div className="rounded-3xl border border-border bg-card p-8 shadow-xl shadow-black/5">
          <div className="mb-7 text-center">
            <span className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-primary-foreground shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6">
                <path
                  d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21Z"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinejoin="round"
                />
                <circle cx="12" cy="9.5" r="2.4" stroke="currentColor" strokeWidth="1.8" />
              </svg>
            </span>
            <h1 className="font-display text-2xl font-semibold text-foreground">{title}</h1>
            <p className="mt-1 text-sm text-muted">{subtitle}</p>
          </div>

          {children}

          <div className="mt-6 text-center text-sm text-muted">{footer}</div>
        </div>
      </div>
    </div>
  );
}
