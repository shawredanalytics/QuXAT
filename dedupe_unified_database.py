#!/usr/bin/env python3
import json
import io
import re
from collections import defaultdict
from pathlib import Path

DB_PATH = Path("unified_healthcare_organizations.json")
JCI_PATH = Path("jci_accredited_organizations.json")

def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = str(s or "")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = " ".join(s.split())
    return s

def is_jci_like(cert) -> bool:
    try:
        name = (cert.get("name", "") if isinstance(cert, dict) else str(cert)).upper()
    except Exception:
        name = str(cert).upper()
    return ("JCI" in name) or ("JOINT COMMISSION" in name)

def load_db(path: Path):
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "organizations" in data:
        return data["organizations"], data
    elif isinstance(data, list):
        return data, data
    else:
        return [data], data

def save_db(path: Path, original):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(original, f, ensure_ascii=False, indent=2)

def load_jci_index(path: Path):
    index = defaultdict(set)  # name -> set of cities
    verified_no_city = set()  # names with verification_required False, city not required
    if not path.exists():
        return index, verified_no_city
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return index, verified_no_city
    if isinstance(data, dict):
        entries = data.get("organizations") or data.get("entries") or []
    elif isinstance(data, list):
        entries = data
    else:
        entries = [data]
    for e in entries:
        if not isinstance(e, dict):
            continue
        name = normalize_text(e.get("name", ""))
        city = normalize_text(e.get("city", ""))
        vr = e.get("verification_required")
        if name:
            if city:
                index[name].add(city)
            if vr is False:
                verified_no_city.add(name)
    return index, verified_no_city

def jci_valid_for(name: str, city: str, jci_index, verified_no_city) -> bool:
    n = normalize_text(name)
    c = normalize_text(city)
    if n in verified_no_city:
        return True
    if n in jci_index:
        # If we have city info in the index, require match
        if jci_index[n]:
            return c in jci_index[n]
        return True
    return False

def dedupe_certifications(certs, org_name, org_city, jci_index, verified_no_city):
    seen = set()
    out = []
    for c in certs or []:
        # Key by normalized name for dedupe
        if isinstance(c, dict):
            key = normalize_text(c.get("name", ""))
        else:
            key = normalize_text(str(c))
        if not key:
            continue
        if key in seen:
            continue
        # JCI entries must be validated against official list
        if is_jci_like(c):
            if not jci_valid_for(org_name, org_city, jci_index, verified_no_city):
                continue
        seen.add(key)
        out.append(c)
    return out

def choose_non_empty(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v
    return ""

def merge_group(entries, jci_index, verified_no_city):
    base_name = choose_non_empty(*(e.get("name", "") for e in entries)) or (entries[0].get("name", "") if entries else "")
    base_city = choose_non_empty(*(e.get("city", "") for e in entries))
    base_state = choose_non_empty(*(e.get("state", "") for e in entries))
    base_country = choose_non_empty(*(e.get("country", "") for e in entries))
    base_address = choose_non_empty(*(e.get("address", "") for e in entries))
    base_phone = choose_non_empty(*(e.get("phone", "") for e in entries))
    base_website = choose_non_empty(*(e.get("website", "") for e in entries))

    # Merge certifications
    all_certs = []
    for e in entries:
        certs = e.get("certifications", [])
        if isinstance(certs, list):
            all_certs.extend(certs)
    merged_certs = dedupe_certifications(all_certs, base_name, base_city, jci_index, verified_no_city)

    # Merge quality indicators
    qi = {}
    for e in entries:
        q = e.get("quality_indicators", {})
        if isinstance(q, dict):
            for k, v in q.items():
                # Prefer truthy values
                if k not in qi or (v and qi.get(k) in [None, False, "", 0]):
                    qi[k] = v
    # Set JCI flag strictly by validation
    qi["jci_accredited"] = jci_valid_for(base_name, base_city, jci_index, verified_no_city)

    return {
        "name": base_name,
        "city": base_city,
        "state": base_state,
        "country": base_country,
        "address": base_address,
        "phone": base_phone,
        "website": base_website,
        "certifications": merged_certs,
        "quality_indicators": qi,
    }

def main():
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return 1
    orgs, original = load_db(DB_PATH)
    jci_index, verified_no_city = load_jci_index(JCI_PATH)
    # Group by normalized name
    groups = defaultdict(list)
    for o in orgs:
        if not isinstance(o, dict):
            continue
        key = normalize_text(o.get("name", ""))
        if not key:
            # Keep entries without name as-is
            groups[id(o)].append(o)
        else:
            groups[key].append(o)

    merged_orgs = []
    merged_count = 0
    for key, entries in groups.items():
        if len(entries) == 1:
            merged_orgs.append(entries[0])
        else:
            merged = merge_group(entries, jci_index, verified_no_city)
            merged_orgs.append(merged)
            merged_count += len(entries) - 1

    # Save respecting original structure
    if isinstance(original, dict) and "organizations" in original:
        original["organizations"] = merged_orgs
    else:
        original = merged_orgs
    save_db(DB_PATH, original)
    print(f"✅ Deduped dataset. Consolidated duplicates removed: {merged_count}")
    print(f"Total organizations: {len(merged_orgs)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())