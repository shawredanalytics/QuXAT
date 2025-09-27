#!/usr/bin/env python3
"""
Simple NABH Data Integrator for QuXAT System
Directly adds validated NABH hospital data to the unified healthcare organizations database.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleNABHIntegrator:
    def __init__(self, validated_data_file: str, unified_db_file: str = "unified_healthcare_organizations.json"):
        self.validated_data_file = validated_data_file
        self.unified_db_file = unified_db_file
        self.integration_stats = {
            'total_validated_hospitals': 0,
            'new_hospitals_added': 0,
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
    
    def convert_to_unified_format(self, hospital: Dict[str, Any]) -> Dict[str, Any]:
        """Convert NABH hospital data to unified format."""
        try:
            # Create unified hospital entry
            unified_hospital = {
                "name": hospital.get('name', '').strip(),
                "original_name": hospital.get('name', '').strip(),
                "city": hospital.get('city', '').strip(),
                "state": hospital.get('state', '').strip(),
                "country": hospital.get('country', 'India'),
                "hospital_type": "Hospital",
                "data_source": "Updated_NABH_Portal",
                "last_updated": datetime.now().isoformat()
            }
            
            # Add address if available
            if hospital.get('address'):
                unified_hospital["address"] = hospital['address'].strip()
            
            # Create NABH certification
            nabh_certification = {
                "type": "NABH",
                "level": hospital.get('accreditation_level', 'Entry Level'),
                "category": hospital.get('accreditation_category', 'Hospital'),
                "status": hospital.get('certification_status', 'Unknown'),
                "accreditation_number": hospital.get('accreditation_number', ''),
                "reference_number": hospital.get('reference_number', ''),
                "valid_from": hospital.get('valid_from_parsed'),
                "valid_upto": hospital.get('valid_upto_parsed'),
                "remarks": hospital.get('remarks', ''),
                "source": "Updated NABH Portal",
                "scraped_date": hospital.get('scraped_date'),
                "portal_url": hospital.get('portal_url', ''),
                "data_version": hospital.get('data_version', ''),
                "serial_number": hospital.get('serial_number', ''),
                "row_number": hospital.get('row_number', 0)
            }
            
            unified_hospital["certifications"] = [nabh_certification]
            
            # Add quality metrics
            unified_hospital["quality_score"] = hospital.get('data_quality_score', 0)
            unified_hospital["data_completeness"] = hospital.get('data_completeness', 0)
            
            # Add metadata
            unified_hospital["metadata"] = {
                "integration_source": "Updated NABH Portal Integration",
                "integration_date": datetime.now().isoformat(),
                "original_data_version": hospital.get('data_version', ''),
                "validation_status": "validated"
            }
            
            return unified_hospital
            
        except Exception as e:
            logger.error(f"Error converting hospital {hospital.get('name', 'Unknown')}: {e}")
            return None
    
    def integrate_data(self) -> Dict[str, Any]:
        """Main integration process."""
        logger.info("Starting simple NABH data integration...")
        
        # Load data
        validated_hospitals = self.load_validated_data()
        if not validated_hospitals:
            logger.error("No validated hospitals to integrate")
            return self.integration_stats
        
        unified_db = self.load_unified_database()
        existing_orgs = unified_db.get('organizations', [])
        
        logger.info(f"Converting {len(validated_hospitals)} validated hospitals...")
        
        # Convert and add each hospital
        new_hospitals = []
        for i, hospital in enumerate(validated_hospitals):
            try:
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(validated_hospitals)} hospitals...")
                
                # Convert to unified format
                unified_hospital = self.convert_to_unified_format(hospital)
                if unified_hospital:
                    new_hospitals.append(unified_hospital)
                    self.integration_stats['new_hospitals_added'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing hospital {hospital.get('name', 'Unknown')}: {e}")
                continue
        
        # Add new hospitals to existing organizations
        existing_orgs.extend(new_hospitals)
        
        # Update unified database
        unified_db['organizations'] = existing_orgs
        unified_db['metadata'].update({
            'last_updated': datetime.now().isoformat(),
            'total_organizations': len(existing_orgs),
            'last_integration': {
                'source': 'Updated NABH Portal',
                'timestamp': datetime.now().isoformat(),
                'hospitals_processed': len(validated_hospitals),
                'new_added': self.integration_stats['new_hospitals_added']
            }
        })
        
        # Update data sources
        data_sources = unified_db['metadata'].get('data_sources', [])
        updated_nabh_source = "Updated NABH Portal"
        
        if updated_nabh_source not in data_sources:
            data_sources.append(updated_nabh_source)
        
        unified_db['metadata']['data_sources'] = data_sources
        
        # Save updated database
        self.save_updated_database(unified_db)
        
        # Generate integration report
        self.generate_integration_report()
        
        logger.info("Simple NABH data integration completed successfully!")
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
        report_file = f"simple_nabh_integration_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.integration_stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Integration report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error saving integration report: {e}")

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python simple_nabh_integrator.py <validated_data_file>")
        sys.exit(1)
    
    validated_data_file = sys.argv[1]
    
    if not os.path.exists(validated_data_file):
        print(f"Error: Validated data file '{validated_data_file}' not found")
        sys.exit(1)
    
    # Initialize integrator
    integrator = SimpleNABHIntegrator(validated_data_file)
    
    # Run integration
    stats = integrator.integrate_data()
    
    # Print summary
    print("\nSimple NABH Data Integration Summary:")
    print("=" * 50)
    print(f"Total validated hospitals processed: {stats['total_validated_hospitals']}")
    print(f"New hospitals added: {stats['new_hospitals_added']}")
    print(f"Integration timestamp: {stats['integration_timestamp']}")
    
    success_rate = (stats['new_hospitals_added'] / stats['total_validated_hospitals'] * 100) if stats['total_validated_hospitals'] > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()