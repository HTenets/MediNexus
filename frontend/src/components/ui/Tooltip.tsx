"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ReactNode, useState } from "react";

interface TooltipProps {
  children: ReactNode;
  content: ReactNode;
  placement?: "top" | "bottom" | "left" | "right";
}

export function Tooltip({ children, content, placement = "top" }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  const placementStyles = {
    top: "-translate-y-full mb-2",
    bottom: "translate-y-full mt-2",
    left: "-translate-x-full mr-2",
    right: "translate-x-full ml-2",
  };

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={`absolute z-50 glass-dark px-3 py-2 rounded-lg text-sm text-white whitespace-nowrap ${placementStyles[placement]}`}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
