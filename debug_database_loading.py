#!/usr/bin/env python3
"""
Debug script to test database loading and search functionality
"""

import json
import os
import sys

def test_database_loading():
    """Test if the database files can be loaded properly"""
    print("=== Database Loading Debug Test ===\n")
    
    # Check if files exist
    files_to_check = [
        'unified_healthcare_organizations.json',
        'nabh_hospitals.json',
        'nabl_validation_results_20250926_165607.json'
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {filename} exists")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        print(f"   📊 Contains {len(data)} records")
                        if len(data) > 0:
                            print(f"   📝 Sample record keys: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"   📊 Contains {len(data)} keys")
                        print(f"   📝 Top-level keys: {list(data.keys())[:5]}")
                    else:
                        print(f"   ⚠️  Unexpected data type: {type(data)}")
            except Exception as e:
                print(f"   ❌ Error loading {filename}: {e}")
        else:
            print(f"❌ {filename} not found")
        print()
    
    # Test unified database loading specifically
    print("🔍 Testing unified database loading...")
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            unified_data = json.load(f)
            
        print(f"✅ Unified database loaded successfully")
        print(f"📊 Total organizations: {len(unified_data)}")
        
        # Test search functionality
        test_names = ["Mayo", "Apollo", "Fortis", "Johns Hopkins"]
        
        print("\n🔍 Testing search functionality...")
        for test_name in test_names:
            matches = []
            test_name_lower = test_name.lower()
            
            for org in unified_data:
                org_name = org.get('name', '').lower()
                if test_name_lower in org_name:
                    matches.append(org.get('name', ''))
            
            if matches:
                print(f"✅ '{test_name}' found {len(matches)} matches:")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"   - {match}")
            else:
                print(f"⚠️  '{test_name}' - no matches found")
        
        # Test suggestion generation logic
        print("\n🔍 Testing suggestion generation logic...")
        partial_input = "Mayo"
        partial_lower = partial_input.lower().strip()
        suggestions = []
        
        for org in unified_data:
            org_name = org.get('name', '')
            if org_name.lower().startswith(partial_lower):
                suggestions.append({
                    'display_name': org_name,
                    'match_type': 'name_start'
                })
            elif partial_lower in org_name.lower():
                suggestions.append({
                    'display_name': org_name,
                    'match_type': 'name_contains'
                })
        
        print(f"✅ Generated {len(suggestions)} suggestions for '{partial_input}':")
        for suggestion in suggestions[:5]:
            print(f"   - {suggestion['display_name']} ({suggestion['match_type']})")
            
    except Exception as e:
        print(f"❌ Error testing unified database: {e}")
    
    print("\n" + "="*50)
    print("DATABASE LOADING TEST SUMMARY")
    print("="*50)

def test_analyzer_initialization():
    """Test the HealthcareOrgAnalyzer initialization"""
    print("\n🔍 Testing HealthcareOrgAnalyzer initialization...")
    
    try:
        # Import without Streamlit context
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Mock streamlit functions to avoid errors
        import streamlit as st
        
        # Create a simple mock for st functions
        class MockST:
            def warning(self, msg): print(f"WARNING: {msg}")
            def error(self, msg): print(f"ERROR: {msg}")
            def success(self, msg): print(f"SUCCESS: {msg}")
        
        # Replace st with mock
        import streamlit_app
        streamlit_app.st = MockST()
        
        from streamlit_app import HealthcareOrgAnalyzer
        
        analyzer = HealthcareOrgAnalyzer()
        
        print("✅ HealthcareOrgAnalyzer initialized successfully")
        
        # Check if databases are loaded
        if hasattr(analyzer, 'unified_database') and analyzer.unified_database:
            print(f"✅ Unified database loaded: {len(analyzer.unified_database)} organizations")
        else:
            print("❌ Unified database not loaded or empty")
            
        # Test search method
        test_org = "Mayo Clinic"
        print(f"\n🔍 Testing search for '{test_org}'...")
        result = analyzer.search_organization_info(test_org)
        
        if result:
            print(f"✅ Search successful: {result.get('name', 'Unknown')}")
            print(f"   Score: {result.get('total_score', 0)}")
            print(f"   Certifications: {len(result.get('certifications', []))}")
        else:
            print(f"⚠️  No results found for '{test_org}'")
            
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_loading()
    test_analyzer_initialization()