"use client";

export default function Disclaimer() {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-xs text-gray-500">
      <p className="font-semibold text-gray-600">⚠️ 면책 고지</p>
      <p className="mt-1">
        본 분석 결과는 공공 데이터를 기반으로 한{" "}
        <strong>참고용 정보</strong>이며, 법적 자문이 아닙니다. 실제 계약 전
        반드시 부동산 전문가 및 법률 전문가와 상담하세요. 분석 결과의 정확성을
        보장하지 않으며, 본 서비스 이용으로 인한 어떠한 손해에도 책임을 지지
        않습니다.
      </p>
    </div>
  );
}
