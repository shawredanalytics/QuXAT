#!/usr/bin/env python3
"""
Test script to check case sensitivity issues with Mayo clinic search
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_mayo_case_variations():
    """Test different case variations of Mayo clinic"""
    
    print("=" * 60)
    print("MAYO CLINIC CASE SENSITIVITY TEST")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test different case variations
    test_cases = [
        "Mayo Clinic",
        "mayo clinic", 
        "Mayo clinic",
        "MAYO CLINIC",
        "mayo Clinic",
        "Mayo CLINIC"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{test_case}'")
        print("-" * 40)
        
        try:
            # Test search_organization_info
            result = analyzer.search_organization_info(test_case)
            
            if result:
                print(f"✅ FOUND in database")
                print(f"   Organization: {result.get('organization_name', 'N/A')}")
                print(f"   Total Score: {result.get('total_score', 'N/A')}")
                print(f"   Location: {result.get('location', 'N/A')}")
            else:
                print(f"❌ NOT FOUND in database")
                
            # Test suggestions
            suggestions = analyzer.generate_organization_suggestions(test_case, max_suggestions=3)
            print(f"   Suggestions found: {len(suggestions)}")
            if suggestions:
                for j, suggestion in enumerate(suggestions[:2], 1):
                    print(f"     {j}. {suggestion.get('display_name', 'N/A')}")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("DATABASE SEARCH TEST")
    print("=" * 60)
    
    # Check what's actually in the database
    try:
        # Load the unified database
        import json
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        mayo_entries = []
        for org in database:
            org_name = org.get('organization_name', '').lower()
            if 'mayo' in org_name:
                mayo_entries.append({
                    'name': org.get('organization_name', ''),
                    'location': org.get('location', ''),
                    'type': org.get('organization_type', '')
                })
        
        print(f"\nFound {len(mayo_entries)} Mayo entries in database:")
        for i, entry in enumerate(mayo_entries, 1):
            print(f"{i}. {entry['name']}")
            print(f"   Location: {entry['location']}")
            print(f"   Type: {entry['type']}")
            print()
            
    except Exception as e:
        print(f"Error loading database: {e}")

if __name__ == "__main__":
    test_mayo_case_variations()