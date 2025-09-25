"""
CAP 15189 Laboratory Data Scraper for QuXAT Healthcare Quality Grid
This module scrapes CAP 15189 accredited laboratory data from the College of American Pathologists website
to build a comprehensive database of accredited healthcare laboratories.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAPLaboratoryScraper:
    """Scraper for CAP 15189 accredited laboratories"""
    
    def __init__(self):
        self.base_url = "https://www.cap.org/laboratory-improvement/accreditation/cap-15189-accreditation-program/cap-15189-accredited-laboratories"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.laboratories = []
    
    def scrape_laboratory_data(self) -> List[Dict]:
        """
        Scrape CAP 15189 accredited laboratory data
        Returns a list of laboratory dictionaries with standardized format
        """
        try:
            logger.info(f"Scraping CAP laboratory data from: {self.base_url}")
            
            # Make request to the CAP website
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract laboratory information
            self._extract_laboratories(soup)
            
            logger.info(f"Successfully scraped {len(self.laboratories)} laboratories")
            return self.laboratories
            
        except requests.RequestException as e:
            logger.error(f"Error fetching CAP laboratory data: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing CAP laboratory data: {e}")
            return []
    
    def _extract_laboratories(self, soup: BeautifulSoup):
        """Extract laboratory information from the parsed HTML"""
        
        # Look for laboratory entries in the content
        # The website contains laboratory information in a structured format
        content_text = soup.get_text()
        
        # Parse laboratory entries using regex patterns
        lab_pattern = r'([A-Za-z0-9\s,&.-]+?)(\d+[\w\s,.-]+?)([A-Z]{2}\s+\d{5}(?:-\d{4})?|\w+\s+\w+,?\s*\w*\s*\d+)(\d{3}-\d{3}-\d{4}|\+\d+[\d\s()-]+)?(Website|Certificate)'
        
        # Alternative approach: look for specific patterns in the text
        lines = content_text.split('\n')
        current_lab = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Look for laboratory names (typically followed by address)
            if self._is_laboratory_name(line):
                if current_lab:
                    self._add_laboratory(current_lab)
                    current_lab = {}
                
                current_lab['name'] = line
                current_lab['accreditation_type'] = 'CAP 15189'
                current_lab['accreditation_body'] = 'College of American Pathologists'
                current_lab['status'] = 'Active'
                current_lab['scraped_date'] = datetime.now().isoformat()
                
                # Look for address in next few lines
                address_lines = []
                for j in range(1, 5):
                    if i + j < len(lines):
                        next_line = lines[i + j].strip()
                        if next_line and not self._is_phone_or_website(next_line):
                            address_lines.append(next_line)
                        else:
                            break
                
                if address_lines:
                    current_lab['address'] = ', '.join(address_lines)
                    current_lab['location'] = self._extract_location(address_lines)
            
            # Look for phone numbers
            elif self._is_phone_number(line):
                if current_lab:
                    current_lab['phone'] = line
            
            # Look for websites
            elif 'website' in line.lower() or line.startswith('http'):
                if current_lab:
                    current_lab['website'] = line
        
        # Add the last laboratory if exists
        if current_lab:
            self._add_laboratory(current_lab)
    
    def _is_laboratory_name(self, text: str) -> bool:
        """Determine if a line contains a laboratory name"""
        # Laboratory names typically contain certain keywords
        lab_keywords = ['laboratory', 'laboratories', 'lab', 'diagnostic', 'pathology', 'medical', 'health', 'hospital', 'clinic']
        text_lower = text.lower()
        
        # Check if it contains lab-related keywords and looks like a proper name
        has_keyword = any(keyword in text_lower for keyword in lab_keywords)
        is_proper_length = 10 < len(text) < 100
        has_letters = any(c.isalpha() for c in text)
        
        return has_keyword and is_proper_length and has_letters
    
    def _is_phone_number(self, text: str) -> bool:
        """Check if text contains a phone number"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        return bool(re.search(phone_pattern, text))
    
    def _is_phone_or_website(self, text: str) -> bool:
        """Check if text is a phone number or website"""
        return self._is_phone_number(text) or 'website' in text.lower() or text.startswith('http')
    
    def _extract_location(self, address_lines: List[str]) -> Dict[str, str]:
        """Extract location information from address lines"""
        location = {}
        
        # Look for country, state, city patterns
        for line in address_lines:
            # US state pattern
            us_state_pattern = r'\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b'
            us_match = re.search(us_state_pattern, line)
            if us_match:
                location['state'] = us_match.group(1)
                location['zip_code'] = us_match.group(2)
                location['country'] = 'United States'
                continue
            
            # International patterns
            if 'germany' in line.lower():
                location['country'] = 'Germany'
            elif 'united kingdom' in line.lower() or 'uk' in line.lower():
                location['country'] = 'United Kingdom'
            elif 'canada' in line.lower():
                location['country'] = 'Canada'
            elif 'japan' in line.lower():
                location['country'] = 'Japan'
            elif 'saudi arabia' in line.lower():
                location['country'] = 'Saudi Arabia'
            elif 'brazil' in line.lower():
                location['country'] = 'Brazil'
            elif 'south africa' in line.lower():
                location['country'] = 'South Africa'
            elif 'ireland' in line.lower():
                location['country'] = 'Ireland'
            elif 'switzerland' in line.lower():
                location['country'] = 'Switzerland'
            elif 'singapore' in line.lower():
                location['country'] = 'Singapore'
            elif 'china' in line.lower():
                location['country'] = 'China'
        
        return location
    
    def _add_laboratory(self, lab_data: Dict):
        """Add laboratory to the list with validation"""
        if lab_data.get('name') and len(lab_data['name']) > 5:
            # Generate a unique ID
            lab_data['id'] = f"cap_{len(self.laboratories) + 1}"
            lab_data['organization_type'] = 'Laboratory'
            lab_data['quality_score'] = self._calculate_quality_score(lab_data)
            
            self.laboratories.append(lab_data)
    
    def _calculate_quality_score(self, lab_data: Dict) -> float:
        """Calculate quality score based on available data"""
        base_score = 75.0  # Base score for CAP 15189 accreditation
        
        # Add points for additional information
        if lab_data.get('address'):
            base_score += 5.0
        if lab_data.get('phone'):
            base_score += 3.0
        if lab_data.get('website'):
            base_score += 7.0
        if lab_data.get('location', {}).get('country'):
            base_score += 5.0
        
        return min(base_score, 95.0)  # Cap at 95
    
    def save_to_json(self, filename: str = 'cap_laboratories.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.laboratories, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.laboratories)} laboratories to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of scraped data"""
        if not self.laboratories:
            return {}
        
        countries = {}
        for lab in self.laboratories:
            country = lab.get('location', {}).get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        return {
            'total_laboratories': len(self.laboratories),
            'countries': countries,
            'average_quality_score': sum(lab.get('quality_score', 0) for lab in self.laboratories) / len(self.laboratories),
            'with_website': sum(1 for lab in self.laboratories if lab.get('website')),
            'with_phone': sum(1 for lab in self.laboratories if lab.get('phone'))
        }

def main():
    """Main function to run the CAP laboratory scraper"""
    scraper = CAPLaboratoryScraper()
    
    print("🔬 Starting CAP 15189 Laboratory Data Scraping...")
    laboratories = scraper.scrape_laboratory_data()
    
    if laboratories:
        print(f"✅ Successfully scraped {len(laboratories)} laboratories")
        
        # Save to JSON
        scraper.save_to_json()
        
        # Print summary
        stats = scraper.get_summary_stats()
        print("\n📊 Summary Statistics:")
        print(f"Total Laboratories: {stats.get('total_laboratories', 0)}")
        print(f"Average Quality Score: {stats.get('average_quality_score', 0):.1f}")
        print(f"With Website: {stats.get('with_website', 0)}")
        print(f"With Phone: {stats.get('with_phone', 0)}")
        
        if stats.get('countries'):
            print("\n🌍 Countries:")
            for country, count in stats['countries'].items():
                print(f"  {country}: {count}")
    else:
        print("❌ No laboratory data was scraped")

if __name__ == "__main__":
    main()