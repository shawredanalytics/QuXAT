"""
NABH Data Extractor
Extracts accredited hospital information from NABH portal
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import re

class NABHDataExtractor:
    def __init__(self):
        self.base_url = "https://portal.nabh.co/frmViewAccreditedHosp.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_nabh_data(self):
        """Extract NABH accredited hospital data from the portal"""
        try:
            print("Fetching NABH accredited hospitals data...")
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table containing hospital data
            table = soup.find('table', {'id': 'GridView1'}) or soup.find('table', class_='table')
            
            if not table:
                # Try to find any table with hospital data
                tables = soup.find_all('table')
                for t in tables:
                    if 'Reference No' in str(t) or 'Acc. No' in str(t):
                        table = t
                        break
            
            if not table:
                print("Could not find hospital data table")
                return []
            
            hospitals = []
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:
                    hospital_data = {
                        'reference_no': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        'name': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        'accreditation_no': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                        'valid_from': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                        'valid_upto': cells[5].get_text(strip=True) if len(cells) > 5 else '',
                        'remarks': cells[6].get_text(strip=True) if len(cells) > 6 else '',
                        'accreditation_type': 'NABH',
                        'country': self._extract_country(cells[2].get_text(strip=True) if len(cells) > 2 else ''),
                        'status': self._determine_status(cells[5].get_text(strip=True) if len(cells) > 5 else '', 
                                                       cells[6].get_text(strip=True) if len(cells) > 6 else ''),
                        'extracted_date': datetime.now().isoformat()
                    }
                    
                    if hospital_data['name']:  # Only add if name exists
                        hospitals.append(hospital_data)
            
            print(f"Successfully extracted {len(hospitals)} NABH accredited hospitals")
            return hospitals
            
        except Exception as e:
            print(f"Error extracting NABH data: {str(e)}")
            return []
    
    def _extract_country(self, name):
        """Extract country from hospital name"""
        # Common country patterns in hospital names
        country_patterns = {
            'India': ['India', 'New Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad'],
            'Nepal': ['Nepal', 'Kathmandu', 'Pokhara'],
            'Bangladesh': ['Bangladesh', 'Dhaka', 'Chittagong'],
            'Philippines': ['Philippines', 'Manila', 'Batangas'],
            'Sri Lanka': ['Sri Lanka', 'Colombo'],
            'UAE': ['UAE', 'Dubai', 'Abu Dhabi'],
            'Saudi Arabia': ['Saudi Arabia', 'Riyadh', 'Jeddah']
        }
        
        name_lower = name.lower()
        for country, patterns in country_patterns.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    return country
        
        return 'India'  # Default to India for domestic hospitals
    
    def _determine_status(self, valid_upto, remarks):
        """Determine accreditation status"""
        if 'expired' in remarks.lower():
            return 'Expired'
        
        try:
            if valid_upto:
                valid_date = datetime.strptime(valid_upto, '%d %b %Y')
                if valid_date > datetime.now():
                    return 'Active'
                else:
                    return 'Expired'
        except:
            pass
        
        return 'Unknown'
    
    def save_to_json(self, hospitals, filename='nabh_hospitals.json'):
        """Save extracted data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(hospitals, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
    
    def save_to_csv(self, hospitals, filename='nabh_hospitals.csv'):
        """Save extracted data to CSV file"""
        try:
            df = pd.DataFrame(hospitals)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")

def main():
    """Main function to extract NABH data"""
    extractor = NABHDataExtractor()
    
    # Extract data
    hospitals = extractor.extract_nabh_data()
    
    if hospitals:
        # Save to both JSON and CSV
        extractor.save_to_json(hospitals)
        extractor.save_to_csv(hospitals)
        
        # Print summary
        print(f"\nExtraction Summary:")
        print(f"Total hospitals: {len(hospitals)}")
        
        # Count by status
        status_counts = {}
        for hospital in hospitals:
            status = hospital.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Status breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Count by country
        country_counts = {}
        for hospital in hospitals:
            country = hospital.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        print("Country breakdown:")
        for country, count in country_counts.items():
            print(f"  {country}: {count}")
    
    else:
        print("No data extracted")

if __name__ == "__main__":
    main()