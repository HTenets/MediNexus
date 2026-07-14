"use client";

import { useState, useEffect, useCallback } from "react";
import AppShell from "@/components/layout/AppShell";
import ChatContainer from "@/components/chat/ChatContainer";
import { createConsultationSocket, ConsultationSocket } from "@/lib/websocket";
import { startConsultation, ApiError, ConsultationStartResponse } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import { CheckCircle, AlertTriangle, Stethoscope, ClipboardList, ShieldCheck, CalendarClock } from "lucide-react";
import Link from "next/link";

const STAGES: { key: string; label: string; icon: any; sub: string }[] = [
  { key: "triage", label: "智能分诊", icon: Stethoscope, sub: "症状评估与科室分诊" },
  { key: "doctor", label: "医生诊断", icon: ClipboardList, sub: "多轮问诊与鉴别诊断" },
  { key: "review", label: "质控审核", icon: ShieldCheck, sub: "用药与禁忌合规复核" },
  { key: "followup", label: "随访管理", icon: CalendarClock, sub: "康复计划与用药提醒" },
];

const DEPARTMENT_LABELS: Record<string, string> = {
  internal_medicine: "内科",
  dermatology: "皮肤科",
  ent: "耳鼻喉科",
  mental_health: "心理科",
  orthopedics: "骨科",
  emergency: "急诊",
  general: "全科",
};

const URGENCY_LABELS: Record<string, { label: string; cls: string }> = {
  routine: { label: "常规", cls: "text-medical-accent bg-medical-accent/10" },
  urgent: { label: "加急", cls: "text-medical-warning bg-medical-warning/10" },
  emergency: { label: "紧急", cls: "text-medical-danger bg-medical-danger/10" },
};

const quickSymptoms = [
  "头痛", "头晕", "恶心", "发热", "咳嗽", "咽痛", "胸痛", "呼吸困难", "腹痛", "腹泻", "皮疹", "失眠",
];

export default function ConsultationPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [socket, setSocket] = useState<ConsultationSocket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeStage, setActiveStage] = useState<string | null>(null);
  const [triageResult, setTriageResult] = useState<{ urgency: string; department: string; reason: string } | null>(null);
  const [pendingQuestions, setPendingQuestions] = useState<string[]>([]);
  const [completed, setCompleted] = useState(false);

  const handleStage = useCallback((agent: string) => setActiveStage(agent), []);

  const handleResult = useCallback((agent: string, manifest: any) => {
    if (agent === "followup") setCompleted(true);
    if (agent === "triage" && manifest?.context?.triage_result) {
      const tr = manifest.context.triage_result;
      setTriageResult({
        urgency: tr.urgency || "routine",
        department: tr.department || "general",
        reason: tr.reason || "",
      });
    }
    if (Array.isArray(manifest?.pending_questions)) {
      setPendingQuestions((prev) => {
        const merged = [...prev, ...manifest.pending_questions];
        return Array.from(new Set(merged)).slice(0, 6);
      });
    }
  }, []);

  useEffect(() => {
    startConsultation()
      .then((response: ConsultationStartResponse) => {
        setSessionId(response.session_id);
        setError(null);
      })
      .catch((err: ApiError) => {
        setError(err.message || "创建会话失败");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    const s = createConsultationSocket(sessionId);
    setSocket(s);
    return () => {
      s.disconnect();
    };
  }, [sessionId]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    startConsultation()
      .then((response: ConsultationStartResponse) => {
        setSessionId(response.session_id);
      })
      .catch((err: ApiError) => {
        setError(err.message || "创建会话失败");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const stageIndex = (k: string) => STAGES.findIndex((s) => s.key === k);
  const activeIdx = activeStage ? stageIndex(activeStage) : -1;
  const urgency = triageResult ? URGENCY_LABELS[triageResult.urgency] || URGENCY_LABELS.routine : null;
  const deptLabel = triageResult ? DEPARTMENT_LABELS[triageResult.department] || triageResult.department : null;

  if (loading) {
    return (
      <AppShell stageLabel="医枢多智能体问诊">
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingState text="创建会话中..." />
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell stageLabel="医枢多智能体问诊">
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-medical-warning mx-auto mb-4" />
            <p className="text-lg text-medical-text-primary mb-4">{error}</p>
            <button
              onClick={handleRetry}
              className="px-6 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium hover:shadow-glow transition-all"
            >
              重试
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell stageLabel="医枢多智能体问诊">
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
          请描述您的症状，系统将依次由 智能分诊 → 医生诊断 → 质控审核 → 随访管理 四个 AI Agent 协作完成问诊。
        </p>

        {completed && (
          <div className="bg-medical-accent-light/60 border border-medical-accent/30 rounded-xl p-4 mb-5 flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2 text-sm text-medical-text-primary">
              <CheckCircle className="w-5 h-5 text-medical-accent" />
              多智能体问诊已完成，可查看质控复核与总结报告。
            </div>
            <div className="flex gap-2">
              <Link
                href={`/consultation/review?session_id=${sessionId}`}
                className="px-4 py-2 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:bg-white/60 transition-colors"
              >
                质控复核 →
              </Link>
              <Link
                href={`/summary?session_id=${sessionId}`}
                className="px-4 py-2 gradient-primary text-white rounded-xl text-sm font-medium hover:shadow-glow transition-all"
              >
                问诊总结 →
              </Link>
            </div>
          </div>
        )}

        <div className="grid grid-cols-12 gap-5" style={{ minHeight: "calc(100vh - 280px)" }}>
          <div className="col-span-8">
            <div className="bg-white rounded-2xl shadow-medical-sm border border-medical-border flex flex-col h-full">
              <ChatContainer
                sessionId={sessionId!}
                socket={socket}
                quickSymptoms={quickSymptoms}
                onStage={handleStage}
                onResult={handleResult}
              />
            </div>
          </div>

          <div className="col-span-4 space-y-5">
            {/* Pipeline stepper */}
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="text-sm font-semibold text-medical-text-primary mb-4">多智能体流水线</div>
              <div className="space-y-1">
                {STAGES.map((stage, idx) => {
                  const done = activeIdx > idx;
                  const active = activeIdx === idx;
                  const Icon = stage.icon;
                  return (
                    <div key={stage.key} className="flex items-center gap-3 py-2">
                      <div
                        className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all ${
                          active
                            ? "bg-medical-primary text-white shadow-glow"
                            : done
                            ? "bg-medical-accent/15 text-medical-accent"
                            : "bg-gray-100 text-medical-text-muted"
                        }`}
                      >
                        {done ? <CheckCircle className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                      </div>
                      <div className="flex-1">
                        <div className={`text-sm font-medium ${active || done ? "text-medical-text-primary" : "text-medical-text-muted"}`}>
                          {stage.label}
                        </div>
                        <div className="text-xs text-medical-text-muted">{stage.sub}</div>
                      </div>
                      {active && (
                        <span className="text-xs text-medical-primary flex items-center gap-1">
                          <span className="w-1.5 h-1.5 bg-medical-primary rounded-full animate-pulse" /> 进行中
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Triage result */}
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="flex items-center gap-2 mb-4">
                <Stethoscope className="w-5 h-5 text-medical-primary" />
                <span className="text-sm font-semibold text-medical-text-primary">分诊结论</span>
              </div>
              {triageResult ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-medical-text-muted">推荐科室</span>
                    <span className="text-sm font-semibold text-medical-text-primary">{deptLabel}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-medical-text-muted">紧急程度</span>
                    {urgency && (
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${urgency.cls}`}>
                        {urgency.label}
                      </span>
                    )}
                  </div>
                  {triageResult.reason && (
                    <p className="text-xs text-medical-text-secondary bg-gray-50 rounded-lg p-2.5">{triageResult.reason}</p>
                  )}
                </div>
              ) : (
                <div className="flex items-center gap-2 text-xs text-medical-primary bg-medical-primary-light rounded-lg px-3 py-2">
                  <span className="w-1.5 h-1.5 bg-medical-primary rounded-full animate-pulse" />
                  等待分诊 Agent 分析...
                </div>
              )}
            </div>

            {/* Pending questions */}
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-medical-warning" />
                <span className="text-sm font-semibold text-medical-text-primary">待确认问题</span>
              </div>
              {pendingQuestions.length > 0 ? (
                <div className="space-y-2.5">
                  {pendingQuestions.map((question, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <span className="w-4 h-4 rounded-full border-2 border-medical-warning flex-shrink-0 mt-0.5"></span>
                      <span className="text-sm text-medical-text-secondary">{question}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-medical-text-muted">Agent 会在分析中给出需要补充的信息。</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
