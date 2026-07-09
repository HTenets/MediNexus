"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  animate?: boolean;
  delay?: number;
}

export function Card({ children, className = "", hover = false, animate = false, delay = 0 }: CardProps) {
  const baseStyles = "glass-card rounded-2xl p-6";
  
  const animationProps = animate ? {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5, delay },
  } : {};

  return (
    <motion.div
      {...animationProps}
      className={`${baseStyles} ${hover ? "card-hover" : ""} ${className}`}
    >
      {children}
    </motion.div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export function CardHeader({ title, subtitle, className = "" }: CardHeaderProps) {
  return (
    <div className={`mb-4 ${className}`}>
      <h3 className="font-heading text-xl font-bold text-medical-text-primary mb-1">{title}</h3>
      {subtitle && <p className="text-sm text-medical-text-secondary">{subtitle}</p>}
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={`${className}`}>{children}</div>;
}
