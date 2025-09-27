#!/usr/bin/env python3
"""
NABH Dental Facilities Integrator for QuXAT System
Integrates validated NABH dental facilities data into the unified healthcare organizations database.
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

class DentalFacilitiesIntegrator:
    def __init__(self, dental_data_file: str = "nabh_dental_facilities.json", unified_db_file: str = "unified_healthcare_organizations.json"):
        self.dental_data_file = dental_data_file
        self.unified_db_file = unified_db_file
        self.integration_stats = {
            'total_dental_facilities': 0,
            'new_facilities_added': 0,
            'integration_timestamp': datetime.now().isoformat()
        }
        
    def load_dental_data(self) -> List[Dict[str, Any]]:
        """Load NABH dental facilities data."""
        try:
            with open(self.dental_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle different data formats
                if isinstance(data, list):
                    facilities = data
                elif isinstance(data, dict):
                    facilities = data.get('dental_facilities', data.get('facilities', []))
                else:
                    facilities = []
                
                self.integration_stats['total_dental_facilities'] = len(facilities)
                logger.info(f"Loaded {len(facilities)} dental facilities from {self.dental_data_file}")
                return facilities
        except Exception as e:
            logger.error(f"Error loading dental data: {e}")
            return []
    
    def load_unified_database(self) -> Dict[str, Any]:
        """Load the unified healthcare organizations database."""
        try:
            if os.path.exists(self.unified_db_file):
                with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                    logger.info(f"Loaded existing database with {len(db.get('organizations', []))} organizations")
                    return db
            else:
                logger.info("Creating new unified database")
                return {
                    "organizations": [],
                    "metadata": {
                        "total_count": 0,
                        "last_updated": datetime.now().isoformat(),
                        "data_sources": []
                    }
                }
        except Exception as e:
            logger.error(f"Error loading unified database: {e}")
            return {"organizations": [], "metadata": {"total_count": 0, "last_updated": datetime.now().isoformat(), "data_sources": []}}
    
    def convert_dental_facility_to_unified_format(self, facility: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dental facility data to unified format."""
        try:
            # Extract location information from name
            name = facility.get('name', '')
            location_parts = name.split(', ')
            
            city = "Unknown"
            state = "Unknown"
            
            if len(location_parts) >= 3:
                city = location_parts[-3].strip()
                state = location_parts[-2].strip()
            elif len(location_parts) >= 2:
                state = location_parts[-2].strip()
            
            unified_facility = {
                "name": facility.get('name', ''),
                "city": city,
                "state": state,
                "country": facility.get('country', 'India'),
                "hospital_type": "Dental Facility",
                "data_source": "NABH_Dental",
                "nabh_accredited": True,
                "nabh_accreditation_number": facility.get('accreditation_no', ''),
                "nabh_reference_number": facility.get('reference_no', ''),
                "nabh_valid_from": facility.get('valid_from', ''),
                "nabh_valid_upto": facility.get('valid_upto', ''),
                "nabh_status": facility.get('status', ''),
                "nabh_remarks": facility.get('remarks', ''),
                "nabh_facility_type": facility.get('facility_type', 'Dental'),
                "nabh_accreditation_type": facility.get('accreditation_type', 'NABH_Dental'),
                "extracted_date": facility.get('extracted_date', datetime.now().isoformat()),
                "integrated_date": datetime.now().isoformat(),
                
                # Quality metrics
                "quality_score": self._calculate_quality_score(facility),
                "data_completeness": self._calculate_data_completeness(facility),
                
                # Additional fields for compatibility
                "jci_accredited": False,
                "nabl_accredited": False,
                "cap_accredited": False,
                "iso_certified": False,
                "website": "",
                "phone": "",
                "email": "",
                "address": "",
                "specialties": ["Dental Care"],
                "services": ["Dental Services"],
                "bed_count": None,
                "established_year": None,
                "ownership_type": "Unknown"
            }
            
            return unified_facility
            
        except Exception as e:
            logger.error(f"Error converting dental facility to unified format: {e}")
            return None
    
    def _calculate_quality_score(self, facility: Dict[str, Any]) -> float:
        """Calculate quality score for dental facility."""
        score = 0.0
        max_score = 10.0
        
        # Name completeness (2 points)
        if facility.get('name', '').strip():
            score += 2.0
        
        # Accreditation number (2 points)
        if facility.get('accreditation_no', '').strip():
            score += 2.0
        
        # Reference number (1 point)
        if facility.get('reference_no', '').strip():
            score += 1.0
        
        # Valid dates (2 points)
        if facility.get('valid_from', '').strip() and facility.get('valid_upto', '').strip():
            score += 2.0
        
        # Status information (1 point)
        if facility.get('status', '').strip():
            score += 1.0
        
        # Country information (1 point)
        if facility.get('country', '').strip():
            score += 1.0
        
        # Remarks/additional info (1 point)
        if facility.get('remarks', '').strip():
            score += 1.0
        
        return round(score / max_score * 100, 2)
    
    def _calculate_data_completeness(self, facility: Dict[str, Any]) -> float:
        """Calculate data completeness percentage."""
        required_fields = ['name', 'accreditation_no', 'reference_no', 'valid_from', 'valid_upto', 'status', 'country']
        completed_fields = sum(1 for field in required_fields if facility.get(field, '').strip())
        return round((completed_fields / len(required_fields)) * 100, 2)
    
    def integrate_dental_facilities(self):
        """Main integration process."""
        logger.info("Starting dental facilities integration...")
        
        # Load data
        dental_facilities = self.load_dental_data()
        if not dental_facilities:
            logger.error("No dental facilities data to integrate")
            return False
        
        unified_db = self.load_unified_database()
        
        # Convert and add facilities
        new_facilities_added = 0
        
        for facility in dental_facilities:
            try:
                unified_facility = self.convert_dental_facility_to_unified_format(facility)
                if unified_facility:
                    unified_db['organizations'].append(unified_facility)
                    new_facilities_added += 1
                    
                    if new_facilities_added % 100 == 0:
                        logger.info(f"Processed {new_facilities_added} dental facilities...")
                        
            except Exception as e:
                logger.error(f"Error processing facility: {e}")
                continue
        
        # Update metadata
        unified_db['metadata']['total_count'] = len(unified_db['organizations'])
        unified_db['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Add dental facilities to data sources if not already present
        data_sources = unified_db['metadata'].get('data_sources', [])
        if 'NABH_Dental' not in data_sources:
            data_sources.append('NABH_Dental')
        unified_db['metadata']['data_sources'] = data_sources
        
        # Update integration stats
        self.integration_stats['new_facilities_added'] = new_facilities_added
        
        # Save updated database
        try:
            with open(self.unified_db_file, 'w', encoding='utf-8') as f:
                json.dump(unified_db, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved updated database with {len(unified_db['organizations'])} total organizations")
        except Exception as e:
            logger.error(f"Error saving updated database: {e}")
            return False
        
        # Save integration report
        self._save_integration_report()
        
        logger.info(f"Dental facilities integration completed successfully!")
        logger.info(f"Added {new_facilities_added} new dental facilities")
        logger.info(f"Total organizations in database: {len(unified_db['organizations'])}")
        
        return True
    
    def _save_integration_report(self):
        """Save integration report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"dental_integration_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.integration_stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Integration report saved to {report_file}")
        except Exception as e:
            logger.error(f"Error saving integration report: {e}")
    
    def print_summary(self):
        """Print integration summary."""
        print(f"\n=== Dental Facilities Integration Summary ===")
        print(f"Total dental facilities processed: {self.integration_stats['total_dental_facilities']}")
        print(f"New facilities added: {self.integration_stats['new_facilities_added']}")
        print(f"Integration timestamp: {self.integration_stats['integration_timestamp']}")
        print(f"Success rate: {(self.integration_stats['new_facilities_added'] / max(self.integration_stats['total_dental_facilities'], 1)) * 100:.1f}%")

if __name__ == "__main__":
    integrator = DentalFacilitiesIntegrator()
    
    if integrator.integrate_dental_facilities():
        integrator.print_summary()
    else:
        print("Dental facilities integration failed!")