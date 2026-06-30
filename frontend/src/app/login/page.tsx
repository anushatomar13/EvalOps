"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, login, setToken } from "@/lib/api";
import { Button, Card, Input, Label } from "@/components/ui";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let token: string;
      if (mode === "register") {
        const res = await api<{ access_token: string }>("/auth/register", {
          method: "POST",
          auth: false,
          body: { email, password, full_name: fullName },
        });
        token = res.access_token;
      } else {
        token = await login(email, password);
      }
      setToken(token);
      router.replace("/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--primary)] text-2xl">
            ⚡
          </div>
          <h1 className="text-2xl font-semibold">EvalForge</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Continuous Evaluation & Observability for AI Systems
          </p>
        </div>

        <Card>
          <div className="mb-5 flex rounded-lg bg-[var(--surface-2)] p-1 text-sm">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 rounded-md py-1.5 capitalize transition-colors ${
                  mode === m ? "bg-[var(--primary)] text-white" : "text-[var(--muted)]"
                }`}
              >
                {m === "login" ? "Sign in" : "Create account"}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            {mode === "register" && (
              <div>
                <Label>Full name</Label>
                <Input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Ada Lovelace" />
              </div>
            )}
            <div>
              <Label>Email</Label>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
              />
            </div>
            <div>
              <Label>Password</Label>
              <Input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
            </Button>
          </form>
        </Card>
        <p className="mt-4 text-center text-xs text-[var(--muted)]">
          The first account created becomes the workspace admin.
        </p>
      </div>
    </div>
  );
}
