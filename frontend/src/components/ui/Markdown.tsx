"use client";

import React from "react";

/**
 * Lightweight Markdown renderer (no external deps).
 * Supports: **bold**, *italic*, `code`, headings (#), bullet lines (-, *, •),
 * and preserves line breaks. Designed for short agent/LLM outputs.
 */

const INLINE_RE = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;

export function InlineMarkdown({ text }: { text: string }): React.ReactElement {
  const parts = text.split(INLINE_RE).filter((p) => p !== "");
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={i} className="font-semibold">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <code
              key={i}
              className="px-1 py-0.5 rounded bg-black/5 text-[0.85em] font-mono"
            >
              {part.slice(1, -1)}
            </code>
          );
        }
        if (part.startsWith("*") && part.endsWith("*")) {
          return (
            <em key={i} className="italic">
              {part.slice(1, -1)}
            </em>
          );
        }
        return <React.Fragment key={i}>{part}</React.Fragment>;
      })}
    </>
  );
}

export default function Markdown({
  content,
  className = "",
}: {
  content: string;
  className?: string;
}): React.ReactElement {
  const lines = String(content || "").split("\n");

  return (
    <div className={`space-y-1 ${className}`}>
      {lines.map((raw, i) => {
        const line = raw.trimEnd();
        if (!line.trim()) return <div key={i} className="h-2" />;

        const heading = line.match(/^(#{1,4})\s+(.*)$/);
        if (heading) {
          return (
            <div key={i} className="font-semibold text-[1.02em] mt-1">
              <InlineMarkdown text={heading[2]} />
            </div>
          );
        }

        const bullet = line.match(/^(\s*)(?:[-*•]\s+)+(.*)$/);
        if (bullet) {
          const indent = bullet[1].length >= 2 || /^\s*[·]/.test(bullet[2]);
          return (
            <div
              key={i}
              className={`flex items-start gap-2 ${indent ? "pl-4" : ""}`}
            >
              <span className="mt-2 w-1.5 h-1.5 rounded-full bg-current opacity-50 flex-shrink-0" />
              <span className="flex-1">
                <InlineMarkdown text={bullet[2]} />
              </span>
            </div>
          );
        }

        return (
          <div key={i}>
            <InlineMarkdown text={line} />
          </div>
        );
      })}
    </div>
  );
}
