"""Reject research-data mistakes before sample rendering."""
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from render_standard_samples import CASES, SAMPLES, validate


class SampleGuards(unittest.TestCase):
    def fixture(self, index):
        return pd.read_csv(SAMPLES / CASES[index] / 'input.csv')

    def test_annual_gap_is_not_silently_connected(self):
        with self.assertRaises(ValueError):
            validate(CASES[0], self.fixture(0).drop(index=3))

    def test_missing_ownership_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            validate(CASES[1], self.fixture(1).drop(index=0))

    def test_inverted_interval_is_rejected(self):
        data = self.fixture(2)
        data.loc[0, 'low'] = .9
        with self.assertRaises(ValueError):
            validate(CASES[2], data)

    def test_duplicate_estimate_key_is_rejected(self):
        data = self.fixture(2)
        with self.assertRaises(ValueError):
            validate(CASES[2], pd.concat([data, data.iloc[[0]]]))

    def test_reference_effect_is_not_silently_discarded(self):
        data = self.fixture(3)
        data.loc[data.event_time == -1, ['estimate', 'high']] = .02
        with self.assertRaises(ValueError):
            validate(CASES[3], data)

    def test_nonfinite_value_is_rejected(self):
        data = self.fixture(0)
        data.loc[0, 'export_growth'] = float('inf')
        with self.assertRaises(ValueError):
            validate(CASES[0], data)


if __name__ == '__main__':
    unittest.main()
