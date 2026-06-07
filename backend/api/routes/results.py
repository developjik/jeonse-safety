"""분석 결과 저장/조회 API (공유/저장 기능)"""
import hashlib
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.models.schemas import AnalyzeResponse
from api.cache.db import get_cached, set_cached

router = APIRouter()

# 결과는 캐시 DB에 저장 (TTL 90일)
SHARE_TTL_HOURS = 90 * 24  # 90 days


def _make_share_id(response: AnalyzeResponse) -> str:
    """결과 해시로 공유 ID 생성"""
    content = json.dumps(response.model_dump(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content.encode()).hexdigest()[:12]


class ShareRequest(BaseModel):
    result: AnalyzeResponse


class ShareResponse(BaseModel):
    share_id: str
    url: str


@router.post("/results", response_model=ShareResponse)
async def save_result(request: ShareRequest):
    """분석 결과 저장 후 공유 URL 반환"""
    share_id = _make_share_id(request.result)

    # 캐시에 저장 (share:<id> 키 사용)
    try:
        cache_key = f"share:{share_id}"
        await set_cached(cache_key, request.result.model_dump(), request.result.model_dump(), ttl_hours=SHARE_TTL_HOURS)
    except Exception:
        raise HTTPException(status_code=503, detail="현재 공유 기능을 사용할 수 없습니다. 잠시 후 다시 시도해주세요.")

    return ShareResponse(share_id=share_id, url=f"/result/{share_id}")


@router.get("/results/{share_id}", response_model=AnalyzeResponse)
async def get_result(share_id: str):
    """공유 ID로 분석 결과 조회"""
    cache_key = f"share:{share_id}"
    cached = await get_cached(cache_key)

    if not cached:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다. 만료되었을 수 있습니다.")

    # cached는 AnalyzeResponse 형태
    if isinstance(cached, dict) and "overall_status" in cached:
        return AnalyzeResponse(**cached)
    if isinstance(cached, dict) and "result" in cached:
        return AnalyzeResponse(**cached["result"])

    raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
