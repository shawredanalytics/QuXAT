#!/usr/bin/env python3
import json
import io
from pathlib import Path

ORG_NAME = "Vasantha Subramanian Hospitals India Pvt. Ltd.".lower()
DB_PATH = Path("unified_healthcare_organizations.json")

def load_db(path: Path):
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize to list of orgs
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

def main():
    if not DB_PATH.exists():
        print(f"❌ Database file not found: {DB_PATH}")
        return 1

    orgs, original = load_db(DB_PATH)
    modified = 0
    jci_removed = 0

    for org in orgs:
        if not isinstance(org, dict):
            continue
        name = org.get("name", "").lower()
        if not name:
            continue
        if ORG_NAME in name:
            # Clean certifications: remove any JCI-like entries and empty strings
            certs = org.get("certifications", [])
            cleaned = []
            for c in certs:
                # Skip empty entries
                if isinstance(c, str) and not c.strip():
                    continue
                if is_jci_cert(c):
                    jci_removed += 1
                    continue
                cleaned.append(c)
            org["certifications"] = cleaned

            # Sanitize quality indicators
            qi = org.get("quality_indicators", {})
            if not isinstance(qi, dict):
                qi = {}
            # Unset JCI/international flags
            qi["jci_accredited"] = False
            qi["international_accreditation"] = False
            org["quality_indicators"] = qi

            modified += 1

    if modified:
        save_db(DB_PATH, original)
        print(f"✅ Updated {modified} matching entries. Removed {jci_removed} JCI-like certifications.")
    else:
        print("ℹ️ No matching entries found; no changes made.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())