"use client";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import ProjectNav from "@/components/ProjectNav";
import { Button, Card, EmptyState, Input, Label, Select } from "@/components/ui";
import { api } from "@/lib/api";
import { Dataset, PromptVersion, Run } from "@/lib/types";

const MODELS = ["gpt-4.1", "gpt-4o", "gpt-4o-mini", "claude", "claude-opus", "gemini", "llama", "mistral"];
const RETRIEVERS = ["hybrid", "dense", "sparse"];
const EMBEDDINGS = ["bge-large", "text-embedding-3-large", "e5-base", "gte-large"];

export default function RunPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [datasets, setDatasets] = useState<Dataset[] | null>(null);
  const [prompts, setPrompts] = useState<PromptVersion[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [datasetId, setDatasetId] = useState<number | "">("");
  const [promptVersion, setPromptVersion] = useState<number | "">("");
  const [name, setName] = useState("");
  const [model, setModel] = useState("gpt-4.1");
  const [temperature, setTemperature] = useState(0.2);
  const [embedding, setEmbedding] = useState("bge-large");
  const [retriever, setRetriever] = useState("hybrid");
  const [chunkSize, setChunkSize] = useState(512);
  const [topK, setTopK] = useState(5);
  const [gitCommit, setGitCommit] = useState("");

  useEffect(() => {
    api<Dataset[]>(`/projects/${id}/datasets`).then((d) => {
      setDatasets(d);
      if (d.length) setDatasetId(d[0].id);
    });
    api<PromptVersion[]>(`/projects/${id}/prompts`).then((p) => {
      setPrompts(p);
      if (p.length) setPromptVersion(p[0].version);
    });
  }, [id]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const run = await api<Run>(`/projects/${id}/runs`, {
        method: "POST",
        body: {
          dataset_id: datasetId,
          prompt_version: promptVersion || null,
          name,
          git_commit: gitCommit,
          config: {
            model,
            temperature,
            embedding,
            retriever,
            chunk_size: chunkSize,
            top_k: topK,
          },
        },
      });
      router.push(`/projects/${id}/runs/${run.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start run");
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 text-xl font-semibold">Run evaluation</h1>
      <p className="mb-4 text-sm text-[var(--muted)]">
        Configure the system under test, then launch an async evaluation job over your dataset.
      </p>
      <ProjectNav projectId={id} />

      {datasets !== null && datasets.length === 0 ? (
        <EmptyState
          title="No datasets yet"
          hint="Upload an evaluation dataset on the Datasets tab before running."
        />
      ) : (
        <form onSubmit={submit} className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <h3 className="mb-4 text-sm font-medium">System configuration</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label>Model</Label>
                <Select value={model} onChange={(e) => setModel(e.target.value)}>
                  {MODELS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Temperature: {temperature}</Label>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={temperature}
                  onChange={(e) => setTemperature(+e.target.value)}
                  className="w-full accent-[var(--primary)]"
                />
              </div>
              <div>
                <Label>Embedding model</Label>
                <Select value={embedding} onChange={(e) => setEmbedding(e.target.value)}>
                  {EMBEDDINGS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Retriever</Label>
                <Select value={retriever} onChange={(e) => setRetriever(e.target.value)}>
                  {RETRIEVERS.map((m) => (
                    <option key={m}>{m}</option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Chunk size</Label>
                <Input type="number" value={chunkSize} onChange={(e) => setChunkSize(+e.target.value)} />
              </div>
              <div>
                <Label>Top K</Label>
                <Input type="number" value={topK} onChange={(e) => setTopK(+e.target.value)} />
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="mb-4 text-sm font-medium">Inputs</h3>
            <div className="space-y-4">
              <div>
                <Label>Dataset</Label>
                <Select value={datasetId} onChange={(e) => setDatasetId(+e.target.value)}>
                  {datasets?.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} v{d.version} ({d.row_count} rows)
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Prompt version</Label>
                <Select value={promptVersion} onChange={(e) => setPromptVersion(+e.target.value)}>
                  <option value="">None</option>
                  {prompts.map((p) => (
                    <option key={p.id} value={p.version}>
                      v{p.version}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Run name (optional)</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="baseline" />
              </div>
              <div>
                <Label>Git commit (optional)</Label>
                <Input value={gitCommit} onChange={(e) => setGitCommit(e.target.value)} placeholder="abc123" />
              </div>
              {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
              <Button type="submit" className="w-full" disabled={submitting || !datasetId}>
                {submitting ? "Launching…" : "▶ Run evaluation"}
              </Button>
              <Link href={`/projects/${id}`} className="block text-center text-xs text-[var(--muted)] hover:underline">
                Cancel
              </Link>
            </div>
          </Card>
        </form>
      )}
    </AppShell>
  );
}
