"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import {
  FileText,
  Calendar,
  ArrowRight,
  Plus,
  Upload,
  Activity,
  Clock,
  AlertTriangle,
  Pill,
  Heart,
  Brain,
  CheckCircle,
  ChevronRight,
} from "lucide-react";

const mockRecords = [
  {
    id: "REC20260612001",
    date: "2026-06-12",
    type: "AI 智能问诊",
    summary: "急性上呼吸道感染，伴头痛、发热、心悸",
    status: "completed",
    department: "内科",
    doctor: "AI 诊断系统",
  },
  {
    id: "REC20260520002",
    date: "2026-05-20",
    type: "健康咨询",
    summary: "偏头痛用药建议，生活方式指导",
    status: "completed",
    department: "神经科",
    doctor: "AI 诊断系统",
  },
  {
    id: "REC20260415003",
    date: "2026-04-15",
    type: "检查报告",
    summary: "年度体检报告，各项指标基本正常",
    status: "completed",
    department: "体检中心",
    doctor: "线下医院",
  },
  {
    id: "REC20260308004",
    date: "2026-03-08",
    type: "AI 智能问诊",
    summary: "皮肤过敏咨询，建议避免接触过敏原",
    status: "completed",
    department: "皮肤科",
    doctor: "AI 诊断系统",
  },
];

const overviewStats = [
  {
    label: "综合健康评分",
    value: "92",
    unit: "/100",
    progress: 92,
    color: "text-medical-primary",
    bgColor: "bg-medical-primary",
  },
  {
    label: "生物学年龄",
    value: "34",
    unit: "岁",
    badge: "↓ -2岁",
    badgeColor: "bg-medical-accent-light text-medical-accent",
  },
  {
    label: "最近问诊",
    value: "急性上呼吸道感染",
    subValue: "2026-06-12 · 已完结",
  },
  {
    label: "待随访任务",
    value: "3",
    subValue: "1 项即将到期",
    valueColor: "text-medical-warning",
  },
];

const vitalsData = [
  { label: "血压", value: "128/82 mmHg" },
  { label: "心率", value: "72 bpm" },
  { label: "BMI", value: "22.4" },
  { label: "血红蛋白", value: "13.5 g/dL", valueColor: "text-medical-accent" },
];

const medications = [
  { name: "对乙酰氨基酚", dosage: "500mg · 每6小时一次" },
  { name: "布洛芬", dosage: "200mg · 必要时服用" },
];

const healthMemories = [
  { label: "慢性偏头痛史 (先兆型)", tag: "高置信度", tagColor: "bg-medical-primary-light text-medical-primary" },
  { label: "轻度青霉素过敏", tag: "医生已验证", tagColor: "bg-medical-warning-light text-medical-warning" },
  { label: "倾向于清晨预约", tag: "推断行为", tagColor: "bg-gray-100 text-gray-600" },
];

const followUps = [
  {
    title: "复查空腹血脂",
    due: "3天后到期",
    dueColor: "text-medical-warning",
    desc: "需空腹 8-12 小时 · 建议上午就诊",
    urgent: true,
  },
  {
    title: "内分泌科咨询",
    due: "2周后",
    desc: "评估血糖控制情况",
    urgent: false,
  },
  {
    title: "年度体检",
    due: "1个月后",
    desc: "全面体检套餐",
    urgent: false,
  },
];

const timelineData = [
  {
    title: "急性上呼吸道感染 AI 问诊",
    date: "2026-06-12",
    source: "MediNexus AI 问诊系统",
    status: "问诊已完成 · 生成诊断建议与用药方案",
    statusColor: "bg-medical-primary-light text-medical-primary",
    active: true,
  },
  {
    title: "综合代谢组图 (CMP)",
    date: "2023-10-15",
    source: "瑞金医院 · 检验科",
    file: "综合代谢组图报告.pdf",
    active: false,
  },
  {
    title: "年度体检",
    date: "2023-03-20",
    source: "华山医院 · 体检中心",
    file: "2023年度体检报告.pdf",
    active: false,
  },
];

export default function RecordsPage() {
  return (
    <AppShell stageLabel="健康档案中心" activePath="/records">
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-medical-primary-light flex items-center justify-center">
              <FileText className="w-5 h-5 text-medical-primary" />
            </div>
            <div>
              <h1 className="font-heading text-3xl font-bold text-medical-text-primary">
                健康档案
              </h1>
              <p className="text-medical-text-secondary text-sm mt-1">
                综合医疗史、AI 智能分析、随访计划及检查报告的统一管理中心。
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/upload-report"
              className="inline-flex items-center gap-2 px-4 py-2.5 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:bg-white transition-colors"
            >
              <Upload className="w-4 h-4" />
              上传报告
            </Link>
            <Link
              href="/consultation"
              className="inline-flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all"
            >
              <Plus className="w-4 h-4" />
              开始新问诊
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-4 gap-4"
        >
          {overviewStats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              className="glass-card rounded-2xl p-5 card-hover"
            >
              <div className="text-xs text-medical-text-muted mb-1">{stat.label}</div>
              <div className={`text-3xl font-bold ${stat.valueColor || "text-medical-text-primary"}`}>
                {stat.value}
                {stat.unit && (
                  <span className="text-base text-medical-text-muted font-normal ml-1">
                    {stat.unit}
                  </span>
                )}
              </div>
              {stat.progress !== undefined && (
                <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${stat.bgColor} rounded-full`}
                    style={{ width: `${stat.progress}%` }}
                  />
                </div>
              )}
              {stat.badge && (
                <span
                  className={`${stat.badgeColor} text-xs px-2 py-0.5 rounded-full mt-1 inline-block`}
                >
                  {stat.badge}
                </span>
              )}
              {stat.subValue && (
                <div className="text-xs text-medical-text-muted mt-1">{stat.subValue}</div>
              )}
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-12 gap-5">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-3 space-y-5"
          >
            <div className="glass-card rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-medical-primary-light flex items-center justify-center">
                  <Brain className="w-4 h-4 text-medical-primary" />
                </div>
                <h3 className="font-semibold text-medical-text-primary text-sm">
                  AI 健康记忆
                </h3>
              </div>
              <div className="space-y-3">
                {healthMemories.map((item, index) => (
                  <div key={index} className="flex justify-between items-start">
                    <span className="text-sm text-medical-text-primary">{item.label}</span>
                    <span
                      className={`${item.tagColor} text-xs px-2 py-0.5 rounded-md flex-shrink-0 ml-2`}
                    >
                      {item.tag}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5">
              <h3 className="font-semibold text-medical-text-primary text-sm mb-4">
                最新体征
              </h3>
              <div className="space-y-3">
                {vitalsData.map((vital, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-medical-text-secondary">{vital.label}</span>
                    <span
                      className={`text-sm font-medium ${vital.valueColor || "text-medical-text-primary"}`}
                    >
                      {vital.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5">
              <h3 className="font-semibold text-medical-text-primary text-sm mb-4">
                当前用药
              </h3>
              <div className="space-y-3">
                {medications.map((med, index) => (
                  <div key={index} className="bg-white/60 rounded-xl p-3">
                    <div className="flex items-center gap-2 text-sm font-medium text-medical-text-primary">
                      <Pill className="w-4 h-4 text-medical-primary" />
                      {med.name}
                    </div>
                    <div className="text-xs text-medical-text-muted mt-0.5 ml-6">
                      {med.dosage}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-6 space-y-5"
          >
            <div className="glass-card rounded-2xl p-5">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-medical-warning-light flex items-center justify-center">
                    <Calendar className="w-4 h-4 text-medical-warning" />
                  </div>
                  <h3 className="font-semibold text-medical-text-primary">随访计划</h3>
                </div>
                <Badge variant="warning">3 项待办</Badge>
              </div>
              <div className="space-y-3">
                {followUps.map((item, index) => (
                  <div
                    key={index}
                    className={`flex gap-3 items-start p-3 rounded-xl border ${
                      item.urgent
                        ? "bg-medical-warning-light/40 border-medical-warning/20"
                        : "bg-white/60 border-medical-border"
                    }`}
                  >
                    <div
                      className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                        item.urgent ? "bg-medical-warning" : "bg-medical-primary"
                      }`}
                    />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-medical-text-primary">
                          {item.title}
                        </span>
                        <span
                          className={`text-xs font-medium ${item.dueColor || "text-medical-text-muted"}`}
                        >
                          {item.due}
                        </span>
                      </div>
                      <div className="text-xs text-medical-text-muted mt-0.5">{item.desc}</div>
                    </div>
                    <button className="text-xs bg-white border border-medical-border rounded-lg px-3 py-1 hover:bg-gray-50 transition-colors flex-shrink-0">
                      预约
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5">
              <div className="flex justify-between items-center mb-5">
                <h3 className="font-semibold text-medical-text-primary">医疗时间线</h3>
                <Link
                  href="#"
                  className="text-sm text-medical-primary hover:text-medical-primary-dark transition-colors"
                >
                  查看全部 →
                </Link>
              </div>
              <div className="relative pl-8">
                <div className="absolute left-[11px] top-0 bottom-0 w-0.5 bg-gray-200" />
                {timelineData.map((item, index) => (
                  <div key={index} className="relative pb-5 last:pb-0">
                    <div
                      className={`absolute left-[-21px] top-1 w-4 h-4 rounded-full ring-4 flex items-center justify-center ${
                        item.active
                          ? "bg-medical-primary ring-medical-primary-light"
                          : "bg-gray-300 ring-gray-100"
                      }`}
                    >
                      {item.active && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                    </div>
                    <div className="flex justify-between items-start mb-1">
                      <div className="text-sm font-semibold text-medical-text-primary">
                        {item.title}
                      </div>
                      <span className="text-xs text-medical-text-muted">{item.date}</span>
                    </div>
                    <div className="text-xs text-medical-text-muted mb-2">{item.source}</div>
                    {item.status && (
                      <div
                        className={`${item.statusColor} rounded-xl p-3 text-xs flex items-center gap-2`}
                      >
                        <CheckCircle className="w-4 h-4" />
                        {item.status}
                      </div>
                    )}
                    {item.file && (
                      <div className="bg-white/60 rounded-xl p-3 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-medical-primary" />
                        <span className="text-xs text-medical-text-secondary">{item.file}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="col-span-3 space-y-5"
          >
            <div className="glass-card rounded-2xl p-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-medical-text-primary text-sm">最近记录</h3>
                <Link
                  href="#"
                  className="text-xs text-medical-primary hover:text-medical-primary-dark transition-colors"
                >
                  全部
                </Link>
              </div>
              <div className="space-y-3">
                {mockRecords.slice(0, 3).map((record) => (
                  <Link
                    key={record.id}
                    href={`/summary?session_id=${record.id}`}
                    className="block p-3 rounded-xl hover:bg-white/60 transition-colors group"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs px-2 py-0.5 rounded-md bg-medical-primary-light text-medical-primary">
                        {record.type}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-medical-text-primary mb-1 line-clamp-1">
                      {record.summary}
                    </div>
                    <div className="text-xs text-medical-text-muted flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      {record.date}
                    </div>
                  </Link>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-5">
              <h3 className="font-semibold text-medical-text-primary text-sm mb-4">
                快捷操作
              </h3>
              <div className="space-y-2">
                <Link
                  href="/consultation"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/60 transition-colors group"
                >
                  <div className="w-9 h-9 rounded-lg bg-medical-primary-light flex items-center justify-center">
                    <Activity className="w-4 h-4 text-medical-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-medical-text-primary">
                      开始新问诊
                    </div>
                    <div className="text-xs text-medical-text-muted">AI 智能导诊</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-medical-text-muted group-hover:text-medical-primary transition-colors" />
                </Link>
                <Link
                  href="/upload-report"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/60 transition-colors group"
                >
                  <div className="w-9 h-9 rounded-lg bg-medical-accent-light flex items-center justify-center">
                    <Upload className="w-4 h-4 text-medical-accent" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-medical-text-primary">
                      上传检查报告
                    </div>
                    <div className="text-xs text-medical-text-muted">AI 自动解析归档</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-medical-text-muted group-hover:text-medical-accent transition-colors" />
                </Link>
                <Link
                  href="/dashboard"
                  className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/60 transition-colors group"
                >
                  <div className="w-9 h-9 rounded-lg bg-medical-purple-light flex items-center justify-center">
                    <Heart className="w-4 h-4 text-medical-purple" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-medical-text-primary">
                      健康仪表盘
                    </div>
                    <div className="text-xs text-medical-text-muted">数字孪生全景视图</div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-medical-text-muted group-hover:text-medical-purple transition-colors" />
                </Link>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-xl font-bold text-medical-text-primary">
              全部就诊记录
            </h2>
            <div className="flex items-center gap-2">
              <select className="bg-white/60 rounded-xl border border-medical-border px-3 py-2 text-sm text-medical-text-secondary outline-none cursor-pointer focus:border-medical-primary transition-colors">
                <option>全部类型</option>
                <option>AI 智能问诊</option>
                <option>健康咨询</option>
                <option>检查报告</option>
              </select>
              <select className="bg-white/60 rounded-xl border border-medical-border px-3 py-2 text-sm text-medical-text-secondary outline-none cursor-pointer focus:border-medical-primary transition-colors">
                <option>全部时间</option>
                <option>最近一个月</option>
                <option>最近三个月</option>
                <option>最近一年</option>
              </select>
            </div>
          </div>

          <div className="space-y-3">
            {mockRecords.map((record, index) => (
              <motion.div
                key={record.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
              >
                <Link
                  href={`/summary?session_id=${record.id}`}
                  className="block glass-card rounded-2xl p-5 hover:shadow-medical-md hover:border-medical-primary/30 transition-all group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-medical-primary-light flex items-center justify-center">
                        <FileText className="w-6 h-6 text-medical-primary" />
                      </div>
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-semibold text-medical-text-primary">
                            {record.type}
                          </span>
                          <Badge variant={record.status === "completed" ? "success" : "warning"}>
                            {record.status === "completed" ? "已完成" : "进行中"}
                          </Badge>
                          <span className="text-xs text-medical-text-muted">
                            {record.department}
                          </span>
                        </div>
                        <p className="text-sm text-medical-text-secondary">{record.summary}</p>
                        <p className="text-xs text-medical-text-muted mt-1">
                          医生：{record.doctor}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1.5 text-xs text-medical-text-muted">
                        <Calendar className="w-3.5 h-3.5" />
                        {record.date}
                      </div>
                      <ArrowRight className="w-5 h-5 text-medical-text-muted group-hover:text-medical-primary transition-colors" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </AppShell>
  );
}
