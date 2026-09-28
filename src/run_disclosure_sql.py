"""Issue #5 공시 SQL을 실제 SQLite에 실행하고 Issue #7 Pandas와 대조한다."""

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.disclosure_pandas_leejeongsu import analyze
from src.validation_leejeongsu import compare_results


QUERY = Path(__file__).resolve().parents[1] / "sql" / "queries_disclosure.sql"


def run(database):
    with closing(sqlite3.connect(database)) as db:
        raw = pd.read_sql_query("SELECT * FROM disclosures", db)
        pandas_type, pandas_month = analyze(raw)
        db.executescript(QUERY.read_text(encoding="utf-8"))
        sql_type = pd.read_sql_query("SELECT * FROM disclosure_q2_by_type", db)
        sql_month = pd.read_sql_query("SELECT * FROM disclosure_q2_monthly", db)

    by_type = compare_results(sql_type, pandas_type,
                              ["corp_code", "period", "report_type"],
                              ["count", "correction_count"])
    current = sql_month.loc[sql_month.period.str.startswith("2024")]
    pandas_current = pandas_month.loc[pandas_month.period.str.startswith("2024")]
    by_month = compare_results(current, pandas_current, ["corp_code", "period"],
                               ["count", "correction_count", "previous_count",
                                "change_count", "change_pct", "candidate"], atol=1e-8)
    checks = by_type + by_month
    failures = [item for item in checks if item["status"] != "PASS"]
    if failures:
        raise ValueError(f"SQL/Pandas 불일치: {failures}")
    return {"raw": len(raw), "type_groups": len(sql_type), "months": len(sql_month),
            "corrections": int(sql_type.correction_count.sum()),
            "candidate_months_2024": current.loc[current.candidate.eq(1), "period"].tolist(),
            "checks": len(checks)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", nargs="?", type=Path,
                        default=Path("data/processed/dart.sqlite"))
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error(f"SQLite 파일 없음: {args.database}")
    print(run(args.database))


if __name__ == "__main__":
    main()
