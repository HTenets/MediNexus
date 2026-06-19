"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";

interface DashboardData {
  vitals: Record<string, string>; bio_age: string;
  risks: string[]; ai_suggestions: string[]; devices: string[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetch("/api/mock/dashboard/patient_demo_001").then(r => r.json()).then(setData).catch(() => {});
  }, []);

  return (
    <AppShell stageLabel="控制台" activePath="/dashboard">
      <div className="p-8 w-full">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary">数字孪生全景视图</h1>
            <span className="bg-medical-accent-light text-medical-accent text-xs font-medium px-3 py-1 rounded-full flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-medical-accent rounded-full animate-pulse" /> 实时同步
            </span>
          </div>
          <p className="text-medical-text-secondary">实时健康状态监测与预测分析</p>
        </div>

        <div className="grid grid-cols-12 gap-5">
          <div className="col-span-3 space-y-4">
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <div className="text-5xl font-bold text-medical-primary mb-2">{data?.bio_age || "--"}<span className="text-lg text-medical-text-muted font-normal ml-1">岁</span></div>
              <div className="text-medical-accent text-sm font-medium">生物学年龄</div>
            </div>
            <div className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
              <h3 className="font-semibold text-medical-text-primary mb-3">核心体征</h3>
              <div className="space-y-3">
                {Object.entries(data?.vitals || { "心率": "--", "血压": "--", "血氧": "--" }).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1 border-b border-gray-100 last:border-0">
                    <span className="text-sm text-medical-text-secondary">{k}</span>
                    <span className="font-semibold text-medical-primary">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-6">
            <div className="bg-white rounded-2xl overflow-hidden shadow-medical-sm border border-medical-border relative">
              <div className="aspect-[3/4] bg-gradient-to-b from-gray-100 to-gray-200 flex items-center justify-center">
                <div className="text-center text-medical-text-muted">
                  <svg className="w-16 h-16 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  <p className="text-sm">3D 数字孪生模型</p>
                </div>
              </div>
            </div>
          </div>

          <div className="col-span-3 space-y-4">
            {[
              ["今日风险", data?.risks || ["暂无风险数据"]],
              ["AI 建议", data?.ai_suggestions || ["暂无建议"]],
              ["设备同步", data?.devices || ["暂无设备信息"]],
            ].map(([title, items]: any) => (
              <div key={title} className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border">
                <h3 className="font-semibold text-medical-text-primary mb-3">{title}</h3>
                <div className="space-y-2">
                  {items.map((i: string) => <div key={i} className="text-sm text-medical-text-secondary bg-gray-50 rounded-lg px-3 py-2">{i}</div>)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
