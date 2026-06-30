"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Fragment, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { MetricCard } from "@/components/MetricCard";
import { Badge, Button, Card, Spinner, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { Run, RunResult } from "@/lib/types";
import { money, ms, pct } from "@/lib/format";

export default function RunDetail() {
  const { id, runId } = useParams<{ id: string; runId: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [results, setResults] = useState<RunResult[] | null>(null);
  const [onlyFailures, setOnlyFailures] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    function poll() {
      api<Run>(`/projects/${id}/runs/${runId}`).then((r) => {
        if (!active) return;
        setRun(r);
        // Re-poll while the job is still queued/running.
        if (r.status === "queued" || r.status === "running") {
          setTimeout(poll, 1500);
        }
      });
    }
    poll();
    return () => {
      active = false;
    };
  }, [id, runId]);

  useEffect(() => {
    if (run?.status === "completed") {
      api<RunResult[]>(
        `/projects/${id}/runs/${runId}/results?only_failures=${onlyFailures}&limit=500`
      ).then(setResults);
    }
  }, [id, runId, run?.status, onlyFailures]);

  if (!run) {
    return (
      <AppShell>
        <Spinner label="Loading run…" />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Link href={`/projects/${id}`} className="text-sm text-[var(--muted)] hover:underline">
              ← Dashboard
            </Link>
          </div>
          <h1 className="mt-1 flex items-center gap-2 text-xl font-semibold">
            Run #{run.id} {run.name} <StatusBadge status={run.status} />
          </h1>
        </div>
        <Link href={`/projects/${id}/compare?a=${run.id}`}>
          <Button variant="outline">Compare this run</Button>
        </Link>
      </div>

      {run.status === "failed" && (
        <Card className="mb-6 border-[var(--danger)]">
          <p className="text-sm text-[var(--danger)]">Run failed: {run.error}</p>
        </Card>
      )}

      {(run.status === "queued" || run.status === "running") && (
        <Card className="mb-6">
          <Spinner label={`Evaluation ${run.status}… this view refreshes automatically.`} />
        </Card>
      )}

      {/* Config snapshot */}
      <Card className="mb-6">
        <h3 className="mb-3 text-sm font-medium">Configuration snapshot</h3>
        <div className="flex flex-wrap gap-2 text-xs">
          {Object.entries(run.config || {}).map(([k, v]) => (
            <span key={k} className="rounded-md bg-[var(--surface-2)] px-2 py-1">
              <span className="text-[var(--muted)]">{k}:</span> {String(v)}
            </span>
          ))}
          {run.git_commit && (
            <span className="rounded-md bg-[var(--surface-2)] px-2 py-1">
              <span className="text-[var(--muted)]">commit:</span> {run.git_commit}
            </span>
          )}
        </div>
      </Card>

      {run.status === "completed" && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4">
            <MetricCard label="Accuracy" value={pct(run.accuracy)} tone="good" />
            <MetricCard label="Avg latency" value={ms(run.avg_latency_ms)} />
            <MetricCard label="Total cost" value={money(run.total_cost_usd)} />
            <MetricCard label="Total tokens" value={run.total_tokens.toLocaleString()} />
            <MetricCard label="Faithfulness" value={pct(run.faithfulness)} tone="good" />
            <MetricCard label="Hallucination" value={pct(run.hallucination_rate)} tone="warn" />
            <MetricCard label="Retrieval precision" value={pct(run.retrieval_precision)} />
            <MetricCard label="Failures" value={run.failures} tone={run.failures ? "bad" : "default"} />
          </div>

          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-medium">Per-example results</h3>
            <label className="flex items-center gap-2 text-xs text-[var(--muted)]">
              <input
                type="checkbox"
                checked={onlyFailures}
                onChange={(e) => setOnlyFailures(e.target.checked)}
                className="accent-[var(--primary)]"
              />
              Only show incorrect / failed
            </label>
          </div>

          {results === null ? (
            <Spinner label="Loading results…" />
          ) : (
            <Card className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-xs uppercase tracking-wide text-[var(--muted)]">
                    <tr className="border-b border-[var(--border)]">
                      <th className="px-4 py-2.5">Question</th>
                      <th className="px-4 py-2.5">Verdict</th>
                      <th className="px-4 py-2.5">Conf.</th>
                      <th className="px-4 py-2.5">Latency</th>
                      <th className="px-4 py-2.5">Tokens</th>
                      <th className="px-4 py-2.5">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r) => (
                      <Fragment key={r.id}>
                        <tr
                          onClick={() => setExpanded(expanded === r.id ? null : r.id)}
                          className="cursor-pointer border-b border-[var(--border)] last:border-0 hover:bg-[var(--surface-2)]"
                        >
                          <td className="max-w-md truncate px-4 py-3">{r.question}</td>
                          <td className="px-4 py-3">
                            {r.error ? (
                              <Badge tone="danger">error</Badge>
                            ) : r.is_correct ? (
                              <Badge tone="success">correct</Badge>
                            ) : r.is_hallucination ? (
                              <Badge tone="danger">hallucination</Badge>
                            ) : (
                              <Badge tone="warning">incorrect</Badge>
                            )}
                          </td>
                          <td className="px-4 py-3 tabular-nums">{pct(r.judge_confidence)}</td>
                          <td className="px-4 py-3 tabular-nums">{ms(r.latency_ms)}</td>
                          <td className="px-4 py-3 tabular-nums">{r.tokens}</td>
                          <td className="px-4 py-3 tabular-nums">{money(r.cost_usd)}</td>
                        </tr>
                        {expanded === r.id && (
                          <tr className="border-b border-[var(--border)] bg-[var(--surface-2)]">
                            <td colSpan={6} className="px-4 py-4">
                              <div className="grid gap-4 md:grid-cols-2">
                                <Field label="Question" value={r.question} />
                                <Field label="Ground truth" value={r.ground_truth || "—"} />
                                <Field label="Model answer" value={r.answer || "—"} />
                                <Field label="Judge reasoning" value={r.judge_reasoning || "—"} />
                                {r.retrieved_docs?.length > 0 && (
                                  <Field label="Retrieved documents" value={r.retrieved_docs.join(", ")} />
                                )}
                                {r.error && <Field label="Error" value={r.error} />}
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}
    </AppShell>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="whitespace-pre-wrap text-sm">{value}</p>
    </div>
  );
}
