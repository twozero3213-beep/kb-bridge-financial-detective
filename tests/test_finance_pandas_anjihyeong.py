"""안지형 Pandas 결과를 강동윤 SQL과 같은 입력으로 비교한다."""

import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.finance_pandas_anjihyeong import KEYS, analyze
from src.validate_results import compare


SQL_FILE = Path(__file__).resolve().parents[1] / "sql" / "queries_finance.sql"


class FinancePandasTest(unittest.TestCase):
    def test_actual_schema_and_edge_cases(self):
        columns = ["corp_code", "bsns_year", "reprt_code", "fs_div", "sj_div",
                   "account_nm", "ord", "currency", "thstrm_amount", "frmtrm_amount"]
        raw = pd.DataFrame([
            ("00126380", "2024", "11011", "CFS", "IS", "매출액", "1", "KRW", "1,200", "1,000"),
            ("00126380", "2024", "11011", "CFS", "IS", "당기순이익(손실)", "2", "KRW", "200", "-100"),
            ("00126380", "2024", "11011", "CFS", "IS", "당기순이익(손실)", "3", "KRW", "200", "-100"),
            ("00126380", "2024", "11011", "CFS", "IS", "영업이익", "4", "KRW", "50", "0"),
            ("00126380", "2024", "11011", "OFS", "IS", "매출액", "5", "KRW", "500", "400"),
            ("00126380", "2024", "11011", "CFS", "BS", "자산총계", "6", "KRW", "abc", "200"),
        ], columns=columns)
        pandas_result = analyze(raw)

        with closing(sqlite3.connect(":memory:")) as db:
            raw.to_sql("finance", db, index=False)
            db.executescript(SQL_FILE.read_text(encoding="utf-8"))
            sql_result = pd.read_sql_query("SELECT * FROM finance_q1_changes", db)
        check = compare(sql_result, pandas_result, KEYS,
                        ["source_rows", "current_amount", "previous_amount",
                         "change_amount", "change_pct"], tolerance=1e-6)
        self.assertEqual(check["status"], "PASS")
        self.assertEqual(check["rows"], 5)
        cfs = pandas_result.loc[pandas_result.fs_div.eq("CFS")].set_index("account_nm")
        self.assertEqual(cfs.loc["매출액", "change_pct"], 20.0)
        self.assertEqual(cfs.loc["당기순이익(손실)", "change_pct"], 300.0)
        self.assertEqual(cfs.loc["당기순이익(손실)", "source_rows"], 2)
        self.assertTrue(pd.isna(cfs.loc["영업이익", "change_pct"]))
        self.assertTrue(pd.isna(cfs.loc["자산총계", "current_amount"]))


if __name__ == "__main__":
    unittest.main()
