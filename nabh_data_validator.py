#!/usr/bin/env python3
"""
NABH Entry Level Hospital Data Validator and Cleaner
Validates and cleans the extracted NABH entry-level hospital data
"""

import json
import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NABHDataValidator:
    def __init__(self, data_file: str):
        """Initialize the validator with the data file"""
        self.data_file = data_file
        self.hospitals = []
        self.validation_report = {
            'total_records': 0,
            'valid_records': 0,
            'invalid_records': 0,
            'issues_found': {},
            'data_quality_metrics': {},
            'cleaned_data_stats': {}
        }
        
    def load_data(self) -> bool:
        """Load the hospital data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.hospitals = json.load(f)
            
            self.validation_report['total_records'] = len(self.hospitals)
            logger.info(f"Loaded {len(self.hospitals)} hospital records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False
    
    def validate_hospital_name(self, hospital: Dict[str, Any]) -> List[str]:
        """Validate hospital name"""
        issues = []
        name = hospital.get('name', '').strip()
        
        if not name:
            issues.append("Missing hospital name")
        elif len(name) < 3:
            issues.append("Hospital name too short")
        elif len(name) > 200:
            issues.append("Hospital name too long")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'^[0-9]+$',  # Only numbers
            r'^[^a-zA-Z]*$',  # No letters
            r'^\s*$',  # Only whitespace
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, name):
                issues.append("Suspicious hospital name pattern")
                break
                
        return issues
    
    def validate_location(self, hospital: Dict[str, Any]) -> List[str]:
        """Validate location information"""
        issues = []
        
        city = hospital.get('city', '').strip()
        state = hospital.get('state', '').strip()
        country = hospital.get('country', '').strip()
        
        if not city:
            issues.append("Missing city")
        if not state:
            issues.append("Missing state")
        if not country:
            issues.append("Missing country")
        elif country.lower() != 'india':
            issues.append("Non-India country")
            
        return issues
    
    def validate_accreditation_info(self, hospital: Dict[str, Any]) -> List[str]:
        """Validate accreditation information"""
        issues = []
        
        acc_number = hospital.get('accreditation_number', '').strip()
        ref_number = hospital.get('reference_number', '').strip()
        
        if not acc_number:
            issues.append("Missing accreditation number")
        elif not re.match(r'^PEH-\d{4}-\d{4}$', acc_number):
            issues.append("Invalid accreditation number format")
            
        if not ref_number:
            issues.append("Missing reference number")
            
        return issues
    
    def validate_dates(self, hospital: Dict[str, Any]) -> List[str]:
        """Validate date information"""
        issues = []
        
        valid_from = hospital.get('valid_from_parsed')
        valid_upto = hospital.get('valid_upto_parsed')
        
        if not valid_from:
            issues.append("Missing valid from date")
        if not valid_upto:
            issues.append("Missing valid upto date")
            
        if valid_from and valid_upto:
            try:
                from_date = datetime.strptime(valid_from, '%Y-%m-%d')
                upto_date = datetime.strptime(valid_upto, '%Y-%m-%d')
                
                if from_date >= upto_date:
                    issues.append("Invalid date range (from >= upto)")
                    
                # Check for unrealistic date ranges
                date_diff = upto_date - from_date
                if date_diff.days < 30:
                    issues.append("Suspiciously short certification period")
                elif date_diff.days > 3650:  # 10 years
                    issues.append("Suspiciously long certification period")
                    
            except ValueError:
                issues.append("Invalid date format")
                
        return issues
    
    def validate_certification_status(self, hospital: Dict[str, Any]) -> List[str]:
        """Validate certification status"""
        issues = []
        
        status = hospital.get('certification_status', '').strip()
        valid_upto = hospital.get('valid_upto_parsed')
        
        if not status:
            issues.append("Missing certification status")
        elif status not in ['Active', 'Expired']:
            issues.append("Invalid certification status")
            
        # Verify status consistency with dates
        if status and valid_upto:
            try:
                upto_date = datetime.strptime(valid_upto, '%Y-%m-%d')
                current_date = datetime.now()
                
                if status == 'Active' and upto_date < current_date:
                    issues.append("Status shows Active but certification expired")
                elif status == 'Expired' and upto_date >= current_date:
                    issues.append("Status shows Expired but certification still valid")
                    
            except ValueError:
                pass  # Date validation will catch this
                
        return issues
    
    def clean_hospital_name(self, name: str) -> str:
        """Clean and standardize hospital name"""
        if not name:
            return name
            
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Fix common formatting issues
        name = re.sub(r'\s+', ' ', name)  # Multiple spaces to single
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)  # Add space between camelCase
        
        # Capitalize properly
        words = name.split()
        cleaned_words = []
        
        for word in words:
            # Don't change words that are already properly capitalized
            if word.isupper() or word.islower():
                cleaned_words.append(word.title())
            else:
                cleaned_words.append(word)
                
        return ' '.join(cleaned_words)
    
    def clean_location(self, location: str) -> str:
        """Clean and standardize location information"""
        if not location:
            return location
            
        # Remove extra whitespace and standardize
        location = ' '.join(location.split())
        
        # Fix common state name variations
        state_mappings = {
            'Chattisgarh': 'Chhattisgarh',
            'Orissa': 'Odisha',
            'Pondicherry': 'Puducherry',
            'Bangalore': 'Karnataka'  # Bangalore is a city, not a state
        }
        
        for old_name, new_name in state_mappings.items():
            if location == old_name:
                return new_name
                
        return location
    
    def update_certification_status(self, hospital: Dict[str, Any]) -> str:
        """Update certification status based on current date"""
        valid_upto = hospital.get('valid_upto_parsed')
        
        if not valid_upto:
            return hospital.get('certification_status', 'Unknown')
            
        try:
            upto_date = datetime.strptime(valid_upto, '%Y-%m-%d')
            current_date = datetime.now()
            
            if upto_date >= current_date:
                return 'Active'
            else:
                return 'Expired'
                
        except ValueError:
            return hospital.get('certification_status', 'Unknown')
    
    def validate_and_clean_data(self) -> Dict[str, Any]:
        """Validate and clean all hospital data"""
        logger.info("Starting data validation and cleaning...")
        
        valid_hospitals = []
        invalid_hospitals = []
        
        for i, hospital in enumerate(self.hospitals):
            issues = []
            
            # Validate different aspects
            issues.extend(self.validate_hospital_name(hospital))
            issues.extend(self.validate_location(hospital))
            issues.extend(self.validate_accreditation_info(hospital))
            issues.extend(self.validate_dates(hospital))
            issues.extend(self.validate_certification_status(hospital))
            
            # Clean the data
            cleaned_hospital = hospital.copy()
            
            # Clean hospital name
            if 'name' in cleaned_hospital:
                cleaned_hospital['name'] = self.clean_hospital_name(cleaned_hospital['name'])
            
            # Clean location data
            if 'city' in cleaned_hospital:
                cleaned_hospital['city'] = self.clean_location(cleaned_hospital['city'])
            if 'state' in cleaned_hospital:
                cleaned_hospital['state'] = self.clean_location(cleaned_hospital['state'])
            
            # Update certification status
            cleaned_hospital['certification_status'] = self.update_certification_status(cleaned_hospital)
            
            # Add validation info
            cleaned_hospital['validation_issues'] = issues
            cleaned_hospital['is_valid'] = len(issues) == 0
            cleaned_hospital['validation_date'] = datetime.now().isoformat()
            
            # Categorize hospital
            if len(issues) == 0:
                valid_hospitals.append(cleaned_hospital)
            else:
                invalid_hospitals.append(cleaned_hospital)
                
            # Track issues
            for issue in issues:
                if issue not in self.validation_report['issues_found']:
                    self.validation_report['issues_found'][issue] = 0
                self.validation_report['issues_found'][issue] += 1
                
            if (i + 1) % 500 == 0:
                logger.info(f"Processed {i + 1} hospitals...")
        
        # Update validation report
        self.validation_report['valid_records'] = len(valid_hospitals)
        self.validation_report['invalid_records'] = len(invalid_hospitals)
        
        # Calculate data quality metrics
        self.calculate_data_quality_metrics(valid_hospitals + invalid_hospitals)
        
        logger.info(f"Validation complete: {len(valid_hospitals)} valid, {len(invalid_hospitals)} invalid")
        
        return {
            'valid_hospitals': valid_hospitals,
            'invalid_hospitals': invalid_hospitals,
            'all_hospitals': valid_hospitals + invalid_hospitals
        }
    
    def calculate_data_quality_metrics(self, hospitals: List[Dict[str, Any]]):
        """Calculate data quality metrics"""
        if not hospitals:
            return
            
        total = len(hospitals)
        
        # Calculate completeness metrics
        metrics = {
            'completeness': {
                'hospital_name': sum(1 for h in hospitals if h.get('name', '').strip()) / total * 100,
                'city': sum(1 for h in hospitals if h.get('city', '').strip()) / total * 100,
                'state': sum(1 for h in hospitals if h.get('state', '').strip()) / total * 100,
                'accreditation_number': sum(1 for h in hospitals if h.get('accreditation_number', '').strip()) / total * 100,
                'valid_from': sum(1 for h in hospitals if h.get('valid_from_parsed')) / total * 100,
                'valid_upto': sum(1 for h in hospitals if h.get('valid_upto_parsed')) / total * 100,
            },
            'certification_status': {
                'active': sum(1 for h in hospitals if h.get('certification_status') == 'Active'),
                'expired': sum(1 for h in hospitals if h.get('certification_status') == 'Expired'),
                'unknown': sum(1 for h in hospitals if h.get('certification_status') not in ['Active', 'Expired'])
            },
            'geographic_distribution': {},
            'temporal_distribution': {}
        }
        
        # Geographic distribution
        state_counts = {}
        for hospital in hospitals:
            state = hospital.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        metrics['geographic_distribution'] = dict(sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Temporal distribution (by year)
        year_counts = {}
        for hospital in hospitals:
            valid_from = hospital.get('valid_from_parsed')
            if valid_from:
                try:
                    year = datetime.strptime(valid_from, '%Y-%m-%d').year
                    year_counts[year] = year_counts.get(year, 0) + 1
                except ValueError:
                    pass
        
        metrics['temporal_distribution'] = dict(sorted(year_counts.items()))
        
        self.validation_report['data_quality_metrics'] = metrics
    
    def save_results(self, results: Dict[str, Any], output_prefix: str = "nabh_entry_level_validated"):
        """Save validation results and cleaned data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save cleaned data (all hospitals)
        cleaned_file = f"{output_prefix}_{timestamp}.json"
        with open(cleaned_file, 'w', encoding='utf-8') as f:
            json.dump(results['all_hospitals'], f, indent=2, ensure_ascii=False)
        
        # Save valid hospitals only
        valid_file = f"{output_prefix}_valid_{timestamp}.json"
        with open(valid_file, 'w', encoding='utf-8') as f:
            json.dump(results['valid_hospitals'], f, indent=2, ensure_ascii=False)
        
        # Save CSV for valid hospitals
        if results['valid_hospitals']:
            csv_file = f"{output_prefix}_valid_{timestamp}.csv"
            df = pd.DataFrame(results['valid_hospitals'])
            df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Save validation report
        self.validation_report['validation_date'] = datetime.now().isoformat()
        self.validation_report['cleaned_data_stats'] = {
            'total_hospitals': len(results['all_hospitals']),
            'valid_hospitals': len(results['valid_hospitals']),
            'invalid_hospitals': len(results['invalid_hospitals']),
            'validation_success_rate': len(results['valid_hospitals']) / len(results['all_hospitals']) * 100 if results['all_hospitals'] else 0
        }
        
        report_file = f"nabh_validation_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved:")
        logger.info(f"  - Cleaned data: {cleaned_file}")
        logger.info(f"  - Valid hospitals: {valid_file}")
        if results['valid_hospitals']:
            logger.info(f"  - Valid hospitals CSV: {csv_file}")
        logger.info(f"  - Validation report: {report_file}")
        
        return {
            'cleaned_file': cleaned_file,
            'valid_file': valid_file,
            'csv_file': csv_file if results['valid_hospitals'] else None,
            'report_file': report_file
        }

def main():
    """Main function to run the validation"""
    # Find the most recent NABH entry level data file
    import glob
    import os
    
    data_files = glob.glob("nabh_entry_level_hospitals_*.json")
    if not data_files:
        logger.error("No NABH entry level hospital data files found")
        return
    
    # Use the most recent file
    latest_file = max(data_files, key=os.path.getctime)
    logger.info(f"Using data file: {latest_file}")
    
    # Initialize validator
    validator = NABHDataValidator(latest_file)
    
    # Load data
    if not validator.load_data():
        logger.error("Failed to load data")
        return
    
    # Validate and clean data
    results = validator.validate_and_clean_data()
    
    # Save results
    output_files = validator.save_results(results)
    
    # Print summary
    print("\n" + "="*60)
    print("NABH Entry Level Hospital Data Validation Complete!")
    print("="*60)
    print(f"Total hospitals processed: {validator.validation_report['total_records']}")
    print(f"Valid hospitals: {validator.validation_report['valid_records']}")
    print(f"Invalid hospitals: {validator.validation_report['invalid_records']}")
    print(f"Success rate: {validator.validation_report['cleaned_data_stats']['validation_success_rate']:.1f}%")
    
    print(f"\nTop validation issues:")
    for issue, count in sorted(validator.validation_report['issues_found'].items(), 
                              key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {issue}: {count}")
    
    print(f"\nData quality metrics:")
    completeness = validator.validation_report['data_quality_metrics']['completeness']
    for field, percentage in completeness.items():
        print(f"  - {field}: {percentage:.1f}% complete")
    
    print(f"\nCertification status:")
    cert_status = validator.validation_report['data_quality_metrics']['certification_status']
    for status, count in cert_status.items():
        print(f"  - {status.title()}: {count}")

if __name__ == "__main__":
    main()