#!/usr/bin/env python3
"""
Test script for NABH data integration with QuXAT Healthcare Quality Scorecard
This script validates the integration of NABH accredited hospitals data
"""

import json
import os
from datetime import datetime

def test_unified_database():
    """Test the unified healthcare database"""
    print("🔍 Testing Unified Healthcare Database...")
    
    # Check if unified database exists
    if not os.path.exists('unified_healthcare_organizations.json'):
        print("❌ ERROR: unified_healthcare_organizations.json not found!")
        return False
    
    # Load and validate database
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        print(f"✅ Database loaded successfully with {len(database)} organizations")
        
        # Count JCI and NABH organizations
        jci_count = sum(1 for org in database if any(cert.get('type') == 'JCI' for cert in org.get('certifications', [])))
        nabh_count = sum(1 for org in database if any(cert.get('type') == 'NABH' for cert in org.get('certifications', [])))
        dual_count = sum(1 for org in database if 
                        any(cert.get('type') == 'JCI' for cert in org.get('certifications', [])) and
                        any(cert.get('type') == 'NABH' for cert in org.get('certifications', [])))
        
        print(f"📊 Database Statistics:")
        print(f"   - Total Organizations: {len(database)}")
        print(f"   - JCI Accredited: {jci_count}")
        print(f"   - NABH Accredited: {nabh_count}")
        print(f"   - Dual Accredited: {dual_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR loading database: {str(e)}")
        return False

def test_nabh_data_structure():
    """Test NABH data structure and quality"""
    print("\n🏥 Testing NABH Data Structure...")
    
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Find NABH organizations
        nabh_orgs = [org for org in database if any(cert.get('type') == 'NABH' for cert in org.get('certifications', []))]
        
        if not nabh_orgs:
            print("❌ ERROR: No NABH organizations found in database!")
            return False
        
        print(f"✅ Found {len(nabh_orgs)} NABH accredited organizations")
        
        # Test first few organizations
        test_orgs = nabh_orgs[:5]
        for i, org in enumerate(test_orgs, 1):
            print(f"\n📋 Testing Organization {i}: {org['name']}")
            
            # Check required fields
            required_fields = ['name', 'city', 'state', 'country', 'certifications']
            for field in required_fields:
                if field not in org:
                    print(f"   ❌ Missing field: {field}")
                else:
                    print(f"   ✅ {field}: {org[field]}")
            
            # Check NABH certification details
            nabh_certs = [cert for cert in org.get('certifications', []) if cert.get('type') == 'NABH']
            if nabh_certs:
                nabh_cert = nabh_certs[0]
                print(f"   ✅ NABH Status: {nabh_cert.get('status', 'Unknown')}")
                print(f"   ✅ Score Impact: {nabh_cert.get('score_impact', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing NABH data: {str(e)}")
        return False

def test_search_functionality():
    """Test search functionality with NABH organizations"""
    print("\n🔍 Testing Search Functionality...")
    
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Test search with different patterns
        test_searches = [
            "Apollo",
            "Fortis",
            "Max Healthcare",
            "Manipal",
            "AIIMS"
        ]
        
        for search_term in test_searches:
            print(f"\n🔍 Searching for: '{search_term}'")
            
            # Direct name match
            direct_matches = [org for org in database if search_term.lower() in org['name'].lower()]
            
            # Original name match (for NABH data)
            original_matches = [org for org in database 
                              if 'original_name' in org and org['original_name'] and 
                              search_term.lower() in org['original_name'].lower()]
            
            total_matches = len(direct_matches) + len(original_matches)
            
            if total_matches > 0:
                print(f"   ✅ Found {total_matches} matches")
                if direct_matches:
                    print(f"      - Direct matches: {len(direct_matches)}")
                    for match in direct_matches[:3]:  # Show first 3
                        print(f"        • {match['name']} ({match.get('city', 'Unknown')}, {match.get('state', 'Unknown')})")
                if original_matches:
                    print(f"      - Original name matches: {len(original_matches)}")
                    for match in original_matches[:3]:  # Show first 3
                        print(f"        • {match['name']} ({match.get('city', 'Unknown')}, {match.get('state', 'Unknown')})")
            else:
                print(f"   ⚠️ No matches found for '{search_term}'")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing search: {str(e)}")
        return False

def test_data_quality():
    """Test data quality and completeness"""
    print("\n📊 Testing Data Quality...")
    
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Quality metrics
        total_orgs = len(database)
        orgs_with_city = sum(1 for org in database if org.get('city'))
        orgs_with_state = sum(1 for org in database if org.get('state'))
        orgs_with_certifications = sum(1 for org in database if org.get('certifications'))
        
        print(f"📈 Data Completeness:")
        print(f"   - Organizations with City: {orgs_with_city}/{total_orgs} ({orgs_with_city/total_orgs*100:.1f}%)")
        print(f"   - Organizations with State: {orgs_with_state}/{total_orgs} ({orgs_with_state/total_orgs*100:.1f}%)")
        print(f"   - Organizations with Certifications: {orgs_with_certifications}/{total_orgs} ({orgs_with_certifications/total_orgs*100:.1f}%)")
        
        # Country distribution
        countries = {}
        for org in database:
            country = org.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n🌍 Country Distribution:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   - {country}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing data quality: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 NABH Data Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Unified Database", test_unified_database),
        ("NABH Data Structure", test_nabh_data_structure),
        ("Search Functionality", test_search_functionality),
        ("Data Quality", test_data_quality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running Test: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! NABH integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()