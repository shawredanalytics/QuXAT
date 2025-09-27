#!/usr/bin/env python3
"""
Test script for the positive improvement messaging feature
"""

from streamlit_app import HealthcareOrgAnalyzer

def test_positive_messaging():
    """Test the positive messaging system with various healthcare organizations"""
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test organizations with different expected score ranges
    test_organizations = [
        # Expected low scores (should show positive message)
        "Small Local Hospital",
        "Community Health Center",
        "Regional Medical Clinic",
        
        # Expected medium scores (should not show positive message)
        "Apollo Hospitals Chennai",
        "Fortis Healthcare",
        
        # Expected high scores (should not show positive message)
        "Mayo Clinic",
        "Cleveland Clinic"
    ]
    
    print("🧪 Testing Positive Improvement Messaging System")
    print("=" * 60)
    
    for org_name in test_organizations:
        print(f"\n🏥 Testing: {org_name}")
        print("-" * 40)
        
        try:
            # Calculate quality score
            result = analyzer.calculate_quality_score(
                certifications=[],  # Empty certifications for low score
                initiatives=[],     # Empty initiatives for low score
                org_name=org_name
            )
            
            if result:
                total_score = result.get('total_score', 0)
                print(f"📊 Total Score: {total_score:.1f}/100")
                
                # Check if positive messaging should be displayed
                if total_score < 50:
                    print("✅ Positive improvement message SHOULD be displayed")
                    print("💬 Message: 'Opportunity for Excellence' section will appear")
                else:
                    print("ℹ️  Positive improvement message will NOT be displayed")
                    print("💬 Score is above threshold (50+ points)")
                
                # Display score breakdown
                print(f"🔍 Score Breakdown:")
                print(f"   - Certification Score: {result.get('certification_score', 0):.1f}")
                print(f"   - Quality Initiatives Score: {result.get('quality_initiatives_score', 0):.1f}")
                print(f"   - Patient Feedback Score: {result.get('patient_feedback_score', 0):.1f}")
                
            else:
                print("❌ Failed to calculate score")
                
        except Exception as e:
            print(f"❌ Error calculating score: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("- Organizations with scores < 50 will see positive improvement messaging")
    print("- Organizations with scores ≥ 50 will not see the messaging")
    print("- The message encourages quality initiatives and public documentation")
    print("- The messaging is designed to be positive and encouraging")

if __name__ == "__main__":
    test_positive_messaging()