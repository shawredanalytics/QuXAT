#!/usr/bin/env python3
"""
Test script for automated patient feedback system
"""

from patient_feedback_module import PatientFeedbackAnalyzer

def test_automated_feedback():
    print("Testing automated patient feedback system...")
    
    # Initialize analyzer
    analyzer = PatientFeedbackAnalyzer()
    
    # Test with Mayo Clinic
    org_name = "Mayo Clinic"
    print(f"\nTesting with: {org_name}")
    
    # Get feedback data
    feedbacks = analyzer.get_patient_feedback_data(org_name, "")
    print(f"Found {len(feedbacks)} feedback entries")
    
    if feedbacks:
        # Calculate scores
        scores = analyzer.calculate_patient_feedback_score(feedbacks)
        print(f"Patient Feedback Score: {scores['patient_feedback_score']:.2f}/15")
        
        # Get summary
        summary = analyzer.analyze_feedback_summary(org_name, "")
        print(f"Total Reviews: {summary.total_feedback_count}")
        print(f"Average Rating: {summary.average_rating:.1f}/5.0")
        print(f"Platform Breakdown: {summary.platform_breakdown}")
        print(f"Recent Trend: {summary.recent_trend}")
        
        # Show some sample feedback
        print("\nSample feedback:")
        for i, feedback in enumerate(feedbacks[:3]):
            print(f"  {i+1}. {feedback.platform}: {feedback.rating}/5 - {feedback.feedback_text[:100]}...")
    else:
        print("No feedback data generated")

if __name__ == "__main__":
    test_automated_feedback()