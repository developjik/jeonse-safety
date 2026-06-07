"use client";

import { RiskStatus } from "../lib/types";

interface RiskGaugeProps {
  status: RiskStatus;
}

const statusConfig: Record<
  RiskStatus,
  { label: string; color: string; bg: string; emoji: string }
> = {
  safe: {
    label: "안전",
    color: "text-green-700",
    bg: "bg-green-100 border-green-300",
    emoji: "✅",
  },
  caution: {
    label: "주의",
    color: "text-yellow-700",
    bg: "bg-yellow-100 border-yellow-300",
    emoji: "⚠️",
  },
  danger: {
    label: "위험",
    color: "text-red-700",
    bg: "bg-red-100 border-red-300",
    emoji: "🔴",
  },
  unavailable: {
    label: "확인 불가",
    color: "text-gray-600",
    bg: "bg-gray-100 border-gray-300",
    emoji: "❓",
  },
};

export default function RiskGauge({ status }: RiskGaugeProps) {
  const config = statusConfig[status];

  return (
    <div
      className={`rounded-xl border-2 p-6 text-center ${config.bg} transition`}
    >
      <div className="text-4xl">{config.emoji}</div>
      <div className={`mt-2 text-2xl font-bold ${config.color}`}>
        종합 판정: {config.label}
      </div>
      <p className="mt-1 text-sm text-gray-500">
        {status === "safe" && "검사 항목에서 특이사항이 발견되지 않았습니다."}
        {status === "caution" &&
          "일부 항목에서 주의가 필요합니다. 상세 내용을 확인하세요."}
        {status === "danger" &&
          "위험 항목이 감지되었습니다. 계약 전 반드시 확인하세요."}
        {status === "unavailable" &&
          "데이터를 충분히 확인할 수 없습니다."}
      </p>
    </div>
  );
}
