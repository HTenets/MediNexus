"use client";

import { IconAlert, IconPhone } from "./icons";

export default function DisclaimerBanner({ type = "standard" }: { type?: "standard" | "emergency" }) {
  if (type === "emergency") {
    return (
      <div className="bg-red-50 border-t-2 border-red-400 px-4 py-3.5 animate-in slide-in-from-bottom">
        <div className="max-w-4xl mx-auto flex items-start gap-3">
          <div className="w-9 h-9 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <IconAlert className="w-5 h-5 text-red-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-red-800 mb-1" style={{ fontFamily: 'var(--font-heading)' }}>检测到紧急情况</p>
            <ul className="text-sm text-red-700 space-y-1">
              <li className="flex items-center gap-2">
                <IconPhone className="w-3.5 h-3.5" />
                请立即拨打 <strong className="text-red-800 mx-0.5">120</strong> 急救电话
              </li>
              <li>• 保持患者平躺，勿随意移动</li>
              <li>• 如有出血可做基础包扎止血</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-amber-50/80 backdrop-blur-sm border-t border-amber-200 px-4 py-2.5">
      <div className="max-w-4xl mx-auto flex items-start gap-2.5">
        <div className="w-5 h-5 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
          <IconAlert className="w-3.5 h-3.5 text-amber-700" />
        </div>
        <p className="text-xs text-amber-800/80 leading-relaxed">
          <strong className="text-amber-900">医疗免责声明</strong>&nbsp;
          以上内容由 AI 生成，仅供参考，不构成医疗诊断建议。如有不适请前往正规医疗机构就诊。紧急情况请拨打 120。
        </p>
      </div>
    </div>
  );
}
