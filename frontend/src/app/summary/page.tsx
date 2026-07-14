"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { getConsultation, ApiError, ConsultationStatus } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import { CheckCircle, RefreshCw, AlertTriangle, ArrowLeft } from "lucide-react";

const AGENT_META: Record<string, { label: string; icon: any; color: string; bg: string }> = {
  triage: { label: "智能分诊", icon: CheckCircle, color: "text-medical-primary", bg: "bg-medical-primary-light" },
  doctor: { label: "医生诊断", icon: CheckCircle, color: "text-medical-accent", bg: "bg-medical-accent-light" },
  review: { label: "质控审核", icon: CheckCircle, color: "text-medical-warning", bg: "bg-medical-warning-light" },
  followup: { label: "随访管理", icon: CheckCircle, color: "text-medical-purple", bg: "bg-medical-purple-light" },
};

function getSessionId() {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("session_id") || "";
}

export default function SummaryPage() {
  const sid = getSessionId();
  const [session, setSession] = useState<ConsultationStatus | null>(null);
  const [loading, setLoading] = useState(sid ? true : false);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    if (!sid) {
      setError("缺少会话 ID，请从问诊页进入");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getConsultation(sid)
      .then(setSession)
      .catch((err: ApiError) => setError(err.message || "获取会话数据失败"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [sid]);

  const agentTurns = session?.history?.filter((h: any) => h.role === "agent") || [];
  const followupTurn = agentTurns.find((t: any) => t.agent === "followup");
  const followupLines = followupTurn
    ? String(followupTurn.content || "")
        .split("\n")
        .map((l) => l.replace(/^[•\-\s]+/, "").trim())
        .filter(Boolean)
    : [];

  return (
    <AppShell stageLabel="问诊总结 阶段 4/4">
      {loading ? (
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingState text="加载会话数据中..." />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-medical-warning mx-auto mb-4" />
            <p className="text-lg text-medical-text-primary mb-4">{error}</p>
            <Button onClick={loadData} leftIcon={<RefreshCw className="w-4 h-4" />}>
              刷新重试
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-gradient-to-b from-medical-primary-light to-transparent pt-10 pb-6 px-8">
            <div className="max-w-3xl mx-auto text-center">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-medical-accent-light flex items-center justify-center mb-4">
                <CheckCircle className="w-7 h-7 text-medical-accent" />
              </div>
              <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">问诊已完成</h1>
              <p className="text-sm text-medical-text-muted max-w-[480px] mx-auto mb-6">
                您的健康档案已更新，AI 建议仅供参考，请务必咨询专业医生。
              </p>
              <div className="flex justify-center gap-3">
                <Link
                  href="/records"
                  className="flex items-center gap-2 px-5 py-2.5 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:bg-white/50 transition-colors"
                >
                  查看就诊记录
                </Link>
                <Link
                  href="/consultation"
                  className="flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all"
                >
                  重新问诊
                </Link>
              </div>
            </div>
          </div>

          <div className="max-w-3xl mx-auto p-6 space-y-6">
            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-medical-text-primary mb-4">本次多智能体协作结论</h2>
              <div className="space-y-4">
                {agentTurns.length === 0 && (
                  <p className="text-sm text-medical-text-muted">暂无本次问诊记录。</p>
                )}
                {agentTurns.map((turn: any, i: number) => {
                  const meta = AGENT_META[turn.agent] || {
                    label: turn.agent,
                    icon: CheckCircle,
                    color: "text-medical-primary",
                    bg: "bg-medical-primary-light",
                  };
                  const Icon = meta.icon;
                  const lines = String(turn.content || "")
                    .split("\n")
                    .map((l) => l.replace(/^[•\-\s]+/, "").trim())
                    .filter(Boolean);
                  return (
                    <div key={i} className="bg-white/60 rounded-xl p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-6 h-6 rounded-md ${meta.bg} flex items-center justify-center`}>
                          <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
                        </div>
                        <span className="text-sm font-semibold text-medical-text-primary">{meta.label} Agent</span>
                      </div>
                      <div className="space-y-1">
                        {lines.map((l: string, j: number) => (
                          <div key={j} className="text-sm text-medical-text-secondary leading-relaxed">
                            • {l}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-medical-text-primary mb-4">随访建议</h2>
              <div className="space-y-3">
                {followupLines.length > 0 ? (
                  followupLines.map((item: string, index: number) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-medical-accent-light flex items-center justify-center flex-shrink-0 mt-0.5">
                        <CheckCircle className="w-3 h-3 text-medical-accent" />
                      </div>
                      <span className="text-sm text-medical-text-secondary">{item}</span>
                    </div>
                  ))
                ) : (
                  [
                    "继续观察症状变化，每日记录",
                    "保证充足休息，多喝水",
                    "如症状持续加重，建议线下就医",
                  ].map((item, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-medical-accent-light flex items-center justify-center flex-shrink-0 mt-0.5">
                        <CheckCircle className="w-3 h-3 text-medical-accent" />
                      </div>
                      <span className="text-sm text-medical-text-secondary">{item}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-medical-warning-light/50 rounded-xl p-3 flex gap-2 items-start">
              <AlertTriangle className="w-4 h-4 text-medical-warning flex-shrink-0 mt-0.5" />
              <p className="text-xs text-medical-warning">本结果不构成医疗诊断建议，请咨询专业医生。</p>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
