#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업 재무·공시 이상징후 탐정 - 브리핑 생성 단위 및 통합 테스트
담당: 임도윤
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# 테스트 대상 모듈 경로 추가
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.briefing_limdoyun import (
    calculate_and_verify_change_rate,
    format_disclosure,
    generate_briefing_markdown,
    is_valid_number,
    load_input_data,
    process_briefing,
    validate_item_basic,
)


class TestBriefingLimdoyun(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.script_path = REPO_ROOT / "src" / "briefing_limdoyun.py"

    def test_case1_valid_item(self):
        """케이스 1: 정상 항목이 브리핑 본문에 포함되고 올바른 형식으로 출력되는지 검증"""
        item = {
            "item_id": "VAL-001",
            "company_name": "(가상) 우주항공",
            "corp_code": "00123456",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출채권",
            "unit": "원",
            "previous_value": 1000000000,
            "current_value": 1500000000,
            "change_rate_pct": 50.0,
            "data_source": "Open DART 반기보고서 재무제표",
            "validated": True,
            "validated_by": "검증담당자",
            "disclosures": [
                {
                    "title": "(가상) 반기보고서",
                    "rcept_dt": "20260814",
                    "rcept_no": "20260814000123",
                }
            ],
        }

        # 기본 유효성 검사
        is_basic_valid, cat, reason = validate_item_basic(item)
        self.assertTrue(is_basic_valid)
        self.assertIsNone(cat)

        # 증감률 검사
        is_rate_valid, rate_str, mismatch, rate_reason = calculate_and_verify_change_rate(item)
        self.assertTrue(is_rate_valid)
        self.assertEqual(rate_str, "+50.0%")
        self.assertIsNone(mismatch)

        # 마크다운 생성 검증
        data = {"schema_version": "0.1", "is_sample": True, "items": [item]}
        markdown = generate_briefing_markdown(
            data,
            valid_items=[(item, rate_str)],
            excluded_items={"unvalidated": [], "missing_field": [], "invalid_number": [], "rate_mismatch": []},
        )

        self.assertIn("※ 가상 예시 데이터", markdown)
        self.assertIn("### 1. (가상) 우주항공 - 매출채권", markdown)
        self.assertIn("1,000,000,000 원", markdown)
        self.assertIn("1,500,000,000 원", markdown)
        self.assertIn("+50.0%", markdown)
        self.assertIn("종합 판정**: 추가 확인 후보", markdown)
        self.assertIn("https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260814000123", markdown)
        self.assertIn("접수일: 2026-08-14", markdown)

    def test_case2_missing_file(self):
        """케이스 2: 입력 파일 경로 없음 -> 종료 코드 1 및 한국어 오류 메시지"""
        non_existent_file = REPO_ROOT / "tests" / "non_existent_file_sample_98765.json"
        cmd = [sys.executable, str(self.script_path), "--input", str(non_existent_file)]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

        self.assertEqual(res.returncode, 1)
        self.assertIn("오류: 입력 파일을 찾을 수 없습니다", res.stderr)

    def test_case3_corrupted_json(self):
        """케이스 3: 깨진 JSON 및 items 누락 JSON -> 종료 코드 1"""
        # 깨진 JSON 테스트
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{ invalid_json: true, ")
            broken_path = Path(f.name)

        try:
            cmd = [sys.executable, str(self.script_path), "--input", str(broken_path)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 1)
            self.assertIn("JSON 형식이 올바르지 않습니다", res.stderr)
        finally:
            if broken_path.exists():
                broken_path.unlink()

        # items 누락 JSON 테스트
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(json.dumps({"schema_version": "0.1"}))
            no_items_path = Path(f.name)

        try:
            cmd = [sys.executable, str(self.script_path), "--input", str(no_items_path)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 1)
            self.assertIn("'items' 배열이 누락되었거나", res.stderr)
        finally:
            if no_items_path.exists():
                no_items_path.unlink()

    def test_case4_missing_required_fields(self):
        """케이스 4: 필수값 누락 -> 제외 및 사유 보고"""
        base_item = {
            "item_id": "REQ-001",
            "company_name": "테스트기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출액",
            "current_value": 1000,
            "data_source": "Open DART",
            "validated": True,
        }

        required_keys = [
            "company_name",
            "period_previous",
            "period_current",
            "metric_name",
            "current_value",
            "data_source",
            "validated",
        ]

        for req in required_keys:
            test_item = base_item.copy()
            del test_item[req]
            is_valid, cat, reason = validate_item_basic(test_item)
            self.assertFalse(is_valid, f"{req} 누락 시 유효하지 않아야 함")
            self.assertEqual(cat, "missing_field" if req != "validated" else "unvalidated")
            self.assertIsNotNone(reason)

        # 빈 문자열 테스트
        blank_item = base_item.copy()
        blank_item["company_name"] = "   "
        is_valid, cat, reason = validate_item_basic(blank_item)
        self.assertFalse(is_valid)
        self.assertEqual(cat, "missing_field")

    def test_case5_invalid_number_strings(self):
        """케이스 5: 숫자 자리에 문자열("1,000", "abc") 및 NaN/Inf -> 제외"""
        base_item = {
            "item_id": "NUM-001",
            "company_name": "테스트기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출액",
            "current_value": 1000,
            "previous_value": 500,
            "data_source": "Open DART",
            "validated": True,
        }

        invalid_vals = ["1,000", "abc", float("nan"), float("inf"), [100], {"val": 10}]
        for inval in invalid_vals:
            # current_value가 숫자가 아닌 경우
            t1 = base_item.copy()
            t1["current_value"] = inval
            is_valid, cat, reason = validate_item_basic(t1)
            self.assertFalse(is_valid)
            self.assertEqual(cat, "invalid_number")

            # previous_value가 숫자가 아닌 경우
            t2 = base_item.copy()
            t2["previous_value"] = inval
            is_valid, cat, reason = validate_item_basic(t2)
            self.assertFalse(is_valid)
            self.assertEqual(cat, "invalid_number")

    def test_case6_validated_variations(self):
        """케이스 6: validated가 false, "true", 1, null, 누락 -> 모두 미검증으로 제외"""
        base_item = {
            "item_id": "VAL-TEST",
            "company_name": "테스트기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출액",
            "current_value": 1000,
            "data_source": "Open DART",
        }

        invalid_validated = [False, "true", "True", 1, 0, None]
        for val in invalid_validated:
            t = base_item.copy()
            t["validated"] = val
            is_valid, cat, reason = validate_item_basic(t)
            self.assertFalse(is_valid, f"validated={val} 는 제외되어야 함")
            self.assertEqual(cat, "unvalidated")

        # validated 키 누락
        t_missing = base_item.copy()
        is_valid, cat, reason = validate_item_basic(t_missing)
        self.assertFalse(is_valid)
        self.assertEqual(cat, "unvalidated")

    def test_case7_growth_rate_mismatch(self):
        """케이스 7: 입력 증감률이 재계산값과 0.1%p 초과 차이 시 제외 및 불일치 보고"""
        # 재계산값: (1500 - 1000) / 1000 * 100 = 50.0%
        item_mismatch = {
            "item_id": "RATE-DIFF",
            "company_name": "차이기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "영업이익",
            "previous_value": 1000,
            "current_value": 1500,
            "change_rate_pct": 40.0,  # 10%p 차이
            "data_source": "Open DART",
            "validated": True,
        }

        is_valid, rate_str, mismatch, reason = calculate_and_verify_change_rate(item_mismatch)
        self.assertFalse(is_valid)
        self.assertIsNone(rate_str)
        self.assertIsNotNone(mismatch)
        self.assertEqual(mismatch["item_id"], "RATE-DIFF")
        self.assertEqual(mismatch["input_rate"], 40.0)
        self.assertEqual(mismatch["calculated_rate"], 50.0)
        self.assertEqual(mismatch["diff"], 10.0)

        # 허용 범위 내 차이 (0.1%p 이하: 예: 50.05% -> 반올림 50.1% vs 입력 50.0%)
        item_match = item_mismatch.copy()
        item_match["change_rate_pct"] = 50.09  # 차이 0.09%p <= 0.1%p
        is_valid_m, rate_str_m, mismatch_m, _ = calculate_and_verify_change_rate(item_match)
        self.assertTrue(is_valid_m)
        self.assertIsNone(mismatch_m)

    def test_case8_previous_value_zero_null_negative(self):
        """케이스 8: 이전 값 0 / 이전 값 null / 이전 값 음수 처리 규칙 검증"""
        # 1. 이전 값 0, 입력 증감률 없음 -> "산출 불가(이전 값 0 또는 없음)"
        item_zero = {
            "item_id": "ZERO-001",
            "company_name": "제로기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출액",
            "previous_value": 0,
            "current_value": 1000,
            "data_source": "Open DART",
            "validated": True,
        }
        is_valid, rate_str, mismatch, _ = calculate_and_verify_change_rate(item_zero)
        self.assertTrue(is_valid)
        self.assertEqual(rate_str, "산출 불가(이전 값 0 또는 없음)")

        # 1-1. 이전 값 0인데 입력 증감률 존재 -> 불일치로 제외
        item_zero_with_rate = item_zero.copy()
        item_zero_with_rate["change_rate_pct"] = 100.0
        is_valid_z, _, mismatch_z, _ = calculate_and_verify_change_rate(item_zero_with_rate)
        self.assertFalse(is_valid_z)
        self.assertIsNotNone(mismatch_z)

        # 2. 이전 값 null, 입력 증감률 없음 -> "산출 불가(이전 값 0 또는 없음)"
        item_null = {
            "item_id": "NULL-001",
            "company_name": "널기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "매출액",
            "previous_value": None,
            "current_value": 1000,
            "data_source": "Open DART",
            "validated": True,
        }
        is_valid, rate_str, mismatch, _ = calculate_and_verify_change_rate(item_null)
        self.assertTrue(is_valid)
        self.assertEqual(rate_str, "산출 불가(이전 값 0 또는 없음)")

        # 2-1. 이전 값 null인데 입력 증감률 존재 -> 불일치로 제외
        item_null_with_rate = item_null.copy()
        item_null_with_rate["change_rate_pct"] = 50.0
        is_valid_n, _, mismatch_n, _ = calculate_and_verify_change_rate(item_null_with_rate)
        self.assertFalse(is_valid_n)
        self.assertIsNotNone(mismatch_n)

        # 3. 이전 값 음수 -> 절대 증감액 및 주석 표시
        item_neg = {
            "item_id": "NEG-001",
            "company_name": "음수기업",
            "period_previous": "2025.1H",
            "period_current": "2026.1H",
            "metric_name": "영업이익",
            "unit": "원",
            "previous_value": -200,
            "current_value": 300,
            "data_source": "Open DART",
            "validated": True,
        }
        is_valid, rate_str, mismatch, _ = calculate_and_verify_change_rate(item_neg)
        self.assertTrue(is_valid)
        self.assertIn("절대 증감액: +500 원", rate_str)
        self.assertIn("이전 값이 음수이므로 증감률 대신 절대 증감액 표시", rate_str)

    def test_case9_invalid_rcept_no(self):
        """케이스 9: rcept_no 형식 오류 시 링크 미생성 및 '접수번호 확인 필요' 표시"""
        # 정상 14자리 숫자
        disc_valid = {"title": "정상보고서", "rcept_dt": "20260814", "rcept_no": "20260814000123"}
        res_valid = format_disclosure(disc_valid)
        self.assertIn("https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260814000123", res_valid)

        # 14자리 미만 숫자
        disc_short = {"title": "짧은번호", "rcept_dt": "20260814", "rcept_no": "12345"}
        res_short = format_disclosure(disc_short)
        self.assertIn("접수번호 확인 필요", res_short)
        self.assertNotIn("https://dart.fss.or.kr", res_short)

        # 문자가 섞인 14자리
        disc_char = {"title": "문자포함", "rcept_dt": "20260814", "rcept_no": "2026081400012A"}
        res_char = format_disclosure(disc_char)
        self.assertIn("접수번호 확인 필요", res_char)

        # None 또는 누락
        disc_none = {"title": "누락보고서", "rcept_dt": "20260814"}
        res_none = format_disclosure(disc_none)
        self.assertIn("접수번호 확인 필요", res_none)


if __name__ == "__main__":
    unittest.main()
