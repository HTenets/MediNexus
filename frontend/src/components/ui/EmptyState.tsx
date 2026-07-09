"use client";

import { motion } from "framer-motion";
import { FileText } from "lucide-react";
import { Button } from "./Button";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      <motion.div
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="w-24 h-24 rounded-full bg-medical-primary-light flex items-center justify-center mb-6"
      >
        <FileText className="w-12 h-12 text-medical-primary" />
      </motion.div>
      <h3 className="font-heading text-xl font-bold text-medical-text-primary mb-2">{title}</h3>
      {description && <p className="text-medical-text-secondary mb-6 max-w-md">{description}</p>}
      {action && (
        <Button onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </motion.div>
  );
}
