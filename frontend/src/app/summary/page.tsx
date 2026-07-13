"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { getConsultation, ApiError, ConsultationStatus } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import { CheckCircle, Clock, User, FileText, AlertTriangle, ArrowLeft, RefreshCw } from "lucide-react";

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
      setError("缺少会话 ID");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getConsultation(sid)
      .then(setSession)
      .catch((err: ApiError) => {
        setError(err.message || "获取会话数据失败");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [sid]);

  const soapData = session?.history?.[session.history.length - 1]?.soap || { subjective: "", objective: "", assessment: "", plan: "" };

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
                  <FileText className="w-4 h-4" />
                  查看就诊记录
                </Link>
                <Link
                  href="/consultation"
                  className="flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all"
                >
                  重新问诊
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadData}
                  leftIcon={<RefreshCw className="w-4 h-4" />}
                >
                  刷新数据
                </Button>
              </div>
            </div>
          </div>

          <div className="max-w-3xl mx-auto p-6 space-y-6">
            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-medical-text-primary mb-4">会话详情</h2>
              <div className="grid grid-cols-4 gap-4">
                {[
                  ["会话 ID", sid || session?.session_id || "—"],
                  ["完成时间", session?.history?.[session.history.length - 1]?.timestamp ? new Date(session.history[session.history.length - 1].timestamp as string).toLocaleString() : new Date().toLocaleString()],
                  ["参与 Agent", session?.current_agent || "导诊 / 诊断 / 审方 / 随访"],
                  ["状态", session?.status || "已完成"],
                ].map(([k, v]) => (
                  <div key={k}>
                    <div className="text-xs text-medical-text-muted mb-1">{k}</div>
                    <div className="text-sm text-medical-text-primary font-medium">{v}</div>
                  </div>
                ))}
              </div>
              <div className="mt-4 bg-medical-warning-light/50 rounded-xl p-3 flex gap-2 items-start">
                <AlertTriangle className="w-4 h-4 text-medical-warning flex-shrink-0 mt-0.5" />
                <p className="text-xs text-medical-warning">本结果不构成医疗诊断建议，请咨询专业医生。</p>
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-medical-text-primary mb-4">SOAP 记录</h2>
              {[
                [
                  "S 主观资料 (Subjective)",
                  "S",
                  "bg-medical-primary",
                  soapData?.subjective || "患者主诉头痛两天，伴有低热（37.8°C），无恶心呕吐，无颈部僵硬。",
                ],
                ["O 客观资料 (Objective)", "O", "bg-medical-accent", soapData?.objective || "体温 37.8°C，暂无线下查体数据。"],
                [
                  "A 评估 (Assessment)",
                  "A",
                  "bg-medical-warning",
                  soapData?.assessment || "急性上呼吸道感染可能，伴紧张性头痛或偏头痛发作。",
                ],
                ["P 计划 (Plan)", "P", "bg-medical-purple", soapData?.plan || "对症处理，休息补液；若症状加重或高热持续，建议线下就医。"],
              ].map(([label, letter, color, text]) => (
                <div key={label} className="mb-4 last:mb-0">
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`w-6 h-6 rounded-md ${color} text-white text-xs font-bold flex items-center justify-center`}>
                      {letter}
                    </div>
                    <span className="text-sm font-semibold text-medical-text-primary">{label}</span>
                  </div>
                  <div className="bg-white/60 rounded-xl p-4 text-sm text-medical-text-secondary leading-relaxed">{text}</div>
                </div>
              ))}
            </div>

            <div className="glass-card rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-medical-text-primary mb-4">随访建议</h2>
              <div className="space-y-3">
                {[
                  "继续观察体温变化，每日记录体温",
                  "保证充足休息，多喝水",
                  "头痛加重时可适当使用非处方止痛药",
                  "如症状持续超过3天或加重，建议线下就医",
                ].map((item, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-medical-accent-light flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3 h-3 text-medical-accent" />
                    </div>
                    <span className="text-sm text-medical-text-secondary">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
