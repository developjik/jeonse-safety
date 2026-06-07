"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import RiskGauge from "../../components/RiskGauge";
import RiskCard from "../../components/RiskCard";
import Disclaimer from "../../components/Disclaimer";
import { AnalyzeResponse } from "../../lib/types";

export default function ResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [requestInfo, setRequestInfo] = useState<{
    address: { roadAddress: string; buildingName: string };
    rentalType: string;
    deposit: number;
    monthlyRent: number | null;
  } | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("analyze_result");
    const reqStored = sessionStorage.getItem("analyze_request");

    if (!stored) {
      router.push("/");
      return;
    }

    try {
      setResult(JSON.parse(stored));
      if (reqStored) setRequestInfo(JSON.parse(reqStored));
    } catch {
      router.push("/");
    }
  }, [router]);

  if (!result) return null;

  return (
    <div className="space-y-6" data-result-area>
      {/* 뒤로 가기 */}
      <button
        onClick={() => router.push("/")}
        className="text-sm text-blue-500 hover:underline"
      >
        ← 새로운 주소 분석하기
      </button>

      {/* 입력 정보 요약 */}
      {requestInfo && (
        <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">
          <p>
            📍 {requestInfo.address.roadAddress}
            {requestInfo.address.buildingName &&
              ` (${requestInfo.address.buildingName})`}
          </p>
          <p>
            {requestInfo.rentalType === "jeonse" ? "전세" : "월세"} |{" "}
            {requestInfo.deposit.toLocaleString()}만원
            {requestInfo.rentalType === "wolse" &&
              requestInfo.monthlyRent &&
              ` + ${requestInfo.monthlyRent.toLocaleString()}만원/월`}
          </p>
        </div>
      )}

      {/* 종합 판정 */}
      <RiskGauge status={result.overall_status} />

      {/* 항목별 결과 */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-600">
          항목별 상세 결과
        </h2>
        {result.items.map((item) => (
          <RiskCard key={item.category} item={item} />
        ))}
      </div>

      {/* 확인 불가 항목 경고 */}
      {(() => {
        const unavailableCount = result.items.filter(item => item.status === 'unavailable').length;
        const totalCount = result.items.length;
        if (unavailableCount === totalCount) {
          return (
            <div className='rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700'>
              ❌ 공공 데이터 서버 오류로 분석이 제한됩니다. 잠시 후 다시 시도해주세요.
            </div>
          );
        }
        if (unavailableCount >= 3) {
          return (
            <div className='rounded-lg border border-orange-200 bg-orange-50 p-3 text-sm text-orange-700'>
              ⚠️ 여러 검사 항목을 확인할 수 없습니다. 사용 가능한 결과만 참고하세요.
            </div>
          );
        }
        if (unavailableCount > 0) {
          return (
            <div className='rounded-lg border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-700'>
              ⚠️ 일부 정보를 확인할 수 없습니다. 해당 항목은 공공 데이터에서 제공하지 않거나 일시적으로 조회할 수 없는 정보입니다.
            </div>
          );
        }
        return null;
      })()}

      {/* 실행 지침 */}
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

      {/* 공유/저장 버튼 */}
      <div className="flex gap-3">
        <button
          onClick={async () => {
            try {
              const resp = await fetch('/api/results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ result }),
              });
              if (resp.status === 503) {
                alert('현재 공유 기능을 사용할 수 없습니다.');
                return;
              }
              const data = await resp.json();
              const url = `${window.location.origin}/result/${data.share_id}`;
              await navigator.clipboard.writeText(url);
              alert('공유 URL이 클립보드에 복사되었습니다!');
            } catch {
              alert('공유 URL 생성에 실패했습니다.');
            }
          }}
          className="flex-1 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm font-medium text-blue-700 hover:bg-blue-100"
        >
          🔗 공유 URL 복사
        </button>
        <button
          onClick={() => {
            const el = document.querySelector('[data-result-area]');
            if (!el) return;
            import('html2canvas').then(({ default: html2canvas }) => {
              html2canvas(el as HTMLElement, { backgroundColor: '#ffffff' }).then(canvas => {
                const link = document.createElement('a');
                link.download = '전세안심-분석결과.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
              });
            }).catch(() => alert('이미지 저장에 실패했습니다.'));
          }}
          className="flex-1 rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          📷 이미지 저장
        </button>
      </div>
      {/* 면책 고지 */}
      <Disclaimer />
    </div>
  );
}
