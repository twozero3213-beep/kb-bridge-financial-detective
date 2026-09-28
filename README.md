# 기업 재무·공시 이상징후 탐정

## 프로젝트 목적

기업의 재무·공시 데이터를 활용해 기업별 재무지표 변화와 공시 패턴을 분석하고, 평소와 다른 변화를 **확인 후보**로 찾는다. SQL과 Pandas/Python 분석 결과를 교차검증한 뒤, 검증된 사실을 토대로 AI 브리핑을 작성한다. 변화만으로 기업의 위험·부실·투자위험을 단정하거나 확인되지 않은 원인을 추측하지 않는다.

## 분석 질문

- **Q1.** 기업의 주요 재무지표는 이전 기간 대비 어떻게 변했는가?
- **Q2.** 기업의 공시 빈도와 유형은 기간별로 어떻게 달라졌는가?
- **Q3.** 재무변화와 공시패턴 중 평소와 크게 다른 ‘확인 후보’가 존재하는가?

## 기술 스택

Python, Pandas, SQL, Git/GitHub, AI, Open DART 또는 강사 제공 데이터. n8n은 핵심 분석 완료 후 필요할 때만 검토한다.

## 프로젝트 구조

| 경로 | 목적 |
| --- | --- |
| `data/raw/` | 원본 데이터의 로컬 보관 위치. 데이터 파일은 Git에서 제외 |
| `data/processed/` | 전처리 데이터의 로컬 보관 위치. 데이터 파일은 Git에서 제외 |
| `sql/queries.sql` | 데이터 스키마 확인 후 팀원이 작성할 SQL 영역 |
| `notebooks/analysis.ipynb` | Pandas 분석과 SQL 결과 비교를 위한 노트북 골격 |
| `src/` | 추후 재사용할 Python 코드 |
| `docs/project_rules.md` | 팀 형상관리·검증 규칙 |
| `workflow/` | 핵심 분석 완료 후 필요한 자동화 자료 |
| `CONTRIBUTION.md` | 팀원별 Issue, Commit, PR, Review, 기여 기록 |
| `ai_log.md` | AI 사용과 사람의 검증·판단 기록 |
| `result_report.md` | 최종 분석 결과 보고서 골격 |

## GitHub Workflow

Issue → 담당자 지정 → 개인 Feature Branch → 의미 있는 Commit → Push → Pull Request → 다른 팀원 Review → `dev` Merge → 통합 검증 → `main` Merge.

`main`에서 직접 기능을 개발하지 않는다. `dev`는 통합 브랜치이며, 각 기능은 `dev`에서 분기한 `feature/<name>-<area>`에서 개발한다. 자세한 규칙은 [프로젝트 규칙](docs/project_rules.md)을 따른다.

## 팀원

| 이름 | 역할 |
| --- | --- |
| 나지수 | 배정 예정 |
| 강동윤 | 배정 예정 |
| 안지형 | 배정 예정 |
| 이영 | 배정 예정 |
| 이정수 | 배정 예정 |
| 임도윤 | 배정 예정 |

## 실행 방법

현재는 초기 골격 단계로 실행 가능한 분석 프로그램이 없다. 데이터 출처·스키마와 담당 기능이 확정되면 `data/`에 로컬 데이터를 준비하고, 담당자가 `sql/`, `notebooks/`, `src/`에 분석을 구현한 뒤 실행 명령과 필요한 패키지 버전을 여기에 기록한다. API 키와 비밀번호는 저장소에 넣지 않는다.

## 핵심 결과

TBD - 분석 완료 후 작성.

## 임도윤: 브리핑 생성

검증된 재무·공시 분석 결과(JSON)를 바탕으로 한국어 Markdown 브리핑을 생성하는 스크립트입니다.

### 실행 방법

```bash
# 가상 예시 데이터로 브리핑 생성 (표준 출력)
python src/briefing_limdoyun.py --input examples/limdoyun/sample_validated_SAMPLE.json

# 결과를 Markdown 파일로 저장
python src/briefing_limdoyun.py --input examples/limdoyun/sample_validated_SAMPLE.json --output examples/limdoyun/briefing_output.md
```

### 테스트 실행

```bash
# 검증 케이스(단위 및 통합 테스트) 실행
python -m unittest tests/test_briefing_limdoyun.py
```
