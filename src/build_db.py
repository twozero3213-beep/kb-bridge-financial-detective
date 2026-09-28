"""로컬 Open DART JSON을 팀 공통 SQLite 테이블로 적재한다."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path


FINANCE_COLUMNS = (
    "corp_code", "bsns_year", "reprt_code", "fs_div", "sj_div", "account_nm",
    "thstrm_amount", "frmtrm_amount", "bfefrmtrm_amount", "currency", "rcept_no", "ord",
)
DISCLOSURE_COLUMNS = (
    "corp_code", "corp_name", "rcept_no", "rcept_dt", "report_nm",
    "corp_cls", "stock_code", "flr_nm", "rm",
)


def build_database(source_dir, database_path):
    source_dir = Path(source_dir)
    database_path = Path(database_path)
    finance_files = sorted(source_dir.glob("*_finance.json"))
    disclosure_files = sorted(source_dir.glob("*_disclosures.json"))
    if not finance_files or not disclosure_files:
        raise ValueError("data/raw에 재무·공시 JSON이 모두 필요합니다.")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as db, db:
        db.executescript("""
            DROP TABLE IF EXISTS finance;
            DROP TABLE IF EXISTS disclosures;
            CREATE TABLE finance (
                corp_code TEXT, bsns_year TEXT, reprt_code TEXT, fs_div TEXT,
                sj_div TEXT, account_nm TEXT, thstrm_amount TEXT,
                frmtrm_amount TEXT, bfefrmtrm_amount TEXT, currency TEXT,
                rcept_no TEXT, ord TEXT
            );
            CREATE TABLE disclosures (
                corp_code TEXT, corp_name TEXT, rcept_no TEXT, rcept_dt TEXT,
                report_nm TEXT, corp_cls TEXT, stock_code TEXT, flr_nm TEXT, rm TEXT
            );
            CREATE INDEX finance_company_year ON finance(corp_code, bsns_year);
            CREATE INDEX disclosure_company_date ON disclosures(corp_code, rcept_dt);
        """)
        for path in finance_files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("status") != "000":
                raise ValueError(f"정상 Open DART 응답이 아닙니다: {path.name}")
            db.executemany(
                "INSERT INTO finance VALUES (" + ",".join("?" * len(FINANCE_COLUMNS)) + ")",
                ([row.get(column) for column in FINANCE_COLUMNS] for row in payload["list"]),
            )
        for path in disclosure_files:
            rows = json.loads(path.read_text(encoding="utf-8"))
            db.executemany(
                "INSERT INTO disclosures VALUES (" + ",".join("?" * len(DISCLOSURE_COLUMNS)) + ")",
                ([row.get(column) for column in DISCLOSURE_COLUMNS] for row in rows),
            )
        return (db.execute("SELECT COUNT(*) FROM finance").fetchone()[0],
                db.execute("SELECT COUNT(*) FROM disclosures").fetchone()[0])


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    counts = build_database(root / "data" / "raw", root / "data" / "processed" / "dart.sqlite")
    print(f"finance={counts[0]}, disclosures={counts[1]} → data/processed/dart.sqlite")
