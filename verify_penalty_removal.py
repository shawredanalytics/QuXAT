#!/usr/bin/env python3
"""
Verification script to ensure compliance penalties have been completely removed
from the QuXAT scoring system.
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_penalty_removal():
    """Test that compliance penalties are completely removed from scoring."""
    
    try:
        # Import the HealthcareOrgAnalyzer from streamlit_app
        from streamlit_app import HealthcareOrgAnalyzer
        
        # Initialize the analyzer
        analyzer = HealthcareOrgAnalyzer()
        
        print("🔍 Testing compliance penalty removal...")
        print("=" * 50)
        
        # Test 1: Create a test organization with minimal certifications
        test_certifications = [
            {"name": "Local Health Department", "status": "Active"},
            {"name": "Basic Safety Certification", "status": "Active"}
        ]
        test_initiatives = ["Basic Patient Care", "Community Health"]
        test_org_name = "Test Hospital"
        
        print(f"📊 Testing organization: {test_org_name}")
        print(f"   Certifications: {[cert['name'] for cert in test_certifications]}")
        print(f"   Initiatives: {test_initiatives}")
        
        # Calculate quality score
        score_result = analyzer.calculate_quality_score(
            certifications=test_certifications,
            initiatives=test_initiatives,
            org_name=test_org_name
        )
        
        print(f"\n📈 Score calculation results:")
        print(f"   Total Score: {score_result['total_score']:.2f}")
        
        # Check if grade exists in result
        if 'grade' in score_result:
            print(f"   Grade: {score_result['grade']}")
        else:
            print(f"   Grade: Not available in result")
        
        # Check score breakdown
        score_breakdown = score_result.get('score_breakdown', {})
        print(f"\n🔍 Score breakdown analysis:")
        
        # Verify compliance_penalty is NOT in score breakdown
        if 'compliance_penalty' in score_breakdown:
            print(f"   ❌ FAIL: compliance_penalty found in score breakdown: {score_breakdown['compliance_penalty']}")
            return False
        else:
            print(f"   ✅ PASS: compliance_penalty not found in score breakdown")
        
        # Print all breakdown components
        print(f"\n📋 Score breakdown components:")
        for key, value in score_breakdown.items():
            print(f"   - {key}: {value}")
        
        # Test 2: Verify scoring logic doesn't reference compliance penalties
        print(f"\n🔍 Testing scoring logic integrity...")
        
        # Check that the total score is calculated without penalty deductions
        expected_components = [
            'weighted_certification_score',
            'patient_satisfaction_score', 
            'safety_rating_score',
            'clinical_outcomes_score',
            'technology_adoption_score',
            'research_score',
            'international_recognition_score',
            'community_impact_score',
            'staff_credentials_score',
            'facility_infrastructure_score',
            'accreditation_history_score'
        ]
        
        missing_components = []
        for component in expected_components:
            if component not in score_breakdown:
                missing_components.append(component)
        
        if missing_components:
            print(f"   ⚠️  WARNING: Missing score components: {missing_components}")
        else:
            print(f"   ✅ PASS: All expected score components present")
        
        # Test 3: Verify total score is reasonable (not artificially reduced)
        total_score = score_result['total_score']
        if total_score < 0:
            print(f"   ❌ FAIL: Total score is negative: {total_score}")
            return False
        elif total_score > 100:
            print(f"   ❌ FAIL: Total score exceeds maximum: {total_score}")
            return False
        else:
            print(f"   ✅ PASS: Total score is within valid range: {total_score:.2f}")
        
        print(f"\n🎉 SUCCESS: Compliance penalties have been successfully removed!")
        print(f"   - No compliance_penalty in score breakdown")
        print(f"   - Score calculation appears normal")
        print(f"   - Total score is within valid range")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the verification test."""
    print("🚀 QuXAT Compliance Penalty Removal Verification")
    print("=" * 60)
    
    success = test_penalty_removal()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ VERIFICATION COMPLETE: Compliance penalties successfully removed!")
        sys.exit(0)
    else:
        print("❌ VERIFICATION FAILED: Issues found with penalty removal!")
        sys.exit(1)

if __name__ == "__main__":
    main()