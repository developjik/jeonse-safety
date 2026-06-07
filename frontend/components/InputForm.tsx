"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AddressSearch from "./AddressSearch";
import { analyzeProperty } from "../lib/api";
import {
  AddressData,
  AnalyzeResponse,
  RentalType,
} from "../lib/types";

function parseBun(jibunAddr: string): string {
  const m = jibunAddr.match(/(\d+)(?:-(\d+))?\s*(?:번지|$)/);
  return m ? m[1].padStart(4, "0") : "";
}
function parseJi(jibunAddr: string): string {
  const m = jibunAddr.match(/(\d+)-(\d+)/);
  return m ? m[2].padStart(4, "0") : "0000";
}
export default function InputForm() {
  const router = useRouter();
  const [address, setAddress] = useState<AddressData | null>(null);
  const [rentalType, setRentalType] = useState<RentalType>("jeonse");
  const [deposit, setDeposit] = useState("");
  const [monthlyRent, setMonthlyRent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address) {
      setError("주소를 먼저 검색해주세요.");
      return;
    }
    if (!deposit || Number(deposit) <= 0) {
      setError("금액을 입력해주세요.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result: AnalyzeResponse = await analyzeProperty({
        address: address.roadAddress,
        jibun_address: address.jibunAddress,
        building_name: address.buildingName,
        sigungu_code: address.sigunguCode,
        bjdong_code: address.bcode ? address.bcode.slice(-5) : "",
        bun: address.jibunAddress ? parseBun(address.jibunAddress) : "",
        ji: address.jibunAddress ? parseJi(address.jibunAddress) : "",
        rental_type: rentalType,
        deposit: Number(deposit),
        monthly_rent: rentalType === "wolse" ? Number(monthlyRent) : null,
      });

      // 결과를 sessionStorage에 저장하고 결과 페이지로 이동
      sessionStorage.setItem("analyze_result", JSON.stringify(result));
      sessionStorage.setItem(
        "analyze_request",
        JSON.stringify({
          address: address,
          rentalType,
          deposit: Number(deposit),
          monthlyRent: rentalType === "wolse" ? Number(monthlyRent) : null,
        })
      );
      router.push("/result");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "분석 중 오류가 발생했습니다."
      );
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value: string) => {
    const num = value.replace(/[^0-9]/g, "");
    return num ? Number(num).toLocaleString() : "";
  };

  const handleDepositChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9]/g, "");
    setDeposit(raw);
  };

  const handleMonthlyRentChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const raw = e.target.value.replace(/[^0-9]/g, "");
    setMonthlyRent(raw);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Step 1: 주소 검색 */}
      <div>
        <label className="mb-2 block text-sm font-semibold text-gray-700">
          1️⃣ 주소 검색
        </label>
        <AddressSearch
          onSelect={setAddress}
          selectedAddress={address?.roadAddress || address?.jibunAddress}
        />
      </div>

      {/* Step 2: 전세/월세 선택 */}
      <div>
        <label className="mb-2 block text-sm font-semibold text-gray-700">
          2️⃣ 계약 유형
        </label>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setRentalType("jeonse")}
            className={`flex-1 rounded-lg py-3 text-sm font-medium transition ${
              rentalType === "jeonse"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            전세
          </button>
          <button
            type="button"
            onClick={() => setRentalType("wolse")}
            className={`flex-1 rounded-lg py-3 text-sm font-medium transition ${
              rentalType === "wolse"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            월세
          </button>
        </div>
      </div>

      {/* Step 3: 금액 입력 */}
      <div>
        <label className="mb-2 block text-sm font-semibold text-gray-700">
          3️⃣ 금액 입력
        </label>
        <div className="space-y-3">
          <div className="relative">
            <input
              type="text"
              inputMode="numeric"
              value={deposit ? formatNumber(deposit) : ""}
              onChange={handleDepositChange}
              placeholder={
                rentalType === "jeonse"
                  ? "전세금 (만원)"
                  : "보증금 (만원)"
              }
              className="w-full rounded-lg border border-gray-300 p-3 pr-12 text-right text-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
              만원
            </span>
          </div>

          {rentalType === "wolse" && (
            <div className="relative">
              <input
                type="text"
                inputMode="numeric"
                value={monthlyRent ? formatNumber(monthlyRent) : ""}
                onChange={handleMonthlyRentChange}
                placeholder="월세 (만원)"
                className="w-full rounded-lg border border-gray-300 p-3 pr-12 text-right text-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                만원/월
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* 분석 버튼 */}
      <button
        type="submit"
        disabled={loading || !address || !deposit}
        className="w-full rounded-lg bg-blue-600 py-4 text-lg font-bold text-white transition hover:bg-blue-700 disabled:bg-gray-300 disabled:text-gray-500"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="h-5 w-5 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            공공 데이터를 조회하고 있어요...
          </span>
        ) : (
          "🔍 안전 분석하기"
        )}
      </button>
    </form>
  );
}
