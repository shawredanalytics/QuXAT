#!/usr/bin/env python3
"""
Debug script to test patient feedback integration
"""

from patient_feedback_module import PatientFeedbackAnalyzer

def test_feedback_integration():
    print("Testing Patient Feedback Integration...")
    
    # Test with a sample organization
    org_name = "Apollo Hospital"
    
    analyzer = PatientFeedbackAnalyzer()
    
    # Test get_patient_feedback_data
    print(f"\n1. Testing get_patient_feedback_data for '{org_name}':")
    scraped_feedbacks = analyzer.get_patient_feedback_data(org_name, location="")
    print(f"   - Returned type: {type(scraped_feedbacks)}")
    print(f"   - Length: {len(scraped_feedbacks) if scraped_feedbacks else 'None'}")
    print(f"   - Boolean evaluation: {bool(scraped_feedbacks)}")
    
    if scraped_feedbacks:
        print(f"   - First feedback: {scraped_feedbacks[0]}")
        
        # Test calculate_patient_feedback_score
        print(f"\n2. Testing calculate_patient_feedback_score:")
        feedback_scores = analyzer.calculate_patient_feedback_score(scraped_feedbacks)
        print(f"   - Feedback scores: {feedback_scores}")
        
        # Test analyze_feedback_summary
        print(f"\n3. Testing analyze_feedback_summary:")
        feedback_summary = analyzer.analyze_feedback_summary(org_name, location="")
        print(f"   - Summary: {feedback_summary}")
        print(f"   - Total count: {feedback_summary.total_feedback_count}")
        print(f"   - Platform breakdown: {feedback_summary.platform_breakdown}")
        
    else:
        print("   - No feedback found!")
        
    # Test with different organization names
    test_orgs = ["Mayo Clinic", "Johns Hopkins", "Cleveland Clinic", "Test Hospital"]
    
    print(f"\n4. Testing with different organization names:")
    for test_org in test_orgs:
        feedbacks = analyzer.get_patient_feedback_data(test_org, location="")
        print(f"   - {test_org}: {len(feedbacks) if feedbacks else 0} feedbacks")

if __name__ == "__main__":
    test_feedback_integration()