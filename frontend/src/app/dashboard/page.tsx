"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
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
  RefreshCw,
  XCircle,
  FileText,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { usePatientProfile } from "@/hooks/usePatient";
import { listRecords, ApiError } from "@/lib/api";

interface DashboardData {
  vitals: Record<string, string>;
  risks: string[];
  ai_suggestions: string[];
  record_count: number;
  last_visit: string | null;
}

const vitalsConfig = {
  heart: { label: "心率", unit: "bpm", icon: Heart, color: "text-red-500", bg: "bg-red-50" },
  blood: { label: "血压", unit: "mmHg", icon: Gauge, color: "text-blue-500", bg: "bg-blue-50" },
  oxygen: { label: "血氧", unit: "%", icon: Activity, color: "text-green-500", bg: "bg-green-50" },
  temperature: { label: "体温", unit: "°C", icon: Thermometer, color: "text-orange-500", bg: "bg-orange-50" },
};

function extractVitalsFromRecords(records: string[]): Record<string, string> {
  const vitals: Record<string, string> = {
    心率: "--",
    血压: "--",
    血氧: "--",
    体温: "--",
  };

  records.forEach((record) => {
    const heartRateMatch = record.match(/心率[：:]\s*(\d+)/);
    if (heartRateMatch) vitals.心率 = heartRateMatch[1];

    const bloodPressureMatch = record.match(/血压[：:]\s*(\d+\/\d+)/);
    if (bloodPressureMatch) vitals.血压 = bloodPressureMatch[1];

    const oxygenMatch = record.match(/血氧[：:]\s*(\d+)/);
    if (oxygenMatch) vitals.血氧 = oxygenMatch[1];

    const temperatureMatch = record.match(/体温[：:]\s*([\d.]+)/);
    if (temperatureMatch) vitals.体温 = temperatureMatch[1];
  });

  return vitals;
}

function extractRisksFromRecords(records: string[], medicalHistory: string[]): string[] {
  const risks: string[] = [];
  const riskKeywords = ["高血压", "糖尿病", "哮喘", "冠心病", "肿瘤", "脑梗", "心梗", "风险"];

  records.forEach((record) => {
    riskKeywords.forEach((keyword) => {
      if (record.includes(keyword) && !risks.includes(keyword)) {
        risks.push(`${keyword}风险`);
      }
    });
  });

  medicalHistory.forEach((history) => {
    riskKeywords.forEach((keyword) => {
      if (history.includes(keyword) && !risks.includes(keyword)) {
        risks.push(`${keyword}既往史`);
      }
    });
  });

  return risks.length > 0 ? risks : ["暂无风险数据"];
}

function extractSuggestionsFromPlans(plans: string[]): string[] {
  const suggestions: string[] = [];
  const suggestionPatterns = [
    { regex: /服药|用药|药物/, text: "按时服药" },
    { regex: /复查|随访|复诊/, text: "定期复查" },
    { regex: /锻炼|运动/, text: "适量运动" },
    { regex: /饮食|忌口|清淡/, text: "注意饮食" },
    { regex: /休息|睡眠/, text: "保证休息" },
  ];

  plans.forEach((plan) => {
    suggestionPatterns.forEach((pattern) => {
      if (pattern.regex.test(plan) && !suggestions.includes(pattern.text)) {
        suggestions.push(pattern.text);
      }
    });
  });

  if (plans.length > 0 && suggestions.length === 0) {
    suggestions.push("遵医嘱治疗");
  }

  return suggestions.length > 0 ? suggestions : ["暂无建议"];
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { patient, loading: profileLoading, error: profileError, reload } = usePatientProfile(user?.name);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!patient) return;
    let cancelled = false;

    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);

      try {
        const recordsResponse = await listRecords(patient.id);

        const records = recordsResponse.records || [];
        const allRecordTexts = records.flatMap((r) => [r.subjective, r.objective, r.assessment, r.plan, r.diagnosis]);
        const plans = records.map((r) => r.plan).filter((p) => p);

        if (cancelled) return;
        setData({
          vitals: extractVitalsFromRecords(allRecordTexts),
          risks: extractRisksFromRecords(allRecordTexts, patient.medical_history || []),
          ai_suggestions: extractSuggestionsFromPlans(plans),
          record_count: records.length,
          last_visit: records[0]?.date || null,
        });
      } catch (err) {
        if (!cancelled) setError(err as ApiError);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadDashboardData();
    return () => {
      cancelled = true;
    };
  }, [patient]);

  const failure: string | null = profileError || error?.message || null;

  if (loading || profileLoading) {
    return (
      <AppShell stageLabel="控制台" activePath="/dashboard">
        <div className="flex items-center justify-center h-96">
          <LoadingState text="加载健康数据..." />
        </div>
      </AppShell>
    );
  }

  if (failure) {
    return (
      <AppShell stageLabel="控制台" activePath="/dashboard">
        <div className="flex flex-col items-center justify-center h-96 space-y-4">
          <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
          <div className="text-center">
            <h2 className="text-xl font-semibold text-medical-text-primary mb-2">
              数据加载失败
            </h2>
            <p className="text-medical-text-secondary mb-4">
              {failure || "网络连接异常，请稍后重试"}
            </p>
            <Button onClick={reload} className="gap-2">
              <RefreshCw className="w-4 h-4" />
              刷新重试
            </Button>
          </div>
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
          <div className="flex items-center gap-3">
            <Badge variant="success" className="px-4 py-2 text-sm">
              <motion.span
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="inline-block w-2 h-2 bg-medical-accent rounded-full mr-2"
              />
              实时同步
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={reload}
              className="gap-2"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              刷新
            </Button>
          </div>
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
                  {patient?.age ?? "--"}
                  <span className="text-xl text-medical-text-muted font-normal ml-1">岁</span>
                </motion.div>
                <div className="text-medical-accent text-sm font-medium flex items-center justify-center gap-2">
                  <Activity className="w-4 h-4" />
                  档案年龄
                </div>
                <div className="text-xs text-medical-text-muted mt-2">
                  {patient?.gender ? `${patient.gender} · ` : ""}
                  {patient?.name || "本人"}
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
              <CardHeader title="过敏与既往史" />
              <CardContent className="space-y-3">
                {[
                  { label: "过敏史", items: patient?.allergies || [] },
                  { label: "既往病史", items: patient?.medical_history || [] },
                ].map((group, groupIndex) => (
                  <div key={group.label} className="space-y-2">
                    <div className="text-xs font-medium text-medical-text-muted">{group.label}</div>
                    {group.items.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {group.items.map((item, index) => (
                          <motion.span
                            key={item}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.6 + groupIndex * 0.1 + index * 0.05 }}
                            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-50 text-sm text-medical-text-secondary"
                          >
                            <Shield className="w-3.5 h-3.5 text-medical-text-muted" />
                            {item}
                          </motion.span>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-medical-text-muted">暂无记录，可在个人档案中补充</div>
                    )}
                  </div>
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
            { title: "病历总数", value: String(data?.record_count ?? 0), icon: FileText, color: "text-medical-accent" },
            {
              title: "最近就诊",
              value: data?.last_visit ? data.last_visit.slice(0, 10) : "暂无",
              icon: Clock,
              color: "text-medical-purple",
            },
            { title: "风险关注项", value: String(data?.risks?.length ?? 0), icon: AlertTriangle, color: "text-medical-primary" },
            { title: "随访建议", value: String(data?.ai_suggestions?.length ?? 0), icon: Heart, color: "text-red-500" },
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
                <Badge variant="primary">来自健康档案</Badge>
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
