"""
NABH Data Processor
Structures and cleans NABH data into standardized format for integration
"""

import json
import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Any

class NABHDataProcessor:
    def __init__(self, input_file='nabh_hospitals.json'):
        self.input_file = input_file
        self.processed_data = []
        
    def load_nabh_data(self) -> List[Dict]:
        """Load NABH data from JSON file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} NABH hospitals")
            return data
        except Exception as e:
            print(f"Error loading NABH data: {str(e)}")
            return []
    
    def clean_hospital_name(self, name: str) -> str:
        """Clean and standardize hospital name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove location suffixes (city, state, country)
        # Keep the main hospital name
        patterns_to_remove = [
            r',\s*[A-Za-z\s]+,\s*[A-Za-z\s]+,\s*India$',  # Remove city, state, India
            r',\s*[A-Za-z\s]+,\s*India$',  # Remove state, India
            r',\s*India$',  # Remove India
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name)
        
        return name.strip()
    
    def extract_location_info(self, original_name: str) -> Dict[str, str]:
        """Extract city, state, and country from hospital name"""
        location_info = {
            'city': '',
            'state': '',
            'country': 'India'
        }
        
        # Pattern to match: Name, City, State, Country
        match = re.search(r',\s*([^,]+),\s*([^,]+),\s*([^,]+)$', original_name)
        if match:
            location_info['city'] = match.group(1).strip()
            location_info['state'] = match.group(2).strip()
            location_info['country'] = match.group(3).strip()
        else:
            # Pattern to match: Name, State, Country
            match = re.search(r',\s*([^,]+),\s*([^,]+)$', original_name)
            if match:
                location_info['state'] = match.group(1).strip()
                location_info['country'] = match.group(2).strip()
        
        return location_info
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date format to ISO format"""
        if not date_str:
            return ""
        
        try:
            # Parse date in format "30 Oct 2021"
            date_obj = datetime.strptime(date_str, '%d %b %Y')
            return date_obj.isoformat()
        except:
            return date_str
    
    def determine_hospital_type(self, name: str) -> str:
        """Determine hospital type based on name"""
        name_lower = name.lower()
        
        if any(keyword in name_lower for keyword in ['heart', 'cardiac', 'cardio']):
            return 'Cardiac Specialty'
        elif any(keyword in name_lower for keyword in ['cancer', 'oncology', 'tumor']):
            return 'Cancer Specialty'
        elif any(keyword in name_lower for keyword in ['eye', 'ophthalmic', 'vision']):
            return 'Eye Specialty'
        elif any(keyword in name_lower for keyword in ['ortho', 'bone', 'joint']):
            return 'Orthopedic Specialty'
        elif any(keyword in name_lower for keyword in ['neuro', 'brain']):
            return 'Neurological Specialty'
        elif any(keyword in name_lower for keyword in ['maternity', 'women', 'gynec']):
            return 'Women & Child Specialty'
        elif any(keyword in name_lower for keyword in ['super specialty', 'multi specialty', 'multispecialty']):
            return 'Multi Specialty'
        elif any(keyword in name_lower for keyword in ['medical college', 'teaching', 'institute']):
            return 'Teaching Hospital'
        else:
            return 'General Hospital'
    
    def calculate_score_impact(self, status: str, remarks: str) -> float:
        """Calculate score impact based on NABH accreditation"""
        base_score = 15.0  # Base NABH score
        
        if status == 'Active':
            if '6th Edition' in remarks:
                return base_score + 5.0  # Latest edition bonus
            elif '5th Edition' in remarks:
                return base_score + 3.0  # Recent edition bonus
            else:
                return base_score
        elif status == 'Expired':
            return base_score * 0.3  # Reduced score for expired
        else:
            return base_score * 0.5  # Unknown status
    
    def process_nabh_data(self) -> List[Dict]:
        """Process NABH data into standardized format"""
        raw_data = self.load_nabh_data()
        
        if not raw_data:
            return []
        
        processed_hospitals = []
        
        for hospital in raw_data:
            try:
                # Extract location information
                location_info = self.extract_location_info(hospital.get('name', ''))
                
                # Create standardized hospital record
                processed_hospital = {
                    'name': self.clean_hospital_name(hospital.get('name', '')),
                    'original_name': hospital.get('name', ''),
                    'city': location_info['city'],
                    'state': location_info['state'],
                    'country': location_info['country'],
                    'hospital_type': self.determine_hospital_type(hospital.get('name', '')),
                    'certifications': [{
                        'name': 'National Accreditation Board for Hospitals & Healthcare Providers (NABH)',
                        'type': 'NABH Accreditation',
                        'status': hospital.get('status', 'Unknown'),
                        'accreditation_date': self.standardize_date(hospital.get('valid_from', '')),
                        'expiry_date': self.standardize_date(hospital.get('valid_upto', '')),
                        'accreditation_no': hospital.get('accreditation_no', ''),
                        'reference_no': hospital.get('reference_no', ''),
                        'remarks': hospital.get('remarks', ''),
                        'score_impact': self.calculate_score_impact(
                            hospital.get('status', 'Unknown'),
                            hospital.get('remarks', '')
                        ),
                        'source': 'NABH Portal'
                    }],
                    'data_source': 'NABH',
                    'last_updated': datetime.now().isoformat(),
                    'quality_indicators': {
                        'nabh_accredited': hospital.get('status') == 'Active',
                        'accreditation_level': self._extract_edition(hospital.get('remarks', '')),
                        'accreditation_valid': hospital.get('status') == 'Active'
                    }
                }
                
                processed_hospitals.append(processed_hospital)
                
            except Exception as e:
                print(f"Error processing hospital {hospital.get('name', 'Unknown')}: {str(e)}")
                continue
        
        self.processed_data = processed_hospitals
        print(f"Successfully processed {len(processed_hospitals)} hospitals")
        return processed_hospitals
    
    def _extract_edition(self, remarks: str) -> str:
        """Extract NABH edition from remarks"""
        if '6th Edition' in remarks:
            return '6th Edition'
        elif '5th Edition' in remarks:
            return '5th Edition'
        elif '4th Edition' in remarks:
            return '4th Edition'
        else:
            return 'Standard'
    
    def save_processed_data(self, filename='processed_nabh_hospitals.json'):
        """Save processed data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            print(f"Processed data saved to {filename}")
        except Exception as e:
            print(f"Error saving processed data: {str(e)}")
    
    def generate_summary_report(self):
        """Generate summary report of processed data"""
        if not self.processed_data:
            print("No processed data available")
            return
        
        total_hospitals = len(self.processed_data)
        active_hospitals = sum(1 for h in self.processed_data 
                              if h['quality_indicators']['nabh_accredited'])
        
        # State-wise breakdown
        state_counts = {}
        for hospital in self.processed_data:
            state = hospital.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Type breakdown
        type_counts = {}
        for hospital in self.processed_data:
            htype = hospital.get('hospital_type', 'Unknown')
            type_counts[htype] = type_counts.get(htype, 0) + 1
        
        # Edition breakdown
        edition_counts = {}
        for hospital in self.processed_data:
            edition = hospital['quality_indicators']['accreditation_level']
            edition_counts[edition] = edition_counts.get(edition, 0) + 1
        
        print(f"\n=== NABH Data Processing Summary ===")
        print(f"Total hospitals processed: {total_hospitals}")
        print(f"Active NABH accredited: {active_hospitals}")
        print(f"Expired/Inactive: {total_hospitals - active_hospitals}")
        
        print(f"\nTop 10 States by Hospital Count:")
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for state, count in sorted_states:
            print(f"  {state}: {count}")
        
        print(f"\nHospital Type Distribution:")
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        for htype, count in sorted_types:
            print(f"  {htype}: {count}")
        
        print(f"\nAccreditation Edition Distribution:")
        for edition, count in sorted(edition_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {edition}: {count}")

def main():
    """Main function to process NABH data"""
    processor = NABHDataProcessor()
    
    # Process the data
    processed_data = processor.process_nabh_data()
    
    if processed_data:
        # Save processed data
        processor.save_processed_data()
        
        # Generate summary report
        processor.generate_summary_report()
    else:
        print("No data to process")

if __name__ == "__main__":
    main()