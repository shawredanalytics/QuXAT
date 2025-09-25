"""
CAP Laboratory Database Integrator
Integrates CAP 15189 accredited laboratory data with the existing unified healthcare organization database
"""

import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import re
import os

class CAPDatabaseIntegrator:
    def __init__(self):
        self.cap_file = 'cap_laboratories_final.json'
        self.unified_file = 'unified_healthcare_organizations.json'
        self.output_file = 'unified_healthcare_organizations_with_cap.json'
        self.backup_file = 'unified_healthcare_organizations_backup.json'
        
    def load_cap_data(self) -> List[Dict]:
        """Load CAP laboratory data"""
        try:
            with open(self.cap_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} CAP laboratories")
            return data
        except Exception as e:
            print(f"❌ Error loading CAP data: {str(e)}")
            return []
    
    def load_unified_data(self) -> List[Dict]:
        """Load existing unified healthcare database"""
        try:
            if os.path.exists(self.unified_file):
                with open(self.unified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded {len(data)} existing healthcare organizations")
                return data
            else:
                print("ℹ️ No existing unified database found, creating new one")
                return []
        except Exception as e:
            print(f"❌ Error loading unified data: {str(e)}")
            return []
    
    def backup_existing_data(self, data: List[Dict]):
        """Create backup of existing unified data"""
        try:
            if data:
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✅ Created backup at {self.backup_file}")
        except Exception as e:
            print(f"❌ Error creating backup: {str(e)}")
    
    def standardize_cap_data(self, cap_data: List[Dict]) -> List[Dict]:
        """Standardize CAP laboratory data to unified format"""
        standardized = []
        
        for lab in cap_data:
            try:
                # Extract location information
                location = lab.get('location', {})
                country = location.get('country', 'United States')
                state = location.get('state', '')
                zip_code = location.get('zip_code', '')
                
                # Determine city from address
                city = self._extract_city_from_address(lab.get('address', ''), state)
                
                standardized_org = {
                    'id': lab.get('id', ''),
                    'name': lab.get('name', ''),
                    'original_name': lab.get('name', ''),
                    'city': city,
                    'state': state,
                    'country': country,
                    'zip_code': zip_code,
                    'address': lab.get('address', ''),
                    'phone': lab.get('phone', ''),
                    'website': lab.get('website', ''),
                    'organization_type': 'Medical Laboratory',
                    'hospital_type': 'Medical Laboratory',
                    'specialties': lab.get('specialties', ['Medical Laboratory Testing']),
                    'certifications': self._convert_cap_certifications(lab.get('certifications', [])),
                    'quality_initiatives': lab.get('quality_initiatives', []),
                    'data_source': 'CAP 15189',
                    'last_updated': datetime.now().isoformat(),
                    'quality_indicators': {
                        'cap_accredited': True,
                        'iso_15189_accredited': True,
                        'jci_accredited': False,
                        'nabh_accredited': False,
                        'international_accreditation': True,
                        'accreditation_valid': True,
                        'laboratory_accreditation': True
                    },
                    'quality_score': lab.get('quality_score', 90.0),
                    'compliance_level': lab.get('compliance_level', 'High'),
                    'accreditation_level': lab.get('accreditation_level', 'International'),
                    'region': self._determine_region(country),
                    'search_keywords': self._generate_search_keywords(lab.get('name', ''), country),
                    'scraped_date': lab.get('scraped_date', ''),
                    'cap_specific_data': {
                        'accreditation_type': lab.get('accreditation_type', 'CAP 15189'),
                        'accreditation_body': lab.get('accreditation_body', 'College of American Pathologists'),
                        'status': lab.get('status', 'Active')
                    }
                }
                
                standardized.append(standardized_org)
                
            except Exception as e:
                print(f"❌ Error standardizing CAP lab {lab.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return standardized
    
    def _extract_city_from_address(self, address: str, state: str) -> str:
        """Extract city name from address"""
        if not address:
            return ''
        
        # Common patterns for US addresses
        if state:
            # Look for pattern: City, State ZIP
            pattern = rf'([^,]+),\s*{re.escape(state)}\s*\d{{5}}'
            match = re.search(pattern, address)
            if match:
                return match.group(1).strip()
        
        # Try to extract city from comma-separated parts
        parts = [part.strip() for part in address.split(',')]
        if len(parts) >= 2:
            # Usually city is the second-to-last or third-to-last part
            for i in range(-3, -1):
                if abs(i) <= len(parts):
                    potential_city = parts[i]
                    # Check if it's not a street address (contains numbers)
                    if not re.search(r'^\d+', potential_city) and len(potential_city) > 2:
                        return potential_city
        
        return ''
    
    def _convert_cap_certifications(self, cap_certifications: List[Dict]) -> List[Dict]:
        """Convert CAP certifications to unified format"""
        converted = []
        
        for cert in cap_certifications:
            converted_cert = {
                'name': cert.get('name', 'ISO 15189 Medical Laboratory Accreditation'),
                'type': 'CAP 15189',
                'status': cert.get('status', 'Active'),
                'accreditation_date': cert.get('issue_date', ''),
                'expiry_date': '',
                'accreditation_no': '',
                'reference_no': '',
                'remarks': 'CAP 15189 Accredited Laboratory',
                'score_impact': 18.0,  # High impact for CAP accreditation
                'source': 'College of American Pathologists',
                'scope': cert.get('scope', 'Medical testing and calibration laboratories'),
                'certification_body': 'College of American Pathologists (CAP)'
            }
            converted.append(converted_cert)
        
        return converted
    
    def _determine_region(self, country: str) -> str:
        """Determine region based on country"""
        region_mapping = {
            'United States': 'Americas',
            'Canada': 'Americas',
            'Brazil': 'Americas',
            'United Kingdom': 'Europe',
            'Germany': 'Europe',
            'Switzerland': 'Europe',
            'Ireland': 'Europe',
            'Japan': 'Asia-Pacific',
            'Singapore': 'Asia-Pacific',
            'China': 'Asia-Pacific',
            'South Korea': 'Asia-Pacific',
            'Saudi Arabia': 'Middle East',
            'UAE': 'Middle East',
            'South Africa': 'Africa'
        }
        
        return region_mapping.get(country, 'Unknown')
    
    def _generate_search_keywords(self, name: str, country: str) -> List[str]:
        """Generate search keywords for the laboratory"""
        keywords = []
        
        if name:
            # Add full name
            keywords.append(name.lower())
            
            # Add individual words
            words = re.findall(r'\b\w+\b', name.lower())
            keywords.extend([word for word in words if len(word) > 2])
            
            # Add laboratory-specific terms
            lab_terms = ['laboratory', 'lab', 'diagnostic', 'pathology', 'clinical']
            keywords.extend(lab_terms)
            
            # Add acronyms
            acronym_words = [word for word in words if len(word) > 3]
            if len(acronym_words) > 1:
                acronym = ''.join([word[0] for word in acronym_words])
                keywords.append(acronym)
        
        if country:
            keywords.append(country.lower())
        
        # Add CAP-specific keywords
        keywords.extend(['cap', 'iso 15189', 'medical laboratory', 'accredited'])
        
        return list(set(keywords))  # Remove duplicates
    
    def check_for_duplicates(self, existing_data: List[Dict], cap_data: List[Dict]) -> Dict:
        """Check for potential duplicates between existing data and CAP data"""
        duplicates = []
        
        for cap_lab in cap_data:
            cap_name_normalized = self._normalize_name(cap_lab['name'])
            
            for existing_org in existing_data:
                existing_name_normalized = self._normalize_name(existing_org['name'])
                
                # Check for name similarity
                if self._names_similar(cap_name_normalized, existing_name_normalized):
                    duplicates.append({
                        'cap_lab': cap_lab['name'],
                        'existing_org': existing_org['name'],
                        'similarity_reason': 'Name similarity'
                    })
        
        return {
            'duplicates_found': len(duplicates),
            'duplicate_pairs': duplicates
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normalize organization name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove common suffixes
        name = name.lower()
        name = re.sub(r'\s*(laboratory|laboratories|lab|labs|inc|llc|ltd|pvt|private limited|corporation|corp)\s*', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar"""
        # Simple similarity check - can be enhanced with fuzzy matching
        if name1 == name2:
            return True
        
        # Check if one name contains the other
        if name1 in name2 or name2 in name1:
            return True
        
        # Check for common words (at least 2 significant words in common)
        words1 = set(word for word in name1.split() if len(word) > 3)
        words2 = set(word for word in name2.split() if len(word) > 3)
        
        common_words = words1.intersection(words2)
        return len(common_words) >= 2
    
    def integrate_cap_data(self):
        """Main method to integrate CAP laboratory data"""
        print("🔬 Starting CAP Laboratory Database Integration...")
        
        # Load data
        cap_data = self.load_cap_data()
        existing_data = self.load_unified_data()
        
        if not cap_data:
            print("❌ No CAP data to integrate")
            return
        
        # Create backup
        self.backup_existing_data(existing_data)
        
        # Standardize CAP data
        standardized_cap = self.standardize_cap_data(cap_data)
        print(f"✅ Standardized {len(standardized_cap)} CAP laboratories")
        
        # Check for duplicates
        duplicate_check = self.check_for_duplicates(existing_data, standardized_cap)
        if duplicate_check['duplicates_found'] > 0:
            print(f"⚠️ Found {duplicate_check['duplicates_found']} potential duplicates")
            for dup in duplicate_check['duplicate_pairs'][:5]:  # Show first 5
                print(f"   - CAP: {dup['cap_lab']} <-> Existing: {dup['existing_org']}")
        
        # Combine data
        combined_data = existing_data + standardized_cap
        
        print(f"✅ Created enhanced database with {len(combined_data)} organizations")
        print(f"   - Existing organizations: {len(existing_data)}")
        print(f"   - New CAP laboratories: {len(standardized_cap)}")
        
        # Save enhanced data
        self.save_enhanced_data(combined_data)
        
        # Generate summary
        self.generate_integration_summary(combined_data)
    
    def save_enhanced_data(self, data: List[Dict]):
        """Save enhanced unified data to JSON file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Enhanced database saved to {self.output_file}")
            
            # Also update the main unified file
            with open(self.unified_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated main unified database: {self.unified_file}")
            
        except Exception as e:
            print(f"❌ Error saving enhanced data: {str(e)}")
    
    def generate_integration_summary(self, data: List[Dict]):
        """Generate integration summary report"""
        if not data:
            return
        
        total_orgs = len(data)
        cap_count = sum(1 for org in data if org.get('quality_indicators', {}).get('cap_accredited', False))
        jci_count = sum(1 for org in data if org.get('quality_indicators', {}).get('jci_accredited', False))
        nabh_count = sum(1 for org in data if org.get('quality_indicators', {}).get('nabh_accredited', False))
        lab_count = sum(1 for org in data if org.get('organization_type') == 'Medical Laboratory')
        
        # Country breakdown
        country_counts = {}
        for org in data:
            country = org.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        # Organization type breakdown
        org_type_counts = {}
        for org in data:
            org_type = org.get('organization_type', 'Unknown')
            org_type_counts[org_type] = org_type_counts.get(org_type, 0) + 1
        
        print(f"\n📊 === CAP Integration Summary ===")
        print(f"Total organizations: {total_orgs}")
        print(f"CAP accredited laboratories: {cap_count}")
        print(f"JCI accredited: {jci_count}")
        print(f"NABH accredited: {nabh_count}")
        print(f"Medical laboratories: {lab_count}")
        
        print(f"\n🌍 Top 10 Countries:")
        sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for country, count in sorted_countries:
            print(f"  {country}: {count}")
        
        print(f"\n🏥 Organization Types:")
        for org_type, count in sorted(org_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {org_type}: {count}")
        
        # Quality score statistics for CAP labs
        cap_labs = [org for org in data if org.get('quality_indicators', {}).get('cap_accredited', False)]
        if cap_labs:
            scores = [lab.get('quality_score', 0) for lab in cap_labs]
            avg_score = sum(scores) / len(scores)
            print(f"\n🔬 CAP Laboratory Statistics:")
            print(f"  Average Quality Score: {avg_score:.1f}")
            print(f"  Score Range: {min(scores):.1f} - {max(scores):.1f}")

def main():
    """Main function to integrate CAP laboratory data"""
    integrator = CAPDatabaseIntegrator()
    integrator.integrate_cap_data()

if __name__ == "__main__":
    main()