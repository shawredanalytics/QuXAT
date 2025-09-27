import json
import csv
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import random
import os

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Please install: pip install selenium")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeleniumNABHScraper:
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for this scraper. Please install: pip install selenium")
        
        self.base_url = "https://nabh.co"
        self.search_url = "https://nabh.co/find-a-healthcare-organisation/"
        self.organizations = []
        self.driver = None
        
        # Search strategies
        self.search_terms = [
            "hospital", "medical", "healthcare", "clinic", "nursing", "diagnostic",
            "mumbai", "delhi", "bangalore", "chennai", "hyderabad", "pune", "kolkata",
            "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane",
            "bhopal", "visakhapatnam", "pimpri", "patna", "vadodara", "ghaziabad",
            "ludhiana", "agra", "nashik", "faridabad", "meerut", "rajkot", "kalyan",
            "vasai", "varanasi", "srinagar", "aurangabad", "dhanbad", "amritsar",
            "navi mumbai", "allahabad", "ranchi", "howrah", "coimbatore", "jabalpur"
        ]
        
        self.states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi", "Jammu and Kashmir", "Ladakh"
        ]

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Disable images and CSS for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome driver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False

    def navigate_to_search_page(self):
        """Navigate to the NABH search page"""
        try:
            logger.info("Navigating to NABH search page...")
            self.driver.get(self.search_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # Additional wait for dynamic content
            
            logger.info("Successfully navigated to search page")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to search page: {e}")
            return False

    def analyze_page_structure(self):
        """Analyze the current page structure to understand available elements"""
        try:
            logger.info("Analyzing page structure...")
            
            # Find all input elements
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {len(inputs)} input elements")
            
            for i, inp in enumerate(inputs[:10]):  # Limit to first 10
                try:
                    input_type = inp.get_attribute("type")
                    input_name = inp.get_attribute("name")
                    input_id = inp.get_attribute("id")
                    input_placeholder = inp.get_attribute("placeholder")
                    
                    logger.info(f"Input {i}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
                except:
                    continue
            
            # Find all select elements
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            logger.info(f"Found {len(selects)} select elements")
            
            for i, sel in enumerate(selects):
                try:
                    select_name = sel.get_attribute("name")
                    select_id = sel.get_attribute("id")
                    
                    logger.info(f"Select {i}: name={select_name}, id={select_id}")
                    
                    # Get options
                    options = sel.find_elements(By.TAG_NAME, "option")
                    logger.info(f"  Options: {len(options)}")
                    
                    for j, opt in enumerate(options[:5]):  # First 5 options
                        try:
                            opt_value = opt.get_attribute("value")
                            opt_text = opt.text
                            logger.info(f"    Option {j}: value={opt_value}, text={opt_text}")
                        except:
                            continue
                            
                except:
                    continue
            
            # Find buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {len(buttons)} button elements")
            
            for i, btn in enumerate(buttons[:5]):
                try:
                    btn_text = btn.text
                    btn_type = btn.get_attribute("type")
                    btn_class = btn.get_attribute("class")
                    
                    logger.info(f"Button {i}: text={btn_text}, type={btn_type}, class={btn_class}")
                except:
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing page structure: {e}")
            return False

    def search_organizations(self, search_term: str = None, state: str = None) -> List[Dict]:
        """Search for organizations using various methods"""
        organizations = []
        
        try:
            logger.info(f"Searching for organizations with term='{search_term}', state='{state}'")
            
            # Method 1: Try to find and use search input
            search_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='search']")
            
            for search_input in search_inputs:
                try:
                    if search_term:
                        search_input.clear()
                        search_input.send_keys(search_term)
                        
                        # Look for search button
                        search_buttons = self.driver.find_elements(By.XPATH, 
                            "//button[contains(text(), 'Search') or contains(text(), 'Find') or @type='submit']")
                        
                        if search_buttons:
                            search_buttons[0].click()
                            time.sleep(3)
                            
                            # Extract results
                            orgs = self.extract_organizations_from_page(search_term, state)
                            organizations.extend(orgs)
                            
                            break
                            
                except Exception as e:
                    logger.debug(f"Search input method failed: {e}")
                    continue
            
            # Method 2: Try to use select dropdowns
            if state:
                try:
                    state_selects = self.driver.find_elements(By.TAG_NAME, "select")
                    
                    for select_elem in state_selects:
                        try:
                            select = Select(select_elem)
                            options = select.options
                            
                            # Look for state in options
                            for option in options:
                                if state.lower() in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    time.sleep(2)
                                    
                                    # Look for submit button
                                    submit_buttons = self.driver.find_elements(By.XPATH, 
                                        "//button[@type='submit'] | //input[@type='submit']")
                                    
                                    if submit_buttons:
                                        submit_buttons[0].click()
                                        time.sleep(3)
                                        
                                        orgs = self.extract_organizations_from_page(search_term, state)
                                        organizations.extend(orgs)
                                    
                                    break
                                    
                        except Exception as e:
                            logger.debug(f"Select dropdown method failed: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"State selection failed: {e}")
            
            # Method 3: Try to scroll and load more content
            try:
                # Scroll down to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Try to find "Load More" or pagination buttons
                load_more_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Load More') or contains(text(), 'More') or contains(text(), 'Next')]")
                
                for button in load_more_buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            time.sleep(3)
                            
                            orgs = self.extract_organizations_from_page(search_term, state)
                            organizations.extend(orgs)
                            
                    except Exception as e:
                        logger.debug(f"Load more button failed: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Scroll and load more failed: {e}")
            
            # Method 4: Extract any visible organizations
            if not organizations:
                orgs = self.extract_organizations_from_page(search_term, state)
                organizations.extend(orgs)
            
        except Exception as e:
            logger.error(f"Error in search_organizations: {e}")
        
        return organizations

    def extract_organizations_from_page(self, search_term: str = None, state: str = None) -> List[Dict]:
        """Extract organization data from the current page"""
        organizations = []
        
        try:
            # Wait for content to load
            time.sleep(2)
            
            # Multiple selectors to find organization containers
            selectors = [
                "//div[contains(@class, 'organization')]",
                "//div[contains(@class, 'hospital')]",
                "//div[contains(@class, 'result')]",
                "//div[contains(@class, 'card')]",
                "//div[contains(@class, 'listing')]",
                "//article",
                "//section[contains(@class, 'org')]",
                "//tr[contains(@class, 'organization')]",
                "//tr[contains(@class, 'hospital')]",
                "//li[contains(@class, 'organization')]",
                "//li[contains(@class, 'hospital')]",
                "//div[@data-name]",
                "//div[@data-organization]",
                "//div[@data-hospital]"
            ]
            
            found_elements = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        found_elements.extend(elements)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Remove duplicates
            unique_elements = []
            seen_elements = set()
            
            for element in found_elements:
                try:
                    element_id = element.id
                    if element_id not in seen_elements:
                        seen_elements.add(element_id)
                        unique_elements.append(element)
                except:
                    unique_elements.append(element)
            
            logger.info(f"Processing {len(unique_elements)} unique elements")
            
            for element in unique_elements:
                try:
                    org_data = self.extract_organization_data(element, search_term, state)
                    if org_data and org_data.get('name') and len(org_data['name']) > 5:
                        organizations.append(org_data)
                except Exception as e:
                    logger.debug(f"Error extracting from element: {e}")
                    continue
            
            # If no structured data found, try text extraction
            if not organizations:
                organizations = self.extract_from_page_text(search_term, state)
            
        except Exception as e:
            logger.error(f"Error extracting organizations from page: {e}")
        
        return organizations

    def extract_organization_data(self, element, search_term: str = None, state: str = None) -> Dict:
        """Extract organization data from a web element"""
        try:
            org_data = {
                'name': '',
                'state': state or 'Unknown',
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
            
            # Extract name
            name_selectors = [
                ".//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6",
                ".//*[contains(@class, 'name')]",
                ".//*[contains(@class, 'title')]",
                ".//*[contains(@class, 'hospital')]",
                ".//*[contains(@class, 'organization')]",
                ".//strong | .//b"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.XPATH, selector)
                    if name_elem and name_elem.text.strip():
                        org_data['name'] = name_elem.text.strip()
                        break
                except:
                    continue
            
            # If no name found, try data attributes
            if not org_data['name']:
                try:
                    for attr in ['data-name', 'data-hospital', 'data-organization', 'title']:
                        attr_value = element.get_attribute(attr)
                        if attr_value:
                            org_data['name'] = attr_value
                            break
                except:
                    pass
            
            # If still no name, use element text
            if not org_data['name']:
                try:
                    element_text = element.text.strip()
                    if element_text:
                        # Take first line or first 100 characters
                        first_line = element_text.split('\n')[0].strip()
                        org_data['name'] = first_line[:100] if len(first_line) > 5 else element_text[:100]
                except:
                    pass
            
            # Extract other information from element text
            try:
                all_text = element.text
                
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
                
                # Extract city and state from address
                if org_data['address']:
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
                
                # Extract accreditation details
                if 'full' in all_text.lower():
                    org_data['accreditation_level'] = 'Full'
                elif 'entry' in all_text.lower():
                    org_data['accreditation_level'] = 'Entry Level'
                elif 'provisional' in all_text.lower():
                    org_data['accreditation_level'] = 'Provisional'
                
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
                
            except Exception as e:
                logger.debug(f"Error extracting text data: {e}")
            
            # Extract website
            try:
                website_elem = element.find_element(By.XPATH, ".//a[starts-with(@href, 'http')]")
                if website_elem:
                    href = website_elem.get_attribute('href')
                    if href and not href.startswith('mailto:'):
                        org_data['website'] = href
            except:
                pass
            
            return org_data
            
        except Exception as e:
            logger.error(f"Error extracting organization data: {e}")
            return {}

    def extract_from_page_text(self, search_term: str = None, state: str = None) -> List[Dict]:
        """Extract organizations from page text if no structured data found"""
        organizations = []
        
        try:
            # Get page text
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
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
                            'state': state or 'Unknown',
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

    def scrape_all_organizations(self):
        """Scrape all organizations using various search strategies"""
        logger.info("Starting comprehensive Selenium-based NABH scraping...")
        
        all_organizations = []
        
        try:
            # Strategy 1: Search with terms
            for i, term in enumerate(self.search_terms[:10]):  # Limit for testing
                logger.info(f"Searching with term: {term} ({i+1}/{min(10, len(self.search_terms))})")
                
                try:
                    # Navigate back to search page
                    self.navigate_to_search_page()
                    
                    # Search with term
                    orgs = self.search_organizations(search_term=term)
                    if orgs:
                        all_organizations.extend(orgs)
                        logger.info(f"Found {len(orgs)} organizations with term '{term}'")
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error searching with term '{term}': {e}")
                    continue
            
            # Strategy 2: Search by states
            for i, state in enumerate(self.states[:5]):  # Limit for testing
                logger.info(f"Searching in state: {state} ({i+1}/{min(5, len(self.states))})")
                
                try:
                    # Navigate back to search page
                    self.navigate_to_search_page()
                    
                    # Search by state
                    orgs = self.search_organizations(state=state)
                    if orgs:
                        all_organizations.extend(orgs)
                        logger.info(f"Found {len(orgs)} organizations in state '{state}'")
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error searching in state '{state}': {e}")
                    continue
            
            # Strategy 3: General page scraping
            try:
                logger.info("Performing general page scraping...")
                self.navigate_to_search_page()
                
                orgs = self.extract_organizations_from_page()
                if orgs:
                    all_organizations.extend(orgs)
                    logger.info(f"Found {len(orgs)} organizations from general scraping")
                    
            except Exception as e:
                logger.error(f"Error in general scraping: {e}")
            
        except Exception as e:
            logger.error(f"Error in scrape_all_organizations: {e}")
        
        # Remove duplicates
        self.organizations = self.remove_duplicates(all_organizations)
        
        logger.info(f"Completed scraping. Total unique organizations: {len(self.organizations)}")

    def remove_duplicates(self, organizations: List[Dict]) -> List[Dict]:
        """Remove duplicate organizations"""
        seen = set()
        unique_orgs = []
        
        for org in organizations:
            # Create a unique key based on name
            name = org.get('name', '').lower().strip()
            
            # Skip if name is too short or contains navigation text
            if (len(name) < 5 or 
                'skip to content' in name.lower() or
                'home' in name.lower() and len(name) < 20 or
                'accreditation' in name.lower() and len(name) < 30):
                continue
            
            if name not in seen and name:
                seen.add(name)
                unique_orgs.append(org)
        
        removed_count = len(organizations) - len(unique_orgs)
        logger.info(f"Removed {removed_count} duplicate/invalid organizations")
        
        return unique_orgs

    def save_data(self):
        """Save scraped data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"selenium_nabh_organizations_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"selenium_nabh_organizations_{timestamp}.csv"
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
        
        report_filename = f"selenium_nabh_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_selenium_scraping(self):
        """Run the complete Selenium-based scraping process"""
        logger.info("Starting Selenium-based NABH directory scraping...")
        
        try:
            # Setup driver
            if not self.setup_driver():
                raise Exception("Failed to setup Chrome driver")
            
            # Navigate to search page
            if not self.navigate_to_search_page():
                raise Exception("Failed to navigate to search page")
            
            # Analyze page structure
            self.analyze_page_structure()
            
            # Scrape all organizations
            self.scrape_all_organizations()
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nSelenium NABH Scraping Completed!")
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
            
        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            raise
        
        finally:
            # Clean up
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("Chrome driver closed")
                except:
                    pass

if __name__ == "__main__":
    if not SELENIUM_AVAILABLE:
        print("Selenium is not installed. Please install it using:")
        print("pip install selenium")
        print("\nAlso make sure you have Chrome browser installed and chromedriver in PATH")
    else:
        scraper = SeleniumNABHScraper()
        scraper.run_selenium_scraping()