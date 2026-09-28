# 이정수 담당 AI 입력문

## 역할·도구·이행

- **담당:** Issue #7, 기간·유형별 공시 Pandas 패턴과 SQL 교차검증.
- **필요 작업:** 실제 `disclosures` 스키마 확인 → 접수일·유형·정정 정책 → Pandas 집계와 전년 같은 달 비교 → SQL과 실제 결과 비교 → 반례·노트북·PR 리뷰.
- **이번에 확인된 AI 도구:** Codex 데스크톱. 이영이 요청했고 Codex가 추가 코드·문서·검사를 작성·실행했다. 기존 PR #10의 범용 검증 코드에 쓰인 AI 도구 이름과 이정수 본인의 직접 입력은 확인되지 않았다.
- **실행 증거:** `src/disclosure_pandas_leejeongsu.py`, `notebooks/analysis_disclosure.ipynb`, `tests/test_disclosure_pandas_leejeongsu.py`, `docs/disclosure_pandas_leejeongsu.md`.

아래는 이정수님이 자신의 AI 도구에 **복사해 사용할 수 있도록 작성한 프롬프트 초안**이다. 실제 이정수님 입력이라고 주장하지 않는다. 직접 사용했다면 사용 도구·시각·답변·직접 실행 결과·채택/수정/폐기 판단을 `ai_log.md`에 추가한다. API 키나 비공개 원본은 넣지 않는다.

## 프롬프트 1: 공시 Pandas 분석

```text
나는 KB Bridge 기업 재무·공시 이상징후 탐정의 공시 Pandas 담당이다.
Issue #7과 src/disclosure_pandas_leejeongsu.py를 검토해 줘.
SQLite disclosures의 실제 컬럼은 corp_code, rcept_no, rcept_dt, report_nm
등이다. 접수일 YYYYMMDD의 연월과 공백을 정리한 보고서명으로 접수 건수를
집계한다. 정정 공시는 별도 접수로 포함하고 수를 따로 표시한다.
접수번호 중복, 잘못된 날짜, 빈 보고서명, 기간 경계에서 오류를 찾아 줘.
같은 달 전년 건수와 비교하고 이전 기간이 없으면 증감률을 비워 둬.
실제 결과에 없는 공시 사건이나 위험 원인을 만들지 마.
```

## 프롬프트 2: SQL 비교·후보 민감도

```text
Issue #7의 notebooks/analysis_disclosure.ipynb와 공시 SQL 집계를
회사·연월·보고서명 키로 비교해 줘. 접수 건수와 정정 건수가 일치해야 한다.
2024년 9월 31건, 전년 같은 달 4건이면 +27건, +675%다.
기본 확인 후보는 절대 증감률 50% 이상 그리고 건수 차이 10건 이상이며
100% 기준으로 바뀔 때 어떤 월이 달라지는지도 계산해 줘.
정정 접수 포함 여부와 데이터 범위를 명시하고 기업 위험 판단은 보류해 줘.
실행 명령, 예상 결과, AI 답변을 검증할 원본 쿼리를 나눠 제시해 줘.
```

## 직접 남길 검증 기록

1. 실제 DB에서 공시 438건, 기간·유형 197그룹, SQL 불일치 0건을 재확인한다.
2. `python -m unittest discover -s tests -v`의 결과와 발견된 오류를 기록한다.
3. GitHub Issue·브랜치·커밋·PR·다른 팀원 리뷰 링크를 `CONTRIBUTION.md`에 반영한다.
