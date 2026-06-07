"use client";

import { useEffect, useState } from "react";
import RiskGauge from "../../../components/RiskGauge";
import RiskCard from "../../../components/RiskCard";
import Disclaimer from "../../../components/Disclaimer";
import { AnalyzeResponse } from "../../../lib/types";
import { useParams } from "next/navigation";

export default function SharedResultPage() {
  const params = useParams();
  const shareId = params?.id as string;
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!shareId) {
      setError("잘못된 접근입니다.");
      setLoading(false);
      return;
    }

    fetch(`/api/results/${shareId}`)
      .then(async (resp) => {
        if (!resp.ok) {
          throw new Error(resp.status === 404 ? "만료되었거나 존재하지 않는 결과입니다." : "결과를 불러올 수 없습니다.");
        }
        return resp.json();
      })
      .then((data) => {
        setResult(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "결과를 불러올 수 없습니다.");
        setLoading(false);
      });
  }, [shareId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
          <p className="text-gray-500">분석 결과를 불러오고 있어요...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center">
        <p className="text-red-600">{error}</p>
        <a href="/" className="mt-3 inline-block text-sm text-blue-500 hover:underline">
          ← 새로운 분석하기
        </a>
      </div>
    );
  }

  if (!result) return null;

  const unavailableCount = result.items.filter(item => item.status === "unavailable").length;
  const totalCount = result.items.length;

  return (
    <div className="space-y-6" data-result-area>
      <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-600">
        📋 공유된 분석 결과입니다
      </div>

      <RiskGauge status={result.overall_status} />

      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-600">항목별 상세 결과</h2>
        {result.items.map((item) => (
          <RiskCard key={item.category} item={item} />
        ))}
      </div>

      {(() => {
        if (unavailableCount === totalCount) {
          return (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              ❌ 공공 데이터 서버 오류로 분석이 제한됩니다.
            </div>
          );
        }
        if (unavailableCount >= 3) {
          return (
            <div className="rounded-lg border border-orange-200 bg-orange-50 p-3 text-sm text-orange-700">
              ⚠️ 여러 검사 항목을 확인할 수 없습니다.
            </div>
          );
        }
        if (unavailableCount > 0) {
          return (
            <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-700">
              ⚠️ 일부 정보를 확인할 수 없습니다.
            </div>
          );
        }
        return null;
      })()}

      <div className="space-y-2">
        <h2 className="text-sm font-semibold text-gray-600">실행 지침</h2>
        <ul className="space-y-1">
          {result.guidance.map((g, i) => (
            <li key={i} className="rounded-lg bg-white p-3 text-sm text-gray-700 shadow-sm">
              {g}
            </li>
          ))}
        </ul>
      </div>

      <Disclaimer />

      <div className="text-center">
        <a href="/" className="text-sm text-blue-500 hover:underline">
          ← 직접 분석해보기
        </a>
      </div>
    </div>
  );
}
