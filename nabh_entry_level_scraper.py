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

class NABHEntryLevelScraper:
    def __init__(self):
        self.portal_url = "https://portal.nabh.co/frmViewAccreditedEntryLevelHosp.aspx"
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
        logger.info("Fetching initial NABH Entry Level portal page...")
        
        try:
            response = self.session.get(self.portal_url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to access portal: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract ViewState and other ASP.NET form data
            self.viewstate = self.extract_form_data(soup)
            
            logger.info("Successfully loaded initial page")
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
            # Find the main data table
            table = soup.find('table', {'id': 'ContentPlaceHolder1_grvHCOApplicant'})
            
            if not table:
                logger.warning("Main data table not found")
                return hospitals
            
            # Get all rows (skip header row)
            rows = table.find_all('tr')[1:]  # Skip header
            
            logger.info(f"Found {len(rows)} hospital rows in table")
            
            for i, row in enumerate(rows):
                try:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 7:  # Ensure we have all required columns
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
        """Parse individual hospital row data"""
        try:
            # Extract cell text
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            # Map to hospital data structure
            hospital_data = {
                'serial_number': cell_texts[0] if len(cell_texts) > 0 else '',
                'reference_number': cell_texts[1] if len(cell_texts) > 1 else '',
                'name': cell_texts[2] if len(cell_texts) > 2 else '',
                'accreditation_number': cell_texts[3] if len(cell_texts) > 3 else '',
                'valid_from': cell_texts[4] if len(cell_texts) > 4 else '',
                'valid_upto': cell_texts[5] if len(cell_texts) > 5 else '',
                'remarks': cell_texts[6] if len(cell_texts) > 6 else '',
                
                # Additional processed fields
                'accreditation_level': 'Entry Level',
                'accreditation_category': 'NABH Entry Level',
                'country': 'India',
                'source': 'NABH Entry Level Portal',
                'scraped_date': datetime.now().isoformat(),
                'portal_url': self.portal_url,
                'row_number': row_number
            }
            
            # Parse location from name
            location_info = self.parse_location_from_name(hospital_data['name'])
            hospital_data.update(location_info)
            
            # Parse dates
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
        """Parse city and state from hospital name"""
        location_info = {
            'city': 'Unknown',
            'state': 'Unknown',
            'address': ''
        }
        
        try:
            # Common pattern: "Hospital Name, City, State, Country"
            if ',' in name:
                parts = [part.strip() for part in name.split(',')]
                
                if len(parts) >= 3:
                    # Last part is usually country (India)
                    if parts[-1].lower() in ['india', 'bharat']:
                        if len(parts) >= 4:
                            location_info['state'] = parts[-2]
                            location_info['city'] = parts[-3]
                        elif len(parts) == 3:
                            location_info['state'] = parts[-2]
                            location_info['city'] = parts[-2]  # Sometimes city = state
                
                # Create address from location parts
                location_parts = parts[1:] if len(parts) > 1 else []
                location_info['address'] = ', '.join(location_parts)
            
            # Clean up location data
            location_info['city'] = self.clean_location_name(location_info['city'])
            location_info['state'] = self.clean_location_name(location_info['state'])
            
        except Exception as e:
            logger.debug(f"Error parsing location from name '{name}': {e}")
        
        return location_info

    def clean_location_name(self, location: str) -> str:
        """Clean and standardize location names"""
        if not location or location.lower() in ['unknown', 'india', 'bharat']:
            return 'Unknown'
        
        # Remove common suffixes
        location = re.sub(r'\s+(India|Bharat)$', '', location, flags=re.I)
        
        # Capitalize properly
        location = location.title()
        
        return location.strip()

    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to standardized format"""
        if not date_str or date_str.strip() == '':
            return None
        
        try:
            # Common formats: "04 May 2015", "24 Dec 2024"
            date_patterns = [
                r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # "04 May 2015"
                r'(\d{1,2})/(\d{1,2})/(\d{4})',   # "04/05/2015"
                r'(\d{4})-(\d{1,2})-(\d{1,2})'    # "2015-05-04"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    if len(match.groups()) == 3:
                        # For "04 May 2015" format
                        if match.group(2).isalpha():
                            day, month_name, year = match.groups()
                            month_map = {
                                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                            }
                            month = month_map.get(month_name.lower()[:3], '01')
                            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        else:
                            # For numeric formats
                            return f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
            
            return date_str  # Return original if no pattern matches
            
        except Exception as e:
            logger.debug(f"Error parsing date '{date_str}': {e}")
            return date_str

    def determine_certification_status(self, remarks: str, valid_upto: Optional[str]) -> str:
        """Determine current certification status"""
        if not remarks:
            remarks = ''
        
        remarks_lower = remarks.lower()
        
        # Check for explicit status in remarks
        if 'expired' in remarks_lower:
            return 'Expired'
        elif 'suspended' in remarks_lower:
            return 'Suspended'
        elif 'revoked' in remarks_lower or 'cancelled' in remarks_lower:
            return 'Revoked'
        elif 'active' in remarks_lower or 'valid' in remarks_lower:
            return 'Active'
        
        # Check validity date
        if valid_upto:
            try:
                from datetime import datetime
                if valid_upto.count('-') == 2:  # YYYY-MM-DD format
                    valid_date = datetime.strptime(valid_upto, '%Y-%m-%d')
                    current_date = datetime.now()
                    
                    if valid_date > current_date:
                        return 'Active'
                    else:
                        return 'Expired'
            except:
                pass
        
        # Default status
        return 'Unknown'

    def clean_hospital_data(self, hospital_data: Dict) -> Dict:
        """Clean and validate hospital data"""
        # Clean hospital name
        name = hospital_data.get('name', '').strip()
        
        # Remove extra whitespace and normalize
        name = re.sub(r'\s+', ' ', name)
        hospital_data['name'] = name
        
        # Clean reference numbers
        for field in ['reference_number', 'accreditation_number']:
            if hospital_data.get(field):
                hospital_data[field] = hospital_data[field].strip()
        
        # Validate required fields
        if not hospital_data.get('name') or len(hospital_data['name']) < 3:
            return None
        
        return hospital_data

    def scrape_all_hospitals(self) -> List[Dict]:
        """Scrape all hospitals from the portal"""
        logger.info("Starting NABH Entry Level hospitals scraping...")
        
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
            logger.info(f"Successfully scraped {len(hospitals)} unique hospitals")
            
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
        """Save scraped data to files"""
        if not self.hospitals:
            logger.warning("No hospitals to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_filename = f"nabh_entry_level_hospitals_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.hospitals, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_filename = f"nabh_entry_level_hospitals_{timestamp}.csv"
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
            'scraping_method': 'Direct table extraction',
            'total_hospitals': len(self.hospitals),
            'by_state': {},
            'by_city': {},
            'by_certification_status': {},
            'by_year': {},
            'data_quality': {
                'with_accreditation_number': 0,
                'with_validity_dates': 0,
                'with_location_info': 0,
                'active_certifications': 0,
                'expired_certifications': 0
            },
            'sample_hospitals': []
        }
        
        # Analyze data
        for hospital in self.hospitals:
            # Count by state
            state = hospital.get('state', 'Unknown')
            report['by_state'][state] = report['by_state'].get(state, 0) + 1
            
            # Count by city
            city = hospital.get('city', 'Unknown')
            report['by_city'][city] = report['by_city'].get(city, 0) + 1
            
            # Count by certification status
            status = hospital.get('certification_status', 'Unknown')
            report['by_certification_status'][status] = report['by_certification_status'].get(status, 0) + 1
            
            # Count by year (from valid_from)
            if hospital.get('valid_from_parsed'):
                try:
                    year = hospital['valid_from_parsed'][:4]
                    report['by_year'][year] = report['by_year'].get(year, 0) + 1
                except:
                    pass
            
            # Data quality metrics
            if hospital.get('accreditation_number'):
                report['data_quality']['with_accreditation_number'] += 1
            if hospital.get('valid_from_parsed') and hospital.get('valid_upto_parsed'):
                report['data_quality']['with_validity_dates'] += 1
            if hospital.get('state') != 'Unknown' and hospital.get('city') != 'Unknown':
                report['data_quality']['with_location_info'] += 1
            if hospital.get('certification_status') == 'Active':
                report['data_quality']['active_certifications'] += 1
            elif hospital.get('certification_status') == 'Expired':
                report['data_quality']['expired_certifications'] += 1
        
        # Sort by count
        report['by_state'] = dict(sorted(report['by_state'].items(), key=lambda x: x[1], reverse=True))
        report['by_city'] = dict(sorted(report['by_city'].items(), key=lambda x: x[1], reverse=True))
        report['by_certification_status'] = dict(sorted(report['by_certification_status'].items(), key=lambda x: x[1], reverse=True))
        
        # Add sample hospitals
        report['sample_hospitals'] = self.hospitals[:10]
        
        # Save report
        report_filename = f"nabh_entry_level_scraping_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated comprehensive report: {report_filename}")
        return report

    def run_scraping(self):
        """Run the complete scraping process"""
        logger.info("Starting NABH Entry Level hospitals scraping process...")
        
        try:
            # Scrape all hospitals
            hospitals = self.scrape_all_hospitals()
            
            if not hospitals:
                logger.error("No hospitals were scraped")
                return
            
            # Save data
            self.save_data()
            
            # Print summary
            print(f"\nNABH Entry Level Hospitals Scraping Completed!")
            print(f"Total hospitals scraped: {len(hospitals)}")
            
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
            logger.error(f"Scraping process failed: {e}")
            raise

if __name__ == "__main__":
    scraper = NABHEntryLevelScraper()
    scraper.run_scraping()