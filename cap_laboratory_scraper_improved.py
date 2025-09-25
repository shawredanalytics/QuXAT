"""
Improved CAP 15189 Laboratory Data Scraper for QuXAT Healthcare Quality Grid
This module scrapes CAP 15189 accredited laboratory data using the provided web content
to build a comprehensive database of accredited healthcare laboratories.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedCAPLaboratoryScraper:
    """Improved scraper for CAP 15189 accredited laboratories using provided web content"""
    
    def __init__(self):
        self.laboratories = []
        # Use the actual laboratory data from the web content provided
        self.raw_data = """
        Accupath Diagnostic Laboratories, Inc.201 Summit View Dr., Suite 100Brentwood, TN 37027800-874-8532WebsiteCertificateAccupath Diagnostic Laboratories, Inc.5005 South 40th Street, Suite 1100 Phoenix, AZ 85040615-495-0615WebsiteCertificateAlmac Diagnostic Services20 Seagoe Industrial EstateCraigavon, Northern Ireland, BT63 5QDUnited Kingdom+44 (0) 28 3833 2200WebsiteCertificateAlmac Diagnostic Services LLC4238 Technology DriveDurham, North Carolina 27704919-479-8850WebsiteCertificateAlverno Laboratories2434 Interstate Plaza Dr.Hammond, IN 46324219-845-4026WebsiteCertificateARUP Laboratories500 Chipeta WaySalt Lake City, UT 84108801-583-2787WebsiteCertificateAvera McKennan Hospital & University Health CenterMain Laboratory800 E. 21st StreetSioux Falls, SD 57105605-322-8000WebsiteCertificateBioReference Health, LLC481 Edward H. Ross DriveElmwood Park, NJ 07407800-229-5227WebsiteCertificateCaris MPI Inc.d/b/a Caris Life Sciences4610 S. 44th PlacePhoenix, AZ 85040602-792-2442WebsiteCertificateCB Laboratory1687-1 Matoba, Kawagoe-shi, Saitama-ken350-1101 Japan+86 21 51371173WebsiteCertificateCentogene GmbHSchillingalee 68Rostock 18057Germany+49(0)381 203652 218WebsiteCertificateCleveland HeartLab6701 Carnegie Avenue - Suite 500Cleveland, Ohio 44103866-358-9828WebsiteCertificateCooperSurgical, Inc.3 Regent St.Livingston, NJ 07039877-282-3112WebsiteCertificateCrown BioScience GmbHFalkenried 88, Bldg. D20251 Hamburg, Germany+49 40 69 63 572 0WebsiteCertificateCytespace Africa Pty. Ltd.125 Amkoor RoadLyttelton Manor, Centurion, South Africa 0157+27 (0) 12 671 2333WebsiteCertificateDepartment of Pathology and Laboratory Medicine KingAbdulaziz Medical City-MNGHAKhashmlaan Road, Riyadh 11426Saudi Arabia+966-11-801-1111 ext. 13456WebsiteCertificateDianon Systems, Inc. and Esoterix Genetic Laboratories, LLC1 and 3 Forest ParkwayShelton, CT 06484203-926-7100WebsiteCertificateEsoterix, IncEndocrinology Laboratory4301 Lost Hills Rd.Calabasas, CA 91301818-867-1419WebsiteCertificateEsoterix Genetic Laboratories, LLC (MA)3400 Computer Dr.Westborough, MA 01581508-898-9001WebsiteCertificateEsoterix Genetic Laboratories, LLC (NM)2000 Vivigen WaySanta Fe, NM 87505800-848-4436WebsiteCertificateFleury S/A LaboratoryAvenida Morumbi, 8860 Sao Paulo, Brazil(55 11) 5014-7200WebsiteCertificateGC LabTech, Inc. 485 Spencer LaneSan Antonio, Texas 78201210-405-4258WebsiteCertificateGRAIL, Inc.4001 E NC 54 Hwy AssemblyDurham, NC 27709833-694-2553WebsiteCertificateGuardant Health, Inc505 Penobscot DriveRedwood City, CA 94063-4737650-458-7381WebsiteCertificateHenry Ford Health System2799 W. Grand Blvd.Detroit, MI 482024313-916-2964WebsiteCertificateICON Clinical Research LimitedSouth County Business ParkLeopardstown, Dublin 18, Ireland+353-1-291-2000WebsiteCertificateInivata Ltd. Clinical Laboratory NeoGenomicsGlenn Berge BuildingBabraham Research ParkCambridge CB22 3FH, United Kingdom239-768-0600WebsiteCertificateJoint Pathology Center Laboratory606 Stephen Sitter AvenueSilver Spring, MD 20910301-295-5002WebsiteCertificateKaleida Health Center for Laboratory Medicine115 Flint RoadWilliamsville, New York 14221716-626-7920WebsiteCertificateLabcorp Central Laboratory Services LP8211 SciCor DriveIndianapolis, IN 46214219-845-4026WebsiteCertificateLabcorp Central Laboratory Services S.a.r.l.7 rue MarcinhesGeneva, Switzerland+41-58-822-7000WebsiteCertificateLabcorp Development (Asia) Pte.Ltd.1 International Business Park, #01-01The Synergy Singapore 609917+41 65 6568 6567WebsiteCertificateLabcorp Pharmaceutical Research and Development (Shanghai) Co., Ltd.1st Floor, No. 6 Building, No. 151 Li Bing RoadZhangijiang Hi-Tech ParkShanghai 201203, China+86 21 5137 1173WebsiteCertificateLaboratory Corporation of America - Houston7207 N. GessnerHouston, TX 77040713-561-4453WebsiteCertificateLaboratory Corporation of America - Tampa, Florida5610 West LaSalle St.Tampa, FL 33607800-877-5227WebsiteCertificateLaboratory Corporation of AmericaCenter For Molecular Biology and Pathology1912 Alexander DriveResearch Triangle Park, NC 27709919-361-7168WebsiteCertificateLaboratory Corporation of America-Birmingham, AL1801 1st Avenue SouthBirmingham, AL 35233800-621-8037WebsiteCertificateLaboratory Corporation of America-Dallas7777 Forest Lane, Suite C350Dallas, TX 75230800-788-9892WebsiteCertificateLaboratory Corporation of America-Englewood8490 Upland DriveEnglewood, CO 80112602-453-6898WebsiteCertificateLaboratory Corporation of America-Phoenix5005 S. 40th St.Phoenix, AZ 85040800-788-9892WebsiteCertificateLaboratory Corporation of America-San Antonio6603 First Park Ten Blvd.San Antonio, TX 78213800-788-9892WebsiteCertificateLaboratory Corporation of America-Tennessee1924 Alcoa HighwayKnoxville, TN 37920865-305-9705WebsiteCertificateLaboratory Corporation of America Holdings19750 South Vermont Avenue, Suite 200
        """
    
    def parse_laboratory_data(self) -> List[Dict]:
        """
        Parse CAP 15189 accredited laboratory data from the raw content
        Returns a list of laboratory dictionaries with standardized format
        """
        try:
            logger.info("Parsing CAP laboratory data from web content")
            
            # Split the data by 'Website' or 'Certificate' markers
            entries = re.split(r'(?:Website|Certificate)', self.raw_data)
            
            for entry in entries:
                entry = entry.strip()
                if len(entry) > 20:  # Filter out very short entries
                    lab_data = self._parse_single_laboratory(entry)
                    if lab_data:
                        self.laboratories.append(lab_data)
            
            logger.info(f"Successfully parsed {len(self.laboratories)} laboratories")
            return self.laboratories
            
        except Exception as e:
            logger.error(f"Error parsing CAP laboratory data: {e}")
            return []
    
    def _parse_single_laboratory(self, entry: str) -> Optional[Dict]:
        """Parse a single laboratory entry"""
        try:
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            if not lines:
                return None
            
            # The first substantial line is usually the laboratory name
            name = lines[0] if lines else ""
            if len(name) < 5:
                return None
            
            # Extract address, phone, and location information
            address_parts = []
            phone = ""
            country = "United States"  # Default
            state = ""
            city = ""
            
            for line in lines[1:]:
                # Check for phone number patterns
                if self._is_phone_number(line):
                    phone = line
                else:
                    address_parts.append(line)
            
            # Parse address for location information
            full_address = ' '.join(address_parts)
            location_info = self._extract_location_info(full_address)
            
            # Create laboratory data structure
            lab_data = {
                'id': f"cap_{len(self.laboratories) + 1}",
                'name': name,
                'organization_type': 'Laboratory',
                'accreditation_type': 'CAP 15189',
                'accreditation_body': 'College of American Pathologists',
                'status': 'Active',
                'address': full_address,
                'phone': phone,
                'location': location_info,
                'certifications': [
                    {
                        'name': 'ISO 15189',
                        'issuer': 'College of American Pathologists',
                        'status': 'Active',
                        'issue_date': datetime.now().strftime('%Y-%m-%d'),
                        'type': 'Medical Laboratory Accreditation'
                    }
                ],
                'quality_initiatives': [
                    {
                        'name': 'CAP 15189 Accreditation Program',
                        'description': 'ISO 15189 accreditation for medical laboratories',
                        'status': 'Active',
                        'impact': 'High'
                    }
                ],
                'quality_score': self._calculate_quality_score(phone, full_address, location_info),
                'scraped_date': datetime.now().isoformat(),
                'data_source': 'CAP 15189 Accredited Laboratories'
            }
            
            return lab_data
            
        except Exception as e:
            logger.error(f"Error parsing laboratory entry: {e}")
            return None
    
    def _is_phone_number(self, text: str) -> bool:
        """Check if text contains a phone number"""
        phone_patterns = [
            r'\d{3}-\d{3}-\d{4}',  # US format
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # US format with parentheses
            r'\+\d{1,3}[\s\-\(\)]*\d{1,4}[\s\-\(\)]*\d{1,4}[\s\-\(\)]*\d{1,9}',  # International
            r'\d{3}\-\d{3}\-\d{4}',  # Standard US
            r'\+\d{2}\s?\(\d\)\s?\d{2,4}\s?\d{3,4}\s?\d{3,4}'  # European style
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _extract_location_info(self, address: str) -> Dict[str, str]:
        """Extract location information from address"""
        location = {}
        
        # US state and zip code pattern
        us_pattern = r'\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b'
        us_match = re.search(us_pattern, address)
        if us_match:
            location['state'] = us_match.group(1)
            location['zip_code'] = us_match.group(2)
            location['country'] = 'United States'
            return location
        
        # International location patterns
        country_patterns = {
            'United Kingdom': ['United Kingdom', 'UK', 'England', 'Scotland', 'Wales', 'Northern Ireland'],
            'Germany': ['Germany', 'Deutschland'],
            'Japan': ['Japan'],
            'Saudi Arabia': ['Saudi Arabia'],
            'Brazil': ['Brazil', 'Brasil'],
            'South Africa': ['South Africa'],
            'Ireland': ['Ireland'],
            'Switzerland': ['Switzerland'],
            'Singapore': ['Singapore'],
            'China': ['China', 'Shanghai', 'Beijing']
        }
        
        address_lower = address.lower()
        for country, keywords in country_patterns.items():
            if any(keyword.lower() in address_lower for keyword in keywords):
                location['country'] = country
                break
        
        if not location.get('country'):
            location['country'] = 'United States'  # Default
        
        return location
    
    def _calculate_quality_score(self, phone: str, address: str, location: Dict) -> float:
        """Calculate quality score based on available data and CAP accreditation"""
        base_score = 85.0  # Higher base score for CAP 15189 accreditation
        
        # Add points for data completeness
        if phone:
            base_score += 5.0
        if address and len(address) > 20:
            base_score += 5.0
        if location.get('country'):
            base_score += 3.0
        if location.get('state'):
            base_score += 2.0
        
        return min(base_score, 95.0)  # Cap at 95
    
    def save_to_json(self, filename: str = 'cap_laboratories_improved.json'):
        """Save parsed data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.laboratories, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.laboratories)} laboratories to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of parsed data"""
        if not self.laboratories:
            return {}
        
        countries = {}
        states = {}
        
        for lab in self.laboratories:
            country = lab.get('location', {}).get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
            
            state = lab.get('location', {}).get('state')
            if state:
                states[state] = states.get(state, 0) + 1
        
        return {
            'total_laboratories': len(self.laboratories),
            'countries': countries,
            'states': states,
            'average_quality_score': sum(lab.get('quality_score', 0) for lab in self.laboratories) / len(self.laboratories),
            'with_phone': sum(1 for lab in self.laboratories if lab.get('phone')),
            'with_complete_address': sum(1 for lab in self.laboratories if lab.get('address') and len(lab['address']) > 20)
        }

def main():
    """Main function to run the improved CAP laboratory scraper"""
    scraper = ImprovedCAPLaboratoryScraper()
    
    print("🔬 Starting Improved CAP 15189 Laboratory Data Parsing...")
    laboratories = scraper.parse_laboratory_data()
    
    if laboratories:
        print(f"✅ Successfully parsed {len(laboratories)} laboratories")
        
        # Save to JSON
        scraper.save_to_json()
        
        # Print summary
        stats = scraper.get_summary_stats()
        print("\n📊 Summary Statistics:")
        print(f"Total Laboratories: {stats.get('total_laboratories', 0)}")
        print(f"Average Quality Score: {stats.get('average_quality_score', 0):.1f}")
        print(f"With Phone: {stats.get('with_phone', 0)}")
        print(f"With Complete Address: {stats.get('with_complete_address', 0)}")
        
        if stats.get('countries'):
            print("\n🌍 Countries:")
            for country, count in sorted(stats['countries'].items()):
                print(f"  {country}: {count}")
        
        if stats.get('states'):
            print("\n🇺🇸 US States:")
            for state, count in sorted(stats['states'].items()):
                print(f"  {state}: {count}")
                
        # Show first few laboratories as examples
        print("\n📋 Sample Laboratories:")
        for i, lab in enumerate(laboratories[:3]):
            print(f"\n{i+1}. {lab['name']}")
            print(f"   Location: {lab['location'].get('country', 'Unknown')}")
            print(f"   Quality Score: {lab['quality_score']}")
            if lab.get('phone'):
                print(f"   Phone: {lab['phone']}")
    else:
        print("❌ No laboratory data was parsed")

if __name__ == "__main__":
    main()