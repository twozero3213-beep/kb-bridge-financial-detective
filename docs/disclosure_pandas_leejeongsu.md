# 이정수 담당: 공시 Pandas 패턴 분석

- Issue [#7](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/7) / PR [#10](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/10)
- 분석 코드: `src/disclosure_pandas_leejeongsu.py`
- 실행 노트북: `notebooks/analysis_disclosure.ipynb`
- SQL/Pandas 비교: `src/validation_leejeongsu.py`
- 반례 검사: `tests/test_disclosure_pandas_leejeongsu.py`

## 집계 정책

SQLite `disclosures`의 한 접수번호를 한 건으로 센다. 접수일 `YYYYMMDD`의 연월과 양쪽 공백을 뺀 보고서명을 유형으로 사용한다. 정정·첨부추가 공시는 별도 접수로 포함하고 수를 따로 표시한다. 중복·빈 접수번호, 잘못된 날짜, 빈 유형이면 계산을 중단한다.

같은 달의 전년 건수와 비교해 증감 건수·증감률을 계산한다. 이전 같은 달이 없으면 증감률은 결측이다. 기본 **확인 후보**는 증감률 절댓값 50% 이상이면서 건수 차이 절댓값 10건 이상이다. 100% 기준도 실행해 민감도를 확인한다. 이 기준은 탐색용이며 기업 위험 판정이 아니다.

## 재현과 실제 결과 (2026-09-28)

저장소 루트에 로컬 `data/processed/dart.sqlite`를 준비하고 노트북을 실행한다. DB 파일은 Git에 올리지 않는다.

```powershell
python -m unittest discover -s tests -v
jupyter nbconvert --to notebook --execute notebooks/analysis_disclosure.ipynb --output analysis_disclosure.executed.ipynb
```

로컬 Open DART 삼성전자(`00126380`) 공시 2023년 154건, 2024년 284건, 합계 **438건**에서 기간·유형 **197그룹**, 월 **24개**, 정정·첨부추가 접수 **30건**이 나왔다. 같은 SQLite 원본의 독립 SQL 집계와 Pandas의 197그룹 건수·정정 건수는 모두 일치했다.

2024년 전년 같은 달 대비 기본 기준 확인 후보는 **6개월**(3·6·9·10·11·12월), 100% 기준이면 **5개월**(3·6·9·10·11월)이다. 예컨대 9월은 4→31건(+27건, +675%), 12월은 27→43건(+16건, +59.259%)이다. 2024년 유형 중 `임원ㆍ주요주주특정증권등소유상황보고서`가 151건으로 많다. 이 수치만으로 이상 원인을 단정하지 않는다.

현재 Windows의 Pandas 3.0.4 환경에서 `pd.to_datetime`이 실제 438행의 Arrow 문자열에 접근 위반을 일으켰다. 날짜 형식 검증과 월 추출은 표준 라이브러리 `datetime.strptime`로 바꾸고 같은 원본·테스트를 다시 통과했다. 다른 환경의 Pandas 동작까지 일반화한 결론은 아니다.

## 최종 공통 제출물과 재검증

공시 SQL 배정 역할은 이영 대체 구현 [PR #16](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/16)으로 `dev`에 통합됐다. 이정수 담당 Pandas 함수와 `sql/queries_disclosure.sql`을 [`src/run_disclosure_sql.py`](../src/run_disclosure_sql.py)로 비교하면 공시 438건, 197그룹, 월 24개, 정정·첨부추가 30건, 비교 36항목 모두 `PASS`다. 기존 담당 노트북의 SQL은 독립 비교용으로 보존하며 공통 제출 `sql/queries.sql`과 `notebooks/analysis.ipynb`가 최종 통합 경로다.

```powershell
python -m src.run_disclosure_sql data/processed/dart.sqlite
jupyter nbconvert --to notebook --execute notebooks/analysis.ipynb --output analysis.recheck.ipynb --output-dir data/processed
```

공통 노트북은 기본 `nbconvert` 커널 작업 폴더가 `notebooks/`라서 `src` import가 실패한 실제 오류를 [PR #18](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/18)에서 수정했다. 재실행에서 코드 셀 4개 완료·오류 출력 0건을 확인했다. 수정 이유는 노트북 첫 코드 셀 주석에 기록됐다.

## 작업 주체

이영 요청으로 Codex가 이정수 담당 브랜치의 실제 데이터 분석·노트북·검사를 추가하고 실행했다. 이전 PR #10의 범용 검증 코드와 이번 수정의 작업 주체를 구분한다. 이정수 본인의 직접 작성·수동 검토는 확인되지 않았다.
