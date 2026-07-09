"use client";

import { motion } from "framer-motion";
import { AlertCircle, X } from "lucide-react";
import { useState } from "react";

export function DisclaimerBanner() {
  const [isClosed, setIsClosed] = useState(false);

  if (isClosed) return null;

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: -100, opacity: 0 }}
      className="glass rounded-xl p-4 flex items-start gap-3 mb-6"
    >
      <div className="w-8 h-8 rounded-full bg-medical-warning-light flex items-center justify-center flex-shrink-0">
        <AlertCircle className="w-4 h-4 text-medical-warning" />
      </div>
      <div className="flex-1">
        <div className="text-sm font-medium text-medical-text-primary">免责声明</div>
        <div className="text-sm text-medical-text-secondary mt-0.5">
          以下治疗方案由 AI 生成，仅供参考，不构成医疗诊断或处方。如有不适，请及时就医。
        </div>
      </div>
      <button
        onClick={() => setIsClosed(true)}
        className="p-1 hover:bg-medical-warning-light rounded-lg transition-colors"
      >
        <X className="w-4 h-4 text-medical-text-muted" />
      </button>
    </motion.div>
  );
}
