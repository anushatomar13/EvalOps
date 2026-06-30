export interface User {
  id: number;
  email: string;
  full_name: string;
  is_admin: boolean;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  task_type: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: number;
  project_id: number;
  version: number;
  content: string;
  notes: string;
  created_at: string;
}

export interface Dataset {
  id: number;
  project_id: number;
  name: string;
  version: number;
  description: string;
  row_count: number;
  created_at: string;
}

export interface DatasetItem {
  id: number;
  question: string;
  ground_truth: string;
  context: string;
}

export interface RunConfig {
  model: string;
  temperature: number;
  embedding: string;
  retriever: string;
  chunk_size: number;
  top_k: number;
}

export interface Run {
  id: number;
  project_id: number;
  dataset_id: number;
  prompt_version_id: number | null;
  name: string;
  status: "queued" | "running" | "completed" | "failed";
  error: string;
  config: RunConfig;
  git_commit: string;
  accuracy: number;
  faithfulness: number;
  hallucination_rate: number;
  toxicity_rate: number;
  retrieval_precision: number;
  avg_latency_ms: number;
  total_tokens: number;
  total_cost_usd: number;
  failures: number;
  created_at: string;
}

export interface RunResult {
  id: number;
  question: string;
  ground_truth: string;
  answer: string;
  is_correct: boolean;
  judge_confidence: number;
  judge_reasoning: string;
  faithfulness: number;
  is_hallucination: boolean;
  toxicity: number;
  latency_ms: number;
  tokens: number;
  cost_usd: number;
  retrieved_docs: string[];
  error: string;
}

export interface MetricDelta {
  metric: string;
  a: number;
  b: number;
  delta: number;
  direction: "up" | "down" | "flat";
}

export interface CompareResult {
  run_a: Run;
  run_b: Run;
  deltas: MetricDelta[];
}
