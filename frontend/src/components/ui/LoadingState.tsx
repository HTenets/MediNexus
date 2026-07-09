"use client";

import { motion } from "framer-motion";

interface LoadingStateProps {
  text?: string;
  size?: "sm" | "md" | "lg";
}

export function LoadingState({ text = "加载中...", size = "md" }: LoadingStateProps) {
  const sizeStyles = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        className={`${sizeStyles[size]} border-4 border-medical-primary/20 border-t-medical-primary rounded-full`}
      />
      {text && <p className="text-sm text-medical-text-muted">{text}</p>}
    </div>
  );
}

interface LoadingDotsProps {
  count?: number;
  size?: "sm" | "md";
}

export function LoadingDots({ count = 3, size = "md" }: LoadingDotsProps) {
  const sizeStyles = {
    sm: "w-2 h-2",
    md: "w-3 h-3",
  };

  return (
    <div className="flex gap-2">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className={`${sizeStyles[size]} bg-medical-primary rounded-full`}
          animate={{
            y: [0, -8, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}
    </div>
  );
}
