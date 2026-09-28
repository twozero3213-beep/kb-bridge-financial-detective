"""Issue #7: monthly disclosure counts from the team's disclosures schema."""
from __future__ import annotations

from contextlib import closing
from pathlib import Path
import re
import sqlite3

import pandas as pd

COLUMNS = ['corp_code', 'rcept_no', 'rcept_dt', 'report_nm']
KEYS = ['corp_code', 'period', 'disclosure_type']
TYPES = ['사업보고서', '반기보고서', '분기보고서', '기타']


def month_boundary(value: str) -> pd.Timestamp:
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Dates must use YYYY-MM-DD')
    stamp = pd.Timestamp(value)
    if stamp.day != 1:
        raise ValueError('Use full months: every range boundary must be the first day')
    return stamp


def validate_window(corp_code, start, end, coverage_start, coverage_end):
    if not re.fullmatch(r'\d{8}', corp_code):
        raise ValueError('corp_code must contain 8 digits')
    start, end, coverage_start, coverage_end = map(
        month_boundary, [start, end, coverage_start, coverage_end])
    if not coverage_start <= start < end <= coverage_end:
        raise ValueError('Analysis window must be inside declared complete data coverage')
    return start, end, coverage_start, coverage_end


def load_disclosures(database: str | Path, corp_code: str) -> pd.DataFrame:
    """Read only: a wrong path must never create an empty database."""
    path = Path(database).resolve()
    if not path.is_file():
        raise FileNotFoundError(f'Team database not found: {path}')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        columns = {row[1] for row in db.execute('PRAGMA table_info(disclosures)')}
        if not set(COLUMNS) <= columns:
            raise ValueError(f'disclosures is missing columns: {sorted(set(COLUMNS) - columns)}')
        return pd.read_sql_query(
            'SELECT corp_code, rcept_no, rcept_dt, report_nm FROM disclosures WHERE corp_code = ?',
            db, params=(corp_code,), dtype={column: 'string' for column in COLUMNS})


def prepare_disclosures(frame: pd.DataFrame, corp_code: str, corrections='include'):
    if corrections not in ('include', 'exclude'):
        raise ValueError('corrections must be include or exclude')
    if not set(COLUMNS) <= set(frame.columns):
        raise ValueError(f'Missing columns: {sorted(set(COLUMNS) - set(frame.columns))}')
    rows = frame.loc[frame.corp_code.eq(corp_code), COLUMNS].copy()
    if rows.empty:
        raise ValueError('No rows for this company; collection completeness cannot be inferred')
    if rows.isna().any().any() or rows.astype('string').apply(lambda x: x.str.strip().eq('')).any().any():
        raise ValueError('Missing required disclosure values; fix input instead of dropping rows')
    rows = rows.astype('string')
    if not rows.rcept_dt.str.fullmatch(r'\d{8}').all():
        raise ValueError('rcept_dt must use YYYYMMDD')
    rows['date'] = pd.to_datetime(rows.rcept_dt, format='%Y%m%d', errors='raise')
    variants = rows[COLUMNS].drop_duplicates()
    if variants.duplicated('rcept_no', keep=False).any():
        raise ValueError('Conflicting records share rcept_no; do not choose one silently')
    audit = {'company_input_rows': len(rows), 'duplicate_rows_removed': len(rows) - len(variants)}
    rows = rows.drop_duplicates('rcept_no').copy()
    rows['is_correction'] = rows.report_nm.str.contains('정정', regex=False)
    audit['correction_rows'] = int(rows.is_correction.sum())
    if corrections == 'exclude':
        rows = rows.loc[~rows.is_correction].copy()
    rows['disclosure_type'] = '기타'
    # Ordered title-based heuristic; these are not official DART classification codes.
    for title in reversed(TYPES[:-1]):
        rows.loc[rows.report_nm.str.contains(title, regex=False), 'disclosure_type'] = title
    audit['corrections_policy'] = corrections
    return rows, audit


def monthly_counts(frame, corp_code, start, end, coverage_start, coverage_end,
                   corrections='include'):
    """[start,end); caller explicitly declares complete collection coverage.

    Build a full calendar including zero-count months and a prior month when covered.
    Data minima/maxima cannot establish collection completeness.
    """
    start_dt, end_dt, coverage_dt, _ = validate_window(
        corp_code, start, end, coverage_start, coverage_end)
    rows, audit = prepare_disclosures(frame, corp_code, corrections)
    baseline = max(coverage_dt, start_dt - pd.offsets.MonthBegin(1))
    selected = rows.loc[(rows.date >= baseline) & (rows.date < end_dt)].copy()
    selected['period'] = selected.date.dt.strftime('%Y-%m')
    periods = pd.date_range(baseline, end_dt, freq='MS', inclusive='left').strftime('%Y-%m')
    grid = pd.MultiIndex.from_product([[corp_code], periods, TYPES], names=KEYS)
    counts = selected.groupby(KEYS).size().reindex(grid, fill_value=0).rename('count').reset_index()
    counts['previous_count'] = counts.groupby(['corp_code', 'disclosure_type'])['count'].shift().astype('Int64')
    counts['change'] = counts['count'] - counts['previous_count']
    counts['change_pct'] = (counts.change / counts.previous_count.where(counts.previous_count.ne(0)) * 100).astype('Float64')
    counts = counts.loc[counts.period.ge(start_dt.strftime('%Y-%m'))].reset_index(drop=True)
    analysis_rows = int(((rows.date >= start_dt) & (rows.date < end_dt)).sum())
    if int(counts['count'].sum()) != analysis_rows:
        raise AssertionError('Grouped counts do not reconcile to retained input rows')
    audit.update(analysis_rows=analysis_rows, grouped_rows=len(counts),
                 baseline_start=baseline.strftime('%Y-%m-%d'), start=start, end_exclusive=end,
                 coverage_start=coverage_start, coverage_end_exclusive=coverage_end,
                 coverage_basis='caller declaration; not inferred from receipt dates',
                 corp_code=corp_code)
    return counts, audit


def mark_candidates(monthly, threshold_pct=100, min_increase=3):
    """Increase-only review candidates; zero baseline uses absolute increase only."""
    import math
    if not math.isfinite(threshold_pct) or threshold_pct < 0 or min_increase < 1 or int(min_increase) != min_increase:
        raise ValueError('Use a finite nonnegative percentage and a positive integer increase')
    rows = monthly.copy()
    comparable = rows.previous_count.notna()
    positive = rows.previous_count.gt(0).fillna(False)
    enough = rows.change.ge(min_increase).fillna(False)
    new_activity = rows.previous_count.eq(0).fillna(False) & enough
    growth = positive & enough & rows.change_pct.ge(threshold_pct).fillna(False)
    rows['candidate'] = (new_activity | growth).astype('boolean').where(comparable)
    rows['candidate_reason'] = 'below_threshold'
    rows.loc[growth, 'candidate_reason'] = 'increase'
    rows.loc[new_activity, 'candidate_reason'] = 'new_activity_zero_baseline'
    rows.loc[~comparable, 'candidate_reason'] = 'no_previous_period'
    return rows


def sensitivity(monthly, percentages=(50, 100, 200), increases=(3, 5)):
    records = []
    for percentage in percentages:
        for increase in increases:
            marked = mark_candidates(monthly, percentage, increase)
            records.append({'threshold_pct': percentage, 'min_increase': increase,
                            'candidate_count': int(marked.candidate.fillna(False).sum()),
                            'uncomparable_count': int(marked.candidate.isna().sum())})
    return pd.DataFrame(records)


def compare_counts(pandas_counts, sql_counts):
    """Strict key comparison: missing SQL groups are not silently treated as zero."""
    import numpy as np
    columns = KEYS + ['count']
    for label, frame in [('pandas', pandas_counts), ('sql', sql_counts)]:
        if not set(columns) <= set(frame.columns):
            raise ValueError(f'{label} output needs columns {columns}')
        if frame.empty or frame[columns].isna().any().any() or frame.duplicated(KEYS).any():
            raise ValueError(f'{label} output is empty or contains nulls/duplicate keys')
        numeric = pd.to_numeric(frame['count'], errors='coerce')
        if not (np.isfinite(numeric) & numeric.ge(0) & numeric.mod(1).eq(0)).all():
            raise ValueError(f'{label} count must be a finite nonnegative integer')
    left, right = pandas_counts[columns].copy(), sql_counts[columns].copy()
    for frame in [left, right]:
        frame[KEYS] = frame[KEYS].astype('string')
        frame['count'] = pd.to_numeric(frame['count']).astype('int64')
    joined = left.merge(right, on=KEYS, how='outer', suffixes=('_pandas', '_sql'), indicator=True)
    joined['match'] = joined['_merge'].eq('both') & joined.count_pandas.eq(joined.count_sql)
    joined['reason'] = joined['_merge'].astype(str).map({
        'both': 'count_differs', 'left_only': 'missing_sql_group', 'right_only': 'missing_pandas_group'})
    joined.loc[joined.match, 'reason'] = 'match'
    return {'status': 'PASS' if joined.match.all() else 'CHECK',
            'matched': int(joined.match.sum()), 'mismatched': int((~joined.match).sum()),
            'differences': joined.loc[~joined.match].astype(str).to_dict('records')}


def read_settings(root, config_path=None):
    """Prefer local data config, then tracked team config. No guessed company or period."""
    import json
    root = Path(root).resolve()
    paths = [Path(config_path)] if config_path else [
        root / 'data/processed/disclosure_config.json', root / 'config/disclosure.json']
    if config_path and not paths[0].is_absolute():
        paths[0] = root / paths[0]
    path = next((p for p in paths if p.is_file()), None)
    if path is None:
        raise FileNotFoundError('Set data/processed/disclosure_config.json from config/disclosure.example.json')
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    required = ['corp_code', 'start', 'end', 'coverage_start', 'coverage_end', 'coverage_confirmed', 'corrections']
    if any(config.get(key) is None for key in required):
        raise ValueError(f'Configuration requires {required}')
    if config['coverage_confirmed'] is not True:
        raise ValueError('Collector must confirm complete pagination/coverage before zero filling')
    validate_window(config['corp_code'], config['start'], config['end'], config['coverage_start'], config['coverage_end'])
    if config['corrections'] not in ('include', 'exclude'):
        raise ValueError('corrections must be include or exclude')
    config['_config_path'] = str(path)
    return config


def execute_counts_sql(database, sql_path, config):
    """Single read-only team SELECT. The SQL file remains owned by its author."""
    params = {key: config[key] for key in ['corp_code', 'corrections']}
    for key in ['start', 'end', 'coverage_start', 'coverage_end']:
        params[key] = config[key].replace('-', '')
        params[key + '_iso'] = config[key]
    params['include_corrections'] = int(config['corrections'] == 'include')
    path = Path(database).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        return pd.read_sql_query(Path(sql_path).read_text(encoding='utf-8-sig'), db, params=params)


def run_analysis(root, config_path=None):
    """Re-run after DB/SQL/settings arrive; exports feed Notebook, validation and briefing."""
    import hashlib
    import json
    root = Path(root).resolve()
    config = read_settings(root, config_path)
    def resolve(value):
        path = Path(value)
        return path if path.is_absolute() else root / path
    database = resolve(config.get('database', 'data/processed/dart.sqlite'))
    raw = load_disclosures(database, config['corp_code'])
    monthly, audit = monthly_counts(raw, **{k: config[k] for k in [
        'corp_code', 'start', 'end', 'coverage_start', 'coverage_end', 'corrections']})
    monthly = mark_candidates(monthly, config.get('threshold_pct', 100), config.get('min_increase', 3))
    variations = sensitivity(monthly)
    reference_path = root / 'sql/disclosure_reference_jw082501.sql'
    reference = execute_counts_sql(database, reference_path, config)
    reference_check = compare_counts(monthly, reference)
    team_sql = resolve(config.get('team_sql', 'sql/queries_disclosure.sql'))
    team_check = {'status': 'CHECK', 'reason': 'Team SQL not yet available', 'path': str(team_sql)}
    if team_sql.is_file():
        try:
            team_result = execute_counts_sql(database, team_sql, config)
            team_check = compare_counts(monthly, team_result)
            team_check['sql_sha256'] = hashlib.sha256(team_sql.read_bytes()).hexdigest()
        except (ValueError, sqlite3.Error, pd.errors.DatabaseError, OSError) as exc:
            team_check = {'status': 'CHECK', 'reason': str(exc), 'path': str(team_sql)}
    audit['input_sha256'] = hashlib.sha256(raw.to_csv(index=False).encode('utf-8')).hexdigest()
    audit['reference_sql_sha256'] = hashlib.sha256(reference_path.read_bytes()).hexdigest()
    audit['pandas_version'] = pd.__version__
    report = {'status': 'PASS' if reference_check['status'] == team_check['status'] == 'PASS' else 'CHECK',
              'dataset_kind': config.get('dataset_kind', 'team_data_unverified_provenance'),
              'config': config, 'audit': audit, 'reference_sql': reference_check, 'team_sql': team_check,
              'candidate_count': int(monthly.candidate.fillna(False).sum()),
              'uncomparable_count': int(monthly.candidate.isna().sum())}
    output = resolve(config.get('output_dir', 'data/processed/disclosure_analysis'))
    output.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(output / 'monthly_counts.csv', index=False, encoding='utf-8-sig')
    monthly.loc[monthly.candidate.fillna(False)].to_csv(output / 'candidates.csv', index=False, encoding='utf-8-sig')
    variations.to_csv(output / 'sensitivity.csv', index=False, encoding='utf-8-sig')
    (output / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return monthly, variations, report


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    args = parser.parse_args()
    try:
        _, variations, report = run_analysis(Path(__file__).resolve().parents[1], args.config)
    except (ValueError, OSError, sqlite3.Error, pd.errors.DatabaseError) as exc:
        print(f'CHECK: {exc}')
        return 1
    print(variations.to_string(index=False))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
