#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업 재무·공시 이상징후 탐정 - 검증된 분석 결과 기반 한국어 브리핑 생성 모듈
담당: 임도윤
"""

import argparse
import decimal
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows 콘솔 환경 등에서 UTF-8 출력 보장
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# 필수 필드 목록
REQUIRED_FIELDS = [
    "company_name",
    "period_previous",
    "period_current",
    "metric_name",
    "current_value",
    "data_source",
    "validated",
]


def load_input_data(file_path: Path) -> Dict[str, Any]:
    """
    JSON 입력 파일을 로드하고 기본 구조(items 키)를 검증합니다.
    실패 시 종료 코드 1로 종료합니다.
    """
    if not file_path.exists() or not file_path.is_file():
        sys.stderr.write(f"오류: 입력 파일을 찾을 수 없습니다. 경로: {file_path}\n")
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"오류: JSON 형식이 올바르지 않습니다. 상세: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"오류: 파일을 읽는 도중 오류가 발생했습니다. 상세: {e}\n")
        sys.exit(1)

    if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
        sys.stderr.write("오류: JSON 최상위에 'items' 배열이 누락되었거나 올바르지 않습니다.\n")
        sys.exit(1)

    return data


def is_valid_number(val: Any) -> bool:
    """
    값이 유효한 숫자인지 확인합니다 (bool 제외, NaN/Inf 제외).
    """
    if val is None or isinstance(val, bool):
        return False
    if isinstance(val, (int, float, Decimal)):
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return False
        return True
    return False


def to_decimal(val: Any) -> Decimal:
    """
    값을 Decimal 객체로 변환합니다.
    """
    return Decimal(str(val))


def validate_item_basic(item: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    항목의 검증 여부, 필수값 누락, 숫자 유효성을 검사합니다.
    반환값: (통과 여부, 제외 카테고리, 사유)
    카테고리: 'unvalidated', 'missing_field', 'invalid_number'
    """
    # 1. 검증 여부 확인 (JSON boolean true만 허용)
    validated = item.get("validated")
    if not (isinstance(validated, bool) and validated is True):
        return False, "unvalidated", f"검증되지 않음 (validated={validated})"

    # 2. 필수값 누락 확인
    for field in REQUIRED_FIELDS:
        if field not in item:
            return False, "missing_field", f"필수 필드 누락: '{field}'"
        val = item[field]
        if val is None:
            return False, "missing_field", f"필수 필드 값 없음(null): '{field}'"
        if isinstance(val, str) and not val.strip():
            return False, "missing_field", f"필수 필드 빈 문자열: '{field}'"

    # 3. 숫자 검사
    cur_val = item.get("current_value")
    if not is_valid_number(cur_val):
        return False, "invalid_number", f"현재 값(current_value)이 유효한 숫자가 아님: {cur_val}"

    if "previous_value" in item and item["previous_value"] is not None:
        prev_val = item["previous_value"]
        if not is_valid_number(prev_val):
            return False, "invalid_number", f"이전 값(previous_value)이 유효한 숫자가 아님: {prev_val}"

    if "change_rate_pct" in item and item["change_rate_pct"] is not None:
        rate_val = item["change_rate_pct"]
        if not is_valid_number(rate_val):
            return False, "invalid_number", f"증감률(change_rate_pct)이 유효한 숫자가 아님: {rate_val}"

    return True, None, None


def calculate_and_verify_change_rate(
    item: Dict[str, Any]
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    """
    증감률을 재계산하고 입력된 증감률과의 정합성을 검증합니다.
    반환값: (통과 여부, 표시용 증감률/증감액 문자열, 불일치 상세 정보, 제외 사유)
    """
    item_id = str(item.get("item_id", "ID_미지정"))
    cur_val_dec = to_decimal(item["current_value"])
    has_prev = "previous_value" in item and item["previous_value"] is not None
    has_input_rate = "change_rate_pct" in item and item["change_rate_pct"] is not None

    # 이전 값이 없는 경우
    if not has_prev:
        if has_input_rate:
            mismatch = {
                "item_id": item_id,
                "input_rate": item["change_rate_pct"],
                "calculated_rate": "산출 불가(이전 값 없음)",
                "diff": "산출 불가",
                "reason": "이전 값이 없으나 입력 증감률이 존재함",
            }
            return False, None, mismatch, "이전 값이 없으나 입력 증감률이 존재함"
        return True, "산출 불가(이전 값 0 또는 없음)", None, None

    prev_val_dec = to_decimal(item["previous_value"])

    # 이전 값이 0인 경우
    if prev_val_dec == Decimal("0"):
        if has_input_rate:
            mismatch = {
                "item_id": item_id,
                "input_rate": item["change_rate_pct"],
                "calculated_rate": "산출 불가(이전 값 0)",
                "diff": "산출 불가",
                "reason": "이전 값이 0이나 입력 증감률이 존재함",
            }
            return False, None, mismatch, "이전 값이 0이나 입력 증감률이 존재함"
        return True, "산출 불가(이전 값 0 또는 없음)", None, None

    unit = item.get("unit", "")
    unit_str = f" {unit}" if unit else ""

    # 이전 값이 음수인 경우
    if prev_val_dec < Decimal("0"):
        diff_amount = cur_val_dec - prev_val_dec
        display_str = f"절대 증감액: {diff_amount:+,.0f}{unit_str} (※ 이전 값이 음수이므로 증감률 대신 절대 증감액 표시)"
        return True, display_str, None, None

    # 이전 값이 양수인 경우: 증감률 재계산 ((현재 - 이전) / |이전|) * 100
    calc_rate = ((cur_val_dec - prev_val_dec) / abs(prev_val_dec)) * Decimal("100")
    calc_rate_rounded = calc_rate.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    if has_input_rate:
        input_rate_dec = to_decimal(item["change_rate_pct"])
        rate_diff = abs(input_rate_dec - calc_rate_rounded)
        if rate_diff > Decimal("0.1"):
            mismatch = {
                "item_id": item_id,
                "input_rate": item["change_rate_pct"],
                "calculated_rate": float(calc_rate_rounded),
                "diff": float(rate_diff.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
                "reason": f"입력값({item['change_rate_pct']}%)과 재계산값({calc_rate_rounded}%) 차이가 0.1%p 초과",
            }
            return False, None, mismatch, f"증감률 불일치 (차이: {rate_diff:.1f}%p)"
        # 허용 범위 내 일치: 입력 증감률 표시
        display_str = f"{input_rate_dec:+.1f}%"
        return True, display_str, None, None
    else:
        # 입력 증감률이 없는 경우: 재계산값에 "(코드 재계산)" 표기
        display_str = f"{calc_rate_rounded:+.1f}% (코드 재계산)"
        return True, display_str, None, None


def format_number(val: Any, unit: Optional[str] = None) -> str:
    """
    숫자를 천단위 구분기호와 함께 포맷팅합니다.
    """
    if val is None:
        return "없음"
    dec = to_decimal(val)
    # 정수 여부 확인
    if dec == dec.to_integral():
        formatted = f"{int(dec):,}"
    else:
        formatted = f"{dec:,}"
    if unit:
        return f"{formatted} {unit}"
    return formatted


def format_disclosure_date(dt_str: Any) -> str:
    """
    접수일자를 YYYY-MM-DD 형식으로 변환합니다.
    """
    if not isinstance(dt_str, str):
        dt_str = str(dt_str)
    dt_str = dt_str.strip()
    if re.fullmatch(r"\d{8}", dt_str):
        return f"{dt_str[:4]}-{dt_str[4:6]}-{dt_str[6:]}"
    return dt_str


def format_disclosure(disc: Dict[str, Any]) -> str:
    """
    개별 공시 항목을 포맷팅합니다.
    """
    title = disc.get("title", "(제목 없음)")
    rcept_dt = format_disclosure_date(disc.get("rcept_dt", "-"))
    rcept_no = disc.get("rcept_no")

    if isinstance(rcept_no, str) and re.fullmatch(r"\d{14}", rcept_no.strip()):
        rcept_no_clean = rcept_no.strip()
        link_str = f"[원문 보기](https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no_clean})"
    else:
        link_str = "접수번호 확인 필요"

    return f"- **{title}** (접수일: {rcept_dt}) | {link_str}"


def generate_briefing_markdown(
    data: Dict[str, Any],
    valid_items: List[Tuple[Dict[str, Any], str]],
    excluded_items: Dict[str, List[Dict[str, Any]]],
) -> str:
    """
    검증된 항목들과 제외된 항목 요약을 결합하여 최종 Markdown 브리핑을 생성합니다.
    """
    lines: List[str] = []

    # 가상 예시 데이터 여부 확인
    is_sample = data.get("is_sample", False)
    if is_sample:
        lines.append("※ 가상 예시 데이터\n")

    lines.append("# 기업 재무·공시 브리핑\n")
    lines.append("본 브리핑은 검증된 분석 결과를 바탕으로 작성되었으며, 변화가 확인된 항목은 '추가 확인 후보'로 제시합니다.\n")

    # 1. 브리핑 본문 (검증 통과 항목)
    if not valid_items:
        lines.append("## 분석 결과 요약\n")
        lines.append("검증을 통과한 분석 항목이 없습니다.\n")
    else:
        lines.append("## 주요 지표 변화 분석\n")
        for idx, (item, rate_str) in enumerate(valid_items, 1):
            comp_name = item.get("company_name", "-")
            metric = item.get("metric_name", "-")
            period_prev = item.get("period_previous", "-")
            period_cur = item.get("period_current", "-")
            unit = item.get("unit")
            prev_val_str = format_number(item.get("previous_value"), unit)
            cur_val_str = format_number(item.get("current_value"), unit)
            data_src = item.get("data_source", "-")

            lines.append(f"### {idx}. {comp_name} - {metric}")
            lines.append(f"- **분석 기간**: {period_prev} → {period_cur}")
            lines.append(f"- **지표명**: {metric}")
            lines.append(f"- **이전 값**: {prev_val_str}")
            lines.append(f"- **현재 값**: {cur_val_str}")
            lines.append(f"- **증감률/증감액**: {rate_str}")
            lines.append(f"- **데이터 출처**: {data_src}")
            lines.append(f"- **종합 판정**: 추가 확인 후보")

            disclosures = item.get("disclosures", [])
            if disclosures and isinstance(disclosures, list):
                lines.append("- **관련 공시**:")
                for d in disclosures:
                    if isinstance(d, dict):
                        lines.append(f"  {format_disclosure(d)}")
            lines.append("")

    # 2. 제외된 항목 요약
    lines.append("## 제외된 항목 요약\n")
    unvalidated = excluded_items.get("unvalidated", [])
    missing_field = excluded_items.get("missing_field", [])
    invalid_number = excluded_items.get("invalid_number", [])
    rate_mismatch = excluded_items.get("rate_mismatch", [])

    lines.append(f"- **미검증**: {len(unvalidated)}건")
    for item in unvalidated:
        lines.append(f"  - [{item['item_id']}] {item['reason']}")

    lines.append(f"- **필수값 누락**: {len(missing_field)}건")
    for item in missing_field:
        lines.append(f"  - [{item['item_id']}] {item['reason']}")

    lines.append(f"- **숫자 오류**: {len(invalid_number)}건")
    for item in invalid_number:
        lines.append(f"  - [{item['item_id']}] {item['reason']}")

    lines.append(f"- **증감률 불일치**: {len(rate_mismatch)}건")
    for item in rate_mismatch:
        lines.append(
            f"  - [{item['item_id']}] 입력: {item.get('input_rate')}, "
            f"재계산: {item.get('calculated_rate')}, 차이: {item.get('diff')} "
            f"({item.get('reason', '')})"
        )

    return "\n".join(lines)


def process_briefing(input_path: Path, output_path: Optional[Path] = None) -> int:
    """
    전체 브리핑 처리 파이프라인을 실행합니다.
    """
    data = load_input_data(input_path)
    items = data.get("items", [])

    valid_items: List[Tuple[Dict[str, Any], str]] = []
    excluded_items: Dict[str, List[Dict[str, Any]]] = {
        "unvalidated": [],
        "missing_field": [],
        "invalid_number": [],
        "rate_mismatch": [],
    }

    for item in items:
        if not isinstance(item, dict):
            excluded_items["invalid_number"].append({
                "item_id": "형식_오류",
                "reason": "항목이 JSON 객체가 아님",
            })
            continue

        item_id = str(item.get("item_id", "ID_미지정"))

        # 1. 기본 검증 (검증 여부, 필수값 누락, 숫자 검사)
        is_basic_valid, category, reason = validate_item_basic(item)
        if not is_basic_valid:
            excluded_items[category].append({
                "item_id": item_id,
                "reason": reason or "",
            })
            continue

        # 2. 증감률 계산 및 일치 여부 검증
        is_rate_valid, rate_str, mismatch_info, rate_reason = calculate_and_verify_change_rate(item)
        if not is_rate_valid:
            excluded_items["rate_mismatch"].append(mismatch_info or {
                "item_id": item_id,
                "reason": rate_reason or "",
            })
            continue

        valid_items.append((item, rate_str or ""))

    markdown_result = generate_briefing_markdown(data, valid_items, excluded_items)

    if output_path:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_result)
        except Exception as e:
            sys.stderr.write(f"오류: 출력 파일을 저장하는 도중 오류가 발생했습니다. 상세: {e}\n")
            return 1
    else:
        sys.stdout.write(markdown_result + "\n")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="기업 재무·공시 이상징후 탐정 - 한국어 브리핑 생성 CLI"
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="검증 완료된 JSON 데이터 파일 경로",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="생성된 Markdown 브리핑을 저장할 파일 경로 (미지정 시 표준출력)",
    )

    args = parser.parse_args()
    exit_code = process_briefing(args.input, args.output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
