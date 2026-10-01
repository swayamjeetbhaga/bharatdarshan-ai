"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signup } from "@/lib/auth";
import { extractErrorMessage } from "@/lib/api";
import AuthShell from "@/components/AuthShell";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSignup(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await signup(email, username, password);
      router.push("/login");
    } catch (err) {
      setError(extractErrorMessage(err, "Could not create account. Email may already be registered."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      title="Start your journey"
      subtitle="Create an account to discover incredible India."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-primary hover:underline">
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSignup} className="flex flex-col gap-4">
        <div>
          <label htmlFor="username" className="mb-1 block text-xs font-medium text-muted">
            Username
          </label>
          <input
            id="username"
            required
            placeholder="wanderer99"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm outline-none transition-colors focus:border-primary"
          />
        </div>
        <div>
          <label htmlFor="email" className="mb-1 block text-xs font-medium text-muted">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm outline-none transition-colors focus:border-primary"
          />
        </div>
        <div>
          <label htmlFor="password" className="mb-1 block text-xs font-medium text-muted">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm outline-none transition-colors focus:border-primary"
          />
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="mt-1 w-full rounded-xl bg-primary py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Creating account…" : "Sign up"}
        </button>
      </form>
    </AuthShell>
  );
}
