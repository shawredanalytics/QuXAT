"""
Comprehensive Hospital Data Collection Strategy for QuXAT Scoring Database
=========================================================================

This module defines a comprehensive strategy for collecting all private hospitals in India
and mapping their quality certifications, accreditations, and initiatives available in the public domain.

Data Sources Identified:
1. Government Sources:
   - National Health Portal (data.gov.in) - Hospital Directory
   - All India Health Centres Directory (data.gov.in)
   - National Health Portal (nhp.gov.in) - Hospital Services

2. Accreditation Bodies:
   - NABH (National Accreditation Board for Hospitals & Healthcare Providers)
   - NABL (National Accreditation Board for Testing & Calibration Laboratories)
   - JCI (Joint Commission International)
   - ISO Certifications for Healthcare

3. Private Directories:
   - Medindia.net (105,255+ hospitals database)
   - Hospital association websites
   - State medical council directories

4. Quality Certifications to Map:
   - NABH Accreditation (Full & Entry Level)
   - NABL Accreditation for Labs
   - JCI Accreditation
   - ISO 9001:2015 Quality Management
   - ISO 14001:2015 Environmental Management
   - ISO 45001:2018 Occupational Health & Safety
   - Green OT Certification
   - CGHS/ECHS Empanelment
   - State Government Empanelments
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import re
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveHospitalDataCollector:
    """
    Comprehensive data collector for all private hospitals in India
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Data sources configuration
        self.data_sources = {
            'government': {
                'national_health_portal': 'https://www.nhp.gov.in/directoryservices/hospitals',
                'ogd_hospital_directory': 'https://www.data.gov.in/catalog/hospital-directory-national-health-portal',
                'health_centres_directory': 'https://www.data.gov.in/catalog/all-india-health-centres-directory'
            },
            'accreditation_bodies': {
                'nabh': 'https://nabh.co/find-a-healthcare-organisation/',
                'nabl': 'https://www.nabl-india.org/',
                'jci': 'https://www.jointcommissioninternational.org/accredited-organizations/',
                'iso': 'https://www.iso.org/members.html'
            },
            'private_directories': {
                'medindia': 'https://www.medindia.net/directories/hospitals/',
                'practo': 'https://www.practo.com/hospitals',
                'justdial': 'https://www.justdial.com/hospitals'
            }
        }
        
        # Quality certifications mapping
        self.certification_types = {
            'NABH': {
                'full_accreditation': 'NABH Full Accreditation',
                'entry_level': 'NABH Entry Level Certification',
                'pre_entry_level': 'NABH Pre-Entry Level Certification'
            },
            'NABL': {
                'medical_testing': 'NABL Medical Testing Laboratory',
                'calibration': 'NABL Calibration Laboratory'
            },
            'JCI': {
                'hospital': 'JCI Hospital Accreditation',
                'academic_medical_center': 'JCI Academic Medical Center',
                'clinical_care_program': 'JCI Clinical Care Program Certification'
            },
            'ISO': {
                'iso_9001': 'ISO 9001:2015 Quality Management',
                'iso_14001': 'ISO 14001:2015 Environmental Management',
                'iso_45001': 'ISO 45001:2018 Occupational Health & Safety'
            },
            'Government': {
                'cghs': 'CGHS Empanelment',
                'echs': 'ECHS Empanelment',
                'state_empanelment': 'State Government Empanelment'
            },
            'Specialty': {
                'green_ot': 'Green OT Certification',
                'fire_safety': 'Fire Safety Certificate',
                'pollution_control': 'Pollution Control Board Clearance'
            }
        }
        
        # Indian states for comprehensive coverage
        self.indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
            'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
            'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
            'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry', 'Chandigarh',
            'Andaman and Nicobar Islands', 'Dadra and Nagar Haveli and Daman and Diu',
            'Lakshadweep'
        ]
    
    def collect_government_hospital_data(self):
        """
        Collect hospital data from government sources
        """
        logger.info("Collecting hospital data from government sources...")
        hospitals = []
        
        try:
            # National Health Portal
            nhp_hospitals = self._extract_nhp_hospitals()
            hospitals.extend(nhp_hospitals)
            
            # Open Government Data Platform
            ogd_hospitals = self._extract_ogd_hospitals()
            hospitals.extend(ogd_hospitals)
            
        except Exception as e:
            logger.error(f"Error collecting government data: {e}")
        
        return hospitals
    
    def collect_nabh_accredited_hospitals(self):
        """
        Collect NABH accredited hospitals data
        """
        logger.info("Collecting NABH accredited hospitals...")
        hospitals = []
        
        try:
            # Use existing NABH data extractor
            from nabh_data_extractor import NABHDataExtractor
            nabh_extractor = NABHDataExtractor()
            nabh_hospitals = nabh_extractor.extract_nabh_data()
            
            # Filter for Indian hospitals only
            indian_nabh_hospitals = [
                hospital for hospital in nabh_hospitals 
                if hospital.get('country', '').lower() == 'india'
            ]
            
            hospitals.extend(indian_nabh_hospitals)
            
        except Exception as e:
            logger.error(f"Error collecting NABH data: {e}")
        
        return hospitals
    
    def collect_jci_accredited_hospitals(self):
        """
        Collect JCI accredited hospitals in India
        """
        logger.info("Collecting JCI accredited hospitals in India...")
        hospitals = []
        
        try:
            # Use existing JCI data extractor
            from jci_data_extractor import JCIDataExtractor
            jci_extractor = JCIDataExtractor()
            jci_hospitals = jci_extractor.extract_jci_data()
            
            # Filter for Indian hospitals only
            indian_jci_hospitals = [
                hospital for hospital in jci_hospitals 
                if hospital.get('country', '').lower() == 'india'
            ]
            
            hospitals.extend(indian_jci_hospitals)
            
        except Exception as e:
            logger.error(f"Error collecting JCI data: {e}")
        
        return hospitals
    
    def collect_private_directory_data(self):
        """
        Collect hospital data from private directories
        """
        logger.info("Collecting hospital data from private directories...")
        hospitals = []
        
        try:
            # Medindia hospitals
            medindia_hospitals = self._extract_medindia_hospitals()
            hospitals.extend(medindia_hospitals)
            
        except Exception as e:
            logger.error(f"Error collecting private directory data: {e}")
        
        return hospitals
    
    def _extract_nhp_hospitals(self):
        """Extract hospitals from National Health Portal"""
        hospitals = []
        
        try:
            response = self.session.get(self.data_sources['government']['national_health_portal'])
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse hospital data from NHP
            # Implementation depends on actual website structure
            
        except Exception as e:
            logger.error(f"Error extracting NHP hospitals: {e}")
        
        return hospitals
    
    def _extract_ogd_hospitals(self):
        """Extract hospitals from Open Government Data"""
        hospitals = []
        
        try:
            # This would require API access or CSV download
            # Implementation depends on available data format
            pass
            
        except Exception as e:
            logger.error(f"Error extracting OGD hospitals: {e}")
        
        return hospitals
    
    def _extract_medindia_hospitals(self):
        """Extract hospitals from Medindia directory"""
        hospitals = []
        
        try:
            # State-wise extraction from Medindia
            for state in self.indian_states:
                state_hospitals = self._extract_medindia_state_hospitals(state)
                hospitals.extend(state_hospitals)
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error extracting Medindia hospitals: {e}")
        
        return hospitals
    
    def _extract_medindia_state_hospitals(self, state):
        """Extract hospitals for a specific state from Medindia"""
        hospitals = []
        
        try:
            # Format state name for URL
            state_url = state.lower().replace(' ', '-')
            url = f"{self.data_sources['private_directories']['medindia']}{state_url}/"
            
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse hospital listings
            # Implementation depends on actual website structure
            
        except Exception as e:
            logger.error(f"Error extracting hospitals for {state}: {e}")
        
        return hospitals
    
    def consolidate_hospital_data(self):
        """
        Consolidate all hospital data from different sources
        """
        logger.info("Starting comprehensive hospital data collection...")
        
        all_hospitals = []
        
        # Collect from all sources
        government_hospitals = self.collect_government_hospital_data()
        nabh_hospitals = self.collect_nabh_accredited_hospitals()
        jci_hospitals = self.collect_jci_accredited_hospitals()
        private_hospitals = self.collect_private_directory_data()
        
        # Combine all sources
        all_hospitals.extend(government_hospitals)
        all_hospitals.extend(nabh_hospitals)
        all_hospitals.extend(jci_hospitals)
        all_hospitals.extend(private_hospitals)
        
        # Remove duplicates based on hospital name and location
        unique_hospitals = self._remove_duplicates(all_hospitals)
        
        # Enhance with certification mapping
        enhanced_hospitals = self._enhance_with_certifications(unique_hospitals)
        
        return enhanced_hospitals
    
    def _remove_duplicates(self, hospitals):
        """Remove duplicate hospitals based on name and location"""
        seen = set()
        unique_hospitals = []
        
        for hospital in hospitals:
            # Create a unique identifier
            identifier = f"{hospital.get('name', '').lower().strip()}_{hospital.get('city', '').lower().strip()}_{hospital.get('state', '').lower().strip()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_hospitals.append(hospital)
        
        return unique_hospitals
    
    def _enhance_with_certifications(self, hospitals):
        """Enhance hospital data with comprehensive certification mapping"""
        enhanced_hospitals = []
        
        for hospital in hospitals:
            # Add comprehensive certification structure
            hospital['certifications'] = {
                'nabh': self._check_nabh_certification(hospital),
                'nabl': self._check_nabl_certification(hospital),
                'jci': self._check_jci_certification(hospital),
                'iso': self._check_iso_certifications(hospital),
                'government': self._check_government_empanelments(hospital),
                'specialty': self._check_specialty_certifications(hospital)
            }
            
            # Calculate quality score based on certifications
            hospital['quality_score'] = self._calculate_quality_score(hospital['certifications'])
            
            enhanced_hospitals.append(hospital)
        
        return enhanced_hospitals
    
    def _check_nabh_certification(self, hospital):
        """Check NABH certification status"""
        # Implementation to verify NABH certification
        return {}
    
    def _check_nabl_certification(self, hospital):
        """Check NABL certification status"""
        # Implementation to verify NABL certification
        return {}
    
    def _check_jci_certification(self, hospital):
        """Check JCI certification status"""
        # Implementation to verify JCI certification
        return {}
    
    def _check_iso_certifications(self, hospital):
        """Check ISO certifications"""
        # Implementation to verify ISO certifications
        return {}
    
    def _check_government_empanelments(self, hospital):
        """Check government empanelments"""
        # Implementation to verify government empanelments
        return {}
    
    def _check_specialty_certifications(self, hospital):
        """Check specialty certifications"""
        # Implementation to verify specialty certifications
        return {}
    
    def _calculate_quality_score(self, certifications):
        """Calculate quality score based on certifications"""
        score = 0
        
        # NABH certifications
        if certifications.get('nabh', {}).get('full_accreditation'):
            score += 30
        elif certifications.get('nabh', {}).get('entry_level'):
            score += 20
        
        # JCI certification
        if certifications.get('jci', {}).get('accredited'):
            score += 25
        
        # ISO certifications
        iso_certs = certifications.get('iso', {})
        if iso_certs.get('iso_9001'):
            score += 15
        if iso_certs.get('iso_14001'):
            score += 10
        if iso_certs.get('iso_45001'):
            score += 10
        
        # Government empanelments
        gov_emp = certifications.get('government', {})
        if gov_emp.get('cghs') or gov_emp.get('echs'):
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def save_comprehensive_data(self, hospitals, filename_prefix='comprehensive_hospitals_india'):
        """Save comprehensive hospital data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_filename = f"{filename_prefix}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(hospitals, f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_filename = f"{filename_prefix}_{timestamp}.csv"
        df = pd.DataFrame(hospitals)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(hospitals)} hospitals to {json_filename} and {csv_filename}")
        
        return json_filename, csv_filename

def main():
    """Main execution function"""
    collector = ComprehensiveHospitalDataCollector()
    
    # Collect comprehensive hospital data
    hospitals = collector.consolidate_hospital_data()
    
    # Save the data
    json_file, csv_file = collector.save_comprehensive_data(hospitals)
    
    print(f"Comprehensive hospital data collection completed!")
    print(f"Total hospitals collected: {len(hospitals)}")
    print(f"Data saved to: {json_file} and {csv_file}")
    
    # Print summary statistics
    nabh_count = sum(1 for h in hospitals if h.get('certifications', {}).get('nabh', {}).get('full_accreditation'))
    jci_count = sum(1 for h in hospitals if h.get('certifications', {}).get('jci', {}).get('accredited'))
    
    print(f"\nCertification Summary:")
    print(f"NABH Accredited: {nabh_count}")
    print(f"JCI Accredited: {jci_count}")

if __name__ == "__main__":
    main()