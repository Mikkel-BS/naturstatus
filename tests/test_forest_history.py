"""Regression tests for forest inventory source, comparability and published assets."""
import csv
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import update_forest

class ForestHistoryTests(unittest.TestCase):
    def sample_dataset(self):
        periods=["2019-2023","2020-2024","2021-2025"]
        measurements=["VernProdSkogAr","ProdSkogArTotal"]
        dimensions={
            "Tid":{"category":{"index":{p:i for i,p in enumerate(periods)}}},
            "ContentsCode":{"category":{"index":{c:i for i,c in enumerate(measurements)}}},
            "Region":{"category":{"index":{"0":0}}},
        }
        # Deliberately permuted dimension order to verify JSON-stat decoding.
        values=[3481,3614,3712,85898,86024,86044]
        return {"id":["ContentsCode","Region","Tid"],
                "size":[2,1,3],"dimension":dimensions,"value":values}

    def test_decoder_handles_dimension_order(self):
        result=update_forest.build(self.sample_dataset())
        self.assertEqual(result["series_type"],"overlapping_five_year_survey_periods")
        self.assertEqual(len(result["points"]),3)
        self.assertEqual(result["points"][0]["period"],"2019-2023")
        self.assertEqual(result["points"][-1]["protected_productive_forest_km2"],3712)
        self.assertEqual(result["points"][-1]["total_productive_forest_km2"],86044)
        self.assertAlmostEqual(result["points"][-1]["share_percent"],4.314,places=2)

    def test_invalid_numerator_fails_closed(self):
        data=self.sample_dataset()
        data["value"][0]=90000
        with self.assertRaises(ValueError):
            update_forest.build(data)

    def test_missing_observation_fails_closed(self):
        data=self.sample_dataset()
        data["value"][0]=None
        with self.assertRaises(ValueError):
            update_forest.build(data)

    def test_periods_are_not_claimed_as_calendar_years(self):
        data=json.loads((ROOT/"data/forest_history.json").read_text(encoding="utf-8"))
        self.assertEqual(data["metric"],"protected_productive_forest_share")
        self.assertEqual(data["scope"],"mainland_norway")
        self.assertEqual(data["table"],"14591")
        self.assertEqual(data["series_type"],"overlapping_five_year_survey_periods")
        self.assertIn("ikke uavhengige",data["warning"])
        periods=[p["period"] for p in data["points"]]
        self.assertEqual(periods,["2019-2023","2020-2024","2021-2025"])
        for p in data["points"]:
            self.assertAlmostEqual(p["share_percent"],100*p["protected_productive_forest_km2"]/p["total_productive_forest_km2"],places=2)
        self.assertEqual(data["points"][-1]["protected_productive_forest_km2"],3712)

    def test_csv_matches_json(self):
        data=json.loads((ROOT/"data/forest_history.json").read_text(encoding="utf-8"))
        with (ROOT/"data/forest_history.csv").open(newline="",encoding="utf-8") as file:
            rows=list(csv.DictReader(file))
        self.assertEqual(len(rows),len(data["points"]))
        for row,point in zip(rows,data["points"]):
            self.assertEqual(row["period"],point["period"])
            self.assertAlmostEqual(float(row["share_percent"]),point["share_percent"])

    def test_site_and_distribution_include_evidence(self):
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        workflow=(ROOT/".github/workflows/pages.yml").read_text(encoding="utf-8")
        script=(ROOT/"forest-history.js").read_text(encoding="utf-8")
        self.assertIn('id="ekosystemhistorikk"',html)
        self.assertIn("overlappende",html)
        self.assertIn("evidence-table",html)
        self.assertIn("forest-history.js",workflow)
        self.assertIn("forest_history.json",workflow)
        self.assertIn("series_type",script)
        self.assertIn("share_percent",script)
        self.assertIn("forest_history.csv",script)

if __name__=="__main__":
    unittest.main()
