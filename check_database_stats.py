#!/usr/bin/env python3
"""
Check Database Statistics
This script analyzes the current unified database to understand its contents.
"""

import json
from collections import Counter

def analyze_database():
    """Analyze the unified healthcare organizations database."""
    print("🔍 Analyzing Current Database...")
    print("=" * 60)
    
    try:
        with open("unified_healthcare_organizations.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        organizations = data.get("organizations", [])
        total_orgs = len(organizations)
        
        print(f"📊 Total Organizations: {total_orgs}")
        
        # Count by data source
        sources = Counter()
        countries = Counter()
        hospital_types = Counter()
        certification_types = Counter()
        
        nabh_count = 0
        nabl_count = 0
        jci_count = 0
        dental_count = 0
        apollo_count = 0
        
        for org in organizations:
            # Handle both dict and string objects
            if isinstance(org, str):
                continue
                
            # Data source
            source = org.get("data_source", "Unknown")
            sources[source] += 1
            
            # Country
            country = org.get("country", "Unknown")
            countries[country] += 1
            
            # Hospital type
            hospital_type = org.get("hospital_type", "Unknown")
            hospital_types[hospital_type] += 1
            
            # Check for specific organizations
            name = org.get("name", "").lower()
            if "apollo" in name:
                apollo_count += 1
            if "dental" in name or "dental" in hospital_type.lower():
                dental_count += 1
            
            # Certifications
            certifications = org.get("certifications", [])
            for cert in certifications:
                if isinstance(cert, dict):
                    cert_type = cert.get("type", "Unknown")
                    certification_types[cert_type] += 1
                    
                    if "nabh" in cert_type.lower():
                        nabh_count += 1
                    elif "nabl" in cert_type.lower():
                        nabl_count += 1
                    elif "jci" in cert_type.lower():
                        jci_count += 1
        
        print(f"\n🏥 Organization Breakdown:")
        print(f"   NABH Accredited: {nabh_count}")
        print(f"   NABL Accredited: {nabl_count}")
        print(f"   JCI Accredited: {jci_count}")
        print(f"   Apollo Hospitals: {apollo_count}")
        print(f"   Dental Facilities: {dental_count}")
        
        print(f"\n🌍 Top Countries:")
        for country, count in countries.most_common(5):
            print(f"   {country}: {count}")
        
        print(f"\n📋 Data Sources:")
        for source, count in sources.most_common():
            print(f"   {source}: {count}")
        
        print(f"\n🏥 Hospital Types (Top 10):")
        for htype, count in hospital_types.most_common(10):
            print(f"   {htype}: {count}")
        
        print(f"\n📜 Certification Types:")
        for cert_type, count in certification_types.most_common():
            print(f"   {cert_type}: {count}")
        
        # Sample organizations
        print(f"\n📝 Sample Organizations (First 5):")
        for i, org in enumerate(organizations[:5]):
            name = org.get("name", "Unknown")
            country = org.get("country", "Unknown")
            source = org.get("data_source", "Unknown")
            print(f"   {i+1}. {name} ({country}) - Source: {source}")
        
        return {
            "total_organizations": total_orgs,
            "nabh_count": nabh_count,
            "nabl_count": nabl_count,
            "jci_count": jci_count,
            "apollo_count": apollo_count,
            "dental_count": dental_count,
            "sources": dict(sources),
            "countries": dict(countries.most_common(10)),
            "hospital_types": dict(hospital_types.most_common(10))
        }
        
    except FileNotFoundError:
        print("❌ Database file not found!")
        return None
    except Exception as e:
        print(f"❌ Error analyzing database: {str(e)}")
        return None

if __name__ == "__main__":
    stats = analyze_database()
    if stats:
        print(f"\n✅ Database analysis completed!")
        print(f"📄 Current database contains {stats['total_organizations']} organizations")
    else:
        print("❌ Database analysis failed!")