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
