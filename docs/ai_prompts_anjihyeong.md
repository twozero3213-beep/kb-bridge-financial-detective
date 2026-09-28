# 안지형 담당 AI 입력문

## 역할·도구·이행 상태

- **담당 역할:** Issue #6. 재무 원본을 Pandas로 계산하고 재무 SQL과 교차검증한다.
- **해야 할 일:** 실제 스키마 확인 → 중복·CFS/OFS·금액 변환 기준 정의 → 코드와 노트북 작성 → 실제 DB 및 반례 실행 → PR·동료 리뷰.
- **실제 사용한 AI 도구:** Codex 데스크톱. 이영의 요청으로 산출물을 작성·실행했다. 안지형 본인이 사용한 도구와 직접 입력은 확인되지 않았다.
- **이행 증거:** `src/finance_pandas_anjihyeong.py`, `notebooks/analysis_finance.ipynb`, `tests/test_finance_pandas_anjihyeong.py`, `docs/finance_pandas_anjihyeong.md`, PR #12.

아래 두 입력문은 안지형님이 자기 AI 도구에서 사용할 수 있도록 작성한 **배포용 초안**이다. 실제로 입력했다고 표시하지 않는다. 직접 사용하면 도구·시각·응답·실행 결과·수정 또는 채택 이유를 `ai_log.md`에 추가한다. API 키와 비공개 원본은 입력하지 않는다.

## 프롬프트 1: Pandas 계산 검토

```text
나는 KB Bridge 기업 재무·공시 이상징후 탐정의 재무 Pandas 담당이다.
Issue #6, src/finance_pandas_anjihyeong.py와 notebooks/analysis_finance.ipynb를
검토해 줘. SQLite finance 테이블의 실제 컬럼은 corp_code, bsns_year,
reprt_code, fs_div, sj_div, account_nm, ord, currency, thstrm_amount,
frmtrm_amount이다. 사업보고서(11011)·KRW에서 네 지표의 전기 대비 증감액과
증감률을 계산한다. CFS/OFS 혼합, 계정 중복, 쉼표 있는 음수 금액, 전기 0,
결측에 따른 오류를 찾아 수정안을 제안해 줘. 원본에 없는 금액은 만들지 마.
```

## 프롬프트 2: SQL 교차검증과 반례

```text
Issue #6의 Pandas 결과와 Issue #4의 sql/queries_finance.sql을 같은 SQLite
원본으로 비교해 줘. 키는 회사·사업연도·보고서·CFS/OFS·재무제표 종류·계정이다.
현재/전기 금액, 증감액, 증감률, source_rows가 맞아야 한다.
전기 -100에서 당기 200은 +300%, 전기 0은 증감률 결측, 같은 계정 두 행은
대표 한 행과 source_rows=2가 되어야 한다. SQL/Pandas 양쪽이 같은 오류를
가질 수 있으므로 원본 금액 확인 방법과 반례 검사를 함께 제시해 줘.
AI 답변은 실행 전 정답으로 기록하지 마.
```

## 직접 확인할 기록

1. 노트북을 실행해 재무 원본 60행, 선택 지표 16행, SQL 불일치 0건인지 확인한다.
2. `python -m unittest discover -s tests -v`의 결과를 기록한다.
3. AI 답변 중 반영·거절한 내용을 실제 입력과 구분해 `ai_log.md`에 쓴다.
