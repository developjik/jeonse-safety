import asyncio

from fastapi import APIRouter, HTTPException
from api.models.schemas import AnalyzeRequest, AnalyzeResponse, RiskItem
from api.services.molit_api import evaluate_jeonse_ratio, evaluate_building
from api.services.contract_checker import evaluate_contract_mismatch
from api.services.hug_api import evaluate_insurance
from api.services.registry_api import evaluate_registry
from api.services.analyzer import analyze
from api.cache.db import make_cache_key, get_cached, set_cached

router = APIRouter()


async def _safe_evaluate(coro, fallback_category: str, fallback_label: str) -> RiskItem:
    """Run a check coroutine with individual error handling."""
    try:
        return await coro
    except Exception:
        return RiskItem(
            category=fallback_category,
            label=fallback_label,
            status="unavailable",
            value="확인 불가",
            interpretation="일시적인 서버 오류로 확인할 수 없습니다.",
            detail="잠시 후 다시 시도해주세요.",
        )


def _sync_safe_evaluate(fn, fallback_category: str, fallback_label: str) -> RiskItem:
    """Run a synchronous check with individual error handling."""
    try:
        return fn()
    except Exception:
        return RiskItem(
            category=fallback_category,
            label=fallback_label,
            status="unavailable",
            value="확인 불가",
            interpretation="일시적인 서버 오류로 확인할 수 없습니다.",
            detail="잠시 후 다시 시도해주세요.",
        )


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

    # 병렬 검사
    items = list(await asyncio.gather(
        _safe_evaluate(evaluate_jeonse_ratio(request), "jeonse_ratio", "전세가율"),
        _safe_evaluate(evaluate_building(request), "building", "건축물대장"),
    ))

    # 동기 검사 (다운계약서)
    items.append(
        _sync_safe_evaluate(
            lambda: evaluate_contract_mismatch(request.contract_gab, request.contract_eul),
            "contract_mismatch",
            "다운계약서 검사",
        )
    )

    # 동기 검사 (HUG 보증보험)
    items.append(
        _sync_safe_evaluate(
            lambda: evaluate_insurance(request.sigungu_code),
            "insurance",
            "HUG 보증보험",
        )
    )

    # 동기 검사 (등기부등록)
    items.append(
        _sync_safe_evaluate(
            lambda: evaluate_registry(request.address, request.deposit),
            "registry",
            "등기부등록",
        )
    )

    # 종합 분석
    response = analyze(request, items)

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
