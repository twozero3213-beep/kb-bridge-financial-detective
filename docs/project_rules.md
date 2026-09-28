# 프로젝트 협업 규칙

1. `main` 브랜치에서 직접 기능을 개발하지 않는다.
2. `dev` 브랜치를 통합 브랜치로 사용한다.
3. 개인 기능은 `dev`에서 분기한 `feature/<name>-<area>` 브랜치에서 개발한다. 역할 확정 전 개인 브랜치를 만들지 않는다.
4. 작업 전에 Issue를 생성하고 목적과 완료 조건을 적는다.
5. Issue마다 담당자를 지정한다.
6. 각 담당자는 의미 있는 Commit을 최소 2회 남긴다.
7. 의미 없는 공백·파일명 수정은 기여로 취급하지 않는다.
8. 모든 개인 작업은 Push 후 Pull Request(PR)를 만든다.
9. 각 팀원은 다른 팀원의 PR을 최소 1회 Review한다.
10. Review를 반영한 뒤 PR을 `dev`에 Merge한다.
11. `dev`에서 SQL·Pandas 결과와 전체 산출물을 통합 검증한 뒤 `main`에 Merge한다.
12. 각 팀원은 자신의 코드와 검증 내용을 60초 안에 설명할 수 있어야 한다.
13. AI가 만든 코드·SQL·분석 결과는 사람이 직접 실행하거나 원천 데이터와 비교해 검증한다.
14. AI 결과의 채택·수정·폐기 판단과 이유를 `ai_log.md`에 기록한다.
15. 개인 코드가 최종 결과물에 실제 포함되어야 한다. `CONTRIBUTION.md`에 연결된 Issue·Commit·PR·Review를 기록한다.
16. 6명 모두 독립 산출물을 맡는다. AI 기록·발표·자료조사만 맡는 역할은 개인 코드 기여를 충족하지 않는다.
17. PR에는 실행·검증 결과를 적고, 리뷰어는 단순 승인 대신 질문·수정 제안·검증 의견을 남긴다.

분석 결과는 ‘변화 발견’, ‘이상값 후보’, ‘확인 후보’, ‘추가 검토 필요’처럼 근거 범위 안에서 표현한다. 확인하지 못한 원인이나 기업 위험을 단정하지 않는다. API 키·비밀번호·원본 데이터는 저장소에 Commit하지 않는다.

브랜치 구조 예시: `main` → `dev` → `feature/<name>-data`, `feature/<name>-sql`, `feature/<name>-finance`, `feature/<name>-disclosure`, `feature/<name>-validation`, `feature/<name>-ai`. 담당자와 기능은 추후 결정한다.

## 형상관리 증거 확인 순서

팀원마다 GitHub에서 **Issue 담당자 → 개인 브랜치 → 의미 있는 Commit 2회 이상 → Push → `dev` 대상 PR → 다른 팀원의 실제 Review → `dev` Merge → 최종 산출물 반영**을 순서대로 확인한다. PR 설명, 체크박스, 로컬 파일만으로 완료 판정하지 않는다. `main` 반영은 `dev` 통합 검증 후 별도 PR과 Review 기록으로 확인한다.

확인할 때는 Issue·Commit·PR·Review URL을 `CONTRIBUTION.md`에 남기고, GitHub의 브랜치·커밋·PR 기록과 대조한다. 초대만 받은 상태, 미배정 Issue, 열린 PR, 승인 없는 Merge는 각 단계의 완료가 아니다. 강사의 평가에서 GitHub 협업 과정 20점과 개인 기여 증거 10점이 별도 항목이므로 여섯 명 모두의 기록을 확인한다.
