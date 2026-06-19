"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import { IconDashboard, IconBrain, IconFile, IconUser, IconBell, IconHeart } from "@/components/medical/Icons";

const navItems = [
  { href: "/dashboard", label: "控制台", Icon: IconDashboard },
  { href: "/consultation", label: "AI 问诊", Icon: IconBrain },
  { href: "/records", label: "健康记录", Icon: IconFile },
  { href: "/profile", label: "个人中心", Icon: IconUser },
];

interface AppShellProps {
  children: ReactNode;
  stageLabel?: string;
  activePath?: string;
}

export default function AppShell({ children, stageLabel = "AI助手在线", activePath }: AppShellProps) {
  const pathname = usePathname();
  const current = activePath || pathname;

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside className="w-60 bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0">
        <div className="p-5 flex items-center gap-3">
          <div className="w-8 h-8 bg-medical-primary rounded-lg flex items-center justify-center text-white font-bold text-sm">M</div>
          <div>
            <Link href="/" className="font-semibold text-medical-text-primary">MediNexus</Link>
            <div className="text-xs text-medical-text-muted">AI助手在线</div>
          </div>
        </div>

        <nav className="px-3 py-2 flex-1">
          {navItems.map(({ href, label, Icon }) => {
            const active = current === href || (href === "/consultation" && current.startsWith("/consultation"));
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm mb-1 transition-all ${
                  active
                    ? "bg-medical-primary text-white font-medium shadow-medical-sm"
                    : "text-medical-text-secondary hover:bg-white/60"
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-medical-border">
          <Link href="/consultation" className="w-full bg-medical-primary text-white py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 hover:bg-medical-primary-hover transition-all shadow-medical-primary">
            <IconHeart className="w-5 h-5" />
            开始新分析
          </Link>
        </div>
      </aside>

      <div className="flex-1 overflow-hidden flex flex-col">
        <header className="h-16 bg-medical-bg/80 backdrop-blur-md border-b border-medical-border flex items-center justify-between px-6 sticky top-0 z-50 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-medical-primary rounded-full animate-pulse" />
            <span className="text-sm font-medium text-medical-primary">{stageLabel}</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full flex items-center justify-center text-medical-text-secondary hover:bg-medical-sidebar cursor-pointer relative">
              <IconBell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-medical-danger rounded-full" />
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-medical-primary to-purple-500 flex items-center justify-center text-white text-xs font-semibold border-2 border-white shadow-medical-sm">DS</div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
