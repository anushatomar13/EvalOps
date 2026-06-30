"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import ProjectNav from "@/components/ProjectNav";
import { Badge, Button, Card, EmptyState, Input, Label, Spinner, Textarea } from "@/components/ui";
import { api } from "@/lib/api";
import { PromptVersion } from "@/lib/types";
import { dateShort } from "@/lib/format";

export default function PromptsPage() {
  const { id } = useParams<{ id: string }>();
  const [prompts, setPrompts] = useState<PromptVersion[] | null>(null);
  const [content, setContent] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  function load() {
    api<PromptVersion[]>(`/projects/${id}/prompts`).then(setPrompts);
  }
  useEffect(load, [id]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api(`/projects/${id}/prompts`, { method: "POST", body: { content, notes } });
      setContent("");
      setNotes("");
      load();
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 text-xl font-semibold">Prompt versions</h1>
      <p className="mb-4 text-sm text-[var(--muted)]">
        Every prompt is stored immutably and versioned, so you can diff and roll back.
      </p>
      <ProjectNav projectId={id} />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <h3 className="mb-3 text-sm font-medium">New version</h3>
          <form onSubmit={save} className="space-y-3">
            <div>
              <Label>System / instruction prompt</Label>
              <Textarea rows={8} value={content} onChange={(e) => setContent(e.target.value)} required placeholder="You are a helpful loan assistant…" />
            </div>
            <div>
              <Label>Notes (what changed?)</Label>
              <Input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Added refusal guardrails" />
            </div>
            <Button type="submit" disabled={saving} className="w-full">
              {saving ? "Saving…" : "Save new version"}
            </Button>
          </form>
        </Card>

        <div className="lg:col-span-2 space-y-3">
          {prompts === null ? (
            <Spinner label="Loading…" />
          ) : prompts.length === 0 ? (
            <EmptyState title="No prompt versions yet" hint="Save your first version to start tracking." />
          ) : (
            prompts.map((p) => (
              <Card key={p.id}>
                <div className="mb-2 flex items-center justify-between">
                  <Badge tone="info">v{p.version}</Badge>
                  <span className="text-xs text-[var(--muted)]">{dateShort(p.created_at)}</span>
                </div>
                <pre className="whitespace-pre-wrap rounded-lg bg-[var(--surface-2)] p-3 font-mono text-xs">
                  {p.content}
                </pre>
                {p.notes && <p className="mt-2 text-xs text-[var(--muted)]">📝 {p.notes}</p>}
              </Card>
            ))
          )}
        </div>
      </div>
    </AppShell>
  );
}
