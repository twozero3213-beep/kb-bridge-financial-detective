# 이정수: 독립 검증 모듈

현재 상태: 실제 데이터·스키마 미제공. 합성 데이터로 코드 동작만 검증했다.
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
실제 기업 분석, 최종 Notebook 연결, 사람의 직접 재실행은 미완료다.

## GitHub 후속 작업

로컬 main 기준으로 dev와 feature/leejeongsu-validation을 생성했다. 원격 dev 기준 여부는 아직 확인하지 않았다.
저장소에는 docs/work_packages.md가 없어 이정수의 상호 리뷰 배정을 확인하지 못했다. 사용자 첫 부분의 공시 분석 브랜치·리뷰 배정을 검증 담당에게 임의 적용하지 않았다.

Issue 초안: "이정수: SQL/Pandas 결과 및 변화 후보 독립 검증".
목적: 동일 집계 조건의 결과 비교, 원본 품질 검사, 증감률과 후보 재계산.
완료 조건: 실제 팀 데이터 실행, 불일치 원인 기록, 최종 분석 연결, 동료 Review 후 dev 통합.
권장 Commit 1: "feat: 이정수 독립 검증 함수와 CSV 실행기 구현"
권장 Commit 2: "test: SQL 교차검증과 경계값 테스트 및 연결 문서 추가"
Issue/Commit/PR/Review/Merge URL은 실제 생성 후 기록한다. 현재 이 기록은 없다.

## 60초 설명

“저는 팀 분석 결과를 독립 검증합니다. 원본에서는 행 수, 고유 키 중복, 결측치를 확인합니다. SQL과 Pandas 집계는 같은 기업·기간·유형 키로 외부 조인해서 빠진 그룹과 다른 수치를 찾습니다. 증감률과 확인 후보도 이전 값과 현재 값으로 다시 계산합니다. 이전 값이 0이면 판단할 수 없다고 표시하고, 불일치는 CHECK로 남깁니다. 결과는 JSON이라 최종 Notebook이나 AI 요약 단계에서 사용할 수 있습니다. 현재 합성 데이터 테스트 10개를 통과했고 실제 팀 데이터 연결은 남아 있습니다.”
