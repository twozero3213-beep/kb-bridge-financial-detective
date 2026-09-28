-- Issue #7 self-check reference. NOT the SQL author's deliverable for Issue #5.
-- Run only after Python's input checks reject null/invalid/conflicting records.
-- Same input table, independently implemented DISTINCT + CASE + GROUP BY.
WITH RECURSIVE
months(period) AS (
    SELECT substr(:start_iso, 1, 7)
    UNION ALL
    SELECT strftime('%Y-%m', date(period || '-01', '+1 month'))
    FROM months WHERE date(period || '-01', '+1 month') < :end_iso
),
types(disclosure_type) AS (
    VALUES ('사업보고서'), ('반기보고서'), ('분기보고서'), ('기타')
),
deduplicated AS (
    SELECT DISTINCT corp_code, rcept_no, rcept_dt, report_nm
    FROM disclosures
    WHERE corp_code = :corp_code
),
classified AS (
    SELECT corp_code, substr(rcept_dt, 1, 4) || '-' || substr(rcept_dt, 5, 2) AS period,
        CASE WHEN instr(report_nm, '사업보고서') > 0 THEN '사업보고서'
             WHEN instr(report_nm, '반기보고서') > 0 THEN '반기보고서'
             WHEN instr(report_nm, '분기보고서') > 0 THEN '분기보고서'
             ELSE '기타' END AS disclosure_type
    FROM deduplicated
    WHERE rcept_dt >= :start AND rcept_dt < :end
      AND (:include_corrections = 1 OR instr(report_nm, '정정') = 0)
),
counts AS (
    SELECT corp_code, period, disclosure_type, COUNT(*) AS count
    FROM classified GROUP BY corp_code, period, disclosure_type
)
SELECT :corp_code AS corp_code, months.period, types.disclosure_type,
       COALESCE(counts.count, 0) AS count
FROM months CROSS JOIN types
LEFT JOIN counts ON counts.period = months.period AND counts.disclosure_type = types.disclosure_type
ORDER BY months.period, types.disclosure_type;
