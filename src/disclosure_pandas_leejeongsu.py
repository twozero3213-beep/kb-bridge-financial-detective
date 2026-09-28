"""Issue #7: 공시 월별·유형별 빈도와 전년 같은 달의 변화."""

import pandas as pd
from datetime import datetime
from math import isfinite


REQUIRED = {"corp_code", "rcept_no", "rcept_dt", "report_nm"}


def analyze(disclosures, threshold_pct=50, min_change=10):
    """접수번호를 1건으로 세며 정정 공시도 별도 접수로 포함한다."""
    missing = REQUIRED - set(disclosures.columns)
    if missing:
        raise ValueError(f"disclosures 컬럼 누락: {', '.join(sorted(missing))}")
    if disclosures.empty:
        raise ValueError("공시 원본이 비어 있습니다")
    if not all(isfinite(value) and value >= 0 for value in (threshold_pct, min_change)):
        raise ValueError("후보 기준은 0 이상의 유한 숫자여야 합니다")
    rows = disclosures.copy()
    if (rows.rcept_no.isna().any() or rows.rcept_no.astype("string").str.strip().eq("").any()
            or rows.rcept_no.duplicated().any()):
        raise ValueError("접수번호 누락 또는 중복")
    try:
        if any(not isinstance(value, str) or len(value) != 8 or not value.isdigit()
               for value in rows.rcept_dt.tolist()):
            raise ValueError("접수일 형식 오류")
        dates = [datetime.strptime(value, "%Y%m%d") for value in rows.rcept_dt.tolist()]
    except (TypeError, ValueError) as exc:
        raise ValueError("접수일 형식 오류") from exc
    rows["report_type"] = rows.report_nm.astype("string").str.strip()
    if rows.report_type.isna().any() or rows.report_type.eq("").any():
        raise ValueError("공시 유형 누락")
    rows["period"] = [value.strftime("%Y-%m") for value in dates]
    rows["is_correction"] = rows.report_type.str.startswith(("[기재정정]", "[첨부추가]"))
    by_type = (rows.groupby(["corp_code", "period", "report_type"], as_index=False)
               .agg(count=("rcept_no", "size"), correction_count=("is_correction", "sum")))
    monthly = (by_type.groupby(["corp_code", "period"], as_index=False)
               [["count", "correction_count"]].sum())
    monthly["previous_period"] = [f"{int(value[:4])-1}{value[4:]}" for value in monthly.period]
    previous = monthly[["corp_code", "period", "count"]].rename(
        columns={"period": "previous_period", "count": "previous_count"})
    monthly = monthly.merge(previous, on=["corp_code", "previous_period"], how="left",
                            validate="one_to_one")
    monthly["change_count"] = monthly["count"] - monthly.previous_count
    monthly["change_pct"] = 100 * monthly.change_count / monthly.previous_count
    monthly["candidate"] = (monthly.change_pct.abs().ge(threshold_pct)
                            & monthly.change_count.abs().ge(min_change))
    return by_type.sort_values(["corp_code", "period", "report_type"]).reset_index(drop=True), monthly.sort_values(["corp_code", "period"]).reset_index(drop=True)
