#!/usr/bin/env python3
"""
Quick test for 'john hopkins' search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_john_hopkins_search():
    """Test 'john hopkins' search specifically"""
    print("🔍 Testing 'john hopkins' Search")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Load database
    print("📊 Loading unified database...")
    analyzer.load_unified_database()
    
    if not analyzer.unified_database:
        print("❌ Failed to load database")
        return False
    
    print(f"✅ Database loaded with {len(analyzer.unified_database)} organizations")
    
    # Test 'john hopkins' search
    print("\n🧪 Testing 'john hopkins' search...")
    
    try:
        result = analyzer.search_unified_database('john hopkins')
        
        if result:
            org_name = result.get('name', '')
            city = result.get('city', '')
            state = result.get('state', '')
            certifications = result.get('certifications', [])
            
            print(f"✅ Found: {org_name}")
            if city or state:
                print(f"   📍 Location: {city}, {state}")
            print(f"   🏆 Certifications: {len(certifications)} found")
            
            # Show some certifications
            if certifications:
                print("   📋 Sample certifications:")
                for i, cert in enumerate(certifications[:3], 1):
                    cert_type = cert.get('type', 'Unknown')
                    cert_status = cert.get('status', 'Unknown')
                    print(f"      {i}. {cert_type} - {cert_status}")
            
            print("\n🎉 SUCCESS: 'john hopkins' search is working correctly!")
            return True
        else:
            print("❌ No result found for 'john hopkins'")
            return False
            
    except Exception as e:
        print(f"❌ Error searching for 'john hopkins': {str(e)}")
        return False

if __name__ == "__main__":
    success = test_john_hopkins_search()
    sys.exit(0 if success else 1)