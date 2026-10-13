import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
class TargetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/targets.json').read_text(encoding='utf-8'))

    def test_scope_and_goal(self):
        d=self.data
        self.assertEqual(d['target_year'],2030)
        self.assertEqual(d['target_percent'],30)
        self.assertIn('Svalbard',d['scope'])
        self.assertIn('Jan Mayen',d['scope'])
        self.assertEqual(d['formal_protection']['percent'],25.8)
        self.assertAlmostEqual(d['target_percent']-d['formal_protection']['percent'],4.2)

    def test_uncertainty_never_treated_as_zero(self):
        d=self.data
        self.assertIsNone(d['qualified_oecm']['percent'])
        self.assertEqual(d['qualified_oecm']['status'],'not_quantified')
        self.assertEqual(d['evidence_status'],'incomplete')
        self.assertNotIn('on_track',d)

    def test_sources_and_method(self):
        d=self.data
        self.assertTrue(d['target_source'].startswith('https://www.regjeringen.no/'))
        self.assertTrue(d['formal_protection']['source'].startswith('https://www.regjeringen.no/'))
        self.assertIn('ikke en prognose',d['methodology'].lower())
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('goal-status',html)
        self.assertIn('goal.js',html)
        self.assertIn('OECM',html)
        self.assertIn('2030',html)

if __name__=='__main__':
    unittest.main()
