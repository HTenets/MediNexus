"use client";

import { motion } from "framer-motion";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = "加载失败，请重试", onRetry }: ErrorStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center gap-6 py-16"
    >
      <motion.div
        animate={{ rotate: [0, -5, 5, -5, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="w-20 h-20 rounded-full bg-medical-danger-light flex items-center justify-center"
      >
        <AlertTriangle className="w-10 h-10 text-medical-danger" />
      </motion.div>
      <div className="text-center">
        <h3 className="font-heading text-xl font-bold text-medical-text-primary mb-2">出错了</h3>
        <p className="text-medical-text-secondary">{message}</p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />}>
          重试
        </Button>
      )}
    </motion.div>
  );
}
