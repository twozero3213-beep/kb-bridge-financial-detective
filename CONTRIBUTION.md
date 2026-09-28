# 팀원별 기여 기록

Issue·Commit·PR·Review 링크와 실제 상태를 기록한다. 계정 인증으로 올린 기록과
팀원 본인이 직접 작성·검토한 사실은 구분한다. 최종 결과물 반영은 `main` 머지 후 확인한다.

## 나지수

담당 Issue:

담당 기능:

Branch:

개인 산출물:

주요 Commit:

Pull Request:

Review한 PR:

본인 기여 설명:

60초 설명:

상태:

- [ ] Issue
- [ ] Feature Branch
- [ ] 의미 있는 Commit 1
- [ ] 의미 있는 Commit 2
- [ ] Pull Request
- [ ] 다른 팀원 PR Review
- [ ] dev Merge
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

담당 Issue:

담당 기능:

Branch:

개인 산출물:

주요 Commit:

Pull Request:

Review한 PR:

본인 기여 설명:

60초 설명:

상태:

- [ ] Issue
- [ ] Feature Branch
- [ ] 의미 있는 Commit 1
- [ ] 의미 있는 Commit 2
- [ ] Pull Request
- [ ] 다른 팀원 PR Review
- [ ] dev Merge
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
