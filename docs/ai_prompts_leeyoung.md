# 이영 담당 AI 입력문

## 역할·도구·실제 이행

- **담당:** Issue #2 형상관리 구조, Issue #3 Open DART 수집·SQLite 적재. 나지수님 배정 Issue #5 공시 SQL의 대체 수행은 별도 코드·기록으로 남긴다.
- **필요 작업:** 실제 기업·기간·API 응답 확인 → 원본 키·금액 문자열 보존 → 로컬 DB 재생성 → 팀원 Issue·브랜치·커밋·PR·리뷰 확인 → `dev` 통합 → 최종 `main` 제출.
- **사용 AI 도구:** Codex 데스크톱. 이영의 요청을 받아 수집·적재 코드, 검사, Git 충돌 해결을 지원했다.
- **실행 증거:** `src/dart_fetch.py`, `src/build_db.py`, `tests/test_dart_fetch.py`, `tests/test_build_db.py`, `docs/data_source.md`, PR #9, `ai_log.md`의 이영 절.

아래 입력문은 담당 작업을 같은 기준으로 재현하거나 추가 점검할 때 사용하는 **구체적 초안**이다. 실제 사용자 입력과 혼동하지 않는다. API 키·원본 JSON 전체는 AI 대화나 Git에 넣지 않는다.

## 프롬프트 1: Open DART 데이터 파이프라인

```text
나는 KB Bridge 기업 재무·공시 이상징후 탐정의 데이터·형상관리 담당이다.
Issue #3의 src/dart_fetch.py와 src/build_db.py를 검토해 줘.
기업은 삼성전자 DART 고유번호 00126380, 기간은 2023·2024년이다.
fnlttSinglAcnt.json의 사업보고서(11011) 주요계정과 list.json의 공시를
로컬 JSON 4개로 저장한 뒤 finance·disclosures SQLite 테이블을 만든다.
공시 페이지 누락, 접수번호 중복, 접수일 형식, 금액 문자열/원화 단위,
CFS/OFS 혼합, 원본 응답 실패 시 잘못된 DB 생성 가능성을 지적해 줘.
실행 명령과 실제 원본·DB 행 수를 대조할 쿼리를 제시하고 숫자를 추측하지 마.
키를 답변이나 저장소에 노출하지 마.
```

## 프롬프트 2: GitHub 형상관리 점검

```text
Issue #2의 협업 규칙과 CONTRIBUTION.md를 실제 GitHub 기록에 대조해 줘.
팀원별 담당 Issue, 작업 범위 댓글, 해당 계정 작성 커밋 2개 이상,
dev 대상 PR 본문, 다른 팀원에게 제출한 Review, dev merge, AI 사용·검증
기록과 최종 main 반영을 링크로 확인해 줘. 댓글과 제출된 Review를 구분해 줘.
기존 dev의 완료 기록이 PR 충돌 해결 때 지워지지 않게 검사하고,
미완료 항목은 완료로 표시하지 마. PR #9 충돌 해결 후 전체 테스트와
재무 60행·공시 438건 DB 재생성을 확인해 줘.
```

## 직접 확인한 결과

Codex가 로컬 Open DART JSON 4개에서 SQLite 재무 60행·공시 438건을 재생성하고 전체 검사 26개를 통과했다. PR #9의 `CONTRIBUTION.md` 충돌에서는 최신 `dev` 기여 링크를 보존했다. 최종 `main` 반영과 Issue #5 공시 SQL 통합은 후속 단계에서 확인한다.
