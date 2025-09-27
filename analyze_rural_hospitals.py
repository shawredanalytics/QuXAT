import json
import pandas as pd
from datetime import datetime
import os

def analyze_existing_database():
    """Analyze the existing healthcare organizations database"""
    print("Analyzing existing database...")
    
    with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"Database Overview:")
    print(f"Total organizations: {db['metadata']['total_organizations']}")
    print(f"Data sources: {db['metadata']['data_sources']}")
    print(f"Last updated: {db['metadata']['integration_timestamp']}")
    
    # Sample organization structure
    if db['organizations']:
        org = db['organizations'][0]
        print(f"\nSample organization structure:")
        print(f"Name: {org['name']}")
        print(f"City: {org.get('city', 'N/A')}")
        print(f"State: {org.get('state', 'N/A')}")
        print(f"Country: {org.get('country', 'N/A')}")
        print(f"Data source: {org.get('data_source', 'N/A')}")
        print(f"Certifications: {len(org.get('certifications', []))}")
    
    # Count organizations by country
    countries = {}
    for org in db['organizations']:
        country = org.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
    
    print(f"\nTop 10 countries by organization count:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{country}: {count}")
    
    return db

def load_rural_hospitals():
    """Load and analyze the rural hospitals Excel file"""
    print("\nLoading rural hospitals data...")
    
    file_path = r'C:\Users\MANIKUMAR\Desktop\QuXAT score model training\Hospitals List - Rural India.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    
    df = pd.read_excel(file_path, sheet_name=0)
    print(f"Rural hospitals data loaded: {df.shape[0]} hospitals")
    print(f"Columns: {list(df.columns)}")
    
    # Analyze the data
    print(f"\nData analysis:")
    print(f"States: {df['State'].nunique()}")
    print(f"Districts: {df['District'].nunique()}")
    print(f"Unique hospitals: {df['Hospital Name'].nunique()}")
    
    print(f"\nTop 10 states by hospital count:")
    state_counts = df['State'].value_counts().head(10)
    for state, count in state_counts.items():
        print(f"{state}: {count}")
    
    return df

def create_hospital_entries(df):
    """Convert Excel data to database format"""
    print("\nConverting Excel data to database format...")
    
    hospitals = []
    for _, row in df.iterrows():
        hospital = {
            "name": row['Hospital Name'].strip(),
            "original_name": row['Hospital Name'].strip(),
            "city": row['District'].strip(),
            "state": row['State'].strip(),
            "country": "India",
            "hospital_type": "Rural Hospital",
            "certifications": [],
            "data_source": "Rural India Excel",
            "last_updated": datetime.now().isoformat(),
            "quality_indicators": {
                "jci_accredited": False,
                "nabh_accredited": False,
                "nabl_accredited": False,
                "rural_hospital": True
            },
            "location": {
                "district": row['District'].strip(),
                "state": row['State'].strip(),
                "country": "India"
            }
        }
        hospitals.append(hospital)
    
    print(f"Created {len(hospitals)} hospital entries")
    return hospitals

def integrate_with_database(db, new_hospitals):
    """Integrate new hospitals with existing database"""
    print("\nIntegrating with existing database...")
    
    existing_names = {org['name'].lower() for org in db['organizations']}
    
    new_count = 0
    duplicate_count = 0
    
    for hospital in new_hospitals:
        if hospital['name'].lower() not in existing_names:
            db['organizations'].append(hospital)
            new_count += 1
        else:
            duplicate_count += 1
    
    # Update metadata
    db['metadata']['total_organizations'] = len(db['organizations'])
    db['metadata']['integration_timestamp'] = datetime.now().isoformat()
    
    if 'Rural India Excel' not in db['metadata']['data_sources']:
        db['metadata']['data_sources'].append('Rural India Excel')
    
    # Update integration statistics
    if 'rural_integration_statistics' not in db['metadata']:
        db['metadata']['rural_integration_statistics'] = {}
    
    db['metadata']['rural_integration_statistics'] = {
        "rural_hospitals_processed": len(new_hospitals),
        "new_hospitals_added": new_count,
        "duplicates_skipped": duplicate_count,
        "integration_date": datetime.now().isoformat()
    }
    
    print(f"Integration complete:")
    print(f"New hospitals added: {new_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    print(f"Total organizations now: {db['metadata']['total_organizations']}")
    
    return db

def save_updated_database(db):
    """Save the updated database with backup"""
    print("\nSaving updated database...")
    
    # Create backup
    backup_file = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Read original file and create backup
    with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
        original_db = json.load(f)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(original_db, f, indent=2, ensure_ascii=False)
    
    print(f"Backup created: {backup_file}")
    
    # Save updated database
    with open('unified_healthcare_organizations.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print("Updated database saved successfully!")

def main():
    """Main function to process rural hospitals integration"""
    try:
        # Analyze existing database
        db = analyze_existing_database()
        
        # Load rural hospitals data
        df = load_rural_hospitals()
        if df is None:
            return
        
        # Convert to database format
        new_hospitals = create_hospital_entries(df)
        
        # Integrate with existing database
        updated_db = integrate_with_database(db, new_hospitals)
        
        # Save updated database
        save_updated_database(updated_db)
        
        print("\n✅ Rural hospitals integration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()