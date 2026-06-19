"use client";

import Link from "next/link";

const sections = ["账户信息", "通知偏好", "隐私与安全", "语言与地区", "数据管理", "设备管理"];

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
          <div><div className="font-semibold text-medical-text-primary">MediNexus</div><div className="text-xs text-medical-text-muted">AI助手在线</div></div>
        </div>
        <nav className="px-3 py-2 flex-1">
          {[{ h: "/dashboard", l: "控制台" }, { h: "/consultation", l: "AI 问诊" }, { h: "/records", l: "健康记录" }, { h: "/profile", l: "个人中心" }, { h: "/settings", l: "设置" }].map(n => (
            <Link key={n.h} href={n.h}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm mb-1 transition-all ${n.h === "/settings" ? "bg-medical-primary text-white font-medium shadow-medical-sm" : "text-medical-text-secondary hover:bg-white/60"}`}>{n.l}</Link>
          ))}
        </nav>
        <div className="p-3 border-t border-medical-border">
          <Link href="/consultation" className="w-full bg-medical-primary text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-medical-primary-hover transition-all shadow-medical-primary">开始新分析</Link>
        </div>
      </aside>
      <div className="flex-1 overflow-y-auto">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50">
          <div className="flex items-center gap-3"><div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" /><span className="text-sm font-medium text-medical-primary">设置</span></div>
        </header>
        <div className="p-8 max-w-4xl mx-auto">
          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">设置</h1>
          <p className="text-medical-text-secondary mb-6">管理您的账户信息、通知偏好、隐私安全及系统配置。</p>
          <div className="bg-white rounded-2xl p-6 shadow-medical-sm border border-medical-border mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-medical-primary to-purple-500 flex items-center justify-center text-white text-xl font-semibold shadow-medical-sm">DS</div>
              <div className="flex-1">
                <div className="text-lg font-semibold text-medical-text-primary">Demo User</div>
                <div className="text-sm text-medical-text-secondary">demo@medinexus.local</div>
              </div>
              <button className="px-4 py-2 bg-medical-primary text-white rounded-xl text-sm font-medium hover:bg-medical-primary-hover transition-colors">编辑资料</button>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {sections.map(s => (
              <div key={s} className="bg-white rounded-2xl p-5 shadow-medical-sm border border-medical-border hover:shadow-medical-md hover:border-medical-primary/30 transition-all group cursor-pointer">
                <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center mb-3">
                  <svg className="w-5 h-5 text-medical-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06A1.65 1.65 0 0015 19.4a1.65 1.65 0 00-1 .6 1.65 1.65 0 00-.33 1.82V22a2 2 0 01-4 0v-.09A1.65 1.65 0 009 20.6a1.65 1.65 0 00-1-.6 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.6 15a1.65 1.65 0 00-.6-1 1.65 1.65 0 00-1.82-.33H2a2 2 0 010-4h.09A1.65 1.65 0 003.4 9a1.65 1.65 0 00.6-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.6a1.65 1.65 0 001-.6 1.65 1.65 0 00.33-1.82V2a2 2 0 014 0v.09A1.65 1.65 0 0015 3.4a1.65 1.65 0 001 .6 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9c.24.36.45.73.6 1.15H22a2 2 0 010 4h-.09A1.65 1.65 0 0019.4 15z"/></svg>
                </div>
                <h3 className="font-semibold text-medical-text-primary mb-1">{s}</h3>
                <p className="text-xs text-medical-text-muted">管理 {s} 相关配置</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
