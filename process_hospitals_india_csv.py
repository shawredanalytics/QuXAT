#!/usr/bin/env python3
"""
HospitalsInIndia CSV Data Processor and Database Integrator
Processes the HospitalsInIndia.csv file and integrates it with the existing QuXAT database.
"""

import pandas as pd
import json
import os
from datetime import datetime
import uuid

def analyze_csv_data():
    """Analyze the HospitalsInIndia.csv file structure and quality."""
    file_path = r'C:\Users\MANIKUMAR\Desktop\QuXAT score model training\HospitalsInIndia.csv'
    
    print("=== ANALYZING HOSPITALSINDIA.CSV ===")
    
    # Load CSV data
    df = pd.read_csv(file_path)
    
    print(f"Dataset Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Data quality analysis
    print(f"\nData Quality Analysis:")
    print(f"- Total hospitals: {len(df)}")
    print(f"- Unique hospitals: {df['Hospital'].nunique()}")
    print(f"- States covered: {df['State'].nunique()}")
    print(f"- Cities covered: {df['City'].nunique()}")
    print(f"- Missing pincodes: {df['Pincode'].isnull().sum()}")
    
    # State distribution
    print(f"\nTop 10 States by Hospital Count:")
    print(df['State'].value_counts().head(10))
    
    # City distribution
    print(f"\nTop 10 Cities by Hospital Count:")
    print(df['City'].value_counts().head(10))
    
    return df

def load_existing_database():
    """Load the existing unified healthcare organizations database."""
    db_path = 'unified_healthcare_organizations.json'
    
    print(f"\n=== LOADING EXISTING DATABASE ===")
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"Current database statistics:")
    total_orgs = db['metadata'].get('total_organizations', 
                                   db['metadata'].get('integration_statistics', {}).get('total_organizations_final', 
                                   len(db.get('organizations', []))))
    print(f"- Total organizations: {total_orgs}")
    print(f"- Data sources: {len(db['metadata']['data_sources'])}")
    last_updated = db['metadata'].get('last_updated', db['metadata'].get('integration_timestamp', 'Unknown'))
    print(f"- Last updated: {last_updated}")
    
    return db

def convert_csv_to_database_format(df):
    """Convert CSV data to database format compatible with existing structure."""
    print(f"\n=== CONVERTING CSV TO DATABASE FORMAT ===")
    
    converted_hospitals = []
    
    for idx, row in df.iterrows():
        # Skip if hospital name is missing or invalid
        if pd.isna(row['Hospital']) or not str(row['Hospital']).strip():
            continue
            
        hospital_id = str(uuid.uuid4())
        
        # Create hospital entry in database format
        hospital_entry = {
            "id": hospital_id,
            "name": str(row['Hospital']).strip(),
            "country": "India",
            "state": str(row['State']).strip() if pd.notna(row['State']) else "",
            "city": str(row['City']).strip() if pd.notna(row['City']) else "",
            "address": str(row['LocalAddress']).strip() if pd.notna(row['LocalAddress']) else "",
            "pincode": str(int(row['Pincode'])) if pd.notna(row['Pincode']) else "",
            "hospital_type": "General Hospital",
            "data_source": "HospitalsInIndia CSV",
            "certifications": [],
            "quality_indicators": {
                "csv_hospital": True,
                "has_address": bool(str(row['LocalAddress']).strip() if pd.notna(row['LocalAddress']) else False),
                "has_pincode": bool(pd.notna(row['Pincode'])),
                "location_verified": True
            },
            "accreditation_status": "Not Specified",
            "services": [],
            "contact_info": {},
            "last_updated": datetime.now().isoformat(),
            "integration_timestamp": datetime.now().isoformat()
        }
        
        converted_hospitals.append(hospital_entry)
    
    print(f"Successfully converted {len(converted_hospitals)} hospitals from CSV")
    return converted_hospitals

def integrate_with_existing_database(existing_db, new_hospitals):
    """Integrate new hospitals with existing database."""
    print(f"\n=== INTEGRATING WITH EXISTING DATABASE ===")
    
    # Create backup
    backup_filename = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(existing_db, f, indent=2, ensure_ascii=False)
    print(f"Backup created: {backup_filename}")
    
    # Check for duplicates based on name and location
    existing_names = set()
    for org in existing_db['organizations']:
        key = f"{org['name'].lower()}_{org.get('city', '').lower()}_{org.get('state', '').lower()}"
        existing_names.add(key)
    
    new_added = 0
    duplicates_skipped = 0
    
    for hospital in new_hospitals:
        key = f"{hospital['name'].lower()}_{hospital['city'].lower()}_{hospital['state'].lower()}"
        
        if key not in existing_names:
            existing_db['organizations'].append(hospital)
            existing_names.add(key)
            new_added += 1
        else:
            duplicates_skipped += 1
    
    # Update metadata
    existing_db['metadata']['total_organizations'] = len(existing_db['organizations'])
    existing_db['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Add new data source
    if "HospitalsInIndia CSV" not in existing_db['metadata']['data_sources']:
        existing_db['metadata']['data_sources'].append("HospitalsInIndia CSV")
    
    # Update integration statistics
    if 'integration_stats' not in existing_db['metadata']:
        existing_db['metadata']['integration_stats'] = {}
    
    existing_db['metadata']['integration_stats']['hospitals_india_csv'] = {
        "total_processed": len(new_hospitals),
        "new_hospitals_added": new_added,
        "duplicates_skipped": duplicates_skipped,
        "integration_date": datetime.now().isoformat()
    }
    
    print(f"Integration completed:")
    print(f"- New hospitals added: {new_added}")
    print(f"- Duplicates skipped: {duplicates_skipped}")
    print(f"- Total organizations now: {existing_db['metadata']['total_organizations']}")
    
    return existing_db

def save_updated_database(updated_db):
    """Save the updated database."""
    print(f"\n=== SAVING UPDATED DATABASE ===")
    
    output_path = 'unified_healthcare_organizations.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_db, f, indent=2, ensure_ascii=False)
    
    print(f"Updated database saved to: {output_path}")
    return output_path

def main():
    """Main processing function."""
    try:
        # Step 1: Analyze CSV data
        df = analyze_csv_data()
        
        # Step 2: Load existing database
        existing_db = load_existing_database()
        
        # Step 3: Convert CSV to database format
        new_hospitals = convert_csv_to_database_format(df)
        
        # Step 4: Integrate with existing database
        updated_db = integrate_with_existing_database(existing_db, new_hospitals)
        
        # Step 5: Save updated database
        save_updated_database(updated_db)
        
        print(f"\n=== INTEGRATION SUMMARY ===")
        print(f"✅ Successfully processed HospitalsInIndia.csv")
        print(f"✅ Integrated {updated_db['metadata']['integration_stats']['hospitals_india_csv']['new_hospitals_added']} new hospitals")
        print(f"✅ Total organizations: {updated_db['metadata']['total_organizations']}")
        print(f"✅ Database updated successfully")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()