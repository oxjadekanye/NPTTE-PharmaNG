"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, error, setError } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login({ username, password });
      router.push("/regulator");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-sovereign-950 px-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-md rounded-2xl border border-sovereign-800 bg-sovereign-900/80 p-8 shadow-xl"
      >
        <p className="text-xs uppercase tracking-widest text-sovereign-accent">NPTTE Command Access</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Regulator sign in</h1>
        {error && <p className="mt-4 rounded bg-red-500/10 px-3 py-2 text-sm text-red-400">{error}</p>}
        <label className="mt-6 block text-sm text-slate-400">
          Username
          <input
            className="mt-1 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-2 text-white"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label className="mt-4 block text-sm text-slate-400">
          Password
          <input
            type="password"
            className="mt-1 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-2 text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <button
          type="submit"
          disabled={submitting}
          className="mt-6 w-full rounded-lg bg-sovereign-accent py-2.5 font-medium text-sovereign-950 disabled:opacity-50"
        >
          {submitting ? "Authenticating…" : "Enter command center"}
        </button>
      </form>
    </div>
  );
}
