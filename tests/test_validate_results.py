"""SQL·Pandas 교차검증의 정상·불일치 경로를 확인한다."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.validate_results import compare, validate


class ValidateResultsTest(unittest.TestCase):
    def test_real_tables_and_mismatch_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "sample.sqlite"
            with closing(sqlite3.connect(database)) as db:
                db.executescript("""
                    CREATE TABLE finance (
                      corp_code TEXT, bsns_year TEXT, fs_div TEXT, sj_div TEXT,
                      account_nm TEXT, ord TEXT, reprt_code TEXT, currency TEXT,
                      thstrm_amount TEXT, frmtrm_amount TEXT
                    );
                    CREATE TABLE disclosures (
                      corp_code TEXT, rcept_dt TEXT, report_nm TEXT
                    );
                    INSERT INTO finance VALUES
                      ('00126380','2024','CFS','IS','매출액','1','11011','KRW','1,200','1,000'),
                      ('00126380','2024','CFS','IS','영업이익','2','11011','KRW','50','0');
                    INSERT INTO disclosures VALUES
                      ('00126380','20240101','사업보고서'),
                      ('00126380','20240102','사업보고서');
                """)
            report = validate(database)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["finance"]["rows"], 2)
            self.assertEqual(report["disclosures"]["rows"], 1)
            self.assertEqual(report["team_finance_sql"]["rows"], 2)
            self.assertEqual(report["team_finance_sql"]["mismatch_count"], 0)

            with closing(sqlite3.connect(database)) as db:
                db.execute("INSERT INTO disclosures VALUES ('00126380', NULL, '사업보고서')")
                db.commit()
            self.assertEqual(validate(database)["status"], "CHECK")
            self.assertEqual(validate(database)["invalid_disclosure_dates"], 1)

        sql = pd.DataFrame({"corp_code": ["00126380"], "count": [2]})
        pandas = pd.DataFrame({"corp_code": ["00126380"], "count": [3]})
        result = compare(sql, pandas, ["corp_code"], ["count"])
        self.assertEqual(result["status"], "CHECK")
        self.assertEqual(result["mismatch_count"], 1)
        self.assertEqual(result["mismatches"][0]["differences"]["count"],
                         {"sql": 2.0, "pandas": 3.0})


if __name__ == "__main__":
    unittest.main()
