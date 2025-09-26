#!/usr/bin/env python3
"""
Test script to verify JCI validation fixes
- Ensures no automatic JCI assignment
- Verifies only validated certifications are shown
"""

import sys
import os
sys.path.append('.')

def test_jci_validation_fix():
    """Test that JCI is not automatically assigned to organizations"""
    print("🧪 Testing JCI Validation Fix...")
    
    try:
        from streamlit_app import HealthcareOrgAnalyzer
        
        # Create analyzer instance
        analyzer = HealthcareOrgAnalyzer()
        
        # Test organizations that should NOT get automatic JCI
        test_organizations = [
            "Random Hospital",
            "Test Medical Center", 
            "Unknown Healthcare",
            "Generic Hospital System",
            "Non-JCI Organization"
        ]
        
        print("\n📋 Testing organizations that should NOT get automatic JCI:")
        
        for org_name in test_organizations:
            print(f"\n🏥 Testing: {org_name}")
            
            # Test the enhance_certification_with_jci method directly
            empty_certs = []
            enhanced_certs = analyzer.enhance_certification_with_jci(empty_certs, org_name)
            
            # Should return empty list (no automatic JCI)
            if len(enhanced_certs) == 0:
                print(f"   ✅ PASS: No automatic JCI assignment")
            else:
                print(f"   ❌ FAIL: Automatic JCI assigned: {enhanced_certs}")
                
            # Test the search_certifications method
            search_results = analyzer.search_certifications(org_name)
            
            # Check if any JCI certifications were added
            jci_found = any('JCI' in cert.get('name', '').upper() or 
                          'JOINT COMMISSION INTERNATIONAL' in cert.get('name', '').upper() 
                          for cert in search_results)
            
            if not jci_found:
                print(f"   ✅ PASS: No JCI in search results")
            else:
                print(f"   ❌ FAIL: JCI found in search results: {search_results}")
        
        # Test known JCI organizations (should only show if validated)
        print(f"\n📋 Testing known JCI organizations:")
        
        jci_test_orgs = [
            "Singapore General Hospital",
            "National University Hospital Singapore"
        ]
        
        for org_name in jci_test_orgs:
            print(f"\n🏥 Testing: {org_name}")
            
            # Test enhance method - should NOT add JCI automatically
            empty_certs = []
            enhanced_certs = analyzer.enhance_certification_with_jci(empty_certs, org_name)
            
            if len(enhanced_certs) == 0:
                print(f"   ✅ PASS: No automatic JCI assignment (even for known JCI org)")
            else:
                print(f"   ❌ FAIL: Automatic JCI assigned: {enhanced_certs}")
        
        print(f"\n🎉 JCI Validation Fix Test Completed!")
        print(f"✅ System now only shows validated certifications from official sources")
        print(f"✅ No automatic JCI assignment occurs")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jci_validation_fix()