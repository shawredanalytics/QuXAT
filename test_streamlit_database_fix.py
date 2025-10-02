#!/usr/bin/env python3
"""
Test Streamlit Database Fix

This script tests whether the Streamlit app now loads the correct database
file and can find Johns Hopkins Hospital with various search terms.

Author: QuXAT Development Team
Date: 2025-01-28
"""

import json
import sys
import os

def test_database_loading():
    """Test that the correct database file is loaded"""
    print("🔍 Testing Database Loading Fix")
    print("=" * 50)
    
    # Check if the correct database file exists
    correct_db = 'unified_healthcare_organizations_with_mayo_cap.json'
    old_db = 'unified_healthcare_organizations.json'
    
    print(f"📁 Checking database files:")
    
    if os.path.exists(correct_db):
        print(f"✅ {correct_db} exists")
        with open(correct_db, 'r', encoding='utf-8') as f:
            correct_data = json.load(f)
            if isinstance(correct_data, dict) and 'organizations' in correct_data:
                correct_orgs = correct_data['organizations']
            elif isinstance(correct_data, list):
                correct_orgs = correct_data
            else:
                correct_orgs = []
        print(f"   📊 Contains {len(correct_orgs)} organizations")
    else:
        print(f"❌ {correct_db} not found")
        return False
    
    if os.path.exists(old_db):
        print(f"📄 {old_db} exists")
        with open(old_db, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            if isinstance(old_data, dict) and 'organizations' in old_data:
                old_orgs = old_data['organizations']
            elif isinstance(old_data, list):
                old_orgs = old_data
            else:
                old_orgs = []
        print(f"   📊 Contains {len(old_orgs)} organizations")
    else:
        print(f"❌ {old_db} not found")
        old_orgs = []
    
    # Check for Johns Hopkins in both databases
    print(f"\n🏥 Searching for Johns Hopkins Hospital:")
    
    johns_hopkins_in_correct = False
    johns_hopkins_in_old = False
    
    # Search in correct database
    for org in correct_orgs:
        if isinstance(org, dict):
            org_name = org.get('name', '').lower()
            if 'johns hopkins' in org_name:
                johns_hopkins_in_correct = True
                print(f"✅ Found in {correct_db}: {org.get('name', 'Unknown')}")
                print(f"   🏆 Certifications: {len(org.get('certifications', []))}")
                print(f"   ⭐ Quality Score: {org.get('quality_score', 'N/A')}")
                break
    
    if not johns_hopkins_in_correct:
        print(f"❌ Johns Hopkins NOT found in {correct_db}")
    
    # Search in old database
    for org in old_orgs:
        if isinstance(org, dict):
            org_name = org.get('name', '').lower()
            if 'johns hopkins' in org_name:
                johns_hopkins_in_old = True
                print(f"📄 Found in {old_db}: {org.get('name', 'Unknown')}")
                break
    
    if not johns_hopkins_in_old:
        print(f"❌ Johns Hopkins NOT found in {old_db}")
    
    return johns_hopkins_in_correct

def simulate_streamlit_search():
    """Simulate the Streamlit app's search functionality"""
    print(f"\n🔍 Simulating Streamlit Search Logic")
    print("=" * 50)
    
    # Load the database the same way Streamlit does now
    try:
        with open('unified_healthcare_organizations_with_mayo_cap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extract organizations array from the JSON structure
            if isinstance(data, dict) and 'organizations' in data:
                database = data['organizations']
            elif isinstance(data, list):
                database = data
            else:
                database = []
    except FileNotFoundError:
        print("❌ Database file not found")
        return False
    
    print(f"📊 Loaded {len(database)} organizations")
    
    # Test search terms
    search_terms = [
        "john hopkins",           # The problematic search
        "johns hopkins",          # Correct spelling
        "Johns Hopkins Hospital", # Full name
        "JOHNS HOPKINS",          # All caps
    ]
    
    def search_unified_database(org_name):
        """Replicate Streamlit's search logic"""
        if not database:
            return None
            
        org_name_lower = org_name.lower().strip()
        
        # Direct name match
        for org in database:
            if not isinstance(org, dict):
                continue
            if org.get('name', '').lower() == org_name_lower:
                return org
        
        # Partial name match
        for org in database:
            if not isinstance(org, dict):
                continue
            org_name_db = org.get('name', '').lower()
            if org_name_lower in org_name_db or org_name_db in org_name_lower:
                return org
        
        # Search in original names for NABH organizations
        for org in database:
            if not isinstance(org, dict):
                continue
            original_name = org.get('original_name', '')
            if original_name:
                original_name_lower = original_name.lower()
                if org_name_lower in original_name_lower or original_name_lower in org_name_lower:
                    return org
        
        return None
    
    print(f"\n🧪 Testing Search Terms:")
    print("-" * 30)
    
    success_count = 0
    for search_term in search_terms:
        print(f"\n🔍 Searching for: '{search_term}'")
        result = search_unified_database(search_term)
        
        if result:
            print(f"✅ FOUND: {result.get('name', 'Unknown')}")
            print(f"   🏆 Certifications: {len(result.get('certifications', []))}")
            print(f"   ⭐ Quality Score: {result.get('quality_score', 'N/A')}")
            success_count += 1
        else:
            print(f"❌ NOT FOUND")
    
    print(f"\n📊 Search Results Summary:")
    print(f"   ✅ Successful searches: {success_count}/{len(search_terms)}")
    print(f"   📈 Success rate: {(success_count/len(search_terms)*100):.1f}%")
    
    # Special focus on the problematic search
    print(f"\n🎯 Focus Test: 'john hopkins' search")
    print("-" * 40)
    result = search_unified_database("john hopkins")
    if result:
        print(f"✅ SUCCESS: 'john hopkins' now finds Johns Hopkins Hospital!")
        print(f"   🏥 Organization: {result.get('name', 'Unknown')}")
        print(f"   🏆 Certifications: {len(result.get('certifications', []))}")
        
        # List certifications
        certs = result.get('certifications', [])
        if certs:
            print(f"   🔖 Certification Details:")
            for i, cert in enumerate(certs[:3], 1):  # Show first 3
                cert_type = cert.get('type', 'Unknown')
                print(f"      {i}. {cert_type}")
        
        return True
    else:
        print(f"❌ FAILED: 'john hopkins' still doesn't find Johns Hopkins Hospital")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Streamlit Database Fix for Johns Hopkins Hospital")
    print("=" * 70)
    
    # Test 1: Database loading
    db_test_passed = test_database_loading()
    
    # Test 2: Search simulation
    search_test_passed = simulate_streamlit_search()
    
    # Final summary
    print(f"\n" + "=" * 70)
    print(f"📋 FINAL TEST RESULTS")
    print(f"=" * 70)
    print(f"✅ Database Loading: {'PASSED' if db_test_passed else 'FAILED'}")
    print(f"✅ Search Functionality: {'PASSED' if search_test_passed else 'FAILED'}")
    
    if db_test_passed and search_test_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   The Streamlit app should now find Johns Hopkins Hospital")
        print(f"   when users search for 'john hopkins' (with missing 's')")
        print(f"\n📝 Next Steps:")
        print(f"   1. Restart the Streamlit app")
        print(f"   2. Test the search in the web interface")
        print(f"   3. Verify certification data is displayed")
    else:
        print(f"\n❌ TESTS FAILED!")
        print(f"   The issue may require additional investigation")
        
        if not db_test_passed:
            print(f"   - Database loading issue detected")
        if not search_test_passed:
            print(f"   - Search functionality issue detected")

if __name__ == "__main__":
    main()