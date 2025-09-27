import requests
from bs4 import BeautifulSoup
import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedNABHEntryLevelScraper:
    def __init__(self):
        # Updated URL from user
        self.portal_url = "https://portal.nabh.co/frmViewApplicantEntryLevelHosp.aspx#gsc.tab=0"
        self.base_url = "https://portal.nabh.co"
        self.hospitals = []
        
        # Session for maintaining cookies and state
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })

    def get_initial_page(self) -> BeautifulSoup:
        """Get the initial page and extract ViewState"""
        logger.info("Fetching updated NABH Entry Level portal page...")
        
        try:
            # Clean URL (remove fragment)
            clean_url = self.portal_url.split('#')[0]
            response = self.session.get(clean_url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to access portal: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract ViewState and other ASP.NET form data
            self.viewstate = self.extract_form_data(soup)
            
            logger.info("Successfully loaded initial page from updated URL")
            return soup
            
        except Exception as e:
            logger.error(f"Error fetching initial page: {e}")
            return None

    def extract_form_data(self, soup: BeautifulSoup) -> Dict:
        """Extract ASP.NET form data for maintaining session state"""
        form_data = {}
        
        # Extract common ASP.NET hidden fields
        hidden_fields = [
            '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
            '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS'
        ]
        
        for field in hidden_fields:
            element = soup.find('input', {'name': field})
            if element:
                form_data[field] = element.get('value', '')
        
        logger.info(f"Extracted {len(form_data)} form fields")
        return form_data

    def extract_hospital_data_from_table(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract hospital data from the main data table"""
        hospitals = []
        
        try:
            # Try multiple possible table IDs/classes for the updated portal
            possible_table_selectors = [
                'table[id*="grvHCOApplicant"]',
                'table[id*="GridView"]',
                'table[id*="DataGrid"]',
                'table.table',
                'table[class*="grid"]',
                'div[id*="UpdatePanel"] table',
                'form table'
            ]
            
            table = None
            for selector in possible_table_selectors:
                table = soup.select_one(selector)
                if table:
                    logger.info(f"Found data table using selector: {selector}")
                    break
            
            if not table:
                logger.warning("Main data table not found with any selector")
                # Log available tables for debugging
                all_tables = soup.find_all('table')
                logger.info(f"Found {len(all_tables)} tables on page")
                for i, t in enumerate(all_tables[:5]):  # Log first 5 tables
                    table_id = t.get('id', 'no-id')
                    table_class = t.get('class', 'no-class')
                    logger.info(f"Table {i}: id='{table_id}', class='{table_class}'")
                return hospitals
            
            # Get all rows (skip header row)
            rows = table.find_all('tr')[1:]  # Skip header
            
            logger.info(f"Found {len(rows)} hospital rows in table")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 5:  # Minimum required columns
                        hospital_data = self.parse_hospital_row(cells, i + 1)
                        if hospital_data:
                            hospitals.append(hospital_data)
                    
                    # Progress logging
                    if (i + 1) % 500 == 0:
                        logger.info(f"Processed {i + 1} hospitals...")
                        
                except Exception as e:
                    logger.debug(f"Error processing row {i}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(hospitals)} hospitals")
            
        except Exception as e:
            logger.error(f"Error extracting hospital data: {e}")
        
        return hospitals

    def parse_hospital_row(self, cells: List, row_number: int) -> Dict:
        """Parse individual hospital row data with enhanced flexibility"""
        try:
            # Extract cell text
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Enhanced mapping to handle different column structures
            hospital_data = {
                'serial_number': cell_texts[0] if len(cell_texts) > 0 else '',
                'reference_number': cell_texts[1] if len(cell_texts) > 1 else '',
                'name': cell_texts[2] if len(cell_texts) > 2 else '',
                'accreditation_number': cell_texts[3] if len(cell_texts) > 3 else '',
                'valid_from': cell_texts[4] if len(cell_texts) > 4 else '',
                'valid_upto': cell_texts[5] if len(cell_texts) > 5 else '',
                'remarks': cell_texts[6] if len(cell_texts) > 6 else '',
                'additional_info': cell_texts[7] if len(cell_texts) > 7 else '',
                
                # Additional processed fields
                'accreditation_level': 'Entry Level',
                'accreditation_category': 'NABH Entry Level',
                'country': 'India',
                'source': 'NABH Entry Level Portal (Updated)',
                'scraped_date': datetime.now().isoformat(),
                'portal_url': self.portal_url,
                'row_number': row_number,
                'data_version': '2.0'  # Mark as updated version
            }
            
            # Parse location from name
            location_info = self.parse_location_from_name(hospital_data['name'])
            hospital_data.update(location_info)
            
            # Parse dates with enhanced date parsing
            hospital_data['valid_from_parsed'] = self.parse_date(hospital_data['valid_from'])
            hospital_data['valid_upto_parsed'] = self.parse_date(hospital_data['valid_upto'])
            
            # Determine certification status
            hospital_data['certification_status'] = self.determine_certification_status(
                hospital_data['remarks'], 
                hospital_data['valid_upto_parsed']
            )
            
            # Clean and validate data
            hospital_data = self.clean_hospital_data(hospital_data)
            
            return hospital_data
            
        except Exception as e:
            logger.debug(f"Error parsing hospital row {row_number}: {e}")
            return None

    def parse_location_from_name(self, name: str) -> Dict:
        """Enhanced location parsing from hospital name"""
        location_info = {
            'city': 'Unknown',
            'state': 'Unknown',
            'address': ''
        }
        
        try:
            # Enhanced patterns for location extraction
            if ',' in name:
                parts = [part.strip() for part in name.split(',')]
                
                # Pattern 1: "Hospital Name, City, State, Country"
                if len(parts) >= 3:
                    if parts[-1].lower() in ['india', 'bharat']:
                        if len(parts) >= 4:
                            location_info['state'] = parts[-2]
                            location_info['city'] = parts[-3]
                        elif len(parts) == 3:
                            location_info['state'] = parts[-2]
                            location_info['city'] = parts[-2]
                
                # Create address from location parts
                location_parts = parts[1:] if len(parts) > 1 else []
                location_info['address'] = ', '.join(location_parts)
            
            # Pattern 2: Look for state names in parentheses
            state_pattern = r'\(([^)]+)\)$'
            state_match = re.search(state_pattern, name)
            if state_match:
                location_info['state'] = state_match.group(1).strip()
            
            # Clean up location data
            location_info['city'] = self.clean_location_name(location_info['city'])
            location_info['state'] = self.clean_location_name(location_info['state'])
            
        except Exception as e:
            logger.debug(f"Error parsing location from name '{name}': {e}")
        
        return location_info

    def clean_location_name(self, location: str) -> str:
        """Clean and standardize location names"""
        if not location or location.lower() in ['unknown', 'na', 'n/a', '']:
            return 'Unknown'
        
        # Remove extra whitespace and standardize
        location = re.sub(r'\s+', ' ', location.strip())
        
        # Capitalize properly
        location = location.title()
        
        return location

    def parse_date(self, date_str: str) -> Optional[str]:
        """Enhanced date parsing with multiple formats"""
        if not date_str or date_str.lower() in ['na', 'n/a', '', 'unknown']:
            return None
        
        # Common date formats
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d.%m.%Y',
            '%d %b %Y',
            '%d %B %Y',
            '%b %d, %Y',
            '%B %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logger.debug(f"Could not parse date: {date_str}")
        return None

    def determine_certification_status(self, remarks: str, valid_upto: Optional[str]) -> str:
        """Determine certification status based on remarks and validity"""
        if not remarks:
            remarks = ""
        
        remarks_lower = remarks.lower()
        
        # Check for explicit status indicators
        if any(word in remarks_lower for word in ['suspended', 'revoked', 'cancelled', 'withdrawn']):
            return 'Suspended'
        
        if any(word in remarks_lower for word in ['expired', 'lapsed']):
            return 'Expired'
        
        # Check validity date
        if valid_upto:
            try:
                valid_date = datetime.strptime(valid_upto, '%Y-%m-%d')
                current_date = datetime.now()
                
                if valid_date < current_date:
                    return 'Expired'
                else:
                    return 'Active'
            except ValueError:
                pass
        
        # Default based on remarks content
        if any(word in remarks_lower for word in ['active', 'valid', 'current']):
            return 'Active'
        
        return 'Unknown'

    def clean_hospital_data(self, hospital_data: Dict) -> Dict:
        """Clean and validate hospital data"""
        # Clean name
        if hospital_data.get('name'):
            hospital_data['name'] = re.sub(r'\s+', ' ', hospital_data['name'].strip())
        
        # Clean accreditation numbers
        for field in ['accreditation_number', 'reference_number']:
            if hospital_data.get(field):
                hospital_data[field] = hospital_data[field].strip()
        
        # Validate required fields
        if not hospital_data.get('name') or len(hospital_data['name']) < 3:
            return None
        
        return hospital_data

    def scrape_all_hospitals(self) -> List[Dict]:
        """Scrape all hospitals from the updated portal"""
        logger.info("Starting updated NABH Entry Level hospitals scraping...")
        
        try:
            # Get initial page
            soup = self.get_initial_page()
            if not soup:
                logger.error("Failed to load initial page")
                return []
            
            # Extract hospital data from table
            hospitals = self.extract_hospital_data_from_table(soup)
            
            if not hospitals:
                logger.warning("No hospitals found in table")
                return []
            
            # Remove duplicates and clean data
            hospitals = self.remove_duplicates_and_clean(hospitals)
            
            self.hospitals = hospitals
            logger.info(f"Successfully scraped {len(hospitals)} unique hospitals from updated portal")
            
            return hospitals
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []

    def remove_duplicates_and_clean(self, hospitals: List[Dict]) -> List[Dict]:
        """Remove duplicates and clean hospital data"""
        seen_hospitals = set()
        unique_hospitals = []
        
        for hospital in hospitals:
            # Create unique identifier
            identifier = (
                hospital.get('name', '').lower().strip(),
                hospital.get('accreditation_number', '').strip(),
                hospital.get('reference_number', '').strip()
            )
            
            if identifier not in seen_hospitals and hospital.get('name'):
                seen_hospitals.add(identifier)
                unique_hospitals.append(hospital)
        
        removed_count = len(hospitals) - len(unique_hospitals)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate hospitals")
        
        return unique_hospitals

    def save_data(self):
        """Save scraped data to files with updated naming"""
        if not self.hospitals:
            logger.warning("No hospitals to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"updated_nabh_entry_level_hospitals_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.hospitals, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"updated_nabh_entry_level_hospitals_{timestamp}.csv"
        if self.hospitals:
            fieldnames = self.hospitals[0].keys()
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.hospitals)
        
        # Generate summary report
        self.generate_summary_report(timestamp)
        
        logger.info(f"Saved {len(self.hospitals)} hospitals to {json_filename} and {csv_filename}")

    def generate_summary_report(self, timestamp: str):
        """Generate comprehensive summary report"""
        report = {
            'scraping_date': datetime.now().isoformat(),
            'portal_url': self.portal_url,
            'scraping_method': 'Updated portal extraction',
            'data_version': '2.0',
            'total_hospitals': len(self.hospitals),
            'by_state': {},
            'by_city': {},
            'by_certification_status': {},
            'by_year': {},
            'data_quality': {
                'with_accreditation_number': 0,
                'with_validity_dates': 0,
                'with_location_info': 0,
                'active_certifications': 0
            }
        }
        
        # Analyze data
        for hospital in self.hospitals:
            # State distribution
            state = hospital.get('state', 'Unknown')
            report['by_state'][state] = report['by_state'].get(state, 0) + 1
            
            # City distribution
            city = hospital.get('city', 'Unknown')
            report['by_city'][city] = report['by_city'].get(city, 0) + 1
            
            # Status distribution
            status = hospital.get('certification_status', 'Unknown')
            report['by_certification_status'][status] = report['by_certification_status'].get(status, 0) + 1
            
            # Data quality metrics
            if hospital.get('accreditation_number'):
                report['data_quality']['with_accreditation_number'] += 1
            
            if hospital.get('valid_from_parsed') or hospital.get('valid_upto_parsed'):
                report['data_quality']['with_validity_dates'] += 1
            
            if hospital.get('state') != 'Unknown':
                report['data_quality']['with_location_info'] += 1
            
            if hospital.get('certification_status') == 'Active':
                report['data_quality']['active_certifications'] += 1
        
        # Save report
        report_filename = f"updated_nabh_entry_level_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_scraping(self):
        """Run the complete updated scraping process"""
        logger.info("Starting updated NABH Entry Level hospitals scraping process...")
        
        try:
            # Scrape all hospitals
            hospitals = self.scrape_all_hospitals()
            
            if not hospitals:
                logger.error("No hospitals were scraped from updated portal")
                return
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nUpdated NABH Entry Level Hospitals Scraping Completed!")
            print(f"Total hospitals scraped: {len(hospitals)}")
            print(f"Portal URL: {self.portal_url}")
            
            # State distribution
            state_counts = {}
            status_counts = {}
            
            for hospital in hospitals:
                state = hospital.get('state', 'Unknown')
                state_counts[state] = state_counts.get(state, 0) + 1
                
                status = hospital.get('certification_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\nTop 10 States by Hospital Count:")
            for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{state}: {count}")
            
            print(f"\nCertification Status Distribution:")
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"{status}: {count}")
            
            # Sample hospitals
            print(f"\nSample Hospitals:")
            for i, hospital in enumerate(hospitals[:5]):
                print(f"{i+1}. {hospital.get('name', 'Unknown')} - {hospital.get('state', 'Unknown')} ({hospital.get('certification_status', 'Unknown')})")
            
            # Data quality summary
            with_acc_num = sum(1 for h in hospitals if h.get('accreditation_number'))
            with_location = sum(1 for h in hospitals if h.get('state') != 'Unknown')
            active_certs = sum(1 for h in hospitals if h.get('certification_status') == 'Active')
            
            print(f"\nData Quality:")
            print(f"Hospitals with accreditation numbers: {with_acc_num}")
            print(f"Hospitals with location info: {with_location}")
            print(f"Active certifications: {active_certs}")
            
        except Exception as e:
            logger.error(f"Updated scraping process failed: {e}")
            raise

if __name__ == "__main__":
    scraper = UpdatedNABHEntryLevelScraper()
    scraper.run_scraping()