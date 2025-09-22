"""
Database Integrator
Integrates NABH data with existing JCI data to create unified healthcare organization database
"""

import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import re

class DatabaseIntegrator:
    def __init__(self):
        self.jci_file = 'jci_accredited_organizations.json'
        self.nabh_file = 'processed_nabh_hospitals.json'
        self.output_file = 'unified_healthcare_organizations.json'
        self.unified_data = []
        
    def load_jci_data(self) -> List[Dict]:
        """Load JCI accredited organizations data"""
        try:
            with open(self.jci_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} JCI organizations")
            return data
        except Exception as e:
            print(f"Error loading JCI data: {str(e)}")
            return []
    
    def load_nabh_data(self) -> List[Dict]:
        """Load processed NABH data"""
        try:
            with open(self.nabh_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} NABH hospitals")
            return data
        except Exception as e:
            print(f"Error loading NABH data: {str(e)}")
            return []
    
    def standardize_jci_data(self, jci_data: List[Dict]) -> List[Dict]:
        """Standardize JCI data to unified format"""
        standardized = []
        
        for org in jci_data:
            try:
                standardized_org = {
                    'name': org.get('name', ''),
                    'original_name': org.get('name', ''),
                    'city': '',
                    'state': '',
                    'country': org.get('country', ''),
                    'hospital_type': org.get('type', 'General Hospital'),
                    'certifications': [{
                        'name': 'JCI',
                        'type': 'JCI Accreditation',
                        'status': 'Active',
                        'accreditation_date': org.get('accreditation_date', ''),
                        'expiry_date': '',
                        'accreditation_no': '',
                        'reference_no': '',
                        'remarks': 'JCI Accredited',
                        'score_impact': 20.0,  # JCI has higher impact than NABH
                        'source': 'JCI Database'
                    }],
                    'data_source': 'JCI',
                    'last_updated': datetime.now().isoformat(),
                    'quality_indicators': {
                        'jci_accredited': True,
                        'nabh_accredited': False,
                        'international_accreditation': True,
                        'accreditation_valid': True
                    },
                    'region': org.get('region', ''),
                    'search_keywords': self._generate_search_keywords(org.get('name', ''), org.get('country', ''))
                }
                
                standardized.append(standardized_org)
                
            except Exception as e:
                print(f"Error standardizing JCI org {org.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return standardized
    
    def enhance_nabh_data(self, nabh_data: List[Dict]) -> List[Dict]:
        """Enhance NABH data with additional fields for unified format"""
        enhanced = []
        
        for hospital in nabh_data:
            try:
                # Check if this hospital also has JCI accreditation
                jci_accredited = self._check_jci_accreditation(hospital['name'])
                
                enhanced_hospital = hospital.copy()
                
                # Add JCI certification if found
                if jci_accredited:
                    jci_cert = {
                        'name': 'JCI',
                        'type': 'JCI Accreditation',
                        'status': 'Active',
                        'accreditation_date': jci_accredited.get('accreditation_date', ''),
                        'expiry_date': '',
                        'accreditation_no': '',
                        'reference_no': '',
                        'remarks': 'JCI Accredited',
                        'score_impact': 20.0,
                        'source': 'JCI Database'
                    }
                    enhanced_hospital['certifications'].append(jci_cert)
                    enhanced_hospital['quality_indicators']['jci_accredited'] = True
                    enhanced_hospital['quality_indicators']['international_accreditation'] = True
                else:
                    enhanced_hospital['quality_indicators']['jci_accredited'] = False
                    enhanced_hospital['quality_indicators']['international_accreditation'] = False
                
                # Add search keywords
                enhanced_hospital['search_keywords'] = self._generate_search_keywords(
                    hospital['name'], hospital.get('country', 'India')
                )
                
                # Add region if not present
                if 'region' not in enhanced_hospital:
                    enhanced_hospital['region'] = self._determine_region(hospital.get('country', 'India'))
                
                enhanced.append(enhanced_hospital)
                
            except Exception as e:
                print(f"Error enhancing NABH hospital {hospital.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return enhanced
    
    def _check_jci_accreditation(self, hospital_name: str) -> Dict:
        """Check if a hospital has JCI accreditation"""
        jci_data = self.load_jci_data()
        
        # Normalize hospital name for comparison
        normalized_name = self._normalize_name(hospital_name)
        
        for jci_org in jci_data:
            jci_normalized = self._normalize_name(jci_org.get('name', ''))
            
            # Check for exact match or partial match
            if normalized_name == jci_normalized or \
               normalized_name in jci_normalized or \
               jci_normalized in normalized_name:
                return jci_org
        
        return None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize hospital name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove common suffixes
        name = name.lower()
        name = re.sub(r'\s*(hospital|medical center|medical centre|clinic|institute|ltd|pvt|private limited)\s*', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _generate_search_keywords(self, name: str, country: str) -> List[str]:
        """Generate search keywords for the organization"""
        keywords = []
        
        if name:
            # Add full name
            keywords.append(name.lower())
            
            # Add individual words
            words = re.findall(r'\b\w+\b', name.lower())
            keywords.extend([word for word in words if len(word) > 2])
            
            # Add acronyms
            acronym_words = [word for word in words if len(word) > 3]
            if len(acronym_words) > 1:
                acronym = ''.join([word[0] for word in acronym_words])
                keywords.append(acronym)
        
        if country:
            keywords.append(country.lower())
        
        return list(set(keywords))  # Remove duplicates
    
    def _determine_region(self, country: str) -> str:
        """Determine region based on country"""
        region_mapping = {
            'India': 'Asia-Pacific',
            'Singapore': 'Asia-Pacific',
            'Malaysia': 'Asia-Pacific',
            'Thailand': 'Asia-Pacific',
            'South Korea': 'Asia-Pacific',
            'UAE': 'Middle East',
            'Saudi Arabia': 'Middle East',
            'Qatar': 'Middle East',
            'Jordan': 'Middle East',
            'Lebanon': 'Middle East',
            'Turkey': 'Europe',
            'Switzerland': 'Europe',
            'Brazil': 'Americas',
            'Colombia': 'Americas',
            'Argentina': 'Americas'
        }
        
        return region_mapping.get(country, 'Unknown')
    
    def merge_duplicate_organizations(self, organizations: List[Dict]) -> List[Dict]:
        """Merge organizations that appear in both JCI and NABH data"""
        merged = []
        processed_names = set()
        
        for org in organizations:
            normalized_name = self._normalize_name(org['name'])
            
            if normalized_name in processed_names:
                # Find the existing organization and merge certifications
                for existing_org in merged:
                    if self._normalize_name(existing_org['name']) == normalized_name:
                        # Merge certifications
                        existing_certs = {cert['name'] for cert in existing_org['certifications']}
                        for cert in org['certifications']:
                            if cert['name'] not in existing_certs:
                                existing_org['certifications'].append(cert)
                        
                        # Update quality indicators
                        existing_org['quality_indicators'].update(org['quality_indicators'])
                        
                        # Update data source
                        if org['data_source'] not in existing_org['data_source']:
                            existing_org['data_source'] += f", {org['data_source']}"
                        
                        break
            else:
                merged.append(org)
                processed_names.add(normalized_name)
        
        return merged
    
    def integrate_databases(self):
        """Main method to integrate JCI and NABH databases"""
        print("Starting database integration...")
        
        # Load data
        jci_data = self.load_jci_data()
        nabh_data = self.load_nabh_data()
        
        if not jci_data and not nabh_data:
            print("No data to integrate")
            return
        
        # Standardize JCI data
        standardized_jci = self.standardize_jci_data(jci_data)
        print(f"Standardized {len(standardized_jci)} JCI organizations")
        
        # Enhance NABH data
        enhanced_nabh = self.enhance_nabh_data(nabh_data)
        print(f"Enhanced {len(enhanced_nabh)} NABH hospitals")
        
        # Combine all organizations
        all_organizations = standardized_jci + enhanced_nabh
        
        # Merge duplicates
        self.unified_data = self.merge_duplicate_organizations(all_organizations)
        
        print(f"Created unified database with {len(self.unified_data)} organizations")
        
        # Save unified data
        self.save_unified_data()
        
        # Generate summary
        self.generate_integration_summary()
    
    def save_unified_data(self):
        """Save unified data to JSON file"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.unified_data, f, indent=2, ensure_ascii=False)
            print(f"Unified database saved to {self.output_file}")
        except Exception as e:
            print(f"Error saving unified data: {str(e)}")
    
    def generate_integration_summary(self):
        """Generate integration summary report"""
        if not self.unified_data:
            return
        
        total_orgs = len(self.unified_data)
        jci_count = sum(1 for org in self.unified_data if org['quality_indicators']['jci_accredited'])
        nabh_count = sum(1 for org in self.unified_data if org['quality_indicators']['nabh_accredited'])
        dual_accredited = sum(1 for org in self.unified_data 
                             if org['quality_indicators']['jci_accredited'] and 
                                org['quality_indicators']['nabh_accredited'])
        
        # Country breakdown
        country_counts = {}
        for org in self.unified_data:
            country = org.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        # Region breakdown
        region_counts = {}
        for org in self.unified_data:
            region = org.get('region', 'Unknown')
            region_counts[region] = region_counts.get(region, 0) + 1
        
        print(f"\n=== Database Integration Summary ===")
        print(f"Total organizations: {total_orgs}")
        print(f"JCI accredited: {jci_count}")
        print(f"NABH accredited: {nabh_count}")
        print(f"Dual accredited (JCI + NABH): {dual_accredited}")
        
        print(f"\nTop 10 Countries:")
        sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for country, count in sorted_countries:
            print(f"  {country}: {count}")
        
        print(f"\nRegion Distribution:")
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {region}: {count}")

def main():
    """Main function to integrate databases"""
    integrator = DatabaseIntegrator()
    integrator.integrate_databases()

if __name__ == "__main__":
    main()