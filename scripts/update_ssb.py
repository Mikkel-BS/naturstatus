#!/usr/bin/env python3
"""Reproducible import of SSB StatBank 08936 via PxWeb API v2.

Total protected land is comparable from 2018 (the introduction of "Alle verneformer").
Earlier protection categories are shown as separate series, never summed.
"""
from __future__ import annotations
import csv
from datetime import date
import itertools
import json
from pathlib import Path
import urllib.parse
import urllib.request

TABLE = "08936"
BASE = "https://data.ssb.no/api/pxwebapi/v2/tables/08936"
ROOT = Path(__file__).resolve().parents[1]
REGIONS = ("0", "21", "22")
PURPOSES = {"total":"0", "national_park":"NP", "nature_reserve":"NR", "landscape_protection":"LV"}
SOURCE = "https://www.ssb.no/statbank/table/08936/"
DENOMINATOR_NOTE = "Areal i km², ikke andel. Territorielle summer er kontrollert mot SSB."

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Naturstatus-Norge/0.2 (open-source statistics dashboard)",
                 "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=45) as result:
        return json.load(result)

def api_url():
    params = {
        "lang": "no",
        "valuecodes[Region]": ",".join(REGIONS),
        "valuecodes[VerneOmrader]": ",".join(PURPOSES.values()),
        "valuecodes[ContentsCode]": "VernetAreal",
        "valuecodes[Tid]": "from(1975)",
    }
    return BASE + "/data?" + urllib.parse.urlencode(params)

def dimension_codes(dimension):
    index = dimension["category"]["index"]
    return [code for code, _ in sorted(index.items(), key=lambda p: p[1])]

def unpack(dataset):
    """Decode dimension-coded JSON-stat2; never assume server row ordering."""
    ids = dataset["id"]
    sizes = dataset["size"]
    if not set(("Region","VerneOmrader","ContentsCode","Tid")).issubset(ids):
        raise ValueError("SSB schema changed")
    codes = [dimension_codes(dataset["dimension"][key]) for key in ids]
    if [len(c) for c in codes] != sizes:
        raise ValueError("SSB dimension sizes inconsistent")
    values = dataset["value"]
    if len(values) != __import__("math").prod(sizes):
        raise ValueError("SSB value count inconsistent")
    output = {}
    for combinations, raw in zip(itertools.product(*codes), values):
        attrs = dict(zip(ids, combinations))
        if attrs["ContentsCode"] != "VernetAreal":
            continue
        if raw is not None and not isinstance(raw, (int,float)):
            raise ValueError("Unexpected SSB numeric value")
        output[(attrs["Region"],attrs["VerneOmrader"],int(attrs["Tid"]))] = raw
    return output

def build(dataset):
    lookup = unpack(dataset)
    years = sorted({y for (_r, _p, y) in lookup})
    if not years or years[-1] < 2025:
        raise ValueError("SSB data is stale")
    series = {}
    for label, purpose in PURPOSES.items():
        points = []
        for year in years:
            if label == "total" and year < 2018:
                continue
            national = lookup.get(("0", purpose, year))
            if national is None:
                if label == "total" or year >= 2018:
                    raise ValueError(f"Missing nationwide value: {purpose}/{year}")
                continue
            # SSB included the Arctic territories only from later years.
            # Missing older regional cells are treated as not included in nationwide sum.
            arctic = [lookup.get((r, purpose, year)) or 0 for r in ("21","22")]
            mainland = round(float(national) - sum(arctic),2)
            if mainland < 0:
                raise ValueError(f"Negative mainland area: {purpose}/{year}")
            points.append({"year": year, "km2": mainland})
        if not points:
            raise ValueError(f"Missing series {label}")
        series[label] = points
    last = series["total"][-1]
    if last["year"] == 2025 and abs(last["km2"] - 57483.38) > 1:
        raise ValueError(f"2025 benchmark mismatch: {last}")
    if series["total"][0]["year"] != 2018:
        raise ValueError("All-protections total must begin in 2018")
    return {
        "scope": "mainland_land",
        "metric": "protected_land_km2",
        "source": SOURCE,
        "table": TABLE,
        "method": "National value minus Svalbard minus Jan Mayen, by year and protection category.",
        "note": DENOMINATOR_NOTE,
        "series": series,
    }

def write_if_changed(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content,encoding="utf-8")
    return True

def main():
    meta = fetch_json(BASE + "/metadata?lang=no")
    for name, expected in (("Region",set(REGIONS)),("VerneOmrader",set(PURPOSES.values()))):
        codes = set(dimension_codes(meta["dimension"][name]))
        if not expected.issubset(codes):
            raise ValueError(f"Expected SSB codes missing: {name}")
    result = build(fetch_json(api_url()))
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    write_if_changed(ROOT/"data"/"historical.json",content)
    rows = [["series","year","protected_land_km2","scope","source"]]
    for key,points in result["series"].items():
        for p in points:
            rows.append([key,p["year"],p["km2"],result["scope"],SOURCE])
    import io
    handle=io.StringIO(newline="")
    writer=csv.writer(handle,lineterminator="\n")
    writer.writerows(rows)
    write_if_changed(ROOT/"data"/"historical.csv",handle.getvalue())
    print("Validated SSB 08936:", ", ".join(f"{name} {len(items)} years" for name,items in result["series"].items()))
    print("Latest mainland protected land km²:",result["series"]["total"][-1])

if __name__ == "__main__":
    main()
