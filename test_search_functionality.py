#!/usr/bin/env python3
"""
Test script to verify the organization search functionality
This will help identify why the search bar is not working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_search_functionality():
    """Test the organization search functionality with various inputs"""
    print("=== Testing Organization Search Functionality ===\n")
    
    # Initialize the analyzer
    try:
        analyzer = HealthcareOrgAnalyzer()
        print("✅ HealthcareOrgAnalyzer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    # Test organizations to search for
    test_organizations = [
        "Mayo Clinic",
        "Apollo Hospitals",
        "Fortis Healthcare",
        "Johns Hopkins",
        "Cleveland Clinic",
        "AIIMS Delhi",
        "Max Healthcare",
        "Manipal Hospitals"
    ]
    
    print(f"\n🔍 Testing search functionality with {len(test_organizations)} organizations...\n")
    
    successful_searches = 0
    failed_searches = 0
    
    for org_name in test_organizations:
        print(f"Searching for: {org_name}")
        try:
            # Test the search_organization_info method
            result = analyzer.search_organization_info(org_name)
            
            if result:
                print(f"  ✅ Found: {result.get('name', 'Unknown')} - Score: {result.get('total_score', 0):.1f}")
                successful_searches += 1
            else:
                print(f"  ⚠️  No data found for: {org_name}")
                failed_searches += 1
                
        except Exception as e:
            print(f"  ❌ Error searching for {org_name}: {e}")
            failed_searches += 1
        
        print()
    
    # Test suggestion generation
    print("🔍 Testing suggestion generation...\n")
    
    test_queries = ["Mayo", "Apollo", "Fortis", "Johns", "AIIMS"]
    
    for query in test_queries:
        print(f"Generating suggestions for: '{query}'")
        try:
            suggestions = analyzer.generate_organization_suggestions(query, max_suggestions=5)
            if suggestions:
                print(f"  ✅ Found {len(suggestions)} suggestions:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    display_name = suggestion.get('display_name', 'Unknown')
                    print(f"    {i}. {display_name}")
            else:
                print(f"  ⚠️  No suggestions found for: '{query}'")
        except Exception as e:
            print(f"  ❌ Error generating suggestions for '{query}': {e}")
        print()
    
    # Test database connectivity
    print("🔍 Testing database connectivity...\n")
    
    try:
        # Check if unified database is accessible
        if hasattr(analyzer, 'unified_db') and analyzer.unified_db:
            print(f"  ✅ Unified database loaded with {len(analyzer.unified_db)} organizations")
        else:
            print("  ⚠️  Unified database not loaded or empty")
            
        # Check NABH database
        if hasattr(analyzer, 'nabh_db') and analyzer.nabh_db:
            print(f"  ✅ NABH database loaded with {len(analyzer.nabh_db)} organizations")
        else:
            print("  ⚠️  NABH database not loaded or empty")
            
        # Check NABL database
        if hasattr(analyzer, 'nabl_db') and analyzer.nabl_db:
            print(f"  ✅ NABL database loaded with {len(analyzer.nabl_db)} organizations")
        else:
            print("  ⚠️  NABL database not loaded or empty")
            
    except Exception as e:
        print(f"  ❌ Error checking database connectivity: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("SEARCH FUNCTIONALITY TEST SUMMARY")
    print("="*50)
    print(f"✅ Successful searches: {successful_searches}")
    print(f"❌ Failed searches: {failed_searches}")
    print(f"📊 Success rate: {(successful_searches/(successful_searches+failed_searches)*100):.1f}%")
    
    if successful_searches > 0:
        print("\n✅ Search functionality is working - organizations can be found")
        if failed_searches > 0:
            print("⚠️  Some organizations not found in database (this is normal)")
    else:
        print("\n❌ Search functionality appears to be broken - no organizations found")
        print("🔧 This indicates a potential issue with database loading or search logic")
    
    return successful_searches > 0

if __name__ == "__main__":
    test_search_functionality()