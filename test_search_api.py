"""
Test script to verify the organization search API functionality
"""

import os
from organization_search_api import get_search_api

def test_search_api():
    """Test the organization search API functionality"""
    
    print("=== Organization Search API Test ===\n")
    
    # Initialize search API
    search_api = get_search_api()
    
    # Check if Google Places API key is configured
    api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
    print(f"Google Places API Key configured: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API Key (first 10 chars): {api_key[:10]}...")
    else:
        print("API Key: Not configured")
    
    print("\n" + "="*50)
    
    # Test search queries
    test_queries = [
        "Apollo Hospital",
        "Mayo Clinic", 
        "Johns Hopkins",
        "Fortis Hospital",
        "Max Healthcare"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 30)
        
        try:
            # Test Google Places suggestions
            google_suggestions = search_api.get_google_places_suggestions(query, max_results=3)
            print(f"Google Places suggestions: {len(google_suggestions)}")
            
            for i, suggestion in enumerate(google_suggestions, 1):
                print(f"  {i}. {suggestion.get('name', 'N/A')}")
                print(f"     Address: {suggestion.get('address', 'N/A')}")
                print(f"     Source: {suggestion.get('source', 'N/A')}")
                print()
            
            # Test fallback suggestions
            fallback_suggestions = search_api.get_fallback_suggestions(query, max_results=3)
            print(f"Fallback suggestions: {len(fallback_suggestions)}")
            
            for i, suggestion in enumerate(fallback_suggestions, 1):
                print(f"  {i}. {suggestion.get('name', 'N/A')}")
                print(f"     Source: {suggestion.get('source', 'N/A')}")
                print()
            
            # Test combined search
            all_suggestions = search_api.search_organizations(query, max_results=5)
            print(f"Combined suggestions: {len(all_suggestions)}")
            
            for i, suggestion in enumerate(all_suggestions, 1):
                formatted = search_api.format_suggestion_for_display(suggestion)
                print(f"  {i}. {formatted}")
            
        except Exception as e:
            print(f"Error testing query '{query}': {e}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_search_api()