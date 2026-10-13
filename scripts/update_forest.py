#!/usr/bin/env python3
"""Download auditable National Forest Inventory rolling five-year forest protection statistics.

SSB StatBank 14591 is not an annual time series. Each data point represents an
overlapping five-year survey period. Never splice this directly into an annual
protection history or compare it directly with broader NIBIO forest definitions.
"""
from __future__ import annotations

import csv
import io
import itertools
import json
import math
from pathlib import Path
import re
import urllib.parse
import urllib.request

BASE = "https://data.ssb.no/api/pxwebapi/v2/tables/14591"
SOURCE = "https://www.ssb.no/statbank/table/14591/"
ROOT = Path(__file__).resolve().parents[1]
NUMERATOR = "VernProdSkogAr"
DENOMINATOR = "ProdSkogArTotal"

def fetch_json(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Naturstatus-Norge/0.3 (open-source accountability dashboard)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=40) as response:
        return json.load(response)

def ordered_codes(dimension):
    indices = dimension["category"]["index"]
    return [key for key, _ in sorted(indices.items(), key=lambda item: item[1])]

def unpack(data):
    ids = data["id"]
    if len(ids) != 3 or set(ids) != {"Region", "ContentsCode", "Tid"}:
        raise ValueError("Unexpected SSB forest dataset dimensions")
    codes = [ordered_codes(data["dimension"][id]) for id in ids]
    sizes = data["size"]
    if [len(c) for c in codes] != sizes or len(data["value"]) != math.prod(sizes):
        raise ValueError("SSB response dimension inconsistency")
    out = {}
    for keys, value in zip(itertools.product(*codes), data["value"]):
        mapping = dict(zip(ids, keys))
        key = (mapping["Region"], mapping["ContentsCode"], mapping["Tid"])
        if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Missing or invalid observation: {key}")
        out[key] = value
    return out

def build(data):
    lookup = unpack(data)
    periods = sorted({period for _region, _measure, period in lookup})
    if len(periods) < 3:
        raise ValueError("Too few survey periods to provide a trend")
    if periods[-1] < "2021-2025":
        raise ValueError("Latest SSB NFI data missing")
    results = []
    for period in periods:
        m = re.fullmatch(r"(\d{4})-(\d{4})", period)
        if not m or int(m.group(2)) - int(m.group(1)) != 4:
            raise ValueError(f"Invalid rolling five-year period: {period}")
        end_year = int(m.group(2))
        protected = lookup[("0", NUMERATOR, period)]
        total = lookup[("0", DENOMINATOR, period)]
        if protected < 0 or total <= 0 or protected > total:
            raise ValueError("Invalid protection area or denominator")
        results.append({
            "period": period,
            "end_year": end_year,
            "protected_productive_forest_km2": protected,
            "total_productive_forest_km2": total,
            "share_percent": round(100 * protected / total, 3),
        })
    results.sort(key=lambda item: item["end_year"])
    if len({r["end_year"] for r in results}) != len(results):
        raise ValueError("Overlapping observations have duplicated end years")
    benchmark = next((r for r in results if r["period"] == "2021-2025"), None)
    if not benchmark or abs(benchmark["protected_productive_forest_km2"]-3712) > 400:
        raise ValueError("2021–2025 protected productive forest deviates unexpectedly")
    if abs(benchmark["total_productive_forest_km2"]-86044) > 5000:
        raise ValueError("2021–2025 productive forest total deviates unexpectedly")
    return {
        "schema_version": 1,
        "id": "ssb_nfi_protected_productive_forest",
        "scope": "mainland_norway",
        "metric": "protected_productive_forest_share",
        "table": "14591",
        "source": SOURCE,
        "license": "CC BY 4.0",
        "series_type": "overlapping_five_year_survey_periods",
        "denominator": "Produktivt skogareal i alt, fra samme femårige takseringsperiode",
        "numerator": "Vernet produktivt skogareal, fra samme femårige takseringsperiode",
        "warning": "Observasjonene er overlappende femårige takseringsperioder, ikke uavhengige årsobservasjoner. Arealandelen bygger på SSBs produktiv-skog-definisjon, og er ikke direkte sammenlignbar med NIBIOs bredere skogvernstatistikk.",
        "points": results
    }

def text_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True

def main():
    meta = fetch_json(BASE+"/metadata?lang=no")
    if set(meta["id"]) != {"Region", "ContentsCode", "Tid"}:
        raise ValueError("SSB 14591 metadata changed")
    categories = {k: set(ordered_codes(meta["dimension"][k])) for k in meta["id"]}
    if not {"0"}.issubset(categories["Region"]) or not {NUMERATOR,DENOMINATOR}.issubset(categories["ContentsCode"]):
        raise ValueError("SSB 14591 required dimension codes unavailable")
    periods = sorted(categories["Tid"])
    params = {"lang": "no", "valuecodes[Region]": "0",
              "valuecodes[ContentsCode]": f"{DENOMINATOR},{NUMERATOR}",
              "valuecodes[Tid]": ",".join(periods)}
    data = fetch_json(BASE+"/data?"+urllib.parse.urlencode(params))
    result = build(data)
    text_if_changed(ROOT/"data"/"forest_history.json", json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["period", "end_year", "protected_productive_forest_km2",
                     "total_productive_forest_km2", "share_percent", "source"])
    for p in result["points"]:
        writer.writerow([p["period"], p["end_year"],
                         p["protected_productive_forest_km2"],
                         p["total_productive_forest_km2"], p["share_percent"], SOURCE])
    text_if_changed(ROOT/"data"/"forest_history.csv", output.getvalue())
    print("Validated SSB forest observations:",[(p["period"],p["protected_productive_forest_km2"],p["share_percent"]) for p in result["points"]])

if __name__ == "__main__":
    main()
