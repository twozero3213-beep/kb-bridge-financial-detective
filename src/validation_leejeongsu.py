"""Team result validation. CHECK means review needed, never company risk."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def result(name, passed, **details):
    return dict(name=name, status='PASS' if passed else 'CHECK', details=details)


def quality(frame, keys, expected_rows=None):
    missing = sorted(set(keys) - set(frame.columns))
    checks = [result('schema', bool(keys) and not missing, missing_columns=missing),
              result('row_count', len(frame) > 0 and
                     (expected_rows is None or len(frame) == expected_rows),
                     actual=len(frame), expected=expected_rows)]
    nulls = frame.isna() | frame.astype('string').apply(lambda s: s.str.strip().eq('')).fillna(False).astype(bool)
    counts = {str(k): int(v) for k, v in nulls.sum().items() if v}
    checks.append(result('missing_values', not counts, counts=counts))
    if keys and not missing:
        duplicates = int(frame.duplicated(keys, keep=False).sum())
        checks.append(result('duplicate_keys', duplicates == 0, affected_rows=duplicates))
    return checks


def compare_results(sql, pandas, keys, metrics, atol=0, rtol=0):
    """Compare unique groups by outer join; numeric metrics default to exact equality."""
    if not keys or not metrics or set(keys) & set(metrics):
        raise ValueError('Nonempty, disjoint keys and metrics required')
    if not np.isfinite([atol, rtol]).all() or min(atol, rtol) < 0:
        raise ValueError('Tolerances must be finite and nonnegative')
    checks = []
    for label, frame in [('sql', sql), ('pandas', pandas)]:
        for item in quality(frame.reindex(columns=keys + metrics), keys):
            item['name'] = label + '.' + item['name']
            checks.append(item)
    if any(c['status'] == 'CHECK' for c in checks):
        return checks
    merged = sql[keys + metrics].merge(pandas[keys + metrics], on=keys,
        how='outer', suffixes=('_sql', '_pandas'), indicator=True, validate='one_to_one')
    absent = merged['_merge'].ne('both')
    checks.append(result('group_coverage', not absent.any(),
        mismatches=merged.loc[absent, keys + ['_merge']].astype(str).to_dict('records')))
    for metric in metrics:
        a = pd.to_numeric(merged[metric + '_sql'], errors='coerce').to_numpy(dtype=float)
        b = pd.to_numeric(merged[metric + '_pandas'], errors='coerce').to_numpy(dtype=float)
        same = np.isfinite(a) & np.isfinite(b) & np.isclose(a, b, atol=atol, rtol=rtol)
        checks.append(result('compare.' + metric, bool(same.all()), atol=atol, rtol=rtol,
            mismatches=merged.loc[~same, keys + [metric + '_sql', metric + '_pandas']]
            .astype(str).to_dict('records')))
    return checks


def validate_changes(frame, keys, threshold_pct=50, min_abs_change=1):
    """Explicit paired periods; abs(previous) denominator; zero baseline undefined."""
    if not np.isfinite([threshold_pct, min_abs_change]).all() or min(threshold_pct, min_abs_change) < 0:
        raise ValueError('Thresholds must be finite and nonnegative')
    required = keys + ['previous', 'current', 'change_pct', 'candidate']
    if not keys or not set(required).issubset(frame.columns):
        return [result('changes.schema', False, required=required)]
    checks = quality(frame[keys + ['previous', 'current']], keys)
    for item in checks:
        item['name'] = 'changes.' + item['name']
    previous = pd.to_numeric(frame.previous, errors='coerce').to_numpy(dtype=float)
    current = pd.to_numeric(frame.current, errors='coerce').to_numpy(dtype=float)
    valid = np.isfinite(previous) & np.isfinite(current) & (previous != 0)
    rate = np.full(len(frame), np.nan)
    np.divide((current - previous) * 100, np.abs(previous), out=rate, where=valid)
    given = pd.to_numeric(frame.change_pct, errors='coerce').to_numpy(dtype=float)
    blank = (frame.change_pct.isna() | frame.change_pct.astype(str).str.strip().eq('')).to_numpy()
    same = (valid & np.isfinite(given) & np.isclose(rate, given, atol=1e-8, rtol=0)) | (~valid & blank)
    checks.append(result('changes.rate', bool(same.all()), mismatch_rows=np.flatnonzero(~same).tolist()))
    expected = (np.abs(rate) >= threshold_pct) & (np.abs(current - previous) >= min_abs_change)
    flags = frame.candidate.astype('string').str.strip().str.lower().fillna('')
    match = np.where(valid, flags.eq('true').to_numpy(dtype=bool) == expected,
                     flags.eq('').to_numpy(dtype=bool))
    match &= np.where(valid, flags.isin(['true', 'false']).to_numpy(), True)
    checks.append(result('changes.candidate', bool(match.all()), threshold_pct=threshold_pct,
        min_abs_change=min_abs_change, mismatch_rows=np.flatnonzero(~match).tolist()))
    checks.append(result('changes.comparable_baseline', bool(valid.all()),
        undefined_rows=np.flatnonzero(~valid).tolist()))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['sql', 'pandas', 'output']:
        parser.add_argument('--' + name, required=True, type=Path)
    for name in ['keys', 'metrics']:
        parser.add_argument('--' + name, required=True, nargs='+')
    parser.add_argument('--changes', type=Path)
    parser.add_argument('--threshold-pct', type=float, default=50)
    parser.add_argument('--min-abs-change', type=float, default=1)
    parser.add_argument('--atol', type=float, default=0)
    parser.add_argument('--rtol', type=float, default=0)
    args = parser.parse_args()
    read = lambda path: pd.read_csv(path, dtype=str, keep_default_na=False)
    try:
        checks = compare_results(read(args.sql), read(args.pandas), args.keys, args.metrics, args.atol, args.rtol)
        if args.changes:
            checks += validate_changes(read(args.changes), args.keys, args.threshold_pct, args.min_abs_change)
        else:
            checks.append(result('changes.not_supplied', False, reason='Rate/candidate checks not run'))
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        checks = [result('input', False, error=str(exc))]
    report = dict(status='PASS' if all(c['status'] == 'PASS' for c in checks) else 'CHECK',
                  inputs=dict(sql=str(args.sql), pandas=str(args.pandas), changes=str(args.changes)), checks=checks)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print(report['status'])
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

