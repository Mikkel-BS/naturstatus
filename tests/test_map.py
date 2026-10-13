import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class MapTests(unittest.TestCase):
    def test_current_and_proposed_layers_explicit(self):
        script=(ROOT/'map.js').read_text(encoding='utf-8')
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertIn('naturvern_omrade',script)
        self.assertIn('foreslatt_naturvern_omrade',script)
        self.assertIn('returnGeometry',script)
        self.assertIn('foerstegangVernet',script)
        self.assertIn('textContent',script)
        self.assertIn('nåværende grensene',html)
        self.assertIn('foreslått vern',html.lower())
        self.assertIn('id="conservation-map"',html)
        self.assertIn('map.js',html)

    def test_pages_publishes_map(self):
        deploy=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        self.assertIn('map.js',deploy)
        self.assertIn('historical.csv',deploy)

if __name__ == '__main__':
    unittest.main()
