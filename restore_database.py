import json
import shutil
from datetime import datetime

# Backup current database first
current_file = "unified_healthcare_organizations.json"
backup_file = "unified_healthcare_organizations_backup_20250927_143420.json"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_backup = f"unified_healthcare_organizations_backup_{timestamp}.json"

try:
    # Create backup of current file
    shutil.copy(current_file, current_backup)
    print(f"Current database backed up to: {current_backup}")
    
    # Restore from backup
    shutil.copy(backup_file, current_file)
    print(f"Database restored from: {backup_file}")
    
    # Verify restoration
    with open(current_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'organizations' in data:
        orgs = data['organizations']
        apollo_count = len([org for org in orgs if 'apollo' in org.get('name', '').lower()])
        print(f"Verification: {len(orgs)} organizations loaded, {apollo_count} Apollo hospitals found")
    
    print("Database restoration completed successfully!")
    
except Exception as e:
    print(f"Error during restoration: {e}")