"use client";

import { useState, useEffect, useMemo } from "react";
import ChatContainer from "@/components/chat/ChatContainer";
import { createConsultationSocket, ConsultationSocket } from "@/lib/websocket";

function generateId(): string {
  return "xxxx-xxxx-xxxx".replace(/x/g, () =>
    Math.floor(Math.random() * 16).toString(16)
  );
}

export default function ConsultationPage() {
  const [sessionId] = useState(() => generateId());
  const [socket, setSocket] = useState<ConsultationSocket | null>(null);

  useEffect(() => {
    const s = createConsultationSocket(sessionId);
    setSocket(s);
    return () => {
      s.disconnect();
    };
  }, [sessionId]);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-gray-800">医枢 MediNexus</h1>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">智能问诊</span>
        </div>
        <a
          href="/"
          className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
        >
          返回首页
        </a>
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-hidden">
        <ChatContainer sessionId={sessionId} socket={socket} />
      </main>
    </div>
  );
}
