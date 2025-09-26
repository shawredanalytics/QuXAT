"""
Test script to verify that validation fixes are working properly
Tests that simulated data generation is properly validated
"""

import logging
from patient_feedback_module import PatientFeedbackAnalyzer
from automated_feedback_scraper import AutomatedFeedbackScraper
from iso_certification_scraper import ISOCertificationScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_patient_feedback_validation():
    """Test that patient feedback module validates organizations"""
    print("\n=== Testing Patient Feedback Module Validation ===")
    
    analyzer = PatientFeedbackAnalyzer()
    
    # Test with a fake organization name
    fake_org = "Fake Hospital XYZ 123"
    print(f"Testing with fake organization: {fake_org}")
    
    result = analyzer.get_patient_feedback_data(fake_org)
    
    print(f"Result for fake organization:")
    print(f"  - Number of feedback entries: {len(result) if result else 0}")
    if result and len(result) > 0:
        print(f"  - First entry rating: {result[0].rating if hasattr(result[0], 'rating') else 'N/A'}")
        print(f"  - First entry sentiment: {result[0].sentiment if hasattr(result[0], 'sentiment') else 'N/A'}")
    
    # Test with a potentially real organization name
    real_org = "Apollo Hospitals"
    print(f"\nTesting with potentially real organization: {real_org}")
    
    result = analyzer.get_patient_feedback_data(real_org)
    
    print(f"Result for potentially real organization:")
    print(f"  - Number of feedback entries: {len(result) if result else 0}")
    if result and len(result) > 0:
        print(f"  - First entry rating: {result[0].rating if hasattr(result[0], 'rating') else 'N/A'}")
        print(f"  - First entry sentiment: {result[0].sentiment if hasattr(result[0], 'sentiment') else 'N/A'}")

def test_automated_feedback_validation():
    """Test that automated feedback scraper validates organizations"""
    print("\n=== Testing Automated Feedback Scraper Validation ===")
    
    scraper = AutomatedFeedbackScraper()
    
    # Test with a fake organization name
    fake_org = "Fake Medical Center ABC 456"
    print(f"Testing with fake organization: {fake_org}")
    
    result = scraper.scrape_organization_feedback(fake_org)
    
    print(f"Result for fake organization:")
    print(f"  - Total reviews: {result.total_reviews}")
    print(f"  - Average rating: {result.average_rating}")
    print(f"  - Sentiment score: {result.sentiment_score}")
    
    # Test with a potentially real organization name
    real_org = "Fortis Healthcare"
    print(f"\nTesting with potentially real organization: {real_org}")
    
    result = scraper.scrape_organization_feedback(real_org)
    
    print(f"Result for potentially real organization:")
    print(f"  - Total reviews: {result.total_reviews}")
    print(f"  - Average rating: {result.average_rating}")
    print(f"  - Sentiment score: {result.sentiment_score}")

def test_iso_certification_validation():
    """Test that ISO certification scraper doesn't generate random data"""
    print("\n=== Testing ISO Certification Scraper Validation ===")
    
    scraper = ISOCertificationScraper()
    
    # Test with a fake organization name
    fake_org = "Fake Healthcare Corp 789"
    print(f"Testing with fake organization: {fake_org}")
    
    result = scraper.get_organization_iso_certifications(fake_org)
    
    print(f"Result for fake organization:")
    print(f"  - Total certifications: {result.total_certifications}")
    print(f"  - Active certifications: {result.active_certifications}")
    print(f"  - Certification types: {result.certification_types}")
    if result.active_certifications > 0:
        print("    - WARNING: Found certifications for fake organization!")
    else:
        print("    - No certifications found (expected for validation)")

if __name__ == "__main__":
    print("Testing validation fixes for simulated data generation...")
    
    try:
        test_patient_feedback_validation()
        test_automated_feedback_validation()
        test_iso_certification_validation()
        
        print("\n=== Validation Test Summary ===")
        print("✅ Patient feedback module validation test completed")
        print("✅ Automated feedback scraper validation test completed")
        print("✅ ISO certification scraper validation test completed")
        print("\nIf fake organizations show 0 reviews/feedback/certifications, validation is working!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        logger.error(f"Test failed with error: {str(e)}")