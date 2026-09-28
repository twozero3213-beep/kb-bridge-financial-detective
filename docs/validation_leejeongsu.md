# 이정수: 독립 검증 모듈

현재 상태: 범용 검증 함수는 합성 데이터로 반례 검증했고, Issue #7의 실제 DART 공시 기간·유형 197그룹도 SQL/Pandas로 비교했다. 자세한 정책과 결과는 `docs/disclosure_pandas_leejeongsu.md`를 따른다.
Q2는 README의 분석 질문 번호이며 2분기라는 가정을 하지 않는다.

## 실행

저장소 루트에서:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.validation_leejeongsu --sql data/processed/sql_result.csv --pandas data/processed/pandas_result.csv --keys corp_code period disclosure_type --metrics count --changes data/processed/changes.csv --output data/processed/validation_report.json
```

SQL/Pandas 결과 CSV는 동일한 키와 수치 컬럼을 가져야 한다. 예시 키는 확정 스키마가 아니며 `--keys`, `--metrics`로 변경한다. 기업코드는 앞자리 0 보존을 위해 문자열로 읽는다. Notebook에서는 `from src.validation_leejeongsu import quality, compare_results, validate_changes`로 직접 사용한다. 원본의 중복·결측·행 수 검사는 `quality(raw_frame, ['rcept_no'], expected_rows=원본건수)`처럼 호출한다. 집계 CSV 검사만으로 원본의 품질을 증명할 수 없다.

## 팀 연결 계약

| 제공자 | 전달할 입력 | 검증 내용 |
| --- | --- | --- |
| 수집 담당 | 원본/정제 DataFrame, 고유 키, 예상 행 수 | quality: 중복·결측·행 수 |
| SQL 담당 | 기업·기간·유형 등의 키와 수치 결과 CSV | 그룹 누락과 값 비교 |
| Pandas 담당 | 같은 조건의 결과 CSV | SQL 결과와 외부 조인 비교 |
| 재무/공시 담당 | 키 + previous,current,change_pct,candidate | 증감률·후보 재계산 |
| AI 담당 | validation_report.json | CHECK 내용을 확인 후 검증 범위에 맞게 사용 |

기간 범위(시작 포함·종료 제외 권장), 정정 공시 처리, 중복 제거 키, 공시 유형 분류, 재무 단위·연결/별도, 결측 처리, 이전 기간 정의를 팀원이 먼저 일치시켜야 한다. 검증기는 임의로 중복 제거하거나 누락 그룹을 0으로 채우지 않는다. 결과 일치는 공통 입력·집계 정책 자체의 정확성을 보증하지 않는다.

changes.csv의 각 행은 분석 담당자가 명시적으로 연결한 이전/현재 기간 쌍이다. 기간 컬럼을 키에 넣어 쌍을 식별한다. 자동 정렬 후 인접 행을 이전 기간으로 추정하지 않는다.

## 계산 정책과 결과

- 증감률 = `(current - previous) / abs(previous) * 100`. 음수 기준값에서 팀 계산식과 합의 필요.
- 이전 값 0, 결측, 비수치는 비교 불가로 CHECK. 0%로 대체하지 않는다.
- 후보 기본값: 증감률 절댓값 50% 이상 **그리고** 증감액 절댓값 1 이상. 이는 설명 가능한 임시 규칙이며 기업 위험 판단이 아니다.
- `candidate`는 true/false 문자열, 비교 불가이면 공란. `change_pct`도 비교 불가이면 공란.
- `--threshold-pct`, `--min-abs-change`로 민감도 확인. 기준을 바꾸면 분석 담당자의 후보 플래그도 해당 기준으로 다시 생성해야 한다.
- 집계값은 기본적으로 정확 비교. 반올림 지표만 합의 후 `--atol`, `--rtol` 지정. 증감률은 절대 허용오차 1e-8 퍼센트포인트.
- JSON은 각 검사의 PASS/CHECK, 불일치 키·값 또는 0부터 시작하는 행 위치를 기록한다.
- 종료 코드 0=제공된 검사 PASS, 1=CHECK. changes 입력이 없으면 미실행 CHECK를 기록한다.

## 이번 검증 근거

Python 3.12.10, Pandas 3.0.5에서 `python -m unittest discover -s tests -v`: 10개 통과.
합성 공시 3행을 SQLite COUNT/GROUP BY와 Pandas groupby로 독립 집계하여 비교했다.
값 불일치, 그룹 누락, 중복, 결측·빈 입력, 비정상 수치, 누락 컬럼, 음수 기준값, 잘못된 증감률·후보, 0 기준값, 임계값 민감도를 검사했다.
실제 공시 438건의 197그룹은 `notebooks/analysis_disclosure.ipynb`에서 SQL/Pandas 대조로 모두 일치했다. 사람의 직접 재실행은 미확인이다.

## GitHub 후속 작업

기존 `feature/leejeongsu-validation`의 PR #10을 원격 `dev` 기준으로 보완했다. 담당 Issue는 #7 공시 Pandas이며 리뷰·머지 상태는 GitHub PR과 `CONTRIBUTION.md`를 따른다.

기존 범용 검증 모듈은 공시 Pandas와 독립 SQL 집계 비교에 실제 사용했다.
Issue/Commit/PR/Review/Merge URL은 실제 GitHub 기록만 `CONTRIBUTION.md`에 남긴다.

## 60초 설명

설명용 요약: “공시 원본을 접수일 월·보고서명으로 묶고 정정 접수를 별도로 셉니다. 실제 438건을 197개 기간·유형 그룹으로 집계해 SQL과 비교했고 불일치가 없었습니다. 전년 같은 달보다 건수가 크게 달라진 월은 확인 후보로만 표시합니다. 기존 검증 함수는 집계 그룹 누락·값 차이를 검사합니다. 기업 위험이나 원인은 이 비교만으로 판단하지 않습니다.” 이정수 본인이 직접 설명할 수 있는지는 확인되지 않았다.
