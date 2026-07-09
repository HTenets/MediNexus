"use client";

import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import {
  User,
  Bell,
  Shield,
  Globe,
  Edit3,
  ChevronRight,
  Settings,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Save,
  Smartphone,
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Server,
} from "lucide-react";
import { useState } from "react";

interface Service {
  name: string;
  status: string;
  latency: string;
}

const sections = [
  {
    icon: User,
    label: "账户信息",
    desc: "管理您的个人资料与联系方式",
    color: "bg-medical-primary-light text-medical-primary",
    id: "account",
  },
  {
    icon: Bell,
    label: "通知偏好",
    desc: "自定义通知类型与接收方式",
    color: "bg-medical-warning-light text-medical-warning",
    id: "notifications",
  },
  {
    icon: Shield,
    label: "隐私与安全",
    desc: "密码、认证与登录设备管理",
    color: "bg-medical-danger-light text-medical-danger",
    id: "privacy",
  },
  {
    icon: Globe,
    label: "语言与地区",
    desc: "设置界面语言与地区偏好",
    color: "bg-medical-accent-light text-medical-accent",
    id: "language",
  },
  {
    icon: Activity,
    label: "系统状态",
    desc: "查看系统运行状态与服务监控",
    color: "bg-medical-purple-light text-medical-purple",
    id: "system-status",
  },
];

const mockServices: Service[] = [
  { name: "AI 分诊服务", status: "healthy", latency: "15ms" },
  { name: "诊断引擎", status: "healthy", latency: "23ms" },
  { name: "知识库服务", status: "warning", latency: "120ms" },
  { name: "WebSocket 服务", status: "healthy", latency: "5ms" },
  { name: "消息推送服务", status: "healthy", latency: "18ms" },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("account");
  const [showPassword, setShowPassword] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    followUp: true,
    system: false,
  });
  const [services, setServices] = useState<Service[]>(mockServices);
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setServices([...mockServices]);
      setRefreshing(false);
    }, 1000);
  };

  const overallStatus = services.every((s) => s.status === "healthy") ? "healthy" : "warning";
  const alertCount = services.filter((s) => s.status !== "healthy").length;

  return (
    <AppShell stageLabel="系统设置" activePath="/settings">
      <div className="max-w-6xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3"
        >
          <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center">
            <Settings className="w-5 h-5 text-medical-primary" />
          </div>
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary">
              设置
            </h1>
            <p className="text-medical-text-secondary text-sm mt-1">
              管理您的账户信息、通知偏好、隐私安全及系统配置。
            </p>
          </div>
        </motion.div>

        <div className="grid grid-cols-12 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-4"
          >
            <div className="glass-card rounded-2xl p-3 sticky top-6">
              <div className="space-y-1">
                {sections.map((section, index) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all ${
                      activeSection === section.id
                        ? "bg-white shadow-medical-sm text-medical-text-primary font-medium"
                        : "text-medical-text-secondary hover:bg-white/50 hover:text-medical-text-primary"
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-lg ${section.color.split(" ")[0]} flex items-center justify-center flex-shrink-0`}
                    >
                      <section.icon
                        className={`w-4 h-4 ${section.color.split(" ")[1]}`}
                      />
                    </div>
                    <div className="text-left flex-1">
                      <div>{section.label}</div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-medical-text-muted" />
                  </button>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-8 space-y-6"
            key={activeSection}
          >
            {activeSection === "account" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-2xl p-6"
              >
                <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                  账户信息
                </h3>
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      用户名
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                        <User className="w-4 h-4" />
                      </div>
                      <input
                        type="text"
                        defaultValue="Demo User"
                        className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      邮箱地址
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                        <Mail className="w-4 h-4" />
                      </div>
                      <input
                        type="email"
                        defaultValue="demo@medinexus.local"
                        className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      手机号
                    </label>
                    <div className="relative">
                      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                        <Smartphone className="w-4 h-4" />
                      </div>
                      <input
                        type="tel"
                        placeholder="请输入手机号"
                        className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                      />
                    </div>
                  </div>
                  <div className="pt-2">
                    <button className="inline-flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all">
                      <Save className="w-4 h-4" />
                      保存更改
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {activeSection === "notifications" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-2xl p-6"
              >
                <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                  通知偏好
                </h3>
                <div className="space-y-4">
                  {[
                    { key: "email", label: "邮件通知", desc: "接收问诊结果、随访提醒等邮件" },
                    { key: "push", label: "推送通知", desc: "浏览器或移动端推送通知" },
                    { key: "sms", label: "短信通知", desc: "重要提醒的短信通知" },
                    { key: "followUp", label: "随访提醒", desc: "复诊、检查等随访计划提醒" },
                    { key: "system", label: "系统公告", desc: "平台更新、维护通知等" },
                  ].map((item, index) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between p-4 rounded-xl hover:bg-white/60 transition-colors"
                    >
                      <div>
                        <div className="text-sm font-medium text-medical-text-primary">
                          {item.label}
                        </div>
                        <div className="text-xs text-medical-text-muted mt-0.5">
                          {item.desc}
                        </div>
                      </div>
                      <button
                        onClick={() =>
                          setNotifications((prev) => ({
                            ...prev,
                            [item.key]: !prev[item.key as keyof typeof prev],
                          }))
                        }
                        className={`relative w-12 h-7 rounded-full transition-colors ${
                          notifications[item.key as keyof typeof notifications]
                            ? "bg-medical-primary"
                            : "bg-gray-200"
                        }`}
                      >
                        <span
                          className={`absolute top-1 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                            notifications[item.key as keyof typeof notifications]
                              ? "left-6"
                              : "left-1"
                          }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeSection === "privacy" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="glass-card rounded-2xl p-6">
                  <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                    修改密码
                  </h3>
                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-medical-text-primary mb-2">
                        当前密码
                      </label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                          <Lock className="w-4 h-4" />
                        </div>
                        <input
                          type={showPassword ? "text" : "password"}
                          placeholder="请输入当前密码"
                          className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-medical-text-muted hover:text-medical-primary"
                        >
                          {showPassword ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-medical-text-primary mb-2">
                        新密码
                      </label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                          <Lock className="w-4 h-4" />
                        </div>
                        <input
                          type="password"
                          placeholder="请输入新密码"
                          className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-medical-text-primary mb-2">
                        确认新密码
                      </label>
                      <div className="relative">
                        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                          <Lock className="w-4 h-4" />
                        </div>
                        <input
                          type="password"
                          placeholder="请再次输入新密码"
                          className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                        />
                      </div>
                    </div>
                    <div className="pt-2">
                      <button className="inline-flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all">
                        <Save className="w-4 h-4" />
                        修改密码
                      </button>
                    </div>
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-6">
                  <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                    双因素认证
                  </h3>
                  <div className="flex items-center justify-between p-4 rounded-xl bg-medical-warning-light/30 border border-medical-warning/20">
                    <div>
                      <div className="text-sm font-medium text-medical-text-primary">
                        启用双因素认证
                      </div>
                      <div className="text-xs text-medical-text-muted mt-0.5">
                        增强账户安全性，登录时需要二次验证
                      </div>
                    </div>
                    <Badge variant="warning">未启用</Badge>
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-6">
                  <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                    登录设备管理
                  </h3>
                  <div className="space-y-3">
                    {[
                      {
                        device: "Chrome on Windows",
                        location: "上海 · 当前设备",
                        lastActive: "刚刚",
                        current: true,
                      },
                      {
                        device: "Safari on iPhone",
                        location: "上海",
                        lastActive: "2小时前",
                        current: false,
                      },
                      {
                        device: "Chrome on macOS",
                        location: "北京",
                        lastActive: "3天前",
                        current: false,
                      },
                    ].map((item, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 rounded-xl hover:bg-white/60 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center">
                            <Smartphone className="w-5 h-5 text-medical-primary" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-medical-text-primary flex items-center gap-2">
                              {item.device}
                              {item.current && (
                                <Badge variant="primary" className="px-2 py-0.5 text-[10px]">
                                  当前
                                </Badge>
                              )}
                            </div>
                            <div className="text-xs text-medical-text-muted mt-0.5">
                              {item.location} · {item.lastActive}
                            </div>
                          </div>
                        </div>
                        {!item.current && (
                          <button className="text-xs text-medical-danger hover:underline">
                            移除
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {activeSection === "language" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-2xl p-6"
              >
                <h3 className="font-semibold text-medical-text-primary text-lg mb-6">
                  语言与地区
                </h3>
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      界面语言
                    </label>
                    <select className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus bg-white cursor-pointer">
                      <option>简体中文 (zh-CN)</option>
                      <option>English (en-US)</option>
                      <option>日本語 (ja-JP)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      时区
                    </label>
                    <select className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus bg-white cursor-pointer">
                      <option>Asia/Shanghai (UTC+8) 北京</option>
                      <option>Asia/Tokyo (UTC+9) 东京</option>
                      <option>America/New_York (UTC-5) 纽约</option>
                      <option>Europe/London (UTC+0) 伦敦</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      日期格式
                    </label>
                    <select className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus bg-white cursor-pointer">
                      <option>YYYY-MM-DD (2024-01-15)</option>
                      <option>DD/MM/YYYY (15/01/2024)</option>
                      <option>MM/DD/YYYY (01/15/2024)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-medical-text-primary mb-2">
                      温度单位
                    </label>
                    <select className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm outline-none transition-all input-focus bg-white cursor-pointer">
                      <option>摄氏度 (°C)</option>
                      <option>华氏度 (°F)</option>
                    </select>
                  </div>
                  <div className="pt-2">
                    <button className="inline-flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all">
                      <Save className="w-4 h-4" />
                      保存偏好
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {activeSection === "system-status" && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-medical-text-primary text-lg">
                      系统状态
                    </h3>
                    <p className="text-sm text-medical-text-secondary mt-1">
                      实时监控 MediNexus 各服务组件的运行状态
                    </p>
                  </div>
                  <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="flex items-center gap-2 px-4 py-2 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:text-medical-primary hover:border-medical-primary transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
                    刷新状态
                  </button>
                </div>

                <div className="grid grid-cols-4 gap-4">
                  {[
                    {
                      label: "系统整体状态",
                      value: overallStatus === "healthy" ? "健康" : "异常",
                      icon: overallStatus === "healthy" ? CheckCircle : AlertTriangle,
                      color: overallStatus === "healthy" ? "text-medical-accent" : "text-medical-warning",
                      bg: overallStatus === "healthy" ? "bg-medical-accent-light" : "bg-medical-warning-light",
                    },
                    { label: "运行时间", value: "99.97%", icon: Clock, color: "text-medical-primary", bg: "bg-medical-primary-light" },
                    { label: "服务总数", value: String(services.length), icon: Server, color: "text-medical-purple", bg: "bg-medical-purple-light" },
                    {
                      label: "告警数",
                      value: String(alertCount),
                      icon: AlertTriangle,
                      color: "text-medical-danger",
                      bg: "bg-medical-danger-light",
                    },
                  ].map((stat) => (
                    <div key={stat.label} className="glass-card rounded-2xl p-5">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs text-medical-text-muted">{stat.label}</span>
                        <div className={`w-8 h-8 rounded-lg ${stat.bg} flex items-center justify-center`}>
                          <stat.icon className={`w-4 h-4 ${stat.color}`} />
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-medical-text-primary">{stat.value}</div>
                    </div>
                  ))}
                </div>

                <div className="glass-card rounded-2xl overflow-hidden">
                  <div className="border-b border-medical-border bg-medical-sidebar/50">
                    <div className="grid grid-cols-3 gap-4 p-4">
                      <div className="font-medium text-medical-text-secondary">服务名称</div>
                      <div className="font-medium text-medical-text-secondary">状态</div>
                      <div className="font-medium text-medical-text-secondary">延迟</div>
                    </div>
                  </div>
                  <div className="divide-y divide-medical-border">
                    {services.map((s) => (
                      <div key={s.name} className="grid grid-cols-3 gap-4 p-4 items-center hover:bg-white/50 transition-colors">
                        <div className="flex items-center gap-3">
                          <Activity className="w-4 h-4 text-medical-primary" />
                          <span className="font-medium text-medical-text-primary">{s.name}</span>
                        </div>
                        <div>
                          <span
                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                              s.status === "healthy"
                                ? "bg-medical-accent-light text-medical-accent"
                                : "bg-medical-warning-light text-medical-warning"
                            }`}
                          >
                            <CheckCircle className="w-3 h-3" />
                            {s.status === "healthy" ? "运行正常" : "存在告警"}
                          </span>
                        </div>
                        <div className="text-sm text-medical-text-secondary">{s.latency}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </AppShell>
  );
}
