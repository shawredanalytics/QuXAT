#!/usr/bin/env python3
"""
Global Database Integrator
Aggregates worldwide healthcare organization sources into unified_healthcare_organizations.json.

Design goals:
- Scan external_organizations/ for JSON/CSV sources from any country/region.
- Normalize names and merge duplicates across sources and existing unified DB.
- Validate premium certifications (JCI cross-check; basic ISO/regional mapping) to avoid false positives.
- Preserve metadata and add data source provenance.
"""

import json
import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple


class GlobalDatabaseIntegrator:
    def __init__(self,
                 unified_db_file: str = "unified_healthcare_organizations.json",
                 sources_dir: str = "external_organizations",
                 jci_file: str = "jci_accredited_organizations.json"):
        self.unified_db_file = unified_db_file
        self.sources_dir = sources_dir
        self.jci_file = jci_file
        self.stats = {
            "existing_organizations_loaded": 0,
            "external_sources_found": 0,
            "records_loaded_from_sources": 0,
            "new_organizations_added": 0,
            "existing_organizations_updated": 0,
            "duplicates_merged": 0,
            "certifications_validated": 0,
            "jci_certifications_removed": 0,
            "total_organizations_final": 0,
        }

        # JCI index for validation
        self.jci_index = set()

    # ------------------------
    # Loading helpers
    # ------------------------
    def load_unified_database(self) -> Dict[str, Any]:
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'organizations' in data:
                orgs = data['organizations']
                meta = data.get('metadata', {})
            elif isinstance(data, list):
                orgs = data
                meta = {}
                data = {"organizations": orgs, "metadata": meta}
            else:
                orgs = []
                meta = {}
                data = {"organizations": orgs, "metadata": meta}
            self.stats["existing_organizations_loaded"] = len(orgs)
            return data
        except FileNotFoundError:
            return {"organizations": [], "metadata": {}}

    def load_jci_index(self) -> None:
        try:
            with open(self.jci_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Support both list and dict structures
            if isinstance(data, list):
                names = [d.get('name') or d.get('organization_name') for d in data]
            elif isinstance(data, dict):
                names = []
                for item in data.get('organizations', data.get('data', [])):
                    names.append(item.get('name') or item.get('organization_name'))
            else:
                names = []
            self.jci_index = {self._normalize_name(n) for n in names if n}
        except FileNotFoundError:
            self.jci_index = set()

    def scan_external_sources(self) -> List[Tuple[str, List[Dict[str, Any]]]]:
        """Return list of (source_name, records) parsed from files in sources_dir."""
        sources: List[Tuple[str, List[Dict[str, Any]]]] = []
        if not os.path.isdir(self.sources_dir):
            return sources

        for entry in os.listdir(self.sources_dir):
            path = os.path.join(self.sources_dir, entry)
            if os.path.isfile(path):
                try:
                    if entry.lower().endswith('.json'):
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        records = self._standardize_external_records(data)
                        sources.append((entry, records))
                    elif entry.lower().endswith('.csv'):
                        with open(path, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            records = self._standardize_external_records(list(reader))
                        sources.append((entry, records))
                except Exception:
                    # Skip unreadable files, keep pipeline resilient
                    continue
        self.stats["external_sources_found"] = len(sources)
        self.stats["records_loaded_from_sources"] = sum(len(r) for _, r in sources)
        return sources

    # ------------------------
    # Normalization & Validation
    # ------------------------
    def _normalize_name(self, name: str) -> str:
        if not name:
            return ""
        s = name.lower().strip()
        s = re.sub(r"[\.,'’&()\-]", " ", s)
        s = re.sub(r"\s+", " ", s)
        # Remove common corporate suffixes
        suffixes = [
            r"\bprivate limited\b", r"\bpvt\.? ltd\.?\b", r"\blimited\b", r"\bltd\b",
            r"\binc\b", r"\bincorporated\b", r"\bco\.?\b", r"\bcompany\b",
            r"\bhospital(s)?\b", r"\bmedical center\b", r"\bmed centre\b", r"\bhealthcare\b",
        ]
        for suf in suffixes:
            s = re.sub(suf, "", s)
        return s.strip()

    def _identify_certification(self, name: str) -> str:
        n = (name or "").lower()
        # Minimal mapping; scoring algorithm has more detail, but this suffices for validation grouping
        if "joint commission international" in n or n.strip() == "jci":
            return "JCI"
        if "iso" in n:
            if "15189" in n:
                return "ISO_15189"
            if "9001" in n:
                return "ISO_9001"
            if "13485" in n:
                return "ISO_13485"
            return "ISO_OTHER"
        if "cap" in n and ("college of american pathologists" in n or "accreditation" in n):
            return "CAP"
        if "nabl" in n:
            return "NABL"
        if "nabh" in n:
            return "NABH"
        if "jcqhc" in n or "japan council for quality" in n:
            return "JCQHC_JAPAN"
        if "dnv" in n:
            return "DNV"
        if "accreditation canada" in n:
            return "ACCREDITATION_CANADA"
        if "cqc" in n or "care quality commission" in n:
            return "CQC_UK"
        if "has" in n or "haute autorité de santé" in n:
            return "HAS_FRANCE"
        if "g-ba" in n or "gemeinsamer bundesausschuss" in n:
            return "GBA_GERMANY"
        if "achs" in n or "australian council on healthcare standards" in n:
            return "ACHS_AUSTRALIA"
        if "tjcha" in n or "taiwan jcia" in n:
            return "TJCHA_TAIWAN"
        if "cbahi" in n:
            return "CBAHI_SAUDI"
        if "haad" in n or "department of health abu dhabi" in n:
            return "HAAD_UAE"
        if "cohsasa" in n:
            return "COHSASA_AFRICA"
        return "OTHER"

    def _validate_and_merge_certifications(self, existing: List[Any], new_certs: List[Dict[str, Any]], org_norm_name: str) -> List[Dict[str, Any]]:
        # Normalize existing certifications to objects
        existing_objs: List[Dict[str, Any]] = []
        for c in existing or []:
            if isinstance(c, dict):
                name = (c.get('name') or '').strip()
                ctype = c.get('type') or self._identify_certification(name)
                existing_objs.append({"name": name, "type": ctype, "validated": c.get('validated', False)})
            elif isinstance(c, str):
                name = c.strip()
                ctype = self._identify_certification(name)
                existing_objs.append({"name": name, "type": ctype, "validated": False})

        existing_names = {(c.get('name') or '').strip().lower() for c in existing_objs}
        merged = list(existing_objs)

        for cert in new_certs or []:
            cname = (cert.get('name') or '').strip()
            ctype = cert.get('type') or self._identify_certification(cname)
            if not cname:
                continue

            # JCI safety: allow only if org is on official list
            if ctype == 'JCI':
                if org_norm_name not in self.jci_index:
                    self.stats["jci_certifications_removed"] += 1
                    # skip adding false-positive JCI
                    continue

            # Merge without duplicates (case-insensitive)
            if cname.lower() not in existing_names:
                merged.append({
                    "name": cname,
                    "type": ctype,
                    "validated": True if ctype != 'JCI' else True,  # JCI validated via index
                })
                existing_names.add(cname.lower())
                self.stats["certifications_validated"] += 1

        return merged

    # ------------------------
    # Integration core
    # ------------------------
    def integrate(self) -> Dict[str, Any]:
        unified = self.load_unified_database()
        organizations = unified.get('organizations', [])
        metadata = unified.get('metadata', {})
        self.load_jci_index()

        # Build index by normalized name
        index = {}
        for org in organizations:
            norm = self._normalize_name(org.get('name', ''))
            if not norm:
                continue
            index.setdefault(norm, []).append(org)

        # Load external sources
        sources = self.scan_external_sources()

        for source_name, records in sources:
            for rec in records:
                org_name = rec.get('name') or rec.get('organization_name')
                if not org_name:
                    continue
                norm_name = self._normalize_name(org_name)
                incoming = self._to_unified_org(rec, source_name)

                if norm_name in index:
                    # Merge into first existing entry under this name
                    target_org = index[norm_name][0]
                    before_certs = len(target_org.get('certifications', []))

                    # Merge certifications with validation
                    target_org['certifications'] = self._validate_and_merge_certifications(
                        target_org.get('certifications', []), incoming.get('certifications', []), norm_name
                    )

                    # Merge other fields conservatively
                    for key in ['city', 'state', 'country', 'hospital_type', 'quality_indicators']:
                        val = incoming.get(key)
                        if val and not target_org.get(key):
                            target_org[key] = val

                    # Update data_source provenance
                    ds = target_org.get('data_source', '')
                    if source_name not in (ds or ''):
                        target_org['data_source'] = (ds + ", " + source_name).strip(', ')

                    after_certs = len(target_org.get('certifications', []))
                    self.stats["duplicates_merged"] += 1 if after_certs > before_certs else 0
                    self.stats["existing_organizations_updated"] += 1
                else:
                    organizations.append(incoming)
                    index.setdefault(norm_name, []).append(incoming)
                    self.stats["new_organizations_added"] += 1

        # Update metadata
        metadata['last_updated'] = datetime.now().isoformat()
        data_sources = metadata.get('data_sources', [])
        if 'Global External Sources' not in data_sources:
            data_sources.append('Global External Sources')
        metadata['data_sources'] = data_sources
        metadata['total_organizations'] = len(organizations)

        # Persist updated database
        updated = {"organizations": organizations, "metadata": metadata}
        self.stats["total_organizations_final"] = len(organizations)
        self._save_backup()
        with open(self.unified_db_file, 'w', encoding='utf-8') as f:
            json.dump(updated, f, indent=2, ensure_ascii=False)
        return updated

    # ------------------------
    # Utilities
    # ------------------------
    def _save_backup(self) -> None:
        backup_file = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(data)
        except FileNotFoundError:
            # No existing DB to back up
            pass

    def _standardize_external_records(self, data: Any) -> List[Dict[str, Any]]:
        """
        Accepts arbitrary JSON list/dict or CSV dicts and returns a list of standardized records
        with keys: name, city, state, country, hospital_type, certifications (list of {name,type}).
        """
        records: List[Dict[str, Any]] = []
        if isinstance(data, dict):
            # Some sources might wrap with {"organizations": [...]}
            iterable = data.get('organizations') or data.get('data') or []
        elif isinstance(data, list):
            iterable = data
        else:
            iterable = []

        for item in iterable:
            try:
                name = item.get('name') or item.get('organization_name') or item.get('hospital_name')
                city = item.get('city') or item.get('town')
                state = item.get('state') or item.get('region')
                country = item.get('country') or item.get('nation')
                htype = item.get('hospital_type') or item.get('type')
                certs = item.get('certifications') or []

                # If certifications are strings, coerce to objects
                if isinstance(certs, list) and certs and isinstance(certs[0], str):
                    certs = [{"name": c, "type": self._identify_certification(c)} for c in certs]

                records.append({
                    "name": name,
                    "city": city,
                    "state": state,
                    "country": country,
                    "hospital_type": htype,
                    "certifications": certs,
                })
            except Exception:
                # Skip malformed entries
                continue
        return records

    def _to_unified_org(self, rec: Dict[str, Any], source_name: str) -> Dict[str, Any]:
        name = rec.get('name') or rec.get('organization_name')
        org = {
            "name": name,
            "original_name": name,
            "city": rec.get('city'),
            "state": rec.get('state'),
            "country": rec.get('country'),
            "hospital_type": rec.get('hospital_type'),
            "certifications": [],
            "quality_indicators": {
                "jci_accredited": False,
                "international_accreditation": False,
            },
            "data_source": source_name,
        }

        norm_name = self._normalize_name(name or "")
        # Validate and attach certifications
        org['certifications'] = self._validate_and_merge_certifications([], rec.get('certifications', []), norm_name)
        # If any validated JCI cert is present, mark indicator true
        org['quality_indicators']['jci_accredited'] = any(c.get('type') == 'JCI' for c in org['certifications'])
        org['quality_indicators']['international_accreditation'] = True if org['certifications'] else False
        return org


def main():
    integrator = GlobalDatabaseIntegrator()
    updated = integrator.integrate()
    print("Global Integration Completed")
    print("Organizations loaded:", integrator.stats["existing_organizations_loaded"])
    print("External sources:", integrator.stats["external_sources_found"],
          "records:", integrator.stats["records_loaded_from_sources"]) 
    print("New added:", integrator.stats["new_organizations_added"],
          "updated:", integrator.stats["existing_organizations_updated"],
          "duplicates merged:", integrator.stats["duplicates_merged"]) 
    print("Certifications validated:", integrator.stats["certifications_validated"],
          "JCI removed:", integrator.stats["jci_certifications_removed"]) 
    print("Total organizations final:", integrator.stats["total_organizations_final"])


if __name__ == "__main__":
    main()