"use client";

import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import { LayoutDashboard, Brain, FileText, Users, Settings, Heart, Stethoscope, Upload, Activity, LogIn, User } from "lucide-react";

const pages = [
  { href: "/profile", title: "个人健康中心", desc: "健康档案、AI记忆、数字孪生预览、设备集成", icon: User, color: "bg-medical-primary-light" },
  { href: "/records", title: "健康记录", desc: "AI档案摘要、医疗时间线、影像查看器", icon: FileText, color: "bg-medical-accent-light" },
  { href: "/dashboard", title: "数字孪生全景", desc: "3D人体模型、实时体征、风险图谱、AI研判", icon: LayoutDashboard, color: "bg-medical-purple-light" },
  { href: "/consultation", title: "分诊与接诊", desc: "导诊护士Agent、多轮对话、科室推荐", icon: Brain, color: "bg-blue-100" },
  { href: "/summary", title: "问诊总结", desc: "SOAP记录、随访计划、结果导出", icon: Heart, color: "bg-green-100" },
  { href: "/upload-report", title: "报告上传", desc: "影像报告、化验单、AI解析", icon: Upload, color: "bg-orange-100" },
  { href: "/system-status", title: "系统状态", desc: "服务健康、Agent状态、知识库状态", icon: Activity, color: "bg-gray-100" },
  { href: "/login", title: "登录", desc: "角色选择、OAuth登录、账户注册", icon: LogIn, color: "bg-rose-100" },
  { href: "/settings", title: "设置", desc: "账户信息、通知偏好、隐私安全", icon: Settings, color: "bg-teal-100" },
  { href: "/patients", title: "患者管理", desc: "患者列表、搜索、状态筛选", icon: Users, color: "bg-cyan-100" },
];

export default function DesignPreviewPage() {
  return (
    <AppShell stageLabel="设计预览">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-medical-primary-light text-medical-primary text-sm font-medium mb-4">
            <Stethoscope className="w-4 h-4" />
            高保真设计预览
          </div>
          <h1 className="font-heading text-4xl font-bold text-medical-text-primary mb-4">MediNexus 设计预览</h1>
          <p className="text-medical-text-secondary">基于设计文档的高保真页面预览，点击卡片跳转至对应页面</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pages.map((page) => (
            <Link
              key={page.href}
              href={page.href}
              className="block glass-card rounded-2xl p-6 hover:shadow-medical-md transition-all duration-300 hover:-translate-y-1 group"
            >
              <div className={`w-14 h-14 ${page.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                <page.icon className="w-7 h-7 text-medical-primary" />
              </div>
              <h2 className="font-heading text-xl font-semibold text-medical-text-primary mb-2">{page.title}</h2>
              <p className="text-medical-text-secondary text-sm mb-4">{page.desc}</p>
              <span className="inline-flex items-center text-medical-primary text-sm font-medium group-hover:gap-2 transition-all">
                查看预览
                <span className="opacity-0 group-hover:opacity-100 transition-opacity">→</span>
              </span>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
