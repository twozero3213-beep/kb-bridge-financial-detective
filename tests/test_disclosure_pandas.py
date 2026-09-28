from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.disclosure_pandas import COLUMNS, load_disclosures, monthly_counts


class DisclosureTests(unittest.TestCase):
    def rows(self):
        return pd.DataFrame([
            ['00126380', '1', '20240101', '사업보고서'],
            ['00126380', '1', '20240101', '사업보고서'],
            ['00126380', '2', '20240201', '[기재정정]사업보고서'],
            ['00126380', '3', '20240401', '분기보고서'],
        ], columns=COLUMNS)

    def analyze(self, frame=None, **kwargs):
        return monthly_counts(self.rows() if frame is None else frame,
            '00126380', '2024-02-01', '2024-04-01', '2024-01-01', '2024-05-01', **kwargs)

    def test_month_boundaries_duplicates_and_zero_month(self):
        monthly, audit = self.analyze()
        self.assertEqual(audit['duplicate_rows_removed'], 1)
        self.assertEqual(audit['analysis_rows'], 1)
        self.assertEqual(len(monthly), 8)
        annual = monthly[monthly.disclosure_type.eq('사업보고서')]
        self.assertEqual(annual['count'].tolist(), [1, 0])
        self.assertEqual(annual.previous_count.tolist(), [1, 1])
        self.assertEqual(annual.change_pct.tolist(), [0, -100])

    def test_correction_exclusion(self):
        monthly, audit = self.analyze(corrections='exclude')
        self.assertEqual(monthly['count'].sum(), 0)
        self.assertEqual(audit['correction_rows'], 1)

    def test_conflicting_receipt_rejected(self):
        frame = self.rows()
        frame.loc[1, 'report_nm'] = '반기보고서'
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.analyze(frame)

    def test_invalid_dates_and_nulls_rejected(self):
        for value in ['20240230', '2024-02-01', None]:
            frame = self.rows()
            frame.loc[0, 'rcept_dt'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.analyze(frame)

    def test_partial_month_and_coverage_rejected(self):
        for start, end in [('2024-02-02', '2024-04-01'), ('2023-12-01', '2024-04-01')]:
            with self.subTest(start=start), self.assertRaises(ValueError):
                monthly_counts(self.rows(), '00126380', start, end, '2024-01-01', '2024-05-01')

    def test_missing_prior_month_is_not_zero(self):
        monthly, _ = monthly_counts(self.rows(), '00126380', '2024-01-01', '2024-02-01', '2024-01-01', '2024-05-01')
        self.assertTrue(monthly.previous_count.isna().all())

    def test_readonly_database_and_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'dart.sqlite'
            with self.assertRaises(FileNotFoundError):
                load_disclosures(path, '00126380')
            self.assertFalse(path.exists())
            with closing(sqlite3.connect(path)) as db, db:
                self.rows().to_sql('disclosures', db, index=False)
            self.assertEqual(len(load_disclosures(path, '00126380')), 4)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'data/processed').mkdir(parents=True)
        (self.root / 'sql').mkdir()
        reference = Path(__file__).resolve().parents[1] / 'sql/disclosure_reference_jw082501.sql'
        (self.root / 'sql' / reference.name).write_bytes(reference.read_bytes())
        rows = []
        for month, count in [('01', 2), ('02', 5), ('03', 0), ('04', 6)]:
            rows += [['00126380', f'{month}{i}', f'2024{month}15', '기타 공시'] for i in range(count)]
        rows += [rows[0].copy(), ['00126380', 'correction', '20240229', '[기재정정]사업보고서'],
                 ['00126380', 'outside', '20240501', '분기보고서']]
        self.frame = pd.DataFrame(rows, columns=COLUMNS)
        with closing(sqlite3.connect(self.root / 'data/processed/dart.sqlite')) as db, db:
            self.frame.to_sql('disclosures', db, index=False)
        self.config = {'corp_code': '00126380', 'start': '2024-02-01', 'end': '2024-05-01',
                       'coverage_start': '2024-01-01', 'coverage_end': '2024-06-01',
                       'coverage_confirmed': True, 'corrections': 'include', 'dataset_kind': 'synthetic_test'}
        self.write_config()

    def tearDown(self):
        self.temp.cleanup()

    def write_config(self):
        import json
        (self.root / 'data/processed/disclosure_config.json').write_text(json.dumps(self.config), encoding='utf-8')

    def test_sql_crosscheck_and_candidate_sensitivity(self):
        from src.disclosure_pandas import run_analysis
        monthly, variation, report = run_analysis(self.root)
        self.assertEqual(report['reference_sql'], {'status': 'PASS', 'matched': 12, 'mismatched': 0, 'differences': []})
        self.assertEqual(report['team_sql']['status'], 'CHECK')
        self.assertEqual(report['status'], 'CHECK')
        self.assertEqual(report['candidate_count'], 2)
        self.assertEqual(report['audit']['analysis_rows'], 12)
        self.assertEqual(variation.candidate_count.tolist(), [2, 1, 2, 1, 1, 1])
        zero_baseline = monthly.loc[monthly.period.eq('2024-04') & monthly.disclosure_type.eq('기타')].iloc[0]
        self.assertTrue(pd.isna(zero_baseline.change_pct))
        self.assertEqual(zero_baseline.candidate_reason, 'new_activity_zero_baseline')

    def test_team_sql_arrival_is_picked_up_and_mismatches_exposed(self):
        from src.disclosure_pandas import run_analysis
        reference = self.root / 'sql/disclosure_reference_jw082501.sql'
        target = self.root / 'sql/queries_disclosure.sql'
        # Test double only; never evidence of the real teammate's SQL.
        target.write_bytes(reference.read_bytes())
        self.assertEqual(run_analysis(self.root)[2]['team_sql']['status'], 'PASS')
        target.write_text(reference.read_text(encoding='utf-8-sig').replace('COALESCE(counts.count, 0) AS count', 'COALESCE(counts.count, 0) + 1 AS count'), encoding='utf-8')
        report = run_analysis(self.root)[2]
        self.assertEqual(report['team_sql']['mismatched'], 12)
        self.assertEqual(report['team_sql']['status'], 'CHECK')

    def test_team_sql_cannot_write(self):
        from src.disclosure_pandas import run_analysis
        (self.root / 'sql/queries_disclosure.sql').write_text('DELETE FROM disclosures', encoding='utf-8')
        report = run_analysis(self.root)[2]
        self.assertEqual(report['team_sql']['status'], 'CHECK')
        self.assertEqual(len(load_disclosures(self.root / 'data/processed/dart.sqlite', '00126380')), len(self.frame))

    def test_unconfirmed_coverage_stops(self):
        from src.disclosure_pandas import run_analysis
        self.config['coverage_confirmed'] = False
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'confirm'):
            run_analysis(self.root)

    def test_reference_excluding_corrections(self):
        from src.disclosure_pandas import run_analysis
        self.config['corrections'] = 'exclude'
        self.write_config()
        report = run_analysis(self.root)[2]
        self.assertEqual(report['audit']['analysis_rows'], 11)
        self.assertEqual(report['reference_sql']['status'], 'PASS')

    def test_sql_duplicate_and_missing_group(self):
        from src.disclosure_pandas import compare_counts, monthly_counts
        counts, _ = monthly_counts(self.frame, '00126380', '2024-02-01', '2024-05-01', '2024-01-01', '2024-06-01')
        report = compare_counts(counts, counts.iloc[1:])
        self.assertEqual(report['mismatched'], 1)
        with self.assertRaises(ValueError):
            compare_counts(counts, pd.concat([counts, counts]))

    def test_notebook_cells_execute_on_synthetic_db(self):
        import contextlib
        import io
        import json
        import os
        from unittest.mock import patch
        notebook = json.loads((Path(__file__).resolve().parents[1] / 'notebooks/analysis_disclosure.ipynb').read_text(encoding='utf-8'))
        self.config['database'] = str(self.root / 'data/processed/dart.sqlite')
        self.config['output_dir'] = str(self.root / 'data/processed/output')
        self.config['team_sql'] = str(self.root / 'sql/queries_disclosure.sql')
        self.write_config()
        namespace = {}
        with patch.dict(os.environ, {'DISCLOSURE_CONFIG': str(self.root / 'data/processed/disclosure_config.json')}), contextlib.redirect_stdout(io.StringIO()):
            for cell in notebook['cells']:
                if cell['cell_type'] == 'code':
                    exec(compile(''.join(cell['source']), '<notebook>', 'exec'), namespace)
        self.assertEqual(namespace['report']['dataset_kind'], 'synthetic_test')
        self.assertEqual(namespace['report']['reference_sql']['matched'], 12)


if __name__ == '__main__':
    unittest.main()
