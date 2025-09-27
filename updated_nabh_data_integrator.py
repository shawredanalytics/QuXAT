#!/usr/bin/env python3
"""
Updated NABH Data Integrator for QuXAT System
Integrates validated NABH hospital data into the unified healthcare organizations database.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UpdatedNABHDataIntegrator:
    def __init__(self, validated_data_file: str, unified_db_file: str = "unified_healthcare_organizations.json"):
        self.validated_data_file = validated_data_file
        self.unified_db_file = unified_db_file
        self.integration_stats = {
            'total_validated_hospitals': 0,
            'new_hospitals_added': 0,
            'existing_hospitals_updated': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'integration_timestamp': datetime.now().isoformat()
        }
        
    def load_validated_data(self) -> List[Dict[str, Any]]:
        """Load validated NABH hospital data."""
        try:
            with open(self.validated_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle different data formats
                if isinstance(data, list):
                    hospitals = data
                elif isinstance(data, dict):
                    hospitals = data.get('validated_hospitals', data.get('hospitals', []))
                else:
                    hospitals = []
                
                self.integration_stats['total_validated_hospitals'] = len(hospitals)
                logger.info(f"Loaded {len(hospitals)} validated hospitals from {self.validated_data_file}")
                return hospitals
        except Exception as e:
            logger.error(f"Error loading validated data: {e}")
            return []
    
    def load_unified_database(self) -> Dict[str, Any]:
        """Load the unified healthcare organizations database."""
        try:
            if os.path.exists(self.unified_db_file):
                with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded existing database with {len(data.get('organizations', []))} organizations")
                    return data
            else:
                logger.info("Creating new unified database")
                return {
                    "metadata": {
                        "created_date": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "version": "1.0",
                        "total_organizations": 0,
                        "data_sources": []
                    },
                    "organizations": []
                }
        except Exception as e:
            logger.error(f"Error loading unified database: {e}")
            return {"metadata": {}, "organizations": []}
    
    def normalize_hospital_data(self, hospital: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize NABH hospital data to unified format."""
        try:
            # Ensure hospital is a dictionary
            if not isinstance(hospital, dict):
                logger.error(f"Hospital data is not a dictionary: {type(hospital)}")
                return None
                
            # Extract basic information
            normalized = {
                "name": str(hospital.get('name', '')).strip(),
                "original_name": str(hospital.get('name', '')).strip(),
                "city": str(hospital.get('city', '')).strip(),
                "state": str(hospital.get('state', '')).strip(),
                "country": str(hospital.get('country', 'India')),
                "hospital_type": "Hospital",
                "data_source": "NABH_Updated_Portal",
                "last_updated": datetime.now().isoformat()
            }
            
            # Add address if available
            address = hospital.get('address')
            if address:
                normalized["address"] = str(address).strip()
            
            # Add NABH certification information
            certifications = []
            
            # Create NABH certification entry
            nabh_cert = {
                "type": "NABH",
                "level": str(hospital.get('accreditation_level', 'Entry Level')),
                "category": str(hospital.get('accreditation_category', 'Hospital')),
                "status": str(hospital.get('certification_status', 'Unknown')),
                "accreditation_number": str(hospital.get('accreditation_number', '')),
                "reference_number": str(hospital.get('reference_number', '')),
                "valid_from": hospital.get('valid_from_parsed'),
                "valid_upto": hospital.get('valid_upto_parsed'),
                "remarks": str(hospital.get('remarks', '')),
                "source": "NABH Updated Portal",
                "scraped_date": hospital.get('scraped_date'),
                "portal_url": str(hospital.get('portal_url', '')),
                "data_version": str(hospital.get('data_version', '')),
                "serial_number": str(hospital.get('serial_number', '')),
                "row_number": hospital.get('row_number', 0)
            }
            
            certifications.append(nabh_cert)
            normalized["certifications"] = certifications
            
            # Add quality metrics
            normalized["quality_score"] = hospital.get('quality_score', 0)
            normalized["data_completeness"] = hospital.get('data_completeness', 0)
            
            # Add additional metadata
            normalized["metadata"] = {
                "integration_source": "Updated NABH Portal Integration",
                "integration_date": datetime.now().isoformat(),
                "original_data_version": str(hospital.get('data_version', '')),
                "validation_status": "validated"
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing hospital data for {hospital.get('name', 'Unknown') if isinstance(hospital, dict) else 'Unknown'}: {e}")
            self.integration_stats['errors'] += 1
            return None
    
    def find_existing_hospital(self, new_hospital: Dict[str, Any], existing_orgs: List[Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        """Find if hospital already exists in database."""
        new_name = new_hospital.get('name', '').lower().strip()
        new_city = new_hospital.get('city', '').lower().strip()
        new_state = new_hospital.get('state', '').lower().strip()
        
        # Get NABH accreditation number from new hospital
        new_nabh_acc_num = ""
        for cert in new_hospital.get('certifications', []):
            if cert.get('type') == 'NABH' and cert.get('accreditation_number'):
                new_nabh_acc_num = cert['accreditation_number'].strip()
                break
        
        for idx, org in enumerate(existing_orgs):
            # Skip if org is not a dictionary (handle corrupted data)
            if not isinstance(org, dict):
                continue
                
            org_name = org.get('name', '').lower().strip()
            org_city = org.get('city', '').lower().strip()
            org_state = org.get('state', '').lower().strip()
            
            # Check for exact name match with same location
            if (new_name == org_name and 
                new_city == org_city and 
                new_state == org_state):
                return idx, org
            
            # Check for NABH accreditation number match
            if new_nabh_acc_num:
                for cert in org.get('certifications', []):
                    if (cert.get('type') == 'NABH' and 
                        cert.get('accreditation_number', '').strip() == new_nabh_acc_num):
                        return idx, org
            
            # Check for similar name match (fuzzy matching)
            if (new_city == org_city and 
                new_state == org_state and
                (new_name in org_name or org_name in new_name) and
                len(new_name) > 5 and len(org_name) > 5):
                return idx, org
        
        return -1, None
    
    def merge_hospital_data(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new hospital data with existing data."""
        try:
            merged = existing.copy()
            
            # Update basic fields if new data is more complete
            for field in ['address', 'hospital_type']:
                if new.get(field) and (not existing.get(field) or len(new[field]) > len(existing.get(field, ''))):
                    merged[field] = new[field]
            
            # Update last_updated timestamp
            merged['last_updated'] = datetime.now().isoformat()
            
            # Merge certifications
            existing_certs = merged.get('certifications', [])
            new_certs = new.get('certifications', [])
            
            # Check if NABH certification already exists
            nabh_cert_exists = False
            for i, cert in enumerate(existing_certs):
                if cert.get('type') == 'NABH':
                    # Update existing NABH certification with newer data
                    for new_cert in new_certs:
                        if new_cert.get('type') == 'NABH':
                            # Keep the newer or more complete certification
                            if (new_cert.get('scraped_date', '') > cert.get('scraped_date', '') or
                                len(str(new_cert.get('accreditation_number', ''))) > len(str(cert.get('accreditation_number', '')))):
                                existing_certs[i] = new_cert
                            nabh_cert_exists = True
                            break
                    break
            
            # Add new NABH certification if it doesn't exist
            if not nabh_cert_exists:
                for new_cert in new_certs:
                    if new_cert.get('type') == 'NABH':
                        existing_certs.append(new_cert)
                        break
            
            merged['certifications'] = existing_certs
            
            # Update quality metrics if new data is better
            if new.get('quality_score', 0) > existing.get('quality_score', 0):
                merged['quality_score'] = new['quality_score']
            
            if new.get('data_completeness', 0) > existing.get('data_completeness', 0):
                merged['data_completeness'] = new['data_completeness']
            
            # Update metadata
            if 'metadata' not in merged:
                merged['metadata'] = {}
            
            merged['metadata'].update({
                'last_integration_date': datetime.now().isoformat(),
                'integration_source': 'Updated NABH Portal Integration',
                'update_type': 'merged'
            })
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging hospital data: {e}")
            return existing
    
    def integrate_data(self) -> Dict[str, Any]:
        """Main integration process."""
        logger.info("Starting updated NABH data integration...")
        
        # Load data
        validated_hospitals = self.load_validated_data()
        if not validated_hospitals:
            logger.error("No validated hospitals to integrate")
            return self.integration_stats
        
        unified_db = self.load_unified_database()
        existing_orgs = unified_db.get('organizations', [])
        
        logger.info(f"Processing {len(validated_hospitals)} validated hospitals...")
        
        # Process each validated hospital
        for i, hospital in enumerate(validated_hospitals):
            try:
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(validated_hospitals)} hospitals...")
                
                # Normalize hospital data
                normalized_hospital = self.normalize_hospital_data(hospital)
                if not normalized_hospital:
                    continue
                
                # Check if hospital already exists
                existing_idx, existing_hospital = self.find_existing_hospital(normalized_hospital, existing_orgs)
                
                if existing_idx >= 0:
                    # Update existing hospital
                    merged_hospital = self.merge_hospital_data(existing_hospital, normalized_hospital)
                    existing_orgs[existing_idx] = merged_hospital
                    self.integration_stats['existing_hospitals_updated'] += 1
                else:
                    # Add new hospital
                    existing_orgs.append(normalized_hospital)
                    self.integration_stats['new_hospitals_added'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing hospital {hospital.get('name', 'Unknown')}: {e}")
                self.integration_stats['errors'] += 1
                continue
        
        # Update unified database metadata
        unified_db['organizations'] = existing_orgs
        unified_db['metadata'].update({
            'last_updated': datetime.now().isoformat(),
            'total_organizations': len(existing_orgs),
            'last_integration': {
                'source': 'Updated NABH Portal',
                'timestamp': datetime.now().isoformat(),
                'hospitals_processed': len(validated_hospitals),
                'new_added': self.integration_stats['new_hospitals_added'],
                'existing_updated': self.integration_stats['existing_hospitals_updated'],
                'errors': self.integration_stats['errors']
            }
        })
        
        # Add data source if not already present
        data_sources = unified_db['metadata'].get('data_sources', [])
        nabh_source = {
            'name': 'Updated NABH Portal',
            'url': 'https://portal.nabh.co/frmViewApplicantEntryLevelHosp.aspx#gsc.tab=0',
            'last_updated': datetime.now().isoformat(),
            'type': 'Hospital Accreditation',
            'records_count': len(validated_hospitals)
        }
        
        # Update or add NABH source
        nabh_source_exists = False
        for i, source in enumerate(data_sources):
            # Handle both string and dict formats
            source_name = source if isinstance(source, str) else source.get('name', '')
            if 'NABH' in source_name:
                if isinstance(source, str):
                    data_sources[i] = nabh_source
                else:
                    data_sources[i] = nabh_source
                nabh_source_exists = True
                break
        
        if not nabh_source_exists:
            data_sources.append(nabh_source)
        
        unified_db['metadata']['data_sources'] = data_sources
        
        # Save updated database
        self.save_updated_database(unified_db)
        
        # Generate integration report
        self.generate_integration_report()
        
        logger.info("Updated NABH data integration completed successfully!")
        return self.integration_stats
    
    def save_updated_database(self, unified_db: Dict[str, Any]):
        """Save the updated unified database."""
        try:
            with open(self.unified_db_file, 'w', encoding='utf-8') as f:
                json.dump(unified_db, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated database saved to {self.unified_db_file}")
        except Exception as e:
            logger.error(f"Error saving updated database: {e}")
    
    def generate_integration_report(self):
        """Generate integration report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"updated_nabh_integration_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.integration_stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Integration report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error saving integration report: {e}")

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python updated_nabh_data_integrator.py <validated_data_file>")
        sys.exit(1)
    
    validated_data_file = sys.argv[1]
    
    if not os.path.exists(validated_data_file):
        print(f"Error: Validated data file '{validated_data_file}' not found")
        sys.exit(1)
    
    # Initialize integrator
    integrator = UpdatedNABHDataIntegrator(validated_data_file)
    
    # Run integration
    stats = integrator.integrate_data()
    
    # Print summary
    print("\nUpdated NABH Data Integration Summary:")
    print("=" * 50)
    print(f"Total validated hospitals processed: {stats['total_validated_hospitals']}")
    print(f"New hospitals added: {stats['new_hospitals_added']}")
    print(f"Existing hospitals updated: {stats['existing_hospitals_updated']}")
    print(f"Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"Errors encountered: {stats['errors']}")
    print(f"Integration timestamp: {stats['integration_timestamp']}")
    
    success_rate = ((stats['new_hospitals_added'] + stats['existing_hospitals_updated']) / 
                   stats['total_validated_hospitals'] * 100) if stats['total_validated_hospitals'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()