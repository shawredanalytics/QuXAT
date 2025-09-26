import json

# Load the JSON file
with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total entries: {len(data)}")

# Find and fix Queens NRI Hospital at index 363
if len(data) > 363:
    entry = data[363]
    if "Queens NRI Hospital" in entry.get("name", ""):
        print(f"Found Queens NRI Hospital at index 363: {entry['name']}")
        
        # Check current quality indicators
        quality_indicators = entry.get('quality_indicators', {})
        print("Current quality indicators:")
        for key, value in quality_indicators.items():
            print(f"  {key}: {value}")
        
        # Check current scores
        total_score = entry.get('total_score', 'Not found')
        cert_score = entry.get('certification_score', 'Not found')
        print(f"Current total_score: {total_score}")
        print(f"Current certification_score: {cert_score}")
        
        # Fix the quality indicators
        if 'quality_indicators' in entry:
            entry['quality_indicators']['jci_accredited'] = False
            entry['quality_indicators']['international_accreditation'] = False
        
        # Add the missing score fields
        entry['total_score'] = 18
        entry['certification_score'] = 18
        
        print("\nFixed quality indicators:")
        for key, value in entry['quality_indicators'].items():
            print(f"  {key}: {value}")
        
        print(f"Fixed total_score: {entry['total_score']}")
        print(f"Fixed certification_score: {entry['certification_score']}")
        
        # Save the updated data
        with open('unified_healthcare_organizations.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Successfully updated Queens NRI Hospital entry at index 363")
    else:
        print(f"Entry at index 363 is not Queens NRI Hospital: {entry.get('name', 'Unknown')}")
else:
    print("Index 363 is out of range")