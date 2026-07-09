"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { User, Bot, Stethoscope, Pill, MessageCircle } from "lucide-react";

interface ChatMessageProps {
  role: "user" | "agent" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

const agentConfig: Record<string, { label: string; icon: typeof Stethoscope; color: string; bg: string; gradient: string }> = {
  triage: {
    label: "导诊护士",
    icon: MessageCircle,
    color: "text-blue-600",
    bg: "bg-blue-50",
    gradient: "from-blue-500 to-blue-600",
  },
  doctor: {
    label: "主治医生",
    icon: Stethoscope,
    color: "text-green-600",
    bg: "bg-green-50",
    gradient: "from-green-500 to-green-600",
  },
  review: {
    label: "审方药师",
    icon: Pill,
    color: "text-purple-600",
    bg: "bg-purple-50",
    gradient: "from-purple-500 to-purple-600",
  },
  followup: {
    label: "随访助手",
    icon: MessageCircle,
    color: "text-orange-600",
    bg: "bg-orange-50",
    gradient: "from-orange-500 to-orange-600",
  },
};

export default function ChatMessage({ role, content, agent, streaming }: ChatMessageProps) {
  const isUser = role === "user";
  const isSystem = role === "system";

  const [displayedContent, setDisplayedContent] = useState(streaming ? "" : content);

  useEffect(() => {
    if (!streaming || !content) {
      setDisplayedContent(content);
      return;
    }

    setDisplayedContent("");
    let i = 0;
    const interval = setInterval(() => {
      i += 3;
      setDisplayedContent(content.slice(0, i));
      if (i >= content.length) clearInterval(interval);
    }, 30);

    return () => clearInterval(interval);
  }, [content, streaming]);

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex justify-center my-6"
      >
        <span className="px-6 py-2.5 text-xs text-medical-text-muted bg-medical-primary-light/50 rounded-full border border-medical-primary/20 shadow-sm">
          {content}
        </span>
      </motion.div>
    );
  }

  const config = agent ? agentConfig[agent] : null;
  const AgentIcon = config?.icon || Bot;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, type: "spring", stiffness: 300 }}
      className={`flex gap-3 mb-5 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${
          isUser
            ? "gradient-primary text-white shadow-medical-primary"
            : config?.bg || "bg-gray-100"
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <AgentIcon className={`w-5 h-5 ${isUser ? "text-white" : config?.color || "text-gray-600"}`} />
        )}
      </motion.div>

      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"}`}>
        {!isUser && agent && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className={`flex items-center gap-2 text-xs font-semibold mb-1.5 ${config?.color || "text-gray-600"}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full bg-current`} />
            {config?.label || agent}
          </motion.div>
        )}

        <motion.div
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
          className={`rounded-2xl px-5 py-4 relative ${
            isUser
              ? "gradient-primary text-white rounded-br-sm shadow-medical-primary"
              : "glass-card rounded-bl-sm"
          }`}
        >
          {!isUser && (
            <div className="absolute -top-1 -left-1 w-2 h-2 bg-white rounded-full border-2 border-medical-border" />
          )}
          {isUser && (
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-white rounded-full border-2 border-medical-primary" />
          )}
          
          <div
            className={`text-sm leading-relaxed whitespace-pre-wrap ${
              isUser ? "text-white" : "text-medical-text-primary"
            }`}
          >
            {displayedContent}
            {streaming && displayedContent.length < (content?.length || 0) && (
              <motion.span
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1, repeat: Infinity }}
                className={`inline-block w-2 h-4 ml-0.5 ${isUser ? "bg-white/80" : "bg-medical-primary"}`}
              />
            )}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
