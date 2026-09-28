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
| `sql/queries.sql` | 실제 재무·공시 SQL을 합친 공통 제출 파일 |
| `notebooks/analysis.ipynb` | 실제 데이터로 실행한 SQL·Pandas 통합 분석 |
| `src/` | 수집·적재·역할별 분석·검증 코드 |
| `docs/project_rules.md` | 팀 형상관리·검증 규칙 |
| `docs/work_packages.md` | 6개 독립 작업 후보와 완료 기준 |
| `docs/data_source.md` | Open DART API 출처와 로컬 실행·검증 기준 |
| `docs/team_prompts.md` | 팀원별 AI 프롬프트 초안과 직접 검증 기준 |
| `docs/recording_guide.md` | 팀원별 GitHub 증거와 기록 방법 |
| `workflow/` | 핵심 분석 완료 후 필요한 자동화 자료 |
| `CONTRIBUTION.md` | 팀원별 Issue, Commit, PR, Review, 기여 기록 |
| `ai_log.md` | AI 사용과 사람의 검증·판단 기록 |
| `result_report.md` | 최종 수치·후보·한계·근거 보고서 |

## GitHub Workflow

Issue → 담당자 지정 → 개인 Feature Branch → 의미 있는 Commit → Push → Pull Request → 다른 팀원 Review → `dev` Merge → 통합 검증 → `main` Merge.

`main`에서 직접 기능을 개발하지 않는다. `dev`는 통합 브랜치이며, 각 기능은 `dev`에서 분기한 `feature/<name>-<area>`에서 개발한다. 자세한 규칙은 [프로젝트 규칙](docs/project_rules.md)을 따른다.

### 팀원 시작 방법

1. [개인 작업 후보와 분배 기준](docs/work_packages.md)을 보고 실제 데이터·스키마에 맞는 Issue를 고른 뒤 담당자를 지정한다.
   AI를 사용할 때는 [팀원용 프롬프트](docs/team_prompts.md)를 실제 입력에 맞춰 수정한다.
   실제 Commit·PR·Review 기록은 [팀원별 GitHub 기록 안내](docs/recording_guide.md)를 따른다.
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
| 나지수 | `skwltn2004-code` | 공시 SQL 배정 (#5), 이영 대체 구현·업로드 |
| 강동윤 | `dongyungang94-coder` | 재무 SQL (#4) |
| 안지형 | `agh3724` | 재무 Pandas (#6) |
| 이영 | `twozero3213-beep` | 데이터 수집·구조 확인 (#3), 저장소 관리 (#2) |
| 이정수 | `jw082501` | 공시 Pandas (#7) |
| 임도윤 | `odyn0624` | SQL·Pandas 교차검증 (#8) |

## 실행 방법

Python, Pandas와 Jupyter가 필요하다. Open DART API 키를 로컬 환경 변수 `DART_API_KEY`로 설정하고 저장소 루트에서 실행한다. 이미 수집한 로컬 JSON이 있으면 수집 명령은 생략할 수 있다. 키·원본 JSON·SQLite 파일은 Git에 올리지 않는다. 데이터 출처와 스키마는 [데이터 연결](docs/data_source.md)을 참고한다.

```powershell
python -m src.dart_fetch 00126380 2023
python -m src.dart_fetch 00126380 2024
python -m src.build_db
python -m unittest discover -s tests -v
jupyter nbconvert --to notebook --execute notebooks/analysis_finance.ipynb --output analysis_finance.executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/analysis_disclosure.ipynb --output analysis_disclosure.executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/analysis.ipynb --output analysis.executed.ipynb
python -m src.run_disclosure_sql data/processed/dart.sqlite
```

`data/processed/dart.sqlite`는 재무 `finance` 60행, 공시 `disclosures` 438건으로 재생성됐다. 역할별 원본은 `sql/queries_finance.sql`, `sql/queries_disclosure.sql`, `notebooks/analysis_finance.ipynb`, `notebooks/analysis_disclosure.ipynb`다. 공통 제출물은 `sql/queries.sql`, `notebooks/analysis.ipynb`, `result_report.md`, `ai_log.md`, `CONTRIBUTION.md`다.

## 핵심 결과

2024년 삼성전자 연결 영업이익은 전기 6,566,976,000,000원에서 32,725,961,000,000원(+398.341%)으로 변했다. 재무 선택 지표 16행의 SQL/Pandas 값이 일치했다. 공시 438건은 기간·유형 197그룹, 24개월, 정정·첨부추가 30건으로 집계됐고 SQL/Pandas 비교 36항목이 모두 일치했다. 2024년 50%/10건 기준 확인 후보는 3·6·9·10·11·12월이다. 원본 진위·기업 위험·인과 관계를 뜻하지 않는다. 수치·방법·한계는 [최종 결과 보고서](result_report.md)에 있다.

## 이정수: 공시 Pandas 분석

로컬 DART DB의 공시 438건을 기간·유형 197그룹으로 분석하고 독립 SQL과 대조했다. 실행 방법과 후보 기준은 [공시 Pandas 기록](docs/disclosure_pandas_leejeongsu.md), 실행 결과는 `notebooks/analysis_disclosure.ipynb`에 있다.

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
