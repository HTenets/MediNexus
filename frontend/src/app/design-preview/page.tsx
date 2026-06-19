"use client";

import Link from "next/link";

const pages = [
  { href: "/profile", title: "个人健康中心", desc: "健康档案、AI记忆、数字孪生预览、设备集成", color: "bg-medical-primary-light" },
  { href: "/records", title: "健康记录", desc: "AI档案摘要、医疗时间线、影像查看器", color: "bg-medical-accent-light" },
  { href: "/dashboard", title: "数字孪生全景", desc: "3D人体模型、实时体征、风险图谱、AI研判", color: "bg-purple-100" },
  { href: "/consultation/review", title: "方案合规复核", desc: "治疗方案验证、禁忌症警报、指南基准测试", color: "bg-medical-warning-light" },
  { href: "/consultation/analysis", title: "多维知识源分析", desc: "临床案例、医学伦理、前沿论文交叉验证", color: "bg-blue-100" },
  { href: "/consultation", title: "分诊与接诊", desc: "导诊护士Agent、多轮对话、科室推荐", color: "bg-indigo-100" },
  { href: "/summary", title: "问诊总结", desc: "SOAP记录、随访计划、结果导出", color: "bg-green-100" },
  { href: "/upload-report", title: "报告上传", desc: "影像报告、化验单、AI解析", color: "bg-orange-100" },
  { href: "/system-status", title: "系统状态", desc: "服务健康、Agent状态、知识库状态", color: "bg-gray-100" },
  { href: "/login", title: "登录", desc: "角色选择、OAuth登录、账户注册", color: "bg-rose-100" },
  { href: "/settings", title: "设置", desc: "账户信息、通知偏好、隐私安全", color: "bg-teal-100" },
  { href: "/patients", title: "患者管理", desc: "患者列表、搜索、状态筛选", color: "bg-cyan-100" },
];

export default function DesignPreviewPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="font-heading text-4xl font-bold text-medical-text-primary mb-4">MediNexus 设计预览</h1>
          <p className="text-medical-text-secondary">基于设计文档的高保真页面预览</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pages.map(p => (
            <Link key={p.href} href={p.href} className="block bg-white rounded-2xl p-8 shadow-medical-sm hover:shadow-medical-md transition-all duration-200 hover:-translate-y-1 border border-medical-border">
              <div className={`w-14 h-14 ${p.color} rounded-xl flex items-center justify-center mb-6`}>
                <svg className="w-7 h-7 text-medical-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/></svg>
              </div>
              <h2 className="font-heading text-xl font-semibold text-medical-text-primary mb-2">{p.title}</h2>
              <p className="text-medical-text-secondary text-sm mb-4">{p.desc}</p>
              <span className="inline-flex items-center text-medical-primary text-sm font-medium">查看预览 →</span>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
