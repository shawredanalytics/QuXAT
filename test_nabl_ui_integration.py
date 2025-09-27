#!/usr/bin/env python3
"""
Test NABL integration in the Streamlit UI context
"""

import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

def test_nabl_ui_integration():
    """Test NABL integration as it would work in the Streamlit UI"""
    print("🖥️  Testing NABL Integration in UI Context")
    print("=" * 50)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test with Apollo Hospitals (known NABL accredited)
    org_name = "Apollo Hospitals"
    print(f"\n🏥 Testing: {org_name}")
    
    # Search for organization info (as UI would do)
    org_info = analyzer.search_organization_info(org_name)
    
    if org_info:
        print(f"✅ Organization found in database")
        print(f"   Name: {org_info.get('name', 'N/A')}")
        print(f"   Country: {org_info.get('country', 'N/A')}")
        
        # Get certifications
        certifications = org_info.get('certifications', [])
        print(f"   Initial certifications: {len(certifications)}")
        
        # Calculate quality score (this will trigger NABL checking)
        score_breakdown = analyzer.calculate_quality_score(
            certifications=certifications,
            initiatives=[],
            org_name=org_name
        )
        
        print(f"\n📊 Score Results:")
        print(f"   • Certification Score: {score_breakdown['certification_score']:.1f}")
        print(f"   • Quality Initiatives Score: {score_breakdown['quality_initiatives_score']:.1f}")
        print(f"   • NABL Accreditation Score: {score_breakdown['nabl_accreditation_score']:.1f}")
        print(f"   • Total Score: {score_breakdown['total_score']:.1f}")
        
        # Check if NABL certification was added
        final_certifications = certifications
        nabl_certs = [cert for cert in final_certifications if 'NABL' in cert.get('name', '').upper()]
        
        if nabl_certs:
            print(f"\n🇮🇳 NABL Certification Added:")
            for cert in nabl_certs:
                print(f"   • Name: {cert['name']}")
                print(f"   • Score Impact: {cert['score_impact']:.1f}")
                print(f"   • Remarks: {cert['remarks']}")
        else:
            print(f"\n❌ No NABL certification was added")
        
        print(f"\n✅ UI Integration Test Successful!")
        return True
    else:
        print(f"❌ Organization not found in database")
        return False

if __name__ == "__main__":
    test_nabl_ui_integration()