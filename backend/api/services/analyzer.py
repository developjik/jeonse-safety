from api.models.schemas import AnalyzeRequest, AnalyzeResponse, RiskItem


def calculate_effective_deposit(rental_type: str, deposit: int, monthly_rent: int | None) -> int:
    """월세인 경우 환산보증금 계산: 보증금 + 월세 × 100"""
    if rental_type == "jeonse":
        return deposit
    return deposit + (monthly_rent or 0) * 100


def determine_overall_status(items: list[RiskItem]) -> str:
    """종합 판정 조합 규칙 (명시적 의사결정표)"""
    available = [i for i in items if i.status != "unavailable"]

    if not available:
        return "unavailable"

    # 규칙 1: danger가 1개 이상 → overall = danger
    if any(i.status == "danger" for i in available):
        return "danger"

    # 규칙 2: danger 없고 caution이 1개 이상 → overall = caution
    if any(i.status == "caution" for i in available):
        return "caution"

    # 규칙 3: 모두 safe → overall = safe
    return "safe"


def generate_guidance(items: list[RiskItem], overall_status: str) -> list[str]:
    """실행 지침 생성"""
    guidance = []

    if overall_status == "danger":
        guidance.append("⚠️ 위험 항목이 감지되었습니다. 계약 전 반드시 전문가 상담을 권장합니다.")

    if overall_status == "caution":
        guidance.append("주의 항목이 있습니다. 추가 확인 후 계약 진행을 고려하세요.")

    for item in items:
        if item.category == "jeonse_ratio" and item.status in ("caution", "danger"):
            guidance.append(f"전세가율이 높습니다. 주변 시세와 비교하여 전세금이 적정한지 확인하세요.")
        if item.category == "building" and item.status == "danger":
            guidance.append(f"건물 정보에 문제가 있습니다. 건축물대장을 직접 확인하세요.")

    if all(i.status == "safe" for i in items if i.status != "unavailable"):
        guidance.append("✅ 검사 항목에서 특이사항이 발견되지 않았습니다. 다만 본 결과는 참고용이며, 계약 전 전문가 상담을 권장합니다.")

    guidance.append("본 분석 결과는 공공 데이터를 기반으로 한 참고용 정보이며, 법적 자문이 아닙니다.")

    return guidance


def analyze(request: AnalyzeRequest, jeonse_ratio_item: RiskItem, building_item: RiskItem) -> AnalyzeResponse:
    """전체 위험 분석 실행"""
    items = [jeonse_ratio_item, building_item]

    overall_status = determine_overall_status(items)
    guidance = generate_guidance(items, overall_status)
    has_unavailable = any(i.status == "unavailable" for i in items)

    return AnalyzeResponse(
        overall_status=overall_status,
        items=items,
        guidance=guidance,
        disclaimer="본 분석 결과는 공공 데이터를 기반으로 한 참고용 정보이며, 법적 자문이 아닙니다. 실제 계약 전 반드시 부동산 전문가와 상담하세요.",
        has_unavailable=has_unavailable,
    )
