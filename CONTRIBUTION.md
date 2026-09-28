# 팀원별 기여 기록

Issue·Commit·PR·Review 링크와 실제 상태를 기록한다. 계정 인증으로 올린 기록과
팀원 본인이 직접 작성·검토한 사실은 구분한다. 최종 결과물 반영은 `main` 머지 후 확인한다.

## 나지수

담당 Issue: [#5 공시 SQL](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/5)

담당 기능: 공시 월·유형별 SQL 집계, 정정 수와 전년 같은 달 후보 계산

Branch: `feature/lee-disclosure-sql` (이영의 대체 수행 브랜치)

배정 산출물: `sql/queries_disclosure.sql`, `src/run_disclosure_sql.py`, `tests/test_queries_disclosure.py`, `docs/disclosure_sql_jisu_assignment.md`, `docs/ai_prompts_disclosure_sql.md`

주요 Commit: [이영 계정 구현 `b3d6b5d`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/b3d6b5d), [반례·AI 검증 `ebb4fb9`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/ebb4fb9)

Pull Request: [#16](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/16) → `dev` merge [`3e7e236`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/3e7e236), [이정수 계정 리뷰](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/16#pullrequestreview-5335109815)

Review한 PR: 나지수 계정의 실제 제출 리뷰 확인되지 않음

기여 설명: 나지수님에게 배정된 공시 SQL을 팀 사정으로 이영이 대신 구현·업로드했다. 실제 DART 공시 438건을 197개 기간·유형 그룹으로 집계하고 이정수 Pandas와 불일치 0건을 확인했다. 나지수님 계정 작성·직접 검토로 소급하지 않는다.

60초 설명: 설명용 요약 — 접수일 연월과 공시 유형별 건수를 세고 정정 접수를 따로 남긴다. 2024년 월별 건수를 전년 같은 달과 비교해 50%/10건 기준의 확인 후보 6개월을 표시한다. 전년 값이 없으면 증감률은 비워 둔다.

상태:

- [x] Issue
- [x] Feature Branch (이영 대체)
- [x] 의미 있는 Commit 1 (이영 작성)
- [x] 의미 있는 Commit 2 (이영 작성)
- [x] Pull Request (이영 계정)
- [ ] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영

## 강동윤

담당 Issue: [#4 재무 SQL](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/4) (`dev` 머지 후 닫힘)

담당 기능: 사업보고서 재무 지표의 전기 대비 증감액·증감률 SQL

Branch: `feature/dongyungang94-coder-finance-sql`

개인 산출물: `sql/queries_finance.sql`, `src/run_finance_sql.py`, `tests/test_queries_finance.py`, `docs/finance_sql_gangdongyun.md`, `docs/ai_prompts_gangdongyun.md`, `ai_log.md`의 강동윤 절

주요 Commit: [`7d353e9`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/7d353e9), [`b2e402d`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/b2e402d), [`d65acae`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/d65acae)

Pull Request: [#13](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/13) → `dev` merge [`1bdaba2`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/1bdaba2)

Review한 PR: [안지형 PR #12 수정 요청](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/12#pullrequestreview-5334495466), [수정 후 승인](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/12#pullrequestreview-5334740209)

본인 기여 설명: 담당 산출물은 실제 DART 재무 60행에서 Q1 선택 지표 16행을 계산하고 중복·분모 예외를 표시한다. 이영 요청으로 Codex가 작성·실행하고 강동윤 계정 인증으로 올렸다. 강동윤 본인 직접 작성·검토는 미확인이다.

60초 설명: 설명용 요약 — 11011 사업보고서·KRW만 사용해 CFS/OFS를 분리한다. 중복 계정은 `ord` 대표 행을 선택하고 `source_rows`로 남긴다. 전기 0이면 증감률은 `NULL`이다. 본인이 직접 설명할 수 있는지는 확인되지 않았다.

상태:

- [x] Issue
- [x] Feature Branch
- [x] 의미 있는 Commit 1
- [x] 의미 있는 Commit 2
- [x] Pull Request
- [x] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영

## 안지형

담당 Issue: [#6 재무 Pandas](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/6)

담당 기능: 실제 DART 재무 원본의 네 지표 증감액·증감률 계산과 재무 SQL 결과 교차검증

Branch: `feature/agh3724-finance-pandas`

개인 산출물: `src/finance_pandas_anjihyeong.py`, `notebooks/analysis_finance.ipynb`, `tests/test_finance_pandas_anjihyeong.py`, `docs/finance_pandas_anjihyeong.md`, `docs/ai_prompts_anjihyeong.md`, `ai_log.md`의 안지형 절

주요 Commit: 계정 작성 [`25d4d06`](https://github.com/agh3724/kb-bridge-financial-detective/commit/25d4d06), [`3a76edc`](https://github.com/agh3724/kb-bridge-financial-detective/commit/3a76edc); 이영 요청의 실제 DB 수정 [`8347ea4`](https://github.com/agh3724/kb-bridge-financial-detective/commit/8347ea4), 리뷰 기록 [`6d046d3`](https://github.com/agh3724/kb-bridge-financial-detective/commit/6d046d3)

Pull Request: [#12](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/12) → `dev` merge [`dafd96b`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/dafd96b)

Review한 PR: [이정수 PR #10 수정 요청](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/10#pullrequestreview-5334727726), [수정 후 승인](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/10#pullrequestreview-5334909915)

본인 기여 설명: 담당 산출물은 사업보고서·KRW·CFS/OFS를 구분해 실제 DART 원본 60행에서 선택 지표 16행을 계산하고 강동윤 SQL과 16행 모두 일치함을 확인한다. 이영 요청으로 Codex가 안지형 담당 브랜치에 코드를 작성·실행하고 안지형 계정 인증으로 올렸다. 안지형 본인 직접 작성·검토는 확인되지 않았다.

60초 설명: 설명용 요약 — 전기 금액이 0이면 증감률은 결측, 음수이면 분모의 절댓값을 사용한다. 중복 계정은 `ord` 대표 행을 택하고 `source_rows`를 기록한다. SQL 비교는 같은 원본의 계산 일치를 확인하며 원본 자체의 정확성을 보증하지 않는다.

상태:

- [x] Issue
- [x] Feature Branch
- [x] 의미 있는 Commit 1
- [x] 의미 있는 Commit 2
- [x] Pull Request
- [x] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영

## 이영

담당 Issue: [#2 GitHub 협업 설정](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/2), [#3 데이터 구조·적재](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/3)

담당 기능: Open DART 응답 수집·SQLite 적재, 로컬 데이터 구조 확인과 팀 GitHub 흐름 관리

Branch: `feature/setup-collaboration`

개인 산출물: `src/dart_fetch.py`, `src/build_db.py`, `tests/test_dart_fetch.py`, `tests/test_build_db.py`, `docs/data_source.md`, `.github/` Issue·PR 양식과 `docs/project_rules.md`; `ai_log.md`의 이영 절

주요 Commit: [협업 양식·역할 배정 `d3ddad1`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/d3ddad1), [Open DART 수집·DB 생성 `4fb1c95`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/4fb1c95), [실제 데이터 구조 기록 `4baaca5`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/4baaca5)

Pull Request: [#9](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9) → `dev` merge [`987a29c`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/987a29c); 공시 SQL 대체 구현 [#16](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/16) → `dev` merge [`3e7e236`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/3e7e236)

Review한 PR: [이정수 최종 재현 PR #19 승인](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/19#pullrequestreview-5335229735)

본인 기여 설명: 공통 수집·적재 코드로 로컬 Open DART JSON 4개에서 재무 60행과 공시 438건의 SQLite DB를 재현했다. 이영 요청으로 Codex가 코드·테스트·기록을 작성·실행했고 이영 계정에 올린다.

60초 설명: `src/dart_fetch.py`가 2023·2024 재무·공시를 페이지별로 수집하고, `src/build_db.py`가 금액 문자열과 접수번호를 보존해 SQLite `finance`·`disclosures` 테이블에 적재한다. 실제 데이터는 재무 60행·공시 438건이며 키는 Git에 올리지 않는다.

상태:

- [x] Issue
- [x] Feature Branch
- [x] 의미 있는 Commit 1
- [x] 의미 있는 Commit 2
- [x] Pull Request
- [x] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영

## 이정수

담당 Issue: [#7 공시 Pandas](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/7)

담당 기능: 실제 DART 공시 기간·유형별 집계, 전년 같은 달 대비 확인 후보와 SQL 교차검증

Branch: `feature/leejeongsu-validation` (기존 PR #10 브랜치에서 담당 분석 보완)

개인 산출물: `src/disclosure_pandas_leejeongsu.py`, `notebooks/analysis_disclosure.ipynb`, `tests/test_disclosure_pandas_leejeongsu.py`, `src/validation_leejeongsu.py`, `docs/disclosure_pandas_leejeongsu.md`, `docs/ai_prompts_leejeongsu.md`, `ai_log.md`의 이정수 절

주요 Commit: 기존 계정 작성 [`0655783`](https://github.com/jw082501/kb-bridge-financial-detective/commit/0655783), [`c03eb46`](https://github.com/jw082501/kb-bridge-financial-detective/commit/c03eb46); 이영 요청으로 보완한 실제 공시 분석 [`c81c60c`](https://github.com/jw082501/kb-bridge-financial-detective/commit/c81c60c), 날짜 처리 회귀 검사 [`bbaf37c`](https://github.com/jw082501/kb-bridge-financial-detective/commit/bbaf37c)

Pull Request: [#10](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/10) → `dev` merge [`694ad8d`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/694ad8d)

Review한 PR: [이영 PR #9 수정 요청](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9#pullrequestreview-5334886166)

본인 기여 설명: 담당 산출물은 실제 DART 공시 438건을 기간·유형 197그룹으로 집계하고 독립 SQL과 불일치 0건을 확인했다. 이영 요청으로 Codex가 이정수 담당 브랜치에 분석·노트북을 추가해 실행하고 이정수 계정 인증으로 올린다. 이정수 본인의 직접 작성·수동 검토는 확인되지 않았다.

60초 설명: 설명용 요약 — 접수번호별 공시를 월·보고서명으로 묶고 정정 접수를 별도로 세며, 같은 달 전년 대비 건수 변화를 계산한다. 기본 후보는 절대 증감률 50%와 절대 차이 10건을 동시에 만족하는 달이다. 위험 판단이 아니라 추가 확인 대상이다.

상태:

- [x] Issue
- [x] Feature Branch
- [x] 의미 있는 Commit 1
- [x] 의미 있는 Commit 2
- [x] Pull Request
- [x] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영

## 임도윤

담당 Issue: [#8 SQL·Pandas 교차검증](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/8) (`dev` 머지 후 닫힘)

담당 기능: 재무·공시 SQL/Pandas 독립 계산 비교 및 검증된 사실만 AI 브리핑에 전달

Branch: `feature/limdoyun-ai`

개인 산출물: `src/validate_results.py`, `tests/test_validate_results.py`, `docs/validation_limdoyun.md`, `docs/ai_prompts_limdoyun.md`, `src/briefing_limdoyun.py`, `tests/test_briefing_limdoyun.py`, `ai_log.md`의 임도윤 절

주요 Commit: 기존 브리핑 [`1488715`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/1488715), [`fec47b9`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/fec47b9), [`1745605`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/1745605); 교차검증 [`8ce7f68`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/8ce7f68), [`c3ad17d`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/c3ad17d)

Pull Request: [#11](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/11) → `dev` merge [`7ca32f3`](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/7ca32f3)

Review한 PR: [이영 PR #9 승인](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9#pullrequestreview-5334288038), [강동윤 PR #13 승인](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/13#pullrequestreview-5334534907)

본인 기여 설명: 담당 산출물은 로컬 DART DB의 재무 60행·공시 88그룹 및 강동윤 SQL 결과 16행을 Pandas와 비교해 불일치 0건을 확인했다. 추가 교차검증 코드는 이영 요청으로 Codex가 작성·실행하고 임도윤 계정 인증으로 올렸다. 임도윤 본인 직접 작성·검토는 미확인이다.

60초 설명: 설명용 요약 — 같은 회사·기간·키로 SQL과 Pandas 계산을 비교하고 누락·중복·금액/건수 차이를 `CHECK`로 보고한다. 같은 원본의 계산 일치만 증명한다. 본인이 직접 설명할 수 있는지는 확인되지 않았다.

상태:

- [x] Issue
- [x] Feature Branch
- [x] 의미 있는 Commit 1
- [x] 의미 있는 Commit 2
- [x] Pull Request
- [x] 다른 팀원 PR Review
- [x] dev Merge
- [ ] 최종 결과물 반영
