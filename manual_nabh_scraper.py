import requests
from bs4 import BeautifulSoup
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

class ManualNABHScraper:
    def __init__(self):
        self.base_url = "https://nabh.co"
        self.search_url = "https://nabh.co/find-a-healthcare-organisation/"
        self.organizations = []
        
        # Session for maintaining cookies and headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get_page_content(self, url: str) -> BeautifulSoup:
        """Get page content and parse with BeautifulSoup"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            else:
                logger.error(f"Failed to fetch {url}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_organizations_from_soup(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract organization data from BeautifulSoup object"""
        organizations = []
        
        try:
            # Multiple strategies to find organization data
            
            # Strategy 1: Look for common organization containers
            selectors = [
                'div[class*="organization"]',
                'div[class*="hospital"]',
                'div[class*="result"]',
                'div[class*="card"]',
                'div[class*="listing"]',
                'article',
                'section[class*="org"]',
                'tr[class*="organization"]',
                'tr[class*="hospital"]',
                'li[class*="organization"]',
                'li[class*="hospital"]',
                '.search-result',
                '.org-item',
                '.hospital-item'
            ]
            
            found_elements = []
            
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        found_elements.extend(elements)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: Look for text patterns that might indicate organizations
            if not found_elements:
                # Look for any div or section that contains hospital-like text
                all_divs = soup.find_all(['div', 'section', 'article', 'li', 'tr'])
                
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if self.looks_like_hospital(text):
                        found_elements.append(div)
            
            # Strategy 3: Look for structured data or JSON-LD
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'name' in data:
                        org_data = self.extract_from_json_ld(data)
                        if org_data:
                            organizations.append(org_data)
                except:
                    continue
            
            # Process found elements
            logger.info(f"Processing {len(found_elements)} potential organization elements")
            
            for element in found_elements:
                try:
                    org_data = self.extract_organization_from_element(element)
                    if org_data and org_data.get('name') and len(org_data['name']) > 5:
                        organizations.append(org_data)
                except Exception as e:
                    logger.debug(f"Error extracting from element: {e}")
                    continue
            
            # Strategy 4: Extract from page text if no structured data
            if not organizations:
                organizations = self.extract_from_page_text(soup.get_text())
            
        except Exception as e:
            logger.error(f"Error extracting organizations from soup: {e}")
        
        return organizations

    def looks_like_hospital(self, text: str) -> bool:
        """Check if text looks like it contains hospital information"""
        if len(text) < 10:
            return False
        
        hospital_keywords = [
            'hospital', 'medical center', 'clinic', 'healthcare', 'nursing home',
            'institute', 'foundation', 'trust', 'multispecialty', 'super specialty',
            'cardiac', 'cancer', 'orthopedic', 'eye care', 'dental', 'maternity',
            'children', 'pediatric', 'neuro', 'kidney', 'liver', 'nabh', 'accredited'
        ]
        
        text_lower = text.lower()
        
        # Check if contains hospital keywords
        has_hospital_keyword = any(keyword in text_lower for keyword in hospital_keywords)
        
        # Check if contains location information
        has_location = any(word in text_lower for word in ['road', 'street', 'avenue', 'city', 'state'])
        
        # Check if contains contact information
        has_contact = bool(re.search(r'\d{10}|@.*\.com', text))
        
        return has_hospital_keyword and (has_location or has_contact or len(text) > 50)

    def extract_from_json_ld(self, data: Dict) -> Dict:
        """Extract organization data from JSON-LD structured data"""
        try:
            org_data = {
                'name': data.get('name', ''),
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
            
            # Extract address
            if 'address' in data:
                address_data = data['address']
                if isinstance(address_data, dict):
                    org_data['address'] = address_data.get('streetAddress', '')
                    org_data['city'] = address_data.get('addressLocality', 'Unknown')
                    org_data['state'] = address_data.get('addressRegion', 'Unknown')
                elif isinstance(address_data, str):
                    org_data['address'] = address_data
            
            # Extract contact info
            if 'telephone' in data:
                org_data['phone'] = data['telephone']
            
            if 'email' in data:
                org_data['email'] = data['email']
            
            if 'url' in data:
                org_data['website'] = data['url']
            
            return org_data
            
        except Exception as e:
            logger.error(f"Error extracting from JSON-LD: {e}")
            return None

    def extract_organization_from_element(self, element) -> Dict:
        """Extract organization data from a BeautifulSoup element"""
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
            
            # Get all text from element
            element_text = element.get_text(separator=' ', strip=True)
            
            # Extract name - look for headings first
            name_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if name_elements:
                org_data['name'] = name_elements[0].get_text(strip=True)
            else:
                # Look for strong or bold text
                strong_elements = element.find_all(['strong', 'b'])
                if strong_elements:
                    org_data['name'] = strong_elements[0].get_text(strip=True)
                else:
                    # Use first line of text
                    lines = element_text.split('\n')
                    if lines:
                        org_data['name'] = lines[0].strip()[:100]
            
            # Extract address
            address_patterns = [
                r'Address[:\s]+([^\n]+(?:Road|Street|Avenue|Lane|Plot|Sector)[^\n]*)',
                r'([A-Za-z\s,\-0-9]+(?:Road|Street|Avenue|Lane|Plot|Sector)[^\n]*)',
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, element_text, re.I)
                if match:
                    org_data['address'] = match.group(1).strip()
                    break
            
            # Extract city and state
            city_state_patterns = [
                r'([A-Za-z\s]+),\s*([A-Za-z\s]+)(?:,|\s|$)',
                r'City[:\s]*([A-Za-z\s]+)',
                r'State[:\s]*([A-Za-z\s]+)'
            ]
            
            for pattern in city_state_patterns:
                match = re.search(pattern, element_text, re.I)
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
            phone_match = re.search(r'(?:Phone|Tel|Mobile|Contact)[:\s]*([+\d\s\-\(\)]{10,})', element_text, re.I)
            if phone_match:
                org_data['phone'] = phone_match.group(1).strip()
            else:
                # Look for any phone number pattern
                phone_match = re.search(r'(\+?91[-\s]?\d{10}|\d{10})', element_text)
                if phone_match:
                    org_data['phone'] = phone_match.group(1).strip()
            
            # Extract email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', element_text)
            if email_match:
                org_data['email'] = email_match.group(1)
            
            # Extract website from links
            links = element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('http') and not href.startswith('mailto:'):
                    org_data['website'] = href
                    break
            
            # Extract accreditation details
            if 'full' in element_text.lower():
                org_data['accreditation_level'] = 'Full'
            elif 'entry' in element_text.lower():
                org_data['accreditation_level'] = 'Entry Level'
            elif 'provisional' in element_text.lower():
                org_data['accreditation_level'] = 'Provisional'
            
            # Extract dates
            date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            dates = re.findall(date_pattern, element_text)
            
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
                cert_match = re.search(pattern, element_text, re.I)
                if cert_match:
                    org_data['certificate_number'] = cert_match.group(1)
                    break
            
            return org_data if org_data['name'] else None
            
        except Exception as e:
            logger.error(f"Error extracting organization from element: {e}")
            return None

    def extract_from_page_text(self, page_text: str) -> List[Dict]:
        """Extract organizations from page text using pattern matching"""
        organizations = []
        
        try:
            # Hospital name patterns
            hospital_patterns = [
                r'([A-Za-z\s&]+(?:Hospital|Medical Center|Clinic|Healthcare|Nursing Home)[A-Za-z\s]*)',
                r'([A-Za-z\s&]+(?:Institute|Foundation|Trust)[A-Za-z\s]*)',
                r'(Dr\.?\s+[A-Za-z\s]+(?:Hospital|Clinic|Medical))',
                r'([A-Za-z\s]+(?:Multi[- ]?specialty|Super[- ]?specialty)[A-Za-z\s]*)'
            ]
            
            found_names = set()
            
            for pattern in hospital_patterns:
                matches = re.findall(pattern, page_text, re.I)
                for match in matches:
                    name = match.strip()
                    if len(name) > 5 and name not in found_names:
                        found_names.add(name)
                        
                        org_data = {
                            'name': name,
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
                        
                        organizations.append(org_data)
            
            logger.info(f"Extracted {len(organizations)} organizations from page text")
            
        except Exception as e:
            logger.error(f"Error extracting from page text: {e}")
        
        return organizations

    def scrape_main_page(self):
        """Scrape the main search page"""
        logger.info("Scraping main NABH search page...")
        
        soup = self.get_page_content(self.search_url)
        if soup:
            organizations = self.extract_organizations_from_soup(soup)
            self.organizations.extend(organizations)
            logger.info(f"Found {len(organizations)} organizations on main page")

    def try_different_urls(self):
        """Try different URL patterns to find organization data"""
        logger.info("Trying different URL patterns...")
        
        # Common URL patterns for healthcare directories
        url_patterns = [
            "https://nabh.co/accredited-organizations/",
            "https://nabh.co/hospitals/",
            "https://nabh.co/directory/",
            "https://nabh.co/search/",
            "https://nabh.co/list/",
            "https://nabh.co/organizations/",
            "https://nabh.co/members/",
            "https://nabh.co/certified/",
            "https://nabh.co/accredited/"
        ]
        
        for url in url_patterns:
            try:
                soup = self.get_page_content(url)
                if soup:
                    organizations = self.extract_organizations_from_soup(soup)
                    if organizations:
                        self.organizations.extend(organizations)
                        logger.info(f"Found {len(organizations)} organizations at {url}")
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.debug(f"Failed to scrape {url}: {e}")
                continue

    def search_with_forms(self):
        """Try to find and submit search forms"""
        logger.info("Looking for search forms...")
        
        soup = self.get_page_content(self.search_url)
        if not soup:
            return
        
        # Find all forms
        forms = soup.find_all('form')
        logger.info(f"Found {len(forms)} forms on the page")
        
        for i, form in enumerate(forms):
            try:
                # Get form action and method
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                
                # Find form inputs
                inputs = form.find_all(['input', 'select', 'textarea'])
                
                form_data = {}
                
                for inp in inputs:
                    input_type = inp.get('type', 'text')
                    input_name = inp.get('name', '')
                    
                    if input_name and input_type not in ['submit', 'button']:
                        if input_type == 'hidden':
                            form_data[input_name] = inp.get('value', '')
                        elif inp.name == 'select':
                            # For select elements, try first option
                            options = inp.find_all('option')
                            if options and len(options) > 1:
                                form_data[input_name] = options[1].get('value', '')
                        else:
                            # For text inputs, try some search terms
                            if 'search' in input_name.lower() or 'query' in input_name.lower():
                                form_data[input_name] = 'hospital'
                
                if form_data:
                    logger.info(f"Submitting form {i} with data: {form_data}")
                    
                    # Submit form
                    if action:
                        submit_url = urljoin(self.search_url, action)
                    else:
                        submit_url = self.search_url
                    
                    if method == 'POST':
                        response = self.session.post(submit_url, data=form_data, timeout=30)
                    else:
                        response = self.session.get(submit_url, params=form_data, timeout=30)
                    
                    if response.status_code == 200:
                        result_soup = BeautifulSoup(response.content, 'html.parser')
                        organizations = self.extract_organizations_from_soup(result_soup)
                        
                        if organizations:
                            self.organizations.extend(organizations)
                            logger.info(f"Form {i} returned {len(organizations)} organizations")
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.debug(f"Error with form {i}: {e}")
                continue

    def remove_duplicates_and_clean(self):
        """Remove duplicates and clean organization data"""
        seen_names = set()
        unique_orgs = []
        
        for org in self.organizations:
            name = org.get('name', '').lower().strip()
            
            # Skip invalid entries
            if (len(name) < 5 or 
                'skip to content' in name or
                'home' in name and len(name) < 20 or
                'accreditation' in name and len(name) < 30 or
                'nabh' in name and len(name) < 20 or
                'search' in name and len(name) < 20 or
                'menu' in name and len(name) < 20):
                continue
            
            # Check for duplicates
            if name not in seen_names and name:
                seen_names.add(name)
                unique_orgs.append(org)
        
        removed_count = len(self.organizations) - len(unique_orgs)
        logger.info(f"Removed {removed_count} duplicate/invalid organizations")
        
        self.organizations = unique_orgs

    def save_data(self):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"manual_nabh_organizations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"manual_nabh_organizations_{timestamp}.csv"
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
            'scraping_method': 'Manual HTML parsing',
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
        
        report_filename = f"manual_nabh_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_manual_scraping(self):
        """Run the complete manual scraping process"""
        logger.info("Starting manual NABH directory scraping...")
        
        try:
            # Scrape main page
            self.scrape_main_page()
            
            # Try different URL patterns
            self.try_different_urls()
            
            # Try form submissions
            self.search_with_forms()
            
            # Clean and deduplicate
            self.remove_duplicates_and_clean()
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nManual NABH Scraping Completed!")
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
            logger.error(f"Manual scraping failed: {e}")
            raise

if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("BeautifulSoup4 is required. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'beautifulsoup4'])
        from bs4 import BeautifulSoup
    
    scraper = ManualNABHScraper()
    scraper.run_manual_scraping()