"""Cross-ecosystem Nature Index comparison uses observed endpoints, not interpolated protection trends."""
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class NatureComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/nature_index_history.json').read_text(encoding='utf-8'))

    def test_each_region_has_comparable_endpoint_estimates(self):
        d=self.data
        self.assertEqual(d['observed_years'],[2000,2010,2014,2019,2024])
        self.assertEqual(len(d['areas']),6)
        self.assertEqual(len(d['ecosystems']),5)
        for area in d['areas']:
            for item in d['ecosystems'].values():
                observations=item['areas'][area]
                self.assertEqual([p['year'] for p in observations],d['observed_years'])
                self.assertTrue(all(0<=p['lower95']<=p['median']<=p['upper95']<=1
                                    for p in observations))
                self.assertLessEqual(abs(observations[-1]['median']-observations[0]['median']),1)

    def test_national_comparison_benchmarks(self):
        eco=self.data['ecosystems']
        values={id:(e['areas']['Hele Norge'][0]['median'],
                    e['areas']['Hele Norge'][-1]['median'])
                for id,e in eco.items()}
        self.assertEqual(values['forest'],(0.388,0.447))
        self.assertEqual(values['wetlands'],(0.715,0.644))
        self.assertEqual(values['open_lowland'],(0.519,0.445))
        self.assertAlmostEqual(values['forest'][1]-values['forest'][0],0.059)
        self.assertAlmostEqual(values['wetlands'][1]-values['wetlands'][0],-0.071)

    def test_comparison_implemented_and_explicitly_not_protection(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        js=(ROOT/'nature_history.js').read_text(encoding='utf-8')
        self.assertIn('id="comparison-rows"',html)
        self.assertIn('id="comparison-region"',html)
        self.assertIn('id="comparison-method"',html)
        self.assertIn('ikke endring i verneandel',html.lower())
        self.assertIn('signifikans',html.lower())
        self.assertIn('function renderComparison(data)',js)
        self.assertIn('p.median',js)
        self.assertIn('renderComparison(data)',js)
        self.assertIn("areaSelect.value",js)
        self.assertIn("ecosystemSelect.value=row.id",js)
        self.assertNotIn('interpolate',js.lower())

if __name__=='__main__':
    unittest.main()
