#!/usr/bin/env python3
"""
Hospital Branch Scraper using Google Maps API
Extracts comprehensive branch data for multi-location hospital groups
"""

import requests
import json
import os
import time
from typing import List, Dict, Optional, Set
from datetime import datetime
import csv
from urllib.parse import quote_plus

class HospitalBranchScraper:
    """
    Scrapes hospital branch data using Google Places API
    """
    
    def __init__(self):
        """
        Initialize the scraper with Google Places API client
        ENFORCES REAL DATA ONLY - NO MOCK OR SIMULATION DATA
        """
        self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
        if not self.google_places_api_key:
            raise ValueError("❌ GOOGLE_PLACES_API_KEY not found in environment variables. Real data validation requires valid API key.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QuXAT Healthcare Branch Scraper/1.0'
        })
        
        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        
        # Cache to avoid duplicate API calls
        self.cache = {}
        
        # HARDCODED VALIDATION: Only real data allowed
        self.REAL_DATA_ONLY = True
        self.ALLOW_MOCK_DATA = False
        self.REQUIRE_GOOGLE_VERIFICATION = True
        
        # Major hospital groups to scrape
        self.major_hospital_groups = {
            'Apollo Hospitals': {
                'search_terms': ['Apollo Hospitals', 'Apollo Hospital', 'Apollo Medical Center'],
                'cities': ['Hyderabad', 'Secunderabad', 'Chennai', 'Bangalore', 'Delhi', 'Mumbai', 'Kolkata', 'Ahmedabad', 'Pune']
            },
            'Fortis Healthcare': {
                'search_terms': ['Fortis Hospital', 'Fortis Healthcare', 'Fortis Medical Center'],
                'cities': ['Delhi', 'Gurgaon', 'Noida', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Mohali']
            },
            'Max Healthcare': {
                'search_terms': ['Max Hospital', 'Max Healthcare', 'Max Super Speciality Hospital'],
                'cities': ['Delhi', 'Gurgaon', 'Noida', 'Saket', 'Patparganj', 'Shalimar Bagh', 'Vaishali', 'Dehradun']
            },
            'Manipal Hospitals': {
                'search_terms': ['Manipal Hospital', 'Manipal Hospitals', 'Manipal Medical Center'],
                'cities': ['Bangalore', 'Delhi', 'Goa', 'Jaipur', 'Salem', 'Vijayawada', 'Bhubaneswar']
            },
            'Narayana Health': {
                'search_terms': ['Narayana Hospital', 'Narayana Health', 'Narayana Medical Center'],
                'cities': ['Bangalore', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Kochi', 'Mysore', 'Gurugram']
            }
        }
        
        self.scraped_branches = []
        self.duplicate_checker = set()
        
        print("✅ Hospital Branch Scraper initialized with REAL DATA ONLY enforcement")
        
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def search_hospital_branches(self, hospital_group: str, search_term: str, city: str = None, state: str = None) -> List[Dict]:
        """
        Search for hospital branches using Google Places API
        ENFORCES REAL DATA ONLY - NO FALLBACK OR MOCK DATA
        """
        if not self.REAL_DATA_ONLY:
            raise ValueError("❌ REAL DATA ONLY mode is disabled. This violates data integrity requirements.")
            
        if not self.google_places_api_key:
            print("❌ Google Places API key not found. Please set GOOGLE_PLACES_API_KEY environment variable.")
            return []
        
        # Construct search query
        query_parts = [search_term]
        if city:
            query_parts.append(city)
        if state:
            query_parts.append(state)
        
        query = " ".join(query_parts)
        
        # Check cache
        cache_key = f"branches_{query.lower().replace(' ', '_')}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self._rate_limit()
        
        try:
            # Google Places Text Search API for real data only
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': query,
                'key': self.google_places_api_key,
                'type': 'hospital',
                'fields': 'name,formatted_address,place_id,rating,types,geometry'
            }
            
            print(f"🔍 Searching for: {query}")
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            branches = []
            
            if data.get('status') == 'OK':
                for place in data.get('results', []):
                    # Filter for healthcare-related places
                    types = place.get('types', [])
                    name = place.get('name', '')
                    
                    # STRICT VALIDATION: Must be real healthcare facility
                    if (any(term.lower() in name.lower() for term in [search_term.split()[0], hospital_group.split()[0]]) and 
                        self.validate_real_healthcare_facility(place)):
                        branch_data = self._extract_branch_details(place, hospital_group)
                        if branch_data and self._is_unique_branch(branch_data):
                            branches.append(branch_data)
                            self.duplicate_checker.add(self._get_branch_key(branch_data))
                            print(f"✅ Found verified real branch: {name}")
                    else:
                        print(f"❌ Rejected non-validated data: {name}")
                
                # Cache results
                self.cache[cache_key] = branches
                print(f"✅ Found {len(branches)} verified real branches for {query}")
                
            elif data.get('status') == 'ZERO_RESULTS':
                print(f"ℹ️ No results found for: {query}")
            else:
                print(f"⚠️ API Error for {query}: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                
            return branches
            
        except Exception as e:
            print(f"❌ Error searching for {query}: {e}")
            return []
    
    def validate_real_healthcare_facility(self, place_data: Dict) -> bool:
        """
        Validate that the place is a real healthcare facility with authentic data
        """
        try:
            name = place_data.get('name', '').lower()
            types = place_data.get('types', [])
            address = place_data.get('formatted_address', '')
            place_id = place_data.get('place_id', '')
            
            # Must have a valid Google Place ID (real places have specific format)
            if not place_id or place_id.startswith('fallback_') or len(place_id) < 10:
                return False
            
            # Must have a real address (not placeholder text)
            if not address or address in ['Location to be verified', 'Unknown location']:
                return False
            
            # Must have healthcare-related types from Google's classification
            healthcare_types = ['hospital', 'health', 'doctor', 'clinic', 'medical', 'dentist', 'pharmacy']
            if not any(htype in str(types).lower() for htype in healthcare_types):
                return False
            
            # Must have legitimate healthcare facility indicators in name
            healthcare_keywords = [
                'hospital', 'medical', 'clinic', 'health', 'care', 'center', 'centre',
                'apollo', 'fortis', 'max', 'manipal', 'narayana', 'aster', 'columbia'
            ]
            if not any(keyword in name for keyword in healthcare_keywords):
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating healthcare facility: {e}")
            return False
    
    def _extract_branch_details(self, place_data: Dict, hospital_group: str) -> Optional[Dict]:
        """
        Extract detailed information from Google Places result
        """
        try:
            name = place_data.get('name', '')
            address = place_data.get('formatted_address', '')
            place_id = place_data.get('place_id', '')
            rating = place_data.get('rating', 0)
            types = place_data.get('types', [])
            geometry = place_data.get('geometry', {})
            location = geometry.get('location', {})
            
            # Parse address components
            address_parts = address.split(',') if address else []
            city = ""
            state = ""
            country = ""
            
            if len(address_parts) >= 3:
                city = address_parts[-3].strip()
                state = address_parts[-2].strip()
                country = address_parts[-1].strip()
            elif len(address_parts) >= 2:
                state = address_parts[-2].strip()
                country = address_parts[-1].strip()
            elif len(address_parts) >= 1:
                country = address_parts[-1].strip()
            
            # Create branch data with validation markers
            branch_data = {
                'hospital_group': hospital_group,
                'name': name,
                'full_address': address,
                'city': city,
                'state': state,
                'country': country,
                'place_id': place_id,
                'latitude': location.get('lat', 0),
                'longitude': location.get('lng', 0),
                'rating': rating,
                'types': types,
                'source': 'Google Places API - Verified Real Data',
                'scraped_date': datetime.now().isoformat(),
                'is_branch': True,
                'parent_organization': hospital_group,
                'data_validation': {
                    'is_real_facility': True,
                    'has_valid_place_id': bool(place_id and len(place_id) >= 10),
                    'has_real_address': bool(address and address not in ['Location to be verified', 'Unknown location']),
                    'google_verified': True
                }
            }
            
            return branch_data
            
        except Exception as e:
            print(f"❌ Error extracting branch details: {e}")
            return None
    
    def _get_branch_key(self, branch_data: Dict) -> str:
        """Generate unique key for branch to avoid duplicates"""
        name = branch_data.get('name', '').lower().strip()
        city = branch_data.get('city', '').lower().strip()
        return f"{name}_{city}"
    
    def _is_unique_branch(self, branch_data: Dict) -> bool:
        """Check if branch is unique"""
        key = self._get_branch_key(branch_data)
        return key not in self.duplicate_checker
    
    def scrape_apollo_hospitals_branches(self) -> List[Dict]:
        """
        Specifically scrape Apollo Hospitals branches in Hyderabad and Secunderabad
        """
        print("\n🏥 Scraping Apollo Hospitals branches...")
        apollo_branches = []
        
        # Focus on Hyderabad and Secunderabad first
        target_cities = [
            {'city': 'Hyderabad', 'state': 'Telangana'},
            {'city': 'Secunderabad', 'state': 'Telangana'},
            {'city': 'Jubilee Hills', 'state': 'Telangana'},
            {'city': 'Banjara Hills', 'state': 'Telangana'},
            {'city': 'Kondapur', 'state': 'Telangana'},
            {'city': 'Gachibowli', 'state': 'Telangana'}
        ]
        
        search_terms = [
            'Apollo Hospitals',
            'Apollo Hospital',
            'Apollo Medical Center',
            'Apollo Specialty Hospital',
            'Apollo Health City'
        ]
        
        for location in target_cities:
            for search_term in search_terms:
                branches = self.search_hospital_branches(
                    'Apollo Hospitals',
                    search_term,
                    location['city'],
                    location['state']
                )
                apollo_branches.extend(branches)
                time.sleep(0.2)  # Additional delay for Apollo searches
        
        # Also search without city restriction to catch any missed branches
        for search_term in search_terms:
            branches = self.search_hospital_branches(
                'Apollo Hospitals',
                f"{search_term} Hyderabad OR Secunderabad",
                None,
                'Telangana'
            )
            apollo_branches.extend(branches)
            time.sleep(0.2)
        
        return apollo_branches
    
    def scrape_all_hospital_groups(self) -> List[Dict]:
        """
        Scrape branches for all major hospital groups
        """
        print("\n🏥 Scraping all major hospital groups...")
        all_branches = []
        
        for group_name, group_config in self.major_hospital_groups.items():
            print(f"\n📍 Scraping {group_name}...")
            
            for search_term in group_config['search_terms']:
                for city in group_config['cities']:
                    branches = self.search_hospital_branches(
                        group_name,
                        search_term,
                        city
                    )
                    all_branches.extend(branches)
                    time.sleep(0.1)  # Small delay between requests
        
        return all_branches
    
    def save_branches_to_files(self, branches: List[Dict], filename_prefix: str = "hospital_branches"):
        """
        Save scraped branches to JSON and CSV files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to JSON
        json_filename = f"{filename_prefix}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(branches, f, indent=2, ensure_ascii=False)
        
        # Save to CSV
        csv_filename = f"{filename_prefix}_{timestamp}.csv"
        if branches:
            fieldnames = branches[0].keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(branches)
        
        print(f"💾 Saved {len(branches)} branches to:")
        print(f"   📄 {json_filename}")
        print(f"   📊 {csv_filename}")
        
        return json_filename, csv_filename
    
    def run_apollo_branch_extraction(self):
        """
        Main method to extract Apollo Hospitals branches
        """
        print("🚀 Starting Apollo Hospitals branch extraction...")
        
        apollo_branches = self.scrape_apollo_hospitals_branches()
        
        if apollo_branches:
            json_file, csv_file = self.save_branches_to_files(apollo_branches, "apollo_hospitals_branches")
            
            print(f"\n📊 Apollo Hospitals Branch Summary:")
            print(f"   Total branches found: {len(apollo_branches)}")
            
            # Group by city
            city_counts = {}
            for branch in apollo_branches:
                city = branch.get('city', 'Unknown')
                city_counts[city] = city_counts.get(city, 0) + 1
            
            print("   Branches by city:")
            for city, count in sorted(city_counts.items()):
                print(f"     {city}: {count}")
            
            return apollo_branches
        else:
            print("❌ No Apollo Hospitals branches found")
            return []

def main():
    """Main execution function"""
    scraper = HospitalBranchScraper()
    
    # Run Apollo branch extraction
    apollo_branches = scraper.run_apollo_branch_extraction()
    
    # Optionally run full extraction for all hospital groups
    print("\n" + "="*60)
    user_input = input("Do you want to scrape all major hospital groups? (y/n): ")
    if user_input.lower() in ['y', 'yes']:
        print("\n🚀 Starting full hospital group extraction...")
        all_branches = scraper.scrape_all_hospital_groups()
        
        if all_branches:
            scraper.save_branches_to_files(all_branches, "all_hospital_branches")
            print(f"\n📊 Total branches found across all groups: {len(all_branches)}")

if __name__ == "__main__":
    main()