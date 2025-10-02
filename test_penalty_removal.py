#!/usr/bin/env python3
"""
Test script to verify that compliance penalties have been removed from the scoring model.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_penalty_removal():
    """Test that compliance penalties are no longer applied to scores."""
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test with Mayo Clinic - should have no compliance penalty
    print("Testing Mayo Clinic scoring without compliance penalties...")
    
    # Get Mayo Clinic data
    mayo_result = analyzer.search_organization_info("Mayo Clinic")
    
    if isinstance(mayo_result, dict) and 'organizations' in mayo_result:
        mayo_data = mayo_result['organizations'][0]
        
        # Calculate score
        score_breakdown = analyzer.calculate_quality_score(
            mayo_data.get('certifications', []),
            mayo_data.get('quality_initiatives', [])
        )
        
        print(f"\nMayo Clinic Score Breakdown:")
        print(f"- Certification Score: {score_breakdown.get('certification_score', 0)}")
        print(f"- Quality Initiatives Score: {score_breakdown.get('quality_initiatives_score', 0)}")
        print(f"- Total Score: {score_breakdown.get('total_score', 0)}")
        
        # Check that compliance_penalty is not in the breakdown
        if 'compliance_penalty' in score_breakdown:
            print(f"❌ ERROR: compliance_penalty still found in score breakdown: {score_breakdown['compliance_penalty']}")
            return False
        else:
            print("✅ SUCCESS: compliance_penalty removed from score breakdown")
        
        # Check compliance status
        compliance_check = score_breakdown.get('compliance_check', {})
        print(f"\nCompliance Status:")
        print(f"- Is Fully Compliant: {compliance_check.get('is_fully_compliant', 'N/A')}")
        print(f"- Non-compliant Count: {compliance_check.get('non_compliant_count', 0)}")
        print(f"- Total Required: {compliance_check.get('total_required', 0)}")
        
        return True
    else:
        print("❌ ERROR: Could not find Mayo Clinic data")
        return False

def test_organization_with_non_compliance():
    """Test an organization that would have had compliance penalties before."""
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Create test data with minimal certifications (would trigger compliance penalty before)
    test_certifications = [
        {
            'name': 'Basic State License',
            'status': 'Active',
            'score_impact': 5
        }
    ]
    
    test_initiatives = []
    
    print("\nTesting organization with minimal certifications...")
    
    score_breakdown = analyzer.calculate_quality_score(test_certifications, test_initiatives)
    
    print(f"\nMinimal Certification Score Breakdown:")
    print(f"- Certification Score: {score_breakdown.get('certification_score', 0)}")
    print(f"- Quality Initiatives Score: {score_breakdown.get('quality_initiatives_score', 0)}")
    print(f"- Total Score: {score_breakdown.get('total_score', 0)}")
    
    # Check that compliance_penalty is not in the breakdown
    if 'compliance_penalty' in score_breakdown:
        print(f"❌ ERROR: compliance_penalty still found in score breakdown: {score_breakdown['compliance_penalty']}")
        return False
    else:
        print("✅ SUCCESS: compliance_penalty removed from score breakdown")
    
    # Check compliance status
    compliance_check = score_breakdown.get('compliance_check', {})
    print(f"\nCompliance Status:")
    print(f"- Is Fully Compliant: {compliance_check.get('is_fully_compliant', 'N/A')}")
    print(f"- Non-compliant Count: {compliance_check.get('non_compliant_count', 0)}")
    print(f"- Total Required: {compliance_check.get('total_required', 0)}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING COMPLIANCE PENALTY REMOVAL")
    print("=" * 60)
    
    success1 = test_penalty_removal()
    success2 = test_organization_with_non_compliance()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ ALL TESTS PASSED: Compliance penalties successfully removed!")
    else:
        print("❌ SOME TESTS FAILED: Check the output above for details")
    print("=" * 60)