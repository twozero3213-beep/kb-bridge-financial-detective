"""공시 SQL과 독립 Pandas 계산의 월·유형·정정·전년 비교."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from src.run_disclosure_sql import run


class DisclosureSQLTest(unittest.TestCase):
    def test_actual_schema_and_invalid_date(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "sample.sqlite"
            with closing(sqlite3.connect(database)) as db, db:
                db.execute("""CREATE TABLE disclosures (
                    corp_code TEXT, rcept_no TEXT, rcept_dt TEXT, report_nm TEXT
                )""")
                db.executemany("INSERT INTO disclosures VALUES (?, ?, ?, ?)", [
                    ("001", "1", "20230615", "사업보고서 "),
                    ("001", "2", "20230616", "[기재정정]사업보고서"),
                    ("001", "3", "20240615", "사업보고서"),
                    ("001", "4", "20240616", "사업보고서"),
                    ("001", "5", "20240617", "사업보고서"),
                    ("002", "6", "20240617", "사업보고서"),
                ])
            result = run(database)
            self.assertEqual((result["raw"], result["type_groups"], result["months"]),
                             (6, 4, 3))
            self.assertEqual(result["corrections"], 1)
            with closing(sqlite3.connect(database)) as db:
                row = db.execute("""SELECT count, previous_count, change_count,
                                  change_pct, candidate FROM disclosure_q2_monthly
                                  WHERE corp_code = '001' AND period = '2024-06'""").fetchone()
            self.assertEqual(row, (3, 2, 1, 50.0, 0))
            with closing(sqlite3.connect(database)) as db, db:
                db.execute("UPDATE disclosures SET rcept_dt = '20241340' WHERE rcept_no = '5'")
            with self.assertRaisesRegex(ValueError, "접수일"):
                run(database)


if __name__ == "__main__":
    unittest.main()
