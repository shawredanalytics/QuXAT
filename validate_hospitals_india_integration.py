#!/usr/bin/env python3
"""
Validation Script for HospitalsInIndia.csv Integration
Validates the successful integration of hospital data from CSV into the QuXAT database.
"""

import json
import pandas as pd
from collections import Counter

def validate_integration():
    """Validate the HospitalsInIndia.csv integration."""
    print("=== VALIDATING HOSPITALSINDIA.CSV INTEGRATION ===")
    
    # Load updated database
    with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print(f"\n📊 DATABASE OVERVIEW:")
    print(f"- Total organizations: {db['metadata']['total_organizations']}")
    print(f"- Data sources: {db['metadata']['data_sources']}")
    
    # Check integration statistics
    if 'integration_stats' in db['metadata'] and 'hospitals_india_csv' in db['metadata']['integration_stats']:
        stats = db['metadata']['integration_stats']['hospitals_india_csv']
        print(f"\n📈 HOSPITALSINDIA.CSV INTEGRATION STATS:")
        print(f"- Total processed: {stats['total_processed']}")
        print(f"- New hospitals added: {stats['new_hospitals_added']}")
        print(f"- Duplicates skipped: {stats['duplicates_skipped']}")
        print(f"- Integration date: {stats['integration_date']}")
    
    # Count organizations by data source
    print(f"\n🏥 ORGANIZATIONS BY DATA SOURCE:")
    source_counts = Counter()
    csv_hospitals = []
    
    for org in db['organizations']:
        source = org.get('data_source', 'Unknown')
        source_counts[source] += 1
        
        if source == "HospitalsInIndia CSV":
            csv_hospitals.append(org)
    
    for source, count in source_counts.most_common():
        print(f"- {source}: {count}")
    
    # Analyze CSV hospitals
    print(f"\n🔍 CSV HOSPITALS ANALYSIS:")
    print(f"- Total CSV hospitals in database: {len(csv_hospitals)}")
    
    if csv_hospitals:
        # State distribution
        states = [h.get('state', 'Unknown') for h in csv_hospitals]
        state_counts = Counter(states)
        print(f"- States covered: {len(state_counts)}")
        print(f"- Top 5 states:")
        for state, count in state_counts.most_common(5):
            print(f"  • {state}: {count}")
        
        # City distribution
        cities = [h.get('city', 'Unknown') for h in csv_hospitals]
        city_counts = Counter(cities)
        print(f"- Cities covered: {len(city_counts)}")
        print(f"- Top 5 cities:")
        for city, count in city_counts.most_common(5):
            print(f"  • {city}: {count}")
        
        # Quality indicators
        has_address = sum(1 for h in csv_hospitals if h.get('quality_indicators', {}).get('has_address', False))
        has_pincode = sum(1 for h in csv_hospitals if h.get('quality_indicators', {}).get('has_pincode', False))
        
        print(f"- Hospitals with address: {has_address} ({has_address/len(csv_hospitals)*100:.1f}%)")
        print(f"- Hospitals with pincode: {has_pincode} ({has_pincode/len(csv_hospitals)*100:.1f}%)")
    
    # Data integrity checks
    print(f"\n✅ DATA INTEGRITY CHECKS:")
    
    # Check for required fields
    missing_name = sum(1 for org in db['organizations'] if not org.get('name', '').strip())
    missing_country = sum(1 for org in db['organizations'] if not org.get('country', '').strip())
    
    print(f"- Organizations missing name: {missing_name}")
    print(f"- Organizations missing country: {missing_country}")
    
    # Check India organizations
    india_orgs = [org for org in db['organizations'] if org.get('country', '').lower() == 'india']
    print(f"- Total India organizations: {len(india_orgs)}")
    
    # Sample CSV hospital
    if csv_hospitals:
        print(f"\n📋 SAMPLE CSV HOSPITAL:")
        sample = csv_hospitals[0]
        print(f"- Name: {sample.get('name', 'N/A')}")
        print(f"- State: {sample.get('state', 'N/A')}")
        print(f"- City: {sample.get('city', 'N/A')}")
        print(f"- Address: {sample.get('address', 'N/A')[:50]}...")
        print(f"- Pincode: {sample.get('pincode', 'N/A')}")
        print(f"- Hospital Type: {sample.get('hospital_type', 'N/A')}")
        print(f"- Data Source: {sample.get('data_source', 'N/A')}")
    
    # Validation summary
    print(f"\n🎯 VALIDATION SUMMARY:")
    
    validation_passed = True
    
    # Check if CSV data was added
    if len(csv_hospitals) == 0:
        print("❌ No CSV hospitals found in database")
        validation_passed = False
    else:
        print(f"✅ {len(csv_hospitals)} CSV hospitals successfully integrated")
    
    # Check data source
    if "HospitalsInIndia CSV" not in db['metadata']['data_sources']:
        print("❌ CSV data source not found in metadata")
        validation_passed = False
    else:
        print("✅ CSV data source properly recorded")
    
    # Check integration stats
    if 'integration_stats' not in db['metadata'] or 'hospitals_india_csv' not in db['metadata']['integration_stats']:
        print("❌ Integration statistics not found")
        validation_passed = False
    else:
        print("✅ Integration statistics properly recorded")
    
    # Check data integrity
    if missing_name > 0 or missing_country > 0:
        print(f"⚠️  Data integrity issues found (missing names: {missing_name}, missing countries: {missing_country})")
    else:
        print("✅ Data integrity checks passed")
    
    if validation_passed:
        print(f"\n🎉 VALIDATION PASSED: HospitalsInIndia.csv integration successful!")
    else:
        print(f"\n❌ VALIDATION FAILED: Issues found in integration")
    
    return validation_passed

def compare_with_original_csv():
    """Compare integrated data with original CSV file."""
    print(f"\n=== COMPARING WITH ORIGINAL CSV ===")
    
    try:
        # Load original CSV
        csv_path = r'C:\Users\MANIKUMAR\Desktop\QuXAT score model training\HospitalsInIndia.csv'
        df = pd.read_csv(csv_path)
        
        # Load database
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Get CSV hospitals from database
        csv_hospitals = [org for org in db['organizations'] if org.get('data_source') == "HospitalsInIndia CSV"]
        
        print(f"📊 COMPARISON RESULTS:")
        print(f"- Original CSV hospitals: {len(df)}")
        print(f"- Integrated CSV hospitals: {len(csv_hospitals)}")
        print(f"- Integration rate: {len(csv_hospitals)/len(df)*100:.1f}%")
        
        # Compare states
        original_states = set(df['State'].unique())
        integrated_states = set(h.get('state', '') for h in csv_hospitals)
        
        print(f"- Original states: {len(original_states)}")
        print(f"- Integrated states: {len(integrated_states)}")
        print(f"- State coverage: {len(integrated_states & original_states)/len(original_states)*100:.1f}%")
        
        # Compare cities
        original_cities = set(df['City'].unique())
        integrated_cities = set(h.get('city', '') for h in csv_hospitals)
        
        print(f"- Original cities: {len(original_cities)}")
        print(f"- Integrated cities: {len(integrated_cities)}")
        print(f"- City coverage: {len(integrated_cities & original_cities)/len(original_cities)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error comparing with original CSV: {str(e)}")

def main():
    """Main validation function."""
    try:
        validation_passed = validate_integration()
        compare_with_original_csv()
        
        if validation_passed:
            print(f"\n🎉 ALL VALIDATIONS PASSED!")
            print(f"✅ HospitalsInIndia.csv data successfully integrated into QuXAT database")
        else:
            print(f"\n❌ VALIDATION ISSUES DETECTED")
            print(f"⚠️  Please review the integration process")
            
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        raise

if __name__ == "__main__":
    main()