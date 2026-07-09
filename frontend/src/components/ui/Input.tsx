"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface InputProps {
  label?: string;
  error?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  className?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
}

export function Input({ label, error, leftIcon, rightIcon, className = "", placeholder, value, onChange, type = "text" }: InputProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-medical-text-primary">
          {label}
        </label>
      )}
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
            {leftIcon}
          </div>
        )}
        <motion.input
          whileFocus={{ scale: 1.01 }}
          className={`w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus ${
            leftIcon ? "pl-11" : ""
          } ${rightIcon ? "pr-11" : ""} ${error ? "border-medical-danger focus:border-medical-danger" : ""} ${className}`}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          type={type}
        />
        {rightIcon && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
            {rightIcon}
          </div>
        )}
      </div>
      {error && <p className="text-xs text-medical-danger">{error}</p>}
    </div>
  );
}

interface TextareaProps {
  label?: string;
  error?: string;
  className?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  disabled?: boolean;
}

export function Textarea({ label, error, className = "", placeholder, value, onChange, disabled }: TextareaProps) {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-medical-text-primary">
          {label}
        </label>
      )}
      <motion.textarea
        whileFocus={{ scale: 1.01 }}
        className={`w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus resize-none ${error ? "border-medical-danger focus:border-medical-danger" : ""} ${className}`}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
      />
      {error && <p className="text-xs text-medical-danger">{error}</p>}
    </div>
  );
}
