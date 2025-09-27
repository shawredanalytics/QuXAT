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

class AdvancedNABHScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://nabh.co/find-a-healthcare-organisation/'
        })
        
        self.base_url = "https://nabh.co"
        self.search_url = "https://nabh.co/find-a-healthcare-organisation/"
        self.ajax_url = "https://nabh.co/search/ajax"
        self.organizations = []
        self.processed_urls = set()
        self.failed_urls = set()
        
        # Search parameters based on analysis
        self.search_params = [
            {'state': 'Maharashtra'},
            {'state': 'Karnataka'},
            {'state': 'Tamil Nadu'},
            {'state': 'Delhi'},
            {'state': 'Gujarat'},
            {'state': 'Rajasthan'},
            {'state': 'Uttar Pradesh'},
            {'state': 'West Bengal'},
            {'state': 'Andhra Pradesh'},
            {'state': 'Telangana'},
            {'state': 'Kerala'},
            {'state': 'Punjab'},
            {'state': 'Haryana'},
            {'state': 'Madhya Pradesh'},
            {'state': 'Bihar'},
            {'state': 'Odisha'},
            {'category': 'Hospital'},
            {'category': 'Small Healthcare Organization'},
            {'category': 'Nursing Home'},
            {'category': 'Blood Bank'},
            {'category': 'Laboratory'},
            {'search': 'hospital'},
            {'search': 'clinic'},
            {'search': 'medical'},
            {'search': 'healthcare'},
            {'q': 'mumbai'},
            {'q': 'delhi'},
            {'q': 'bangalore'},
            {'q': 'chennai'},
            {'q': 'hyderabad'},
            {'q': 'pune'},
            {'q': 'kolkata'},
            {'q': 'ahmedabad'},
            {'q': 'jaipur'},
            {'q': 'lucknow'}
        ]

    def get_page_content(self, url: str, params: Dict = None) -> Optional[BeautifulSoup]:
        """Get page content with error handling"""
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                logger.warning(f"HTTP {response.status_code} for {url} with params {params}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def try_ajax_search(self, params: Dict) -> List[Dict]:
        """Try AJAX search endpoint"""
        try:
            # Try different AJAX request formats
            ajax_attempts = [
                # POST request
                lambda: self.session.post(self.ajax_url, data=params),
                # GET request
                lambda: self.session.get(self.ajax_url, params=params),
                # JSON POST
                lambda: self.session.post(self.ajax_url, json=params, 
                                        headers={'Content-Type': 'application/json'})
            ]
            
            for attempt in ajax_attempts:
                try:
                    response = attempt()
                    
                    if response.status_code == 200:
                        # Try to parse as JSON
                        try:
                            data = response.json()
                            logger.info(f"AJAX JSON response received for {params}")
                            return self.parse_ajax_json_response(data)
                        except:
                            # Try to parse as HTML
                            soup = BeautifulSoup(response.content, 'html.parser')
                            return self.parse_html_response(soup, params)
                            
                except Exception as e:
                    logger.debug(f"AJAX attempt failed: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"AJAX search failed for {params}: {e}")
        
        return []

    def parse_ajax_json_response(self, data) -> List[Dict]:
        """Parse JSON response from AJAX endpoint"""
        organizations = []
        
        try:
            # Handle different JSON response formats
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                elif 'data' in data:
                    results = data['data']
                elif 'organizations' in data:
                    results = data['organizations']
                else:
                    results = [data]  # Single organization
            elif isinstance(data, list):
                results = data
            else:
                return []
            
            for item in results:
                if isinstance(item, dict):
                    org_data = self.extract_organization_from_json(item)
                    if org_data and org_data.get('name'):
                        organizations.append(org_data)
            
            logger.info(f"Parsed {len(organizations)} organizations from JSON response")
            
        except Exception as e:
            logger.error(f"Error parsing JSON response: {e}")
        
        return organizations

    def extract_organization_from_json(self, item: Dict) -> Dict:
        """Extract organization data from JSON item"""
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
                'nabh_url': self.search_url
            }
            
            # Map common JSON fields
            field_mappings = {
                'name': ['name', 'organization_name', 'hospital_name', 'title'],
                'state': ['state', 'state_name', 'location_state'],
                'city': ['city', 'city_name', 'location_city'],
                'address': ['address', 'full_address', 'location'],
                'phone': ['phone', 'contact_number', 'mobile'],
                'email': ['email', 'email_address', 'contact_email'],
                'website': ['website', 'url', 'web_url'],
                'accreditation_level': ['level', 'accreditation_level', 'grade'],
                'accreditation_category': ['category', 'type', 'organization_type'],
                'certificate_number': ['certificate_no', 'cert_number', 'registration_no'],
                'valid_from': ['valid_from', 'start_date', 'issue_date'],
                'valid_until': ['valid_until', 'end_date', 'expiry_date']
            }
            
            for org_field, json_fields in field_mappings.items():
                for json_field in json_fields:
                    if json_field in item and item[json_field]:
                        org_data[org_field] = str(item[json_field]).strip()
                        break
            
            return org_data
            
        except Exception as e:
            logger.error(f"Error extracting organization from JSON: {e}")
            return {}

    def parse_html_response(self, soup: BeautifulSoup, search_params: Dict) -> List[Dict]:
        """Parse HTML response for organization data"""
        organizations = []
        
        try:
            # Look for organization containers with various selectors
            selectors = [
                # Common organization card patterns
                'div[class*="organization"]',
                'div[class*="hospital"]',
                'div[class*="result"]',
                'div[class*="card"]',
                'div[class*="listing"]',
                'article',
                'section[class*="org"]',
                # Table rows
                'tr[class*="organization"]',
                'tr[class*="hospital"]',
                'tbody tr',
                # List items
                'li[class*="organization"]',
                'li[class*="hospital"]',
                # Generic containers with data attributes
                'div[data-name]',
                'div[data-organization]',
                'div[data-hospital]'
            ]
            
            found_containers = []
            for selector in selectors:
                try:
                    containers = soup.select(selector)
                    if containers:
                        found_containers.extend(containers)
                        logger.info(f"Found {len(containers)} containers with selector: {selector}")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
            
            # Remove duplicates
            unique_containers = []
            seen_elements = set()
            
            for container in found_containers:
                element_id = id(container)
                if element_id not in seen_elements:
                    seen_elements.add(element_id)
                    unique_containers.append(container)
            
            logger.info(f"Processing {len(unique_containers)} unique containers")
            
            for container in unique_containers:
                org_data = self.extract_organization_from_html(container, search_params)
                if org_data and org_data.get('name') and len(org_data['name']) > 2:
                    organizations.append(org_data)
            
            # If no organizations found, try to extract from any text content
            if not organizations:
                organizations = self.extract_from_text_content(soup, search_params)
            
        except Exception as e:
            logger.error(f"Error parsing HTML response: {e}")
        
        return organizations

    def extract_organization_from_html(self, container, search_params: Dict) -> Dict:
        """Extract organization data from HTML container"""
        try:
            org_data = {
                'name': '',
                'state': search_params.get('state', 'Unknown'),
                'city': 'Unknown',
                'country': 'India',
                'accreditation_level': 'Unknown',
                'accreditation_category': search_params.get('category', 'Unknown'),
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
            
            # Extract name - try multiple approaches
            name_selectors = [
                'h1, h2, h3, h4, h5, h6',
                '[class*="name"]',
                '[class*="title"]',
                '[class*="hospital"]',
                '[class*="organization"]',
                'strong',
                'b',
                '.name',
                '.title',
                '.hospital-name',
                '.org-name'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = container.select_one(selector)
                    if name_elem and name_elem.get_text(strip=True):
                        org_data['name'] = name_elem.get_text(strip=True)
                        break
                except:
                    continue
            
            # If no name found, use data attributes
            if not org_data['name']:
                for attr in ['data-name', 'data-hospital', 'data-organization', 'title']:
                    if container.get(attr):
                        org_data['name'] = container.get(attr)
                        break
            
            # If still no name, use first text content
            if not org_data['name']:
                text_content = container.get_text(strip=True)
                if text_content:
                    # Take first line or first 100 characters
                    first_line = text_content.split('\n')[0].strip()
                    org_data['name'] = first_line[:100] if len(first_line) > 5 else text_content[:100]
            
            # Extract other information from text content
            all_text = container.get_text()
            
            # Extract address
            address_patterns = [
                r'Address[:\s]+([^\n]+)',
                r'Location[:\s]+([^\n]+)',
                r'([A-Za-z\s,\-0-9]+(?:Road|Street|Avenue|Lane|Plot|Sector)[^\n]*)',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, all_text, re.I)
                if match:
                    org_data['address'] = match.group(1).strip()
                    break
            
            # Extract city and state from address or text
            if org_data['address']:
                # Try to extract city from address
                city_match = re.search(r'([A-Za-z\s]+),\s*([A-Za-z\s]+)$', org_data['address'])
                if city_match:
                    org_data['city'] = city_match.group(1).strip()
                    if org_data['state'] == 'Unknown':
                        org_data['state'] = city_match.group(2).strip()
            
            # Extract phone
            phone_match = re.search(r'(?:Phone|Tel|Mobile|Contact)[:\s]*([+\d\s\-\(\)]{10,})', all_text, re.I)
            if phone_match:
                org_data['phone'] = phone_match.group(1).strip()
            
            # Extract email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', all_text)
            if email_match:
                org_data['email'] = email_match.group(1)
            
            # Extract website
            website_elem = container.select_one('a[href^="http"]')
            if website_elem:
                href = website_elem.get('href')
                if href and not href.startswith('mailto:'):
                    org_data['website'] = href
            
            # Extract accreditation details
            accred_keywords = ['full', 'entry', 'provisional', 'level', 'grade']
            for keyword in accred_keywords:
                if keyword.lower() in all_text.lower():
                    if 'full' in all_text.lower():
                        org_data['accreditation_level'] = 'Full'
                    elif 'entry' in all_text.lower():
                        org_data['accreditation_level'] = 'Entry Level'
                    elif 'provisional' in all_text.lower():
                        org_data['accreditation_level'] = 'Provisional'
                    break
            
            # Extract dates
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            dates = re.findall(date_pattern, all_text)
            
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
                cert_match = re.search(pattern, all_text, re.I)
                if cert_match:
                    org_data['certificate_number'] = cert_match.group(1)
                    break
            
            return org_data
            
        except Exception as e:
            logger.error(f"Error extracting organization from HTML: {e}")
            return {}

    def extract_from_text_content(self, soup: BeautifulSoup, search_params: Dict) -> List[Dict]:
        """Extract organizations from general text content if no structured data found"""
        organizations = []
        
        try:
            # Look for hospital/organization names in text
            text_content = soup.get_text()
            
            # Common hospital name patterns
            hospital_patterns = [
                r'([A-Za-z\s&]+(?:Hospital|Medical Center|Clinic|Healthcare|Nursing Home)[A-Za-z\s]*)',
                r'([A-Za-z\s&]+(?:Institute|Foundation|Trust)[A-Za-z\s]*)',
                r'(Dr\.?\s+[A-Za-z\s]+(?:Hospital|Clinic|Medical))',
                r'([A-Za-z\s]+(?:Multi[- ]?specialty|Super[- ]?specialty)[A-Za-z\s]*)'
            ]
            
            found_names = set()
            
            for pattern in hospital_patterns:
                matches = re.findall(pattern, text_content, re.I)
                for match in matches:
                    name = match.strip()
                    if len(name) > 5 and name not in found_names:
                        found_names.add(name)
                        
                        org_data = {
                            'name': name,
                            'state': search_params.get('state', 'Unknown'),
                            'city': 'Unknown',
                            'country': 'India',
                            'accreditation_level': 'Unknown',
                            'accreditation_category': search_params.get('category', 'Unknown'),
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
                        
                        organizations.append(org_data)
            
            logger.info(f"Extracted {len(organizations)} organizations from text content")
            
        except Exception as e:
            logger.error(f"Error extracting from text content: {e}")
        
        return organizations

    def scrape_with_params(self, params: Dict) -> List[Dict]:
        """Scrape organizations with specific parameters"""
        organizations = []
        
        try:
            logger.info(f"Scraping with parameters: {params}")
            
            # Try AJAX first
            ajax_orgs = self.try_ajax_search(params)
            if ajax_orgs:
                organizations.extend(ajax_orgs)
                logger.info(f"Found {len(ajax_orgs)} organizations via AJAX")
            
            # Try regular HTTP request
            soup = self.get_page_content(self.search_url, params)
            if soup:
                html_orgs = self.parse_html_response(soup, params)
                if html_orgs:
                    organizations.extend(html_orgs)
                    logger.info(f"Found {len(html_orgs)} organizations via HTML")
            
            # Try with pagination
            for page in range(1, 6):  # Try first 5 pages
                page_params = params.copy()
                page_params['page'] = page
                
                soup = self.get_page_content(self.search_url, page_params)
                if soup:
                    page_orgs = self.parse_html_response(soup, page_params)
                    if page_orgs:
                        organizations.extend(page_orgs)
                        logger.info(f"Found {len(page_orgs)} organizations on page {page}")
                    else:
                        break  # No more results
                
                time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.error(f"Error scraping with params {params}: {e}")
        
        return organizations

    def scrape_all_organizations(self):
        """Scrape all organizations using various search parameters"""
        logger.info("Starting advanced NABH organization scraping...")
        
        all_organizations = []
        
        for i, params in enumerate(self.search_params):
            logger.info(f"Progress: {i+1}/{len(self.search_params)} - {params}")
            
            try:
                orgs = self.scrape_with_params(params)
                if orgs:
                    all_organizations.extend(orgs)
                    logger.info(f"Total organizations so far: {len(all_organizations)}")
                
                # Rate limiting
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Error with params {params}: {e}")
                continue
        
        # Remove duplicates
        self.organizations = self.remove_duplicates(all_organizations)
        
        logger.info(f"Completed scraping. Total unique organizations: {len(self.organizations)}")

    def remove_duplicates(self, organizations: List[Dict]) -> List[Dict]:
        """Remove duplicate organizations"""
        seen = set()
        unique_orgs = []
        
        for org in organizations:
            # Create a unique key based on name and address
            name = org.get('name', '').lower().strip()
            address = org.get('address', '').lower().strip()
            key = f"{name}_{address}"
            
            if key not in seen and name and len(name) > 2:
                seen.add(key)
                unique_orgs.append(org)
        
        removed_count = len(organizations) - len(unique_orgs)
        logger.info(f"Removed {removed_count} duplicate organizations")
        
        return unique_orgs

    def save_data(self):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"advanced_nabh_organizations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"advanced_nabh_organizations_{timestamp}.csv"
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
        
        report_filename = f"advanced_nabh_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_advanced_scraping(self):
        """Run the complete advanced scraping process"""
        logger.info("Starting advanced NABH directory scraping...")
        
        try:
            # Scrape all organizations
            self.scrape_all_organizations()
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nAdvanced NABH Scraping Completed!")
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
                
                # Category distribution
                category_counts = {}
                for org in self.organizations:
                    category = org.get('accreditation_category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                print(f"\nAccreditation Categories:")
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"{category}: {count}")
                
                # Sample organizations
                print(f"\nSample Organizations:")
                for i, org in enumerate(self.organizations[:5]):
                    print(f"{i+1}. {org.get('name', 'Unknown')} - {org.get('state', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Advanced scraping failed: {e}")
            raise

if __name__ == "__main__":
    scraper = AdvancedNABHScraper()
    scraper.run_advanced_scraping()