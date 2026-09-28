"""공시 유형 집계의 기간·정정·중복 반례."""

import unittest
import sqlite3
from contextlib import closing

import pandas as pd

from src.disclosure_pandas_leejeongsu import analyze


class DisclosurePandasTest(unittest.TestCase):
    def test_sqlite_loaded_dates_regression(self):
        raw = pd.DataFrame([
            ("001", f"{number:014d}", "20240101", "사업보고서")
            for number in range(438)
        ], columns=["corp_code", "rcept_no", "rcept_dt", "report_nm"])
        with closing(sqlite3.connect(":memory:")) as db:
            raw.to_sql("disclosures", db, index=False)
            loaded = pd.read_sql_query("SELECT * FROM disclosures", db)
        by_type, monthly = analyze(loaded)
        self.assertEqual(int(by_type["count"].sum()), 438)
        self.assertEqual(int(monthly["count"].sum()), 438)

    def test_period_type_correction_and_candidate(self):
        raw = pd.DataFrame([
            ("001", "1", "20230615", "사업보고서 "),
            ("001", "2", "20230616", "[기재정정]사업보고서"),
            ("001", "3", "20240615", "사업보고서"),
            ("001", "4", "20240616", "사업보고서"),
            ("001", "5", "20240617", "사업보고서"),
            ("002", "6", "20240617", "사업보고서"),
        ], columns=["corp_code", "rcept_no", "rcept_dt", "report_nm"])
        by_type, monthly = analyze(raw, threshold_pct=50, min_change=1)
        self.assertEqual(len(by_type), 4)
        current = monthly.loc[monthly.corp_code.eq("001") & monthly.period.eq("2024-06")].iloc[0]
        self.assertEqual((current["count"], current.previous_count, current.change_pct), (3, 2, 50))
        self.assertTrue(current.candidate)
        self.assertEqual(int(by_type.correction_count.sum()), 1)
        self.assertTrue(pd.isna(monthly.loc[monthly.corp_code.eq("002"), "previous_count"].iloc[0]))
        with self.assertRaisesRegex(ValueError, "중복"):
            analyze(pd.concat([raw, raw.iloc[[0]]]))
        with self.assertRaisesRegex(ValueError, "접수일"):
            analyze(raw.assign(rcept_dt="20241340"))
        with self.assertRaisesRegex(ValueError, "후보 기준"):
            analyze(raw, threshold_pct=-1)


if __name__ == "__main__":
    unittest.main()
