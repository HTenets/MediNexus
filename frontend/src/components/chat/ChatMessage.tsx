"use client";

import { useEffect, useState } from "react";

interface ChatMessageProps {
  role: "user" | "agent" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

const agentLabels: Record<string, string> = {
  triage: "导诊护士",
  doctor: "医生",
  review: "审方药师",
  followup: "随访助手",
};

const agentColors: Record<string, string> = {
  triage: "bg-blue-50 border-blue-200",
  doctor: "bg-green-50 border-green-200",
  review: "bg-purple-50 border-purple-200",
  followup: "bg-orange-50 border-orange-200",
};

const agentTextColors: Record<string, string> = {
  triage: "text-blue-700",
  doctor: "text-green-700",
  review: "text-purple-700",
  followup: "text-orange-700",
};

export default function ChatMessage({ role, content, agent, streaming }: ChatMessageProps) {
  const isUser = role === "user";
  const isSystem = role === "system";

  // Simulate streaming effect
  const [displayedContent, setDisplayedContent] = useState(streaming ? "" : content);

  useEffect(() => {
    if (!streaming || !content) {
      setDisplayedContent(content);
      return;
    }

    setDisplayedContent("");
    let i = 0;
    const interval = setInterval(() => {
      i += 3; // add 3 chars at a time for smooth effect
      setDisplayedContent(content.slice(0, i));
      if (i >= content.length) clearInterval(interval);
    }, 30);

    return () => clearInterval(interval);
  }, [content, streaming]);

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <span className="px-3 py-1 text-xs text-gray-500 bg-gray-100 rounded-full">
          {content}
        </span>
      </div>
    );
  }

  const borderColor = isUser ? "bg-gray-100 border-gray-200" : (agentColors[agent || ""] || "bg-white border-gray-200");

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 border ${borderColor} ${
          isUser ? "rounded-br-sm" : "rounded-bl-sm"
        }`}
      >
        {!isUser && agent && (
          <div className={`text-xs font-semibold mb-1 ${agentTextColors[agent] || "text-gray-600"}`}>
            {agentLabels[agent] || agent}
          </div>
        )}
        <div className="text-sm leading-relaxed text-gray-800 whitespace-pre-wrap">
          {displayedContent}
          {streaming && displayedContent.length < (content?.length || 0) && (
            <span className="inline-block w-1.5 h-4 ml-0.5 bg-gray-400 animate-pulse" />
          )}
        </div>
      </div>
    </div>
  );
}
