# 임도윤 담당 AI 사용·입력문

## 담당과 실제 이행

- **담당:** Issue #8, SQL·Pandas 교차검증. 검증된 재무·공시 결과만 브리핑에 전달한다.
- **목적:** 같은 기업·기간·단위·키로 만든 두 계산의 누락·중복·값 차이를 찾고 근거 없는 브리핑을 막는다.
- **해야 할 일:** 실제 DB 스키마 확인 → SQL/Pandas 독립 계산 → 잘못된 금액·접수일·빈 데이터 반례 검증 → 실행 결과·한계 기록 → PR·동료 리뷰.
- **이번에 실제 사용한 AI 도구:** Codex 데스크톱. 이영이 요청했고 Codex가 코드를 작성·실행했다. 임도윤 본인이 사용한 도구·수동 검토는 확인되지 않았다.
- **이행 산출물:** `src/validate_results.py`, `tests/test_validate_results.py`, `docs/validation_limdoyun.md`, `ai_log.md`, PR #11. 로컬 DART DB에서 재무 60행·공시 88그룹과 강동윤 SQL 선택 지표 16행이 일치했고 전체 테스트 11개가 통과했다.

아래는 임도윤님이 자신의 AI 도구에 **추후 복사해 사용할 수 있도록 만든
구체적인 프롬프트**다. 실제 입력 이력은 `ai_log.md`의 이영→Codex 요청과
구분한다. API 키나 원본 데이터 전체를 붙여넣지 않는다.

## 프롬프트 1: SQL·Pandas 교차검증

```text
나는 KB Bridge 「기업 재무·공시 이상징후 탐정」의 검증 담당이다.
Issue #8의 src/validate_results.py를 검토한다. 입력은 Open DART JSON을
적재한 SQLite dart.sqlite이며 finance와 disclosures 테이블이 있다.
재무는 corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm, ord,
thstrm_amount, frmtrm_amount를 사용한다. 공시는 corp_code, rcept_dt,
report_nm을 사용한다. SQL과 Pandas가 같은 기업·연도·연결/별도·계정 키로
증감액·증감률과 공시 건수를 각각 계산했는지 비교해 줘.
한쪽에만 있는 키, 중복, 숫자 변환 실패, 전기 0, 빈 원본, 잘못된 접수일을
숨기지 말고 CHECK로 보고하도록 반례를 제안해 줘. 데이터에 없는 수치나
기업 위험 판단을 만들어내지 마.
```

## 프롬프트 2: 검증된 사실만 브리핑

```text
나는 같은 프로젝트의 검증 담당이다. 검증 보고서의 status가 PASS이고
원본 DART 접수번호·접수일·회사·기간을 대조한 항목만 브리핑 후보로 쓴다.
src/briefing_limdoyun.py가 입력의 current/previous 값으로 증감률을 다시
계산하고, 0·음수 분모·잘못된 숫자·검증되지 않은 항목을 안전하게 처리하는지
검토해 줘. 공시 링크는 형식이 확인된 rcept_no에만 만든다.
수치는 출처와 함께 쓰고, 실제 데이터로 확인되지 않은 원인·기업 위험·투자
판단은 쓰지 마. 불일치가 있으면 제거 이유와 사람이 확인할 절차를 제시해 줘.
```

## 본인이 실제 사용한 뒤 남길 검증

1. 도구·일시·실제 입력문·AI 응답을 기록한다.
2. `python -m src.validate_results data/processed/dart.sqlite`의 행 수·불일치·결측을 원본과 대조한다.
3. `python -m unittest discover -s tests -v`를 실행하고 채택·수정·폐기 판단 이유를 적는다.
