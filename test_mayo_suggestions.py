import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

from streamlit_app import HealthcareOrgAnalyzer

# Initialize analyzer
analyzer = HealthcareOrgAnalyzer()

# Test Mayo suggestions
print("Testing Mayo Clinic suggestions...")
suggestions = analyzer.generate_organization_suggestions('Mayo')
print(f'Suggestions for "Mayo": {len(suggestions)}')
for i, s in enumerate(suggestions[:10]):
    print(f'{i+1}. {s["display_name"]} - {s.get("location", "No location")}')

print("\n" + "="*50)

# Test exact match
suggestions_exact = analyzer.generate_organization_suggestions('Mayo Clinic')
print(f'Suggestions for "Mayo Clinic": {len(suggestions_exact)}')
for i, s in enumerate(suggestions_exact[:10]):
    print(f'{i+1}. {s["display_name"]} - {s.get("location", "No location")}')

print("\n" + "="*50)

# Check if Mayo Clinic exists in database
print("Checking if Mayo Clinic exists in database...")
found_orgs = analyzer.search_organization_info('Mayo Clinic')
print(f'Found organizations: {found_orgs}')
print(f'Type of found_orgs: {type(found_orgs)}')

if isinstance(found_orgs, dict):
    print(f'Organization data: {found_orgs.get("name", "Unknown")} - {found_orgs.get("city", "No city")}')
elif isinstance(found_orgs, list):
    for i, org in enumerate(found_orgs[:5]):
        print(f'{i+1}. {org.get("name", "Unknown")} - {org.get("city", "No city")}')
else:
    print(f'Unexpected type: {type(found_orgs)}')

print("\n" + "="*50)

# Check unified database directly
print("Checking unified database for Mayo entries...")
if analyzer.unified_database:
    mayo_entries = []
    for org in analyzer.unified_database:
        org_name = org.get('name', '').lower()
        if 'mayo' in org_name:
            mayo_entries.append(org)
    
    print(f'Found {len(mayo_entries)} entries with "mayo" in name:')
    for org in mayo_entries[:10]:
        print(f'- {org.get("name", "Unknown")} - {org.get("city", "No city")}')