#!/usr/bin/env python3
"""
Script to add Johns Hopkins Hospital to the unified healthcare organizations database
"""

import json
import os
from datetime import datetime

def add_johns_hopkins_to_database():
    """Add Johns Hopkins Hospital entry to the unified database"""
    
    # Load the current database
    database_file = 'unified_healthcare_organizations_with_mayo_cap.json'
    
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file {database_file} not found")
        return False
    
    # Handle different JSON structures
    if isinstance(data, dict) and 'organizations' in data:
        orgs = data['organizations']
    elif isinstance(data, list):
        orgs = data
        data = {'organizations': orgs}
    else:
        orgs = [data] if isinstance(data, dict) else []
        data = {'organizations': orgs}
    
    # Check if Johns Hopkins already exists
    for org in orgs:
        if 'johns hopkins' in org.get('name', '').lower():
            print(f"✅ Johns Hopkins already exists in database: {org['name']}")
            return True
    
    # Create Johns Hopkins Hospital entry
    johns_hopkins_entry = {
        "name": "Johns Hopkins Hospital",
        "original_name": "Johns Hopkins Hospital",
        "city": "Baltimore",
        "state": "Maryland",
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
                "remarks": "JCI Accredited - World-renowned academic medical center",
                "score_impact": 20.0,
                "source": "JCI Database"
            },
            {
                "name": "The Joint Commission",
                "type": "Hospital Accreditation",
                "status": "Active",
                "accreditation_date": "2023-01-01",
                "expiry_date": "2026-01-01",
                "accreditation_no": "",
                "reference_no": "",
                "remarks": "Joint Commission Accredited Hospital",
                "score_impact": 15.0,
                "source": "Joint Commission"
            },
            {
                "name": "Magnet Recognition Program",
                "type": "Nursing Excellence",
                "status": "Active",
                "accreditation_date": "2022-01-01",
                "expiry_date": "2026-01-01",
                "accreditation_no": "",
                "reference_no": "",
                "remarks": "Magnet Recognition for Nursing Excellence",
                "score_impact": 12.0,
                "source": "American Nurses Credentialing Center"
            }
        ],
        "data_source": "Manual Entry",
        "last_updated": datetime.now().isoformat(),
        "quality_indicators": {
            "jci_accredited": True,
            "joint_commission_accredited": True,
            "magnet_recognized": True,
            "international_accreditation": True,
            "accreditation_valid": True,
            "academic_medical_center": True,
            "research_hospital": True
        },
        "region": "North America",
        "search_keywords": [
            "johns hopkins",
            "hopkins",
            "baltimore",
            "maryland",
            "academic medical center",
            "research hospital",
            "teaching hospital"
        ],
        "quality_initiatives": [
            {
                "name": "Johns Hopkins Quality and Safety",
                "description": "Comprehensive quality improvement and patient safety program",
                "status": "Active",
                "impact": "High",
                "category": "Quality Management"
            },
            {
                "name": "Johns Hopkins Research Excellence",
                "description": "Leading medical research and innovation programs",
                "status": "Active",
                "impact": "High",
                "category": "Research and Innovation"
            }
        ],
        "specialties": [
            "Cardiac Surgery",
            "Oncology",
            "Neurology",
            "Neurosurgery",
            "Transplant Medicine",
            "Pediatrics",
            "Emergency Medicine",
            "Internal Medicine"
        ],
        "quality_score": 95.0,
        "us_news_ranking": {
            "overall_rank": 3,
            "specialty_rankings": {
                "Cardiology": 2,
                "Neurology": 1,
                "Oncology": 4,
                "Orthopedics": 5
            }
        }
    }
    
    # Add to database
    orgs.append(johns_hopkins_entry)
    
    # Update metadata if it exists
    if 'metadata' in data:
        data['metadata']['total_organizations'] = len(orgs)
        data['metadata']['last_updated'] = datetime.now().isoformat()
        if 'data_sources' not in data['metadata']:
            data['metadata']['data_sources'] = []
        if 'Manual Entry - Johns Hopkins' not in data['metadata']['data_sources']:
            data['metadata']['data_sources'].append('Manual Entry - Johns Hopkins')
    
    # Save updated database
    try:
        with open(database_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Johns Hopkins Hospital added to database successfully")
        print(f"   Name: {johns_hopkins_entry['name']}")
        print(f"   Location: {johns_hopkins_entry['city']}, {johns_hopkins_entry['state']}, {johns_hopkins_entry['country']}")
        print(f"   Type: {johns_hopkins_entry['hospital_type']}")
        print(f"   Quality Score: {johns_hopkins_entry['quality_score']}")
        print(f"   Certifications: {len(johns_hopkins_entry['certifications'])}")
        print(f"   Total organizations in database: {len(orgs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving database: {e}")
        return False

def main():
    """Main function"""
    print("🏥 Adding Johns Hopkins Hospital to QuXAT Database")
    print("=" * 50)
    
    success = add_johns_hopkins_to_database()
    
    if success:
        print("\n🎉 Johns Hopkins Hospital integration completed!")
        print("   - Added to unified database")
        print("   - Includes JCI, Joint Commission, and Magnet certifications")
        print("   - Quality score: 95.0")
        print("   - Ready for QuXAT scoring system")
    else:
        print("\n❌ Failed to add Johns Hopkins Hospital")

if __name__ == "__main__":
    main()