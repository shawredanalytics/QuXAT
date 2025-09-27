#!/usr/bin/env python3
"""
Test script for enhanced search functionality with Google Custom Search API integration
"""

import os
import sys
from organization_search_api import OrganizationSearchAPI

def test_enhanced_search():
    """Test the enhanced search functionality"""
    
    print("🔍 Testing Enhanced Search Functionality")
    print("=" * 50)
    
    # Initialize the search API
    search_api = OrganizationSearchAPI()
    
    # Test queries
    test_queries = [
        "AIIMS Delhi",
        "Apollo Hospital",
        "Fortis Healthcare",
        "Max Hospital",
        "Manipal Hospital",
        "Christian Medical College Vellore",
        "Tata Memorial Hospital",
        "Sankara Nethralaya"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            # Get search suggestions
            suggestions = search_api.search_organizations(query, max_results=5)
            
            if suggestions:
                print(f"✅ Found {len(suggestions)} suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    name = suggestion.get('name', 'Unknown')
                    location = suggestion.get('location', 'No location')
                    source = suggestion.get('source', 'Unknown source')
                    
                    print(f"  {i}. {name}")
                    print(f"     📍 Location: {location}")
                    print(f"     🔗 Source: {source}")
                    
                    # Test web scraping verification for first result
                    if i == 1:
                        print(f"     🔍 Verifying with web scraping...")
                        verification = search_api.verify_organization_with_web_scraping(name, location)
                        if verification.get('verified'):
                            print(f"     ✅ Verified (Confidence: {verification.get('confidence_score', 0):.2f})")
                            if 'keywords' in verification.get('found_details', {}):
                                keywords = verification['found_details']['keywords']
                                print(f"     🏥 Keywords found: {', '.join(keywords)}")
                        else:
                            print(f"     ❌ Could not verify")
                    print()
            else:
                print("❌ No suggestions found")
                
        except Exception as e:
            print(f"❌ Error testing query '{query}': {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Enhanced Search Test Complete!")

def test_api_keys():
    """Test if API keys are properly configured"""
    print("\n🔑 Testing API Key Configuration")
    print("-" * 30)
    
    # Check Google Places API key
    places_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if places_key:
        print("✅ Google Places API key found")
    else:
        print("❌ Google Places API key not found")
    
    # Check Google Custom Search API key
    custom_search_key = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
    if custom_search_key:
        print("✅ Google Custom Search API key found")
    else:
        print("❌ Google Custom Search API key not found")
    
    # Check Google Custom Search Engine ID
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    if search_engine_id:
        print("✅ Google Custom Search Engine ID found")
    else:
        print("❌ Google Custom Search Engine ID not found")

if __name__ == "__main__":
    print("🚀 Enhanced Search API Test Suite")
    print("=" * 50)
    
    # Test API keys first
    test_api_keys()
    
    # Test search functionality
    test_enhanced_search()
    
    print("\n✨ All tests completed!")