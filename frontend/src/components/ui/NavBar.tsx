"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { IconHome, IconMessage, IconClipboard, IconUser } from "@/components/ui/icons";

const navItems = [
  { href: "/", label: "首页", Icon: IconHome },
  { href: "/consultation", label: "智能问诊", Icon: IconMessage },
  { href: "/records", label: "就诊记录", Icon: IconClipboard },
  { href: "/profile", label: "个人中心", Icon: IconUser },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[var(--color-border)]">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-secondary)] rounded-lg flex items-center justify-center shadow-sm shadow-[var(--color-primary)]/20">
            <span className="text-white font-bold text-sm" style={{ fontFamily: 'var(--font-heading)' }}>M</span>
          </div>
          <span className="font-semibold text-[var(--color-foreground)] text-sm" style={{ fontFamily: 'var(--font-heading)' }}>
            MediNexus
            <span className="hidden sm:inline text-[var(--color-muted-foreground)] font-normal text-xs ml-1">医枢</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {navItems.map(({ href, label, Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                aria-label={label}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-all duration-200
                  ${active
                    ? "bg-[var(--color-primary)]/10 text-[var(--color-primary)] font-medium"
                    : "text-[var(--color-muted-foreground)] hover:text-[var(--color-foreground)] hover:bg-[var(--color-muted)]"
                  }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
