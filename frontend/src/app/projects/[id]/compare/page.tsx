"use client";
import { useParams, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import ProjectNav from "@/components/ProjectNav";
import { Card, EmptyState, Label, Select, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { CompareResult, Run } from "@/lib/types";
import { money, ms, pct } from "@/lib/format";

const METRIC_LABELS: Record<string, string> = {
  accuracy: "Accuracy",
  faithfulness: "Faithfulness",
  hallucination_rate: "Hallucination rate",
  toxicity_rate: "Toxicity rate",
  retrieval_precision: "Retrieval precision",
  avg_latency_ms: "Avg latency",
  total_cost_usd: "Total cost",
};

function fmt(metric: string, v: number) {
  if (metric === "avg_latency_ms") return ms(v);
  if (metric === "total_cost_usd") return money(v);
  return pct(v);
}

function CompareInner() {
  const { id } = useParams<{ id: string }>();
  const search = useSearchParams();
  const [runs, setRuns] = useState<Run[]>([]);
  const [a, setA] = useState<number | "">(search.get("a") ? +search.get("a")! : "");
  const [b, setB] = useState<number | "">(search.get("b") ? +search.get("b")! : "");
  const [result, setResult] = useState<CompareResult | null>(null);

  useEffect(() => {
    api<Run[]>(`/projects/${id}/runs`).then((rs) => {
      const done = rs.filter((r) => r.status === "completed");
      setRuns(done);
    });
  }, [id]);

  useEffect(() => {
    if (a && b && a !== b) {
      api<CompareResult>(`/projects/${id}/runs/compare?a=${a}&b=${b}`).then(setResult);
    } else {
      setResult(null);
    }
  }, [id, a, b]);

  const runLabel = (r: Run) => `#${r.id} ${r.name} · ${r.config?.model}`;

  return (
    <>
      <h1 className="mb-1 text-xl font-semibold">Compare runs</h1>
      <p className="mb-4 text-sm text-[var(--muted)]">
        Diff two completed runs side by side — prompt v7 vs v8, GPT vs Claude, before vs after.
      </p>
      <ProjectNav projectId={id} />

      {runs.length < 2 ? (
        <EmptyState title="Need at least two completed runs" hint="Run more evaluations to compare them." />
      ) : (
        <>
          <div className="mb-6 grid gap-4 md:grid-cols-2">
            <Card>
              <Label>Baseline (A)</Label>
              <Select value={a} onChange={(e) => setA(+e.target.value)}>
                <option value="">Select run…</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>
                    {runLabel(r)}
                  </option>
                ))}
              </Select>
            </Card>
            <Card>
              <Label>Candidate (B)</Label>
              <Select value={b} onChange={(e) => setB(+e.target.value)}>
                <option value="">Select run…</option>
                {runs.map((r) => (
                  <option key={r.id} value={r.id}>
                    {runLabel(r)}
                  </option>
                ))}
              </Select>
            </Card>
          </div>

          {a && b && a === b && (
            <p className="text-sm text-[var(--warning)]">Pick two different runs.</p>
          )}

          {result && (
            <Card className="p-0">
              <table className="w-full text-sm">
                <thead className="text-left text-xs uppercase tracking-wide text-[var(--muted)]">
                  <tr className="border-b border-[var(--border)]">
                    <th className="px-5 py-3">Metric</th>
                    <th className="px-5 py-3">A · #{result.run_a.id}</th>
                    <th className="px-5 py-3">B · #{result.run_b.id}</th>
                    <th className="px-5 py-3">Δ</th>
                  </tr>
                </thead>
                <tbody>
                  {result.deltas.map((d) => (
                    <tr key={d.metric} className="border-b border-[var(--border)] last:border-0">
                      <td className="px-5 py-3 font-medium">{METRIC_LABELS[d.metric] || d.metric}</td>
                      <td className="px-5 py-3 tabular-nums text-[var(--muted)]">{fmt(d.metric, d.a)}</td>
                      <td className="px-5 py-3 tabular-nums">{fmt(d.metric, d.b)}</td>
                      <td className="px-5 py-3 tabular-nums">
                        <span
                          className={
                            d.direction === "up"
                              ? "text-[var(--success)]"
                              : d.direction === "down"
                              ? "text-[var(--danger)]"
                              : "text-[var(--muted)]"
                          }
                        >
                          {d.direction === "up" ? "▲" : d.direction === "down" ? "▼" : "—"}{" "}
                          {fmt(d.metric, Math.abs(d.delta))}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}
        </>
      )}
    </>
  );
}

export default function ComparePage() {
  return (
    <AppShell>
      <Suspense fallback={<Spinner label="Loading…" />}>
        <CompareInner />
      </Suspense>
    </AppShell>
  );
}
