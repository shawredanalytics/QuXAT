#!/usr/bin/env python3
"""
Simple test script to verify suggestion-based scoring functionality
"""

import os
import logging
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

# Disable all logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('data_validator').setLevel(logging.CRITICAL)
logging.getLogger('iso_certification_scraper').setLevel(logging.CRITICAL)

from streamlit_app import HealthcareOrgAnalyzer

def test_suggestion_scoring_simple():
    """Test that scoring uses complete organization data from suggestions"""
    
    print("🧪 Testing Suggestion-Based Scoring (Simple)")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test Mayo Clinic
    print("\n🏥 Testing Mayo Clinic")
    suggestions = analyzer.generate_organization_suggestions('Mayo Clinic')
    
    if suggestions:
        mayo_suggestion = suggestions[0]
        print(f"✅ Suggestion: {mayo_suggestion['display_name']}")
        
        # Test suggestion-based scoring
        result = analyzer.search_organization_info_from_suggestion(mayo_suggestion)
        
        if result:
            print(f"✅ Suggestion Score: {result.get('total_score', 'N/A')}")
            print(f"   Certifications: {len(result.get('certifications', []))}")
            print(f"   Quality Initiatives: {len(result.get('quality_initiatives', []))}")
        else:
            print("❌ Suggestion scoring failed")
        
        # Compare with regular search
        regular_result = analyzer.search_organization_info('Mayo Clinic')
        if regular_result:
            print(f"✅ Regular Score: {regular_result.get('total_score', 'N/A')}")
        else:
            print("❌ Regular search failed")
    else:
        print("❌ No Mayo suggestions found")
    
    # Test Apollo
    print("\n🏥 Testing Apollo Hospitals")
    apollo_suggestions = analyzer.generate_organization_suggestions('Apollo')
    
    if apollo_suggestions:
        apollo_suggestion = apollo_suggestions[0]
        print(f"✅ Suggestion: {apollo_suggestion['display_name']}")
        
        apollo_result = analyzer.search_organization_info_from_suggestion(apollo_suggestion)
        
        if apollo_result:
            print(f"✅ Apollo Score: {apollo_result.get('total_score', 'N/A')}")
        else:
            print("❌ Apollo scoring failed")
    else:
        print("❌ No Apollo suggestions found")

if __name__ == "__main__":
    test_suggestion_scoring_simple()