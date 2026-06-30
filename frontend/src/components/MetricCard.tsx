"use client";
import { ReactNode } from "react";
import { Card } from "@/components/ui";

export function MetricCard({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: "default" | "good" | "bad" | "warn";
}) {
  const color = {
    default: "text-[var(--foreground)]",
    good: "text-[var(--success)]",
    bad: "text-[var(--danger)]",
    warn: "text-[var(--warning)]",
  }[tone];
  return (
    <Card className="p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className={`mt-2 text-2xl font-semibold tabular-nums ${color}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-[var(--muted)]">{hint}</p>}
    </Card>
  );
}
