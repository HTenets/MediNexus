"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Service {
  name: string; status: string; latency: string;
}

export default function SystemStatusPage() {
  const [overall, setOverall] = useState("healthy");
  const [uptime, setUptime] = useState("99.97%");
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/mock/system-status")
      .then(r => r.json())
      .then(d => { setOverall(d.overall); setUptime(d.uptime); setServices(d.services); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
          <div><div className="font-semibold text-medical-text-primary">MediNexus</div><div className="text-xs text-medical-text-muted">AI助手在线</div></div>
        </div>
        <nav className="px-3 py-2 flex-1">
          {[{ h: "/dashboard", l: "控制台" }, { h: "/consultation", l: "AI 问诊" }, { h: "/records", l: "健康记录" }, { h: "/patients", l: "患者管理" }, { h: "/system-status", l: "系统状态" }, { h: "/profile", l: "个人中心" }].map(n => (
            <Link key={n.h} href={n.h}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm mb-1 transition-all ${n.h === "/system-status" ? "bg-medical-primary text-white font-medium shadow-medical-sm" : "text-medical-text-secondary hover:bg-white/60"}`}>{n.l}</Link>
          ))}
        </nav>
        <div className="p-3 border-t border-medical-border">
          <Link href="/consultation" className="w-full bg-medical-primary text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-medical-primary-hover transition-all shadow-medical-primary">开始新分析</Link>
        </div>
      </aside>

      <div className="flex-1 overflow-y-auto">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50">
          <div className="flex items-center gap-3"><div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" /><span className="text-sm font-medium text-medical-primary">系统状态</span></div>
        </header>

        <div className="p-8 w-full">
          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">系统状态</h1>
          <p className="text-medical-text-secondary mb-6">实时监控 MediNexus 各服务组件的运行状态。</p>

          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              ["系统整体状态", overall, "bg-medical-accent"],
              ["运行时间", uptime, "bg-medical-primary"],
              ["服务总数", String(services.length), "bg-medical-warning"],
              ["告警", String(services.filter(s => s.status !== "healthy").length), "bg-medical-danger"],
            ].map(([k, v, c]) => (
              <div key={k} className={`bg-white rounded-2xl p-5 shadow-medical-sm border-l-4 ${c} border-y border-r border-medical-border`}>
                <div className="text-xs text-medical-text-muted mb-1">{k}</div>
                <div className="text-2xl font-bold text-medical-text-primary">{v}</div>
              </div>
            ))}
          </div>

          {loading ? (
            <div className="flex justify-center py-16">{[0,150,300].map(d => <span key={d} className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{animationDelay:`${d}ms`}}/>)}</div>
          ) : (
            <div className="bg-white rounded-2xl shadow-medical-sm border border-medical-border overflow-hidden">
              <table className="w-full text-sm"><thead className="bg-medical-sidebar text-medical-text-secondary"><tr><th className="text-left p-4">服务</th><th className="text-left p-4">状态</th><th className="text-left p-4">延迟</th></tr></thead>
                <tbody>{services.map(s => (
                  <tr key={s.name} className="border-t border-medical-border">
                    <td className="p-4 font-medium text-medical-text-primary">{s.name}</td>
                    <td className="p-4"><span className={`text-xs px-2 py-0.5 rounded-full ${s.status === "healthy" ? "bg-medical-accent-light text-medical-accent" : "bg-medical-warning-light text-medical-warning"}`}>{s.status}</span></td>
                    <td className="p-4 text-medical-text-secondary">{s.latency}</td>
                  </tr>
                ))}</tbody></table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
