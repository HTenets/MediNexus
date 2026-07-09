"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingState } from "@/components/ui/LoadingState";
import {
  Heart,
  Activity,
  Thermometer,
  Gauge,
  AlertTriangle,
  CheckCircle,
  Zap,
  Shield,
  Clock,
} from "lucide-react";

interface DashboardData {
  vitals: Record<string, string>;
  bio_age: string;
  risks: string[];
  ai_suggestions: string[];
  devices: string[];
}

const vitalsConfig = {
  heart: { label: "心率", unit: "bpm", icon: Heart, color: "text-red-500", bg: "bg-red-50" },
  blood: { label: "血压", unit: "mmHg", icon: Gauge, color: "text-blue-500", bg: "bg-blue-50" },
  oxygen: { label: "血氧", unit: "%", icon: Activity, color: "text-green-500", bg: "bg-green-50" },
  temperature: { label: "体温", unit: "°C", icon: Thermometer, color: "text-orange-500", bg: "bg-orange-50" },
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/mock/dashboard/patient_demo_001")
      .then((r) => r.json())
      .then((d) => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <AppShell stageLabel="控制台" activePath="/dashboard">
        <div className="flex items-center justify-center h-96">
          <LoadingState text="加载健康数据..." />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell stageLabel="控制台" activePath="/dashboard">
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary">
              数字孪生全景视图
            </h1>
            <p className="text-medical-text-secondary mt-2">
              实时健康状态监测与预测分析
            </p>
          </div>
          <Badge variant="success" className="px-4 py-2 text-sm">
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="inline-block w-2 h-2 bg-medical-accent rounded-full mr-2"
            />
            实时同步
          </Badge>
        </motion.div>

        <div className="grid grid-cols-12 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-3 space-y-6"
          >
            <Card className="p-6">
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200 }}
                  className="text-6xl font-bold text-gradient mb-2"
                >
                  {data?.bio_age || "--"}
                  <span className="text-xl text-medical-text-muted font-normal ml-1">岁</span>
                </motion.div>
                <div className="text-medical-accent text-sm font-medium flex items-center justify-center gap-2">
                  <Activity className="w-4 h-4" />
                  生物学年龄
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <CardHeader title="核心体征" />
              <CardContent className="space-y-4">
                {Object.entries(data?.vitals || { 心率: "--", 血压: "--", 血氧: "--" }).map(([key, value], index) => {
                  const config = Object.values(vitalsConfig)[index % 4];
                  const Icon = config.icon;
                  return (
                    <motion.div
                      key={key}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 + index * 0.1 }}
                      className="flex items-center justify-between p-3 rounded-xl bg-gray-50/50"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg ${config.bg} flex items-center justify-center`}>
                          <Icon className={`w-4 h-4 ${config.color}`} />
                        </div>
                        <span className="text-sm text-medical-text-secondary">{key}</span>
                      </div>
                      <span className="font-semibold text-medical-text-primary">{value}</span>
                    </motion.div>
                  );
                })}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-6"
          >
            <Card className="p-6 h-full">
              <CardHeader
                title="3D 数字孪生模型"
                subtitle="基于患者数据生成的人体数字模型"
              />
              <CardContent className="relative h-[400px]">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-medical-primary-light/30 via-white to-medical-accent-light/30 flex items-center justify-center">
                  <div className="text-center">
                    <motion.div
                      animate={{ rotateY: 360 }}
                      transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                      style={{ transformStyle: "preserve-3d" }}
                      className="w-32 h-32 mx-auto mb-6 relative"
                    >
                      <div className="absolute inset-0 rounded-full border-4 border-medical-primary/20" />
                      <div className="absolute inset-4 rounded-full border-4 border-medical-primary/40" />
                      <div className="absolute inset-8 rounded-full border-4 border-medical-primary/60" />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <motion.div
                          animate={{ scale: [1, 1.1, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="w-12 h-12 rounded-full gradient-primary flex items-center justify-center text-white"
                        >
                          <Activity className="w-6 h-6" />
                        </motion.div>
                      </div>
                    </motion.div>
                    <p className="text-medical-text-muted text-sm">人体数字孪生模型</p>
                    <p className="text-medical-text-secondary text-xs mt-1">数据同步中...</p>
                  </div>
                </div>

                <div className="absolute bottom-4 left-4 right-4 flex justify-between">
                  {[
                    { label: "心率", value: data?.vitals?.心率 || "--", color: "text-red-500" },
                    { label: "血氧", value: data?.vitals?.血氧 || "--", color: "text-green-500" },
                    { label: "血压", value: data?.vitals?.血压 || "--", color: "text-blue-500" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${item.color} bg-current`} />
                      <span className="text-xs text-medical-text-muted">{item.label}</span>
                      <span className="text-sm font-semibold text-medical-text-primary">{item.value}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-3 space-y-6"
          >
            <Card className="p-6">
              <CardHeader title="今日风险" />
              <CardContent className="space-y-3">
                {(data?.risks || ["暂无风险数据"]).map((risk, index) => (
                  <motion.div
                    key={risk}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className={`flex items-start gap-3 p-3 rounded-xl ${
                      risk.includes("风险") ? "bg-medical-danger-light/50" : "bg-medical-accent-light/50"
                    }`}
                  >
                    {risk.includes("风险") ? (
                      <AlertTriangle className="w-4 h-4 text-medical-danger flex-shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-medical-accent flex-shrink-0 mt-0.5" />
                    )}
                    <span className="text-sm text-medical-text-secondary">{risk}</span>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            <Card className="p-6">
              <CardHeader title="AI 建议" />
              <CardContent className="space-y-3">
                {(data?.ai_suggestions || ["暂无建议"]).map((suggestion, index) => (
                  <motion.div
                    key={suggestion}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="flex items-start gap-3 p-3 rounded-xl bg-medical-primary-light/50"
                  >
                    <Zap className="w-4 h-4 text-medical-primary flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-medical-text-secondary">{suggestion}</span>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            <Card className="p-6">
              <CardHeader title="设备同步" />
              <CardContent className="space-y-3">
                {(data?.devices || ["暂无设备信息"]).map((device, index) => (
                  <motion.div
                    key={device}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-xl bg-gray-50"
                  >
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-medical-text-muted" />
                      <span className="text-sm text-medical-text-secondary">{device}</span>
                    </div>
                    <span className="w-2 h-2 rounded-full bg-medical-accent" />
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-4 gap-6"
        >
          {[
            { title: "今日步数", value: "8,520", icon: Activity, color: "text-medical-accent" },
            { title: "睡眠时长", value: "7.5h", icon: Clock, color: "text-medical-purple" },
            { title: "饮水量", value: "1.8L", icon: Thermometer, color: "text-medical-primary" },
            { title: "卡路里", value: "1,250", icon: Heart, color: "text-red-500" },
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ y: -4 }}
              className="glass-card rounded-2xl p-6 card-hover"
            >
              <div className="flex items-center justify-between mb-4">
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
                <Badge variant="primary">{new Date().toLocaleDateString()}</Badge>
              </div>
              <div className="text-3xl font-bold text-medical-text-primary mb-1">{stat.value}</div>
              <div className="text-sm text-medical-text-secondary">{stat.title}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </AppShell>
  );
}
