"use client";

import Link from "next/link";

export default function RecordsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-gray-800">就诊记录</h1>
          <span className="text-xs text-gray-400">Medical Records</span>
        </div>
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
          返回首页
        </Link>
      </header>
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="text-center py-16">
          <div className="text-4xl mb-4">📋</div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">暂无就诊记录</h2>
          <p className="text-gray-500 mb-6">完成问诊后，您的就诊记录将显示在这里。</p>
          <Link
            href="/consultation"
            className="inline-block px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors text-sm"
          >
            开始问诊
          </Link>
        </div>
      </main>
    </div>
  );
}
