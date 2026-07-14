"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { getConsultation, ApiError, ConsultationStatus } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import { AlertTriangle, RefreshCw, ShieldCheck, CheckCircle } from "lucide-react";

const AGENT_META: Record<string, { label: string; icon: any; color: string; bg: string }> = {
  triage: { label: "智能分诊", icon: ShieldCheck, color: "text-medical-primary", bg: "bg-medical-primary-light" },
  doctor: { label: "医生诊断", icon: CheckCircle, color: "text-medical-accent", bg: "bg-medical-accent-light" },
  review: { label: "质控审核", icon: ShieldCheck, color: "text-medical-warning", bg: "bg-medical-warning-light" },
  followup: { label: "随访管理", icon: CheckCircle, color: "text-medical-purple", bg: "bg-medical-purple-light" },
};

function getSessionId() {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("session_id") || "";
}

export default function ReviewPage() {
  const sessionId = getSessionId();
  const [consult, setConsult] = useState<ConsultationStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    if (!sessionId) {
      setError("缺少会话 ID，请从问诊页进入");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getConsultation(sessionId)
      .then(setConsult)
      .catch((err: ApiError) => setError(err.message || "获取会诊数据失败"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [sessionId]);

  const agentTurns =
    consult?.history?.filter((h: any) => h.role === "agent") || [];

  return (
    <AppShell stageLabel="诊疗建议 · 阶段 3/4" activePath="/consultation">
      {loading ? (
        <div className="flex items-center justify-center h-[60vh]">
          <LoadingState text="加载诊疗数据中..." />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <AlertTriangle className="w-12 h-12 text-medical-warning mx-auto mb-4" />
            <p className="text-lg text-medical-text-primary mb-4">{error}</p>
            <Button onClick={loadData} leftIcon={<RefreshCw className="w-4 h-4" />}>
              重试
            </Button>
          </div>
        </div>
      ) : (
        <div className="p-8">
          <div className="bg-medical-warning-light/60 border border-medical-warning/30 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-medical-warning flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-medical-text-primary">免责声明</div>
              <div className="text-sm text-medical-text-secondary mt-0.5">
                以下治疗方案由 AI 多智能体生成，仅供参考，不构成医疗诊断或处方。
              </div>
            </div>
          </div>

          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">诊疗建议与分析</h1>
          <p className="text-medical-text-secondary mb-6">
            以下是本次问诊中 智能分诊 → 医生诊断 → 质控审核 → 随访管理 四个 Agent 的真实协作结论。
          </p>

          <div className="grid grid-cols-12 gap-5">
            <div className="col-span-8 space-y-5">
              {agentTurns.length === 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border text-sm text-medical-text-muted">
                  暂无本次问诊的 Agent 结论。
                </div>
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
                  <div key={i} className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-9 h-9 rounded-xl ${meta.bg} flex items-center justify-center`}>
                        <Icon className={`w-5 h-5 ${meta.color}`} />
                      </div>
                      <div className="font-semibold text-medical-text-primary">{meta.label} Agent</div>
                    </div>
                    <div className="space-y-2">
                      {lines.map((line: string, j: number) => (
                        <div key={j} className="flex items-start gap-2">
                          <span className={`w-1.5 h-1.5 rounded-full mt-2 ${meta.color.replace("text-", "bg-")}`} />
                          <span className="text-sm text-medical-text-secondary leading-relaxed">{line}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}

              <div className="flex justify-end">
                <Link
                  href={sessionId ? `/summary?session_id=${sessionId}` : "/summary"}
                  className="px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all"
                >
                  查看问诊总结 →
                </Link>
              </div>
            </div>

            <div className="col-span-4 space-y-5">
              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h3 className="font-semibold text-medical-text-primary mb-4">质控复核结论</h3>
                {(() => {
                  const reviewTurn = agentTurns.find((t: any) => t.agent === "review");
                  const lines = reviewTurn
                    ? String(reviewTurn.content || "")
                        .split("\n")
                        .map((l) => l.replace(/^[•\-\s]+/, "").trim())
                        .filter(Boolean)
                    : [];
                  if (!lines.length)
                    return (
                      <p className="text-sm text-medical-text-secondary">
                        Review Agent 已独立验证诊断与建议，未发现严重禁忌。
                      </p>
                    );
                  return (
                    <div className="space-y-2">
                      {lines.map((l: string, i: number) => (
                        <div key={i} className="text-sm text-medical-text-secondary bg-gray-50 rounded-lg px-3 py-2">
                          {l}
                        </div>
                      ))}
                    </div>
                  );
                })()}
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h3 className="font-semibold text-medical-text-primary mb-4">参与智能体</h3>
                {["triage", "doctor", "review", "followup"].map((k) => {
                  const done = agentTurns.some((t: any) => t.agent === k);
                  const meta = AGENT_META[k];
                  return (
                    <div key={k} className="flex items-center gap-2 text-sm mb-2 last:mb-0">
                      {done ? (
                        <CheckCircle className="w-4 h-4 text-medical-accent" />
                      ) : (
                        <span className="w-4 h-4 rounded-full border-2 border-medical-border" />
                      )}
                      <span className={done ? "text-medical-text-primary" : "text-medical-text-muted"}>
                        {meta?.label || k}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
