from pydantic import BaseModel, Field
from typing import Literal


class AnalyzeRequest(BaseModel):
    address: str = Field(..., description="도로명주소")
    jibun_address: str = Field(default="", description="지번주소")
    building_name: str = Field(default="", description="건물명")
    sigungu_code: str = Field(default="", description="시군구코드")
    bjdong_code: str = Field(default="", description="법정동코드 하위 5자리")
    bun: str = Field(default="", description="번지 (4자리 zero-pad)")
    ji: str = Field(default="", description="지번 (4자리 zero-pad)")
    rental_type: Literal["jeonse", "wolse"] = Field(..., description="전세/월세 구분")
    deposit: int = Field(..., description="보증금 (만원 단위)")
    monthly_rent: int | None = Field(default=None, description="월세 (만원 단위, wolse인 경우)")


class RiskItem(BaseModel):
    category: str = Field(..., description="검사 항목: jeonse_ratio | building | insurance")
    label: str = Field(..., description="항목명 (한국어)")
    status: Literal["safe", "caution", "danger", "unavailable"] = Field(..., description="판정")
    value: str = Field(..., description="수치 (예: 87.5%)")
    interpretation: str = Field(..., description="해석 (한국어)")
    detail: str = Field(default="", description="상세 설명")


class AnalyzeResponse(BaseModel):
    overall_status: Literal["safe", "caution", "danger", "unavailable"] = Field(..., description="종합 판정")
    items: list[RiskItem] = Field(..., description="항목별 검사 결과")
    guidance: list[str] = Field(default_factory=list, description="실행 지침")
    disclaimer: str = Field(default="", description="면책 문구")
    has_unavailable: bool = Field(default=False, description="확인 불가 항목 존재 여부")
