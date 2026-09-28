"""공통 DB가 원본 금액과 공시 키를 보존하는지 확인한다."""

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from src.build_db import build_database


class BuildDatabaseTest(unittest.TestCase):
    def test_finance_and_disclosure_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "sample_finance.json").write_text(json.dumps({
                "status": "000", "list": [{"corp_code": "00126380", "bsns_year": "2024",
                                         "account_nm": "자산총계", "thstrm_amount": "1,200"}]
            }), encoding="utf-8")
            (root / "sample_disclosures.json").write_text(json.dumps([
                {"corp_code": "00126380", "rcept_no": "20240101000001", "rcept_dt": "20240101"}
            ]), encoding="utf-8")
            database = root / "result.sqlite"
            self.assertEqual(build_database(root, database), (1, 1))
            with closing(sqlite3.connect(database)) as db:
                self.assertEqual(db.execute("SELECT thstrm_amount FROM finance").fetchone()[0], "1,200")
                self.assertEqual(db.execute("SELECT rcept_no FROM disclosures").fetchone()[0], "20240101000001")


if __name__ == "__main__":
    unittest.main()
