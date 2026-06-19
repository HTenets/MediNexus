"use client";

export default function LoadingState({ message = "加载中..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="flex gap-2 mb-4">
        {[0, 200, 400].map(delay => (
          <span
            key={delay}
            className="w-2.5 h-2.5 rounded-full bg-[var(--color-primary)]/30 animate-bounce"
            style={{ animationDelay: `${delay}ms`, animationDuration: "1s" }}
          />
        ))}
      </div>
      <p className="text-sm text-[var(--color-muted-foreground)]">{message}</p>
    </div>
  );
}
