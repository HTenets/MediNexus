"use client";

import { useState, useEffect } from "react";
import AppShell from "@/components/layout/AppShell";
import ChatContainer from "@/components/chat/ChatContainer";
import { createConsultationSocket, ConsultationSocket } from "@/lib/websocket";
import { User, CheckCircle, AlertTriangle, Stethoscope } from "lucide-react";

function generateId(): string {
  return "xxxx-xxxx-xxxx".replace(/x/g, () =>
    Math.floor(Math.random() * 16).toString(16)
  );
}

const confirmedSymptoms = [
  "头痛持续 2 天，双侧胀痛",
  "低热 37.8°C",
  "既往偏头痛病史",
  "轻微咽痛，无流鼻涕",
];

const pendingQuestions = [
  "是否有畏寒、全身酸痛？",
  "头痛是否随咳嗽或低头加重？",
];

const quickSymptoms = [
  "头痛", "头晕", "恶心", "发热", "咳嗽", "咽痛", "胸痛", "呼吸困难", "腹痛", "腹泻"
];

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
    <AppShell stageLabel="导诊护士 Agent 阶段 1/4">
      <div className="h-full">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center">
            <Stethoscope className="w-5 h-5 text-medical-primary" />
          </div>
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary">分诊与接诊</h1>
          </div>
        </div>
        <p className="text-medical-text-secondary mb-6">
          请与 AI 导诊护士对话，详细描述您的症状。症状描述越详细，分诊结果越准确。
        </p>

        <div className="grid grid-cols-12 gap-5" style={{ minHeight: "calc(100vh - 280px)" }}>
          <div className="col-span-8">
            <div className="bg-white rounded-2xl shadow-medical-sm border border-medical-border flex flex-col h-full">
              <ChatContainer sessionId={sessionId} socket={socket} quickSymptoms={quickSymptoms} />
            </div>
          </div>

          <div className="col-span-4 space-y-5">
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-medical-primary-light flex items-center justify-center">
                  <Stethoscope className="w-5 h-5 text-medical-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-medical-text-primary">导诊护士 Agent</div>
                  <div className="text-xs text-medical-text-muted">正在多轮确认症状</div>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-medical-primary bg-medical-primary-light rounded-lg px-3 py-2">
                <span className="w-1.5 h-1.5 bg-medical-primary rounded-full animate-pulse" />
                等待患者回复...
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="w-5 h-5 text-medical-accent" />
                <span className="text-sm font-semibold text-medical-text-primary">已确认症状</span>
              </div>
              <div className="space-y-2.5">
                {confirmedSymptoms.map((symptom, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-medical-accent flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-medical-text-secondary">{symptom}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-medical-warning" />
                <span className="text-sm font-semibold text-medical-text-primary">待确认问题</span>
              </div>
              <div className="space-y-2.5">
                {pendingQuestions.map((question, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="w-4 h-4 rounded-full border-2 border-medical-warning flex-shrink-0 mt-0.5"></span>
                    <span className="text-sm text-medical-text-secondary">{question}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="text-sm font-semibold text-medical-text-primary mb-3">患者信息</div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-medical-text-muted">姓名</span>
                  <span className="text-medical-text-secondary">张三</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-medical-text-muted">年龄</span>
                  <span className="text-medical-text-secondary">34 岁</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-medical-text-muted">性别</span>
                  <span className="text-medical-text-secondary">男</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
