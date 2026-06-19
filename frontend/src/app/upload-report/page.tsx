"use client";

import { useState } from "react";
import Link from "next/link";

export default function UploadReportPage() {
  const [dragging, setDragging] = useState(false);

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
          <div><div className="font-semibold text-medical-text-primary">MediNexus</div><div className="text-xs text-medical-text-muted">AI助手在线</div></div>
        </div>
        <nav className="px-3 py-2 flex-1">
          {[{ h: "/dashboard", l: "控制台" }, { h: "/consultation", l: "AI 问诊" }, { h: "/records", l: "健康记录" }, { h: "/profile", l: "个人中心" }].map(n => (
            <Link key={n.h} href={n.h} className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-medical-text-secondary hover:bg-white/60 transition-all text-sm mb-1">{n.l}</Link>
          ))}
        </nav>
        <div className="p-3 border-t border-medical-border">
          <Link href="/consultation" className="w-full bg-medical-primary text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-medical-primary-hover transition-all shadow-medical-primary">开始新分析</Link>
        </div>
      </aside>
      <div className="flex-1 overflow-y-auto">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50">
          <div className="flex items-center gap-3"><div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" /><span className="text-sm font-medium text-medical-primary">报告上传</span></div>
        </header>
        <div className="p-8 w-full">
          <button className="flex items-center gap-2 text-sm text-medical-text-muted hover:text-medical-primary transition-colors mb-4">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M15.75 19.5L8.25 12l7.5-7.5"/></svg>
            返回健康记录
          </button>
          <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">上传新报告</h1>
          <p className="text-medical-text-secondary mb-6">上传检验报告、影像资料或处方单，AI 将自动解析并归档。</p>

          <div className={`bg-white rounded-2xl p-8 shadow-medical-sm border-2 border-dashed transition-colors cursor-pointer mb-6 ${dragging ? "border-medical-primary bg-medical-primary-light" : "border-medical-border hover:border-medical-primary"}`}
            onDragOver={e => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)}
            onDrop={e => { e.preventDefault(); setDragging(false); }}>
            <div className="text-center py-10">
              <div className="w-16 h-16 mx-auto rounded-full bg-medical-primary-light flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-medical-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M9 8.25c0-1.209.668-2.25 1.5-2.25S12 7.041 12 8.25V13.5m0-5.25c0-1.209.668-2.25 1.5-2.25S15 7.041 15 8.25V13.5m0-5.25c0-1.209.668-2.25 1.5-2.25S18 7.041 18 8.25V15c0 2.25-1.5 4.5-4.5 4.5S9 17.25 9 15V8.25z"/></svg>
              </div>
              <div className="text-lg font-semibold text-medical-primary mb-2">拖放文件到此处，或点击上传</div>
              <p className="text-sm text-medical-text-muted mb-4">支持 PDF、JPG、PNG、DICOM 格式，单个文件不超过 50MB</p>
              <button className="bg-medical-primary text-white rounded-xl px-6 py-2.5 text-sm font-medium shadow-medical-primary hover:bg-medical-primary-hover transition-colors">选择文件</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
