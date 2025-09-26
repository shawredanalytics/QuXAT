import json

"""Debug script to find all Queens NRI Hospital entries and their quality indicators"""

# Load the JSON file
with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Searching for Queens NRI Hospital entries...")
print("=" * 60)

found_entries = []
for i, entry in enumerate(data):
    if "Queens NRI Hospital" in entry.get("name", ""):
        found_entries.append((i, entry))
        print(f"\nEntry #{len(found_entries)} (Index: {i}):")
        print(f"Name: {entry.get('name', 'N/A')}")
        print(f"Line position in file: ~{i * 20 + 1}")  # Rough estimate
        
        # Check quality indicators
        quality_indicators = entry.get('quality_indicators', {})
        print("Quality Indicators:")
        for key, value in quality_indicators.items():
            print(f"  {key}: {value}")
        
        # Check scores
        total_score = entry.get('total_score', 'Not found')
        cert_score = entry.get('certification_score', 'Not found')
        print(f"Total Score: {total_score}")
        print(f"Certification Score: {cert_score}")
        
        # Check certifications
        certifications = entry.get('certifications', [])
        print(f"Certifications ({len(certifications)}):")
        for cert in certifications:
            print(f"  - {cert.get('name', 'Unknown')}")

print(f"\nTotal entries found: {len(found_entries)}")

# Also check if there are any entries with similar names
print("\n" + "=" * 60)
print("Checking for similar entries...")
similar_entries = []
for i, entry in enumerate(data):
    name = entry.get("name", "").lower()
    if "queens" in name and "nri" in name and i not in [idx for idx, _ in found_entries]:
        similar_entries.append((i, entry))
        print(f"Similar entry at index {i}: {entry.get('name', 'N/A')}")

print(f"Similar entries found: {len(similar_entries)}")