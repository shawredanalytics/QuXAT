#!/usr/bin/env python3
import json
import io
from pathlib import Path

ORG_KEY = "Vasantha Subramanian Hospitals India Pvt. Ltd.".lower()
DB_PATH = Path("unified_healthcare_organizations.json")

def load_db(path: Path):
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize to iterable orgs and keep original structure for saving
    if isinstance(data, dict) and "organizations" in data:
        return data["organizations"], data
    elif isinstance(data, list):
        return data, data
    else:
        return [data], data

def save_db(path: Path, original):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(original, f, ensure_ascii=False, indent=2)

def is_jci_cert(cert):
    try:
        name = (cert.get("name", "") if isinstance(cert, dict) else str(cert)).upper()
    except Exception:
        name = str(cert).upper()
    return ("JCI" in name) or ("JOINT COMMISSION" in name)

def dedupe_certs(certs):
    """Deduplicate certifications by name, drop empties, drop JCI."""
    seen = set()
    out = []
    for c in certs or []:
        # Skip empty string entries
        if isinstance(c, str) and not c.strip():
            continue
        # Drop any JCI-like entries
        if is_jci_cert(c):
            continue
        # Use name for dedupe when possible
        key = None
        if isinstance(c, dict):
            key = (c.get("name", "") or "").strip().upper()
        else:
            key = str(c).strip().upper()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out.append(c)
    return out

def choose_value(*vals):
    """Choose the first non-empty string value."""
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v
    return ""

def merge_entries(entries):
    """Merge duplicate org entries into a single canonical entry."""
    base = {}
    if not entries:
        return base
    # Start with the first as base
    base = dict(entries[0])
    # Normalize name formatting
    base["name"] = choose_value(*(e.get("name", "") for e in entries)) or base.get("name", "")
    # Prefer filled location fields
    base["city"] = choose_value(*(e.get("city", "") for e in entries))
    base["state"] = choose_value(*(e.get("state", "") for e in entries))
    base["country"] = choose_value(*(e.get("country", "") for e in entries)) or base.get("country", "")
    # Merge certifications cleanly
    all_certs = []
    for e in entries:
        certs = e.get("certifications", [])
        if isinstance(certs, list):
            all_certs.extend(certs)
    base["certifications"] = dedupe_certs(all_certs)
    # Merge quality_indicators; ensure JCI false and international false
    qi = {}
    for e in entries:
        q = e.get("quality_indicators", {})
        if isinstance(q, dict):
            qi.update({k: v for k, v in q.items() if v is not None})
    if not isinstance(qi, dict):
        qi = {}
    qi["jci_accredited"] = False
    qi["international_accreditation"] = False
    base["quality_indicators"] = qi
    return base

def main():
    if not DB_PATH.exists():
        print(f"❌ Database file not found: {DB_PATH}")
        return 1
    orgs, original = load_db(DB_PATH)
    # Find duplicates by name contains
    matches = [o for o in orgs if isinstance(o, dict) and ORG_KEY in o.get("name", "").lower()]
    if len(matches) <= 1:
        print("ℹ️ No duplicates found; nothing to merge.")
        return 0
    # Build merged entry
    merged = merge_entries(matches)
    # Remove all original matches from orgs
    remaining = [o for o in orgs if not (isinstance(o, dict) and ORG_KEY in o.get("name", "").lower())]
    # Insert merged entry
    remaining.append(merged)
    # Save back respecting original structure
    if isinstance(original, dict) and "organizations" in original:
        original["organizations"] = remaining
    else:
        original = remaining
    save_db(DB_PATH, original)
    print(f"✅ Merged {len(matches)} entries into one. Certifications: {len(merged.get('certifications', []))}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())