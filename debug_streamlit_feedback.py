#!/usr/bin/env python3
"""
Debug script to test the exact same patient feedback code path as Streamlit app
"""

def test_streamlit_feedback_path():
    print("Testing Streamlit Patient Feedback Code Path...")
    
    org_name = "Apollo Hospital"
    
    # Simulate the exact code from streamlit_app.py
    patient_feedback_score = 0
    score_breakdown = {}
    
    try:
        from patient_feedback_module import PatientFeedbackAnalyzer
        analyzer = PatientFeedbackAnalyzer()
        
        print(f"1. Analyzer created successfully")
        
        # Scrape and analyze patient feedback from multiple platforms
        scraped_feedbacks = analyzer.get_patient_feedback_data(org_name, location="")
        
        print(f"2. Scraped feedbacks: {len(scraped_feedbacks) if scraped_feedbacks else 'None'}")
        print(f"   - Type: {type(scraped_feedbacks)}")
        print(f"   - Boolean: {bool(scraped_feedbacks)}")
        
        if scraped_feedbacks:
            print("3. Feedbacks found - calculating scores...")
            
            # Calculate patient feedback score using automated system
            feedback_scores = analyzer.calculate_patient_feedback_score(scraped_feedbacks)
            patient_feedback_score = feedback_scores['patient_feedback_score']
            
            print(f"   - Patient feedback score: {patient_feedback_score}")
            
            # Store additional feedback metrics for detailed view
            score_breakdown['feedback_volume_score'] = feedback_scores.get('volume_score', 0)
            score_breakdown['feedback_sentiment_score'] = feedback_scores.get('sentiment_score', 0)
            score_breakdown['feedback_rating_score'] = feedback_scores.get('rating_score', 0)
            score_breakdown['feedback_trend_score'] = feedback_scores.get('trend_score', 0)
            score_breakdown['feedback_confidence'] = feedback_scores.get('confidence_multiplier', 0)
            
            # Get summary for additional context
            feedback_summary = analyzer.analyze_feedback_summary(org_name, location="")
            score_breakdown['feedback_platform_breakdown'] = feedback_summary.platform_breakdown
            score_breakdown['feedback_total_count'] = feedback_summary.total_feedback_count
            score_breakdown['feedback_average_rating'] = feedback_summary.average_rating
            score_breakdown['feedback_recent_trend'] = feedback_summary.recent_trend
            
            print(f"   - Total count: {score_breakdown['feedback_total_count']}")
            print(f"   - Average rating: {score_breakdown['feedback_average_rating']}")
            print(f"   - Platform breakdown: {score_breakdown['feedback_platform_breakdown']}")
            
        else:
            print("3. No feedback found - setting default values")
            # No feedback found - set default values
            patient_feedback_score = 0.0
            score_breakdown['feedback_volume_score'] = 0
            score_breakdown['feedback_sentiment_score'] = 0
            score_breakdown['feedback_rating_score'] = 0
            score_breakdown['feedback_trend_score'] = 0
            score_breakdown['feedback_confidence'] = 0
            score_breakdown['feedback_platform_breakdown'] = {}
            score_breakdown['feedback_total_count'] = 0
            score_breakdown['feedback_average_rating'] = 0.0
            score_breakdown['feedback_recent_trend'] = 'stable'
            
    except Exception as e:
        print(f"4. Exception caught: {e}")
        print(f"   - Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        patient_feedback_score = 0.0
        # Set default values for error case
        score_breakdown['feedback_volume_score'] = 0
        score_breakdown['feedback_sentiment_score'] = 0
        score_breakdown['feedback_rating_score'] = 0
        score_breakdown['feedback_trend_score'] = 0
        score_breakdown['feedback_confidence'] = 0
        score_breakdown['feedback_platform_breakdown'] = {}
        score_breakdown['feedback_total_count'] = 0
        score_breakdown['feedback_average_rating'] = 0.0
        score_breakdown['feedback_recent_trend'] = 'stable'
    
    score_breakdown['patient_feedback_score'] = patient_feedback_score
    
    print(f"\nFinal Results:")
    print(f"- Patient feedback score: {patient_feedback_score}")
    print(f"- Total count: {score_breakdown.get('feedback_total_count', 'Not set')}")
    print(f"- Will show 'No patient feedback found'? {score_breakdown.get('feedback_total_count', 0) <= 0}")

if __name__ == "__main__":
    test_streamlit_feedback_path()