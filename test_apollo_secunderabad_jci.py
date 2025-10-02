#!/usr/bin/env python3
"""
Test script to check Apollo Hospitals Secunderabad JCI accreditation status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_apollo_secunderabad_jci():
    """Test Apollo Hospitals Secunderabad JCI accreditation status"""
    
    print("🔍 Testing Apollo Hospitals Secunderabad JCI Status")
    print("=" * 60)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Search for Apollo Hospitals Secunderabad using the correct method
    result = analyzer.search_organization_info('Apollo Hospitals Secunderabad')
    
    if result:
        print(f"\n✅ Found Apollo Hospitals Secunderabad:")
        print(f"   Name: {result.get('name', 'N/A')}")
        print(f"   Original Name: {result.get('original_name', 'N/A')}")
        print(f"   City: {result.get('city', 'N/A')}")
        print(f"   State: {result.get('state', 'N/A')}")
        
        # Check quality indicators
        quality_indicators = result.get('quality_indicators', {})
        jci_accredited = quality_indicators.get('jci_accredited', False)
        print(f"   JCI Accredited (Quality Indicator): {jci_accredited}")
        
        # Check certifications
        certifications = result.get('certifications', [])
        print(f"   Total Certifications: {len(certifications)}")
        
        # Look for JCI certifications specifically
        jci_certs = [cert for cert in certifications if 'JCI' in cert.get('name', '').upper() or 'JOINT COMMISSION' in cert.get('name', '').upper()]
        if jci_certs:
            print(f"   🚨 JCI Certifications Found:")
            for cert in jci_certs:
                print(f"      - Name: {cert.get('name', 'Unknown')}")
                print(f"        Type: {cert.get('type', 'Unknown')}")
                print(f"        Status: {cert.get('status', 'Unknown')}")
                print(f"        Source: {cert.get('source', 'Unknown')}")
                print(f"        Score Impact: {cert.get('score_impact', 0)}")
        else:
            print(f"   ✅ No JCI Certifications Found")
        
        print(f"\n   All Certifications:")
        for i, cert in enumerate(certifications, 1):
            cert_name = cert.get('name', 'Unknown')
            cert_type = cert.get('type', 'Unknown')
            cert_source = cert.get('source', 'Unknown')
            print(f"      {i}. {cert_name} ({cert_type}) - Source: {cert_source}")
        
        print("\n" + "=" * 60)
    else:
        print("❌ Apollo Hospitals Secunderabad not found in database")

if __name__ == "__main__":
    test_apollo_secunderabad_jci()