"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import AppShell from "@/components/AppShell";
import ProjectNav from "@/components/ProjectNav";
import { MetricCard } from "@/components/MetricCard";
import { TrendChart, MultiLineChart } from "@/components/charts";
import { Badge, Button, Card, EmptyState, Spinner, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { Project, Run } from "@/lib/types";
import { dateShort, money, ms, pct } from "@/lib/format";

export default function ProjectDashboard() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [runs, setRuns] = useState<Run[] | null>(null);

  useEffect(() => {
    api<Project>(`/projects/${id}`).then(setProject);
    api<Run[]>(`/projects/${id}/runs`).then(setRuns);
  }, [id]);

  const completed = useMemo(
    () => (runs || []).filter((r) => r.status === "completed").slice().reverse(),
    [runs]
  );
  const latest = completed[completed.length - 1];

  const accuracySeries = completed.map((r) => ({ label: `#${r.id}`, value: r.accuracy }));
  const hallucinationSeries = completed.map((r) => ({ label: `#${r.id}`, value: r.hallucination_rate }));
  const latencyCost = completed.map((r) => ({
    label: `#${r.id}`,
    "latency (s)": +(r.avg_latency_ms / 1000).toFixed(2),
    "cost ($)": +r.total_cost_usd.toFixed(2),
  }));

  return (
    <AppShell>
      {project && (
        <div className="mb-6 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-semibold">{project.name}</h1>
              <Badge tone="info">{project.task_type}</Badge>
            </div>
            <p className="text-sm text-[var(--muted)]">{project.description || "No description"}</p>
          </div>
          <Link href={`/projects/${id}/run`}>
            <Button>+ Run evaluation</Button>
          </Link>
        </div>
      )}

      <ProjectNav projectId={id} />

      {runs === null ? (
        <Spinner label="Loading runs…" />
      ) : completed.length === 0 ? (
        <EmptyState
          title="No completed runs yet"
          hint="Upload a dataset, then run an evaluation to populate the dashboard."
        />
      ) : (
        <>
          <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
            <MetricCard label="Accuracy" value={pct(latest.accuracy)} tone="good" hint={`run #${latest.id}`} />
            <MetricCard label="Avg latency" value={ms(latest.avg_latency_ms)} />
            <MetricCard label="Total cost" value={money(latest.total_cost_usd)} />
            <MetricCard
              label="Hallucination"
              value={pct(latest.hallucination_rate)}
              tone={latest.hallucination_rate > 0.1 ? "bad" : "warn"}
            />
            <MetricCard label="Faithfulness" value={pct(latest.faithfulness)} tone="good" />
            <MetricCard label="Toxicity" value={pct(latest.toxicity_rate, 2)} />
            <MetricCard label="Retrieval precision" value={pct(latest.retrieval_precision)} />
            <MetricCard label="Failures" value={latest.failures} tone={latest.failures > 0 ? "bad" : "default"} />
          </div>

          <div className="mb-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <TrendChart title="Accuracy over time" data={accuracySeries} color="#22c55e" percent />
            <TrendChart title="Hallucination rate" data={hallucinationSeries} color="#ef4444" percent />
            <MultiLineChart
              title="Latency & cost over time"
              data={latencyCost}
              lines={[
                { key: "latency (s)", color: "#38bdf8", name: "Latency (s)" },
                { key: "cost ($)", color: "#f59e0b", name: "Cost ($)" },
              ]}
            />
          </div>
        </>
      )}

      <Card className="p-0">
        <div className="border-b border-[var(--border)] px-5 py-3 text-sm font-medium">Recent runs</div>
        {!runs || runs.length === 0 ? (
          <div className="p-6 text-sm text-[var(--muted)]">No runs yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs uppercase tracking-wide text-[var(--muted)]">
                <tr className="border-b border-[var(--border)]">
                  <th className="px-5 py-2.5">Run</th>
                  <th className="px-5 py-2.5">Model</th>
                  <th className="px-5 py-2.5">Status</th>
                  <th className="px-5 py-2.5">Accuracy</th>
                  <th className="px-5 py-2.5">Latency</th>
                  <th className="px-5 py-2.5">Cost</th>
                  <th className="px-5 py-2.5">When</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--surface-2)]"
                  >
                    <td className="px-5 py-3">
                      <Link href={`/projects/${id}/runs/${r.id}`} className="font-medium hover:text-[var(--primary)]">
                        #{r.id} {r.name}
                      </Link>
                    </td>
                    <td className="px-5 py-3 text-[var(--muted)]">{r.config?.model}</td>
                    <td className="px-5 py-3">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="px-5 py-3 tabular-nums">
                      {r.status === "completed" ? pct(r.accuracy) : "—"}
                    </td>
                    <td className="px-5 py-3 tabular-nums">
                      {r.status === "completed" ? ms(r.avg_latency_ms) : "—"}
                    </td>
                    <td className="px-5 py-3 tabular-nums">
                      {r.status === "completed" ? money(r.total_cost_usd) : "—"}
                    </td>
                    <td className="px-5 py-3 text-[var(--muted)]">{dateShort(r.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  );
}
