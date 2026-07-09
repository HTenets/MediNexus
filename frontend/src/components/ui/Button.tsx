"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface ButtonProps {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  loading?: boolean;
  className?: string;
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
}

export function Button({
  variant = "primary",
  size = "md",
  children,
  leftIcon,
  rightIcon,
  loading = false,
  className = "",
  disabled = false,
  onClick,
  type = "button",
}: ButtonProps) {
  const baseStyles = "inline-flex items-center justify-center gap-2 font-medium rounded-xl transition-all duration-300 btn-ripple focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

  const variantStyles = {
    primary: "gradient-primary text-white shadow-medical-primary hover:shadow-glow hover:scale-[1.02] active:scale-[0.98] focus:ring-medical-primary",
    secondary: "gradient-accent text-white shadow-medical-accent hover:shadow-glow-accent hover:scale-[1.02] active:scale-[0.98] focus:ring-medical-accent",
    outline: "border-2 border-medical-primary text-medical-primary bg-white hover:bg-medical-primary-light focus:ring-medical-primary",
    ghost: "text-medical-text-secondary hover:text-medical-primary hover:bg-medical-primary-light focus:ring-medical-primary",
    danger: "bg-medical-danger text-white hover:bg-medical-danger-dark focus:ring-medical-danger",
  };

  const sizeStyles = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-sm",
    lg: "px-8 py-4 text-base",
  };

  return (
    <motion.button
      whileHover={!disabled && !loading ? { scale: 1.02 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
      type={type}
    >
      {loading ? (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
        />
      ) : (
        <>
          {leftIcon}
          {children}
          {rightIcon}
        </>
      )}
    </motion.button>
  );
}
