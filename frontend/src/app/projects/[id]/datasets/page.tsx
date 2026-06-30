"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import ProjectNav from "@/components/ProjectNav";
import { Badge, Button, Card, EmptyState, Input, Label, Spinner } from "@/components/ui";
import { api, getToken } from "@/lib/api";
import { Dataset, DatasetItem } from "@/lib/types";
import { dateShort } from "@/lib/format";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export default function DatasetsPage() {
  const { id } = useParams<{ id: string }>();
  const [datasets, setDatasets] = useState<Dataset[] | null>(null);
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [viewing, setViewing] = useState<number | null>(null);
  const [items, setItems] = useState<DatasetItem[]>([]);

  function load() {
    api<Dataset[]>(`/projects/${id}/datasets`).then(setDatasets);
  }
  useEffect(load, [id]);

  async function upload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const form = new FormData();
      form.set("name", name);
      form.set("file", file);
      // Multipart upload (handled directly to keep FormData intact).
      const res = await fetch(`${API_BASE}/projects/${id}/datasets`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: form,
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || "Upload failed");
      }
      setName("");
      setFile(null);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  function viewItems(ds: Dataset) {
    if (viewing === ds.id) {
      setViewing(null);
      return;
    }
    setViewing(ds.id);
    api<DatasetItem[]>(`/projects/${id}/datasets/${ds.id}/items?limit=50`).then(setItems);
  }

  return (
    <AppShell>
      <h1 className="mb-1 text-xl font-semibold">Datasets</h1>
      <p className="mb-4 text-sm text-[var(--muted)]">
        Upload evaluation datasets as CSV. Re-uploading the same name creates a new version
        (finance_v1, finance_v2…).
      </p>
      <ProjectNav projectId={id} />

      <Card className="mb-6">
        <form onSubmit={upload} className="grid items-end gap-4 md:grid-cols-3">
          <div>
            <Label>Dataset name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="finance" required />
          </div>
          <div>
            <Label>CSV file</Label>
            <Input
              type="file"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              required
            />
          </div>
          <Button type="submit" disabled={uploading || !file}>
            {uploading ? "Uploading…" : "Upload dataset"}
          </Button>
        </form>
        <p className="mt-3 text-xs text-[var(--muted)]">
          Expected columns: a question column (Question / Prompt / Input) and an answer column
          (Ground Truth / Expected SQL / Unit Tests / Correct Documents). Matching is flexible.
        </p>
        {error && <p className="mt-2 text-sm text-[var(--danger)]">{error}</p>}
      </Card>

      {datasets === null ? (
        <Spinner label="Loading…" />
      ) : datasets.length === 0 ? (
        <EmptyState title="No datasets yet" hint="Upload a CSV to get started." />
      ) : (
        <div className="space-y-3">
          {datasets.map((d) => (
            <Card key={d.id}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="font-medium">{d.name}</span>
                  <Badge tone="info">v{d.version}</Badge>
                  <span className="text-xs text-[var(--muted)]">{d.row_count} rows · {dateShort(d.created_at)}</span>
                </div>
                <Button variant="ghost" onClick={() => viewItems(d)}>
                  {viewing === d.id ? "Hide" : "Preview"}
                </Button>
              </div>
              {viewing === d.id && (
                <div className="mt-3 overflow-x-auto rounded-lg border border-[var(--border)]">
                  <table className="w-full text-sm">
                    <thead className="text-left text-xs uppercase tracking-wide text-[var(--muted)]">
                      <tr className="border-b border-[var(--border)]">
                        <th className="px-3 py-2">Question</th>
                        <th className="px-3 py-2">Ground truth</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((it) => (
                        <tr key={it.id} className="border-b border-[var(--border)] last:border-0">
                          <td className="px-3 py-2">{it.question}</td>
                          <td className="px-3 py-2 text-[var(--muted)]">{it.ground_truth}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}
