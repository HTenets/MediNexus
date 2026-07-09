"use client";

import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function Skeleton({ className = "", animate = true }: SkeletonProps) {
  return (
    <motion.div
      className={`bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 rounded-lg ${className}`}
      animate={animate ? {
        backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
      } : {}}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "linear",
      }}
      style={{
        backgroundSize: "200% 100%",
      }}
    />
  );
}

interface SkeletonCardProps {
  className?: string;
}

export function SkeletonCard({ className = "" }: SkeletonCardProps) {
  return (
    <div className={`glass-card rounded-2xl p-6 ${className}`}>
      <div className="flex items-center gap-4 mb-4">
        <Skeleton className="w-12 h-12 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
      <div className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    </div>
  );
}

interface SkeletonAvatarProps {
  className?: string;
}

export function SkeletonAvatar({ className = "" }: SkeletonAvatarProps) {
  return <Skeleton className={`w-10 h-10 rounded-full ${className}`} />;
}
