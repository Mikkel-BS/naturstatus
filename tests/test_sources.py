import csv
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SourceTests(unittest.TestCase):
    def test_benchmarks(self):
        with (ROOT / 'data' / 'overview.csv').open(newline='') as f:
            rows = list(csv.DictReader(f))
        figures = {(int(r['year']), r['geography']): float(r['percent']) for r in rows}
        self.assertEqual(figures[(2020, 'Mainland Norway')], 17.5)
        self.assertEqual(figures[(2025, 'Mainland Norway')], 17.8)
        self.assertEqual(figures[(2026, 'Norway including Svalbard and Jan Mayen')], 25.8)
        self.assertTrue(all(0 <= float(r['percent']) <= 100 for r in rows))

    def test_historical_series_has_explicit_completeness(self):
        data = json.loads((ROOT / 'data' / 'historical.json').read_text())
        self.assertEqual(data['scope'], 'mainland_land')
        years = [point['year'] for point in data['points']]
        self.assertEqual(years, sorted(set(years)))
        self.assertTrue(all(0 <= p['percent'] <= 100 for p in data['points']))
        if data['complete']:
            self.assertEqual(years, list(range(years[0], years[-1]+1)))
        else:
            self.assertEqual(years, [2020, 2025])

    def test_claims_have_context(self):
        html = (ROOT / 'index.html').read_text()
        self.assertIn('OECM', html)
        self.assertIn('fastlandet', html.lower())
        self.assertIn('ikke full tidsserie', html)

if __name__ == '__main__':
    unittest.main()
