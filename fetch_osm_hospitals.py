#!/usr/bin/env python3
"""
Fetch Hospitals from OpenStreetMap via Overpass API

Countries covered (sample, expandable): US, UK, India, Japan, Germany, France,
Australia, Canada, Saudi Arabia, UAE, South Africa.

Notes:
- Overpass data is ODbL licensed; we store provenance in metadata.
- We limit per-country results to avoid rate limits and excessive payloads.
- Output format aligns with global_database_integrator.py expectations.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

COUNTRIES = [
    "United States", "United Kingdom", "India", "Japan", "Germany",
    "France", "Australia", "Canada", "Saudi Arabia", "United Arab Emirates",
    "South Africa",
]


def build_query(country_name: str, limit: int = 500) -> str:
    # Query area by country name, fetch nodes/ways/relations with amenity=hospital
    # Limit output to given number to be polite to Overpass
    return f"""
    [out:json][timeout:60];
    area["name"="{country_name}"];
    (
      node["amenity"="hospital"](area);
      way["amenity"="hospital"](area);
      rel["amenity"="hospital"](area);
    );
    out center {limit};
    """


def fetch_country(country_name: str, limit: int = 500) -> List[Dict[str, Any]]:
    q = build_query(country_name, limit)
    data = urllib.parse.urlencode({"data": q}).encode("utf-8")
    req = urllib.request.Request(OVERPASS_URL, data=data)
    req.add_header("User-Agent", "QuXAT-Scoring-OSM-Fetcher/1.0")
    req.add_header("Accept", "application/json")
    records: List[Dict[str, Any]] = []
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            for el in payload.get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                city = tags.get("addr:city") or tags.get("is_in:city")
                state = tags.get("addr:state") or tags.get("is_in:state")
                country = tags.get("addr:country") or country_name
                lat = el.get("lat") or (el.get("center", {}).get("lat"))
                lon = el.get("lon") or (el.get("center", {}).get("lon"))

                records.append({
                    "name": name,
                    "city": city,
                    "state": state,
                    "country": country,
                    "lat": lat,
                    "lon": lon,
                    "hospital_type": None,
                    "certifications": [],
                })
    except Exception as e:
        print(f"❌ OSM fetch failed for {country_name}: {e}")
    print(f"✅ OSM hospitals fetched for {country_name}: {len(records)}")
    return records


def save_external_dataset(filename: str, records: List[Dict[str, Any]], source_name: str) -> None:
    os.makedirs("external_organizations", exist_ok=True)
    payload = {
        "metadata": {
            "source": source_name,
            "fetched_at": datetime.now().isoformat(),
            "record_count": len(records),
            "license": "ODbL (OpenStreetMap)",
        },
        "organizations": records,
    }
    path = os.path.join("external_organizations", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(records)} records to {path}")


def main():
    all_records: List[Dict[str, Any]] = []
    for country in COUNTRIES:
        recs = fetch_country(country, limit=400)
        all_records.extend(recs)
    save_external_dataset("osm_hospitals_sample.json", all_records, "OpenStreetMap Overpass")
    print("OSM dataset fetching completed.")


if __name__ == "__main__":
    main()