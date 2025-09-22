"""
Test script for full JCI integration with the QuXAT scoring system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_full_integration():
    print("🧪 Testing Full JCI Integration with QuXAT Scoring System...")
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test organizations with different JCI statuses
    test_organizations = [
        "Singapore General Hospital",  # JCI accredited
        "Apollo Hospitals",           # JCI accredited (partial match)
        "Mayo Clinic",               # Not in JCI database
        "Cleveland Clinic"           # Not in JCI database
    ]
    
    for org_name in test_organizations:
        print(f"\n{'='*60}")
        print(f"🏥 Testing: {org_name}")
        print(f"{'='*60}")
        
        # Search for certifications
        certifications = analyzer.search_certifications(org_name)
        
        if certifications:
            print(f"✅ Found {len(certifications)} certifications:")
            for cert in certifications:
                print(f"   - {cert.get('name', 'Unknown')}: {cert.get('status', 'Unknown')} ({cert.get('score_impact', 0)} points)")
                if cert.get('name') == 'JCI' and 'organization_info' in cert:
                    org_info = cert['organization_info']
                    print(f"     🌟 JCI Details: {org_info.get('country', 'N/A')}, Accredited: {org_info.get('accreditation_date', 'N/A')}")
            
            # Calculate quality score
            initiatives = [
                {'name': 'Patient Safety Initiative', 'impact_score': 8},
                {'name': 'Digital Health Program', 'impact_score': 6}
            ]
            
            score_breakdown = analyzer.calculate_quality_score(certifications, initiatives, org_name)
            
            print(f"\n📊 Quality Score Breakdown:")
            print(f"   - Certification Score: {score_breakdown['certification_score']}/50")
            print(f"   - Initiative Score: {score_breakdown['initiative_score']}/15")
            print(f"   - Transparency Score: {score_breakdown['transparency_score']}/15")
            print(f"   - Reputation Bonus: {score_breakdown['reputation_bonus']}/10")
            print(f"   - TOTAL SCORE: {score_breakdown['total_score']}/85")
            
            # Determine grade
            total_score = score_breakdown['total_score']
            if total_score >= 75:
                grade = "A+"
            elif total_score >= 65:
                grade = "A"
            elif total_score >= 55:
                grade = "B+"
            elif total_score >= 45:
                grade = "B"
            else:
                grade = "C"
            
            print(f"   - GRADE: {grade}")
            
        else:
            print("❌ No certifications found")
    
    print(f"\n{'='*60}")
    print("🎉 Full Integration Test Completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_full_integration()