#!/usr/bin/env python3
"""
NABL Database Integrator
Integrates cleaned NABL data with the unified healthcare organizations database
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class NABLDatabaseIntegrator:
    def __init__(self, nabl_data_file: str = None, unified_db_file: str = None):
        self.project_root = Path.cwd()
        self.nabl_data_file = nabl_data_file or "nabl_cleaned_data_20250926_175749.json"
        self.unified_db_file = unified_db_file or "unified_healthcare_organizations.json"
        self.backup_file = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Integration statistics
        self.stats = {
            'nabl_organizations_loaded': 0,
            'existing_organizations_loaded': 0,
            'new_organizations_added': 0,
            'existing_organizations_updated': 0,
            'duplicates_merged': 0,
            'nabl_certifications_added': 0,
            'total_organizations_final': 0
        }
    
    def load_nabl_data(self) -> List[Dict[str, Any]]:
        """Load cleaned NABL data"""
        try:
            with open(self.nabl_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract organizations from metadata structure if present
            if isinstance(data, dict) and 'organizations' in data:
                organizations = data['organizations']
            else:
                organizations = data
            
            self.stats['nabl_organizations_loaded'] = len(organizations)
            self.logger.info(f"Loaded {len(organizations)} cleaned NABL organizations")
            return organizations
        except Exception as e:
            self.logger.error(f"Error loading NABL data: {e}")
            return []
    
    def load_existing_database(self) -> List[Dict[str, Any]]:
        """Load existing unified healthcare database"""
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different data structures
            if isinstance(data, dict):
                if 'organizations' in data:
                    organizations = data['organizations']
                elif 'data' in data:
                    organizations = data['data']
                else:
                    organizations = []
            else:
                organizations = data
            
            self.stats['existing_organizations_loaded'] = len(organizations)
            self.logger.info(f"Loaded {len(organizations)} existing organizations")
            return organizations
        except FileNotFoundError:
            self.logger.info("No existing database found, creating new one")
            return []
        except Exception as e:
            self.logger.error(f"Error loading existing database: {e}")
            return []
    
    def backup_existing_database(self) -> bool:
        """Create backup of existing database"""
        try:
            if Path(self.unified_db_file).exists():
                with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                with open(self.backup_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                self.logger.info(f"Database backup created: {self.backup_file}")
                return True
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
        
        return True
    
    def normalize_organization_name(self, name: str) -> str:
        """Normalize organization name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Remove common suffixes and prefixes
        patterns_to_remove = [
            r'\b(private\s+limited|pvt\.?\s*ltd\.?|ltd\.?|limited)\b',
            r'\b(hospital|medical\s+center|medical\s+centre|clinic|institute|laboratory|labs?)\b',
            r'\b(dr\.?|prof\.?|sir|smt\.?|shri)\b',
            r'[^\w\s]',  # Remove punctuation
        ]
        
        for pattern in patterns_to_remove:
            name = re.sub(pattern, ' ', name, flags=re.IGNORECASE)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name
    
    def find_matching_organization(self, nabl_org: Dict[str, Any], existing_orgs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching organization in existing database"""
        nabl_name_normalized = self.normalize_organization_name(nabl_org['organization_name'])
        
        for existing_org in existing_orgs:
            existing_name_normalized = self.normalize_organization_name(existing_org.get('name', ''))
            
            # Exact match
            if nabl_name_normalized == existing_name_normalized:
                return existing_org
            
            # Partial match (one contains the other)
            if nabl_name_normalized and existing_name_normalized:
                if (nabl_name_normalized in existing_name_normalized or 
                    existing_name_normalized in nabl_name_normalized):
                    # Additional check for significant overlap
                    overlap_ratio = len(set(nabl_name_normalized.split()) & set(existing_name_normalized.split())) / max(len(nabl_name_normalized.split()), len(existing_name_normalized.split()))
                    if overlap_ratio >= 0.6:  # 60% word overlap
                        return existing_org
        
        return None
    
    def convert_nabl_to_unified_format(self, nabl_org: Dict[str, Any]) -> Dict[str, Any]:
        """Convert NABL organization to unified database format"""
        # Create NABL certification entry
        nabl_certification = {
            'name': 'National Accreditation Board for Testing and Calibration Laboratories (NABL)',
            'type': 'NABL Accreditation',
            'status': nabl_org.get('accreditation_status', 'Active'),
            'accreditation_date': '',
            'expiry_date': '',
            'accreditation_no': nabl_org.get('accreditation_number', ''),
            'reference_no': '',
            'remarks': f"NABL Accredited - {nabl_org.get('accreditation_type', 'Testing')}",
            'score_impact': 15.0,
            'source': 'NABL Database',
            'iso_standard': nabl_org.get('iso_standard', ''),
            'scope': nabl_org.get('scope', ''),
            'services': nabl_org.get('services', [])
        }
        
        # Determine location information
        locations = nabl_org.get('locations', [])
        city = locations[0] if locations else ''
        state = ''
        
        # Try to extract state from location or organization name
        indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa',
            'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
            'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
            'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir'
        ]
        
        org_name_lower = nabl_org['organization_name'].lower()
        for state_name in indian_states:
            if state_name.lower() in org_name_lower:
                state = state_name
                break
        
        # Create unified organization entry
        unified_org = {
            'name': nabl_org['organization_name'],
            'original_name': nabl_org['organization_name'],
            'city': city,
            'state': state,
            'country': 'India',
            'hospital_type': nabl_org.get('organization_type', 'Healthcare Organization'),
            'certifications': [nabl_certification],
            'data_source': 'NABL',
            'last_updated': datetime.now().isoformat(),
            'quality_indicators': {
                'jci_accredited': False,
                'nabh_accredited': False,
                'nabl_accredited': True,
                'international_accreditation': False,
                'accreditation_valid': nabl_org.get('accreditation_status', 'Active').lower() == 'active',
                'confidence_score': nabl_org.get('data_quality', {}).get('confidence_score', 0)
            },
            'region': 'Asia-Pacific',
            'search_keywords': self.generate_search_keywords(nabl_org['organization_name'], locations),
            'nabl_data': {
                'extraction_method': nabl_org.get('extraction_method', 'PDF'),
                'source': nabl_org.get('source', 'NABL PDF Document'),
                'last_verified': nabl_org.get('last_verified', datetime.now().isoformat()),
                'data_quality': nabl_org.get('data_quality', {})
            }
        }
        
        return unified_org
    
    def generate_search_keywords(self, name: str, locations: List[str]) -> List[str]:
        """Generate search keywords for the organization"""
        keywords = []
        
        if name:
            # Add full name
            keywords.append(name.lower())
            
            # Add individual words (longer than 2 characters)
            words = re.findall(r'\b\w{3,}\b', name.lower())
            keywords.extend(words)
            
            # Add acronym if multiple words
            if len(words) > 1:
                acronym = ''.join([word[0] for word in words if len(word) > 2])
                if len(acronym) > 2:
                    keywords.append(acronym)
        
        # Add locations
        keywords.extend([loc.lower() for loc in locations])
        
        # Add common healthcare terms
        keywords.extend(['healthcare', 'medical', 'laboratory', 'testing', 'nabl'])
        
        return list(set(keywords))  # Remove duplicates
    
    def merge_organizations(self, existing_org: Dict[str, Any], nabl_org: Dict[str, Any]) -> Dict[str, Any]:
        """Merge NABL data with existing organization"""
        merged_org = existing_org.copy()
        
        # Add NABL certification
        nabl_unified = self.convert_nabl_to_unified_format(nabl_org)
        nabl_certification = nabl_unified['certifications'][0]
        
        # Check if NABL certification already exists
        has_nabl = any(cert.get('type') == 'NABL Accreditation' for cert in merged_org.get('certifications', []))
        
        if not has_nabl:
            if 'certifications' not in merged_org:
                merged_org['certifications'] = []
            merged_org['certifications'].append(nabl_certification)
            self.stats['nabl_certifications_added'] += 1
        
        # Update quality indicators
        if 'quality_indicators' not in merged_org:
            merged_org['quality_indicators'] = {}
        
        merged_org['quality_indicators']['nabl_accredited'] = True
        merged_org['quality_indicators']['accreditation_valid'] = True
        
        # Update data source to include NABL
        if merged_org.get('data_source') == 'JCI':
            merged_org['data_source'] = 'JCI+NABL'
        elif merged_org.get('data_source') == 'NABH':
            merged_org['data_source'] = 'NABH+NABL'
        else:
            merged_org['data_source'] = 'NABL'
        
        # Add NABL-specific data
        merged_org['nabl_data'] = nabl_unified['nabl_data']
        
        # Update search keywords
        existing_keywords = set(merged_org.get('search_keywords', []))
        new_keywords = set(nabl_unified['search_keywords'])
        merged_org['search_keywords'] = list(existing_keywords | new_keywords)
        
        # Update last modified
        merged_org['last_updated'] = datetime.now().isoformat()
        
        return merged_org
    
    def integrate_nabl_data(self) -> Dict[str, Any]:
        """Main method to integrate NABL data with existing database"""
        self.logger.info("Starting NABL database integration")
        
        # Load data
        nabl_organizations = self.load_nabl_data()
        if not nabl_organizations:
            self.logger.error("No NABL data to integrate")
            return self.stats
        
        existing_organizations = self.load_existing_database()
        
        # Create backup
        self.backup_existing_database()
        
        # Process integration
        integrated_organizations = existing_organizations.copy()
        processed_existing_ids = set()
        
        for nabl_org in nabl_organizations:
            try:
                # Find matching organization
                matching_org = self.find_matching_organization(nabl_org, existing_organizations)
                
                if matching_org:
                    # Merge with existing organization
                    org_index = existing_organizations.index(matching_org)
                    if org_index not in processed_existing_ids:
                        integrated_organizations[org_index] = self.merge_organizations(matching_org, nabl_org)
                        processed_existing_ids.add(org_index)
                        self.stats['existing_organizations_updated'] += 1
                    else:
                        self.stats['duplicates_merged'] += 1
                else:
                    # Add as new organization
                    new_org = self.convert_nabl_to_unified_format(nabl_org)
                    integrated_organizations.append(new_org)
                    self.stats['new_organizations_added'] += 1
                    self.stats['nabl_certifications_added'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error processing NABL organization {nabl_org.get('organization_name', 'Unknown')}: {e}")
                continue
        
        self.stats['total_organizations_final'] = len(integrated_organizations)
        
        # Save integrated database
        self.save_integrated_database(integrated_organizations)
        
        return self.stats
    
    def save_integrated_database(self, organizations: List[Dict[str, Any]]) -> str:
        """Save integrated database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare output data
        output_data = {
            'metadata': {
                'integration_timestamp': datetime.now().isoformat(),
                'nabl_source_file': self.nabl_data_file,
                'integration_statistics': self.stats,
                'total_organizations': len(organizations),
                'data_sources': list(set(org.get('data_source', 'Unknown') for org in organizations)),
                'version': '2.0',
                'description': 'Unified Healthcare Organizations Database with NABL Integration'
            },
            'organizations': organizations
        }
        
        # Save to main file
        with open(self.unified_db_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Save timestamped copy
        timestamped_file = f"unified_healthcare_organizations_{timestamp}.json"
        with open(timestamped_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Integrated database saved to: {self.unified_db_file}")
        self.logger.info(f"Timestamped copy saved to: {timestamped_file}")
        
        return self.unified_db_file
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        report = {
            'integration_summary': self.stats,
            'integration_timestamp': datetime.now().isoformat(),
            'files_processed': {
                'nabl_data_file': self.nabl_data_file,
                'unified_db_file': self.unified_db_file,
                'backup_file': self.backup_file
            },
            'success_metrics': {
                'integration_rate': (self.stats['existing_organizations_updated'] + self.stats['new_organizations_added']) / max(self.stats['nabl_organizations_loaded'], 1) * 100,
                'database_growth': self.stats['new_organizations_added'] / max(self.stats['existing_organizations_loaded'], 1) * 100 if self.stats['existing_organizations_loaded'] > 0 else 100,
                'certification_enhancement': self.stats['nabl_certifications_added'] / max(self.stats['total_organizations_final'], 1) * 100
            }
        }
        
        # Save report
        report_file = f"nabl_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Integration report saved to: {report_file}")
        return report

def main():
    import sys
    
    # Get input files from command line or use defaults
    nabl_file = sys.argv[1] if len(sys.argv) > 1 else None
    unified_db_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    integrator = NABLDatabaseIntegrator(nabl_file, unified_db_file)
    
    print("🔗 NABL Database Integration Started")
    print("=" * 50)
    
    # Perform integration
    stats = integrator.integrate_nabl_data()
    
    # Generate report
    report = integrator.generate_integration_report()
    
    if stats['total_organizations_final'] > 0:
        print(f"✅ Database integration completed successfully!")
        print(f"\n📊 Integration Summary:")
        print(f"   • NABL Organizations Loaded: {stats['nabl_organizations_loaded']}")
        print(f"   • Existing Organizations: {stats['existing_organizations_loaded']}")
        print(f"   • New Organizations Added: {stats['new_organizations_added']}")
        print(f"   • Existing Organizations Updated: {stats['existing_organizations_updated']}")
        print(f"   • NABL Certifications Added: {stats['nabl_certifications_added']}")
        print(f"   • Total Organizations Final: {stats['total_organizations_final']}")
        
        print(f"\n🎯 Success Metrics:")
        print(f"   • Integration Rate: {report['success_metrics']['integration_rate']:.1f}%")
        print(f"   • Database Growth: {report['success_metrics']['database_growth']:.1f}%")
        print(f"   • Certification Enhancement: {report['success_metrics']['certification_enhancement']:.1f}%")
        
    else:
        print("❌ No organizations were integrated")
    
    print("\n" + "=" * 50)
    print("🎉 NABL Database Integration Complete!")

if __name__ == "__main__":
    main()