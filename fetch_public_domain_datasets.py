#!/usr/bin/env python3
"""
Fetch Public-Domain Healthcare Organization Datasets

Sources implemented:
- Wikidata (CC0): global hospitals via SPARQL API

Outputs:
- external_organizations/wikidata_hospitals.json
  Structure: { "organizations": [ { name, country, city?, state?, lat?, lon?, certifications: [] } ] }

Notes:
- Designed to be ingested by global_database_integrator.py.
- Safe to run multiple times; will overwrite the output file.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


def _wikidata_query(limit: int = 5000, offset: int = 0) -> str:
    # Hospitals: instance of hospital (Q16917)
    # Fetch label, country label, coordinates, website if available
    return f"""
    SELECT ?item ?itemLabel ?countryLabel ?coord ?website WHERE {{
      ?item wdt:P31 wd:Q16917 .
      OPTIONAL {{ ?item wdt:P17 ?country }}
      OPTIONAL {{ ?item wdt:P625 ?coord }}
      OPTIONAL {{ ?item wdt:P856 ?website }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    OFFSET {offset}
    """


def fetch_wikidata_hospitals(max_records: int = 5000) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    limit = min(5000, max_records)
    offset = 0

    query = _wikidata_query(limit=limit, offset=offset)
    params = urllib.parse.urlencode({
        "query": query,
        "format": "json",
    }).encode("utf-8")

    req = urllib.request.Request(WIKIDATA_SPARQL_ENDPOINT, data=params)
    req.add_header("Accept", "application/sparql-results+json")
    req.add_header("User-Agent", "QuXAT-Scoring-Fetcher/1.0")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for b in data.get("results", {}).get("bindings", []):
                name = b.get("itemLabel", {}).get("value")
                country = b.get("countryLabel", {}).get("value")
                coord = b.get("coord", {}).get("value")
                website = b.get("website", {}).get("value")

                lat = lon = None
                if coord and coord.startswith("Point("):
                    try:
                        # WKT Point(lon lat)
                        inner = coord[len("Point("):-1]
                        parts = inner.split(" ")
                        lon = float(parts[0])
                        lat = float(parts[1])
                    except Exception:
                        lat = lon = None

                records.append({
                    "name": name,
                    "country": country,
                    "lat": lat,
                    "lon": lon,
                    "website": website,
                    "hospital_type": None,
                    "certifications": [],
                })
    except Exception as e:
        print(f"❌ Error fetching Wikidata hospitals: {e}")

    print(f"✅ Wikidata hospitals fetched: {len(records)}")
    return records


def save_external_dataset(filename: str, records: List[Dict[str, Any]], source_name: str) -> None:
    os.makedirs("external_organizations", exist_ok=True)
    payload = {
        "metadata": {
            "source": source_name,
            "fetched_at": datetime.now().isoformat(),
            "record_count": len(records),
            "license": "CC0 (Wikidata)",
        },
        "organizations": records,
    }
    path = os.path.join("external_organizations", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(records)} records to {path}")


def main():
    records = fetch_wikidata_hospitals(max_records=3000)
    save_external_dataset("wikidata_hospitals.json", records, "Wikidata Hospitals SPARQL")
    print("Public-domain dataset fetching completed.")


if __name__ == "__main__":
    main()