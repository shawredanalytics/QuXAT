"""
Organization Search API Integration Module
Provides real-time organization suggestions from external APIs like Google Places API
"""

import requests
import json
import os
from typing import List, Dict, Optional
import time
from urllib.parse import quote_plus

class OrganizationSearchAPI:
    """
    Handles external API integration for organization name suggestions
    """
    
    def __init__(self):
        self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuXAT Healthcare Quality Assessment Tool/1.0'
        })
        
        # Cache for API responses to avoid excessive calls
        self.cache = {}
        self.cache_expiry = 300  # 5 minutes
        
    def get_google_places_suggestions(self, query: str, max_results: int = 8) -> List[Dict]:
        """
        Get organization suggestions from Google Places API
        """
        if not self.google_places_api_key:
            return []
            
        # Check cache first
        cache_key = f"google_places_{query.lower()}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_expiry:
                return cached_data[:max_results]
        
        try:
            # Google Places Text Search API
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': f"{query} hospital OR clinic OR medical center OR healthcare",
                'key': self.google_places_api_key,
                'type': 'hospital',
                'fields': 'name,formatted_address,place_id,rating,types'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            suggestions = []
            
            if data.get('status') == 'OK':
                for place in data.get('results', [])[:max_results]:
                    # Filter for healthcare-related places
                    types = place.get('types', [])
                    healthcare_types = ['hospital', 'health', 'doctor', 'clinic', 'medical']
                    
                    if any(htype in str(types).lower() for htype in healthcare_types):
                        suggestion = {
                            'name': place.get('name', ''),
                            'address': place.get('formatted_address', ''),
                            'place_id': place.get('place_id', ''),
                            'rating': place.get('rating', 0),
                            'source': 'Google Places',
                            'types': types
                        }
                        suggestions.append(suggestion)
                
                # Cache the results
                self.cache[cache_key] = (suggestions, time.time())
                
            return suggestions[:max_results]
            
        except Exception as e:
            print(f"Error fetching Google Places suggestions: {e}")
            return []
    
    def get_fallback_suggestions(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Fallback method using a simple web search approach
        """
        try:
            # Use a simple approach with common healthcare organization patterns
            suggestions = []
            
            # Common healthcare organization suffixes
            suffixes = [
                "Hospital", "Medical Center", "Clinic", "Health System",
                "Healthcare", "Medical Group", "Regional Medical Center"
            ]
            
            # Generate suggestions based on query
            base_query = query.strip().title()
            
            for suffix in suffixes:
                if suffix.lower() not in query.lower():
                    suggestion = {
                        'name': f"{base_query} {suffix}",
                        'address': "Location to be verified",
                        'place_id': f"fallback_{hash(f'{base_query}_{suffix}')}",
                        'rating': 0,
                        'source': 'Generated Suggestion',
                        'types': ['hospital', 'health']
                    }
                    suggestions.append(suggestion)
                    
                    if len(suggestions) >= max_results:
                        break
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating fallback suggestions: {e}")
            return []
    
    def search_organizations(self, query: str, max_results: int = 8) -> List[Dict]:
        """
        Main method to get organization suggestions from multiple sources
        """
        if not query or len(query.strip()) < 2:
            return []
        
        all_suggestions = []
        
        # Try Google Places API first
        google_suggestions = self.get_google_places_suggestions(query, max_results // 2)
        all_suggestions.extend(google_suggestions)
        
        # If we don't have enough suggestions, use fallback
        if len(all_suggestions) < max_results:
            remaining = max_results - len(all_suggestions)
            fallback_suggestions = self.get_fallback_suggestions(query, remaining)
            all_suggestions.extend(fallback_suggestions)
        
        # Remove duplicates based on name similarity
        unique_suggestions = []
        seen_names = set()
        
        for suggestion in all_suggestions:
            name_key = suggestion['name'].lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:max_results]
    
    def format_suggestion_for_display(self, suggestion: Dict) -> str:
        """
        Format suggestion for display in Streamlit selectbox
        """
        name = suggestion.get('name', '')
        address = suggestion.get('address', '')
        source = suggestion.get('source', '')
        rating = suggestion.get('rating', 0)
        
        # Create display string
        display_parts = [name]
        
        if address and address != "Location to be verified":
            # Shorten address for display
            addr_parts = address.split(',')
            if len(addr_parts) > 2:
                short_address = f"{addr_parts[-2].strip()}, {addr_parts[-1].strip()}"
            else:
                short_address = address
            display_parts.append(short_address)
        
        if rating > 0:
            display_parts.append(f"★ {rating}")
        
        if source:
            display_parts.append(f"({source})")
        
        return " • ".join(display_parts)
    
    def clear_cache(self):
        """Clear the API response cache"""
        self.cache.clear()

# Global instance
_search_api = None

def get_search_api():
    """Get or create the global search API instance"""
    global _search_api
    if _search_api is None:
        _search_api = OrganizationSearchAPI()
    return _search_api