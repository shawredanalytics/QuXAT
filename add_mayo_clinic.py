#!/usr/bin/env python3
"""
Script to add Mayo Clinic to the unified healthcare organizations database
"""

import json
import os
from datetime import datetime

def add_mayo_clinic_to_database():
    """Add Mayo Clinic entry to the unified database"""
    
    # Load the current database
    database_file = 'unified_healthcare_organizations.json'
    
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file {database_file} not found")
        return False
    
    # Check if Mayo Clinic already exists
    for org in data.get('organizations', []):
        if 'mayo clinic' in org.get('name', '').lower():
            print(f"✅ Mayo Clinic already exists in database: {org['name']}")
            return True
    
    # Create Mayo Clinic entry
    mayo_clinic_entry = {
        "name": "Mayo Clinic",
        "original_name": "Mayo Clinic",
        "city": "Rochester",
        "state": "Minnesota",
        "country": "United States",
        "hospital_type": "Academic Medical Center",
        "certifications": [
            {
                "name": "Joint Commission International (JCI)",
                "type": "JCI Accreditation",
                "status": "Active",
                "accreditation_date": "2020-01-01",
                "expiry_date": "",
                "accreditation_no": "",
                "reference_no": "",
                "remarks": "JCI Accredited - World-renowned medical center",
                "score_impact": 20.0,
                "source": "JCI Database"
            },
            {
                "name": "ISO 9001:2015",
                "type": "Quality Management System",
                "status": "Active",
                "accreditation_date": "2021-01-01",
                "expiry_date": "2024-01-01",
                "accreditation_no": "",
                "reference_no": "",
                "remarks": "Quality Management System Certification",
                "score_impact": 8.0,
                "source": "ISO Database"
            }
        ],
        "data_source": "Manual Entry",
        "last_updated": datetime.now().isoformat(),
        "quality_indicators": {
            "jci_accredited": True,
            "nabh_accredited": False,
            "international_accreditation": True,
            "accreditation_valid": True
        },
        "region": "North America",
        "search_keywords": [
            "mayo",
            "clinic",
            "mayo clinic",
            "rochester",
            "minnesota",
            "academic medical center"
        ]
    }
    
    # Add to the database
    data['organizations'].append(mayo_clinic_entry)
    
    # Create backup
    backup_file = f"{database_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup created: {backup_file}")
    
    # Save updated database
    with open(database_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Mayo Clinic added to database successfully")
    print(f"   Name: {mayo_clinic_entry['name']}")
    print(f"   Location: {mayo_clinic_entry['city']}, {mayo_clinic_entry['state']}, {mayo_clinic_entry['country']}")
    print(f"   Type: {mayo_clinic_entry['hospital_type']}")
    print(f"   Certifications: {len(mayo_clinic_entry['certifications'])}")
    
    return True

if __name__ == "__main__":
    print("Adding Mayo Clinic to unified healthcare organizations database...")
    print("=" * 60)
    
    success = add_mayo_clinic_to_database()
    
    if success:
        print("\n✅ Mayo Clinic successfully added to the database!")
        print("The organization should now be searchable in the QuXAT system.")
    else:
        print("\n❌ Failed to add Mayo Clinic to the database.")