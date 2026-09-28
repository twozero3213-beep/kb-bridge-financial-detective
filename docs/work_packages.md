# 개인 작업 후보와 분배 기준

참고 문서는 팀당 3~4명을 권장한다. 이 팀은 6명이므로 작업 경계를 더 분명히 하고, **6명 모두** 최종 결과물에 포함되는 SQL 또는 Python/Pandas 코드를 맡는다. 2026-09-28에 아래처럼 배정했다. 실제 데이터와 스키마를 확인한 뒤 Issue 범위를 조정할 수 있지만, 개인 코드·PR·리뷰 기준은 모두에게 동일하게 적용한다. AI 기록·발표만 담당하는 역할은 만들지 않는다.

| 후보 | 독립 코드 산출물 | 완료 증거 | 난이도·의존성 |
| --- | --- | --- | --- |
| 데이터 수집·구조 확인 | `src/load_data.py` 등 데이터 로드/검사 코드 | 출처·컬럼·식별자·기간·결측 확인 | 높음. Open DART/API 또는 제공 데이터가 필요 |
| 재무 SQL | `sql/queries_finance.sql` | 기업·기간별 지표 조회와 계산 근거 | 중간. 실제 스키마 확정 후 가능 |
| 공시 SQL | `sql/queries_disclosure.sql` | 기간별 빈도·유형 집계와 기준 | 중간. 실제 스키마 확정 후 가능 |
| 재무 Pandas | `notebooks/analysis_finance.ipynb` 등 | Q1 변화 계산, 단위·분모 검증 | 중간~높음. 재무 데이터 필요 |
| 공시 Pandas | `notebooks/analysis_disclosure.ipynb` 등 | Q2 집계, 평소 대비 확인 후보 | 중간. 공시 데이터 필요 |
| 교차검증 | `src/validate_results.py` 등 | 동일 기업·기간·집계 기준의 SQL/Pandas 비교 | 높음. SQL·Pandas 결과가 선행 |

| 담당자 | GitHub | Issue | 개인 브랜치 예정 | 기본 리뷰 대상 |
| --- | --- | --- | --- | --- |
| 이영 · 데이터 수집·구조 확인 | `twozero3213-beep` | #3 | `feature/twozero3213-beep-data` | 임도윤 PR |
| 강동윤 · 재무 SQL | `dongyungang94-coder` | #4 | `feature/dongyungang94-coder-finance-sql` | 안지형 PR |
| 나지수 · 공시 SQL | `skwltn2004-code` | #5 | `feature/skwltn2004-code-disclosure-sql` | 이정수 PR |
| 안지형 · 재무 Pandas | `agh3724` | #6 | `feature/agh3724-finance-pandas` | 강동윤 PR |
| 이정수 · 공시 Pandas | `jw082501` | #7 | `feature/jw082501-disclosure-pandas` | 나지수 PR |
| 임도윤 · 교차검증 | `odyn0624` | #8 | `feature/odyn0624-validation` | 이영 PR |

위 리뷰 대상은 최소 1회 상호 검토를 빠뜨리지 않기 위한 배정이다. 실제 PR이 열리면 GitHub에서 리뷰어를 요청한다. 이영은 저장소 관리도 맡지만, 개인 코드 산출물과 검증 기준은 동일하다. 데이터 수집·DB 생성 공용 골격은 이미 있으므로 이영의 남은 데이터 검증 범위를 과도하게 늘리지 않는다. 교차검증은 선행 결과가 필요하므로 임도윤은 초반에 비교 키·단위 규칙을 정하고 후반에 실제 불일치를 확인한다. 데이터 수집이 막히면 강사 제공 CSV의 사용 가능 여부를 확인한다. 실제 스키마 없이 완성된 SQL이나 분석 결과를 가정하지 않는다.

## 완료 판정

1. 모든 팀원이 담당 Issue, 개인 브랜치, 의미 있는 Commit 2회 이상, `dev` 대상 PR, 다른 팀원 PR Review 1회 이상을 남긴다.
2. 각자의 SQL 또는 Python/Pandas 코드가 통합 결과물에서 실제 사용된다. 파일 존재만으로 완료 처리하지 않는다.
3. SQL과 Pandas 결과를 같은 키·기간·단위로 교차검증하고 차이를 설명한다.
4. AI 사용 사례 2개 이상에 직접 검증 방법과 채택·수정·폐기 이유를 기록한다.
5. `dev` 통합 검증 후 `main`으로 PR을 보내고 Review를 거쳐 제출한다.

GitHub 커밋·PR·Review 기록은 실제 팀원의 행동으로만 채운다. 빈 체크박스와 미배정 Issue는 기여 증거가 아니다.
