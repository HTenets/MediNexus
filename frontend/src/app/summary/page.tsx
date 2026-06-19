"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getConsultation } from "@/lib/api";

function getSessionId() {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("session_id") || "";
}

export default function SummaryPage() {
  const sid = getSessionId();
  const [session, setSession] = useState<{ session_id: string; status: string; current_agent: string; history: any[] } | null>(null);
  const [loading, setLoading] = useState(sid ? true : false);

  useEffect(() => {
    if (sid) {
      getConsultation(sid).then(setSession).catch(() => setLoading(false)).finally(() => setLoading(false));
    }
  }, [sid]);

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
          <div><div className="font-semibold text-medical-text-primary">MediNexus</div><div className="text-xs text-medical-text-muted">AI助手在线</div></div>
        </div>
        <nav className="px-3 py-2 flex-1">
          {["/dashboard","控制台",'/consultation',"AI 问诊",'/records',"健康记录",'/profile',"个人中心"].map((v,i)=>
            i%2===0 ? null : <a key={v} href={v} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-medical-text-secondary hover:bg-white/60 transition-all text-sm mb-1">{v}</a>
          )}
        </nav>
        <div className="p-3 border-t border-medical-border">
          <a href="/consultation" className="w-full bg-medical-primary text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-medical-primary-hover transition-all shadow-medical-primary">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
            开始新分析
          </a>
        </div>
      </aside>

      <div className="flex-1 overflow-y-auto">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50">
          <div className="flex items-center gap-3"><div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" /><span className="text-sm font-medium text-medical-primary">问诊总结 阶段 4/4</span></div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-medical-primary to-purple-500 flex items-center justify-center text-white text-xs font-semibold border-2 border-white shadow-medical-sm">DS</div>
          </div>
        </header>

        {loading ? (
          <div className="flex items-center justify-center h-64"><div className="flex gap-1.5">{[0,150,300].map(d=><span key={d} className="w-2 h-2 bg-medical-primary/40 rounded-full animate-bounce" style={{animationDelay:`${d}ms`}}/>)}</div></div>
        ) : (
          <>
            <div className="bg-gradient-to-b from-medical-primary-light to-transparent pt-10 pb-6 px-8">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto rounded-xl bg-medical-accent-light flex items-center justify-center mb-3">
                  <svg className="w-6 h-6 text-medical-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
                <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">问诊已完成</h1>
                <p className="text-sm text-medical-text-muted max-w-[480px] mx-auto">您的健康档案已更新，AI 建议仅供参考，请务必咨询专业医生。</p>
                <div className="flex justify-center gap-3 mt-6">
                  <Link href="/records" className="border border-medical-border rounded-xl px-4 py-2.5 text-sm text-medical-text-secondary flex items-center gap-2 hover:bg-white transition-colors">查看就诊记录</Link>
                  <Link href="/consultation" className="bg-medical-primary text-white rounded-xl px-4 py-2.5 text-sm flex items-center gap-2 hover:bg-medical-primary-hover transition-colors">重新问诊</Link>
                </div>
              </div>
            </div>

            <div className="p-8 space-y-6">
              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h2 className="text-lg font-semibold text-medical-text-primary mb-4">会话详情</h2>
                <div className="grid grid-cols-4 gap-4">
                  {[["会话 ID", sid || session?.session_id || "—"],["完成时间", new Date().toLocaleString()],["参与 Agent","导诊 / 诊断 / 审方 / 随访"],["证据等级","B 级 (医学共识)"]].map(([k,v])=>(
                    <div key={k}><div className="text-xs text-medical-text-muted mb-1">{k}</div><div className="text-sm text-medical-text-primary">{v}</div></div>
                  ))}
                </div>
                <div className="mt-4 bg-medical-warning-light/50 rounded-lg p-3 flex gap-2">
                  <svg className="w-4 h-4 text-medical-warning flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.941 3.374 1.653 0 3.034-.825 3.75-2.062M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  <p className="text-xs text-medical-warning">本结果不构成医疗诊断建议，请咨询专业医生。</p>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
                <h2 className="text-lg font-semibold text-medical-text-primary mb-4">SOAP 记录</h2>
                {[
                  ["S 主观资料 (Subjective)","S","bg-medical-primary","患者主诉头痛两天，伴有低热（37.8°C），无恶心呕吐，无颈部僵硬。"],
                  ["O 客观资料 (Objective)","O","bg-medical-accent","体温 37.8°C，暂无线下查体数据。"],
                  ["A 评估 (Assessment)","A","bg-medical-warning","急性上呼吸道感染可能，伴紧张性头痛或偏头痛发作。"],
                  ["P 计划 (Plan)","P","bg-purple-500","对症处理，休息补液；若症状加重或高热持续，建议线下就医。"],
                ].map(([label,letter,color,text]) => (
                  <div key={label} className="mb-4 last:mb-0">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-6 h-6 rounded-md ${color} text-white text-xs font-bold flex items-center justify-center`}>{letter}</div>
                      <span className="text-sm font-semibold">{label}</span>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4 text-sm text-medical-text-secondary leading-relaxed">{text}</div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
