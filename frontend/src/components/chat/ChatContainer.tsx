"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState, useCallback } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { ConsultationSocket } from "@/lib/websocket";
import { Wifi, WifiOff, Clock, RefreshCw } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
  agent?: string;
  streaming?: boolean;
}

interface ChatContainerProps {
  sessionId: string;
  socket: ConsultationSocket | null;
  quickSymptoms?: string[];
  onStage?: (agent: string) => void;
  onResult?: (agent: string, manifest: any) => void;
}

export default function ChatContainer({
  sessionId,
  socket,
  quickSymptoms = [],
  onStage,
  onResult,
}: ChatContainerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "system",
      content: "欢迎使用医枢智能问诊，请描述您的症状。",
    },
  ]);
  const [connected, setConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastAgentRef = useRef<string>("");

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!socket) return;

    socket.setConnectionHandler(setConnected);
    socket.connect();

    const unsubs = [
      socket.on("agent_start", (event) => {
        setIsProcessing(true);
        const agent = (event.data.agent as string) || "unknown";
        lastAgentRef.current = agent;
        onStage?.(agent);
        setMessages((prev) => [
          ...prev,
          {
            id: `agent-${agent}-${Date.now()}`,
            role: "agent",
            content: "",
            agent,
            streaming: true,
          },
        ]);
      }),
      socket.on("token", (event) => {
        const token = event.data.token as string;
        if (!token) return;
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === "agent" && last.streaming) {
            updated[updated.length - 1] = { ...last, content: last.content + token };
          }
          return updated;
        });
      }),
      socket.on("agent_end", (event) => {
        setIsProcessing(false);
        const manifest = (event.data?.manifest as any) || null;
        const agent = (event.data?.agent as string) || lastAgentRef.current;
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.streaming) {
            updated[updated.length - 1] = { ...last, streaming: false };
          }
          return updated;
        });
        if (manifest) onResult?.(agent, manifest);
      }),
      socket.on("error", (event) => {
        setIsProcessing(false);
        const errMsg = (event.data?.message as string) || "系统错误，请重试。";
        setMessages((prev) => [
          ...prev,
          { id: `error-${Date.now()}`, role: "system", content: `错误: ${errMsg}` },
        ]);
      }),
    ];

    return () => unsubs.forEach((u) => u());
  }, [socket]);

  const handleSend = useCallback(
    (content: string) => {
      if (!socket || !content.trim()) return;

      setMessages((prev) => [
        ...prev,
        { id: `user-${Date.now()}`, role: "user", content },
      ]);

      socket.send({ type: "message", content });
    },
    [socket]
  );

  const handleQuickSymptom = (symptom: string) => {
    handleSend(`我有${symptom}症状`);
  };

  return (
    <div className="flex flex-col h-full">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between px-4 py-3 border-b border-medical-border bg-gray-50/50"
      >
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${connected ? "bg-medical-accent" : "bg-medical-danger"} animate-pulse`} />
          <span className="text-xs font-medium text-medical-text-secondary">
            {connected ? "已连接" : "连接中..."}
          </span>
          {connected ? (
            <Wifi className="w-3.5 h-3.5 text-medical-accent" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-medical-danger" />
          )}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-medical-text-muted">
            <Clock className="w-3.5 h-3.5" />
            <span>会话: {sessionId.slice(0, 8)}</span>
          </div>
          <button
            onClick={() => socket?.connect()}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-medical-text-muted hover:text-medical-primary hover:bg-medical-primary-light transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        <AnimatePresence>
          {messages.map((msg) => (
            <ChatMessage key={msg.id} {...msg} />
          ))}
        </AnimatePresence>

        {isProcessing && !messages.some((m) => m.streaming) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex gap-3"
          >
            <div className="w-11 h-11 rounded-xl bg-medical-primary-light flex items-center justify-center flex-shrink-0">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-medical-primary/30 border-t-medical-primary rounded-full"
              />
            </div>
            <div className="bg-white border border-medical-border rounded-2xl rounded-bl-sm p-4 shadow-medical-sm">
              <div className="flex gap-2">
                <motion.span
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  className="w-2 h-2 bg-medical-primary/40 rounded-full"
                />
                <motion.span
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  className="w-2 h-2 bg-medical-primary/40 rounded-full"
                />
                <motion.span
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  className="w-2 h-2 bg-medical-primary/40 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {quickSymptoms.length > 0 && (
        <div className="px-4 py-3 border-t border-medical-border bg-gray-50/50">
          <div className="text-xs text-medical-text-muted mb-2">快速选择症状（点击即可发送）：</div>
          <div className="flex flex-wrap gap-2">
            {quickSymptoms.map((symptom) => (
              <button
                key={symptom}
                onClick={() => handleQuickSymptom(symptom)}
                disabled={isProcessing}
                className="border border-medical-border bg-white rounded-full px-3 py-1 text-sm text-medical-text-secondary cursor-pointer hover:border-medical-primary hover:text-medical-primary hover:bg-medical-primary-light transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {symptom}
              </button>
            ))}
          </div>
        </div>
      )}

      <ChatInput onSend={handleSend} disabled={isProcessing} />
    </div>
  );
}
