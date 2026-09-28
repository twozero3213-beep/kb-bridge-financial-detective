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
| `docs/work_packages.md` | 6개 독립 작업 후보와 완료 기준 |
| `docs/data_source.md` | Open DART API 출처와 로컬 실행·검증 기준 |
| `docs/team_prompts.md` | 팀원별 AI 프롬프트 초안과 직접 검증 기준 |
| `workflow/` | 핵심 분석 완료 후 필요한 자동화 자료 |
| `CONTRIBUTION.md` | 팀원별 Issue, Commit, PR, Review, 기여 기록 |
| `ai_log.md` | AI 사용과 사람의 검증·판단 기록 |
| `result_report.md` | 최종 분석 결과 보고서 골격 |

## GitHub Workflow

Issue → 담당자 지정 → 개인 Feature Branch → 의미 있는 Commit → Push → Pull Request → 다른 팀원 Review → `dev` Merge → 통합 검증 → `main` Merge.

`main`에서 직접 기능을 개발하지 않는다. `dev`는 통합 브랜치이며, 각 기능은 `dev`에서 분기한 `feature/<name>-<area>`에서 개발한다. 자세한 규칙은 [프로젝트 규칙](docs/project_rules.md)을 따른다.

### 팀원 시작 방법

1. [개인 작업 후보와 분배 기준](docs/work_packages.md)을 보고 실제 데이터·스키마에 맞는 Issue를 고른 뒤 담당자를 지정한다.
   AI를 사용할 때는 [팀원용 프롬프트](docs/team_prompts.md)를 실제 입력에 맞춰 수정한다.
2. 저장소를 Clone하고 `dev`를 최신 상태로 가져온다.

   ```bash
   git clone https://github.com/twozero3213-beep/kb-bridge-financial-detective.git
   cd kb-bridge-financial-detective
   git switch dev
   git pull origin dev
   git switch -c feature/<name>-<area>
   ```

3. 본인 코드와 검증 기록을 만들고 의미 있는 Commit을 최소 2회 남긴다. Push 후 **대상 브랜치를 `dev`로 지정**해 PR을 만든다.
4. 다른 팀원의 PR을 최소 1회 검토한다. 통합 검증이 끝나면 `dev`에서 `main`으로 PR을 만든다.

공개 저장소 주소만으로 Push 권한이 생기지는 않는다. GitHub 계정 사용자명을 저장소 관리자에게 전달해 협업자로 초대받거나, 권한이 없으면 Fork에서 작업하고 원본 저장소로 PR을 보낸다.

## 팀원

| 이름 | GitHub | 담당 작업 |
| --- | --- | --- |
| 나지수 | `skwltn2004-code` | 공시 SQL (#5) |
| 강동윤 | `dongyungang94-coder` | 재무 SQL (#4) |
| 안지형 | `agh3724` | 재무 Pandas (#6) |
| 이영 | `twozero3213-beep` | 데이터 수집·구조 확인 (#3), 저장소 관리 (#2) |
| 이정수 | `jw082501` | 공시 Pandas (#7) |
| 임도윤 | `odyn0624` | SQL·Pandas 교차검증 (#8) |

## 실행 방법

현재는 초기 골격 단계로 실행 가능한 분석 프로그램이 없다. 데이터 출처·스키마와 담당 기능이 확정되면 `data/`에 로컬 데이터를 준비하고, 담당자가 `sql/`, `notebooks/`, `src/`에 분석을 구현한 뒤 실행 명령과 필요한 패키지 버전을 여기에 기록한다. API 키와 비밀번호는 저장소에 넣지 않는다.

Open DART 데이터를 사용할 경우 키를 로컬 환경 변수 `DART_API_KEY`로 설정하고 `python -m src.dart_fetch <8자리_고유번호> <4자리_사업연도>`를 실행한다. 자세한 내용은 [데이터 연결](docs/data_source.md)을 참고한다. 분석 코드는 아직 팀원이 작성해야 한다.
SQL용 공통 DB는 `python -m src.build_db`로 생성한다.

## 핵심 결과

TBD - 분석 완료 후 작성.
