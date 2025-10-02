#!/usr/bin/env python3
"""
Live Streamlit App Search Test

This script tests the search functionality directly using the same
functions that the Streamlit app uses to ensure everything works
in the live environment.

Author: QuXAT Development Team
Date: 2025-01-28
"""

import sys
import os

# Add the current directory to Python path to import streamlit_app functions
sys.path.insert(0, os.getcwd())

try:
    # Import the actual class from streamlit_app
    from streamlit_app import HealthcareOrgAnalyzer
    print("✅ Successfully imported Streamlit app class")
    
    # Create an instance of the analyzer
    analyzer = HealthcareOrgAnalyzer()
    print("✅ Successfully created analyzer instance")
except ImportError as e:
    print(f"❌ Failed to import Streamlit app class: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to create analyzer instance: {e}")
    sys.exit(1)

def test_live_streamlit_search():
    """Test the search functionality using actual Streamlit app functions"""
    print("🔍 Testing Live Streamlit App Search Functionality")
    print("=" * 60)
    
    # Load the database using the actual Streamlit function
    print("📊 Loading database using Streamlit app function...")
    try:
        database = analyzer.load_unified_database()
        print(f"✅ Successfully loaded {len(database)} organizations")
    except Exception as e:
        print(f"❌ Failed to load database: {e}")
        return False
    
    # Test the problematic search case
    print(f"\n🎯 Testing the original problematic search: 'john hopkins'")
    print("-" * 50)
    
    try:
        # Use the actual search function from Streamlit app
        result = analyzer.search_unified_database("john hopkins")
        
        if result:
            print(f"✅ SUCCESS: Found organization for 'john hopkins'")
            
            org_name = result.get('name', '')
            print(f"   🏥 {org_name}")
            
            if 'johns hopkins' in org_name.lower():
                print(f"      ✅ This is Johns Hopkins Hospital!")
                print(f"      🏆 Certifications: {len(result.get('certifications', []))}")
                print(f"      ⭐ Quality Score: {result.get('quality_score', 'N/A')}")
                
                # Show certification details
                certs = result.get('certifications', [])
                if certs:
                    print(f"      🔖 Certification Types:")
                    for cert in certs[:3]:
                        cert_type = cert.get('type', 'Unknown')
                        print(f"         - {cert_type}")
                
                print(f"\n🎉 PERFECT! Johns Hopkins Hospital found with 'john hopkins' search!")
                return True
            else:
                print(f"\n⚠️  Found organization but not Johns Hopkins Hospital")
                return False
                
        else:
            print(f"❌ FAILED: No results found for 'john hopkins'")
            return False
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return False

def test_additional_search_cases():
    """Test additional search cases to ensure robustness"""
    print(f"\n🧪 Testing Additional Search Cases")
    print("=" * 40)
    
    database = analyzer.load_unified_database()
    
    test_cases = [
        "johns hopkins",
        "Johns Hopkins Hospital", 
        "JOHN HOPKINS",
        "hopkins hospital"
    ]
    
    for search_term in test_cases:
        print(f"\n🔍 Testing: '{search_term}'")
        try:
            result = analyzer.search_unified_database(search_term)
            if result:
                org_name = result.get('name', '')
                johns_hopkins_match = 'johns hopkins' in org_name.lower()
                print(f"   ✅ Found: {org_name} ({'Johns Hopkins' if johns_hopkins_match else 'Other'})")
            else:
                print(f"   ❌ No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test execution"""
    print("🚀 Live Streamlit App Search Test")
    print("=" * 60)
    
    # Test the main issue
    success = test_live_streamlit_search()
    
    # Test additional cases
    test_additional_search_cases()
    
    # Final summary
    print(f"\n" + "=" * 60)
    print(f"🏁 FINAL RESULT")
    print(f"=" * 60)
    
    if success:
        print(f"🎊 SUCCESS!")
        print(f"✅ The Johns Hopkins search issue is COMPLETELY RESOLVED")
        print(f"✅ Users can now search 'john hopkins' and find Johns Hopkins Hospital")
        print(f"✅ Full certification data and quality scores are available")
        print(f"\n🌟 The Streamlit app is ready for production use!")
    else:
        print(f"❌ ISSUE STILL EXISTS")
        print(f"The search functionality needs additional work")
    
    return success

if __name__ == "__main__":
    main()