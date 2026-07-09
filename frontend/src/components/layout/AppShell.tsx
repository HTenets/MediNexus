"use client";

import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ReactNode, useState } from "react";
import {
  LayoutDashboard,
  Brain,
  FileText,
  Users,
  Settings,
  Bell,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
} from "lucide-react";


const navItems = [
  { href: "/dashboard", label: "控制台", icon: LayoutDashboard },
  { href: "/consultation", label: "AI 问诊", icon: Brain },
  { href: "/records", label: "健康记录", icon: FileText },
  { href: "/patients", label: "患者管理", icon: Users },
  { href: "/profile", label: "个人中心", icon: User },
  { href: "/settings", label: "设置", icon: Settings },
];

interface AppShellProps {
  children: ReactNode;
  stageLabel?: string;
  activePath?: string;
}

export default function AppShell({ children, stageLabel = "AI助手在线", activePath }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [showLogout, setShowLogout] = useState(false);
  const current = activePath || pathname;

  const handleLogout = () => {
    setShowLogout(false);
    router.push("/login");
  };

  return (
    <div className="flex h-screen bg-medical-bg">
      <aside
        className={`bg-medical-sidebar border-r border-medical-border flex flex-col flex-shrink-0 relative transition-all duration-300 ease-in-out ${
          collapsed ? "w-[72px]" : "w-[240px]"
        }`}
      >
        <div className="p-4 flex items-center gap-3">
          <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-medical-primary flex-shrink-0">
            M
          </div>
          {!collapsed && (
            <div className="overflow-hidden flex-1 min-w-0">
              <Link href="/" className="font-semibold text-medical-text-primary block truncate">
                MediNexus
              </Link>
              <div className="text-xs text-medical-text-muted">AI助手在线</div>
            </div>
          )}
        </div>

        <nav className="px-3 py-4 flex-1 flex flex-col gap-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive =
              current === href ||
              (href === "/consultation" && current.startsWith("/consultation"));
            return (
              <Link
                key={href}
                href={href}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm transition-all duration-200 ${
                  isActive
                    ? "gradient-primary text-white font-medium shadow-medical-primary"
                    : "text-medical-text-secondary hover:text-medical-primary hover:bg-white/60"
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span className="whitespace-nowrap">{label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-medical-border">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center py-3 rounded-xl text-medical-text-secondary hover:text-medical-primary hover:bg-white/60 transition-all"
          >
            {collapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>
      </aside>

      <div className="flex-1 overflow-hidden flex flex-col">
        <header className="h-16 glass sticky top-0 z-50 flex-shrink-0 border-b border-medical-border">
          <div className="h-full px-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-medical-accent rounded-full animate-pulse" />
              <span className="text-sm font-medium text-medical-primary">
                {stageLabel}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative">
                <button className="w-10 h-10 rounded-full flex items-center justify-center text-medical-text-secondary hover:text-medical-primary hover:bg-medical-primary-light transition-all">
                  <Bell className="w-5 h-5" />
                </button>
                <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-medical-danger rounded-full border-2 border-white" />
              </div>

              <div className="relative">
                <button
                  onClick={() => setShowLogout(!showLogout)}
                  className="flex items-center gap-3 px-2 py-1.5 rounded-full hover:bg-medical-primary-light transition-all"
                >
                  <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-white text-sm font-semibold shadow-medical-sm border-2 border-white">
                    DS
                  </div>
                  {!collapsed && (
                    <span className="text-sm font-medium text-medical-text-primary whitespace-nowrap">
                      Demo User
                    </span>
                  )}
                </button>

                <AnimatePresence>
                  {showLogout && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 top-full mt-2 w-48 glass-card rounded-xl shadow-medical-lg overflow-hidden z-50"
                    >
                      <Link
                        href="/profile"
                        onClick={() => setShowLogout(false)}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-medical-text-primary hover:bg-medical-primary-light transition-colors"
                      >
                        <User className="w-4 h-4" />
                        个人中心
                      </Link>
                      <Link
                        href="/settings"
                        onClick={() => setShowLogout(false)}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-medical-text-primary hover:bg-medical-primary-light transition-colors border-t border-medical-border"
                      >
                        <Settings className="w-4 h-4" />
                        设置
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-3 text-sm text-medical-danger hover:bg-medical-danger-light transition-colors border-t border-medical-border"
                      >
                        <LogOut className="w-4 h-4" />
                        退出登录
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
