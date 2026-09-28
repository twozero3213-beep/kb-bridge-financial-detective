"""재무 SQL의 중복·음수·0 분모·잘못된 금액 처리를 확인한다."""

import sqlite3
import unittest
from contextlib import closing
from pathlib import Path


SQL_FILE = Path(__file__).resolve().parents[1] / "sql" / "queries_finance.sql"


class FinanceSQLTest(unittest.TestCase):
    def test_finance_changes(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.executescript("""
                CREATE TABLE finance (
                    corp_code TEXT, bsns_year TEXT, reprt_code TEXT, fs_div TEXT,
                    sj_div TEXT, account_nm TEXT, ord TEXT, currency TEXT,
                    thstrm_amount TEXT, frmtrm_amount TEXT
                );
                INSERT INTO finance VALUES
                ('00126380','2024','11011','CFS','IS','매출액','1','KRW','1,200','1,000'),
                ('00126380','2024','11011','CFS','IS','당기순이익(손실)','2','KRW','200','-100'),
                ('00126380','2024','11011','CFS','IS','당기순이익(손실)','3','KRW','200','-100'),
                ('00126380','2024','11011','CFS','IS','영업이익','4','KRW','50','0'),
                ('00126380','2024','11011','OFS','IS','매출액','5','KRW','500','400'),
                ('00126380','2024','11011','CFS','BS','자산총계','6','KRW','abc','200');
            """)
            db.executescript(SQL_FILE.read_text(encoding="utf-8"))
            rows = db.execute("""
                SELECT account_nm, fs_div, current_amount, previous_amount,
                       change_amount, change_pct, source_rows
                FROM finance_q1_changes
            """).fetchall()

        self.assertEqual(len(rows), 5)
        by_key = {(row[0], row[1]): row[2:] for row in rows}
        self.assertEqual(by_key[("매출액", "CFS")][:3], (1200, 1000, 200))
        self.assertEqual(by_key[("매출액", "CFS")][3], 20.0)
        self.assertEqual(by_key[("매출액", "OFS")][:3], (500, 400, 100))
        self.assertEqual(by_key[("당기순이익(손실)", "CFS")], (200, -100, 300, 300.0, 2))
        self.assertIsNone(by_key[("영업이익", "CFS")][3])
        self.assertIsNone(by_key[("자산총계", "CFS")][0])


if __name__ == "__main__":
    unittest.main()
