"use client";

import { motion } from "framer-motion";
import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Paperclip, Mic } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSend, disabled, placeholder }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }
  }, [input]);

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="border-t border-medical-border glass p-4"
    >
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
        <div className="flex gap-2">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-xl flex items-center justify-center text-medical-text-muted hover:text-medical-primary hover:bg-medical-primary-light transition-all"
          >
            <Paperclip className="w-5 h-5" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 rounded-xl flex items-center justify-center text-medical-text-muted hover:text-medical-primary hover:bg-medical-primary-light transition-all"
          >
            <Mic className="w-5 h-5" />
          </motion.button>
        </div>

        <motion.div
          whileFocus={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
          className="flex-1 relative"
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || "描述您的症状..."}
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-2xl border border-medical-border px-4 py-3.5 text-sm outline-none transition-all input-focus bg-white/80 backdrop-blur-sm disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            size="sm"
            className="h-12 px-6 rounded-2xl"
          >
            <Send className="w-4 h-4" />
          </Button>
        </motion.div>
      </div>
    </motion.div>
  );
}
