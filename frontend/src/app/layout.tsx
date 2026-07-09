"use client";

import Link from "next/link";
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <head>
        <title>MediNexus / 医枢 — 智能医疗诊断平台</title>
        <meta name="description" content="开源多智能体医疗诊断平台" />
      </head>
      <body className="min-h-screen bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  );
}
