"use client";

import Link from "next/link";

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-gray-800">个人中心</h1>
          <span className="text-xs text-gray-400">Profile</span>
        </div>
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
          返回首页
        </Link>
      </header>
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-2xl text-blue-600 font-bold">?</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">访客用户</h2>
              <p className="text-sm text-gray-500">登录后可查看完整健康档案</p>
            </div>
          </div>
          <div className="border-t border-gray-100 pt-4">
            <p className="text-sm text-gray-500 text-center">
              个人中心功能正在开发中...
            </p>
          </div>
        </div>
        <Link
          href="/consultation"
          className="block text-center text-sm text-blue-600 hover:text-blue-700"
        >
          开始问诊 →
        </Link>
      </main>
    </div>
  );
}
