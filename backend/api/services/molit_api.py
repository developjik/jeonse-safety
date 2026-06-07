"""국토교통부 공공데이터포털 API 연동 — 실거래가 + 건축물대장"""
import asyncio
import os
import httpx
import xmltodict
from datetime import datetime
from api.models.schemas import RiskItem, AnalyzeRequest
from api.services.analyzer import calculate_effective_deposit


MOLIT_BASE_URL = "https://apis.data.go.kr/1613000"
SERVICE_KEY = os.environ.get("MOLIT_SERVICE_KEY_DECODED", "")


async def _fetch_month_trade(client: httpx.AsyncClient, sem: asyncio.Semaphore, sigungu_code: str, yyyymm: str, area_sqm: float | None = None, building_name: str | None = None) -> list[float]:
    """Single month fetch for trade avg."""
    async with sem:
        url = f"{MOLIT_BASE_URL}/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
        params = {
            "serviceKey": SERVICE_KEY,
            "LAWD_CD": sigungu_code[:5] if len(sigungu_code) >= 5 else sigungu_code,
            "DEAL_YMD": yyyymm,
            "numOfRows": "100",
        }
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = data.get("response", {}).get("body", {}).get("items", {})
            result_items = []
            if items:
                item_list = items.get("item", [])
                if isinstance(item_list, dict):
                    item_list = [item_list]
                for item in item_list:
                    # Building name filter (1st priority)
                    if building_name:
                        apt_nm = item.get('aptNm', item.get('아파트', ''))
                        if apt_nm and building_name not in apt_nm and apt_nm not in building_name:
                            continue
                    # Area filter
                    if area_sqm:
                        try:
                            area = float(item.get('excluUseAr', item.get('전용면적', '0')))
                            if abs(area - area_sqm) > 10:
                                continue
                        except ValueError:
                            pass
                    amount_str = item.get("dealAmount", item.get("거래금액", "0")).replace(",", "").strip()
                    try:
                        result_items.append(float(amount_str))
                    except ValueError:
                        continue
            return result_items
        except Exception:
            return []


async def fetch_apt_trade_avg(sigungu_code: str, months: int = 6, area_sqm: float | None = None, building_name: str | None = None) -> float | None:
    """
    국토교통부 아파트 실거래가 API에서 최근 N개월 평균 거래가 조회.
    반환: 평균 거래가 (만원 단위) 또는 None
    """
    if not SERVICE_KEY:
        return None

    now = datetime.now()
    sem = asyncio.Semaphore(3)
    async with httpx.AsyncClient(timeout=3.0) as client:
        tasks = []
        for i in range(months):
            month_date = datetime(now.year, now.month - i, 1) if now.month > i else datetime(now.year - 1, 12 - (i - now.month), 1)
            yyyymm = month_date.strftime("%Y%m")
            tasks.append(_fetch_month_trade(client, sem, sigungu_code, yyyymm, area_sqm, building_name))
        results = await asyncio.gather(*tasks)

    amounts = [a for batch in results for a in batch]
    if not amounts:
        return None
    return sum(amounts) / len(amounts)


async def _fetch_month_jeonse(client: httpx.AsyncClient, sem: asyncio.Semaphore, sigungu_code: str, yyyymm: str, area_sqm: float | None = None, building_name: str | None = None) -> list[float]:
    """Single month fetch for jeonse avg."""
    async with sem:
        url = f"{MOLIT_BASE_URL}/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
        params = {
            "serviceKey": SERVICE_KEY,
            "LAWD_CD": sigungu_code[:5] if len(sigungu_code) >= 5 else sigungu_code,
            "DEAL_YMD": yyyymm,
            "numOfRows": "100",
        }
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = data.get("response", {}).get("body", {}).get("items", {})
            result_items = []
            if items:
                item_list = items.get("item", [])
                if isinstance(item_list, dict):
                    item_list = [item_list]
                for item in item_list:
                    # Building name filter (1st priority)
                    if building_name:
                        apt_nm = item.get('aptNm', item.get('아파트', ''))
                        if apt_nm and building_name not in apt_nm and apt_nm not in building_name:
                            continue
                    # Area filter
                    if area_sqm:
                        try:
                            area = float(item.get('excluUseAr', item.get('전용면적', '0')))
                            if abs(area - area_sqm) > 10:
                                continue
                        except ValueError:
                            pass
                    amount_str = item.get("deposit", item.get("보증금액", "0")).replace(",", "").strip()
                    try:
                        result_items.append(float(amount_str))
                    except ValueError:
                        continue
            return result_items
        except Exception:
            return []


async def fetch_jeonse_trade_avg(sigungu_code: str, months: int = 6, area_sqm: float | None = None, building_name: str | None = None) -> float | None:
    """전세 실거래가 평균 조회"""
    if not SERVICE_KEY:
        return None

    now = datetime.now()
    sem = asyncio.Semaphore(3)
    async with httpx.AsyncClient(timeout=3.0) as client:
        tasks = []
        for i in range(months):
            month_date = datetime(now.year, now.month - i, 1) if now.month > i else datetime(now.year - 1, 12 - (i - now.month), 1)
            yyyymm = month_date.strftime("%Y%m")
            tasks.append(_fetch_month_jeonse(client, sem, sigungu_code, yyyymm, area_sqm, building_name))
        results = await asyncio.gather(*tasks)

    amounts = [a for batch in results for a in batch]
    if not amounts:
        return None
    return sum(amounts) / len(amounts)


async def evaluate_jeonse_ratio(request: AnalyzeRequest) -> RiskItem:
    """전세가율 검사"""
    effective_deposit = calculate_effective_deposit(
        request.rental_type, request.deposit, request.monthly_rent
    )

    market_avg, region_avg_data = await asyncio.gather(
        fetch_apt_trade_avg(request.sigungu_code, area_sqm=request.area_sqm, building_name=request.building_name or None),
        fetch_jeonse_trade_avg(request.sigungu_code, area_sqm=request.area_sqm, building_name=request.building_name or None),
    )
    region_avg = region_avg_data

    if market_avg is None or market_avg == 0:
        return RiskItem(
            category="jeonse_ratio",
            label="전세가율",
            status="unavailable",
            value="확인 불가",
            interpretation="시세 데이터를 조회할 수 없습니다.",
            detail="공공데이터포털에서 해당 지역의 실거래가 데이터를 불러올 수 없습니다.",
        )

    # 전세가율 = 환산보증금(만원) / 시세(만원) × 100
    ratio = (effective_deposit / market_avg) * 100

    # 지역 평균 전세가율
    region_avg_pct = (region_avg / market_avg * 100) if region_avg and market_avg else None

    if ratio < 70:
        status = "safe"
        interpretation = f"전세가율이 낮아 안전합니다."
    elif ratio <= 85:
        status = "caution"
        interpretation = f"전세가율이 다소 높습니다."
    else:
        status = "danger"
        interpretation = f"전세가율이 매우 높아 까대기 위험이 있습니다."

    detail_parts = [
        f"전세가율: {ratio:.1f}%",
        f"시세 추정: {market_avg:.0f}만원",
        f"환산보증금: {effective_deposit:,}만원",
    ]
    if request.area_sqm:
        detail_parts.append(f'전용면적: {request.area_sqm}㎡ 기준 (±10㎡)')
    else:
        detail_parts.append('시군구 전체 평균 기준')
    if region_avg_pct:
        detail_parts.append(f"지역 평균 전세가율: {region_avg_pct:.1f}%")

    return RiskItem(
        category="jeonse_ratio",
        label="전세가율",
        status=status,
        value=f"{ratio:.1f}%",
        interpretation=interpretation,
        detail=" | ".join(detail_parts),
    )


async def fetch_building_info(sigungu_cd: str, bjdong_cd: str, bun: str, ji: str) -> dict | None:
    """건축물대장 표제부 정보 조회"""
    if not SERVICE_KEY or not sigungu_cd:
        return None

    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {
            "serviceKey": SERVICE_KEY,
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "platGbCd": "0",
            "bun": bun,
            "ji": ji,
            "numOfRows": "10",
        }

        # 번지가 있으면 정확히 조회
        if bun:
            try:
                url = f"{MOLIT_BASE_URL}/BldRgstHubService/getBrTitleInfo"
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = xmltodict.parse(resp.text)
                items = data.get("response", {}).get("body", {}).get("items", {})
                if items:
                    return items
            except Exception:
                pass

        # 번지 없으면 법정동 전체에서 첫 건물 반환
        params2 = {
            "serviceKey": SERVICE_KEY,
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "numOfRows": "1",
        }
        try:
            url = f"{MOLIT_BASE_URL}/BldRgstHubService/getBrTitleInfo"
            resp = await client.get(url, params=params2)
            resp.raise_for_status()
            data = xmltodict.parse(resp.text)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if items:
                return items
        except Exception:
            pass

    return None


async def evaluate_building(request: AnalyzeRequest) -> RiskItem:
    """건축물대장 검사"""
    # 프론트엔드에서 파싱한 파라미터 사용, 없으면 지번주소에서 추출 시도
    sigungu_cd = request.sigungu_code[:5] if request.sigungu_code else ""
    bjdong_cd = request.bjdong_code if request.bjdong_code else ""
    bun = request.bun if request.bun else _parse_bun(request.jibun_address)
    ji = request.ji if request.ji else _parse_ji(request.jibun_address)

    building_data = await fetch_building_info(sigungu_cd, bjdong_cd, bun, ji)

    if building_data is None:
        return RiskItem(
            category="building",
            label="건축물대장",
            status="unavailable",
            value="확인 불가",
            interpretation="건축물대장 정보를 조회할 수 없습니다.",
            detail="공공데이터포털에서 해당 주소의 건축물대장 데이터를 불러올 수 없습니다. 건축물대장은 주민센터에서 직접 발급받아 확인하세요.",
        )

    item_list = building_data.get("item", [])
    if isinstance(item_list, dict):
        item_list = [item_list]

    if not item_list:
        return RiskItem(
            category="building",
            label="건축물대장",
            status="unavailable",
            value="데이터 없음",
            interpretation="해당 주소의 건물 정보가 없습니다.",
            detail="공공데이터포털에서 해당 주소의 건물 데이터를 찾을 수 없습니다.",
        )

    item = item_list[0]
    main_purps = item.get("mainPurpsCdNm", item.get("주용도코드명", ""))
    is_violation = item.get("violBldtnYn", item.get("위반건축물여부", "N")) == "Y"
    bld_nm = item.get("bldNm", "")
    strct = item.get("strctCdNm", "")
    grnd_floors = item.get("grndFlrCnt", "")
    ugrnd_floors = item.get("ugrndFlrCnt", "")
    use_apr = item.get("useAprDay", "")
    arch_area = item.get("archArea", "")
    # 건물 노후도 계산
    building_age = None
    if use_apr and len(use_apr) >= 8:
        try:
            apr_year = int(use_apr[:4])
            building_age = datetime.now().year - apr_year
        except ValueError:
            pass

    # 내진 설계 여부 (향후 활용)
    _seismic_yn = item.get('strctCdNm', '')


    detail_parts = []
    if bld_nm:
        detail_parts.append(f"건물명: {bld_nm}")
    if main_purps:
        detail_parts.append(f"주용도: {main_purps}")
    if strct:
        detail_parts.append(f"구조: {strct}")
    if grnd_floors:
        detail_parts.append(f"층수: 지상{grnd_floors}층" + (f"/지하{ugrnd_floors}층" if ugrnd_floors else ""))
    if arch_area:
        detail_parts.append(f"건축면적: {arch_area}㎡")
    if building_age is not None:
        detail_parts.append(f"준공년도: {use_apr[:4]}년 ({building_age}년됨)")
    if building_age is not None:
        if building_age >= 30:
            detail_parts.append("노후도: 위험 (30년 이상)")
        elif building_age >= 20:
            detail_parts.append("노후도: 주의 (20-30년)")
        else:
            detail_parts.append("노후도: 양호 (20년 미만)")

    if is_violation:
        detail_parts.append("위반 건축물: 예")
        return RiskItem(
            category="building",
            label="건축물대장",
            status="danger",
            value="위반 건축물",
            interpretation="위반 건축물로 등록된 건물입니다.",
            detail=" | ".join(detail_parts),
        )

    # 노후도 판정 (위반 건축물이 아닐 때)
    if building_age is not None and building_age >= 30:
        return RiskItem(
            category="building",
            label="건축물대장",
            status="danger",
            value=f"{building_age}년 노후",
            interpretation=f"준공 {building_age}년으로 노후 건물입니다.",
            detail=" | ".join(detail_parts),
        )

    # 주거용 용도인지 확인
    residential_purposes = ["공동주택", "다가구주택", "단독주택", "아파트", "연립주택", "다세대주택", "주택", "근린생활시설"]
    is_residential = any(p in main_purps for p in residential_purposes) if main_purps else True

    if not is_residential:
        return RiskItem(
            category="building",
            label="건축물대장",
            status="danger",
            value="용도 불일치",
            interpretation=f"건물 용도({main_purps})가 주거용이 아닐 수 있습니다.",
            detail=" | ".join(detail_parts) + " | 주거용 여부: 불일치 의심",
        )

    detail_parts.append("위반 건축물: 아니오")
    return RiskItem(
        category="building",
        label="건축물대장",
        status="safe",
        value="정상",
        interpretation="건물 정보가 정상입니다.",
        detail=" | ".join(detail_parts),
    )


def _parse_bun(jibun_address: str) -> str:
    """지번주소에서 번 추출 (4자리 zero-pad)"""
    import re
    if not jibun_address:
        return ""
    m = re.search(r'(\d+)(?:-(\d+))?', jibun_address)
    return m.group(1).zfill(4) if m else ""


def _parse_ji(jibun_address: str) -> str:
    """지번주소에서 지 추출 (4자리 zero-pad)"""
    import re
    if not jibun_address:
        return "0000"
    m = re.search(r'(\d+)-(\d+)', jibun_address)
    return m.group(2).zfill(4) if m else "0000"
