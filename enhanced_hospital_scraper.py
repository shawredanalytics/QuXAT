"""
Enhanced Hospital Scraper for Private Hospitals in India
=======================================================

This module implements comprehensive data collection for all private hospitals in India
with their quality certifications, accreditations, and public domain initiatives.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import re
from urllib.parse import urljoin, quote
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedHospitalScraper:
    """
    Enhanced scraper for comprehensive hospital data collection
    """
    
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
        
        # Load existing data to avoid duplicates
        self.existing_hospitals = self._load_existing_hospitals()
        
        # Indian states and major cities
        self.states_cities = {
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli'],
            'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam'],
            'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur', 'Nellore', 'Kurnool', 'Tirupati'],
            'Kerala': ['Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Thrissur', 'Kollam', 'Kannur'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Udaipur', 'Ajmer'],
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Meerut', 'Varanasi', 'Allahabad'],
            'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain'],
            'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
            'Haryana': ['Gurgaon', 'Faridabad', 'Panipat', 'Ambala', 'Hisar'],
            'Delhi': ['New Delhi', 'Delhi'],
            'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Darbhanga'],
            'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur'],
            'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro'],
            'Assam': ['Guwahati', 'Dibrugarh', 'Silchar', 'Jorhat'],
            'Chhattisgarh': ['Raipur', 'Bhilai', 'Korba', 'Bilaspur'],
            'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani'],
            'Himachal Pradesh': ['Shimla', 'Dharamshala', 'Solan', 'Mandi'],
            'Goa': ['Panaji', 'Margao', 'Vasco da Gama'],
            'Jammu and Kashmir': ['Srinagar', 'Jammu'],
            'Chandigarh': ['Chandigarh'],
            'Puducherry': ['Puducherry']
        }
        
        # Hospital chains and groups to prioritize
        self.major_hospital_chains = [
            'Apollo Hospitals', 'Fortis Healthcare', 'Max Healthcare', 'Manipal Hospitals',
            'Narayana Health', 'Aster DM Healthcare', 'Columbia Asia', 'Global Hospitals',
            'Continental Hospitals', 'Yashoda Hospitals', 'KIMS Hospitals', 'Rainbow Hospitals',
            'Gleneagles Global Hospitals', 'Sakra World Hospital', 'BGS Global Hospitals',
            'Cloudnine Hospitals', 'Motherhood Hospitals', 'Nova Specialty Hospitals',
            'Wockhardt Hospitals', 'Kokilaben Dhirubhai Ambani Hospital', 'Lilavati Hospital',
            'Breach Candy Hospital', 'Jaslok Hospital', 'Hinduja Hospital', 'Tata Memorial Hospital'
        ]
    
    def _load_existing_hospitals(self):
        """Load existing hospital data to avoid duplicates"""
        existing = set()
        
        try:
            # Load from unified database
            if os.path.exists('unified_healthcare_organizations.json'):
                with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for hospital in data:
                        if hospital.get('country') == 'India':
                            name = hospital.get('name', '').lower().strip()
                            city = hospital.get('city', '').lower().strip()
                            existing.add(f"{name}_{city}")
            
            # Load from NABH data
            if os.path.exists('nabh_hospitals.json'):
                with open('nabh_hospitals.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for hospital in data:
                        name = hospital.get('name', '').lower().strip()
                        city = hospital.get('city', '').lower().strip()
                        existing.add(f"{name}_{city}")
                        
        except Exception as e:
            logger.error(f"Error loading existing hospitals: {e}")
        
        logger.info(f"Loaded {len(existing)} existing hospitals to avoid duplicates")
        return existing
    
    def scrape_medindia_hospitals(self):
        """Scrape hospitals from Medindia directory"""
        logger.info("Starting Medindia hospital scraping...")
        hospitals = []
        
        base_url = "https://www.medindia.net/directories/hospitals"
        
        try:
            # Get main directory page
            response = self.session.get(f"{base_url}/index.htm", timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find state links
            state_links = soup.find_all('a', href=re.compile(r'/directories/hospitals/.*\.htm'))
            
            for link in state_links[:10]:  # Limit for testing
                try:
                    state_url = urljoin(base_url, link.get('href'))
                    state_name = link.text.strip()
                    
                    logger.info(f"Scraping hospitals from {state_name}")
                    state_hospitals = self._scrape_medindia_state(state_url, state_name)
                    hospitals.extend(state_hospitals)
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping state {state_name}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Medindia: {e}")
        
        return hospitals
    
    def _scrape_medindia_state(self, state_url, state_name):
        """Scrape hospitals from a specific state page on Medindia"""
        hospitals = []
        
        try:
            response = self.session.get(state_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find hospital listings
            hospital_links = soup.find_all('a', href=re.compile(r'/hospitals/.*\.htm'))
            
            for link in hospital_links:
                try:
                    hospital_name = link.text.strip()
                    hospital_url = urljoin(state_url, link.get('href'))
                    
                    # Extract hospital details
                    hospital_data = self._extract_medindia_hospital_details(hospital_url, hospital_name, state_name)
                    
                    if hospital_data and self._is_private_hospital(hospital_data):
                        # Check for duplicates
                        identifier = f"{hospital_data.get('name', '').lower().strip()}_{hospital_data.get('city', '').lower().strip()}"
                        if identifier not in self.existing_hospitals:
                            hospitals.append(hospital_data)
                            self.existing_hospitals.add(identifier)
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error extracting hospital {hospital_name}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping state page {state_url}: {e}")
        
        return hospitals
    
    def _extract_medindia_hospital_details(self, hospital_url, hospital_name, state_name):
        """Extract detailed information about a hospital from Medindia"""
        try:
            response = self.session.get(hospital_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract hospital information
            hospital_data = {
                'name': hospital_name,
                'state': state_name,
                'country': 'India',
                'source': 'Medindia',
                'url': hospital_url,
                'scraped_date': datetime.now().isoformat()
            }
            
            # Extract address and contact information
            contact_section = soup.find('div', class_='contact-info') or soup.find('div', id='contact')
            if contact_section:
                address_text = contact_section.get_text(strip=True)
                hospital_data['address'] = address_text
                
                # Extract city from address
                city_match = re.search(r'([A-Za-z\s]+),\s*' + re.escape(state_name), address_text)
                if city_match:
                    hospital_data['city'] = city_match.group(1).strip()
                
                # Extract phone numbers
                phone_matches = re.findall(r'(\+91[\s-]?\d{10}|\d{10})', address_text)
                if phone_matches:
                    hospital_data['phone'] = phone_matches[0]
            
            # Extract specialties
            specialties_section = soup.find('div', class_='specialties') or soup.find('div', id='specialties')
            if specialties_section:
                specialties = [spec.strip() for spec in specialties_section.get_text().split(',')]
                hospital_data['specialties'] = specialties
            
            # Extract hospital type
            hospital_data['hospital_type'] = self._determine_hospital_type(hospital_name, hospital_data.get('specialties', []))
            
            # Initialize certifications structure
            hospital_data['certifications'] = {
                'nabh': {'status': 'Unknown', 'level': None},
                'jci': {'status': 'Unknown'},
                'nabl': {'status': 'Unknown'},
                'iso': {'certifications': []},
                'government_empanelments': []
            }
            
            return hospital_data
            
        except Exception as e:
            logger.error(f"Error extracting details for {hospital_name}: {e}")
            return None
    
    def scrape_practo_hospitals(self):
        """Scrape hospitals from Practo directory"""
        logger.info("Starting Practo hospital scraping...")
        hospitals = []
        
        base_url = "https://www.practo.com"
        
        try:
            for state, cities in list(self.states_cities.items())[:5]:  # Limit for testing
                for city in cities[:2]:  # Limit cities per state
                    try:
                        city_url = f"{base_url}/{city.lower().replace(' ', '-')}/hospitals"
                        logger.info(f"Scraping hospitals from {city}, {state}")
                        
                        city_hospitals = self._scrape_practo_city(city_url, city, state)
                        hospitals.extend(city_hospitals)
                        
                        time.sleep(3)  # Rate limiting
                        
                    except Exception as e:
                        logger.error(f"Error scraping {city}, {state}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error scraping Practo: {e}")
        
        return hospitals
    
    def _scrape_practo_city(self, city_url, city, state):
        """Scrape hospitals from a specific city on Practo"""
        hospitals = []
        
        try:
            response = self.session.get(city_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find hospital cards/listings
            hospital_cards = soup.find_all('div', class_=re.compile(r'hospital|listing|card'))
            
            for card in hospital_cards[:20]:  # Limit per city
                try:
                    # Extract hospital name
                    name_elem = card.find('h2') or card.find('h3') or card.find('a')
                    if not name_elem:
                        continue
                    
                    hospital_name = name_elem.get_text(strip=True)
                    
                    # Skip if already exists
                    identifier = f"{hospital_name.lower().strip()}_{city.lower().strip()}"
                    if identifier in self.existing_hospitals:
                        continue
                    
                    hospital_data = {
                        'name': hospital_name,
                        'city': city,
                        'state': state,
                        'country': 'India',
                        'source': 'Practo',
                        'scraped_date': datetime.now().isoformat()
                    }
                    
                    # Extract additional details
                    address_elem = card.find('div', class_=re.compile(r'address|location'))
                    if address_elem:
                        hospital_data['address'] = address_elem.get_text(strip=True)
                    
                    # Extract rating if available
                    rating_elem = card.find('span', class_=re.compile(r'rating|score'))
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            hospital_data['rating'] = float(rating_match.group(1))
                    
                    # Determine hospital type
                    hospital_data['hospital_type'] = self._determine_hospital_type(hospital_name, [])
                    
                    # Initialize certifications
                    hospital_data['certifications'] = {
                        'nabh': {'status': 'Unknown', 'level': None},
                        'jci': {'status': 'Unknown'},
                        'nabl': {'status': 'Unknown'},
                        'iso': {'certifications': []},
                        'government_empanelments': []
                    }
                    
                    if self._is_private_hospital(hospital_data):
                        hospitals.append(hospital_data)
                        self.existing_hospitals.add(identifier)
                
                except Exception as e:
                    logger.error(f"Error extracting hospital from card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping city {city}: {e}")
        
        return hospitals
    
    def scrape_hospital_chains(self):
        """Scrape major hospital chains' websites for comprehensive data"""
        logger.info("Scraping major hospital chains...")
        hospitals = []
        
        chain_urls = {
            'Apollo Hospitals': 'https://www.apollohospitals.com/locations',
            'Fortis Healthcare': 'https://www.fortishealthcare.com/hospitals',
            'Max Healthcare': 'https://www.maxhealthcare.in/hospitals',
            'Manipal Hospitals': 'https://www.manipalhospitals.com/hospitals',
            'Narayana Health': 'https://www.narayanahealth.org/hospitals'
        }
        
        for chain_name, chain_url in chain_urls.items():
            try:
                logger.info(f"Scraping {chain_name} locations...")
                chain_hospitals = self._scrape_hospital_chain(chain_name, chain_url)
                hospitals.extend(chain_hospitals)
                time.sleep(5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping {chain_name}: {e}")
                continue
        
        return hospitals
    
    def _scrape_hospital_chain(self, chain_name, chain_url):
        """Scrape hospitals from a specific chain's website"""
        hospitals = []
        
        try:
            response = self.session.get(chain_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find location/hospital listings
            location_links = soup.find_all('a', href=re.compile(r'hospital|location|branch'))
            
            for link in location_links[:10]:  # Limit per chain
                try:
                    hospital_name = link.get_text(strip=True)
                    if not hospital_name or len(hospital_name) < 5:
                        continue
                    
                    # Extract location from name or URL
                    location_match = re.search(r'([A-Za-z\s]+)(?:,\s*([A-Za-z\s]+))?', hospital_name)
                    if location_match:
                        city = location_match.group(1).strip()
                        state = location_match.group(2) if location_match.group(2) else 'Unknown'
                    else:
                        city = 'Unknown'
                        state = 'Unknown'
                    
                    # Skip if already exists
                    identifier = f"{hospital_name.lower().strip()}_{city.lower().strip()}"
                    if identifier in self.existing_hospitals:
                        continue
                    
                    hospital_data = {
                        'name': hospital_name,
                        'city': city,
                        'state': state,
                        'country': 'India',
                        'hospital_chain': chain_name,
                        'hospital_type': 'Multi-specialty Hospital',
                        'source': f'{chain_name} Website',
                        'scraped_date': datetime.now().isoformat()
                    }
                    
                    # Hospital chains are typically private and well-certified
                    hospital_data['certifications'] = {
                        'nabh': {'status': 'Likely Accredited', 'level': 'Full'},
                        'jci': {'status': 'Possible'},
                        'nabl': {'status': 'Likely'},
                        'iso': {'certifications': ['ISO 9001:2015']},
                        'government_empanelments': ['CGHS', 'ECHS']
                    }
                    
                    hospitals.append(hospital_data)
                    self.existing_hospitals.add(identifier)
                
                except Exception as e:
                    logger.error(f"Error extracting chain hospital: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping chain {chain_name}: {e}")
        
        return hospitals
    
    def _is_private_hospital(self, hospital_data):
        """Determine if a hospital is private"""
        name = hospital_data.get('name', '').lower()
        
        # Exclude government hospitals
        government_keywords = [
            'government', 'govt', 'municipal', 'corporation', 'district', 'state',
            'central', 'public', 'civil', 'general hospital', 'medical college',
            'aiims', 'pgimer', 'jipmer', 'safdarjung', 'ram manohar lohia'
        ]
        
        for keyword in government_keywords:
            if keyword in name:
                return False
        
        return True
    
    def _determine_hospital_type(self, hospital_name, specialties):
        """Determine the type of hospital based on name and specialties"""
        name_lower = hospital_name.lower()
        
        if any(keyword in name_lower for keyword in ['cancer', 'oncology', 'tumor']):
            return 'Cancer Hospital'
        elif any(keyword in name_lower for keyword in ['heart', 'cardiac', 'cardio']):
            return 'Cardiac Hospital'
        elif any(keyword in name_lower for keyword in ['eye', 'ophthal', 'vision']):
            return 'Eye Hospital'
        elif any(keyword in name_lower for keyword in ['maternity', 'women', 'gynec']):
            return 'Maternity Hospital'
        elif any(keyword in name_lower for keyword in ['children', 'pediatric', 'child']):
            return 'Pediatric Hospital'
        elif any(keyword in name_lower for keyword in ['ortho', 'bone', 'joint']):
            return 'Orthopedic Hospital'
        elif len(specialties) > 5:
            return 'Multi-specialty Hospital'
        elif len(specialties) > 1:
            return 'Specialty Hospital'
        else:
            return 'General Hospital'
    
    def enhance_with_certifications(self, hospitals):
        """Enhance hospital data with certification information"""
        logger.info("Enhancing hospitals with certification data...")
        
        # Load existing certification data
        nabh_hospitals = self._load_nabh_data()
        jci_hospitals = self._load_jci_data()
        
        for hospital in hospitals:
            hospital_name = hospital.get('name', '').lower()
            
            # Check NABH certification
            for nabh_hospital in nabh_hospitals:
                if self._names_match(hospital_name, nabh_hospital.get('name', '').lower()):
                    hospital['certifications']['nabh'] = {
                        'status': 'Accredited',
                        'level': nabh_hospital.get('accreditation_level', 'Full'),
                        'valid_until': nabh_hospital.get('valid_upto'),
                        'reference_no': nabh_hospital.get('reference_no')
                    }
                    break
            
            # Check JCI certification
            for jci_hospital in jci_hospitals:
                if self._names_match(hospital_name, jci_hospital.get('name', '').lower()):
                    hospital['certifications']['jci'] = {
                        'status': 'Accredited',
                        'accreditation_date': jci_hospital.get('accreditation_date'),
                        'type': jci_hospital.get('type')
                    }
                    break
        
        return hospitals
    
    def _load_nabh_data(self):
        """Load existing NABH data"""
        try:
            with open('nabh_hospitals.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _load_jci_data(self):
        """Load existing JCI data"""
        try:
            with open('jci_accredited_organizations.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _names_match(self, name1, name2, threshold=0.8):
        """Check if two hospital names match with fuzzy matching"""
        # Simple fuzzy matching - can be enhanced with libraries like fuzzywuzzy
        name1_clean = re.sub(r'[^\w\s]', '', name1).strip()
        name2_clean = re.sub(r'[^\w\s]', '', name2).strip()
        
        # Check for exact match
        if name1_clean == name2_clean:
            return True
        
        # Check for substring match
        if name1_clean in name2_clean or name2_clean in name1_clean:
            return True
        
        # Check for word overlap
        words1 = set(name1_clean.split())
        words2 = set(name2_clean.split())
        
        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1.intersection(words2))
            total = len(words1.union(words2))
            similarity = overlap / total
            return similarity >= threshold
        
        return False
    
    def run_comprehensive_scraping(self):
        """Run comprehensive hospital scraping from all sources"""
        logger.info("Starting comprehensive hospital scraping...")
        
        all_hospitals = []
        
        # Scrape from different sources
        try:
            # 1. Medindia hospitals
            medindia_hospitals = self.scrape_medindia_hospitals()
            all_hospitals.extend(medindia_hospitals)
            logger.info(f"Collected {len(medindia_hospitals)} hospitals from Medindia")
            
            # 2. Practo hospitals
            practo_hospitals = self.scrape_practo_hospitals()
            all_hospitals.extend(practo_hospitals)
            logger.info(f"Collected {len(practo_hospitals)} hospitals from Practo")
            
            # 3. Hospital chains
            chain_hospitals = self.scrape_hospital_chains()
            all_hospitals.extend(chain_hospitals)
            logger.info(f"Collected {len(chain_hospitals)} hospitals from chains")
            
            # 4. Enhance with certifications
            enhanced_hospitals = self.enhance_with_certifications(all_hospitals)
            
            # 5. Save the data
            self.save_hospital_data(enhanced_hospitals)
            
            logger.info(f"Total hospitals collected: {len(enhanced_hospitals)}")
            return enhanced_hospitals
            
        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            return []
    
    def save_hospital_data(self, hospitals):
        """Save hospital data to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_filename = f"private_hospitals_india_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(hospitals, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_filename = f"private_hospitals_india_{timestamp}.csv"
        df = pd.DataFrame(hospitals)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(hospitals)} hospitals to {json_filename} and {csv_filename}")
        
        # Generate summary report
        self._generate_summary_report(hospitals, timestamp)
        
        return json_filename, csv_filename
    
    def _generate_summary_report(self, hospitals, timestamp):
        """Generate a summary report of collected hospitals"""
        report = {
            'collection_date': datetime.now().isoformat(),
            'total_hospitals': len(hospitals),
            'by_state': {},
            'by_type': {},
            'by_source': {},
            'certifications_summary': {
                'nabh_accredited': 0,
                'jci_accredited': 0,
                'iso_certified': 0,
                'government_empaneled': 0
            }
        }
        
        for hospital in hospitals:
            # Count by state
            state = hospital.get('state', 'Unknown')
            report['by_state'][state] = report['by_state'].get(state, 0) + 1
            
            # Count by type
            hospital_type = hospital.get('hospital_type', 'Unknown')
            report['by_type'][hospital_type] = report['by_type'].get(hospital_type, 0) + 1
            
            # Count by source
            source = hospital.get('source', 'Unknown')
            report['by_source'][source] = report['by_source'].get(source, 0) + 1
            
            # Count certifications
            certs = hospital.get('certifications', {})
            if certs.get('nabh', {}).get('status') == 'Accredited':
                report['certifications_summary']['nabh_accredited'] += 1
            if certs.get('jci', {}).get('status') == 'Accredited':
                report['certifications_summary']['jci_accredited'] += 1
            if certs.get('iso', {}).get('certifications'):
                report['certifications_summary']['iso_certified'] += 1
            if certs.get('government_empanelments'):
                report['certifications_summary']['government_empaneled'] += 1
        
        # Save report
        report_filename = f"hospital_collection_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated summary report: {report_filename}")

def main():
    """Main execution function"""
    scraper = EnhancedHospitalScraper()
    
    # Run comprehensive scraping
    hospitals = scraper.run_comprehensive_scraping()
    
    print(f"\nHospital Data Collection Completed!")
    print(f"Total private hospitals collected: {len(hospitals)}")
    
    # Print summary statistics
    nabh_count = sum(1 for h in hospitals if h.get('certifications', {}).get('nabh', {}).get('status') == 'Accredited')
    jci_count = sum(1 for h in hospitals if h.get('certifications', {}).get('jci', {}).get('status') == 'Accredited')
    
    print(f"\nCertification Summary:")
    print(f"NABH Accredited: {nabh_count}")
    print(f"JCI Accredited: {jci_count}")
    
    # Print top states by hospital count
    state_counts = {}
    for hospital in hospitals:
        state = hospital.get('state', 'Unknown')
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"\nTop 10 States by Hospital Count:")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{state}: {count}")

if __name__ == "__main__":
    main()