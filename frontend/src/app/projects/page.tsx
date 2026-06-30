"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";
import { Project } from "@/lib/types";
import { Badge, Button, Card, EmptyState, Input, Label, Select, Spinner, Textarea } from "@/components/ui";
import { dateShort } from "@/lib/format";

const TASK_TYPES = [
  { value: "rag", label: "RAG / Q&A" },
  { value: "chat", label: "Chat assistant" },
  { value: "sql", label: "Text-to-SQL" },
  { value: "coding", label: "Code generation" },
];

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [taskType, setTaskType] = useState("rag");
  const [saving, setSaving] = useState(false);

  function load() {
    api<Project[]>("/projects").then(setProjects);
  }
  useEffect(load, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api<Project>("/projects", {
        method: "POST",
        body: { name, description, task_type: taskType },
      });
      setName("");
      setDescription("");
      setShowForm(false);
      load();
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Projects</h1>
          <p className="text-sm text-[var(--muted)]">
            Each project tracks an AI system you want to evaluate continuously.
          </p>
        </div>
        <Button onClick={() => setShowForm((s) => !s)}>+ New project</Button>
      </div>

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={create} className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Project name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Loan Assistant" required />
            </div>
            <div>
              <Label>Task type</Label>
              <Select value={taskType} onChange={(e) => setTaskType(e.target.value)}>
                {TASK_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="md:col-span-2">
              <Label>Description</Label>
              <Textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What does this AI system do?"
              />
            </div>
            <div className="md:col-span-2">
              <Button type="submit" disabled={saving}>
                {saving ? "Creating…" : "Create project"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {projects === null ? (
        <Spinner label="Loading projects…" />
      ) : projects.length === 0 ? (
        <EmptyState title="No projects yet" hint="Create your first project to start evaluating." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card className="h-full transition-colors hover:border-[var(--primary)]">
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="font-medium">{p.name}</h3>
                  <Badge tone="info">{p.task_type}</Badge>
                </div>
                <p className="line-clamp-2 text-sm text-[var(--muted)]">
                  {p.description || "No description"}
                </p>
                <p className="mt-4 text-xs text-[var(--muted)]">Created {dateShort(p.created_at)}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </AppShell>
  );
}
