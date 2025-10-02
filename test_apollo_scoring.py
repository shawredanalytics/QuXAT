#!/usr/bin/env python3
"""
Test script to debug Apollo Hospitals Chennai scoring issue
"""

from streamlit_app import HealthcareOrgAnalyzer
import json

def test_apollo_scoring():
    print("=== APOLLO HOSPITALS CHENNAI SCORING DEBUG ===")
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Get Apollo Hospitals Chennai data
    result = analyzer.search_organization_info('Apollo Hospitals Chennai')
    
    if not result:
        print("❌ Apollo Hospitals Chennai not found in database")
        return
    
    print("✅ Apollo Hospitals Chennai found in database")
    print(f"Name: {result.get('name', 'N/A')}")
    print(f"Country: {result.get('country', 'N/A')}")
    print(f"City: {result.get('city', 'N/A')}")
    print(f"Hospital Type: {result.get('hospital_type', 'N/A')}")
    
    # Check certifications
    certifications = result.get('certifications', [])
    print(f"\nCertifications found: {len(certifications)}")
    
    for i, cert in enumerate(certifications):
        print(f"  Cert {i+1}:")
        print(f"    Name: {cert.get('name', 'Unknown')}")
        print(f"    Status: {cert.get('status', 'Unknown')}")
        print(f"    Score Impact: {cert.get('score_impact', 0)}")
        print(f"    Type: {cert.get('type', 'Unknown')}")
    
    # Check quality initiatives
    quality_initiatives = result.get('quality_initiatives', [])
    print(f"\nQuality initiatives found: {len(quality_initiatives)}")
    
    # Test the scoring function
    print("\n=== TESTING SCORING FUNCTION ===")
    try:
        score_result = analyzer.calculate_quality_score(
            certifications=certifications,
            initiatives=quality_initiatives,
            org_name='Apollo Hospitals Chennai'
        )
        
        print("✅ Scoring function executed successfully")
        print(f"Score result type: {type(score_result)}")
        print(f"Score result keys: {list(score_result.keys()) if isinstance(score_result, dict) else 'Not a dict'}")
        
        if isinstance(score_result, dict):
            print(f"Total score: {score_result.get('total_score', 'N/A')}")
            print(f"Certification score: {score_result.get('certification_score', 'N/A')}")
            print(f"Initiative score: {score_result.get('initiative_score', 'N/A')}")
            
            # Print full score breakdown
            print("\nFull score breakdown:")
            for key, value in score_result.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Score result is not a dictionary: {score_result}")
            
    except Exception as e:
        print(f"❌ Error in scoring function: {e}")
        import traceback
        traceback.print_exc()
    
    # Check if the issue is in the search_organization_info function
    print("\n=== CHECKING SEARCH FUNCTION RESULT ===")
    print(f"Result total_score: {result.get('total_score', 'N/A')}")
    print(f"Result score_breakdown: {result.get('score_breakdown', 'N/A')}")
    
    # Print the full result structure
    print("\nFull result structure:")
    for key, value in result.items():
        if key not in ['certifications', 'quality_initiatives']:  # Skip large arrays
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_apollo_scoring()