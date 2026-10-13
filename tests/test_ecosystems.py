import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
class EcosystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/ecosystems.json').read_text(encoding='utf-8'))

    def test_ecosystem_values_and_scope(self):
        d=self.data
        self.assertEqual(d['schema_version'],1)
        self.assertEqual(d['nature_index']['reference_year'],2025)
        self.assertEqual(d['nature_index']['range'],[0,1])
        self.assertEqual({x['id'] for x in d['ecosystems']},
                         {'forest','wetlands','mountains','open_lowland','freshwater'})
        self.assertTrue(all(0<=x['nature_index']<=1 for x in d['ecosystems']))

    def test_government_2024_coverages(self):
        d=self.data
        self.assertEqual(d['government_2024']['publication_year'],2024)
        self.assertIn('regjeringen.no',d['government_2024']['url'])
        expected={'forest':7.6,'wetlands':16,'mountains':34,'open_lowland':12,'freshwater':14}
        for entry in d['ecosystems']:
            self.assertEqual(entry['protected_percent'],expected[entry['id']])
            if entry['id']=='forest':
                self.assertEqual(entry['protected_status'],'available')
            else:
                self.assertEqual(entry['protected_status'],'published_approximate')
                self.assertEqual(entry['protected_report_year'],2024)
                self.assertEqual(entry['protected_source'],d['government_2024']['url'])
        self.assertIn('2024',d['methods']['coverage'])

    def test_forest_definitions_separate(self):
        forest=self.data['forest_source']
        self.assertEqual(forest['reference_date'],'2025-01-01')
        shares=forest['protected_share']
        self.assertEqual(shares['all_forest_all_three_forms'],7.6)
        self.assertEqual(shares['all_forest_national_park_nature_reserve'],5.6)
        self.assertEqual(shares['productive_forest_all_three_forms'],5.9)
        self.assertEqual(shares['productive_forest_national_park_nature_reserve'],4.4)
        self.assertTrue(forest['url'].startswith('https://www.skogbruk.nibio.no/'))

    def test_index_not_protection_and_page_uses_assets(self):
        d=self.data
        self.assertIn('kan ikke',d['methods']['comparability'])
        self.assertIn('Svalbard',d['methods']['geography'])
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        deploy=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        self.assertIn('ecosystem-overview',html)
        self.assertIn('ecosystems.js',html)
        self.assertIn('data/ecosystems.json',deploy)

if __name__=='__main__':unittest.main()
