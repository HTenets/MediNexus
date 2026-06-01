"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">M</span>
          </div>
          <span className="font-semibold text-gray-800">MediNexus / 医枢</span>
        </div>
        <nav className="flex gap-4 text-sm text-gray-600">
          <a href="#features" className="hover:text-blue-600 transition-colors">功能</a>
          <a href="#about" className="hover:text-blue-600 transition-colors">关于</a>
        </nav>
      </header>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <div className="max-w-2xl">
          <div className="inline-block px-3 py-1 mb-6 text-xs font-medium text-blue-600 bg-blue-100 rounded-full">
            开源 AI 医疗诊断平台 v0.1.0
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-4">
            智能导诊 · 精准诊断
          </h1>
          <p className="text-lg text-gray-600 mb-8 leading-relaxed">
            MediNexus 基于多智能体协作，为您提供从症状分析到就诊建议的智能导诊服务。
            由 AI 驱动的全流程问诊体验。
          </p>
          <Link
            href="/consultation"
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all"
          >
            开始智能问诊
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {/* Feature cards */}
        <div id="features" className="grid md:grid-cols-3 gap-6 mt-16 max-w-4xl w-full px-4">
          {[
            {
              title: "多科室导诊",
              desc: "智能分析症状，精确推荐就诊科室",
              icon: "🏥",
            },
            {
              title: "流式对话",
              desc: "实时流式输出，对话体验流畅自然",
              icon: "💬",
            },
            {
              title: "记忆追踪",
              desc: "跨会话追踪健康档案，复诊无缝衔接",
              icon: "📋",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="text-2xl mb-3">{feature.icon}</div>
              <h3 className="font-semibold text-gray-800 mb-1">{feature.title}</h3>
              <p className="text-sm text-gray-500">{feature.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer id="about" className="text-center py-6 text-xs text-gray-400">
        MediNexus / 医枢 — 开源多智能体医疗诊断平台
      </footer>
    </div>
  );
}
