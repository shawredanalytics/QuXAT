#!/usr/bin/env python3
"""
Generate an integration audit CSV from unified_healthcare_organizations.json.

Outputs:
- integration_audit.csv: Per-organization provenance, certifications summary, scores, JCI dates
- integration_audit_summary.csv: Counts by source and JCI presence

This script is defensive to accommodate variations in the unified DB structure:
- The DB may be a list of orgs, or a dict with key 'organizations'
- Provenance may appear under 'sources', 'data_sources', 'source', or similar
- Certifications may be a list of dicts or strings
"""

import csv
import json
import os
from typing import Any, Dict, List


DB_PATH = os.path.join(os.path.dirname(__file__), 'unified_healthcare_organizations.json')
AUDIT_CSV_PATH = os.path.join(os.path.dirname(__file__), 'integration_audit.csv')
SUMMARY_CSV_PATH = os.path.join(os.path.dirname(__file__), 'integration_audit_summary.csv')


def load_organizations() -> List[Dict[str, Any]]:
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file not found: {DB_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return []

    if isinstance(data, dict) and 'organizations' in data:
        orgs = data.get('organizations', [])
    elif isinstance(data, list):
        orgs = data
    else:
        orgs = []

    # Filter to dicts only
    return [o for o in orgs if isinstance(o, dict)]


def ensure_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


def extract_sources(org: Dict[str, Any]) -> List[str]:
    candidates = []
    for key in ['sources', 'data_sources', 'source', 'provenance', 'external_sources']:
        v = org.get(key)
        if v:
            candidates.extend(ensure_list(v))
    # Normalize to strings and strip
    normalized = []
    for s in candidates:
        if isinstance(s, dict):
            # try common fields
            name = s.get('name') or s.get('source') or s.get('id') or ''
            if name:
                normalized.append(str(name).strip())
        else:
            normalized.append(str(s).strip())
    # Deduplicate while preserving order
    seen = set()
    result = []
    for s in normalized:
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return result


def extract_certifications(org: Dict[str, Any]) -> List[Dict[str, Any]]:
    certs = org.get('certifications')
    if not certs:
        return []
    result = []
    for c in ensure_list(certs):
        if isinstance(c, dict):
            result.append(c)
        elif isinstance(c, str):
            # Normalize string certification into dict-like
            result.append({'name': c})
    return result


def has_jci(certifications: List[Dict[str, Any]]) -> bool:
    for c in certifications:
        name = str(c.get('name', '')).lower()
        typ = str(c.get('type', '')).lower()
        issuer = str(c.get('issuer', '')).lower()
        if 'jci' in name or 'joint commission international' in name:
            return True
        if 'jci' in typ or 'joint commission international' in typ:
            return True
        if 'jci' in issuer or 'joint commission international' in issuer:
            return True
    return False


def extract_jci_dates(certifications: List[Dict[str, Any]]) -> Dict[str, str]:
    """Return accreditation and expiry dates if JCI cert present."""
    acc = ''
    exp = ''
    for c in certifications:
        name = str(c.get('name', '')).lower()
        typ = str(c.get('type', '')).lower()
        issuer = str(c.get('issuer', '')).lower()
        is_jci = (
            'jci' in name or 'joint commission international' in name or
            'jci' in typ or 'joint commission international' in typ or
            'jci' in issuer or 'joint commission international' in issuer
        )
        if is_jci:
            acc = str(c.get('accreditation_date', c.get('valid_from', c.get('date', ''))))
            exp = str(c.get('expiry_date', c.get('valid_until', '')))
            break
    return {'jci_accreditation_date': acc, 'jci_expiry_date': exp}


def safe_get(org: Dict[str, Any], key: str, default: str = '') -> str:
    val = org.get(key)
    if val is None:
        return default
    return str(val)


def write_audit_csv(orgs: List[Dict[str, Any]]) -> Dict[str, int]:
    os.makedirs(os.path.dirname(AUDIT_CSV_PATH), exist_ok=True)
    source_counts: Dict[str, int] = {}
    jci_count = 0
    total = 0

    with open(AUDIT_CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'name', 'country', 'city', 'sources', 'source_count',
            'certifications_count', 'certification_names', 'has_jci',
            'jci_accreditation_date', 'jci_expiry_date',
            'total_score', 'certification_score', 'quality_initiatives_score', 'patient_feedback_score',
            'website', 'last_updated'
        ])

        for org in orgs:
            total += 1
            sources = extract_sources(org)
            for s in sources:
                source_counts[s] = source_counts.get(s, 0) + 1

            certs = extract_certifications(org)
            jci_flag = has_jci(certs)
            jci_dates = extract_jci_dates(certs)
            if jci_flag:
                jci_count += 1

            cert_names = '; '.join([str(c.get('name', '') or '').strip() for c in certs if isinstance(c, dict)])

            # Scores (defensive: may be absent)
            total_score = org.get('total_score', org.get('score', ''))
            cert_score = org.get('certification_score', '')
            qi_score = org.get('quality_initiatives_score', org.get('quality_score', ''))
            pf_score = org.get('patient_feedback_score', '')

            writer.writerow([
                safe_get(org, 'id') or safe_get(org, 'uuid') or safe_get(org, 'organization_id'),
                safe_get(org, 'name'),
                safe_get(org, 'country'),
                safe_get(org, 'city'),
                '; '.join(sources),
                len(sources),
                len(certs),
                cert_names,
                'yes' if jci_flag else 'no',
                jci_dates.get('jci_accreditation_date', ''),
                jci_dates.get('jci_expiry_date', ''),
                total_score,
                cert_score,
                qi_score,
                pf_score,
                safe_get(org, 'website'),
                safe_get(org, 'last_updated') or safe_get(org, 'updated_at') or safe_get(org, 'timestamp')
            ])

    return {
        'total': total,
        'jci': jci_count,
        **{f'source::{k}': v for k, v in source_counts.items()}
    }


def write_summary_csv(summary: Dict[str, int]):
    with open(SUMMARY_CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'count'])
        # Ensure deterministic ordering: total, jci, then sources alphabetical
        keys = ['total', 'jci'] + sorted([k for k in summary.keys() if k.startswith('source::')])
        for k in keys:
            writer.writerow([k, summary.get(k, 0)])


def main():
    orgs = load_organizations()
    if not orgs:
        print("⚠️ No organizations loaded; audit will be empty.")
    summary = write_audit_csv(orgs)
    write_summary_csv(summary)
    print(f"✅ Audit generated: {AUDIT_CSV_PATH}")
    print(f"✅ Summary generated: {SUMMARY_CSV_PATH}")
    print(f"Total organizations: {summary.get('total', 0)}")
    print(f"Organizations with JCI: {summary.get('jci', 0)}")
    # Show top 10 sources by count
    source_items = [(k.replace('source::', ''), v) for k, v in summary.items() if k.startswith('source::')]
    source_items.sort(key=lambda x: x[1], reverse=True)
    print("Top sources:")
    for name, count in source_items[:10]:
        print(f"- {name}: {count}")


if __name__ == '__main__':
    main()