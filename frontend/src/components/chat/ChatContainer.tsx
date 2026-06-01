"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { ConsultationSocket } from "@/lib/websocket";

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
}

export default function ChatContainer({ sessionId, socket }: ChatContainerProps) {
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

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Listen for WebSocket events
  useEffect(() => {
    if (!socket) return;

    socket.setConnectionHandler(setConnected);
    socket.connect();

    const unsubs = [
      socket.on("agent_start", (event) => {
        setIsProcessing(true);
        setMessages((prev) => [
          ...prev,
          {
            id: `agent-${event.data.agent || "unknown"}-${Date.now()}`,
            role: "agent",
            content: "",
            agent: (event.data.agent as string) || undefined,
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
      socket.on("agent_end", () => {
        setIsProcessing(false);
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.streaming) {
            updated[updated.length - 1] = { ...last, streaming: false };
          }
          return updated;
        });
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

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100 bg-white">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              connected ? "bg-green-500" : "bg-red-400"
            }`}
          />
          <span className="text-xs text-gray-500">
            {connected ? "已连接" : "连接中..."}
          </span>
        </div>
        <span className="text-xs text-gray-400">会话: {sessionId.slice(0, 8)}</span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} {...msg} />
        ))}
        {isProcessing && !messages.some((m) => m.streaming) && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={isProcessing} />
    </div>
  );
}
