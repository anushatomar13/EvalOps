"use client";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui";

const AXIS = "#8a95ad";
const GRID = "#1f2940";

interface SeriesPoint {
  label: string;
  value: number;
}

function ChartFrame({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <Card className="p-4">
      <div className="mb-3">
        <h3 className="text-sm font-medium">{title}</h3>
        {subtitle && <p className="text-xs text-[var(--muted)]">{subtitle}</p>}
      </div>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          {children as React.ReactElement}
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

const tooltipStyle = {
  background: "#161d2e",
  border: "1px solid #1f2940",
  borderRadius: 8,
  fontSize: 12,
  color: "#e6ebf5",
};

export function TrendChart({
  title,
  subtitle,
  data,
  color = "#6366f1",
  percent = false,
}: {
  title: string;
  subtitle?: string;
  data: SeriesPoint[];
  color?: string;
  percent?: boolean;
}) {
  return (
    <ChartFrame title={title} subtitle={subtitle}>
      <AreaChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="label" tick={{ fill: AXIS, fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis
          tick={{ fill: AXIS, fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => (percent ? `${Math.round(v * 100)}%` : `${v}`)}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: number) => (percent ? `${(v * 100).toFixed(1)}%` : v)}
        />
        <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2} fill={`url(#grad-${title})`} />
      </AreaChart>
    </ChartFrame>
  );
}

export function MultiLineChart({
  title,
  subtitle,
  data,
  lines,
}: {
  title: string;
  subtitle?: string;
  data: Record<string, number | string>[];
  lines: { key: string; color: string; name: string }[];
}) {
  return (
    <ChartFrame title={title} subtitle={subtitle}>
      <LineChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="label" tick={{ fill: AXIS, fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: AXIS, fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} />
        {lines.map((l) => (
          <Line key={l.key} type="monotone" dataKey={l.key} name={l.name} stroke={l.color} strokeWidth={2} dot={false} />
        ))}
      </LineChart>
    </ChartFrame>
  );
}

export function CategoryBarChart({
  title,
  subtitle,
  data,
  color = "#38bdf8",
}: {
  title: string;
  subtitle?: string;
  data: SeriesPoint[];
  color?: string;
}) {
  return (
    <ChartFrame title={title} subtitle={subtitle}>
      <BarChart data={data} margin={{ top: 5, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID} vertical={false} />
        <XAxis dataKey="label" tick={{ fill: AXIS, fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: AXIS, fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "#ffffff08" }} />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={color} />
          ))}
        </Bar>
      </BarChart>
    </ChartFrame>
  );
}
