"use client";

import { RiskItem, RiskStatus } from "../lib/types";

interface RiskCardProps {
  item: RiskItem;
}

const statusStyles: Record<RiskStatus, string> = {
  safe: "border-l-green-500 bg-green-50",
  caution: "border-l-yellow-500 bg-yellow-50",
  danger: "border-l-red-500 bg-red-50",
  unavailable: "border-l-gray-400 bg-gray-50",
};

const statusBadge: Record<RiskStatus, { text: string; class: string }> = {
  safe: { text: "안전", class: "bg-green-100 text-green-700" },
  caution: { text: "주의", class: "bg-yellow-100 text-yellow-700" },
  danger: { text: "위험", class: "bg-red-100 text-red-700" },
  unavailable: { text: "확인 불가", class: "bg-gray-100 text-gray-600" },
};

export default function RiskCard({ item }: RiskCardProps) {
  const badge = statusBadge[item.status];

  return (
    <div
      className={`rounded-lg border-l-4 p-4 ${statusStyles[item.status]}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-800">{item.label}</h3>
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${badge.class}`}
        >
          {badge.text}
        </span>
      </div>

      <div className="mt-2 text-2xl font-bold text-gray-900">{item.value}</div>

      <p className="mt-1 text-sm text-gray-600">{item.interpretation}</p>

      {item.detail && (
        <p className="mt-2 text-xs text-gray-400">{item.detail}</p>
      )}
    </div>
  );
}
