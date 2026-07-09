"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import {
  User,
  Search,
  Plus,
  Calendar,
  ChevronRight,
  Users,
  Clock,
  Activity,
  AlertTriangle,
  Eye,
  MoreHorizontal,
  Download,
  Filter,
  FileText,
} from "lucide-react";

interface Patient {
  id: string;
  name: string;
  patient_id: string;
  avatar: string;
  status: string;
  stage: string;
  symptoms: string;
  last_visit: string;
  urgency?: string;
  department?: string;
}

const mockPatients: Patient[] = [
  {
    id: "1",
    name: "张三",
    patient_id: "#4092",
    avatar: "张",
    status: "active",
    stage: "评估复核",
    symptoms: "头痛、发热、心悸，持续3天，伴有恶心呕吐",
    last_visit: "10分钟前",
    urgency: "紧急",
    department: "内科",
  },
  {
    id: "2",
    name: "李四",
    patient_id: "#3871",
    avatar: "李",
    status: "active",
    stage: "诊断中",
    symptoms: "咳嗽、胸闷、气短，活动后加重",
    last_visit: "25分钟前",
    department: "呼吸科",
  },
  {
    id: "3",
    name: "王五",
    patient_id: "#3562",
    avatar: "王",
    status: "active",
    stage: "待分诊",
    symptoms: "皮肤瘙痒、红疹，散布于躯干和四肢",
    last_visit: "1小时前",
    department: "皮肤科",
  },
  {
    id: "4",
    name: "赵六",
    patient_id: "#3245",
    avatar: "赵",
    status: "completed",
    stage: "已完成",
    symptoms: "胃痛、反酸、嗳气，进食后加重",
    last_visit: "2小时前",
    department: "消化科",
  },
  {
    id: "5",
    name: "孙七",
    patient_id: "#2980",
    avatar: "孙",
    status: "active",
    stage: "待复核",
    symptoms: "头晕、血压偏高，既往有高血压病史",
    last_visit: "3小时前",
    urgency: "紧急",
    department: "心血管",
  },
  {
    id: "6",
    name: "周八",
    patient_id: "#2756",
    avatar: "周",
    status: "completed",
    stage: "已完成",
    symptoms: "失眠、焦虑、注意力不集中",
    last_visit: "昨天",
    department: "神经科",
  },
];

const statsData = [
  { label: "总患者数", value: "128", icon: Users, color: "text-medical-primary", bg: "bg-medical-primary-light" },
  { label: "待处理", value: "12", icon: Clock, color: "text-medical-warning", bg: "bg-medical-warning-light" },
  { label: "本月新增", value: "86", icon: Activity, color: "text-medical-accent", bg: "bg-medical-accent-light" },
  { label: "紧急标记", value: "3", icon: AlertTriangle, color: "text-medical-danger", bg: "bg-medical-danger-light" },
];

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [deptFilter, setDeptFilter] = useState("all");

  useEffect(() => {
    const timer = setTimeout(() => {
      setPatients(mockPatients);
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  const filteredPatients = patients.filter((p) => {
    const matchSearch =
      p.name.includes(searchQuery) ||
      p.patient_id.includes(searchQuery) ||
      p.symptoms.includes(searchQuery);
    const matchStatus = statusFilter === "all" || p.status === statusFilter;
    const matchDept = deptFilter === "all" || p.department === deptFilter;
    return matchSearch && matchStatus && matchDept;
  });

  const getStageColor = (stage: string) => {
    switch (stage) {
      case "待分诊":
        return "bg-medical-warning-light text-medical-warning";
      case "诊断中":
        return "bg-medical-primary-light text-medical-primary";
      case "待复核":
        return "bg-purple-100 text-purple-600";
      case "评估复核":
        return "bg-medical-primary-light text-medical-primary";
      case "已完成":
        return "bg-medical-accent-light text-medical-accent";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  return (
    <AppShell stageLabel="患者管理" activePath="/patients">
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="font-heading text-3xl font-bold text-medical-text-primary mb-2">
              患者管理
            </h1>
            <p className="text-medical-text-secondary">
              管理您的患者队列，查看问诊状态与历史记录。
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/upload-report"
              className="inline-flex items-center gap-2 px-4 py-2.5 border border-medical-border rounded-xl text-sm text-medical-text-secondary hover:bg-white transition-colors"
            >
              <Download className="w-4 h-4" />
              导出列表
            </Link>
            <Link
              href="/consultation"
              className="inline-flex items-center gap-2 px-5 py-2.5 gradient-primary text-white rounded-xl text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all"
            >
              <Plus className="w-4 h-4" />
              新建问诊
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-4 gap-4"
        >
          {statsData.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              whileHover={{ y: -4 }}
              className="glass-card rounded-2xl p-5 flex items-center gap-4 card-hover"
            >
              <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center flex-shrink-0`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold text-medical-text-primary">{stat.value}</div>
                <div className="text-sm text-medical-text-muted">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card rounded-2xl p-4"
        >
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex-1 min-w-[240px] flex items-center gap-2 bg-white/60 rounded-xl border border-medical-border px-4 py-2.5">
              <Search className="w-4 h-4 text-medical-text-muted" />
              <input
                type="text"
                placeholder="搜索患者姓名、ID、症状..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent outline-none text-sm w-full text-medical-text-primary placeholder:text-medical-text-muted"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-white/60 rounded-xl border border-medical-border px-3 py-2.5 text-sm text-medical-text-secondary outline-none cursor-pointer focus:border-medical-primary transition-colors"
            >
              <option value="all">全部状态</option>
              <option value="active">进行中</option>
              <option value="completed">已完成</option>
            </select>
            <select
              value={deptFilter}
              onChange={(e) => setDeptFilter(e.target.value)}
              className="bg-white/60 rounded-xl border border-medical-border px-3 py-2.5 text-sm text-medical-text-secondary outline-none cursor-pointer focus:border-medical-primary transition-colors"
            >
              <option value="all">全部科室</option>
              <option value="内科">内科</option>
              <option value="呼吸科">呼吸科</option>
              <option value="皮肤科">皮肤科</option>
              <option value="消化科">消化科</option>
              <option value="心血管">心血管</option>
              <option value="神经科">神经科</option>
            </select>
            <button className="bg-white/60 rounded-xl border border-medical-border px-3 py-2.5 text-sm text-medical-text-secondary flex items-center gap-1.5 hover:bg-white transition-colors">
              <Filter className="w-4 h-4" />
              更多筛选
            </button>
          </div>
        </motion.div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex gap-1.5">
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
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="glass-card rounded-2xl overflow-hidden"
          >
            <div className="border-b border-medical-border bg-medical-sidebar/50">
              <div className="grid grid-cols-12 gap-4 px-6 py-3 text-xs text-medical-text-muted font-medium uppercase tracking-wider">
                <div className="col-span-3">患者信息</div>
                <div className="col-span-2">当前阶段</div>
                <div className="col-span-3">症状摘要</div>
                <div className="col-span-2">更新时间</div>
                <div className="col-span-2 text-right">操作</div>
              </div>
            </div>
            <div className="divide-y divide-medical-border">
              {filteredPatients.map((patient, index) => (
                <motion.div
                  key={patient.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-white/50 transition-colors cursor-pointer group"
                >
                  <div className="col-span-3 flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-medical-primary-light flex items-center justify-center text-sm font-medium text-medical-primary flex-shrink-0">
                      {patient.avatar}
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-medical-text-primary">
                        {patient.name}
                      </div>
                      <div className="text-xs text-medical-text-muted font-mono">
                        {patient.patient_id}
                      </div>
                      {patient.urgency && (
                        <div className="flex gap-1 mt-0.5">
                          <Badge variant="danger" className="px-2 py-0.5 text-[10px]">
                            {patient.urgency}
                          </Badge>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="col-span-2">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${getStageColor(
                        patient.stage
                      )}`}
                    >
                      {patient.status === "active" && (
                        <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
                      )}
                      {patient.stage}
                    </span>
                  </div>
                  <div className="col-span-3 text-sm text-medical-text-secondary truncate">
                    {patient.symptoms}
                  </div>
                  <div className="col-span-2 flex items-center gap-1.5 text-xs text-medical-text-muted">
                    <Calendar className="w-3.5 h-3.5" />
                    {patient.last_visit}
                  </div>
                  <div className="col-span-2 flex justify-end gap-2">
                    <Link
                      href={`/consultation?patient_id=${patient.id}`}
                      className="w-8 h-8 rounded-lg hover:bg-medical-primary-light flex items-center justify-center text-medical-text-muted hover:text-medical-primary transition-colors"
                      title="查看详情"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                    <Link
                      href={`/summary?session_id=${patient.id}`}
                      className="w-8 h-8 rounded-lg hover:bg-medical-primary-light flex items-center justify-center text-medical-text-muted hover:text-medical-primary transition-colors"
                      title="查看报告"
                    >
                      <FileText className="w-4 h-4" />
                    </Link>
                    <button className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-medical-text-muted hover:text-medical-text-secondary transition-colors">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
