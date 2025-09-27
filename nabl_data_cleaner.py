#!/usr/bin/env python3
"""
NABL Data Cleaner
Processes and validates extracted NABL data for database integration
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class NABLDataCleaner:
    def __init__(self, input_file: str = None):
        self.input_file = input_file or "nabl_pdf_extracted_data_20250926_175604.json"
        self.project_root = Path.cwd()
        self.cleaned_data = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Validation patterns
        self.validation_patterns = {
            'valid_org_name': r'^[A-Za-z][A-Za-z\s&.,()-]{3,}(?:Ltd|Limited|Pvt|Private|Hospital|Clinic|Laboratory|Labs?|Centre|Center|Institute|Corporation|Company|Medical|Healthcare|Diagnostics|Pathology)?\.?$',
            'invalid_patterns': [
                r'^(No\.|S\.No|Serial|Page|Document|NABL|National|Accreditation|Board|Testing|Calibration|Laboratories?|Issue|Expiry|Person|Number|Date|Certificate|Validity|Scope|Address|Contact|Phone|Email|Website|www\.|http|https).*',
                r'^\d+$',  # Only numbers
                r'^[^A-Za-z]*$',  # No letters
                r'^.{1,3}$',  # Too short
                r'.*\d{10,}.*',  # Contains long numbers (likely phone/ID)
                r'.*@.*\.(com|org|in|net).*',  # Email addresses
                r'.*www\..*',  # Websites
            ],
            'location_indicators': [
                'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad',
                'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam',
                'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut',
                'Rajkot', 'Varanasi', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Allahabad', 'Ranchi',
                'Coimbatore', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur', 'Madurai', 'Raipur',
                'Kota', 'Guwahati', 'Chandigarh', 'Solapur', 'Hubli', 'Tiruchirappalli', 'Bareilly',
                'Mysore', 'Tiruppur', 'Gurgaon', 'Aligarh', 'Jalandhar', 'Bhubaneswar', 'Salem',
                'Warangal', 'Guntur', 'Bhiwandi', 'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati',
                'Noida', 'Jamshedpur', 'Bhilai', 'Cuttack', 'Firozabad', 'Kochi', 'Nellore',
                'Bhavnagar', 'Dehradun', 'Durgapur', 'Asansol', 'Rourkela', 'Nanded', 'Kolhapur',
                'Ajmer', 'Akola', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Siliguri', 'Jhansi',
                'Jammu', 'Mangalore', 'Erode', 'Belgaum', 'Tirunelveli', 'Malegaon', 'Gaya',
                'Jalgaon', 'Udaipur'
            ],
            'healthcare_keywords': [
                'Hospital', 'Clinic', 'Laboratory', 'Labs', 'Medical', 'Healthcare', 'Diagnostics',
                'Pathology', 'Radiology', 'Centre', 'Center', 'Institute', 'Nursing', 'Pharmacy',
                'Surgical', 'Dental', 'Eye', 'Heart', 'Cancer', 'Oncology', 'Cardiology',
                'Neurology', 'Orthopedic', 'Pediatric', 'Maternity', 'Fertility', 'IVF',
                'Blood Bank', 'Transfusion', 'Dialysis', 'Rehabilitation', 'Physiotherapy'
            ]
        }
    
    def load_extracted_data(self) -> List[Dict[str, Any]]:
        """Load extracted NABL data from JSON file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data)} extracted organizations")
            return data
        except Exception as e:
            self.logger.error(f"Error loading extracted data: {e}")
            return []
    
    def is_valid_organization_name(self, name: str) -> bool:
        """Check if organization name is valid"""
        if not name or len(name.strip()) < 4:
            return False
        
        name = name.strip()
        
        # Check against invalid patterns
        for pattern in self.validation_patterns['invalid_patterns']:
            if re.match(pattern, name, re.IGNORECASE):
                return False
        
        # Must contain at least some letters
        if not re.search(r'[A-Za-z]{3,}', name):
            return False
        
        # Check for healthcare relevance (bonus points but not required)
        has_healthcare_keyword = any(keyword.lower() in name.lower() 
                                   for keyword in self.validation_patterns['healthcare_keywords'])
        
        # Check for location in name (might indicate address line)
        has_location = any(location.lower() in name.lower() 
                          for location in self.validation_patterns['location_indicators'])
        
        # If it's just a location or address, it's probably not an org name
        if has_location and not has_healthcare_keyword and len(name.split()) < 3:
            return False
        
        return True
    
    def clean_organization_name(self, name: str) -> str:
        """Clean and standardize organization name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove leading/trailing punctuation
        name = name.strip('.,;:-_()[]{}|')
        
        # Fix common OCR errors
        replacements = {
            'Laboratoryoratories': 'Laboratories',
            'Hospitall': 'Hospital',
            'Clinicc': 'Clinic',
            'Medicall': 'Medical',
            'Centrre': 'Centre',
            'Institutee': 'Institute'
        }
        
        for error, correction in replacements.items():
            name = name.replace(error, correction)
        
        # Standardize common abbreviations
        standardizations = {
            r'\bPvt\.?\s*Ltd\.?': 'Private Limited',
            r'\bLtd\.?': 'Limited',
            r'\bHosp\.?': 'Hospital',
            r'\bLab\.?': 'Laboratory',
            r'\bMed\.?': 'Medical',
            r'\bClin\.?': 'Clinic',
            r'\bDiag\.?': 'Diagnostics',
            r'\bPath\.?': 'Pathology'
        }
        
        for pattern, replacement in standardizations.items():
            name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        
        # Capitalize properly
        name = ' '.join(word.capitalize() if word.lower() not in ['and', 'of', 'the', 'for', 'in', 'at', 'by', 'with'] 
                       else word.lower() for word in name.split())
        
        return name.strip()
    
    def extract_location_from_name(self, name: str) -> List[str]:
        """Extract location information from organization name"""
        locations = []
        
        for location in self.validation_patterns['location_indicators']:
            if location.lower() in name.lower():
                locations.append(location)
        
        return list(set(locations))  # Remove duplicates
    
    def determine_organization_type(self, name: str, services: List[str]) -> str:
        """Determine the type of healthcare organization"""
        name_lower = name.lower()
        
        # Hospital
        if any(keyword in name_lower for keyword in ['hospital', 'medical college', 'nursing home']):
            return 'Hospital'
        
        # Laboratory
        if any(keyword in name_lower for keyword in ['laboratory', 'labs', 'diagnostics', 'pathology']):
            return 'Laboratory'
        
        # Clinic
        if any(keyword in name_lower for keyword in ['clinic', 'centre', 'center']):
            return 'Clinic'
        
        # Institute
        if any(keyword in name_lower for keyword in ['institute', 'academy', 'college']):
            return 'Institute'
        
        # Default based on services
        if services and any('laboratory' in service.lower() for service in services):
            return 'Laboratory'
        
        return 'Healthcare Organization'
    
    def enhance_organization_data(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance organization data with additional information"""
        enhanced_org = org.copy()
        
        # Clean organization name
        enhanced_org['organization_name'] = self.clean_organization_name(org['organization_name'])
        
        # Extract locations from name if not present
        if not enhanced_org['locations']:
            enhanced_org['locations'] = self.extract_location_from_name(enhanced_org['organization_name'])
        
        # Determine organization type
        enhanced_org['organization_type'] = self.determine_organization_type(
            enhanced_org['organization_name'], 
            enhanced_org.get('services', [])
        )
        
        # Standardize services
        if enhanced_org.get('services'):
            enhanced_org['services'] = list(set(enhanced_org['services']))  # Remove duplicates
        
        # Add quality indicators
        enhanced_org['data_quality'] = {
            'has_location': bool(enhanced_org['locations']),
            'has_accreditation_number': bool(enhanced_org.get('accreditation_number')),
            'has_scope': bool(enhanced_org.get('scope')),
            'name_length': len(enhanced_org['organization_name']),
            'confidence_score': self.calculate_confidence_score(enhanced_org)
        }
        
        return enhanced_org
    
    def calculate_confidence_score(self, org: Dict[str, Any]) -> float:
        """Calculate confidence score for organization data"""
        score = 0.0
        
        # Base score for valid name
        if self.is_valid_organization_name(org['organization_name']):
            score += 40.0
        
        # Healthcare keywords bonus
        name_lower = org['organization_name'].lower()
        healthcare_matches = sum(1 for keyword in self.validation_patterns['healthcare_keywords'] 
                               if keyword.lower() in name_lower)
        score += min(healthcare_matches * 10, 30)  # Max 30 points
        
        # Location information
        if org.get('locations'):
            score += 15.0
        
        # Accreditation details
        if org.get('accreditation_number'):
            score += 10.0
        
        # Scope information
        if org.get('scope'):
            score += 5.0
        
        return min(score, 100.0)  # Cap at 100
    
    def clean_and_validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate the extracted data"""
        cleaned_organizations = []
        stats = {
            'total_input': len(data),
            'valid_organizations': 0,
            'invalid_names': 0,
            'duplicates_removed': 0,
            'enhanced_with_locations': 0,
            'high_confidence': 0
        }
        
        seen_names = set()
        
        for org in data:
            # Validate organization name
            if not self.is_valid_organization_name(org.get('organization_name', '')):
                stats['invalid_names'] += 1
                continue
            
            # Enhance organization data
            enhanced_org = self.enhance_organization_data(org)
            
            # Check for duplicates
            org_name_key = enhanced_org['organization_name'].lower().strip()
            if org_name_key in seen_names:
                stats['duplicates_removed'] += 1
                continue
            
            seen_names.add(org_name_key)
            
            # Quality checks
            if enhanced_org['data_quality']['has_location']:
                stats['enhanced_with_locations'] += 1
            
            if enhanced_org['data_quality']['confidence_score'] >= 70:
                stats['high_confidence'] += 1
            
            cleaned_organizations.append(enhanced_org)
            stats['valid_organizations'] += 1
        
        self.logger.info(f"Data cleaning completed: {stats}")
        return cleaned_organizations, stats
    
    def save_cleaned_data(self, cleaned_data: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """Save cleaned data to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nabl_cleaned_data_{timestamp}.json"
        filepath = self.project_root / filename
        
        # Prepare output data
        output_data = {
            'metadata': {
                'cleaning_timestamp': datetime.now().isoformat(),
                'source_file': self.input_file,
                'cleaning_statistics': stats,
                'total_organizations': len(cleaned_data)
            },
            'organizations': cleaned_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Cleaned data saved to: {filepath}")
        return str(filepath)
    
    def generate_cleaning_report(self, stats: Dict[str, Any], cleaned_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive cleaning report"""
        # Analyze organization types
        org_types = {}
        locations = {}
        confidence_distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for org in cleaned_data:
            # Organization types
            org_type = org.get('organization_type', 'Unknown')
            org_types[org_type] = org_types.get(org_type, 0) + 1
            
            # Locations
            for location in org.get('locations', []):
                locations[location] = locations.get(location, 0) + 1
            
            # Confidence distribution
            confidence = org['data_quality']['confidence_score']
            if confidence >= 80:
                confidence_distribution['high'] += 1
            elif confidence >= 60:
                confidence_distribution['medium'] += 1
            else:
                confidence_distribution['low'] += 1
        
        report = {
            'cleaning_summary': stats,
            'data_analysis': {
                'organization_types': dict(sorted(org_types.items(), key=lambda x: x[1], reverse=True)),
                'top_locations': dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:20]),
                'confidence_distribution': confidence_distribution,
                'quality_metrics': {
                    'avg_confidence_score': sum(org['data_quality']['confidence_score'] for org in cleaned_data) / len(cleaned_data) if cleaned_data else 0,
                    'organizations_with_locations': sum(1 for org in cleaned_data if org['locations']),
                    'organizations_with_accreditation_numbers': sum(1 for org in cleaned_data if org.get('accreditation_number')),
                    'avg_name_length': sum(len(org['organization_name']) for org in cleaned_data) / len(cleaned_data) if cleaned_data else 0
                }
            },
            'sample_high_quality_organizations': [
                org for org in cleaned_data 
                if org['data_quality']['confidence_score'] >= 80
            ][:10]
        }
        
        # Save report
        report_file = self.project_root / f"nabl_cleaning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Cleaning report saved to: {report_file}")
        return report
    
    def process_data(self) -> tuple:
        """Main method to process and clean NABL data"""
        self.logger.info("Starting NABL data cleaning process")
        
        # Load extracted data
        raw_data = self.load_extracted_data()
        if not raw_data:
            self.logger.error("No data to process")
            return [], {}
        
        # Clean and validate data
        cleaned_data, stats = self.clean_and_validate_data(raw_data)
        
        # Save cleaned data
        output_file = self.save_cleaned_data(cleaned_data, stats)
        
        # Generate report
        report = self.generate_cleaning_report(stats, cleaned_data)
        
        self.cleaned_data = cleaned_data
        return cleaned_data, report

def main():
    import sys
    
    # Get input file from command line or use default
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    cleaner = NABLDataCleaner(input_file)
    
    print("🧹 NABL Data Cleaning Started")
    print("=" * 50)
    
    # Process the data
    cleaned_data, report = cleaner.process_data()
    
    if cleaned_data:
        print(f"✅ Data cleaning completed successfully!")
        print(f"\n📊 Cleaning Summary:")
        print(f"   • Input Organizations: {report['cleaning_summary']['total_input']}")
        print(f"   • Valid Organizations: {report['cleaning_summary']['valid_organizations']}")
        print(f"   • Invalid Names Removed: {report['cleaning_summary']['invalid_names']}")
        print(f"   • Duplicates Removed: {report['cleaning_summary']['duplicates_removed']}")
        print(f"   • High Confidence Organizations: {report['cleaning_summary']['high_confidence']}")
        
        print(f"\n🏥 Organization Types:")
        for org_type, count in list(report['data_analysis']['organization_types'].items())[:5]:
            print(f"   • {org_type}: {count}")
        
        print(f"\n📍 Top Locations:")
        for location, count in list(report['data_analysis']['top_locations'].items())[:5]:
            print(f"   • {location}: {count}")
        
        print(f"\n🎯 Quality Metrics:")
        quality = report['data_analysis']['quality_metrics']
        print(f"   • Average Confidence Score: {quality['avg_confidence_score']:.1f}%")
        print(f"   • Organizations with Locations: {quality['organizations_with_locations']}")
        print(f"   • Organizations with Accreditation Numbers: {quality['organizations_with_accreditation_numbers']}")
        
    else:
        print("❌ No valid organizations found after cleaning")
    
    print("\n" + "=" * 50)
    print("🎉 NABL Data Cleaning Complete!")

if __name__ == "__main__":
    main()