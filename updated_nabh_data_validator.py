import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatedNABHDataValidator:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.hospitals = []
        self.validated_hospitals = []
        self.validation_stats = {
            'total_input': 0,
            'valid_hospitals': 0,
            'invalid_hospitals': 0,
            'duplicates_removed': 0,
            'data_quality_issues': 0,
            'status_corrections': 0
        }

    def load_data(self) -> bool:
        """Load hospital data from JSON file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.hospitals = json.load(f)
            
            self.validation_stats['total_input'] = len(self.hospitals)
            logger.info(f"Loaded {len(self.hospitals)} hospitals from {self.input_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def validate_hospital(self, hospital: Dict) -> Optional[Dict]:
        """Validate and clean individual hospital data"""
        try:
            # Create a copy for validation
            validated = hospital.copy()
            
            # 1. Validate required fields
            if not validated.get('name') or len(validated['name'].strip()) < 3:
                logger.debug(f"Invalid hospital name: {validated.get('name', 'None')}")
                return None
            
            # 2. Clean and standardize name
            validated['name'] = self.clean_hospital_name(validated['name'])
            
            # 3. Validate and clean reference number
            if not validated.get('reference_number'):
                logger.debug(f"Missing reference number for: {validated['name']}")
                return None
            
            validated['reference_number'] = validated['reference_number'].strip()
            
            # 4. Parse and validate dates from the data structure
            validated = self.parse_application_dates(validated)
            
            # 5. Determine proper certification status
            validated['certification_status'] = self.determine_proper_status(validated)
            
            # 6. Validate and clean location data
            validated = self.validate_location_data(validated)
            
            # 7. Add validation metadata
            validated['validation_date'] = datetime.now().isoformat()
            validated['validation_version'] = '2.0'
            validated['data_source'] = 'Updated NABH Entry Level Portal'
            
            # 8. Calculate quality score
            validated['data_quality_score'] = self.calculate_quality_score(validated)
            
            return validated
            
        except Exception as e:
            logger.debug(f"Error validating hospital {hospital.get('name', 'Unknown')}: {e}")
            return None

    def clean_hospital_name(self, name: str) -> str:
        """Clean and standardize hospital name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove trailing commas and periods
        name = name.rstrip('.,')
        
        # Standardize common abbreviations
        replacements = {
            ' Pvt Ltd': ' Private Limited',
            ' Pvt. Ltd.': ' Private Limited',
            ' Ltd.': ' Limited',
            ' Hosp.': ' Hospital',
            ' Med.': ' Medical',
            ' Ctr.': ' Centre',
            ' Ctr': ' Centre'
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        return name

    def parse_application_dates(self, hospital: Dict) -> Dict:
        """Parse application dates from the scraped data"""
        # The scraped data has dates in 'accreditation_number' field and status in 'valid_from'
        date_field = hospital.get('accreditation_number', '')
        status_field = hospital.get('valid_from', '')
        
        # Parse application date
        if date_field and date_field not in ['', 'N/A', 'Unknown']:
            parsed_date = self.parse_date_string(date_field)
            if parsed_date:
                hospital['application_date'] = parsed_date
                hospital['application_date_original'] = date_field
        
        # Parse application status
        if status_field:
            hospital['application_status'] = status_field.strip()
        
        return hospital

    def parse_date_string(self, date_str: str) -> Optional[str]:
        """Parse various date formats"""
        if not date_str or date_str.lower() in ['na', 'n/a', '', 'unknown']:
            return None
        
        # Common date formats
        date_formats = [
            '%d %b %Y',      # 08 Dec 2014
            '%d %B %Y',      # 08 December 2014
            '%d/%m/%Y',      # 08/12/2014
            '%d-%m-%Y',      # 08-12-2014
            '%Y-%m-%d',      # 2014-12-08
            '%d.%m.%Y',      # 08.12.2014
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logger.debug(f"Could not parse date: {date_str}")
        return None

    def determine_proper_status(self, hospital: Dict) -> str:
        """Determine proper certification status based on available data"""
        application_status = hospital.get('application_status', '').lower()
        
        # Map application status to certification status
        if 'closed' in application_status:
            return 'Application Closed'
        elif 'pending' in application_status:
            return 'Application Pending'
        elif 'approved' in application_status:
            return 'Approved'
        elif 'rejected' in application_status:
            return 'Rejected'
        elif 'withdrawn' in application_status:
            return 'Withdrawn'
        else:
            return 'Under Review'

    def validate_location_data(self, hospital: Dict) -> Dict:
        """Validate and enhance location data"""
        # Clean city and state
        if hospital.get('city'):
            hospital['city'] = self.clean_location_name(hospital['city'])
        
        if hospital.get('state'):
            hospital['state'] = self.clean_location_name(hospital['state'])
        
        # Validate state names against known Indian states
        hospital['state'] = self.validate_indian_state(hospital.get('state', ''))
        
        # Set country to India
        hospital['country'] = 'India'
        
        return hospital

    def clean_location_name(self, location: str) -> str:
        """Clean location names"""
        if not location or location.lower() in ['unknown', 'na', 'n/a', '']:
            return 'Unknown'
        
        # Remove extra whitespace and standardize
        location = re.sub(r'\s+', ' ', location.strip())
        
        # Capitalize properly
        location = location.title()
        
        # Fix common state name variations
        state_corrections = {
            'Tamilnadu': 'Tamil Nadu',
            'Tamilnadu': 'Tamil Nadu',
            'Andhra Pradesh': 'Andhra Pradesh',
            'Madhya Pradesh': 'Madhya Pradesh',
            'Uttar Pradesh': 'Uttar Pradesh',
            'West Bengal': 'West Bengal',
            'Himachal Pradesh': 'Himachal Pradesh',
            'Arunachal Pradesh': 'Arunachal Pradesh',
            'Jammu And Kashmir': 'Jammu and Kashmir',
            'Chattisgarh': 'Chhattisgarh',
            'Orissa': 'Odisha'
        }
        
        return state_corrections.get(location, location)

    def validate_indian_state(self, state: str) -> str:
        """Validate against known Indian states"""
        if not state or state == 'Unknown':
            return 'Unknown'
        
        # List of Indian states and UTs
        indian_states = {
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
            'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
            'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
        }
        
        # Check if state is in the list (case insensitive)
        for valid_state in indian_states:
            if state.lower() == valid_state.lower():
                return valid_state
        
        # Return as-is if not found (might be a valid variation)
        return state

    def calculate_quality_score(self, hospital: Dict) -> int:
        """Calculate data quality score (0-100)"""
        score = 0
        
        # Name quality (20 points)
        if hospital.get('name') and len(hospital['name']) > 10:
            score += 20
        elif hospital.get('name'):
            score += 10
        
        # Reference number (15 points)
        if hospital.get('reference_number'):
            score += 15
        
        # Location data (25 points)
        if hospital.get('state') and hospital['state'] != 'Unknown':
            score += 15
        if hospital.get('city') and hospital['city'] != 'Unknown':
            score += 10
        
        # Application data (20 points)
        if hospital.get('application_date'):
            score += 10
        if hospital.get('application_status'):
            score += 10
        
        # Additional data (20 points)
        if hospital.get('address'):
            score += 5
        if hospital.get('certification_status') != 'Unknown':
            score += 10
        if hospital.get('accreditation_level'):
            score += 5
        
        return min(score, 100)

    def remove_duplicates(self, hospitals: List[Dict]) -> List[Dict]:
        """Remove duplicate hospitals based on name and reference number"""
        seen = set()
        unique_hospitals = []
        
        for hospital in hospitals:
            # Create identifier
            identifier = (
                hospital.get('name', '').lower().strip(),
                hospital.get('reference_number', '').strip()
            )
            
            if identifier not in seen:
                seen.add(identifier)
                unique_hospitals.append(hospital)
            else:
                self.validation_stats['duplicates_removed'] += 1
        
        return unique_hospitals

    def validate_all_hospitals(self) -> List[Dict]:
        """Validate all hospitals"""
        logger.info("Starting validation of all hospitals...")
        
        validated = []
        
        for i, hospital in enumerate(self.hospitals):
            validated_hospital = self.validate_hospital(hospital)
            
            if validated_hospital:
                validated.append(validated_hospital)
                self.validation_stats['valid_hospitals'] += 1
            else:
                self.validation_stats['invalid_hospitals'] += 1
            
            # Progress logging
            if (i + 1) % 100 == 0:
                logger.info(f"Validated {i + 1}/{len(self.hospitals)} hospitals...")
        
        # Remove duplicates
        validated = self.remove_duplicates(validated)
        
        self.validated_hospitals = validated
        logger.info(f"Validation completed: {len(validated)} valid hospitals")
        
        return validated

    def save_validated_data(self):
        """Save validated data to files"""
        if not self.validated_hospitals:
            logger.warning("No validated hospitals to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save validated JSON
        json_filename = f"updated_nabh_entry_level_validated_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.validated_hospitals, f, indent=2, ensure_ascii=False)
        
        # Generate validation report
        self.generate_validation_report(timestamp)
        
        logger.info(f"Saved {len(self.validated_hospitals)} validated hospitals to {json_filename}")

    def generate_validation_report(self, timestamp: str):
        """Generate comprehensive validation report"""
        report = {
            'validation_date': datetime.now().isoformat(),
            'input_file': self.input_file,
            'validation_version': '2.0',
            'statistics': self.validation_stats,
            'data_distribution': {
                'by_state': {},
                'by_certification_status': {},
                'by_quality_score': {
                    'excellent': 0,  # 90-100
                    'good': 0,       # 70-89
                    'fair': 0,       # 50-69
                    'poor': 0        # <50
                }
            },
            'quality_metrics': {
                'avg_quality_score': 0,
                'hospitals_with_dates': 0,
                'hospitals_with_location': 0,
                'hospitals_with_complete_data': 0
            }
        }
        
        # Calculate distributions
        total_quality_score = 0
        
        for hospital in self.validated_hospitals:
            # State distribution
            state = hospital.get('state', 'Unknown')
            report['data_distribution']['by_state'][state] = \
                report['data_distribution']['by_state'].get(state, 0) + 1
            
            # Status distribution
            status = hospital.get('certification_status', 'Unknown')
            report['data_distribution']['by_certification_status'][status] = \
                report['data_distribution']['by_certification_status'].get(status, 0) + 1
            
            # Quality score distribution
            quality_score = hospital.get('data_quality_score', 0)
            total_quality_score += quality_score
            
            if quality_score >= 90:
                report['data_distribution']['by_quality_score']['excellent'] += 1
            elif quality_score >= 70:
                report['data_distribution']['by_quality_score']['good'] += 1
            elif quality_score >= 50:
                report['data_distribution']['by_quality_score']['fair'] += 1
            else:
                report['data_distribution']['by_quality_score']['poor'] += 1
            
            # Quality metrics
            if hospital.get('application_date'):
                report['quality_metrics']['hospitals_with_dates'] += 1
            
            if hospital.get('state') != 'Unknown':
                report['quality_metrics']['hospitals_with_location'] += 1
            
            if (hospital.get('application_date') and 
                hospital.get('state') != 'Unknown' and 
                hospital.get('reference_number')):
                report['quality_metrics']['hospitals_with_complete_data'] += 1
        
        # Calculate average quality score
        if self.validated_hospitals:
            report['quality_metrics']['avg_quality_score'] = \
                total_quality_score / len(self.validated_hospitals)
        
        # Save report
        report_filename = f"updated_nabh_validation_report_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated validation report: {report_filename}")
        return report

    def run_validation(self):
        """Run the complete validation process"""
        logger.info("Starting updated NABH data validation process...")
        
        try:
            # Load data
            if not self.load_data():
                logger.error("Failed to load data")
                return
            
            # Validate all hospitals
            validated = self.validate_all_hospitals()
            
            if not validated:
                logger.error("No hospitals passed validation")
                return
            
            # Save validated data
            self.save_validated_data()
            
            # Print summary
            print(f"\nUpdated NABH Data Validation Completed!")
            print(f"Input hospitals: {self.validation_stats['total_input']}")
            print(f"Valid hospitals: {self.validation_stats['valid_hospitals']}")
            print(f"Invalid hospitals: {self.validation_stats['invalid_hospitals']}")
            print(f"Duplicates removed: {self.validation_stats['duplicates_removed']}")
            
            # Quality distribution
            quality_dist = {}
            for hospital in validated:
                score = hospital.get('data_quality_score', 0)
                if score >= 90:
                    quality_dist['Excellent (90-100)'] = quality_dist.get('Excellent (90-100)', 0) + 1
                elif score >= 70:
                    quality_dist['Good (70-89)'] = quality_dist.get('Good (70-89)', 0) + 1
                elif score >= 50:
                    quality_dist['Fair (50-69)'] = quality_dist.get('Fair (50-69)', 0) + 1
                else:
                    quality_dist['Poor (<50)'] = quality_dist.get('Poor (<50)', 0) + 1
            
            print(f"\nData Quality Distribution:")
            for quality, count in quality_dist.items():
                print(f"{quality}: {count}")
            
            # Top states
            state_counts = {}
            for hospital in validated:
                state = hospital.get('state', 'Unknown')
                state_counts[state] = state_counts.get(state, 0) + 1
            
            print(f"\nTop 10 States:")
            for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{state}: {count}")
            
        except Exception as e:
            logger.error(f"Validation process failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python updated_nabh_data_validator.py <input_json_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    validator = UpdatedNABHDataValidator(input_file)
    validator.run_validation()