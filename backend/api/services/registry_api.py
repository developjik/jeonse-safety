"""등기부등록 오픈 API — 근저당/가등기 검사"""
import os
from api.models.schemas import RiskItem

REGISTRY_SERVICE_KEY = os.environ.get('REGISTRY_SERVICE_KEY', '')


def evaluate_registry(address: str, deposit: int) -> RiskItem:
    """근저당/가등기 검사"""
    # API key not yet available — return unavailable
    return RiskItem(
        category='registry',
        label='등기부등록',
        status='unavailable',
        value='확인 불가',
        interpretation='등기부등록 API 승인 대기 중입니다.',
        detail='공공데이터포털 등기부등록 오픈 API 활용신청 후 근저당/가등기 정보를 제공할 예정입니다.',
    )
