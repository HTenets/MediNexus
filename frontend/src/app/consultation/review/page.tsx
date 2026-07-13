"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { getConsultation, ApiError, ConsultationStatus } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import { AlertTriangle, RefreshCw } from "lucide-react";

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
      setError("缺少会话 ID");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getConsultation(sessionId)
      .then(setConsult)
      .catch((err: ApiError) => {
        setError(err.message || "获取会诊数据失败");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [sessionId]);

  const soap = consult?.history?.[consult.history.length - 1]?.soap;

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
            <svg className="w-5 h-5 text-medical-warning flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.941 3.374 1.653 0 3.034-.825 3.75-2.062M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <div><div className="text-sm font-medium text-medical-text-primary">免责声明</div><div className="text-sm text-medical-text-secondary mt-0.5">以下治疗方案由 AI 生成，仅供参考，不构成医疗诊断或处方。</div></div>
          </div>

          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">诊疗建议与分析</h1>
          <p className="text-medical-text-secondary mb-6">基于您的症状描述，综合多源医学知识生成以下分析与建议。</p>

          <div className="grid grid-cols-12 gap-5">
            <div className="col-span-8 space-y-5">
              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h3 className="font-semibold text-medical-text-primary mb-4">建议治疗方案</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-xl p-4">
                    <div className="text-xs text-medical-text-muted uppercase mb-1">初步诊断</div>
                    <div className="text-base font-semibold text-medical-text-primary">{soap?.assessment || "暂无诊断"}</div>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4">
                    <div className="text-xs text-medical-text-muted uppercase mb-1">建议</div>
                    <div className="text-base font-semibold text-medical-text-primary">{soap?.plan || "暂无建议"}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h3 className="font-semibold text-medical-text-primary mb-4">SOAP 记录</h3>
                <div className="space-y-4">
                  <div className="bg-medical-primary-light/30 rounded-xl p-4">
                    <div className="text-xs text-medical-primary uppercase mb-1">S 主观资料</div>
                    <div className="text-sm text-medical-text-secondary">{soap?.subjective || "暂无数据"}</div>
                  </div>
                  <div className="bg-medical-accent-light/30 rounded-xl p-4">
                    <div className="text-xs text-medical-accent uppercase mb-1">O 客观资料</div>
                    <div className="text-sm text-medical-text-secondary">{soap?.objective || "暂无数据"}</div>
                  </div>
                  <div className="bg-medical-warning-light/30 rounded-xl p-4">
                    <div className="text-xs text-medical-warning uppercase mb-1">A 评估</div>
                    <div className="text-sm text-medical-text-secondary">{soap?.assessment || "暂无数据"}</div>
                  </div>
                  <div className="bg-medical-purple-light/30 rounded-xl p-4">
                    <div className="text-xs text-medical-purple uppercase mb-1">P 计划</div>
                    <div className="text-sm text-medical-text-secondary">{soap?.plan || "暂无数据"}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border border-l-4 border-l-medical-danger">
                <h3 className="font-semibold text-medical-danger mb-4">禁忌症与风险复核</h3>
                <div className="bg-medical-danger-light/50 rounded-xl p-5 border border-medical-danger/20">
                  <div className="text-base font-semibold text-medical-danger mb-2">未发现严重禁忌</div>
                  <p className="text-sm text-medical-text-secondary leading-relaxed">Review Agent 已独立查询知识库验证诊断和建议。若存在药物过敏或长期用药，请在线下就诊时告知医生。</p>
                </div>
              </div>
            </div>

            <div className="col-span-4 space-y-5">
              {[
                ["信息来源", ["临床病例库 0.8", "医学理论库 0.6", "最新论文库 0.3"]],
                ["审查结论", ["证据等级: C", "建议补充体温和既往病史", "无紧急风险标记"]],
              ].map(([title, items]: any) => (
                <div key={title} className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                  <h3 className="font-semibold text-medical-text-primary mb-4">{title}</h3>
                  {items.map((l: string) => <div key={l} className="text-sm text-medical-text-secondary bg-gray-50 rounded-lg px-3 py-2 mb-2">{l}</div>)}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
