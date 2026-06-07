export type RentalType = "jeonse" | "wolse";
export type RiskStatus = "safe" | "caution" | "danger" | "unavailable";

export interface AddressData {
  roadAddress: string;
  jibunAddress: string;
  buildingName: string;
  sigunguCode: string;
  bcode: string;
  zonecode: string;
}

export interface AnalyzeRequest {
  address: string;
  jibun_address: string;
  building_name: string;
  sigungu_code: string;
  bjdong_code: string;
  bun: string;
  ji: string;
  rental_type: RentalType;
  deposit: number;
  monthly_rent?: number | null;
}

export interface RiskItem {
  category: string;
  label: string;
  status: RiskStatus;
  value: string;
  interpretation: string;
  detail: string;
}

export interface AnalyzeResponse {
  overall_status: RiskStatus;
  items: RiskItem[];
  guidance: string[];
  disclaimer: string;
  has_unavailable: boolean;
}
