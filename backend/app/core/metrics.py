"""Prometheus metrics for the EvalForge API.

Exposes HTTP request metrics plus EvalForge-specific counters/gauges so the
platform's own quality signals (run counts, last accuracy) are observable in
Grafana — eating our own dog food on observability.
"""
from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS = Counter(
    "evalforge_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_LATENCY = Histogram(
    "evalforge_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

EVAL_RUNS = Counter(
    "evalforge_eval_runs_total",
    "Evaluation runs by terminal status",
    ["status"],
)

EVAL_RUN_DURATION = Histogram(
    "evalforge_eval_run_duration_seconds",
    "Wall-clock duration of an evaluation run",
)

LAST_ACCURACY = Gauge(
    "evalforge_last_accuracy",
    "Most recent run accuracy per project",
    ["project_id"],
)

LAST_HALLUCINATION_RATE = Gauge(
    "evalforge_last_hallucination_rate",
    "Most recent run hallucination rate per project",
    ["project_id"],
)
