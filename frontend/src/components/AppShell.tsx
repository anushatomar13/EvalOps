"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { api, clearToken, getToken } from "@/lib/api";
import { User } from "@/lib/types";
import { Spinner } from "@/components/ui";

export default function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api<User>("/auth/me")
      .then(setUser)
      .catch(() => router.replace("/login"))
      .finally(() => setChecked(true));
  }, [router]);

  function logout() {
    clearToken();
    router.replace("/login");
  }

  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner label="Loading EvalForge…" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-[var(--border)] bg-[var(--background)]/90 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
          <Link href="/projects" className="flex items-center gap-2 font-semibold">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--primary)] text-sm">⚡</span>
            EvalForge
          </Link>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/projects" className="text-[var(--muted)] hover:text-[var(--foreground)]">
              Projects
            </Link>
            <span className="text-[var(--muted)]">{user?.email}</span>
            <button onClick={logout} className="text-[var(--muted)] hover:text-[var(--danger)]">
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
    </div>
  );
}
