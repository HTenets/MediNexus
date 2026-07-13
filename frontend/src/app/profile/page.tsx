"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import AppShell from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { useAuth } from "@/hooks/useAuth";
import { listRecords, getPatient, ApiError } from "@/lib/api";
import { LoadingState } from "@/components/ui/LoadingState";
import {
  User,
  Mail,
  Calendar,
  Heart,
  ChevronRight,
  Edit3,
  Activity,
  Clock,
  Award,
  Shield,
  FileText,
  Cpu,
  Watch,
  Smartphone,
  Plus,
  RefreshCw,
  Zap,
  Sliders,
  Brain,
  Bell,
  ChevronDown,
} from "lucide-react";

const menuItems = [
  {
    icon: Heart,
    label: "健康档案",
    href: "/records",
    desc: "查看您的健康数据与就诊记录",
    color: "bg-medical-primary-light text-medical-primary",
  },
  {
    icon: FileText,
    label: "健康报告",
    href: "/records",
    desc: "查看AI生成的健康分析报告",
    color: "bg-medical-accent-light text-medical-accent",
  },
  {
    icon: Cpu,
    label: "AI 分析配置",
    href: "#ai-config",
    desc: "自定义AI诊断模型与偏好",
    color: "bg-medical-purple-light text-medical-purple",
  },
  {
    icon: Smartphone,
    label: "设备管理",
    href: "#devices",
    desc: "管理已授权的健康设备",
    color: "bg-medical-warning-light text-medical-warning",
  },
];

const aiModels = [
  { value: "standard", label: "标准模型" },
  { value: "advanced", label: "高级模型" },
  { value: "expert", label: "专家模型" },
];

const analysisModes = [
  { value: "fast", label: "快速", icon: Zap, desc: "快速分析，基础诊断" },
  { value: "balanced", label: "均衡", icon: Sliders, desc: "平衡速度与深度" },
  { value: "deep", label: "深度", icon: Brain, desc: "深度分析，精准诊断" },
];

const devices = [
  {
    name: "Apple Watch Series 9",
    type: "智能手表",
    status: "online",
    lastSync: "10分钟前",
    icon: Watch,
    color: "bg-medical-primary-light text-medical-primary",
  },
  {
    name: "小米血压计 2",
    type: "血压监测",
    status: "offline",
    lastSync: "2天前",
    icon: Activity,
    color: "bg-medical-accent-light text-medical-accent",
  },
  {
    name: "华为体脂秤",
    type: "体重体脂",
    status: "online",
    lastSync: "3小时前",
    icon: Award,
    color: "bg-medical-purple-light text-medical-purple",
  },
  {
    name: "欧姆龙血糖仪",
    type: "血糖监测",
    status: "offline",
    lastSync: "1周前",
    icon: Shield,
    color: "bg-medical-warning-light text-medical-warning",
  },
];

export default function ProfilePage() {
  const [selectedModel, setSelectedModel] = useState("standard");
  const [analysisMode, setAnalysisMode] = useState("balanced");
  const [conservativeDiagnosis, setConservativeDiagnosis] = useState(true);
  const [autoFollowUp, setAutoFollowUp] = useState(true);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [consultationCount, setConsultationCount] = useState(0);
  const [patientAge, setPatientAge] = useState("-");
  const [patientGender, setPatientGender] = useState("-");

  const { user, loading: authLoading } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      setDataLoading(true);
      setError(null);
      try {
        const recordsResult = await listRecords("patient_demo_001");
        setConsultationCount(recordsResult.total || 0);

        const patientData = await getPatient("patient_demo_001");
        setPatientAge(patientData.age?.toString() || "-");
        setPatientGender(patientData.gender === "male" ? "男" : patientData.gender === "female" ? "女" : "-");
      } catch (err) {
        setError(err as ApiError);
      } finally {
        setDataLoading(false);
      }
    };

    if (!authLoading && user) {
      fetchData();
    }
  }, [authLoading, user]);

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleLabel = (role: string) => {
    return role === "patient" ? "普通用户" : role === "doctor" ? "医生" : "未知";
  };

  if (authLoading || dataLoading) {
    return (
      <AppShell stageLabel="个人中心" activePath="/profile">
        <div className="max-w-4xl mx-auto py-20">
          <LoadingState text="加载中..." size="lg" />
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell stageLabel="个人中心" activePath="/profile">
        <div className="max-w-4xl mx-auto py-20 text-center">
          <div className="text-medical-text-muted mb-4">
            <p className="text-lg">加载失败</p>
            <p className="text-sm mt-2">{error.message}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 gradient-primary text-white rounded-xl text-sm font-medium hover:shadow-glow transition-all"
          >
            重试
          </button>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell stageLabel="个人中心" activePath="/profile">
      <div className="max-w-4xl mx-auto space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-2xl p-6"
        >
          <div className="flex items-start gap-5">
            <div className="w-20 h-20 rounded-2xl gradient-primary flex items-center justify-center text-white text-2xl font-bold shadow-medical-primary flex-shrink-0">
              {user ? getInitials(user.name) : "?"}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-xl font-semibold text-medical-text-primary">{user?.name || "未知用户"}</h2>
                <Badge variant="primary">{user ? getRoleLabel(user.role) : "未知"}</Badge>
              </div>
              <div className="flex items-center gap-1.5 text-sm text-medical-text-secondary mb-2">
                <Mail className="w-4 h-4" />
                {user?.email || "-"}
              </div>
              <div className="flex items-center gap-1.5 text-sm text-medical-text-muted">
                <Calendar className="w-4 h-4" />
                年龄: {patientAge} 岁 · {patientGender}
              </div>
            </div>
            <Link
              href="/settings"
              className="flex items-center gap-1.5 px-4 py-2 border border-medical-primary text-medical-primary rounded-xl text-sm font-medium hover:bg-medical-primary-light transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              编辑资料
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-medical-text-primary text-lg">健康指标概览</h3>
            <Link
              href="/dashboard"
              className="text-sm text-medical-primary hover:text-medical-primary-dark transition-colors flex items-center gap-1"
            >
              查看详情
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: "问诊次数", value: consultationCount.toString(), icon: Activity, color: "text-medical-primary", bg: "bg-medical-primary-light" },
              { label: "健康评分", value: "92", icon: Award, color: "text-medical-accent", bg: "bg-medical-accent-light" },
              { label: "档案完整度", value: "68%", icon: Shield, color: "text-medical-purple", bg: "bg-medical-purple-light" },
              { label: "连续打卡", value: "12天", icon: Clock, color: "text-medical-warning", bg: "bg-medical-warning-light" },
            ].map((stat, index) => (
              <div
                key={stat.label}
                className="text-center p-4 rounded-xl bg-white/60 hover:bg-white transition-colors"
              >
                <div className={`w-10 h-10 mx-auto rounded-xl ${stat.bg} flex items-center justify-center mb-2`}>
                  <stat.icon className={`w-5 h-5 ${stat.color}`} />
                </div>
                <div className="text-2xl font-bold text-medical-text-primary">{stat.value}</div>
                <div className="text-xs text-medical-text-muted">{stat.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          id="ai-config"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-medical-purple-light flex items-center justify-center">
              <Cpu className="w-5 h-5 text-medical-purple" />
            </div>
            <div>
              <h3 className="font-semibold text-medical-text-primary text-lg">AI 分析配置</h3>
              <p className="text-sm text-medical-text-muted">自定义AI诊断模型与分析偏好</p>
            </div>
          </div>

          <div className="space-y-5">
            <div className="flex items-center justify-between p-4 rounded-xl bg-white/60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center">
                  <Brain className="w-5 h-5 text-medical-primary" />
                </div>
                <div>
                  <div className="font-medium text-medical-text-primary">诊断模型</div>
                  <div className="text-sm text-medical-text-muted">选择用于诊断分析的AI模型</div>
                </div>
              </div>
              <div className="relative">
                <button
                  onClick={() => setModelDropdownOpen(!modelDropdownOpen)}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-medical-border rounded-xl text-sm text-medical-text-primary hover:border-medical-primary transition-colors"
                >
                  {aiModels.find(m => m.value === selectedModel)?.label}
                  <ChevronDown className="w-4 h-4 text-medical-text-muted" />
                </button>
                {modelDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-40 bg-white border border-medical-border rounded-xl shadow-lg z-10 overflow-hidden"
                  >
                    {aiModels.map((model) => (
                      <button
                        key={model.value}
                        onClick={() => {
                          setSelectedModel(model.value);
                          setModelDropdownOpen(false);
                        }}
                        className={`w-full px-4 py-2.5 text-left text-sm hover:bg-medical-primary-light transition-colors ${
                          selectedModel === model.value
                            ? "text-medical-primary bg-medical-primary-light/50"
                            : "text-medical-text-primary"
                        }`}
                      >
                        {model.label}
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white/60">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-medical-accent-light flex items-center justify-center">
                  <Zap className="w-5 h-5 text-medical-accent" />
                </div>
                <div>
                  <div className="font-medium text-medical-text-primary">分析强度</div>
                  <div className="text-sm text-medical-text-muted">调整分析深度与速度的平衡</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {analysisModes.map((mode) => {
                  const Icon = mode.icon;
                  const isActive = analysisMode === mode.value;
                  return (
                    <button
                      key={mode.value}
                      onClick={() => setAnalysisMode(mode.value)}
                      className={`p-3 rounded-xl transition-all ${
                        isActive
                          ? "bg-medical-accent text-white shadow-medical-accent"
                          : "bg-white/80 hover:bg-white text-medical-text-secondary"
                      }`}
                    >
                      <Icon className={`w-5 h-5 mx-auto mb-1 ${isActive ? "text-white" : ""}`} />
                      <div className={`text-sm font-medium ${isActive ? "text-white" : "text-medical-text-primary"}`}>
                        {mode.label}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-white/60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-medical-purple-light flex items-center justify-center">
                  <Shield className="w-5 h-5 text-medical-purple" />
                </div>
                <div>
                  <div className="font-medium text-medical-text-primary">诊断偏好</div>
                  <div className="text-sm text-medical-text-muted">
                    {conservativeDiagnosis ? "保守诊断 - 建议进一步检查确认" : "积极治疗 - 直接给出治疗方案"}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setConservativeDiagnosis(!conservativeDiagnosis)}
                className={`relative w-14 h-7 rounded-full transition-colors ${
                  conservativeDiagnosis ? "bg-medical-purple" : "bg-medical-border"
                }`}
              >
                <motion.div
                  animate={{ x: conservativeDiagnosis ? 28 : 2 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  className="absolute top-0.5 w-6 h-6 bg-white rounded-full shadow-md"
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-white/60">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-medical-warning-light flex items-center justify-center">
                  <Bell className="w-5 h-5 text-medical-warning" />
                </div>
                <div>
                  <div className="font-medium text-medical-text-primary">自动随访提醒</div>
                  <div className="text-sm text-medical-text-muted">AI自动提醒复诊和健康检查</div>
                </div>
              </div>
              <button
                onClick={() => setAutoFollowUp(!autoFollowUp)}
                className={`relative w-14 h-7 rounded-full transition-colors ${
                  autoFollowUp ? "bg-medical-warning" : "bg-medical-border"
                }`}
              >
                <motion.div
                  animate={{ x: autoFollowUp ? 28 : 2 }}
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  className="absolute top-0.5 w-6 h-6 bg-white rounded-full shadow-md"
                />
              </button>
            </div>
          </div>
        </motion.div>

        <motion.div
          id="devices"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-medical-warning-light flex items-center justify-center">
                <Smartphone className="w-5 h-5 text-medical-warning" />
              </div>
              <div>
                <h3 className="font-semibold text-medical-text-primary text-lg">设备授权管理</h3>
                <p className="text-sm text-medical-text-muted">管理已连接的健康监测设备</p>
              </div>
            </div>
            <button className="flex items-center gap-1.5 px-4 py-2 gradient-primary text-white rounded-xl text-sm font-medium hover:shadow-glow transition-all">
              <Plus className="w-4 h-4" />
              添加设备
            </button>
          </div>

          <div className="space-y-3">
            {devices.map((device, index) => {
              const Icon = device.icon;
              return (
                <motion.div
                  key={device.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.35 + index * 0.05 }}
                  className="flex items-center gap-4 p-4 rounded-xl bg-white/60 hover:bg-white transition-colors"
                >
                  <div className={`w-12 h-12 rounded-xl ${device.color.split(" ")[0]} flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-6 h-6 ${device.color.split(" ")[1]}`} />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-medical-text-primary">{device.name}</div>
                    <div className="text-sm text-medical-text-muted flex items-center gap-2">
                      <span>{device.type}</span>
                      <span className="text-medical-border">·</span>
                      <span className={`inline-flex items-center gap-1 ${
                        device.status === "online" ? "text-medical-accent" : "text-medical-text-muted"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          device.status === "online" ? "bg-medical-accent" : "bg-medical-text-muted"
                        }`} />
                        {device.status === "online" ? "在线" : "离线"}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-sm text-medical-text-muted">
                      <RefreshCw className="w-3.5 h-3.5" />
                      {device.lastSync}同步
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-medical-text-muted" />
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card rounded-2xl overflow-hidden"
        >
          <div className="p-5 border-b border-medical-border">
            <h3 className="font-semibold text-medical-text-primary text-lg">功能菜单</h3>
            <p className="text-sm text-medical-text-muted mt-1">快速访问各项功能</p>
          </div>
          <div className="divide-y divide-medical-border">
            {menuItems.map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.45 + index * 0.05 }}
              >
                <Link
                  href={item.href}
                  className="flex items-center gap-4 p-4 hover:bg-white/50 transition-colors group"
                >
                  <div className={`w-10 h-10 rounded-xl ${item.color.split(" ")[0]} flex items-center justify-center flex-shrink-0`}>
                    <item.icon className={`w-5 h-5 ${item.color.split(" ")[1]}`} />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-medical-text-primary">{item.label}</div>
                    <div className="text-sm text-medical-text-muted">{item.desc}</div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-medical-text-muted group-hover:text-medical-primary transition-colors" />
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card rounded-2xl p-6"
        >
          <h3 className="font-semibold text-medical-text-primary mb-4">关于 MediNexus</h3>
          <div className="grid grid-cols-3 gap-4 text-center mb-4">
            {[
              { label: "版本", value: "v0.1.0" },
              { label: "协议", value: "MIT" },
              { label: "更新时间", value: "2024-01" },
            ].map((item) => (
              <div key={item.label} className="p-3 rounded-xl bg-white/60">
                <div className="text-xs text-medical-text-muted mb-1">{item.label}</div>
                <div className="text-sm font-medium text-medical-text-primary">{item.value}</div>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center">
            <Link
              href="/settings"
              className="px-6 py-2 border border-medical-primary text-medical-primary rounded-xl text-sm hover:bg-medical-primary-light transition-colors"
            >
              设置
            </Link>
          </div>
        </motion.div>
      </div>
    </AppShell>
  );
}
