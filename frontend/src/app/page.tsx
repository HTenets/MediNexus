"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { NavBar } from "@/components/layout/NavBar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  Stethoscope,
  MessageCircle,
  FileText,
  ArrowRight,
  Shield,
  Brain,
  HeartPulse,
} from "lucide-react";

const features = [
  {
    icon: Stethoscope,
    title: "多科室智能导诊",
    description: "AI 智能分析症状，精确推荐就诊科室，缩短就医路径",
    gradient: "from-medical-primary to-blue-600",
    bgLight: "bg-medical-primary-light",
  },
  {
    icon: MessageCircle,
    title: "流式对话问诊",
    description: "实时流式输出，对话体验流畅自然，如同面对面问诊",
    gradient: "from-medical-accent to-green-600",
    bgLight: "bg-medical-accent-light",
  },
  {
    icon: FileText,
    title: "健康记忆追踪",
    description: "跨会话追踪健康档案，复诊无缝衔接，数据安全加密",
    gradient: "from-medical-purple to-violet-600",
    bgLight: "bg-medical-purple-light",
  },
];

const stats = [
  { value: "98%", label: "诊断准确率" },
  { value: "50+", label: "覆盖科室" },
  { value: "10万+", label: "服务患者" },
  { value: "24/7", label: "全天候服务" },
];

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          className="absolute top-0 left-1/4 w-96 h-96 bg-medical-primary/10 rounded-full blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-medical-accent/10 rounded-full blur-3xl"
          animate={{
            x: [0, -50, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-medical-purple/5 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      <NavBar />

      <main className="relative z-10">
        <section className="py-20 px-4">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="mb-8"
            >
              <Badge variant="primary" className="px-4 py-2 text-sm">
                <motion.span
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="inline-block w-2 h-2 bg-medical-accent rounded-full mr-2"
                />
                开源 AI 医疗诊断平台 v0.1.0
              </Badge>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="font-heading text-5xl md:text-6xl lg:text-7xl font-bold text-medical-text-primary mb-6"
            >
              智能导诊
              <br />
              <span className="text-gradient">精准诊断</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-lg md:text-xl text-medical-text-secondary max-w-2xl mx-auto mb-10"
            >
              MediNexus 基于多智能体协作，为您提供从症状分析到就诊建议的智能导诊服务。
              AI 驱动的全流程问诊体验，让健康触手可及。
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link href="/consultation">
                <Button size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                  开始智能问诊
                </Button>
              </Link>
              <Button variant="outline" size="lg">
                了解更多
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 1 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16"
            >
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-3xl md:text-4xl font-bold text-gradient mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-medical-text-secondary">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        <section id="features" className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-16"
            >
              <h2 className="font-heading text-3xl md:text-4xl font-bold text-medical-text-primary mb-4">
                核心功能
              </h2>
              <p className="text-medical-text-secondary max-w-2xl mx-auto">
                基于多智能体协作的智能问诊系统，为您提供专业、高效的医疗健康服务
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  whileHover={{ y: -8 }}
                >
                  <Card className="h-full p-8 card-hover">
                    <div
                      className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-6 shadow-lg`}
                    >
                      <feature.icon className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="font-heading text-xl font-bold text-medical-text-primary mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-medical-text-secondary leading-relaxed">
                      {feature.description}
                    </p>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="glass-card rounded-3xl p-10 md:p-14 text-center"
            >
              <div className="w-16 h-16 gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-medical-primary">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <h2 className="font-heading text-2xl md:text-3xl font-bold text-medical-text-primary mb-4">
                多智能体协作诊断
              </h2>
              <p className="text-medical-text-secondary mb-8">
                Triage → Doctor → Review → Follow-up，四步闭环，确保诊断准确可靠
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Badge variant="primary">导诊护士</Badge>
                <Badge variant="success">主治医生</Badge>
                <Badge variant="secondary">审方药师</Badge>
                <Badge variant="warning">随访助手</Badge>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="text-center mb-16"
            >
              <h2 className="font-heading text-3xl md:text-4xl font-bold text-medical-text-primary mb-4">
                为什么选择我们
              </h2>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  icon: Shield,
                  title: "数据安全",
                  description: "本地部署，数据不出设备，私有化部署保障隐私安全",
                },
                {
                  icon: HeartPulse,
                  title: "专业可靠",
                  description: "基于权威医学知识库，AI 诊断符合临床指南",
                },
                {
                  icon: Brain,
                  title: "开源透明",
                  description: "完全开源，透明可审计，持续迭代优化",
                },
              ].map((item, index) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                >
                  <div className="flex items-start gap-4 p-6 rounded-2xl hover:bg-white/50 transition-colors">
                    <div className="w-12 h-12 gradient-accent rounded-xl flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-medical-text-primary mb-2">
                        {item.title}
                      </h3>
                      <p className="text-sm text-medical-text-secondary">
                        {item.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="gradient-hero rounded-3xl p-10 md:p-16 text-center text-white"
            >
              <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">
                准备好开始您的健康之旅了吗？
              </h2>
              <p className="text-white/80 mb-8 max-w-xl mx-auto">
                立即体验 AI 智能问诊，让专业医疗服务触手可及
              </p>
              <Link href="/consultation">
                <Button
                  size="lg"
                  rightIcon={<ArrowRight className="w-5 h-5" />}
                  className="bg-white text-medical-primary hover:bg-white/90 shadow-lg"
                >
                  开始问诊
                </Button>
              </Link>
            </motion.div>
          </div>
        </section>
      </main>

      <footer className="py-8 px-4 text-center text-sm text-medical-text-muted">
        <p>MediNexus / 医枢 — 开源多智能体医疗诊断平台</p>
        <p className="mt-2">免责声明：AI 诊断仅供参考，不构成医疗建议</p>
      </footer>
    </div>
  );
}
