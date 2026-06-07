"""HUG 주택도시보증공사 전세보증금반환보증 사고 현황 API"""
import os
from api.models.schemas import RiskItem

HUG_SERVICE_KEY = os.environ.get('HUG_SERVICE_KEY', '')


async def fetch_hug_accident_stats(sigungu_code: str) -> dict | None:
    """HUG 지역별 전세보증금반환보증 사고 현황 조회"""
    if not HUG_SERVICE_KEY:
        return None
    # HUG API endpoint — use 공공데이터포털 proxy
    # Note: Exact endpoint TBD after API key approval
    # Using placeholder endpoint structure
    return None


def evaluate_insurance(sigungu_code: str) -> RiskItem:
    """HUG 보증보험 검사"""
    # API key not yet available — return unavailable
    return RiskItem(
        category='insurance',
        label='HUG 보증보험',
        status='unavailable',
        value='확인 불가',
        interpretation='HUG 전세금 반환보증보험 API 승인 대기 중입니다.',
        detail='HUG 주택도시보증공사 오픈 API 활용신청 후 사고 현황 데이터를 제공할 예정입니다.',
    )
