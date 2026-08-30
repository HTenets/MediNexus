"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input, Textarea } from "@/components/ui/Input";
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
  RefreshCw,
  Trash2,
  X,
} from "lucide-react";
import {
  listPatients,
  createPatient,
  deletePatient,
  ApiError,
  Patient,
  PatientCreate,
  PatientListResponse,
} from "@/lib/api";

interface DisplayPatient {
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

function mapPatientToDisplay(patient: Patient): DisplayPatient {
  const patientId = patient.id.toString();
  const last4Digits = patientId.slice(-4).padStart(4, "0");
  
  const stage = patient.status === "active" ? "进行中" : "已完成";
  
  const symptomsParts: string[] = [];
  if (patient.medical_history && patient.medical_history.length > 0) {
    symptomsParts.push(...patient.medical_history);
  }
  if (patient.allergies && patient.allergies.length > 0) {
    symptomsParts.push(`过敏史: ${patient.allergies.join(", ")}`);
  }
  const symptoms = symptomsParts.length > 0 ? symptomsParts.join("；") : "暂无症状记录";
  
  const department = patient.medical_history && patient.medical_history.length > 0
    ? inferDepartment(patient.medical_history)
    : "全科";
  
  return {
    id: patient.id,
    name: patient.name,
    patient_id: `#${last4Digits}`,
    avatar: patient.name.charAt(0),
    status: patient.status,
    stage,
    symptoms,
    last_visit: formatLastVisit(patient.last_visit),
    department,
  };
}

function inferDepartment(medicalHistory: string[]): string {
  const deptKeywords: Record<string, string> = {
    "头痛": "神经内科",
    "发热": "内科",
    "咳嗽": "呼吸科",
    "胸闷": "呼吸科",
    "气短": "呼吸科",
    "皮肤": "皮肤科",
    "瘙痒": "皮肤科",
    "红疹": "皮肤科",
    "胃痛": "消化科",
    "反酸": "消化科",
    "嗳气": "消化科",
    "血压": "心血管",
    "高血压": "心血管",
    "失眠": "神经科",
    "焦虑": "神经科",
    "心悸": "心血管",
    "恶心": "消化科",
    "呕吐": "消化科",
  };
  
  for (const record of medicalHistory) {
    for (const [keyword, dept] of Object.entries(deptKeywords)) {
      if (record.includes(keyword)) {
        return dept;
      }
    }
  }
  return "全科";
}

function formatLastVisit(dateStr?: string): string {
  if (!dateStr) return "未知";
  
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 1) return "刚刚";
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  
  return date.toLocaleDateString("zh-CN");
}

const statsData = [
  { label: "总患者数", value: "--", icon: Users, color: "text-medical-primary", bg: "bg-medical-primary-light" },
  { label: "待处理", value: "--", icon: Clock, color: "text-medical-warning", bg: "bg-medical-warning-light" },
  { label: "本月新增", value: "--", icon: Activity, color: "text-medical-accent", bg: "bg-medical-accent-light" },
  { label: "紧急标记", value: "0", icon: AlertTriangle, color: "text-medical-danger", bg: "bg-medical-danger-light" },
];

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [deptFilter, setDeptFilter] = useState("all");
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletingPatientId, setDeletingPatientId] = useState<string | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  
  const [formData, setFormData] = useState<PatientCreate>({
    name: "",
    gender: "",
    dob: "",
    phone: "",
    id_number: "",
    address: "",
    allergies: [],
    medical_history: [],
  });
  const [formError, setFormError] = useState<string>("");

  const fetchPatients = useCallback(async (search?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response: PatientListResponse = await listPatients(search, 1, 100);
      setPatients(response.items);
      setError(null);
    } catch (err) {
      setError(err as ApiError);
      setPatients([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      fetchPatients(searchQuery || undefined);
    }, 500);
    return () => clearTimeout(debounceTimer);
  }, [searchQuery, fetchPatients]);

  const handleRefresh = () => {
    fetchPatients(searchQuery || undefined);
  };

  const handleCreatePatient = async () => {
    if (!formData.name.trim()) {
      setFormError("请输入患者姓名");
      return;
    }
    setFormError("");
    setCreateLoading(true);
    try {
      await createPatient(formData);
      setIsCreateModalOpen(false);
      setFormData({
        name: "",
        gender: "",
        dob: "",
        phone: "",
        id_number: "",
        address: "",
        allergies: [],
        medical_history: [],
      });
      fetchPatients();
    } catch (err) {
      setFormError((err as ApiError).message);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleDeletePatient = async () => {
    if (!deletingPatientId) return;
    setDeleteLoading(true);
    try {
      await deletePatient(deletingPatientId);
      setIsDeleteModalOpen(false);
      setDeletingPatientId(null);
      fetchPatients();
    } catch (err) {
      console.error("删除失败:", err);
    } finally {
      setDeleteLoading(false);
    }
  };

  const confirmDelete = (patientId: string) => {
    setDeletingPatientId(patientId);
    setIsDeleteModalOpen(true);
  };

  const displayPatients = patients.map(mapPatientToDisplay);

  const filteredPatients = displayPatients.filter((p) => {
    const matchStatus = statusFilter === "all" || p.status === statusFilter;
    const matchDept = deptFilter === "all" || p.department === deptFilter;
    return matchStatus && matchDept;
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
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              刷新
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsCreateModalOpen(true)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              新建患者
            </Button>
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
                      href={`/records?patient_id=${patient.id}`}
                      className="w-8 h-8 rounded-lg hover:bg-medical-primary-light flex items-center justify-center text-medical-text-muted hover:text-medical-primary transition-colors"
                      title="查看该患者的病历"
                    >
                      <FileText className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => confirmDelete(patient.id)}
                      className="w-8 h-8 rounded-lg hover:bg-medical-danger-light flex items-center justify-center text-medical-text-muted hover:text-medical-danger transition-colors"
                      title="删除患者"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                    <button className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center text-medical-text-muted hover:text-medical-text-secondary transition-colors">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-2xl p-8 text-center"
          >
            <div className="w-16 h-16 rounded-full bg-medical-danger-light flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-medical-danger" />
            </div>
            <h3 className="text-lg font-semibold text-medical-text-primary mb-2">加载失败</h3>
            <p className="text-medical-text-secondary mb-4">{error.message}</p>
            <Button onClick={handleRefresh} leftIcon={<RefreshCw className="w-4 h-4" />}>
              重试
            </Button>
          </motion.div>
        )}
      </div>

      <Modal isOpen={isCreateModalOpen} onClose={() => { setIsCreateModalOpen(false); setFormError(""); }} title="新建患者" size="lg">
        <div className="space-y-4">
          {formError && <p className="text-sm text-medical-danger">{formError}</p>}
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="姓名"
              placeholder="请输入患者姓名"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <Input
              label="性别"
              placeholder="男/女"
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="出生日期"
              type="date"
              value={formData.dob as string}
              onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
            />
            <Input
              label="联系电话"
              placeholder="请输入联系电话"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>
          <Input
            label="身份证号"
            placeholder="请输入身份证号"
            value={formData.id_number}
            onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
          />
          <Input
            label="地址"
            placeholder="请输入住址"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          />
          <Textarea
            label="过敏史（用逗号分隔）"
            placeholder="如：青霉素、海鲜"
            value={(formData.allergies || []).join(", ")}
            onChange={(e) => setFormData({ ...formData, allergies: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })}
          />
          <Textarea
            label="既往病史"
            placeholder="请描述患者既往病史"
            value={(formData.medical_history || []).join("；")}
            onChange={(e) => setFormData({ ...formData, medical_history: e.target.value.split("；").map(s => s.trim()).filter(Boolean) })}
          />
          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={() => { setIsCreateModalOpen(false); setFormError(""); }} className="flex-1">
              取消
            </Button>
            <Button variant="primary" onClick={handleCreatePatient} loading={createLoading} className="flex-1">
              创建患者
            </Button>
          </div>
        </div>
      </Modal>

      <Modal isOpen={isDeleteModalOpen} onClose={() => { setIsDeleteModalOpen(false); setDeletingPatientId(null); }} title="确认删除" size="sm">
        <div className="space-y-4">
          <div className="flex items-center gap-3 text-medical-danger">
            <AlertTriangle className="w-5 h-5" />
            <p>确定要删除该患者吗？此操作无法撤销。</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => { setIsDeleteModalOpen(false); setDeletingPatientId(null); }} className="flex-1">
              取消
            </Button>
            <Button variant="danger" onClick={handleDeletePatient} loading={deleteLoading} className="flex-1">
              删除
            </Button>
          </div>
        </div>
      </Modal>
    </AppShell>
  );
}
