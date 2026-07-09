"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MessageCircle, ClipboardList, User } from "lucide-react";

const navItems = [
  { href: "/", label: "首页", icon: Home },
  { href: "/consultation", label: "智能问诊", icon: MessageCircle },
  { href: "/records", label: "就诊记录", icon: ClipboardList },
  { href: "/profile", label: "个人中心", icon: User },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 glass border-b border-medical-border"
    >
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <motion.div
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-medical-primary"
          >
            M
          </motion.div>
          <div>
            <span className="font-heading font-semibold text-medical-text-primary text-sm">
              MediNexus
            </span>
            <span className="hidden sm:inline text-medical-text-muted font-normal text-xs ml-1">
              医枢
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href;
            return (
              <motion.div key={href} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link
                  href={href}
                  aria-label={label}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm transition-all duration-300 ${
                    isActive
                      ? "gradient-primary text-white font-medium shadow-medical-primary"
                      : "text-medical-text-secondary hover:text-medical-primary hover:bg-medical-primary-light"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              </motion.div>
            );
          })}
        </nav>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="gradient-primary text-white px-5 py-2 rounded-xl text-sm font-medium shadow-medical-primary"
        >
          登录
        </motion.button>
      </div>
    </motion.header>
  );
}
