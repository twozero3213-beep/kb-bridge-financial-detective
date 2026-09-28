import sqlite3
import unittest

import pandas as pd

from src.validation_leejeongsu import compare_results, quality, validate_changes


def passed(checks):
    return all(c['status'] == 'PASS' for c in checks)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.frame = pd.DataFrame({'corp_code': ['001', '002'], 'count': [2, 1]})

    def test_real_sql_engine_against_pandas_on_synthetic_rows(self):
        raw = pd.DataFrame({'corp_code': ['001', '001', '002']})
        with sqlite3.connect(':memory:') as connection:
            raw.to_sql('disclosures', connection, index=False)
            sql = pd.read_sql_query('SELECT corp_code, COUNT(*) AS count FROM disclosures GROUP BY corp_code', connection)
        grouped = raw.groupby('corp_code').size().reset_index(name='count')
        self.assertTrue(passed(compare_results(sql, grouped.iloc[::-1], ['corp_code'], ['count'])))

    def test_wrong_value(self):
        other = self.frame.copy()
        other.loc[0, 'count'] = 3
        self.assertFalse(passed(compare_results(self.frame, other, ['corp_code'], ['count'])))

    def test_missing_group(self):
        self.assertFalse(passed(compare_results(self.frame, self.frame.iloc[:1], ['corp_code'], ['count'])))

    def test_duplicate(self):
        self.assertFalse(passed(quality(pd.concat([self.frame, self.frame]), ['corp_code'])))

    def test_missing_and_empty(self):
        for value in [None, '', ' ']:
            self.assertFalse(passed(quality(pd.DataFrame({'id': [value]}), ['id'])))
        self.assertFalse(passed(quality(self.frame.iloc[:0], ['corp_code'])))

    def test_bad_numeric_and_missing_column(self):
        other = self.frame.copy().astype(str)
        other.loc[0, 'count'] = 'inf'
        self.assertFalse(passed(compare_results(self.frame, other, ['corp_code'], ['count'])))
        self.assertFalse(passed(compare_results(self.frame, self.frame.drop(columns='count'), ['corp_code'], ['count'])))

    def changes(self):
        return pd.DataFrame({'id': ['a', 'b'], 'previous': [100, -100], 'current': [150, -50],
                             'change_pct': [50, 50], 'candidate': ['true', 'true']})

    def test_rate_and_negative_baseline(self):
        self.assertTrue(passed(validate_changes(self.changes(), ['id'])))

    def test_wrong_rate_and_candidate(self):
        frame = self.changes()
        frame.loc[0, 'change_pct'] = 40
        frame.loc[1, 'candidate'] = 'false'
        checks = validate_changes(frame, ['id'])
        self.assertEqual([c['status'] for c in checks if c['name'] in ['changes.rate', 'changes.candidate']], ['CHECK', 'CHECK'])

    def test_zero_baseline(self):
        frame = self.changes()
        frame.loc[0, 'previous'] = 0
        frame['change_pct'] = frame.change_pct.astype(object)
        frame.loc[0, 'change_pct'] = ''
        frame.loc[0, 'candidate'] = ''
        self.assertFalse(passed(validate_changes(frame, ['id'])))

    def test_sensitivity(self):
        frame = self.changes()
        frame['candidate'] = 'false'
        self.assertTrue(passed(validate_changes(frame, ['id'], threshold_pct=51)))
        self.assertTrue(passed(validate_changes(frame, ['id'], min_abs_change=51)))


if __name__ == '__main__':
    unittest.main()
