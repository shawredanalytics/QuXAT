import requests
import json
import csv
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import random
from urllib.parse import urljoin, quote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedNABHScraper:
    def __init__(self):
        self.base_url = "https://nabh.co"
        self.search_endpoint = "https://nabh.co/search/ajax"
        self.organizations = []
        
        # Session for maintaining cookies and headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://nabh.co/find-a-healthcare-organisation/',
            'Origin': 'https://nabh.co'
        })
        
        # Search parameters to try
        self.search_terms = [
            "", "hospital", "medical", "healthcare", "clinic", "nursing", "diagnostic",
            "center", "centre", "institute", "foundation", "trust", "multispecialty",
            "super specialty", "cardiac", "cancer", "orthopedic", "eye", "dental",
            "maternity", "children", "pediatric", "neuro", "kidney", "liver"
        ]
        
        self.states = [
            "", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Dadra and Nagar Haveli",
            "Daman and Diu", "Lakshadweep", "Puducherry", "Andaman and Nicobar Islands"
        ]
        
        self.cities = [
            "", "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata",
            "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
            "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad", "Ludhiana",
            "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Varanasi", "Srinagar",
            "Aurangabad", "Dhanbad", "Amritsar", "Allahabad", "Ranchi", "Howrah",
            "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai",
            "Raipur", "Kota", "Chandigarh", "Guwahati", "Solapur", "Hubli", "Mysore",
            "Tiruchirappalli", "Bareilly", "Aligarh", "Moradabad", "Gorakhpur", "Noida"
        ]

    def initialize_session(self):
        """Initialize session by visiting the main page"""
        try:
            logger.info("Initializing session...")
            
            # Visit main search page to get cookies and session
            response = self.session.get("https://nabh.co/find-a-healthcare-organisation/")
            
            if response.status_code == 200:
                logger.info("Session initialized successfully")
                
                # Extract any CSRF tokens or session data if needed
                content = response.text
                
                # Look for CSRF token
                csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', content)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
                    logger.info(f"Found CSRF token: {self.csrf_token[:10]}...")
                
                return True
            else:
                logger.error(f"Failed to initialize session: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return False

    def search_organizations_api(self, search_term: str = "", state: str = "", city: str = "", page: int = 1) -> Dict:
        """Search organizations using the API endpoint"""
        try:
            # Prepare search parameters
            params = {
                'search': search_term,
                'state': state,
                'city': city,
                'page': page,
                'per_page': 50  # Try to get more results per request
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            logger.debug(f"Searching with params: {params}")
            
            # Make API request
            response = self.session.get(self.search_endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return data
                except json.JSONDecodeError:
                    # If not JSON, try to parse HTML response
                    return self.parse_html_response(response.text)
            else:
                logger.warning(f"API request failed with status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error in API search: {e}")
            return {}

    def parse_html_response(self, html_content: str) -> Dict:
        """Parse HTML response if JSON is not returned"""
        try:
            # Extract organization data from HTML
            organizations = []
            
            # Look for organization patterns in HTML
            org_patterns = [
                r'<div[^>]*class="[^"]*organization[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*hospital[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
                r'<tr[^>]*class="[^"]*org[^"]*"[^>]*>(.*?)</tr>'
            ]
            
            for pattern in org_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    org_data = self.extract_org_from_html(match)
                    if org_data:
                        organizations.append(org_data)
            
            return {
                'organizations': organizations,
                'total': len(organizations),
                'page': 1,
                'has_more': len(organizations) >= 20
            }
            
        except Exception as e:
            logger.error(f"Error parsing HTML response: {e}")
            return {}

    def extract_org_from_html(self, html_snippet: str) -> Dict:
        """Extract organization data from HTML snippet"""
        try:
            org_data = {
                'name': '',
                'state': 'Unknown',
                'city': 'Unknown',
                'country': 'India',
                'accreditation_level': 'Unknown',
                'accreditation_category': 'Unknown',
                'valid_from': None,
                'valid_until': None,
                'certificate_number': None,
                'address': '',
                'phone': '',
                'email': '',
                'website': '',
                'source': 'NABH Official Directory',
                'scraped_date': datetime.now().isoformat(),
                'nabh_url': 'https://nabh.co/find-a-healthcare-organisation/'
            }
            
            # Remove HTML tags for text extraction
            text_content = re.sub(r'<[^>]+>', ' ', html_snippet)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Extract name (usually the first significant text)
            name_match = re.search(r'^([^,\n]{10,100})', text_content)
            if name_match:
                org_data['name'] = name_match.group(1).strip()
            
            # Extract address
            address_patterns = [
                r'Address[:\s]+([^\n,]+(?:Road|Street|Avenue|Lane|Plot|Sector)[^\n]*)',
                r'([A-Za-z\s,\-0-9]+(?:Road|Street|Avenue|Lane|Plot|Sector)[^\n]*)',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text_content, re.I)
                if match:
                    org_data['address'] = match.group(1).strip()
                    break
            
            # Extract city and state from address or text
            city_state_patterns = [
                r'([A-Za-z\s]+),\s*([A-Za-z\s]+)(?:,|\s|$)',
                r'City[:\s]*([A-Za-z\s]+)',
                r'State[:\s]*([A-Za-z\s]+)'
            ]
            
            for pattern in city_state_patterns:
                match = re.search(pattern, text_content, re.I)
                if match:
                    if len(match.groups()) >= 2:
                        org_data['city'] = match.group(1).strip()
                        org_data['state'] = match.group(2).strip()
                    else:
                        if 'city' in pattern.lower():
                            org_data['city'] = match.group(1).strip()
                        elif 'state' in pattern.lower():
                            org_data['state'] = match.group(1).strip()
                    break
            
            # Extract phone
            phone_match = re.search(r'(?:Phone|Tel|Mobile|Contact)[:\s]*([+\d\s\-\(\)]{10,})', text_content, re.I)
            if phone_match:
                org_data['phone'] = phone_match.group(1).strip()
            
            # Extract email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text_content)
            if email_match:
                org_data['email'] = email_match.group(1)
            
            # Extract accreditation details
            if 'full' in text_content.lower():
                org_data['accreditation_level'] = 'Full'
            elif 'entry' in text_content.lower():
                org_data['accreditation_level'] = 'Entry Level'
            elif 'provisional' in text_content.lower():
                org_data['accreditation_level'] = 'Provisional'
            
            # Extract dates
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            dates = re.findall(date_pattern, text_content)
            
            if len(dates) >= 2:
                org_data['valid_from'] = dates[0]
                org_data['valid_until'] = dates[1]
            elif len(dates) == 1:
                org_data['valid_until'] = dates[0]
            
            # Extract certificate number
            cert_patterns = [
                r'(?:Certificate|Cert|Ref)\.?\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9/-]+)',
                r'([A-Z]{2,}\d{4,})',
                r'(NABH/[A-Z0-9/-]+)'
            ]
            
            for pattern in cert_patterns:
                cert_match = re.search(pattern, text_content, re.I)
                if cert_match:
                    org_data['certificate_number'] = cert_match.group(1)
                    break
            
            return org_data if org_data['name'] else None
            
        except Exception as e:
            logger.error(f"Error extracting organization from HTML: {e}")
            return None

    def comprehensive_search(self):
        """Perform comprehensive search using various combinations"""
        logger.info("Starting comprehensive NABH API-based search...")
        
        all_organizations = []
        search_count = 0
        
        try:
            # Strategy 1: Search with empty parameters to get all
            logger.info("Searching with empty parameters...")
            for page in range(1, 21):  # Try up to 20 pages
                result = self.search_organizations_api(page=page)
                
                if result and 'organizations' in result:
                    orgs = result['organizations']
                    if orgs:
                        all_organizations.extend(orgs)
                        logger.info(f"Page {page}: Found {len(orgs)} organizations")
                        search_count += 1
                        
                        if not result.get('has_more', False) or len(orgs) < 10:
                            break
                    else:
                        break
                else:
                    break
                
                time.sleep(random.uniform(1, 2))
            
            # Strategy 2: Search by states
            for i, state in enumerate(self.states[:10]):  # Limit for efficiency
                if not state:  # Skip empty state
                    continue
                    
                logger.info(f"Searching in state: {state} ({i+1}/{min(10, len(self.states))})")
                
                for page in range(1, 6):  # Up to 5 pages per state
                    result = self.search_organizations_api(state=state, page=page)
                    
                    if result and 'organizations' in result:
                        orgs = result['organizations']
                        if orgs:
                            all_organizations.extend(orgs)
                            logger.info(f"State {state}, Page {page}: Found {len(orgs)} organizations")
                            search_count += 1
                            
                            if not result.get('has_more', False) or len(orgs) < 5:
                                break
                        else:
                            break
                    else:
                        break
                    
                    time.sleep(random.uniform(0.5, 1.5))
                
                time.sleep(random.uniform(1, 2))
            
            # Strategy 3: Search by terms
            for i, term in enumerate(self.search_terms[:8]):  # Limit for efficiency
                if not term:  # Skip empty term
                    continue
                    
                logger.info(f"Searching with term: {term} ({i+1}/{min(8, len(self.search_terms))})")
                
                for page in range(1, 4):  # Up to 3 pages per term
                    result = self.search_organizations_api(search_term=term, page=page)
                    
                    if result and 'organizations' in result:
                        orgs = result['organizations']
                        if orgs:
                            all_organizations.extend(orgs)
                            logger.info(f"Term '{term}', Page {page}: Found {len(orgs)} organizations")
                            search_count += 1
                            
                            if not result.get('has_more', False) or len(orgs) < 5:
                                break
                        else:
                            break
                    else:
                        break
                    
                    time.sleep(random.uniform(0.5, 1.5))
                
                time.sleep(random.uniform(1, 2))
            
            # Strategy 4: Search by major cities
            for i, city in enumerate(self.cities[:15]):  # Limit for efficiency
                if not city:  # Skip empty city
                    continue
                    
                logger.info(f"Searching in city: {city} ({i+1}/{min(15, len(self.cities))})")
                
                result = self.search_organizations_api(city=city)
                
                if result and 'organizations' in result:
                    orgs = result['organizations']
                    if orgs:
                        all_organizations.extend(orgs)
                        logger.info(f"City {city}: Found {len(orgs)} organizations")
                        search_count += 1
                
                time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error in comprehensive search: {e}")
        
        logger.info(f"Completed {search_count} API calls")
        
        # Remove duplicates and clean data
        self.organizations = self.remove_duplicates_and_clean(all_organizations)
        
        logger.info(f"Total unique organizations found: {len(self.organizations)}")

    def remove_duplicates_and_clean(self, organizations: List[Dict]) -> List[Dict]:
        """Remove duplicates and clean organization data"""
        seen_names = set()
        unique_orgs = []
        
        for org in organizations:
            name = org.get('name', '').lower().strip()
            
            # Skip invalid entries
            if (len(name) < 5 or 
                'skip to content' in name or
                'home' in name and len(name) < 20 or
                'accreditation' in name and len(name) < 30 or
                'nabh' in name and len(name) < 20 or
                'search' in name and len(name) < 20):
                continue
            
            # Check for duplicates
            if name not in seen_names and name:
                seen_names.add(name)
                
                # Clean and validate data
                cleaned_org = self.clean_organization_data(org)
                if cleaned_org:
                    unique_orgs.append(cleaned_org)
        
        removed_count = len(organizations) - len(unique_orgs)
        logger.info(f"Removed {removed_count} duplicate/invalid organizations")
        
        return unique_orgs

    def clean_organization_data(self, org: Dict) -> Dict:
        """Clean and validate organization data"""
        try:
            # Clean name
            name = org.get('name', '').strip()
            if len(name) < 5:
                return None
            
            # Clean address
            address = org.get('address', '').strip()
            
            # Clean phone
            phone = org.get('phone', '').strip()
            phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
            
            # Clean email
            email = org.get('email', '').strip().lower()
            
            # Validate state
            state = org.get('state', 'Unknown').strip()
            if state.lower() in ['unknown', '', 'none']:
                state = 'Unknown'
            
            # Validate city
            city = org.get('city', 'Unknown').strip()
            if city.lower() in ['unknown', '', 'none']:
                city = 'Unknown'
            
            return {
                'name': name,
                'state': state,
                'city': city,
                'country': 'India',
                'accreditation_level': org.get('accreditation_level', 'Unknown'),
                'accreditation_category': org.get('accreditation_category', 'Unknown'),
                'valid_from': org.get('valid_from'),
                'valid_until': org.get('valid_until'),
                'certificate_number': org.get('certificate_number'),
                'address': address,
                'phone': phone,
                'email': email,
                'website': org.get('website', ''),
                'source': 'NABH Official Directory',
                'scraped_date': datetime.now().isoformat(),
                'nabh_url': 'https://nabh.co/find-a-healthcare-organisation/'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning organization data: {e}")
            return None

    def save_data(self):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"optimized_nabh_organizations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"optimized_nabh_organizations_{timestamp}.csv"
        if self.organizations:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = self.organizations[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.organizations)
        
        # Generate summary report
        self.generate_summary_report(timestamp)
        
        logger.info(f"Saved {len(self.organizations)} organizations to {json_filename} and {csv_filename}")

    def generate_summary_report(self, timestamp: str):
        """Generate comprehensive summary report"""
        report = {
            'scraping_date': datetime.now().isoformat(),
            'scraping_method': 'Optimized API-based',
            'total_organizations': len(self.organizations),
            'by_state': {},
            'by_city': {},
            'by_accreditation_level': {},
            'data_quality': {
                'with_certificate_number': 0,
                'with_validity_dates': 0,
                'with_contact_info': 0,
                'with_address': 0,
                'with_complete_data': 0
            },
            'sample_organizations': []
        }
        
        for org in self.organizations:
            # Count by state
            state = org.get('state', 'Unknown')
            report['by_state'][state] = report['by_state'].get(state, 0) + 1
            
            # Count by city
            city = org.get('city', 'Unknown')
            report['by_city'][city] = report['by_city'].get(city, 0) + 1
            
            # Count by accreditation level
            level = org.get('accreditation_level', 'Unknown')
            report['by_accreditation_level'][level] = report['by_accreditation_level'].get(level, 0) + 1
            
            # Data quality metrics
            if org.get('certificate_number'):
                report['data_quality']['with_certificate_number'] += 1
            if org.get('valid_until'):
                report['data_quality']['with_validity_dates'] += 1
            if org.get('phone') or org.get('email'):
                report['data_quality']['with_contact_info'] += 1
            if org.get('address'):
                report['data_quality']['with_address'] += 1
            
            # Complete data check
            if (org.get('certificate_number') and org.get('address') and 
                (org.get('phone') or org.get('email'))):
                report['data_quality']['with_complete_data'] += 1
        
        # Sort by count
        report['by_state'] = dict(sorted(report['by_state'].items(), key=lambda x: x[1], reverse=True))
        report['by_city'] = dict(sorted(report['by_city'].items(), key=lambda x: x[1], reverse=True))
        
        # Add sample organizations
        report['sample_organizations'] = self.organizations[:10]
        
        report_filename = f"optimized_nabh_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_optimized_scraping(self):
        """Run the complete optimized scraping process"""
        logger.info("Starting optimized NABH directory scraping...")
        
        try:
            # Initialize session
            if not self.initialize_session():
                raise Exception("Failed to initialize session")
            
            # Perform comprehensive search
            self.comprehensive_search()
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nOptimized NABH Scraping Completed!")
            print(f"Total organizations scraped: {len(self.organizations)}")
            
            if self.organizations:
                # State distribution
                state_counts = {}
                for org in self.organizations:
                    state = org.get('state', 'Unknown')
                    state_counts[state] = state_counts.get(state, 0) + 1
                
                print(f"\nTop 10 States by Organization Count:")
                for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"{state}: {count}")
                
                # Sample organizations
                print(f"\nSample Organizations:")
                for i, org in enumerate(self.organizations[:5]):
                    print(f"{i+1}. {org.get('name', 'Unknown')} - {org.get('state', 'Unknown')}")
                
                # Data quality summary
                with_cert = sum(1 for org in self.organizations if org.get('certificate_number'))
                with_address = sum(1 for org in self.organizations if org.get('address'))
                with_contact = sum(1 for org in self.organizations if org.get('phone') or org.get('email'))
                
                print(f"\nData Quality:")
                print(f"Organizations with certificate numbers: {with_cert}")
                print(f"Organizations with addresses: {with_address}")
                print(f"Organizations with contact info: {with_contact}")
            
        except Exception as e:
            logger.error(f"Optimized scraping failed: {e}")
            raise

if __name__ == "__main__":
    scraper = OptimizedNABHScraper()
    scraper.run_optimized_scraping()