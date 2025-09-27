import json
import logging
from datetime import datetime
from typing import Dict, List, Set
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseIntegrator:
    def __init__(self):
        self.main_database_file = 'unified_healthcare_organizations.json'
        self.backup_database_file = f'unified_healthcare_organizations_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        self.main_database = []
        self.new_hospitals = []
        self.existing_names = set()
        
    def load_main_database(self):
        """Load the main QuXAT database"""
        try:
            with open(self.main_database_file, 'r', encoding='utf-8') as f:
                self.main_database = json.load(f)
            
            # Create set of existing hospital names for duplicate checking
            for hospital in self.main_database:
                if hospital.get('country') == 'India':
                    name_key = hospital.get('name', '').lower().strip()
                    self.existing_names.add(name_key)
            
            logger.info(f"Loaded {len(self.main_database)} hospitals from main database")
            logger.info(f"Found {len(self.existing_names)} existing Indian hospitals")
            
        except FileNotFoundError:
            logger.error(f"Main database file {self.main_database_file} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading main database: {e}")
            raise

    def load_new_hospital_data(self):
        """Load newly collected hospital data"""
        # Find the most recent hospital data files
        hospital_files = []
        
        # Check for improved hospital data
        for filename in os.listdir('.'):
            if filename.startswith('improved_private_hospitals_india_') and filename.endswith('.json'):
                hospital_files.append(filename)
        
        # Check for enhanced hospital data
        for filename in os.listdir('.'):
            if filename.startswith('private_hospitals_india_') and filename.endswith('.json'):
                hospital_files.append(filename)
        
        if not hospital_files:
            logger.warning("No new hospital data files found")
            return
        
        # Use the most recent file
        latest_file = max(hospital_files, key=lambda x: os.path.getmtime(x))
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                self.new_hospitals = json.load(f)
            
            logger.info(f"Loaded {len(self.new_hospitals)} new hospitals from {latest_file}")
            
        except Exception as e:
            logger.error(f"Error loading new hospital data from {latest_file}: {e}")
            raise

    def create_backup(self):
        """Create backup of main database before integration"""
        try:
            with open(self.backup_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created backup: {self.backup_database_file}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    def standardize_hospital_format(self, hospital: Dict) -> Dict:
        """Standardize hospital data format to match main database schema"""
        standardized = {
            'name': hospital.get('name', ''),
            'country': 'India',
            'state': hospital.get('state', 'Unknown'),
            'city': hospital.get('city', 'Unknown'),
            'hospital_type': hospital.get('hospital_type', 'General Hospital'),
            'source': hospital.get('source', 'Web Scraping'),
            'scraped_date': hospital.get('scraped_date', datetime.now().isoformat()),
            'url': hospital.get('url', ''),
            'certifications': {}
        }
        
        # Process certifications
        certs = hospital.get('certifications', {})
        
        # NABH certification
        nabh_info = certs.get('nabh', {})
        if nabh_info.get('status') == 'Accredited':
            standardized['certifications']['NABH'] = {
                'status': 'Accredited',
                'level': nabh_info.get('level', 'Full'),
                'valid_until': nabh_info.get('valid_until'),
                'reference_no': nabh_info.get('reference_no')
            }
        
        # JCI certification
        jci_info = certs.get('jci', {})
        if jci_info.get('status') == 'Accredited':
            standardized['certifications']['JCI'] = {
                'status': 'Accredited',
                'accreditation_date': jci_info.get('accreditation_date'),
                'type': jci_info.get('type', 'Hospital')
            }
        
        # NABL certification
        nabl_info = certs.get('nabl', {})
        if nabl_info.get('status') == 'Accredited':
            standardized['certifications']['NABL'] = {
                'status': 'Accredited'
            }
        
        # ISO certifications
        iso_info = certs.get('iso', {})
        if iso_info.get('certifications'):
            standardized['certifications']['ISO'] = {
                'certifications': iso_info['certifications']
            }
        
        # Government empanelments
        gov_emp = certs.get('government_empanelments', [])
        if gov_emp:
            standardized['certifications']['Government_Empanelments'] = gov_emp
        
        # Calculate quality score based on certifications
        standardized['quality_score'] = self.calculate_quality_score(standardized['certifications'])
        
        return standardized

    def calculate_quality_score(self, certifications: Dict) -> float:
        """Calculate quality score based on certifications"""
        score = 0.0
        
        # Base score for being in database
        score += 1.0
        
        # NABH accreditation
        if 'NABH' in certifications:
            score += 2.0
            if certifications['NABH'].get('level') == 'Full':
                score += 0.5
        
        # JCI accreditation (international standard)
        if 'JCI' in certifications:
            score += 3.0
        
        # NABL accreditation
        if 'NABL' in certifications:
            score += 1.0
        
        # ISO certifications
        if 'ISO' in certifications and certifications['ISO'].get('certifications'):
            score += len(certifications['ISO']['certifications']) * 0.5
        
        # Government empanelments
        if 'Government_Empanelments' in certifications:
            score += len(certifications['Government_Empanelments']) * 0.3
        
        # Cap the score at 10.0
        return min(score, 10.0)

    def is_duplicate(self, hospital_name: str) -> bool:
        """Check if hospital is already in the database"""
        return hospital_name.lower().strip() in self.existing_names

    def integrate_new_hospitals(self):
        """Integrate new hospitals into the main database"""
        added_count = 0
        duplicate_count = 0
        
        for hospital in self.new_hospitals:
            hospital_name = hospital.get('name', '')
            
            if not hospital_name or self.is_duplicate(hospital_name):
                duplicate_count += 1
                continue
            
            # Standardize format
            standardized_hospital = self.standardize_hospital_format(hospital)
            
            # Add to main database
            self.main_database.append(standardized_hospital)
            self.existing_names.add(hospital_name.lower().strip())
            added_count += 1
        
        logger.info(f"Integration complete: {added_count} new hospitals added, {duplicate_count} duplicates skipped")
        return added_count, duplicate_count

    def save_updated_database(self):
        """Save the updated database"""
        try:
            with open(self.main_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.main_database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated database saved to {self.main_database_file}")
            logger.info(f"Total hospitals in database: {len(self.main_database)}")
            
        except Exception as e:
            logger.error(f"Error saving updated database: {e}")
            raise

    def generate_integration_report(self, added_count: int, duplicate_count: int):
        """Generate integration report"""
        report = {
            'integration_date': datetime.now().isoformat(),
            'hospitals_added': added_count,
            'duplicates_skipped': duplicate_count,
            'total_hospitals_in_database': len(self.main_database),
            'indian_hospitals_count': len([h for h in self.main_database if h.get('country') == 'India']),
            'certification_summary': {
                'nabh_accredited': len([h for h in self.main_database if h.get('country') == 'India' and 'NABH' in h.get('certifications', {})]),
                'jci_accredited': len([h for h in self.main_database if h.get('country') == 'India' and 'JCI' in h.get('certifications', {})]),
                'nabl_accredited': len([h for h in self.main_database if h.get('country') == 'India' and 'NABL' in h.get('certifications', {})]),
                'iso_certified': len([h for h in self.main_database if h.get('country') == 'India' and 'ISO' in h.get('certifications', {})])
            }
        }
        
        report_filename = f"database_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Integration report saved: {report_filename}")
        return report

    def run_integration(self):
        """Run the complete database integration process"""
        logger.info("Starting database integration process...")
        
        try:
            # Load data
            self.load_main_database()
            self.load_new_hospital_data()
            
            if not self.new_hospitals:
                logger.info("No new hospitals to integrate")
                return
            
            # Create backup
            self.create_backup()
            
            # Integrate new hospitals
            added_count, duplicate_count = self.integrate_new_hospitals()
            
            # Save updated database
            self.save_updated_database()
            
            # Generate report
            report = self.generate_integration_report(added_count, duplicate_count)
            
            # Print summary
            print(f"\nDatabase Integration Completed!")
            print(f"New hospitals added: {added_count}")
            print(f"Duplicates skipped: {duplicate_count}")
            print(f"Total hospitals in database: {len(self.main_database)}")
            print(f"Indian hospitals: {report['indian_hospitals_count']}")
            print(f"\nCertification Summary:")
            print(f"NABH Accredited: {report['certification_summary']['nabh_accredited']}")
            print(f"JCI Accredited: {report['certification_summary']['jci_accredited']}")
            print(f"NABL Accredited: {report['certification_summary']['nabl_accredited']}")
            print(f"ISO Certified: {report['certification_summary']['iso_certified']}")
            
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            raise

if __name__ == "__main__":
    integrator = DatabaseIntegrator()
    integrator.run_integration()