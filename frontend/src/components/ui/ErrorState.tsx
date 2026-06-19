"use client";

import { IconAlert } from "./icons";

export default function ErrorState({ message = "加载失败", onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
        <IconAlert className="w-6 h-6 text-red-500" />
      </div>
      <p className="text-sm text-[var(--color-muted-foreground)] mb-5">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary-medical text-sm px-5 py-2">
          重新加载
        </button>
      )}
    </div>
  );
}
