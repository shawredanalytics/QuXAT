"""
NABH Dental Facilities Data Extractor
Extracts accredited dental facilities information from NABH portal
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import re

class NABHDentalExtractor:
    def __init__(self):
        self.base_url = "https://portal.nabh.co/frmViewAccreditedDentalFacilities.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_dental_data(self):
        """Extract NABH accredited dental facilities data from the portal"""
        try:
            print("Fetching NABH accredited dental facilities data...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table containing dental facilities data
            table = soup.find('table', {'id': 'GridView1'}) or soup.find('table', class_='table')
            
            if not table:
                # Try to find any table with dental facilities data
                tables = soup.find_all('table')
                for t in tables:
                    if 'Reference No' in str(t) or 'Acc. No' in str(t) or 'Dental' in str(t):
                        table = t
                        break
            
            if not table:
                print("Could not find dental facilities data table")
                return []
            
            dental_facilities = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:
                    facility_data = {
                        'reference_no': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        'name': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        'accreditation_no': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                        'valid_from': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                        'valid_upto': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                        'remarks': cells[6].get_text(strip=True) if len(cells) > 6 else '',
                        'accreditation_type': 'NABH_Dental',
                        'facility_type': 'Dental',
                        'country': self._extract_country(cells[2].get_text(strip=True) if len(cells) > 2 else ''),
                        'status': self._determine_status(cells[5].get_text(strip=True) if len(cells) > 5 else '', 
                                                       cells[6].get_text(strip=True) if len(cells) > 6 else ''),
                        'extracted_date': datetime.now().isoformat()
                    }
                    
                    if facility_data['name']:  # Only add if name exists
                        dental_facilities.append(facility_data)
            
            print(f"Successfully extracted {len(dental_facilities)} NABH accredited dental facilities")
            return dental_facilities
            
        except Exception as e:
            print(f"Error extracting NABH dental data: {str(e)}")
            return []
    
    def _extract_country(self, name_text):
        """Extract country from facility name"""
        if 'India' in name_text or any(state in name_text for state in ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Ahmedabad']):
            return 'India'
        return 'Unknown'
    
    def _determine_status(self, valid_upto, remarks):
        """Determine facility status based on validity and remarks"""
        try:
            if 'withdrawn' in remarks.lower() or 'suspended' in remarks.lower():
                return 'Suspended'
            elif 'expired' in remarks.lower() or 'not renewed' in remarks.lower():
                return 'Expired'
            elif valid_upto:
                # Parse date and check if still valid
                from datetime import datetime
                try:
                    # Try different date formats
                    for fmt in ['%d %b %Y', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            expiry_date = datetime.strptime(valid_upto, fmt)
                            if expiry_date > datetime.now():
                                return 'Active'
                            else:
                                return 'Expired'
                        except ValueError:
                            continue
                except:
                    pass
            return 'Active'  # Default to active if can't determine
        except:
            return 'Unknown'
    
    def save_data(self, dental_facilities):
        """Save extracted data to JSON and CSV files"""
        if not dental_facilities:
            print("No dental facilities data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to JSON
        json_filename = f"nabh_dental_facilities.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(dental_facilities, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(dental_facilities)} dental facilities to {json_filename}")
        
        # Save to CSV
        csv_filename = f"nabh_dental_facilities.csv"
        df = pd.DataFrame(dental_facilities)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Saved {len(dental_facilities)} dental facilities to {csv_filename}")
        
        # Print summary
        self._print_summary(dental_facilities)
    
    def _print_summary(self, dental_facilities):
        """Print summary of extracted data"""
        print(f"\n=== NABH Dental Facilities Extraction Summary ===")
        print(f"Total facilities extracted: {len(dental_facilities)}")
        
        # Status breakdown
        status_counts = {}
        for facility in dental_facilities:
            status = facility.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nStatus breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Country breakdown
        country_counts = {}
        for facility in dental_facilities:
            country = facility.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        print(f"\nCountry breakdown:")
        for country, count in country_counts.items():
            print(f"  {country}: {count}")
        
        # Sample facilities
        print(f"\nSample facilities:")
        for i, facility in enumerate(dental_facilities[:5]):
            print(f"  {i+1}. {facility.get('name', 'Unknown')} ({facility.get('status', 'Unknown')})")
    
    def run_extraction(self):
        """Run the complete extraction process"""
        print("Starting NABH Dental Facilities extraction...")
        
        dental_facilities = self.extract_dental_data()
        
        if dental_facilities:
            self.save_data(dental_facilities)
            print("Dental facilities extraction completed successfully!")
        else:
            print("No dental facilities data extracted. Please check the portal structure.")
        
        return dental_facilities

if __name__ == "__main__":
    extractor = NABHDentalExtractor()
    extractor.run_extraction()