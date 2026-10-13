import csv
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import update_ssb

class SSBTests(unittest.TestCase):
    def test_jsonstat_decoder_and_mainland_subtraction(self):
        codes={"Region":["0","21","22"],"VerneOmrader":["0","NP","NR","LV"],
               "ContentsCode":["VernetAreal"],"Tid":["2018","2025"]}
        dim={name:{"category":{"index":{c:i for i,c in enumerate(items)}}} for name,items in codes.items()}
        val=[]
        for region in codes["Region"]:
            for purpose in codes["VerneOmrader"]:
                for _ in codes["ContentsCode"]:
                    for year in codes["Tid"]:
                        val.append({"0":{"2018":98000,"2025":99416.44},
                                    "21":{"2018":41000,"2025":41558.12},
                                    "22":{"2018":375,"2025":374.94}}[region][year] if purpose=="0" else 0)
        result=update_ssb.build({"id":list(codes),"size":[3,4,1,2],"dimension":dim,"value":val})
        self.assertEqual(result["series"]["total"][-1],{"year":2025,"km2":57483.38})
        self.assertEqual(result["series"]["total"][0]["year"],2018)
        self.assertEqual(result["series"]["national_park"][0]["km2"],0)

    def test_benchmarks(self):
        with (ROOT/"data"/"overview.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        figures={(int(r["year"]),r["geography"]):float(r["percent"]) for r in rows}
        self.assertEqual(figures[(2025,"Mainland Norway")],17.8)
        self.assertEqual(figures[(2026,"Norway including Svalbard and Jan Mayen")],25.8)

    def test_dataset_and_scope(self):
        d=json.loads((ROOT/"data"/"historical.json").read_text())
        self.assertEqual(d["scope"],"mainland_land")
        if "series" in d:
            self.assertEqual(d["metric"],"protected_land_km2")
            self.assertEqual(d["series"]["total"][0]["year"],2018)
        else:
            self.assertFalse(d["complete"])
        html=(ROOT/"index.html").read_text()
        self.assertIn("OECM",html)
        self.assertIn("fastlandet",html.lower())
        self.assertIn("2018",html)

if __name__=="__main__":unittest.main()
