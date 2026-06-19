"use client";

import Link from "next/link";
import { IconClipboard } from "./icons";

export default function EmptyState({
  title, description, actionLabel, actionHref,
}: {
  icon?: string; title: string; description: string;
  actionLabel?: string; actionHref?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 rounded-2xl bg-[var(--color-muted)] flex items-center justify-center mb-5">
        <IconClipboard className="w-7 h-7 text-[var(--color-muted-foreground)]" />
      </div>
      <h3 className="text-lg font-semibold text-[var(--color-foreground)] mb-1.5" style={{ fontFamily: 'var(--font-heading)' }}>
        {title}
      </h3>
      <p className="text-sm text-[var(--color-muted-foreground)] mb-6 max-w-xs leading-relaxed">{description}</p>
      {actionLabel && actionHref && (
        <Link href={actionHref} className="btn-primary-medical inline-flex">
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
