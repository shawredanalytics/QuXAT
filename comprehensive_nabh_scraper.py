import requests
import json
import csv
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
import re
import random
from urllib.parse import urljoin, urlparse, parse_qs
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveNABHScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.base_url = "https://nabh.co"
        self.search_url = "https://nabh.co/find-a-healthcare-organisation/"
        self.organizations = []
        self.processed_urls = set()
        self.failed_urls = set()
        
        # Indian states for comprehensive coverage
        self.indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
            'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
            'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Chandigarh', 'Dadra and Nagar Haveli',
            'Daman and Diu', 'Lakshadweep', 'Puducherry', 'Andaman and Nicobar Islands'
        ]
        
        # NABH accreditation categories
        self.accreditation_categories = [
            'Hospital', 'Small Healthcare Organization', 'Nursing Home',
            'Ayush Hospital', 'Blood Bank', 'Wellness Centre', 'Laboratory',
            'Imaging Centre', 'Dental Care Organization', 'Home Healthcare',
            'Transport of Critically Ill Patient', 'Pre-Hospital Emergency Care'
        ]

    def get_csrf_token(self, url: str) -> Optional[str]:
        """Extract CSRF token from the page if required"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                csrf_token = soup.find('input', {'name': '_token'})
                if csrf_token:
                    return csrf_token.get('value')
                
                # Alternative CSRF token locations
                csrf_meta = soup.find('meta', {'name': 'csrf-token'})
                if csrf_meta:
                    return csrf_meta.get('content')
                    
        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
        
        return None

    def analyze_search_form(self) -> Dict:
        """Analyze the search form structure to understand available filters"""
        try:
            logger.info("Analyzing NABH search form structure...")
            response = self.session.get(self.search_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to access search page: {response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find form elements
            form_data = {
                'states': [],
                'categories': [],
                'form_action': None,
                'form_method': 'GET'
            }
            
            # Look for state dropdown/options
            state_select = soup.find('select', {'name': re.compile(r'state|location', re.I)})
            if state_select:
                options = state_select.find_all('option')
                form_data['states'] = [opt.get('value') for opt in options if opt.get('value')]
            
            # Look for category dropdown/options
            category_select = soup.find('select', {'name': re.compile(r'category|type', re.I)})
            if category_select:
                options = category_select.find_all('option')
                form_data['categories'] = [opt.get('value') for opt in options if opt.get('value')]
            
            # Find form action
            form = soup.find('form')
            if form:
                form_data['form_action'] = form.get('action', '')
                form_data['form_method'] = form.get('method', 'GET').upper()
            
            logger.info(f"Found {len(form_data['states'])} states and {len(form_data['categories'])} categories")
            return form_data
            
        except Exception as e:
            logger.error(f"Error analyzing search form: {e}")
            return {}

    def search_organizations(self, state: str = None, category: str = None, page: int = 1) -> List[Dict]:
        """Search for organizations with specific filters"""
        try:
            # Prepare search parameters
            params = {}
            
            if state:
                params['state'] = state
            if category:
                params['category'] = category
            if page > 1:
                params['page'] = page
            
            # Make search request
            response = self.session.get(self.search_url, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Search failed for state={state}, category={category}, page={page}: {response.status_code}")
                return []
            
            return self.parse_search_results(response.content, state, category)
            
        except Exception as e:
            logger.error(f"Error searching organizations: {e}")
            return []

    def parse_search_results(self, html_content: bytes, state: str = None, category: str = None) -> List[Dict]:
        """Parse search results from HTML content"""
        organizations = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for organization cards/listings
            # Common patterns for healthcare organization listings
            org_containers = soup.find_all(['div', 'article', 'section'], 
                                         class_=re.compile(r'organization|hospital|healthcare|result|card|listing', re.I))
            
            if not org_containers:
                # Try alternative selectors
                org_containers = soup.find_all(['div', 'tr'], 
                                             attrs={'data-organization': True}) or \
                               soup.find_all(['div'], 
                                           class_=re.compile(r'row|item|entry', re.I))
            
            for container in org_containers:
                org_data = self.extract_organization_data(container, state, category)
                if org_data and org_data.get('name'):
                    organizations.append(org_data)
            
            # Look for pagination info
            pagination_info = self.extract_pagination_info(soup)
            
            logger.info(f"Parsed {len(organizations)} organizations from search results")
            
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
        
        return organizations

    def extract_organization_data(self, container, state: str = None, category: str = None) -> Dict:
        """Extract organization data from a container element"""
        try:
            org_data = {
                'name': '',
                'state': state or 'Unknown',
                'city': 'Unknown',
                'country': 'India',
                'accreditation_level': 'Unknown',
                'accreditation_category': category or 'Unknown',
                'valid_from': None,
                'valid_until': None,
                'certificate_number': None,
                'address': '',
                'phone': '',
                'email': '',
                'website': '',
                'source': 'NABH Official Directory',
                'scraped_date': datetime.now().isoformat(),
                'nabh_url': self.search_url
            }
            
            # Extract organization name
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']) or \
                       container.find(class_=re.compile(r'name|title|heading', re.I)) or \
                       container.find(attrs={'data-name': True})
            
            if name_elem:
                org_data['name'] = name_elem.get_text(strip=True)
            
            # Extract address/location
            address_elem = container.find(class_=re.compile(r'address|location|city', re.I)) or \
                          container.find(text=re.compile(r'Address|Location', re.I))
            
            if address_elem:
                if hasattr(address_elem, 'get_text'):
                    org_data['address'] = address_elem.get_text(strip=True)
                else:
                    # If it's a text node, get the parent's text
                    parent = address_elem.parent if address_elem.parent else address_elem
                    org_data['address'] = parent.get_text(strip=True) if hasattr(parent, 'get_text') else str(address_elem)
            
            # Extract city from address
            if org_data['address']:
                city_match = re.search(r'([A-Za-z\s]+),\s*([A-Za-z\s]+)$', org_data['address'])
                if city_match:
                    org_data['city'] = city_match.group(1).strip()
                    if not state:
                        org_data['state'] = city_match.group(2).strip()
            
            # Extract accreditation details
            accred_elem = container.find(class_=re.compile(r'accreditation|certificate|level', re.I))
            if accred_elem:
                accred_text = accred_elem.get_text(strip=True)
                
                # Extract accreditation level
                if 'full' in accred_text.lower():
                    org_data['accreditation_level'] = 'Full'
                elif 'entry' in accred_text.lower():
                    org_data['accreditation_level'] = 'Entry Level'
                elif 'provisional' in accred_text.lower():
                    org_data['accreditation_level'] = 'Provisional'
            
            # Extract validity dates
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            all_text = container.get_text()
            dates = re.findall(date_pattern, all_text)
            
            if len(dates) >= 2:
                org_data['valid_from'] = dates[0]
                org_data['valid_until'] = dates[1]
            elif len(dates) == 1:
                org_data['valid_until'] = dates[0]
            
            # Extract certificate number
            cert_match = re.search(r'(?:Certificate|Cert|Ref)\.?\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9/-]+)', all_text, re.I)
            if cert_match:
                org_data['certificate_number'] = cert_match.group(1)
            
            # Extract contact information
            phone_match = re.search(r'(?:Phone|Tel|Mobile)\.?\s*:?\s*([\d\s\-\+\(\)]+)', all_text, re.I)
            if phone_match:
                org_data['phone'] = phone_match.group(1).strip()
            
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', all_text)
            if email_match:
                org_data['email'] = email_match.group(1)
            
            # Extract website
            website_elem = container.find('a', href=re.compile(r'http'))
            if website_elem:
                href = website_elem.get('href')
                if href and not href.startswith('mailto:'):
                    org_data['website'] = href
            
            return org_data
            
        except Exception as e:
            logger.error(f"Error extracting organization data: {e}")
            return {}

    def extract_pagination_info(self, soup) -> Dict:
        """Extract pagination information"""
        pagination_info = {
            'current_page': 1,
            'total_pages': 1,
            'has_next': False,
            'next_url': None
        }
        
        try:
            # Look for pagination elements
            pagination = soup.find(['nav', 'div'], class_=re.compile(r'pagination|pager', re.I))
            
            if pagination:
                # Extract current page
                current = pagination.find(class_=re.compile(r'current|active', re.I))
                if current:
                    try:
                        pagination_info['current_page'] = int(current.get_text(strip=True))
                    except ValueError:
                        pass
                
                # Extract total pages
                page_links = pagination.find_all('a', href=True)
                page_numbers = []
                
                for link in page_links:
                    try:
                        page_num = int(link.get_text(strip=True))
                        page_numbers.append(page_num)
                    except ValueError:
                        continue
                
                if page_numbers:
                    pagination_info['total_pages'] = max(page_numbers)
                
                # Check for next page
                next_link = pagination.find('a', text=re.compile(r'next|>', re.I))
                if next_link:
                    pagination_info['has_next'] = True
                    pagination_info['next_url'] = next_link.get('href')
        
        except Exception as e:
            logger.error(f"Error extracting pagination info: {e}")
        
        return pagination_info

    def scrape_all_organizations(self):
        """Scrape all organizations from NABH directory"""
        logger.info("Starting comprehensive NABH organization scraping...")
        
        # First, analyze the search form
        form_data = self.analyze_search_form()
        
        # If we have specific states and categories, use them
        states_to_search = form_data.get('states', []) or self.indian_states
        categories_to_search = form_data.get('categories', []) or self.accreditation_categories
        
        # If no specific filters found, try general search
        if not states_to_search and not categories_to_search:
            logger.info("No specific filters found, attempting general search...")
            self.scrape_general_search()
        else:
            # Search with filters
            for state in states_to_search[:5]:  # Limit to first 5 states for testing
                for category in categories_to_search[:3]:  # Limit to first 3 categories
                    logger.info(f"Searching for {category} in {state}...")
                    
                    page = 1
                    while page <= 10:  # Limit to 10 pages per combination
                        orgs = self.search_organizations(state, category, page)
                        
                        if not orgs:
                            break
                        
                        self.organizations.extend(orgs)
                        page += 1
                        
                        # Rate limiting
                        time.sleep(random.uniform(1, 3))
                    
                    # Rate limiting between searches
                    time.sleep(random.uniform(2, 5))
        
        # Remove duplicates
        self.remove_duplicates()
        
        logger.info(f"Completed scraping. Total organizations found: {len(self.organizations)}")

    def scrape_general_search(self):
        """Scrape with general search if specific filters are not available"""
        try:
            logger.info("Performing general search...")
            
            page = 1
            while page <= 50:  # Limit to 50 pages for general search
                logger.info(f"Scraping page {page}...")
                
                orgs = self.search_organizations(page=page)
                
                if not orgs:
                    logger.info(f"No more organizations found at page {page}")
                    break
                
                self.organizations.extend(orgs)
                page += 1
                
                # Rate limiting
                time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.error(f"Error in general search: {e}")

    def remove_duplicates(self):
        """Remove duplicate organizations based on name and address"""
        seen = set()
        unique_orgs = []
        
        for org in self.organizations:
            # Create a unique key based on name and address
            key = f"{org.get('name', '').lower().strip()}_{org.get('address', '').lower().strip()}"
            
            if key not in seen and org.get('name'):
                seen.add(key)
                unique_orgs.append(org)
        
        removed_count = len(self.organizations) - len(unique_orgs)
        self.organizations = unique_orgs
        
        logger.info(f"Removed {removed_count} duplicate organizations")

    def enhance_with_existing_data(self):
        """Enhance scraped data with existing NABH data if available"""
        try:
            existing_files = ['nabh_hospitals.json', 'processed_nabh_hospitals.json']
            
            for filename in existing_files:
                if os.path.exists(filename):
                    logger.info(f"Enhancing with existing data from {filename}")
                    
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    
                    # Create lookup dictionary
                    existing_lookup = {}
                    for org in existing_data:
                        if isinstance(org, dict) and org.get('name'):
                            key = org['name'].lower().strip()
                            existing_lookup[key] = org
                    
                    # Enhance current data
                    enhanced_count = 0
                    for org in self.organizations:
                        key = org.get('name', '').lower().strip()
                        if key in existing_lookup:
                            existing_org = existing_lookup[key]
                            
                            # Enhance with additional data
                            if not org.get('certificate_number') and existing_org.get('certificate_number'):
                                org['certificate_number'] = existing_org['certificate_number']
                            
                            if not org.get('valid_until') and existing_org.get('valid_until'):
                                org['valid_until'] = existing_org['valid_until']
                            
                            if not org.get('accreditation_level') and existing_org.get('accreditation_level'):
                                org['accreditation_level'] = existing_org['accreditation_level']
                            
                            enhanced_count += 1
                    
                    logger.info(f"Enhanced {enhanced_count} organizations with existing data")
                    break
                    
        except Exception as e:
            logger.error(f"Error enhancing with existing data: {e}")

    def save_data(self):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"comprehensive_nabh_organizations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"comprehensive_nabh_organizations_{timestamp}.csv"
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
            'total_organizations': len(self.organizations),
            'by_state': {},
            'by_category': {},
            'by_accreditation_level': {},
            'data_quality': {
                'with_certificate_number': 0,
                'with_validity_dates': 0,
                'with_contact_info': 0,
                'with_address': 0
            }
        }
        
        for org in self.organizations:
            # Count by state
            state = org.get('state', 'Unknown')
            report['by_state'][state] = report['by_state'].get(state, 0) + 1
            
            # Count by category
            category = org.get('accreditation_category', 'Unknown')
            report['by_category'][category] = report['by_category'].get(category, 0) + 1
            
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
        
        # Sort by count
        report['by_state'] = dict(sorted(report['by_state'].items(), key=lambda x: x[1], reverse=True))
        report['by_category'] = dict(sorted(report['by_category'].items(), key=lambda x: x[1], reverse=True))
        
        report_filename = f"comprehensive_nabh_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_comprehensive_scraping(self):
        """Run the complete comprehensive scraping process"""
        logger.info("Starting comprehensive NABH directory scraping...")
        
        try:
            # Scrape all organizations
            self.scrape_all_organizations()
            
            # Enhance with existing data
            self.enhance_with_existing_data()
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nComprehensive NABH Scraping Completed!")
            print(f"Total organizations scraped: {len(self.organizations)}")
            
            # State distribution
            state_counts = {}
            for org in self.organizations:
                state = org.get('state', 'Unknown')
                state_counts[state] = state_counts.get(state, 0) + 1
            
            print(f"\nTop 10 States by Organization Count:")
            for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{state}: {count}")
            
            # Category distribution
            category_counts = {}
            for org in self.organizations:
                category = org.get('accreditation_category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            print(f"\nAccreditation Categories:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{category}: {count}")
            
        except Exception as e:
            logger.error(f"Comprehensive scraping failed: {e}")
            raise

if __name__ == "__main__":
    scraper = ComprehensiveNABHScraper()
    scraper.run_comprehensive_scraping()