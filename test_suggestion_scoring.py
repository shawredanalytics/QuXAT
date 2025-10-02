#!/usr/bin/env python3
"""
Test script to verify suggestion-based scoring functionality
"""

import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

from streamlit_app import HealthcareOrgAnalyzer

def test_suggestion_scoring():
    """Test that scoring uses complete organization data from suggestions"""
    
    print("🧪 Testing Suggestion-Based Scoring")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test 1: Get Mayo Clinic suggestions
    print("\n1️⃣ GETTING MAYO CLINIC SUGGESTIONS")
    suggestions = analyzer.generate_organization_suggestions('Mayo Clinic')
    
    if not suggestions:
        print("❌ No suggestions found for Mayo Clinic")
        return
    
    print(f"✅ Found {len(suggestions)} suggestions")
    
    # Find Mayo Clinic in suggestions
    mayo_suggestion = None
    for suggestion in suggestions:
        if 'mayo clinic' in suggestion['display_name'].lower():
            mayo_suggestion = suggestion
            break
    
    if not mayo_suggestion:
        print("❌ Mayo Clinic not found in suggestions")
        return
    
    print(f"✅ Found Mayo Clinic suggestion: {mayo_suggestion['display_name']}")
    print(f"   Location: {mayo_suggestion.get('location', 'N/A')}")
    
    # Test 2: Test suggestion-based scoring
    print("\n2️⃣ TESTING SUGGESTION-BASED SCORING")
    
    try:
        # Use the new method that takes complete suggestion data
        result = analyzer.search_organization_info_from_suggestion(mayo_suggestion)
        
        if result:
            print("✅ Successfully scored using suggestion data")
            print(f"   Organization: {result.get('organization_name', 'N/A')}")
            print(f"   Total Score: {result.get('total_score', 'N/A')}")
            print(f"   Location: {result.get('location', 'N/A')}")
            print(f"   Certifications: {len(result.get('certifications', []))}")
            print(f"   Quality Initiatives: {len(result.get('quality_initiatives', []))}")
            
            # Check if we have complete data
            if result.get('certifications') or result.get('quality_initiatives'):
                print("✅ Complete organization data used for scoring")
            else:
                print("⚠️  Limited data - may need fallback")
                
        else:
            print("❌ Failed to score using suggestion data")
            
    except Exception as e:
        print(f"❌ Error in suggestion-based scoring: {e}")
    
    # Test 3: Compare with regular search
    print("\n3️⃣ COMPARING WITH REGULAR SEARCH")
    
    try:
        regular_result = analyzer.search_organization_info('Mayo Clinic')
        
        if regular_result and result:
            print("✅ Both methods returned results")
            
            # Compare scores
            suggestion_score = result.get('total_score', 0)
            regular_score = regular_result.get('total_score', 0)
            
            print(f"   Suggestion-based score: {suggestion_score}")
            print(f"   Regular search score: {regular_score}")
            
            if abs(suggestion_score - regular_score) < 0.1:
                print("✅ Scores are consistent")
            else:
                print("⚠️  Scores differ - may indicate different data sources")
                
        else:
            print("❌ One or both methods failed")
            
    except Exception as e:
        print(f"❌ Error in comparison: {e}")
    
    # Test 4: Test with Apollo Hospitals
    print("\n4️⃣ TESTING WITH APOLLO HOSPITALS")
    
    try:
        apollo_suggestions = analyzer.generate_organization_suggestions('Apollo')
        
        if apollo_suggestions:
            apollo_suggestion = apollo_suggestions[0]  # Take first suggestion
            print(f"✅ Testing with: {apollo_suggestion['display_name']}")
            
            apollo_result = analyzer.search_organization_info_from_suggestion(apollo_suggestion)
            
            if apollo_result:
                print(f"✅ Apollo scored: {apollo_result.get('total_score', 'N/A')}")
            else:
                print("❌ Apollo scoring failed")
        else:
            print("❌ No Apollo suggestions found")
            
    except Exception as e:
        print(f"❌ Error testing Apollo: {e}")

if __name__ == "__main__":
    test_suggestion_scoring()