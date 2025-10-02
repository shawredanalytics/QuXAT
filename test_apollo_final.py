#!/usr/bin/env python3
"""
Final test to verify Apollo Hospitals Chennai scoring after penalty system fix
"""

from streamlit_app import HealthcareOrgAnalyzer

def test_apollo_final():
    print("=== APOLLO HOSPITALS CHENNAI - FINAL SCORING TEST ===")
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Get Apollo Hospitals Chennai data
    result = analyzer.search_organization_info('Apollo Hospitals Chennai')
    
    if not result:
        print("❌ Apollo Hospitals Chennai not found")
        return
    
    print("✅ Apollo Hospitals Chennai found")
    print(f"Name: {result.get('name')}")
    print(f"Total Score: {result.get('total_score')}")
    print(f"Country: {result.get('country')}")
    print(f"City: {result.get('city')}")
    
    # Check certifications
    certifications = result.get('certifications', [])
    print(f"\nCertifications: {len(certifications)} found")
    for cert in certifications:
        print(f"  - {cert.get('name')}: {cert.get('status')} (Impact: {cert.get('score_impact')})")
    
    # Check score breakdown
    score_breakdown = result.get('score_breakdown', {})
    print(f"\nScore Breakdown:")
    print(f"  Certification Score: {score_breakdown.get('certification_score')}")
    print(f"  Initiative Score: {score_breakdown.get('initiative_score')}")
    print(f"  Total Score: {score_breakdown.get('total_score')}")
    print(f"  Mandatory Penalty: {score_breakdown.get('mandatory_penalty')}")
    
    # Check penalty details
    penalty_breakdown = score_breakdown.get('penalty_breakdown', {})
    if penalty_breakdown:
        print(f"\nPenalty Breakdown:")
        for category, penalty in penalty_breakdown.items():
            print(f"  {category}: -{penalty} points")
    
    # Check missing critical standards
    missing_critical = score_breakdown.get('missing_critical_standards', [])
    if missing_critical:
        print(f"\nMissing Critical Standards:")
        for std in missing_critical:
            print(f"  {std.get('standard')}: -{std.get('penalty')} points ({std.get('impact')})")
    
    # Check warnings
    cap_warning = score_breakdown.get('cap_warning')
    if cap_warning:
        print(f"\nWarning: {cap_warning}")
    
    print(f"\n🎯 FINAL RESULT: Apollo Hospitals Chennai scored {result.get('total_score')}/100")

if __name__ == "__main__":
    test_apollo_final()