# 나지수 배정 공시 SQL AI 입력문

## 역할·도구·이행

- **배정 역할:** Issue #5 공시 SQL. 실제 대체 구현자는 이영이며 나지수님의 AI 도구 직접 사용은 확인되지 않았다.
- **필요 작업:** 실제 `disclosures` 스키마·접수번호·접수일 확인 → 월·유형·정정 집계 SQL → 전년 같은 달 변화 → 이정수 Pandas와 비교 → 반례·PR.
- **실제 AI 도구:** Codex 데스크톱. 이영이 요청하고 Codex가 SQL·실행기·검사·문서를 작성·실행했다.
- **이행 증거:** `sql/queries_disclosure.sql`, `src/run_disclosure_sql.py`, `tests/test_queries_disclosure.py`, `docs/disclosure_sql_jisu_assignment.md`.

아래는 역할 담당자가 재현·점검에 사용할 수 있는 **복사용 프롬프트 초안**이다. 실제 나지수님 입력으로 기록하지 않는다. 키나 원본 JSON 전체는 입력하지 않는다.

## 프롬프트 1: 공시 SQL 설계

```text
나는 KB Bridge 기업 재무·공시 이상징후 탐정의 공시 SQL 배정 역할을 검토한다.
Issue #5, SQLite disclosures의 실제 컬럼은 corp_code, rcept_no, rcept_dt,
report_nm 등이다. 삼성전자 00126380의 2023·2024 접수 공시를 사용한다.
접수번호 한 개를 한 건으로 세고 YYYYMMDD 접수일을 연월로, 보고서명은 양쪽
공백을 제거해 유형으로 집계하는 SQL을 검토해 줘. 정정·첨부추가 접수는 포함하되
별도 수를 표시한다. 2024년 월별 수를 2023년 같은 달과 비교할 때 전년 값이
없거나 0인 경우 NULL 처리해 줘. 실제 없는 컬럼·수치·기업 위험 판단을 만들지 마.
```

## 프롬프트 2: SQL/Pandas 비교와 반례

```text
sql/queries_disclosure.sql의 기간·유형 197그룹과
src/disclosure_pandas_leejeongsu.py의 결과를 회사·연월·유형 키로 비교해 줘.
접수 건수와 정정 건수가 모두 같아야 한다. 월 합계·전년 같은 달 건수·증감률·
후보 50%/10건 기준도 비교한다. 전년 월이 없는 회사는 전기 유무를 먼저
대조한 다음 계산 가능한 행만 수치 비교해 줘. 접수번호 중복, 20241340 같은
잘못된 날짜, 빈 보고서명 반례를 제시하고 실행 결과 없이 정답으로 표시하지 마.
```

실제 요청·AI 출력·직접 실행과 수정 이유는 `ai_log.md`에 별도로 기록한다.
