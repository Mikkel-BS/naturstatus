#!/usr/bin/env python3
"""Import official Nature Index 2025 time series, preserving uncertainty and actual years.

The Nature Index measures condition, NOT the share of any ecosystem under protection.
See https://www.naturindeks.no/DownloadData and
https://doi.org/10.21345/gfbt-pr39 (CC BY 4.0).
"""
import argparse
import csv
import io
import json
import math
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.naturindeks.no"
ECOSYSTEMS = {
    "forest": (8, "Skog"),
    "mountains": (2, "Fjell"),
    "wetlands": (7, "Våtmark"),
    "open_lowland": (9, "Åpent lavland"),
    "freshwater": (1, "Ferskvann"),
}
AREAS = ("Hele Norge", "Øst-Norge", "Sør-Norge", "Vest-Norge", "Midt-Norge", "Nord-Norge")
YEARS = (2000, 2010, 2014, 2019, 2024)
SOURCE_DOI = "https://doi.org/10.21345/gfbt-pr39"


def fetch_json(url):
    req = urllib.request.Request(
        url, headers={
            "User-Agent": "Naturstatus Norge / historical biodiversity research (https://github.com/Mikkel-BS/naturstatus)",
            "Accept": "application/json",
        })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def validate_series(raw, ecosystem):
    if not isinstance(raw, list) or len(raw) != len(AREAS):
        raise ValueError(f"Unexpected areas for {ecosystem}")
    by_area = {}
    for area in raw:
        title = area.get("title")
        if title not in AREAS or title in by_area:
            raise ValueError(f"Invalid/duplicate area for {ecosystem}: {title}")
        series = area.get("chartSeries")
        if not isinstance(series, list) or [p.get("year") for p in series] != list(YEARS):
            raise ValueError(f"Noncanonical year series for {ecosystem}/{title}")
        points = []
        for point in series:
            lower, median, upper = (point.get(k) for k in ("nedreGrense", "median", "ovreGrense"))
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (lower, median, upper)):
                raise ValueError(f"Missing/non-numeric Nature Index observation {ecosystem}/{title}")
            if not 0 <= lower <= median <= upper <= 1:
                raise ValueError(f"Invalid confidence range {ecosystem}/{title}")
            points.append({
                "year": point["year"],
                "median": median,
                "lower95": lower,
                "upper95": upper,
            })
        by_area[title] = points
    if set(by_area) != set(AREAS):
        raise ValueError(f"Region coverage differs for {ecosystem}")
    return {name: by_area[name] for name in AREAS}


def build(fetcher=fetch_json):
    result = {
        "schema_version": 1,
        "metric": "nature_index_ecological_condition",
        "published_edition": "Naturindeks for Norge 2025",
        "source_doi": SOURCE_DOI,
        "source_home": "https://www.naturindeks.no/DownloadData",
        "license": "CC BY 4.0",
        "observed_years": list(YEARS),
        "areas": list(AREAS),
        "methodology": "Indeks fra 0 til 1: økologisk tilstand, ikke verneandel. Fem observerte referanseår, ikke årlig interpolasjon. Intervaller er kildens 95 % konfidensgrenser. Resultatene for 2025-utgaven er modellberegninger for siste referanseår 2024.",
        "ecosystems": {},
    }
    reference = json.loads((ROOT / "data" / "ecosystems.json").read_text(encoding="utf-8"))
    expected_latest = {entry["id"]: entry["nature_index"] for entry in reference["ecosystems"]}
    for ecosystem, (source_id, label) in ECOSYSTEMS.items():
        areas = validate_series(fetcher(f"{BASE}/Ecosystem/GetEcosystemChart/{source_id}"), ecosystem)
        last = areas["Hele Norge"][-1]["median"]
        if abs(last - expected_latest[ecosystem]) > 0.011:
            raise ValueError(f"2024 {ecosystem} differs from published 2025 index: {last}")
        result["ecosystems"][ecosystem] = {
            "label": label,
            "source_id": source_id,
            "areas": areas,
        }
    return result


def csv_text(data):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["ecosystem", "area", "reference_year", "nature_index_median",
                     "lower_95", "upper_95", "source"])
    for ecosystem, information in data["ecosystems"].items():
        for area, points in information["areas"].items():
            for p in points:
                writer.writerow([ecosystem, area, p["year"], p["median"],
                                 p["lower95"], p["upper95"], SOURCE_DOI])
    return output.getvalue()


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Verify committed JSON and CSV match the official API")
    args = parser.parse_args()
    data = build()
    outputs = {
        ROOT / "data" / "nature_index_history.json": json.dumps(
            data, ensure_ascii=False, indent=2) + "\n",
        ROOT / "data" / "nature_index_history.csv": csv_text(data),
    }
    if args.check:
        if any(not path.exists() or path.read_text(encoding="utf-8") != text
               for path, text in outputs.items()):
            raise SystemExit("Official Nature Index dataset differs from committed data; review changes")
    else:
        for path, text in outputs.items():
            if write_if_changed(path, text):
                print(f"Updated {path.relative_to(ROOT)}")
    print("Verified 5 ecosystems × 6 areas × 5 reference years, 95% intervals included")


if __name__ == "__main__":
    main()
