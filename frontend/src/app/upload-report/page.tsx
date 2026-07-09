"use client";

import { useState } from "react";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { Upload, ArrowLeft, FileText, FileImage, File } from "lucide-react";

export default function UploadReportPage() {
  const [dragging, setDragging] = useState(false);

  return (
    <AppShell stageLabel="报告上传">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-2 text-sm text-medical-text-muted hover:text-medical-primary transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" />
          <Link href="/records">返回健康记录</Link>
        </div>

        <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">上传新报告</h1>
        <p className="text-medical-text-secondary mb-6">上传检验报告、影像资料或处方单，AI 将自动解析并归档。</p>

        <div
          className={`glass-card rounded-2xl p-8 border-2 border-dashed transition-all cursor-pointer ${
            dragging ? "border-medical-primary bg-medical-primary-light/30" : "border-medical-border hover:border-medical-primary"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
          }}
        >
          <div className="text-center py-10">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-medical-primary-light flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-medical-primary" />
            </div>
            <div className="text-lg font-semibold text-medical-text-primary mb-2">拖放文件到此处，或点击上传</div>
            <p className="text-sm text-medical-text-muted mb-4">支持 PDF、JPG、PNG、DICOM 格式，单个文件不超过 50MB</p>
            <button className="gradient-primary text-white rounded-xl px-6 py-3 text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all">
              选择文件
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {[
            { icon: FileText, label: "检验报告", desc: "血常规、生化等", color: "bg-medical-primary-light" },
            { icon: FileImage, label: "影像资料", desc: "X光、CT、MRI", color: "bg-medical-accent-light" },
            { icon: File, label: "处方单", desc: "医生处方、用药记录", color: "bg-medical-purple-light" },
          ].map((item) => (
            <div key={item.label} className="glass-card rounded-2xl p-4 text-center hover:shadow-medical-sm transition-all">
              <div className={`w-12 h-12 mx-auto rounded-xl ${item.color} flex items-center justify-center mb-3`}>
                <item.icon className="w-6 h-6 text-medical-primary" />
              </div>
              <div className="font-medium text-medical-text-primary text-sm mb-1">{item.label}</div>
              <div className="text-xs text-medical-text-muted">{item.desc}</div>
            </div>
          ))}
        </div>

        <div className="glass-card rounded-2xl p-4 mt-6">
          <h3 className="font-semibold text-medical-text-primary text-sm mb-3">上传历史</h3>
          <div className="text-center py-8">
            <FileText className="w-8 h-8 text-medical-text-muted mx-auto mb-2" />
            <p className="text-sm text-medical-text-muted">暂无上传记录</p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
