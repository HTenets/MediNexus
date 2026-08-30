"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { searchKnowledge, type KnowledgeItem } from "@/lib/api";

interface SourceItem {
  title: string; source: string; match?: string; weight?: string;
  content: string; journal?: string | null;
}

export default function Page() {
  return <Suspense fallback={<div className="flex justify-center py-16"><div className="flex gap-1.5">{[0,150,300].map(d=><span key={d} className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:`${d}ms`}}/>)}</div></div>}>
    <AnalysisContent />
  </Suspense>;
}

function AnalysisContent() {
  const params = useSearchParams();
  const query = params.get("q") || "cough";
  const [cases, setCases] = useState<SourceItem[]>([]);
  const [theory, setTheory] = useState<SourceItem[]>([]);
  const [papers, setPapers] = useState<SourceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [route, setRoute] = useState<"bm25" | "vector" | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    searchKnowledge(query)
      .then((result) => {
        if (cancelled) return;
        setCases(result.cases || []);
        setTheory(result.theory || []);
        setPapers(result.papers || []);
        setRoute(result.route);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError((err as { message?: string }).message || "知识库检索失败");
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [query]);

  const renderSource = (items: SourceItem[], label: string, color: string, bg: string) => (
    <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border">
      <h3 className={`font-semibold text-lg mb-4 flex items-center gap-2`}>
        <span className={`w-9 h-9 rounded-lg ${bg} flex items-center justify-center`}>
          <svg className={`w-5 h-5 ${color}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
        </span>
        {label}
      </h3>
      {loading ? (
        <div className="flex gap-1.5 py-8 justify-center">{[0,150,300].map(d=><span key={d} className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:`${d}ms`}}/>)}</div>
      ) : error ? (
        <div className="text-sm text-medical-danger py-8 text-center">{error}</div>
      ) : items.length === 0 ? (
        <div className="text-sm text-medical-text-muted py-8 text-center">
          该知识库未检索到与「{query}」相关的内容
        </div>
      ) : (
        items.map((item, i) => (
          <div key={i} className="bg-gray-50 rounded-xl p-4 border border-medical-border mb-3 last:mb-0">
            <div className="font-semibold text-medical-text-primary mb-1">{item.title}</div>
            <div className="text-xs text-medical-text-muted mb-2">
              来源: {item.source}{item.journal ? ` · ${item.journal}` : ""}
            </div>
            <p className="text-sm text-medical-text-secondary leading-relaxed">{item.content}</p>
          </div>
        ))
      )}
    </div>
  );

  return (
    <AppShell stageLabel="多维知识源分析 · 阶段 2/4" activePath="/consultation">
      <div className="p-8">
        <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">多维知识源深度分析</h1>
        <p className="text-medical-text-secondary mb-6">
          MediNexus 正在基于三个专业知识库对「{query}」进行交叉验证
          {route && (
            <span className="ml-2 text-xs text-medical-text-muted">
              （检索路由：{route === "bm25" ? "BM25 全文检索" : "向量检索"}）
            </span>
          )}
        </p>
        <div className="grid grid-cols-3 gap-5">
          {renderSource(cases, "临床案例库", "text-medical-primary", "bg-medical-primary-light")}
          {renderSource(theory, "医学理论库", "text-medical-warning", "bg-medical-warning-light")}
          {renderSource(papers, "前沿论文库", "text-medical-accent", "bg-medical-accent-light")}
        </div>
      </div>
    </AppShell>
  );
}
