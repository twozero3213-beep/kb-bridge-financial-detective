-- 공통 제출 SQL: Q1 재무 + Q2 공시. src/build_db.py의 SQLite에 실행.

-- Issue #4 강동윤: Open DART 주요계정의 전기 대비 재무 변화(Q1).
-- 입력: src/build_db.py가 만든 SQLite finance 테이블. 금액 단위는 원본 KRW.
-- 11011(사업보고서)만 사용하고 CFS(연결)와 OFS(별도)는 섞지 않는다.

DROP VIEW IF EXISTS finance_q1_changes;
CREATE VIEW finance_q1_changes AS
WITH raw AS (
    SELECT corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm,
           ord, currency,
           REPLACE(TRIM(thstrm_amount), ',', '') AS current_text,
           REPLACE(TRIM(frmtrm_amount), ',', '') AS previous_text
    FROM finance
    WHERE reprt_code = '11011' AND currency = 'KRW'
      AND account_nm IN ('매출액', '영업이익', '당기순이익(손실)', '자산총계')
), parsed AS (
    SELECT *,
           CASE WHEN current_text <> '' AND (
                    current_text NOT GLOB '*[^0-9]*' OR
                    (SUBSTR(current_text, 1, 1) = '-'
                     AND SUBSTR(current_text, 2) <> ''
                     AND SUBSTR(current_text, 2) NOT GLOB '*[^0-9]*'))
                THEN CAST(current_text AS INTEGER) END AS current_amount,
           CASE WHEN previous_text <> '' AND (
                    previous_text NOT GLOB '*[^0-9]*' OR
                    (SUBSTR(previous_text, 1, 1) = '-'
                     AND SUBSTR(previous_text, 2) <> ''
                     AND SUBSTR(previous_text, 2) NOT GLOB '*[^0-9]*'))
                THEN CAST(previous_text AS INTEGER) END AS previous_amount
    FROM raw
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
               PARTITION BY corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm
               ORDER BY CAST(ord AS INTEGER)
           ) AS row_number,
           COUNT(*) OVER (
               PARTITION BY corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm
           ) AS source_rows
    FROM parsed
)
SELECT corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm, ord,
       currency, source_rows, current_amount, previous_amount,
       current_amount - previous_amount AS change_amount,
       CASE WHEN previous_amount IS NOT NULL AND previous_amount <> 0
            THEN 100.0 * (current_amount - previous_amount) / ABS(previous_amount)
       END AS change_pct
FROM ranked
WHERE row_number = 1;

-- 예시 실행: 회사·연도·CFS/OFS를 먼저 선택한다. 2024 전기 금액은 2023 당기
-- 금액의 반복 정보이므로 두 연도 값을 합산하지 않는다.
SELECT corp_code, bsns_year, fs_div, sj_div, account_nm, current_amount,
       previous_amount, change_amount, change_pct, source_rows
FROM finance_q1_changes
WHERE corp_code = '00126380' AND bsns_year = '2024' AND fs_div = 'CFS'
ORDER BY sj_div, account_nm;

-- 품질 점검: 중복 원본 계정이나 숫자로 읽을 수 없는 금액은 확인한다.
SELECT corp_code, bsns_year, fs_div, sj_div, account_nm, source_rows,
       current_amount, previous_amount
FROM finance_q1_changes
WHERE source_rows > 1 OR current_amount IS NULL OR previous_amount IS NULL
ORDER BY corp_code, bsns_year, fs_div, sj_div, account_nm;


-- Issue #5 나지수 배정 공시 SQL. 이영 계정에서 대체 구현·업로드.
-- 입력: src/build_db.py가 만든 SQLite disclosures. 접수번호 1건당 공시 1건.
-- 정정·첨부추가 접수도 포함하고 별도 수로 표시한다.

DROP VIEW IF EXISTS disclosure_q2_monthly;
DROP VIEW IF EXISTS disclosure_q2_month_counts;
DROP VIEW IF EXISTS disclosure_q2_by_type;

CREATE VIEW disclosure_q2_by_type AS
SELECT corp_code,
       substr(rcept_dt, 1, 4) || '-' || substr(rcept_dt, 5, 2) AS period,
       trim(report_nm) AS report_type,
       count(*) AS count,
       sum(CASE WHEN trim(report_nm) LIKE '[기재정정]%'
                     OR trim(report_nm) LIKE '[첨부추가]%'
                THEN 1 ELSE 0 END) AS correction_count
FROM disclosures
GROUP BY corp_code, period, report_type;

CREATE VIEW disclosure_q2_month_counts AS
SELECT corp_code, period, sum(count) AS count,
       sum(correction_count) AS correction_count
FROM disclosure_q2_by_type
GROUP BY corp_code, period;

CREATE VIEW disclosure_q2_monthly AS
SELECT cur.corp_code, cur.period, cur.count, cur.correction_count,
       prev.count AS previous_count,
       cur.count - prev.count AS change_count,
       CASE WHEN prev.count > 0
            THEN 100.0 * (cur.count - prev.count) / prev.count
            ELSE NULL END AS change_pct,
       CASE WHEN prev.count > 0
                     AND abs(100.0 * (cur.count - prev.count) / prev.count) >= 50
                     AND abs(cur.count - prev.count) >= 10
            THEN 1 ELSE 0 END AS candidate
FROM disclosure_q2_month_counts AS cur
LEFT JOIN disclosure_q2_month_counts AS prev
  ON prev.corp_code = cur.corp_code
 AND prev.period = printf('%04d', cast(substr(cur.period, 1, 4) AS integer) - 1)
                   || substr(cur.period, 5);
