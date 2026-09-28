# 이정수 공시 Pandas — Issue #7

## 현재 상태

`notebooks/analysis_disclosure.ipynb`가 개인 산출물이고 `src/disclosure_pandas.py`를 실제 호출한다.
팀 원본 `dev`의 `284ad00`에서 `feature/jw082501-disclosure-pandas`를 분기했다.
기존 `feature/leejeongsu-validation`의 두 커밋과 Push 기록은 별도로 보존되어 있다.
사용자가 Commit·Push를 승인하여 기능 구현과 테스트·문서를 별도 커밋으로 저장한다. 실제 커밋·원격 반영은 Git 기록으로 확인한다. PR/Review/Merge는 아직 미완료다.
ZIP은 스키마 참고 스냅샷으로 읽었으며 팀원 수집 코드나 SQL 코드를 본인 산출물로 복사하지 않았다.
현재 실제 DB·분석 기업·기간·나지수 SQL이 미제공 상태다. 아래 숫자는 합성 테스트이며 실제 기업 결과가 아니다.

## 나중에 팀 파일이 올라오면

다시 실행할 때 다음 파일을 자동으로 읽는다. 백그라운드 동기화나 자동 Git pull은 하지 않는다.

| 입력 | 기본 경로 |
| --- | --- |
| 공통 DB | `data/processed/dart.sqlite` |
| 팀 설정 1순위 | `data/processed/disclosure_config.json` |
| 팀 설정 2순위 | `config/disclosure.json` |
| 나지수 공시 SQL | `sql/queries_disclosure.sql` |

실제 데이터는 Git 제외 대상이므로 코드만 Pull해도 DB가 생기는 것은 아니다. 팀에서 받은 DB를 해당 위치에 두거나, 수집 코드 병합 후 수집 담당자의 실행법에 따라 생성한다.
설정은 팀에서 받은 파일을 그대로 놓거나 `config/disclosure.example.json`을 복사해 한 번 채운다.

```bat
copy config\disclosure.example.json data\processed\disclosure_config.json
python -m pip install -r requirements-disclosure.txt
python -m src.disclosure_pandas
```

설정의 `corp_code`는 문자열 8자리, `start`/`end`는 분석 범위, `coverage_start`/`coverage_end`는 **모든 페이지 수집이 완료된 범위**다. 모두 YYYY-MM-01 형식이고 시작 포함·종료 제외다.
`coverage_confirmed`는 수집 담당자 확인 후에만 true로 바꾼다. 접수일 최소/최대만으로 완료 범위를 추정하지 않는다.
예컨대 1월을 기준으로 2~4월을 비교하려면 분석은 2월 1일~5월 1일, 수집 범위는 적어도 1월 1일~5월 1일이어야 한다. 이는 입력법 예시이지 팀의 분석 기간 지정이 아니다.
경로는 저장소 루트 기준이며 절대 경로도 가능하다. 개별 설정은 `python -m src.disclosure_pandas --config 경로`로 선택한다.
Notebook도 같은 설정을 자동으로 읽는다. Run All을 실행하면 같은 분석과 결과 파일이 생성된다.

## 입력 스키마와 분석 정책

ZIP의 build_db.py에서 확인한 필수 컬럼은 `corp_code`, `rcept_no`, `rcept_dt`, `report_nm`이다.
실제 실행 시 PRAGMA로 테이블·컬럼을 다시 확인한다. DB는 읽기 전용이고 잘못된 경로에 새 DB를 만들지 않는다.

- 기업 필터 후 필수 결측·빈 문자열·유효하지 않은 YYYYMMDD 날짜는 오류로 중단한다.
- 동일 `rcept_no`와 필수 내용이 같으면 1건. 같은 접수번호의 상충 내용은 오류다.
- 정정 제목에 `정정`이 포함되는지를 검사한다. 기본 포함, `corrections: exclude`이면 제외한다. 원공시와 최신 정정본을 연결해 대체하는 기능은 아니다.
- 제목 분류 우선순위는 사업보고서, 반기보고서, 분기보고서, 기타. 공식 DART 유형이 아닌 임시 제목 분류다. SQL 담당자와 최종 합의해야 한다.
- 완전한 월만 비교한다. 수집 완료를 확인한 범위의 비어 있는 월/유형은 0건이다.
- 범위 내에 전월이 있으면 전월과 비교한다. 전월이 수집 범위 밖이면 previous_count, 증감률, 후보 여부는 결측이다.
- 증감률은 `(현재-전월)/전월*100`. 전월 0건은 증감률 결측, 무한대나 0%로 대체하지 않는다.
- 기본 확인 후보: 100% 이상 **증가**하고 3건 이상 증가. 전월 0건에서 3건 이상 발생하면 별도 신규 발생 후보. 감소는 이 증가 탐지 규칙 대상이 아니다.
- 설정 `threshold_pct`, `min_increase` 변경 가능. 민감도는 50/100/200% × 3/5건을 비교한다. 작은 분모에 민감하므로 상대·절대 기준을 함께 둔 임시 규칙이며 위험 판정이 아니다.
- Q2는 분석 질문 번호다. 공시 데이터에는 재무제표의 연결/별도 필터를 임의 적용하지 않는다.

## 나지수 SQL 연결 계약

팀 SQL 파일 자체는 수정하지 않는다. 한 번에 실행 가능한 단일 SELECT 또는 WITH...SELECT 쿼리이며 반환 컬럼은 다음과 같아야 한다.

| 컬럼 | 형식 |
| --- | --- |
| corp_code | 8자리 문자열 |
| period | YYYY-MM |
| disclosure_type | 합의한 제목 유형 |
| count | 0 이상 정수 |

지원하는 SQLite 바인딩 변수: `:corp_code`, `:start`/`:end`(YYYYMMDD), `:start_iso`/`:end_iso`(YYYY-MM-DD), `:coverage_start`, `:coverage_end`와 각각 `_iso`, `:include_corrections`(1/0), `:corrections`(include/exclude).
팀 SQL이 여러 쿼리 묶음이면 단일 월별 집계 쿼리를 별도 파일로 제공받아 설정의 `team_sql` 경로로 지정한다.
기간·중복·정정·유형 정책과 빈 월 0건 행이 일치해야 한다. 누락 키는 자동으로 0으로 맞추지 않고 CHECK로 남긴다.
파일 없음, 중복 키, 결측, 잘못된 컬럼, 값 차이, 쿼리 실패는 CHECK에 기록된다. 원인은 missing_sql_group, missing_pandas_group, count_differs 등으로 구분하며 정책상의 원인은 사람이 확인한다.

`sql/disclosure_reference_jw082501.sql`은 **본인 자체 점검용**이다. 동일 DB에 DISTINCT/CASE/GROUP BY와 월 달력 CTE를 적용한 독립 구현이다. 이 쿼리와 일치해도 나지수 SQL 검증 완료를 뜻하지 않는다.

## 출력과 최종 연결

`data/processed/disclosure_analysis/`에 다음을 저장한다.

- `monthly_counts.csv`: 월·유형별 count/previous_count/change/change_pct/candidate/candidate_reason.
- `candidates.csv`: 확인 후보 행.
- `sensitivity.csv`: 임계값별 후보 수·비교 불가 수.
- `validation.json`: 실행 설정, 입력 행 수·중복 제거 수, 입력/SQL SHA-256, Pandas 버전, 자체 SQL 대조와 팀 SQL 대조를 별도 기록.

임도윤님은 CSV를 교차검증 입력으로 사용하고, 최종 분석은 `run_analysis` 함수 또는 위 결과 파일을 읽을 수 있다. 현재 개인 Notebook에서 본인 함수를 사용하는 연결은 완료했지만 팀 최종 Notebook·보고서 반영은 아직 확인하지 않았다.
CLI 종료 코드 0은 실행한 SQL 수치 대조 PASS, 1은 CHECK/입력 오류다. PASS도 자료의 출처·완전성·원인에 대한 보증은 아니다. 이전 기간이 없는 행 수는 별도 확인한다.

## 실행 검증 근거

명령: `python -m unittest discover -s tests -v`
환경: Python 3.12.10 / Pandas 3.0.5. 결과: **14개 테스트 통과**.
Notebook은 Jupyter 커널이 아니라 Python에서 코드 셀을 순서대로 실행하는 smoke test로 검증했다. Notebook 파일에는 실행되지 않은 실제 데이터 출력을 넣지 않았다.

통합 합성 입력은 접수 행 16개(동일 내용 중복 1개 포함)이며, 분석 기간의 정정 포함 유지 건수는 12건이다.
기간은 테스트용 2024-02-01~2024-05-01, 기준월은 1월이다. 기타 유형의 월별 건수는 1월 2, 2월 5, 3월 0, 4월 6이고 2월 정정 사업보고서 1건을 추가했다.
자체 SQLite SQL/Pandas: **12그룹 일치, 0 불일치**. 정정 제외 시 분석 11건으로 별도 검증.
기본 후보는 2개: 2월 기타 2→5(+150%, +3), 4월 기타 0→6(증감률 없음, 신규 발생).

| 증가율 기준 | 최소 증가 건수 | 후보 수 |
| --- | --- | --- |
| 50% | 3 | 2 |
| 50% | 5 | 1 |
| 100% | 3 | 2 |
| 100% | 5 | 1 |
| 200% | 3 | 1 |
| 200% | 5 | 1 |

팀 SQL 도착 자동 감지는 자체 쿼리를 테스트 대역으로 배치해 확인했다. 대역의 값을 1씩 바꾸자 12개 불일치를 검출했다. 이는 실제 나지수 SQL 실행 증거가 아니다.
경계일·0건 월·중복·상충 접수번호·잘못된 날짜·결측·범위 미확인·이전 기간 없음·SQL 누락 그룹·읽기 전용 보호를 검증했다.
실행 과정에서 테스트용 SQLite 연결이 닫히지 않아 Windows 임시 파일 정리가 실패했고, contextlib.closing으로 수정 후 재검증했다.

## 60초 설명

“저는 이정수의 공시 Pandas 분석을 맡았습니다. 공통 DB에서 기업 공시를 읽고 접수번호 중복과 날짜를 확인합니다. 제목으로 유형을 나누고 월별 건수를 세며, 수집이 완료된 범위에서만 빈 달을 0으로 채웁니다. 전월보다 100% 이상, 3건 이상 늘어난 경우를 확인 후보로 표시하고 기준을 바꿔 후보 수를 비교합니다. 전월이 0이면 증감률은 계산하지 않습니다. 자체 SQL과 팀 SQL 대조는 따로 기록합니다. 현재 합성 테스트 14개를 통과했고 실제 팀 데이터가 오면 설정을 채워 다시 실행해야 합니다.”
