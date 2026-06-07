"use client";

import { useEffect, useRef } from "react";
import { AddressData } from "../lib/types";

declare global {
  interface Window {
    daum: {
      Postcode: new (params: {
        oncomplete: (data: Record<string, string>) => void;
      }) => { open: () => void };
    };
  }
}

interface AddressSearchProps {
  onSelect: (data: AddressData) => void;
  selectedAddress?: string;
}

export default function AddressSearch({
  onSelect,
  selectedAddress,
}: AddressSearchProps) {
  const postcodeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "https://t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js";
    script.async = true;
    document.head.appendChild(script);
  }, []);

  const openPostcode = () => {
    if (!window.daum) return;

    new window.daum.Postcode({
      oncomplete: (data) => {
        onSelect({
          roadAddress: data.roadAddress || "",
          jibunAddress: data.jibunAddress || "",
          buildingName: data.buildingName || "",
          sigunguCode: data.sigunguCode || "",
          bcode: data.bcode || data.sigunguCode || "",
          zonecode: data.zonecode || "",
        });
      },
    }).open();
  };

  return (
    <div>
      <button
        type="button"
        onClick={openPostcode}
        className="w-full rounded-lg border-2 border-dashed border-blue-300 bg-blue-50 p-4 text-center text-blue-600 transition hover:border-blue-400 hover:bg-blue-100"
      >
        {selectedAddress ? (
          <span className="text-sm">
            📍 {selectedAddress}
            <br />
            <span className="text-xs text-blue-400">클릭하여 변경</span>
          </span>
        ) : (
          <span>
            📍 주소 검색하기
            <br />
            <span className="text-xs text-gray-400">
              카카오 우편번호 서비스
            </span>
          </span>
        )}
      </button>
      <div ref={postcodeRef} />
    </div>
  );
}
