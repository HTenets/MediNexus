"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "primary" | "secondary" | "success" | "warning" | "danger" | "default";
  className?: string;
}

export function Badge({ children, variant = "default", className = "" }: BadgeProps) {
  const variantStyles = {
    primary: "bg-medical-primary-light text-medical-primary",
    secondary: "bg-medical-purple-light text-medical-purple",
    success: "bg-medical-accent-light text-medical-accent",
    warning: "bg-medical-warning-light text-medical-warning",
    danger: "bg-medical-danger-light text-medical-danger",
    default: "bg-gray-100 text-gray-600",
  };

  return (
    <motion.span
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${variantStyles[variant]} ${className}`}
    >
      {children}
    </motion.span>
  );
}
