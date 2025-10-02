import json

# Check backup database for Apollo hospitals
backup_file = "unified_healthcare_organizations_backup_20250927_143420.json"

try:
    with open(backup_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Backup database structure:")
    print(f"Keys: {list(data.keys())}")
    
    if 'organizations' in data:
        orgs = data['organizations']
        print(f"Total organizations in backup: {len(orgs)}")
        
        # Search for Apollo hospitals
        apollo_orgs = [org for org in orgs if 'apollo' in org.get('name', '').lower()]
        print(f"Apollo organizations found: {len(apollo_orgs)}")
        
        if apollo_orgs:
            print("\nFirst few Apollo organizations:")
            for i, org in enumerate(apollo_orgs[:5]):
                print(f"{i+1}. {org.get('name', 'N/A')}")
        
        # Show first few organizations
        print(f"\nFirst 5 organizations in backup:")
        for i, org in enumerate(orgs[:5]):
            print(f"{i+1}. {org.get('name', 'N/A')}")
    
except Exception as e:
    print(f"Error reading backup file: {e}")