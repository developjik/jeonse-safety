from fastapi import APIRouter, HTTPException
from api.models.schemas import AnalyzeRequest, AnalyzeResponse
from api.services.molit_api import evaluate_jeonse_ratio, evaluate_building
from api.services.analyzer import analyze
from api.cache.db import make_cache_key, get_cached, set_cached

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_property(request: AnalyzeRequest):
    """부동산 위험 분석 API"""
    # 캐시 조회
    cache_key = make_cache_key(
        request.address, request.rental_type, request.deposit, request.monthly_rent
    )
    cached = await get_cached(cache_key)
    if cached:
        return AnalyzeResponse(**cached)

    # 전세가율 검사
    jeonse_ratio_item = await evaluate_jeonse_ratio(request)

    # 건축물대장 검사
    building_item = await evaluate_building(request)

    # 종합 분석
    response = analyze(request, jeonse_ratio_item, building_item)

    # 캐시 저장
    try:
        await set_cached(
            cache_key,
            request.model_dump(),
            response.model_dump(),
        )
    except Exception:
        pass  # 캐싱 실패는 무시 (DB 미연결 시)

    return response
