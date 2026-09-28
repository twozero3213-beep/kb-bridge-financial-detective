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
