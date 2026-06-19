"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Patient { id: string; name: string; last_visit: string; status: string }

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  useEffect(() => { fetch("/api/mock/patients").then(r => r.json()).then(setPatients).catch(() => {}); }, []);

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3"><div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div><div><div className="font-semibold text-medical-text-primary">MediNexus</div><div className="text-xs text-medical-text-muted">AI助手在线</div></div></div>
        <nav className="px-3 py-2 flex-1">
          {[{ href: "/dashboard", label: "控制台" }, { href: "/consultation", label: "AI 问诊" }, { href: "/patients", label: "患者管理" }, { href: "/system-status", label: "系统状态" }].map(n => (
            <Link key={n.href} href={n.href} className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm mb-1 transition-all ${n.href==="/patients"?"bg-medical-primary text-white font-medium shadow-medical-sm":"text-medical-text-secondary hover:bg-white/60"}`}>{n.label}</Link>
          ))}
        </nav>
      </aside>
      <div className="flex-1 overflow-y-auto">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50">
          <div className="flex items-center gap-3"><div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" /><span className="text-sm font-medium text-medical-primary">患者管理</span></div>
        </header>
        <div className="p-8">
          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-6">患者列表</h1>
          <div className="bg-white rounded-2xl shadow-medical-sm border border-medical-border overflow-hidden">
            <table className="w-full text-sm"><thead className="bg-medical-sidebar text-medical-text-secondary"><tr><th className="text-left p-4">患者</th><th className="text-left p-4">最近问诊</th><th className="text-left p-4">状态</th></tr></thead>
              <tbody>{patients.map(p => (
                <tr key={p.id} className="border-t border-medical-border"><td className="p-4 font-medium">{p.name}</td><td className="p-4 text-medical-text-secondary">{p.last_visit}</td><td className="p-4"><span className="bg-medical-accent-light text-medical-accent px-2 py-0.5 rounded-full text-xs">{p.status}</span></td></tr>
              ))}</tbody></table>
          </div>
        </div>
      </div>
    </div>
  );
}
