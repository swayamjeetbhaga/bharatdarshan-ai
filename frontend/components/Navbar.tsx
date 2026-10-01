"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { isLoggedIn, logout } from "@/lib/auth";
import AiHelper from "@/components/AiHelper";
import ThemeToggle from "@/components/ThemeToggle";

function subscribe(callback: () => void) {
  window.addEventListener("storage", callback);
  return () => window.removeEventListener("storage", callback);
}

function getServerSnapshot() {
  return false;
}

function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent text-primary-foreground shadow-sm">
        <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
          <path
            d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21Z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="9.5" r="2.4" stroke="currentColor" strokeWidth="1.8" />
        </svg>
      </span>
      <span className="flex items-baseline gap-1.5">
        <span className="font-display text-xl font-semibold tracking-tight text-foreground">
          BharatDarshan
        </span>
        <span className="rounded-full bg-secondary/10 px-1.5 py-0.5 text-[0.65rem] font-bold uppercase tracking-wider text-secondary">
          AI
        </span>
      </span>
    </Link>
  );
}

export default function Navbar() {
  // Re-render (and re-read isLoggedIn) on every client-side navigation, e.g.
  // right after the login page pushes to /dashboard.
  usePathname();
  const authed = useSyncExternalStore(subscribe, isLoggedIn, getServerSnapshot);

  async function handleLogout() {
    await logout();
  }

  return (
    <nav className="sticky top-0 z-[1200] flex items-center justify-between border-b border-border bg-card/90 px-6 py-3.5 backdrop-blur-sm">
      <Logo />
      <div className="flex items-center gap-5 text-sm font-medium">
        {authed ? (
          <>
            <Link href="/favourites" className="text-foreground/80 transition-colors hover:text-primary">
              Favourites
            </Link>
            <Link href="/dashboard?category=restaurants" className="text-foreground/80 transition-colors hover:text-primary">
              Food near me
            </Link>
            <Link href="/dashboard?category=hotels" className="text-foreground/80 transition-colors hover:text-primary">
              Hotels near me
            </Link>
            <AiHelper />
            <ThemeToggle />
            <button
              onClick={handleLogout}
              className="rounded-full bg-secondary px-4 py-1.5 text-secondary-foreground transition-colors hover:opacity-90"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="text-foreground/80 transition-colors hover:text-primary">
              Login
            </Link>
            <ThemeToggle />
            <Link
              href="/signup"
              className="rounded-full bg-primary px-4 py-1.5 text-primary-foreground shadow-sm transition-colors hover:opacity-90"
            >
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
