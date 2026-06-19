"use client";

import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex flex-1 bg-medical-primary flex-col justify-center items-center p-[60px] text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>
        <div className="relative z-10 text-center">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-white/20 flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <h1 className="text-3xl font-bold mb-2">MediNexus</h1>
          <p className="text-lg text-white/80">AI 多智能体医疗诊断平台</p>
        </div>
        <div className="relative z-10 mt-12 space-y-6 max-w-[360px]">
          {[
            { title: "多 Agent 协作诊断", desc: "Triage → Doctor → Review → Follow-up" },
            { title: "本地部署，数据不出设备", desc: "私有化部署保障数据安全" },
            { title: "完全开源，隐私可控", desc: "透明可审计的医疗AI平台" },
          ].map(f => (
            <div key={f.title} className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/></svg>
              </div>
              <div><div className="text-base font-medium">{f.title}</div><div className="text-sm text-white/70">{f.desc}</div></div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center items-center p-10">
        <div className="w-full max-w-[440px] bg-white rounded-2xl shadow-medical-lg p-10">
          <div className="flex mb-8 bg-gray-100 rounded-xl p-1">
            <button className="flex-1 text-center py-2.5 rounded-lg text-sm font-medium bg-white text-medical-primary shadow-sm">登录</button>
            <button className="flex-1 text-center py-2.5 rounded-lg text-sm text-medical-text-muted">注册</button>
          </div>

          <div className="mb-6">
            <div className="text-sm text-medical-text-muted mb-2">选择角色</div>
            <div className="grid grid-cols-2 gap-3">
              <div className="border border-medical-primary bg-medical-primary-light rounded-xl p-4 text-center cursor-pointer">
                <svg className="w-6 h-6 mx-auto text-medical-primary mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                <div className="text-sm font-medium">我是患者</div>
                <div className="text-xs text-medical-text-muted mt-0.5">自助问诊</div>
              </div>
              <div className="border border-medical-border rounded-xl p-4 text-center cursor-pointer hover:border-medical-primary/50 transition-all">
                <svg className="w-6 h-6 mx-auto text-medical-text-muted mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/></svg>
                <div className="text-sm font-medium">我是医生</div>
                <div className="text-xs text-medical-text-muted mt-0.5">诊断辅助</div>
              </div>
            </div>
          </div>

          <form className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-medical-text-primary mb-1.5">邮箱 / 手机号</label>
              <input type="text" placeholder="请输入邮箱或手机号" className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm focus:ring-2 focus:ring-medical-primary focus:border-medical-primary outline-none transition-all" />
            </div>
            <div>
              <div className="flex justify-between mb-1.5">
                <label className="block text-sm font-medium text-medical-text-primary">密码</label>
                <a href="#" className="text-xs text-medical-primary hover:underline">忘记密码?</a>
              </div>
              <input type="password" placeholder="请输入密码" className="w-full rounded-xl border border-medical-border px-4 py-3 text-sm focus:ring-2 focus:ring-medical-primary focus:border-medical-primary outline-none transition-all" />
            </div>
            <button type="button" className="w-full bg-medical-primary text-white rounded-xl py-3 text-sm font-medium shadow-medical-primary hover:bg-medical-primary-hover transition-all active:scale-[0.98]">登录</button>
          </form>

          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-medical-border"></div><span className="text-xs text-medical-text-muted">或</span><div className="flex-1 h-px bg-medical-border"></div>
          </div>

          <Link href="/consultation" className="block text-center text-sm text-medical-primary hover:underline">跳过登录，直接问诊 →</Link>
        </div>
      </div>
    </div>
  );
}
