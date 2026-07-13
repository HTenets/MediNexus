"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  User,
  Lock,
  Eye,
  EyeOff,
  ChevronRight,
  Shield,
  Database,
  Code,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { login, loading } = useAuth();
  const [role, setRole] = useState<"patient" | "doctor">("patient");
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    if (!email || !password) {
      setError("请输入邮箱和密码");
      return;
    }
    setError("");
    try {
      await login(email, password, role);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    }
  };

  return (
    <div className="min-h-screen flex">
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        className="hidden lg:flex flex-1 gradient-hero flex-col justify-center items-center p-[60px] text-white relative overflow-hidden"
      >
        <div className="absolute inset-0">
          <motion.div
            className="absolute top-20 left-20 w-72 h-72 bg-white/10 rounded-full blur-3xl"
            animate={{
              x: [0, 30, 0],
              y: [0, 30, 0],
            }}
            transition={{ duration: 8, repeat: Infinity }}
          />
          <motion.div
            className="absolute bottom-20 right-20 w-96 h-96 bg-white/10 rounded-full blur-3xl"
            animate={{
              x: [0, -30, 0],
              y: [0, -30, 0],
            }}
            transition={{ duration: 8, repeat: Infinity }}
          />
        </div>

        <div className="relative z-10 text-center mb-12">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="w-20 h-20 mx-auto rounded-2xl bg-white/20 flex items-center justify-center mb-6"
          >
            <span className="text-3xl font-bold">M</span>
          </motion.div>
          <h1 className="text-4xl font-bold mb-3">MediNexus</h1>
          <p className="text-lg text-white/80">AI 多智能体医疗诊断平台</p>
        </div>

        <div className="relative z-10 space-y-6 max-w-[400px] w-full">
          {[
            {
              icon: Shield,
              title: "多 Agent 协作诊断",
              desc: "Triage → Doctor → Review → Follow-up",
            },
            {
              icon: Database,
              title: "本地部署，数据不出设备",
              desc: "私有化部署保障数据安全",
            },
            {
              icon: Code,
              title: "完全开源，隐私可控",
              desc: "透明可审计的医疗AI平台",
            },
          ].map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.2 }}
              className="flex items-center gap-4 p-4 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                <feature.icon className="w-6 h-6" />
              </div>
              <div>
                <div className="text-base font-medium">{feature.title}</div>
                <div className="text-sm text-white/70">{feature.desc}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="flex-1 flex flex-col justify-center items-center p-10"
      >
        <div className="w-full max-w-[480px]">
          <Link
            href="/"
            className="flex items-center gap-2 mb-8 group"
          >
            <motion.div
              whileHover={{ scale: 1.1 }}
              className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-medical-primary"
            >
              M
            </motion.div>
            <span className="font-heading font-semibold text-medical-text-primary">
              MediNexus
            </span>
          </Link>

          <Card className="p-8 mb-6">
            <div className="flex mb-8 bg-gray-100 rounded-xl p-1">
              <button
                onClick={() => setActiveTab("login")}
                className={`flex-1 text-center py-3 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "login"
                    ? "bg-white text-medical-primary shadow-sm"
                    : "text-medical-text-muted hover:text-medical-text-secondary"
                }`}
              >
                登录
              </button>
              <button
                onClick={() => setActiveTab("register")}
                className={`flex-1 text-center py-3 rounded-lg text-sm font-medium transition-all ${
                  activeTab === "register"
                    ? "bg-white text-medical-primary shadow-sm"
                    : "text-medical-text-muted hover:text-medical-text-secondary"
                }`}
              >
                注册
              </button>
            </div>

            <div className="mb-6">
              <div className="text-sm text-medical-text-muted mb-3">选择角色</div>
              <div className="grid grid-cols-2 gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setRole("patient")}
                  className={`rounded-xl p-5 text-center transition-all ${
                    role === "patient"
                      ? "gradient-primary text-white shadow-medical-primary"
                      : "border-2 border-medical-border hover:border-medical-primary/50"
                  }`}
                >
                  <User className={`w-6 h-6 mx-auto mb-3 ${role === "patient" ? "text-white" : "text-medical-primary"}`} />
                  <div className={`text-sm font-medium ${role === "patient" ? "text-white" : "text-medical-text-primary"}`}>
                    我是患者
                  </div>
                  <div className={`text-xs mt-1 ${role === "patient" ? "text-white/80" : "text-medical-text-muted"}`}>
                    自助问诊
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setRole("doctor")}
                  className={`rounded-xl p-5 text-center transition-all ${
                    role === "doctor"
                      ? "gradient-primary text-white shadow-medical-primary"
                      : "border-2 border-medical-border hover:border-medical-primary/50"
                  }`}
                >
                  <Shield className={`w-6 h-6 mx-auto mb-3 ${role === "doctor" ? "text-white" : "text-medical-primary"}`} />
                  <div className={`text-sm font-medium ${role === "doctor" ? "text-white" : "text-medical-text-primary"}`}>
                    我是医生
                  </div>
                  <div className={`text-xs mt-1 ${role === "doctor" ? "text-white/80" : "text-medical-text-muted"}`}>
                    诊断辅助
                  </div>
                </motion.button>
              </div>
            </div>

            <form className="space-y-5">
              <Input
                label="邮箱 / 手机号"
                placeholder="请输入邮箱或手机号"
                leftIcon={<User className="w-4 h-4" />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="block text-sm font-medium text-medical-text-primary">
                    密码
                  </label>
                  <a href="#" className="text-xs text-medical-primary hover:underline">
                    忘记密码?
                  </a>
                </div>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-medical-text-muted">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="请输入密码"
                    className="w-full rounded-xl border border-medical-border px-11 py-3 text-sm outline-none transition-all input-focus"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-sm text-medical-danger bg-medical-danger-light/30 px-4 py-2 rounded-lg"
                >
                  {error}
                </motion.div>
              )}

              <motion.button
                whileHover={!loading ? { scale: 1.02 } : {}}
                whileTap={!loading ? { scale: 0.98 } : {}}
                type="button"
                onClick={handleLogin}
                disabled={loading}
                className="w-full gradient-primary text-white rounded-xl py-3.5 text-sm font-medium shadow-medical-primary hover:shadow-glow transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    登录中...
                  </>
                ) : (
                  <>
                    {activeTab === "login" ? "登录" : "注册"}
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </motion.button>
            </form>

            <div className="flex items-center gap-3 my-6">
              <div className="flex-1 h-px bg-medical-border" />
              <span className="text-xs text-medical-text-muted">或</span>
              <div className="flex-1 h-px bg-medical-border" />
            </div>

            <Link
              href="/consultation"
              className="block text-center text-sm text-medical-primary hover:text-medical-primary-dark hover:underline flex items-center justify-center gap-1"
            >
              跳过登录，直接问诊
              <ChevronRight className="w-4 h-4" />
            </Link>
          </Card>
        </div>
      </motion.div>
    </div>
  );
}