# 임도윤 담당: SQL·Pandas 결과 교차검증

- 연결 Issue: #8 / PR: #11 / 작업 브랜치: `feature/limdoyun-ai`
- 실행 코드: `src/validate_results.py`; 검증 코드: `tests/test_validate_results.py`
- 기존 AI 브리핑 코드: `src/briefing_limdoyun.py` (PR #11에 포함)

## 재현 방법

Python 3.11 이상과 `pandas>=2.2,<4`가 필요하다. DART 원본은 Git에 올리지 않고
로컬 `data/processed/dart.sqlite`에 둔다. DB에는 `finance`, `disclosures` 테이블이
필요하다. 저장소 루트에서 다음을 실행한다.

```powershell
python -m pip install "pandas>=2.2,<4"
python -m src.validate_results data/processed/dart.sqlite --output data/processed/validation_report.json
python -m unittest discover -s tests -v
```

재무는 회사·연도·재무제표·계정·순번별 당기/전기 금액, 증감액, 증감률을 대조한다.
전기 금액이 0이면 증감률은 비워 둔다. 공시는 회사·접수연도·보고서명별 건수를
대조한다. 한쪽에만 있는 키, 중복 키, 값 불일치, 숫자로 바꿀 수 없는 금액,
8자리 형식이 아닌 접수일을 `CHECK`로 표시한다. 값 차이 허용치는 재무 0.000001이다.

## 실제 실행 기록 (2026-09-28)

로컬 삼성전자 DART 예시 DB(2023·2024년)에서 재무 60행, 공시 88개 그룹을
대조했다. 강동윤 담당 `sql/queries_finance.sql`의 선택 지표 16행도 독립
Pandas 계산과 비교해 불일치 0건이었다. 세 항목 모두 `PASS`, 잘못된 금액
0행, 잘못된 접수일 0건이다. 테스트는 브리핑·재무 SQL까지 포함해 11개 통과했다.

SQL과 Pandas는 **같은 로컬 SQLite 원본**을 사용한다. 따라서 이 결과는 두 계산의
일치만 증명하며, DART 원본 자체의 정확성이나 전체 팀의 최종 Q1·Q2 결과를
증명하지 않는다. 최종 보고서에서는 통합 데이터로 다시 실행해야 한다.

## 작성·검증 책임 기록

이 교차검증 코드·테스트·문서는 이영의 요청에 따라 Codex가 임도윤 계정의
기존 PR에 추가한 AI 지원 작업이다. 자동 테스트 및 위 로컬 DB 실행은
2026-09-28에 수행했다. 임도윤 본인의 수동 검토와 PR 리뷰 참여는 별도 기록이
확인되기 전까지 완료로 표시하지 않는다.
