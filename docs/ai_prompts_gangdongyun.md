# 강동윤 담당 AI 입력문

## 역할·도구·이행 상태

- **담당 역할:** 재무 SQL로 Q1의 매출액·영업이익·당기순이익·자산총계 전기 대비 변화를 계산한다.
- **해야 할 일:** 실제 finance 스키마 확인 → CFS/OFS·중복·금액 변환 규칙 정의 → SQL 작성 → 실제 DB 및 반례 테스트 → PR·동료 리뷰.
- **이번에 사용한 AI 도구:** Codex. 이영의 요청으로 코드·테스트·문서 작성을 지원했다. 강동윤 본인이 사용한 AI 도구는 아직 확인되지 않았다.
- **이행 증거:** `sql/queries_finance.sql`, `src/run_finance_sql.py`, `tests/test_queries_finance.py`, `docs/finance_sql_gangdongyun.md`. 실제 DB 실행 결과와 남은 검증은 마지막 문서에 기록한다.

다음은 강동윤님이 자신의 AI 도구에 **복사해 사용할 수 있도록 작성한 프롬프트**다.
현재 강동윤님이 직접 입력·검토했다는 기록은 확인되지 않았다. 입력했다면 사용한
도구·시각·AI 답변·직접 실행 결과·채택/수정/폐기 이유를 `ai_log.md`에 남긴다.
API 키나 원본 데이터 전체를 붙여넣지 않는다.

## 프롬프트 1: 재무 SQL 작성·검토

```text
나는 KB Bridge 「기업 재무·공시 이상징후 탐정」의 재무 SQL 담당이다.
Issue #4, 파일 sql/queries_finance.sql을 작업한다. SQLite finance 테이블의 실제
컬럼은 corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm, ord,
currency, thstrm_amount, frmtrm_amount이다. 금액은 쉼표가 있는 원화 문자열이며
음수도 있다. 2023·2024 사업보고서(11011)를 사용한다.
매출액·영업이익·당기순이익·자산총계의 전기 대비 증감액과 증감률을 계산하는
현재 SQL을 검토해 줘. 연결(CFS)과 별도(OFS)를 섞지 말고, 중복 account_nm,
전기 0·음수·결측, 숫자로 읽을 수 없는 문자열을 어떻게 처리하는지 지적해 줘.
실제 데이터에 없는 수치나 회사 위험 판단을 만들어내지 마.
```

## 프롬프트 2: 반례·검증 질문

```text
같은 Issue #4의 sql/queries_finance.sql과 tests/test_queries_finance.py를
검토해 줘. 매출액 1,200/1,000은 증감률 20%, 당기순이익 200/-100은
분모 절댓값 기준 300%, 전기 0이면 증감률 NULL이어야 한다.
같은 계정 두 행이 있을 때 한 행만 선택하되 source_rows=2가 남아야 한다.
연결/별도가 섞이거나 'abc'가 숫자 0으로 변환되는 오류가 없는지 확인하고,
추가로 필요한 실제 데이터 검증 쿼리와 반례를 제안해 줘.
AI의 답변을 실행 없이 정답으로 표시하지 마. 검증할 명령과 예상 결과를 분리해 줘.
```

## 직접 확인할 기록

1. `python -m src.run_finance_sql data/processed/dart.sqlite 00126380 2024 --fs-div CFS`의 4행과 원본 금액을 대조한다.
2. `python -m unittest discover -s tests -v`의 통과/실패를 기록한다.
3. AI 제안 중 실제 반영한 부분과 거절한 부분을 이유와 함께 `ai_log.md`에 쓴다.
