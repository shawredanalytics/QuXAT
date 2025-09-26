import json

# Load the unified healthcare organizations database
with open('unified_healthcare_organizations.json', 'r') as f:
    organizations = json.load(f)

print(f"Total healthcare organizations in database: {len(organizations)}")
print("\nSample organization names:")
for i, org in enumerate(organizations[:10]):
    print(f"{i+1}. {org['name']} ({org.get('country', 'Unknown')})")

# Analyze organization distribution by country
countries = {}
for org in organizations:
    country = org.get('country', 'Unknown')
    countries[country] = countries.get(country, 0) + 1

print(f"\nTop 10 countries by organization count:")
sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)
for country, count in sorted_countries[:10]:
    print(f"- {country}: {count} organizations")

# Check for organizations with existing scores
scored_orgs = 0
for org in organizations:
    if 'total_score' in org or 'score' in org:
        scored_orgs += 1

print(f"\nOrganizations with existing scores: {scored_orgs}")
print(f"Organizations needing new scoring: {len(organizations) - scored_orgs}")