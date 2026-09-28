# Issue #7 PR 본문 초안 — 아직 게시하지 않음

제목: feat: 공시 Pandas 월별·유형별 집계와 확인 후보 분석
대상: twozero3213-beep/kb-bridge-financial-detective의 dev
소스: jw082501:feature/jw082501-disclosure-pandas
리뷰 요청 대상: skwltn2004-code
관련 Issue: https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/7

공통 disclosures 스키마를 읽어 월별·제목 유형별 빈도와 전월 대비 변화를 계산한다. 정정·중복·기간 경계를 명시하고 임계값별 확인 후보 수를 비교한다. 팀 DB·설정·SQL이 도착하면 재실행으로 반영한다.

코드: notebooks/analysis_disclosure.ipynb → src/disclosure_pandas.py
정책/입력 계약/60초 설명: docs/disclosure_pandas.md
실행: python -m src.disclosure_pandas
테스트: python -m unittest discover -s tests -v

현재 검증: Python 3.12.10/Pandas 3.0.5, 테스트 14개 PASS. 합성 데이터의 자체 SQLite SQL/Pandas 12그룹 일치·0 불일치, 임계값별 후보 수 1~2개. Notebook 코드 셀을 Python으로 순서대로 실행했다.

미완료: 실제 기업·기간·DB 실행, 나지수 SQL 대조, 사용자의 직접 재실행·채택 판단, 타인 Review, dev Merge, 팀 최종 결과 반영. 실제 데이터 실행 전에는 과제 완료 PR로 표현하지 않는다.

실제 데이터 도착 후 아래를 채운다:
- 기업/분석 기간/수집 완료 범위:
- 원본·중복 제거·정정·분석 건수:
- SQL 일치/불일치 수와 대표 원인:
- 후보 수와 민감도:
- Commit 1/2 URL:
- 내가 나지수 PR에 제출한 Review URL:
- 팀 최종 결과 사용 위치:
