"use client";
import clsx from "clsx";
import { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={clsx(
        "rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5",
        className
      )}
    >
      {children}
    </div>
  );
}

export function Button({
  children,
  variant = "primary",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "danger" | "outline";
}) {
  const styles = {
    primary: "bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]",
    ghost: "text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--surface-2)]",
    outline:
      "border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--surface-2)]",
    danger: "bg-[var(--danger)] text-white hover:opacity-90",
  };
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
        styles[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

const fieldCls =
  "w-full rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2 text-sm text-[var(--foreground)] outline-none focus:border-[var(--primary)] placeholder:text-[var(--muted)]";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={clsx(fieldCls, props.className)} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={clsx(fieldCls, "font-mono", props.className)} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={clsx(fieldCls, props.className)} />;
}

export function Label({ children }: { children: ReactNode }) {
  return <label className="mb-1.5 block text-xs font-medium text-[var(--muted)]">{children}</label>;
}

export function Badge({
  children,
  tone = "default",
}: {
  children: ReactNode;
  tone?: "default" | "success" | "warning" | "danger" | "info";
}) {
  const tones = {
    default: "bg-[var(--surface-2)] text-[var(--muted)]",
    success: "bg-[var(--success)]/15 text-[var(--success)]",
    warning: "bg-[var(--warning)]/15 text-[var(--warning)]",
    danger: "bg-[var(--danger)]/15 text-[var(--danger)]",
    info: "bg-[var(--accent)]/15 text-[var(--accent)]",
  };
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        tones[tone]
      )}
    >
      {children}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, "default" | "success" | "warning" | "danger" | "info"> = {
    completed: "success",
    running: "info",
    queued: "warning",
    failed: "danger",
  };
  return <Badge tone={map[status] || "default"}>{status}</Badge>;
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-[var(--muted)]">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
      {label}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[var(--border)] p-10 text-center">
      <p className="text-sm font-medium">{title}</p>
      {hint && <p className="mt-1 text-xs text-[var(--muted)]">{hint}</p>}
    </div>
  );
}
