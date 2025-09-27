#!/usr/bin/env python3
"""
NABH Entry Level Hospital Database Integrator
Integrates validated NABH entry-level hospital data into the QuXAT database system
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Any
import os
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NABHDatabaseIntegrator:
    def __init__(self):
        """Initialize the NABH database integrator"""
        self.main_database_file = 'unified_healthcare_organizations.json'
        self.backup_database_file = f'unified_healthcare_organizations_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        self.main_database = {'organizations': [], 'metadata': {}}
        self.nabh_hospitals = []
        self.existing_names = set()
        self.integration_stats = {
            'total_nabh_hospitals': 0,
            'new_hospitals_added': 0,
            'existing_hospitals_updated': 0,
            'duplicates_skipped': 0,
            'integration_date': datetime.now().isoformat(),
            'data_source': 'NABH Entry Level Portal'
        }
        
    def load_main_database(self) -> bool:
        """Load the main QuXAT database"""
        try:
            if os.path.exists(self.main_database_file):
                with open(self.main_database_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different database formats
                if isinstance(data, list):
                    # Old format - convert to new format
                    self.main_database = {
                        'organizations': data,
                        'metadata': {
                            'total_organizations': len(data),
                            'last_updated': datetime.now().isoformat(),
                            'data_sources': ['Legacy Data'],
                            'version': '2.0'
                        }
                    }
                elif isinstance(data, dict) and 'organizations' in data:
                    # New format
                    self.main_database = data
                else:
                    # Unknown format - create new structure
                    self.main_database = {
                        'organizations': [],
                        'metadata': {
                            'total_organizations': 0,
                            'last_updated': datetime.now().isoformat(),
                            'data_sources': [],
                            'version': '2.0'
                        }
                    }
                
                # Create set of existing hospital names for duplicate checking
                for hospital in self.main_database['organizations']:
                    if hospital.get('country') == 'India':
                        name_key = hospital.get('name', '').lower().strip()
                        self.existing_names.add(name_key)
                
                logger.info(f"Loaded {len(self.main_database['organizations'])} hospitals from main database")
                logger.info(f"Found {len(self.existing_names)} existing Indian hospitals")
                
            else:
                # Create new database structure
                self.main_database = {
                    'organizations': [],
                    'metadata': {
                        'total_organizations': 0,
                        'last_updated': datetime.now().isoformat(),
                        'data_sources': [],
                        'version': '2.0'
                    }
                }
                logger.info("Created new database structure")
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading main database: {e}")
            return False
    
    def load_nabh_hospital_data(self) -> bool:
        """Load validated NABH entry-level hospital data"""
        try:
            # Find the most recent validated NABH data file
            valid_files = glob.glob("nabh_entry_level_validated_valid_*.json")
            
            if not valid_files:
                logger.error("No validated NABH entry-level hospital data files found")
                return False
            
            # Use the most recent file
            latest_file = max(valid_files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.nabh_hospitals = json.load(f)
            
            self.integration_stats['total_nabh_hospitals'] = len(self.nabh_hospitals)
            logger.info(f"Loaded {len(self.nabh_hospitals)} validated NABH hospitals from {latest_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading NABH hospital data: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create backup of main database before integration"""
        try:
            with open(self.backup_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created backup: {self.backup_database_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def standardize_nabh_hospital_format(self, nabh_hospital: Dict[str, Any]) -> Dict[str, Any]:
        """Convert NABH hospital data to QuXAT database format"""
        
        # Extract hospital name (remove location info if present)
        full_name = nabh_hospital.get('name', '')
        hospital_name = full_name
        
        # Try to extract just the hospital name without location
        if ', ' in full_name:
            parts = full_name.split(', ')
            if len(parts) >= 2:
                hospital_name = parts[0].strip()
        
        # Determine hospital type based on name
        hospital_type = self._determine_hospital_type(hospital_name)
        
        # Create standardized hospital record
        standardized = {
            'name': hospital_name,
            'full_name': full_name,
            'country': nabh_hospital.get('country', 'India'),
            'state': nabh_hospital.get('state', ''),
            'city': nabh_hospital.get('city', ''),
            'address': nabh_hospital.get('address', ''),
            'hospital_type': hospital_type,
            'data_source': 'NABH Entry Level Portal',
            'source_url': nabh_hospital.get('portal_url', ''),
            'scraped_date': nabh_hospital.get('scraped_date', ''),
            'last_updated': datetime.now().isoformat(),
            'certifications': {
                'nabh_entry_level': {
                    'status': nabh_hospital.get('certification_status', 'Unknown'),
                    'accreditation_number': nabh_hospital.get('accreditation_number', ''),
                    'reference_number': nabh_hospital.get('reference_number', ''),
                    'valid_from': nabh_hospital.get('valid_from', ''),
                    'valid_upto': nabh_hospital.get('valid_upto', ''),
                    'valid_from_parsed': nabh_hospital.get('valid_from_parsed', ''),
                    'valid_upto_parsed': nabh_hospital.get('valid_upto_parsed', ''),
                    'remarks': nabh_hospital.get('remarks', ''),
                    'accreditation_level': nabh_hospital.get('accreditation_level', 'Entry Level'),
                    'accreditation_category': nabh_hospital.get('accreditation_category', 'NABH Entry Level'),
                    'verification_date': datetime.now().isoformat()
                }
            },
            'quality_indicators': {
                'nabh_accredited': True,
                'nabh_entry_level': True,
                'nabh_status': nabh_hospital.get('certification_status', 'Unknown'),
                'accreditation_current': nabh_hospital.get('certification_status') == 'Active'
            },
            'nabh_details': {
                'serial_number': nabh_hospital.get('serial_number', ''),
                'row_number': nabh_hospital.get('row_number', ''),
                'portal_extraction_date': nabh_hospital.get('scraped_date', ''),
                'validation_status': nabh_hospital.get('is_valid', True),
                'validation_issues': nabh_hospital.get('validation_issues', [])
            }
        }
        
        return standardized
    
    def _determine_hospital_type(self, hospital_name: str) -> str:
        """Determine hospital type based on name patterns"""
        name_lower = hospital_name.lower()
        
        # Specialty hospitals
        if any(keyword in name_lower for keyword in ['cancer', 'oncology', 'tumor']):
            return 'Cancer Specialty'
        elif any(keyword in name_lower for keyword in ['heart', 'cardiac', 'cardio']):
            return 'Cardiac Specialty'
        elif any(keyword in name_lower for keyword in ['eye', 'ophthal', 'vision']):
            return 'Eye Specialty'
        elif any(keyword in name_lower for keyword in ['kidney', 'nephro', 'dialysis']):
            return 'Nephrology Specialty'
        elif any(keyword in name_lower for keyword in ['maternity', 'women', 'gynec', 'obstet']):
            return 'Women & Child Specialty'
        elif any(keyword in name_lower for keyword in ['child', 'pediatric', 'paediatric']):
            return 'Pediatric Specialty'
        elif any(keyword in name_lower for keyword in ['ortho', 'bone', 'joint']):
            return 'Orthopedic Specialty'
        elif any(keyword in name_lower for keyword in ['neuro', 'brain', 'spine']):
            return 'Neurology Specialty'
        
        # Hospital categories
        elif any(keyword in name_lower for keyword in ['super specialty', 'super speciality', 'multispecialty', 'multi specialty']):
            return 'Multi-specialty Hospital'
        elif any(keyword in name_lower for keyword in ['medical college', 'teaching', 'university']):
            return 'Teaching Hospital'
        elif any(keyword in name_lower for keyword in ['district', 'government', 'govt', 'public']):
            return 'Government Hospital'
        elif any(keyword in name_lower for keyword in ['nursing home']):
            return 'Nursing Home'
        elif any(keyword in name_lower for keyword in ['clinic']):
            return 'Clinic'
        else:
            return 'General Hospital'
    
    def find_existing_hospital(self, nabh_hospital: Dict[str, Any]) -> Dict[str, Any]:
        """Find if hospital already exists in database"""
        nabh_name = nabh_hospital.get('name', '').lower().strip()
        nabh_city = nabh_hospital.get('city', '').lower().strip()
        nabh_state = nabh_hospital.get('state', '').lower().strip()
        
        for existing in self.main_database['organizations']:
            if existing.get('country') != 'India':
                continue
                
            existing_name = existing.get('name', '').lower().strip()
            existing_city = existing.get('city', '').lower().strip()
            existing_state = existing.get('state', '').lower().strip()
            
            # Exact name match
            if nabh_name == existing_name:
                return existing
            
            # Name similarity with location match
            if (nabh_city == existing_city and nabh_state == existing_state and
                (nabh_name in existing_name or existing_name in nabh_name)):
                return existing
        
        return None
    
    def update_existing_hospital(self, existing: Dict[str, Any], nabh_hospital: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing hospital with NABH certification data"""
        
        # Update certifications (existing database uses list format)
        if 'certifications' not in existing:
            existing['certifications'] = []
        
        # Handle case where certifications might be in different formats
        if not isinstance(existing['certifications'], list):
            # Convert to list format if it's not already
            existing['certifications'] = []
        
        # Check if NABH entry level certification already exists
        nabh_cert_exists = False
        for i, cert in enumerate(existing['certifications']):
            # Skip if cert is not a dictionary (handle malformed data)
            if not isinstance(cert, dict):
                continue
                
            if cert.get('type') == 'NABH Entry Level':
                # Update existing NABH certification
                existing['certifications'][i] = {
                    'name': 'National Accreditation Board for Hospitals & Healthcare Providers (NABH) - Entry Level',
                    'type': 'NABH Entry Level',
                    'status': nabh_hospital.get('certification_status', 'Unknown'),
                    'accreditation_date': nabh_hospital.get('valid_from', ''),
                    'expiry_date': nabh_hospital.get('valid_upto', ''),
                    'accreditation_no': nabh_hospital.get('accreditation_number', ''),
                    'reference_no': nabh_hospital.get('reference_number', ''),
                    'remarks': nabh_hospital.get('remarks', ''),
                    'score_impact': 15.0 if nabh_hospital.get('certification_status') == 'Active' else 0.0,
                    'source': 'NABH Entry Level Portal',
                    'verification_date': datetime.now().isoformat()
                }
                nabh_cert_exists = True
                break
        
        # Add new NABH certification if it doesn't exist
        if not nabh_cert_exists:
            nabh_certification = {
                'name': 'National Accreditation Board for Hospitals & Healthcare Providers (NABH) - Entry Level',
                'type': 'NABH Entry Level',
                'status': nabh_hospital.get('certification_status', 'Unknown'),
                'accreditation_date': nabh_hospital.get('valid_from', ''),
                'expiry_date': nabh_hospital.get('valid_upto', ''),
                'accreditation_no': nabh_hospital.get('accreditation_number', ''),
                'reference_no': nabh_hospital.get('reference_number', ''),
                'remarks': nabh_hospital.get('remarks', ''),
                'score_impact': 15.0 if nabh_hospital.get('certification_status') == 'Active' else 0.0,
                'source': 'NABH Entry Level Portal',
                'verification_date': datetime.now().isoformat()
            }
            existing['certifications'].append(nabh_certification)
        
        # Update quality indicators
        if 'quality_indicators' not in existing:
            existing['quality_indicators'] = {}
        
        existing['quality_indicators'].update({
            'nabh_accredited': True,
            'nabh_entry_level': True,
            'nabh_status': nabh_hospital.get('certification_status', 'Unknown'),
            'accreditation_current': nabh_hospital.get('certification_status') == 'Active'
        })
        
        # Add NABH details
        existing['nabh_details'] = {
            'serial_number': nabh_hospital.get('serial_number', ''),
            'row_number': nabh_hospital.get('row_number', ''),
            'portal_extraction_date': nabh_hospital.get('scraped_date', ''),
            'validation_status': nabh_hospital.get('is_valid', True),
            'validation_issues': nabh_hospital.get('validation_issues', [])
        }
        
        # Update metadata
        existing['last_updated'] = datetime.now().isoformat()
        if 'data_sources' not in existing:
            existing['data_sources'] = []
        if 'NABH Entry Level Portal' not in existing['data_sources']:
            existing['data_sources'].append('NABH Entry Level Portal')
        
        return existing
    
    def integrate_nabh_data(self) -> Dict[str, Any]:
        """Integrate NABH hospital data into main database"""
        logger.info("Starting NABH data integration...")
        
        processed_count = 0
        
        for nabh_hospital in self.nabh_hospitals:
            processed_count += 1
            
            # Check if hospital already exists
            existing = self.find_existing_hospital(nabh_hospital)
            
            if existing:
                # Update existing hospital with NABH data
                updated_hospital = self.update_existing_hospital(existing, nabh_hospital)
                self.integration_stats['existing_hospitals_updated'] += 1
                logger.debug(f"Updated existing hospital: {nabh_hospital.get('name', '')}")
                
            else:
                # Check for duplicate by name only
                name_key = nabh_hospital.get('name', '').lower().strip()
                if name_key in self.existing_names:
                    self.integration_stats['duplicates_skipped'] += 1
                    logger.debug(f"Skipped duplicate: {nabh_hospital.get('name', '')}")
                    continue
                
                # Add new hospital
                standardized_hospital = self.standardize_nabh_hospital_format(nabh_hospital)
                self.main_database['organizations'].append(standardized_hospital)
                self.existing_names.add(name_key)
                self.integration_stats['new_hospitals_added'] += 1
                logger.debug(f"Added new hospital: {nabh_hospital.get('name', '')}")
            
            if processed_count % 500 == 0:
                logger.info(f"Processed {processed_count} NABH hospitals...")
        
        # Update database metadata
        self._update_database_metadata()
        
        logger.info(f"NABH integration complete:")
        logger.info(f"  - Total NABH hospitals processed: {self.integration_stats['total_nabh_hospitals']}")
        logger.info(f"  - New hospitals added: {self.integration_stats['new_hospitals_added']}")
        logger.info(f"  - Existing hospitals updated: {self.integration_stats['existing_hospitals_updated']}")
        logger.info(f"  - Duplicates skipped: {self.integration_stats['duplicates_skipped']}")
        
        return self.integration_stats
    
    def _update_database_metadata(self):
        """Update database metadata after integration"""
        metadata = self.main_database['metadata']
        
        # Update basic metadata
        metadata['total_organizations'] = len(self.main_database['organizations'])
        metadata['last_updated'] = datetime.now().isoformat()
        metadata['version'] = '2.1'
        
        # Update data sources
        if 'data_sources' not in metadata:
            metadata['data_sources'] = []
        if 'NABH Entry Level Portal' not in metadata['data_sources']:
            metadata['data_sources'].append('NABH Entry Level Portal')
        
        # Add integration statistics
        if 'integration_stats' not in metadata:
            metadata['integration_stats'] = {}
        metadata['integration_stats']['nabh_entry_level'] = self.integration_stats
        
        # Add quality metrics
        nabh_hospitals = [org for org in self.main_database['organizations'] 
                         if org.get('quality_indicators', {}).get('nabh_entry_level', False)]
        
        metadata['quality_metrics'] = {
            'nabh_entry_level_hospitals': len(nabh_hospitals),
            'nabh_active_certifications': len([org for org in nabh_hospitals 
                                             if org.get('quality_indicators', {}).get('accreditation_current', False)]),
            'nabh_expired_certifications': len([org for org in nabh_hospitals 
                                              if not org.get('quality_indicators', {}).get('accreditation_current', False)])
        }
    
    def save_integrated_database(self) -> bool:
        """Save the integrated database"""
        try:
            # Save main database
            with open(self.main_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_database, f, indent=2, ensure_ascii=False)
            
            # Save integration report
            report_file = f"nabh_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.integration_stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved integrated database: {self.main_database_file}")
            logger.info(f"Saved integration report: {report_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving integrated database: {e}")
            return False

def main():
    """Main function to run NABH database integration"""
    print("="*60)
    print("NABH Entry Level Hospital Database Integration")
    print("="*60)
    
    # Initialize integrator
    integrator = NABHDatabaseIntegrator()
    
    # Load main database
    if not integrator.load_main_database():
        print("❌ Failed to load main database")
        return
    
    # Load NABH hospital data
    if not integrator.load_nabh_hospital_data():
        print("❌ Failed to load NABH hospital data")
        return
    
    # Create backup
    if not integrator.create_backup():
        print("❌ Failed to create backup")
        return
    
    # Integrate data
    stats = integrator.integrate_nabh_data()
    
    # Save integrated database
    if not integrator.save_integrated_database():
        print("❌ Failed to save integrated database")
        return
    
    # Print summary
    print("\n" + "="*60)
    print("NABH Integration Complete!")
    print("="*60)
    print(f"Total NABH hospitals processed: {stats['total_nabh_hospitals']}")
    print(f"New hospitals added: {stats['new_hospitals_added']}")
    print(f"Existing hospitals updated: {stats['existing_hospitals_updated']}")
    print(f"Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"Integration success rate: {((stats['new_hospitals_added'] + stats['existing_hospitals_updated']) / stats['total_nabh_hospitals'] * 100):.1f}%")
    
    print(f"\nDatabase now contains:")
    print(f"Total organizations: {integrator.main_database['metadata']['total_organizations']}")
    print(f"NABH entry-level hospitals: {integrator.main_database['metadata']['quality_metrics']['nabh_entry_level_hospitals']}")
    print(f"Active NABH certifications: {integrator.main_database['metadata']['quality_metrics']['nabh_active_certifications']}")
    print(f"Expired NABH certifications: {integrator.main_database['metadata']['quality_metrics']['nabh_expired_certifications']}")

if __name__ == "__main__":
    main()