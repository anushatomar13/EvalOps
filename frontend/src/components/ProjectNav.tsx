"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function ProjectNav({ projectId }: { projectId: string }) {
  const pathname = usePathname();
  const base = `/projects/${projectId}`;
  const tabs = [
    { href: base, label: "Dashboard" },
    { href: `${base}/run`, label: "Run evaluation" },
    { href: `${base}/compare`, label: "Compare" },
    { href: `${base}/prompts`, label: "Prompts" },
    { href: `${base}/datasets`, label: "Datasets" },
  ];
  return (
    <nav className="mb-6 flex gap-1 border-b border-[var(--border)] text-sm">
      {tabs.map((t) => {
        const active = pathname === t.href;
        return (
          <Link
            key={t.href}
            href={t.href}
            className={`-mb-px border-b-2 px-4 py-2.5 transition-colors ${
              active
                ? "border-[var(--primary)] text-[var(--foreground)]"
                : "border-transparent text-[var(--muted)] hover:text-[var(--foreground)]"
            }`}
          >
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}
