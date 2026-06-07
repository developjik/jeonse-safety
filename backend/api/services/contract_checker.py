"""갑/을 목적물 비교 검사"""
from api.models.schemas import RiskItem


def evaluate_contract_mismatch(gab_items: list[str] | None, eul_items: list[str] | None) -> RiskItem:
    """갑 목적물과 을 목적물 비교"""
    if not gab_items or not eul_items:
        return RiskItem(
            category='contract_mismatch',
            label='다운계약서 검사',
            status='unavailable',
            value='미입력',
            interpretation='갑/을 목적물 정보가 입력되지 않았습니다.',
            detail='갑/을 목적물을 입력하면 다운계약서 여부를 확인할 수 있습니다.',
        )

    # Normalize for comparison
    gab_set = {item.strip().lower() for item in gab_items if item.strip()}
    eul_set = {item.strip().lower() for item in eul_items if item.strip()}

    missing_in_eul = gab_set - eul_set
    extra_in_eul = eul_set - gab_set

    if not missing_in_eul and not extra_in_eul:
        return RiskItem(
            category='contract_mismatch',
            label='다운계약서 검사',
            status='safe',
            value='일치',
            interpretation='갑/을 목적물이 일치합니다.',
            detail=f'갑 {len(gab_set)}개 항목 = 을 {len(eul_set)}개 항목',
        )

    mismatches = []
    if missing_in_eul:
        mismatches.append(f"을에 없는 항목: {', '.join(sorted(missing_in_eul))}")
    if extra_in_eul:
        mismatches.append(f"을에 추가된 항목: {', '.join(sorted(extra_in_eul))}")

    return RiskItem(
        category='contract_mismatch',
        label='다운계약서 검사',
        status='danger',
        value='불일치',
        interpretation='갑/을 목적물이 일치하지 않아 다운계약서 의심됩니다.',
        detail=' | '.join(mismatches),
    )
