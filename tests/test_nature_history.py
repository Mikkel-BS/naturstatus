import csv
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import update_nature_index as ni

class NatureIndexHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/nature_index_history.json').read_text(encoding='utf-8'))

    def test_history_is_real_source_and_not_protection(self):
        d=self.data
        self.assertEqual(d['metric'],'nature_index_ecological_condition')
        self.assertEqual(d['observed_years'],[2000,2010,2014,2019,2024])
        self.assertEqual(len(d['ecosystems']),5)
        self.assertEqual(len(d['areas']),6)
        self.assertEqual(d['source_doi'],'https://doi.org/10.21345/gfbt-pr39')
        self.assertIn('ikke verneandel',d['methodology'])

    def test_five_ecosystems_all_years_and_uncertainty(self):
        d=self.data
        self.assertEqual(set(d['ecosystems']),set(ni.ECOSYSTEMS))
        for ecosystem in d['ecosystems'].values():
            self.assertEqual(set(ecosystem['areas']),set(ni.AREAS))
            for area,series in ecosystem['areas'].items():
                self.assertEqual([p['year'] for p in series],list(ni.YEARS))
                for p in series:
                    self.assertTrue(0<=p['lower95']<=p['median']<=p['upper95']<=1,
                                    (ecosystem['label'],area,p))
        self.assertEqual(sum(len(v) for ecos in d['ecosystems'].values()
                             for v in ecos['areas'].values()),150)

    def test_published_benchmarks_and_interpretation(self):
        d=self.data['ecosystems']
        self.assertEqual(d['forest']['areas']['Hele Norge'][0]['median'],0.388)
        self.assertEqual(d['forest']['areas']['Hele Norge'][-1]['median'],0.447)
        self.assertEqual(d['wetlands']['areas']['Hele Norge'][0]['median'],0.715)
        self.assertEqual(d['wetlands']['areas']['Hele Norge'][-1]['median'],0.644)
        self.assertEqual(d['open_lowland']['areas']['Hele Norge'][-1]['median'],0.445)
        self.assertEqual(d['freshwater']['areas']['Hele Norge'][-1]['median'],0.789)
        self.assertEqual(d['mountains']['areas']['Hele Norge'][-1]['median'],0.569)

    def test_import_schema_validation_and_csv(self):
        d=self.data
        fixture=[{
            'title':area,
            'chartSeries':[{'year':p['year'],'median':p['median'],
                            'nedreGrense':p['lower95'],'ovreGrense':p['upper95']}
                           for p in d['ecosystems']['forest']['areas'][area]]
        } for area in ni.AREAS]
        self.assertEqual(ni.validate_series(fixture,'forest'),
                         d['ecosystems']['forest']['areas'])
        fixture[0]['chartSeries'][0]['nedreGrense']=0.999
        with self.assertRaises(ValueError):
            ni.validate_series(fixture,'forest')
        self.assertEqual((ROOT/'data/nature_index_history.csv').read_text(encoding='utf-8'),
                         ni.csv_text(d))
        with (ROOT/'data/nature_index_history.csv').open(encoding='utf-8',newline='') as f:
            self.assertEqual(len(list(csv.DictReader(f))),150)

    def test_website_includes_historical_assets(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        deployment=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        self.assertIn('ecosystem-history',html)
        self.assertIn('nature_history.js',html)
        self.assertIn('data/nature_index_history.json',deployment)
        self.assertIn('data/nature_index_history.csv',deployment)
        self.assertIn('historiske verneandeler',html.lower())

if __name__=='__main__':
    unittest.main()
