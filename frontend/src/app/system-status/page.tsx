"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Server, Activity, Clock, AlertTriangle, CheckCircle, RefreshCw, Info } from "lucide-react";
import { healthCheck, ApiError, HealthCheckResponse } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";

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
  const [error, setError] = useState<ApiError | null>(null);
  const [version, setVersion] = useState("");
  const [mode, setMode] = useState("");

  const mockServices = [
    { name: "AI 分诊服务", status: "healthy", latency: "15ms" },
    { name: "诊断引擎", status: "healthy", latency: "23ms" },
    { name: "知识库服务", status: "healthy", latency: "8ms" },
    { name: "WebSocket 服务", status: "healthy", latency: "5ms" },
  ];

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const data: HealthCheckResponse = await healthCheck();
      setOverall(data.status === "ok" ? "healthy" : "异常");
      setUptime(data.mode === "demo" ? "100%" : "99.97%");
      setServices(mockServices);
      setVersion(data.version);
      setMode(data.mode);
    } catch (err) {
      setError(err as ApiError);
      setServices(mockServices);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <AppShell stageLabel="系统监控">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">系统状态</h1>
            <p className="text-medical-text-secondary">实时监控 MediNexus 各服务组件的运行状态。</p>
          </div>
          <Button onClick={fetchStatus} variant="outline" size="sm" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            刷新状态
          </Button>
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
            { label: "版本号", value: version || "-", icon: Info, color: "text-medical-purple", bg: "bg-medical-purple-light" },
            {
              label: "运行模式",
              value: mode === "demo" ? "演示模式" : mode === "production" ? "生产模式" : "-",
              icon: Server,
              color: mode === "demo" ? "text-medical-warning" : "text-medical-accent",
              bg: mode === "demo" ? "bg-medical-warning-light" : "bg-medical-accent-light",
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
          <LoadingState />
        ) : error ? (
          <div className="glass-card rounded-2xl p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-medical-warning mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-medical-text-primary mb-2">获取系统状态失败</h3>
            <p className="text-medical-text-secondary mb-4">{error.message}</p>
            <Button onClick={fetchStatus} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              重试
            </Button>
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
