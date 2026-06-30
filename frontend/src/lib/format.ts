export const pct = (v: number, digits = 1) => `${(v * 100).toFixed(digits)}%`;

export const money = (v: number) =>
  v < 0.01 ? `$${v.toFixed(4)}` : `$${v.toFixed(2)}`;

export const ms = (v: number) =>
  v >= 1000 ? `${(v / 1000).toFixed(2)} s` : `${Math.round(v)} ms`;

export const compact = (v: number) =>
  Intl.NumberFormat("en", { notation: "compact" }).format(v);

export const dateShort = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
