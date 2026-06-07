import { AddressData } from "./types";

/**
 * 카카오 우편번호 API 결과를 정규화.
 * 백엔드가 API 호출용 권위 출처이며, 프론트엔드는 UI 표시용만 담당.
 */
export function normalizeAddressForDisplay(data: AddressData): {
  displayAddress: string;
  displayBuilding: string;
} {
  const displayAddress = data.roadAddress || data.jibunAddress || "";
  const displayBuilding = data.buildingName
    ? `(${data.buildingName})`
    : "";
  return { displayAddress, displayBuilding };
}
