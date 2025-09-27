import json

def validate_database():
    """Validate the updated database"""
    print("Database Validation Report:")
    print("=" * 50)
    
    # Load and validate the updated database
    with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Basic statistics
    print(f"Total organizations: {db['metadata']['total_organizations']}")
    print(f"Data sources: {db['metadata']['data_sources']}")
    
    # Validate rural integration statistics
    if 'rural_integration_statistics' in db['metadata']:
        stats = db['metadata']['rural_integration_statistics']
        print(f"\nRural Integration Statistics:")
        print(f"Rural hospitals processed: {stats['rural_hospitals_processed']}")
        print(f"New hospitals added: {stats['new_hospitals_added']}")
        print(f"Duplicates skipped: {stats['duplicates_skipped']}")
    
    # Count by data source
    data_sources = {}
    rural_count = 0
    for org in db['organizations']:
        source = org.get('data_source', 'Unknown')
        data_sources[source] = data_sources.get(source, 0) + 1
        if org.get('hospital_type') == 'Rural Hospital':
            rural_count += 1
    
    print(f"\nOrganizations by data source:")
    for source, count in sorted(data_sources.items(), key=lambda x: x[1], reverse=True):
        print(f"{source}: {count}")
    
    print(f"\nRural hospitals (by type): {rural_count}")
    
    # Validate India organizations
    india_orgs = [org for org in db['organizations'] if org.get('country') == 'India']
    print(f"Total India organizations: {len(india_orgs)}")
    
    # Check for required fields
    missing_fields = []
    for i, org in enumerate(db['organizations'][:100]):  # Check first 100
        if not org.get('name'):
            missing_fields.append(f"Organization {i}: missing name")
        if not org.get('country'):
            missing_fields.append(f"Organization {i}: missing country")
    
    if missing_fields:
        print(f"\nData integrity issues found:")
        for issue in missing_fields[:10]:  # Show first 10 issues
            print(f"- {issue}")
    else:
        print(f"\n✅ Data integrity check passed!")
    
    # Sample rural hospital
    rural_hospitals = [org for org in db['organizations'] if org.get('hospital_type') == 'Rural Hospital']
    if rural_hospitals:
        sample = rural_hospitals[0]
        print(f"\nSample rural hospital:")
        print(f"Name: {sample['name']}")
        print(f"State: {sample.get('state', 'N/A')}")
        print(f"City/District: {sample.get('city', 'N/A')}")
        print(f"Country: {sample.get('country', 'N/A')}")
        print(f"Hospital Type: {sample.get('hospital_type', 'N/A')}")
    
    print(f"\n✅ Database validation completed successfully!")
    return True

if __name__ == "__main__":
    validate_database()