"""같은 SQLite 원본을 SQL과 Pandas로 독립 집계해 결과를 대조한다."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd


FINANCE_KEYS = ["corp_code", "bsns_year", "fs_div", "sj_div", "account_nm", "ord"]
TEAM_FINANCE_KEYS = ["corp_code", "bsns_year", "reprt_code", "fs_div", "sj_div", "account_nm"]
DISCLOSURE_KEYS = ["corp_code", "year", "report_nm"]


def compare(sql, pandas, keys, values, *, tolerance=0):
    """키 누락·중복과 계산값 차이를 모두 보고한다."""
    if sql.duplicated(keys).any() or pandas.duplicated(keys).any():
        return {"status": "CHECK", "reason": "duplicate_keys", "rows": 0, "mismatches": []}
    joined = sql.merge(pandas, on=keys, how="outer", suffixes=("_sql", "_pandas"),
                       indicator=True, validate="one_to_one")
    mismatches = []
    for _, row in joined.iterrows():
        differences = {}
        if row["_merge"] != "both":
            differences["presence"] = str(row["_merge"])
        else:
            for value in values:
                left, right = row[f"{value}_sql"], row[f"{value}_pandas"]
                if pd.isna(left) and pd.isna(right):
                    continue
                if pd.isna(left) or pd.isna(right) or abs(float(left) - float(right)) > tolerance:
                    differences[value] = {"sql": None if pd.isna(left) else float(left),
                                          "pandas": None if pd.isna(right) else float(right)}
        if differences:
            mismatches.append({"key": {key: str(row[key]) for key in keys},
                               "differences": differences})
    return {"status": "PASS" if not mismatches else "CHECK",
            "rows": len(joined), "mismatch_count": len(mismatches),
            "mismatches": mismatches[:20]}


def validate(database):
    """재무 증감액·증감률과 공시 연도/유형별 건수를 각각 계산한다."""
    with closing(sqlite3.connect(database)) as db:
        finance_sql = pd.read_sql_query("""
            SELECT corp_code, bsns_year, fs_div, sj_div, account_nm, ord,
                   CAST(REPLACE(thstrm_amount, ',', '') AS REAL) AS current,
                   CAST(REPLACE(frmtrm_amount, ',', '') AS REAL) AS previous,
                   CAST(REPLACE(thstrm_amount, ',', '') AS REAL)
                     - CAST(REPLACE(frmtrm_amount, ',', '') AS REAL) AS change_amount,
                   CASE WHEN CAST(REPLACE(frmtrm_amount, ',', '') AS REAL) <> 0
                        THEN 100.0 * (CAST(REPLACE(thstrm_amount, ',', '') AS REAL)
                          - CAST(REPLACE(frmtrm_amount, ',', '') AS REAL))
                          / ABS(CAST(REPLACE(frmtrm_amount, ',', '') AS REAL))
                   END AS change_pct
            FROM finance
        """, db)
        raw_finance = pd.read_sql_query("""
            SELECT corp_code, bsns_year, reprt_code, fs_div, sj_div, account_nm, ord,
                   currency,
                   thstrm_amount, frmtrm_amount FROM finance
        """, db)
        finance_pandas = raw_finance[FINANCE_KEYS].copy()
        finance_pandas["current"] = pd.to_numeric(
            raw_finance["thstrm_amount"].str.replace(",", "", regex=False), errors="coerce")
        finance_pandas["previous"] = pd.to_numeric(
            raw_finance["frmtrm_amount"].str.replace(",", "", regex=False), errors="coerce")
        finance_pandas["change_amount"] = finance_pandas.current - finance_pandas.previous
        finance_pandas["change_pct"] = (
            100 * finance_pandas.change_amount / finance_pandas.previous.abs()
        ).where(finance_pandas.previous.ne(0))

        disclosures_sql = pd.read_sql_query("""
            SELECT corp_code, SUBSTR(rcept_dt, 1, 4) AS year, report_nm,
                   COUNT(*) AS count FROM disclosures
            GROUP BY corp_code, SUBSTR(rcept_dt, 1, 4), report_nm
        """, db)
        raw_disclosures = pd.read_sql_query(
            "SELECT corp_code, rcept_dt, report_nm FROM disclosures", db)
        raw_disclosures["year"] = raw_disclosures.rcept_dt.str.slice(0, 4)
        disclosures_pandas = (raw_disclosures.groupby(DISCLOSURE_KEYS, dropna=False)
                              .size().rename("count").reset_index())

        # 강동윤 담당 SQL의 실제 결과를 별도 Pandas 계산과 같은 키로 대조한다.
        finance_sql_file = Path(__file__).resolve().parents[1] / "sql" / "queries_finance.sql"
        db.executescript(finance_sql_file.read_text(encoding="utf-8"))
        team_sql = pd.read_sql_query("SELECT * FROM finance_q1_changes", db)
        team_raw = raw_finance.loc[
            raw_finance.reprt_code.eq("11011") & raw_finance.currency.eq("KRW")
            & raw_finance.account_nm.isin(("매출액", "영업이익", "당기순이익(손실)", "자산총계"))
        ].copy()
        team_raw["source_rows"] = team_raw.groupby(TEAM_FINANCE_KEYS, dropna=False)["ord"].transform("size")
        team_raw["ord_number"] = pd.to_numeric(team_raw.ord, errors="coerce").fillna(0)
        team_raw = team_raw.sort_values("ord_number").drop_duplicates(TEAM_FINANCE_KEYS)
        for source, target in (("thstrm_amount", "current_amount"),
                               ("frmtrm_amount", "previous_amount")):
            amount = team_raw[source].str.replace(",", "", regex=False).str.strip()
            team_raw[target] = pd.to_numeric(amount.where(amount.str.fullmatch(r"-?\d+")),
                                             errors="coerce")
        team_raw["change_amount"] = team_raw.current_amount - team_raw.previous_amount
        team_raw["change_pct"] = (
            100 * team_raw.change_amount / team_raw.previous_amount.abs()
        ).where(team_raw.previous_amount.ne(0))
        team_finance = compare(team_sql, team_raw, TEAM_FINANCE_KEYS,
                               ["source_rows", "current_amount", "previous_amount",
                                "change_amount", "change_pct"], tolerance=1e-6)

    invalid_amounts = int(finance_pandas[["current", "previous"]].isna().any(axis=1).sum())
    invalid_dates = int((~raw_disclosures.rcept_dt.str.fullmatch(r"\d{8}").fillna(False)).sum())
    finance = compare(finance_sql, finance_pandas, FINANCE_KEYS,
                      ["current", "previous", "change_amount", "change_pct"],
                      tolerance=1e-6)
    disclosures = compare(disclosures_sql, disclosures_pandas, DISCLOSURE_KEYS, ["count"])
    status = "PASS" if (finance["status"] == disclosures["status"] == team_finance["status"] == "PASS"
                        and finance["rows"] and disclosures["rows"] and team_finance["rows"]
                        and not invalid_amounts and not invalid_dates) else "CHECK"
    return {"status": status, "finance": finance, "disclosures": disclosures,
            "team_finance_sql": team_finance,
            "invalid_amount_rows": invalid_amounts, "invalid_disclosure_dates": invalid_dates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="로컬 dart.sqlite 경로")
    parser.add_argument("--output", type=Path, help="검증 JSON 저장 경로")
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error(f"DB 파일이 없습니다: {args.database}")
    report = validate(args.database)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
