# 팀원별 GitHub 기록 안내

이 문서는 여섯 명 모두에게 같은 증거 기준을 적용한다. 실제 작업 전에 담당 Issue에 계획을 적고, 본인 계정의 기능 브랜치에서 코드를 작성한다. 완료 표시는 GitHub에서 확인되는 기록에만 한다. 강사 참고 문서의 개인 기준은 **독립 코드 산출물, 의미 있는 Commit 2회 이상, 타인 PR Review 1회 이상, 최종 결과물 반영, 60초 설명**이다.

## 시작 전에 확인

1. [설정 PR #9](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9)의 **Reviewers**에 `odyn0624 — Awaiting requested review`가 보이면 리뷰 요청은 등록된 상태다. 임도윤은 **Files changed → Review changes → Approve 또는 Request changes → Submit review**로 실제 검토를 제출한다. 이영은 승인 후 `dev`에 병합한다. 저장소 첫 화면의 노란 **recent pushes** 배너는 임도윤의 개인 브랜치 Push이며 PR #9의 Review 완료 표시가 아니다.
2. 각자 자신의 GitHub 계정으로 로그인하고, 각자의 작업 폴더에 저장소를 Clone한다. 공용 PC에서도 Git 작성자와 인증 계정이 본인인지 확인한다.
3. 데이터와 API 키는 Commit하지 않는다. `data/raw/`와 `data/processed/`는 Git에서 제외된다.

## 공통 기록 순서

### 1 Issue에 시작 기록

아래 내용을 **본인에게 배정된 Issue의 댓글**로 남긴다. 템플릿 문장을 그대로 제출하지 말고 실제 데이터·파일을 채운다.

```text
작업 시작: [날짜/시간]
분석 질문: [Q1/Q2/Q3]
사용 데이터: [출처, 기업, 기간, 실제 파일 또는 테이블]
확인한 컬럼과 단위: [실제 확인한 내용]
작성할 코드: [본인 파일명과 담당 부분]
검증 계획: [실행 명령/Notebook 셀, SQL·Pandas 비교 또는 원본 대조]
현재 막힌 점: [없음 또는 구체적 내용]
```

### 2 본인 브랜치와 Git 작성자 확인

각자 별도 Clone에서 실행한다. 이미 Clone했다면 해당 폴더로 이동해 `git fetch origin`을 실행하고 아래의 `git switch dev`부터 진행한다.

```bash
git clone https://github.com/twozero3213-beep/kb-bridge-financial-detective.git
cd kb-bridge-financial-detective
git switch dev
git pull --ff-only origin dev
git config user.name "<본인 GitHub 이름>"
git config user.email "<본인 GitHub에 연결된 이메일 또는 noreply 주소>"
git switch -c <아래 표의 본인 브랜치 전체 이름>
git branch --show-current
git config user.name
git config user.email
```

마지막 `git switch -c` 명령에는 아래 표의 **전체 브랜치 이름**을 넣는다. 예: `git switch -c feature/agh3724-finance-pandas`. 자신의 계정이 아닌 작성자로 Commit하면 GitHub 개인 기여가 잘못 집계될 수 있다.

### 3 의미 있는 Commit 2회 이상

첫 Commit에는 실제 SQL/Python/Pandas 기능을, 두 번째에는 실제 데이터 실행을 바탕으로 한 검증·오류 수정·예외 처리를 담는다. 공백·파일명만 바꾼 Commit은 세지 않는다.

```bash
git status --short
git add <본인이 수정한 코드 파일> <필요한 검증 기록 파일>
git diff --cached --check
git commit -m "feat: <실제 구현 내용>"
# 검증·수정 작업 후
git add <본인이 수정한 파일>
git diff --cached --check
git commit -m "test: <실제 검증 또는 수정 내용>"
git log -2 --format="%h %an <%ae> %s"
git push -u origin <본인 브랜치 이름>
```

`git add .`는 키·원본 데이터를 실수로 추가할 수 있으므로 파일을 지정한다. 각 Commit URL은 GitHub 브랜치의 **Commits**에서 복사해 Issue와 `CONTRIBUTION.md`에 기록한다.

### 4 `dev` 대상 PR

GitHub 저장소의 **Pull requests → New pull request**에서 `base: dev`, `compare: 본인 feature 브랜치`를 확인한다. [GitHub의 PR 생성 안내](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)를 따른다. PR 본문에는 아래를 채운다.

```text
관련 Issue: #번호
내가 작성한 코드: 파일 경로와 핵심 기능
실행 방법: 실제 실행한 명령 또는 Notebook 셀
검증 결과: 데이터 범위, 행 수, 계산 예시, 예상값과 실제값
SQL·Pandas 비교: 같은 기업·기간·단위·필터인지, 일치/불일치 건수
AI 사용: 실제 프롬프트·직접 검증·판단을 기록한 ai_log.md 위치
남은 한계: 확인하지 못한 데이터나 결과
리뷰 요청: 아래 표의 지정 팀원
```

`dev`는 기본 브랜치가 아니므로 PR 본문에는 `관련 Issue: #번호`처럼 참조를 적고, 필요하면 PR 오른쪽 **Development**에서 Issue를 직접 연결한다. `Closes #번호`만으로는 `dev` 병합 시 Issue가 자동 종료되지 않는다. [GitHub의 Issue 연결 안내](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)를 참고한다.

### 5 타인 PR Review와 병합

지정된 상대의 PR에서 **Files changed**를 읽고 실제 데이터·스키마·기간·단위·중복·검증을 확인한다. 코드 줄에 질문이나 수정 제안을 남긴 뒤 **Review changes → Approve** 또는 **Request changes → Submit review**를 누른다. 단순 댓글, 이모지, AI 답변 복사만으로는 검토를 끝냈다고 기록하지 않는다. [GitHub의 Review 절차](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request)를 따른다.

수정 Commit이 추가되면 이전 승인이 무효가 될 수 있으므로 마지막 Push 뒤 승인 상태를 다시 확인한다. 승인과 대화 해결 후 `dev`에 병합한다. **Create a merge commit**을 사용하면 개인의 두 Commit이 통합 브랜치 기록에도 그대로 남는다.

### 6 기여 기록과 최종 반영

본인 Issue에 아래 완료 댓글을 남기고, `CONTRIBUTION.md`의 **본인 이름 아래만** 실제 링크로 채운다. 리뷰 URL은 실제 Review를 제출한 뒤 적는다. 시점이 달라 본인 PR에 반영하기 어렵다면 통합 문서 PR에서 사실을 확인한 뒤 갱신한다.

```text
작업 완료: [날짜/시간]
브랜치 URL: [링크]
의미 있는 Commit 1·2: [각 링크와 구현 내용]
내 PR URL: [링크, base=dev]
내 PR을 검토한 팀원과 Review URL: [링크]
내가 검토한 다른 팀원 PR·Review URL: [링크]
dev 병합 URL: [링크]
최종 Notebook/보고서에서 내 코드·결과가 사용된 위치: [파일과 절]
60초 설명: [입력 → 처리 → 출력 → 직접 검증을 본인 말로 3~5문장]
```

`dev`에서 SQL·Pandas 교차검증과 결과 보고를 마친 뒤 **`dev` → `main` PR**을 만들고 다른 팀원의 Review 후 병합한다. `main`에 직접 Push하지 않는다.

## 팀원별 정확한 기록

| 팀원 | 담당 Issue | 본인 브랜치 | 코드 산출물 | 첫 Commit 예시 | 둘째 Commit에 남길 검증 | 직접 Review할 PR |
| --- | --- | --- | --- | --- | --- | --- |
| 이영 `twozero3213-beep` | [#2](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/2), [#3](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/3) | `feature/setup-collaboration` | `src/dart_fetch.py`, `src/build_db.py` | 이미 있는 협업 설정·API 코드 Commit URL 기록 | Open DART 실제 응답, SQLite 행 수, 키 비노출 검증 | 임도윤의 #8 PR |
| 강동윤 `dongyungang94-coder` | [#4](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/4) | `feature/dongyungang94-coder-finance-sql` | `sql/queries_finance.sql` | 기업·사업연도별 재무 SQL | 연결/별도, 금액 변환, 중복·0 분모, 실행 결과 | 안지형의 #6 PR |
| 나지수 `skwltn2004-code` | [#5](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/5) | `feature/skwltn2004-code-disclosure-sql` | `sql/queries_disclosure.sql` | 기간·유형별 공시 SQL | 정정공시·중복·접수일 경계, 실행 결과 | 이정수의 #7 PR |
| 안지형 `agh3724` | [#6](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/6) | `feature/agh3724-finance-pandas` | `notebooks/analysis_finance.ipynb` | 재무지표 전기 대비 Pandas 계산 | 분모 0/음수·결측, SQL 결과 대조 | 강동윤의 #4 PR |
| 이정수 `jw082501` | [#7](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/7) | `feature/jw082501-disclosure-pandas` | `notebooks/analysis_disclosure.ipynb` | 기간·유형별 Pandas 집계 | 정정·중복 기준, 후보 기준 민감도, SQL 대조 | 나지수의 #5 PR |
| 임도윤 `odyn0624` | [#8](https://github.com/twozero3213-beep/kb-bridge-financial-detective/issues/8) | 현재 Fork의 [`feature/limdoyun-ai`](https://github.com/odyn0624/kb-bridge-financial-detective/tree/feature/limdoyun-ai) | 현재 `src/briefing_limdoyun.py`, `tests/test_briefing_limdoyun.py`; #8의 교차검증 산출물은 별도 확인 필요 | 이미 올린 브리핑 코드 Commit URL 기록 | 실제 SQL·Pandas 일치·불일치 건수와 차이 원인을 검증해 #8 충족 | 이영의 [PR #9](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9) |

이영의 #2·#3 작업은 이미 `feature/setup-collaboration`에서 PR #9로 열려 있다. 두 의미 있는 Commit은 [협업 설정](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/d3ddad19455d9ec4ab54ff459f5ae4d48952e582), [API·DB 코드](https://github.com/twozero3213-beep/kb-bridge-financial-detective/commit/4fb1c959f6e9be541352a50c51c1513b0febe36b)다. **임도윤의 실제 Review와 이영 본인의 코드 설명·직접 검증은 아직 별도 확인해야 한다.**

안지형이 예전에 만든 PR #1은 `main → main`으로 병합됐고 Commit이 1개라서 이 안내서의 **개인 feature → dev, Commit 2회, 타인 Review** 기준을 충족하는 증거로 세지 않는다. #6 작업은 새 기능 브랜치와 별도 PR로 진행한다.

임도윤은 이미 본인 Fork에 `feature/limdoyun-ai`와 본인 작성 Commit 3개를 올렸다. 이는 코드 Push 증거다. [PR #9의 리뷰 요청](https://github.com/twozero3213-beep/kb-bridge-financial-detective/pull/9)과는 별개이며, 본인 산출물도 `base: twozero3213-beep:dev`, `compare: odyn0624:feature/limdoyun-ai`로 PR을 열어야 한다. 현재 브리핑 코드는 #8에 배정된 SQL·Pandas 교차검증과 범위가 다르므로, 실제 검증 결과를 추가하고 Issue #8에 근거를 기록한 뒤 완료로 표시한다.

## AI 사용 기록

[팀원별 프롬프트 초안](team_prompts.md)은 실제 입력을 넣어 수정한 뒤 사용한다. 사용 후 `ai_log.md`에 **실제로 보낸 프롬프트, AI 결과, 사람이 직접 실행·대조한 방법과 결과, 채택·수정·폐기 이유**를 기록한다. 팀 전체 최소 2건이 필요하다. 실행하지 않은 코드를 정상 작동했다고 쓰지 않는다.
