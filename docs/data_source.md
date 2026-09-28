# Open DART 데이터 연결

## 선택한 데이터

- 단일회사 주요계정: 사업연도와 보고서 코드 `11011`로 주요 재무계정을 조회한다. [공식 개발가이드](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019016)
- 공시검색: 고유번호와 접수일 범위로 공시 목록을 조회한다. 여러 페이지를 모두 가져와야 기간별 빈도를 계산할 수 있다. [공식 개발가이드](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001)
- DART 고유번호는 회사별 8자리 코드이며, 주식코드와 다르다. [공식 고유번호 안내](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019018)

2026-09-28에 공용 로컬 설정의 키로 공식 문서 예시 고유번호 `00126380`을 조회했다. 2024년 사업보고서 주요계정과 2024년 공시검색 모두 `status=000`을 반환했다. 이는 **API 연결 확인**이며, 재무변화·공시패턴의 분석 결과나 사람의 검증 완료를 뜻하지 않는다.

## 로컬 실행

각 팀원은 자신의 `DART_API_KEY`를 환경 변수로 설정한다. 키가 들어 있는 파일이나 명령 출력은 GitHub에 올리지 않는다.

```bash
python -m src.dart_fetch <8자리_고유번호> <4자리_사업연도>
```

응답 JSON은 `data/raw/`에 저장되며 `.gitignore`로 Git에서 제외된다. `finance`에는 주요계정 원본 응답이, `disclosures`에는 해당 연도의 모든 페이지를 합친 공시 목록이 들어간다. `tests/test_dart_fetch.py`는 네트워크 없이 페이지 결합을 검사한다.

같은 데이터로 SQL을 실행하려면 `python -m src.build_db`를 실행한다. `data/processed/dart.sqlite`에 `finance`와 `disclosures` 테이블을 다시 만든다. 이 DB는 생성 파일이므로 두 테이블을 재생성한다. 금액 열은 원본 문자열(쉼표 포함)로 보존한다. SQL 담당자는 변환 기준을 명시해 숫자로 비교해야 한다.

## 분석 전 확인

- 기업·사업연도·접수일이 분석 질문과 일치하는지 확인한다.
- 재무제표의 연결/별도(`fs_div`), 재무제표 유형(`sj_div`), 통화(`currency`), 기준 기간을 구분한다.
- 공시의 `rcept_no`와 `rcept_dt`를 확인하고 정정공시·중복 집계 기준을 정한다.
- SQL과 Pandas 집계는 동일한 기업·기간·단위·필터에서 비교한다.
- API가 막히면 강사 제공 CSV의 이용 가능 여부와 컬럼을 확인한다. 합성 데이터를 실제 기업 결과로 표현하지 않는다.
