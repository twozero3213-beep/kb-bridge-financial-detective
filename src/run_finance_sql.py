"""Issue #4의 재무 SQL을 로컬 SQLite에서 실행한다."""

import argparse
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


SQL_FILE = Path(__file__).resolve().parents[1] / "sql" / "queries_finance.sql"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("corp_code")
    parser.add_argument("year")
    parser.add_argument("--fs-div", choices=("CFS", "OFS"), default="CFS")
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error(f"DB 파일이 없습니다: {args.database}")
    if not (args.corp_code.isascii() and args.corp_code.isdigit() and len(args.corp_code) == 8):
        parser.error("corp_code는 8자리 숫자여야 합니다")
    if not (args.year.isascii() and args.year.isdigit() and len(args.year) == 4):
        parser.error("year는 4자리 숫자여야 합니다")

    with closing(sqlite3.connect(args.database)) as db:
        db.row_factory = sqlite3.Row
        db.executescript(SQL_FILE.read_text(encoding="utf-8"))
        rows = db.execute("""
            SELECT * FROM finance_q1_changes
            WHERE corp_code = ? AND bsns_year = ? AND fs_div = ?
            ORDER BY sj_div, account_nm
        """, (args.corp_code, args.year, args.fs_div)).fetchall()
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2))
    return 0 if rows and all(row["current_amount"] is not None
                             and row["previous_amount"] is not None for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
