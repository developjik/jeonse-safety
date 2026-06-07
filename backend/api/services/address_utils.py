"""주소 정규화 유틸리티 — 카카오 우편번호 결과를 공공 API 호출용으로 변환"""
import re


def extract_sigungu_code(jibun_address: str) -> str:
    """
    지번주소에서 법정동 시군구코드 추출.
    카카오 우편번호 API가 sigunguCode를 제공하면 그것을 우선 사용.
    폴백: 주소 문자열에서 추정.
    """
    # 카카오 API 응답에 sigunguCode가 있으면 그것을 사용 (caller에서 세팅)
    # 여기서는 폴백 로직만 제공
    if not jibun_address:
        return ""

    # 한국 주소 패턴: 시도 + 시군구 + 읍면동
    # 예: "서울특별시 강남구 역삼동 123-4"
    pattern = r"(\w+[시도])\s+(\w+[시군구])"
    match = re.search(pattern, jibun_address)
    if match:
        return match.group(0).replace(" ", "")
    return ""


def normalize_address(
    road_address: str,
    jibun_address: str,
    building_name: str,
    sigungu_code: str = "",
) -> dict:
    """카카오 우편번호 결과를 API 호출용으로 정규화"""
    return {
        "road_address": road_address,
        "jibun_address": jibun_address,
        "building_name": building_name,
        "sigungu_code": sigungu_code or extract_sigungu_code(jibun_address),
        "primary_address": road_address or jibun_address,
        "fallback_address": jibun_address,
    }
