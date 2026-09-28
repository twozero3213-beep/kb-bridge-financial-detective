"""Open DART 주요 재무계정을 Pandas로 전기 대비 분석한다 (Issue #6)."""

import pandas as pd


KEYS = ["corp_code", "bsns_year", "reprt_code", "fs_div", "sj_div", "account_nm"]
METRICS = ("매출액", "영업이익", "당기순이익(손실)", "자산총계")
REQUIRED = set(KEYS) | {"ord", "currency", "thstrm_amount", "frmtrm_amount"}


def analyze(finance):
    """사업보고서·KRW만 분석하고 CFS/OFS와 중복 원본 수를 보존한다."""
    missing = REQUIRED - set(finance.columns)
    if missing:
        raise ValueError(f"finance 컬럼 누락: {', '.join(sorted(missing))}")

    rows = finance.loc[
        finance.reprt_code.eq("11011") & finance.currency.eq("KRW")
        & finance.account_nm.isin(METRICS)
    ].copy()
    rows["source_rows"] = rows.groupby(KEYS, dropna=False)["ord"].transform("size")
    rows["ord_number"] = pd.to_numeric(rows.ord, errors="coerce").fillna(0)
    rows = rows.sort_values("ord_number").drop_duplicates(KEYS)

    for source, target in (("thstrm_amount", "current_amount"),
                           ("frmtrm_amount", "previous_amount")):
        amount = rows[source].astype("string").str.replace(",", "", regex=False).str.strip()
        rows[target] = pd.to_numeric(amount.where(amount.str.fullmatch(r"-?\d+")),
                                     errors="coerce")
    rows["change_amount"] = rows.current_amount - rows.previous_amount
    rows["change_pct"] = (
        100 * rows.change_amount / rows.previous_amount.abs()
    ).where(rows.previous_amount.ne(0))
    return (rows[KEYS + ["ord", "currency", "source_rows", "current_amount",
                         "previous_amount", "change_amount", "change_pct"]]
            .sort_values(KEYS).reset_index(drop=True))
