"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Server, Activity, Clock, AlertTriangle, CheckCircle, RefreshCw } from "lucide-react";

interface Service {
  name: string;
  status: string;
  latency: string;
}

export default function SystemStatusPage() {
  const [overall, setOverall] = useState("healthy");
  const [uptime, setUptime] = useState("99.97%");
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/mock/system-status")
      .then((r) => r.json())
      .then((d) => {
        setOverall(d.overall || "healthy");
        setUptime(d.uptime || "99.97%");
        setServices(d.services || []);
        setLoading(false);
      })
      .catch(() => {
        setServices([
          { name: "AI 分诊服务", status: "healthy", latency: "15ms" },
          { name: "诊断引擎", status: "healthy", latency: "23ms" },
          { name: "知识库服务", status: "healthy", latency: "8ms" },
          { name: "WebSocket 服务", status: "healthy", latency: "5ms" },
        ]);
        setLoading(false);
      });
  }, []);

  return (
    <AppShell stageLabel="系统监控">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">系统状态</h1>
            <p className="text-medical-text-secondary">实时监控 MediNexus 各服务组件的运行状态。</p>
          </div>
          <button
            onClick={() => setLoading(true)}
            className="flex items-center gap-2 px-4 py-2 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:text-medical-primary hover:border-medical-primary transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            刷新状态
          </button>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            {
              label: "系统整体状态",
              value: overall === "healthy" ? "健康" : "异常",
              icon: overall === "healthy" ? CheckCircle : AlertTriangle,
              color: overall === "healthy" ? "text-medical-accent" : "text-medical-warning",
              bg: overall === "healthy" ? "bg-medical-accent-light" : "bg-medical-warning-light",
            },
            { label: "运行时间", value: uptime, icon: Clock, color: "text-medical-primary", bg: "bg-medical-primary-light" },
            { label: "服务总数", value: String(services.length), icon: Server, color: "text-medical-purple", bg: "bg-medical-purple-light" },
            {
              label: "告警",
              value: String(services.filter((s) => s.status !== "healthy").length),
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

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex gap-2">
              {[0, 150, 300].map((d) => (
                <span
                  key={d}
                  className="w-2 h-2 bg-medical-primary/40 rounded-full animate-bounce"
                  style={{ animationDelay: `${d}ms` }}
                />
              ))}
            </div>
          </div>
        ) : (
          <div className="glass-card rounded-2xl overflow-hidden">
            <div className="border-b border-medical-border bg-medical-sidebar/50">
              <div className="grid grid-cols-3 gap-4 p-4">
                <div className="font-medium text-medical-text-secondary">服务</div>
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
        )}
      </div>
    </AppShell>
  );
}
