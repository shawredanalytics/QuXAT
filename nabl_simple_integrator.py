#!/usr/bin/env python3
"""
Simple NABL Integrator
Integrates NABL data focusing only on lab name, address, and certification details with validity.
"""

import json
import re
from datetime import datetime
from pathlib import Path
import logging

class SimpleNABLIntegrator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.unified_db_file = "unified_healthcare_organizations.json"
        self.backup_file = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Integration statistics
        self.stats = {
            'nabl_labs_processed': 0,
            'nabl_certifications_added': 0,
            'organizations_updated': 0,
            'total_organizations': 0
        }
    
    def extract_nabl_labs_from_text(self) -> list:
        """Extract NABL lab data from the extracted text file"""
        labs = []
        
        try:
            with open('nabl_pdf_extracted_text.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by pages and process each page
            pages = content.split('--- PAGE')
            
            for page in pages:
                lines = page.strip().split('\n')
                
                for i, line in enumerate(lines):
                    # Look for lines with MC- pattern (NABL certificate numbers)
                    if 'MC-' in line and any(keyword in line.lower() for keyword in ['hospital', 'lab', 'diagnostic', 'medical', 'clinic']):
                        try:
                            # Extract lab information from the line
                            parts = line.split()
                            
                            # Find the lab name (usually before MC-)
                            mc_index = next(j for j, part in enumerate(parts) if 'MC-' in part)
                            
                            # Extract state and lab name
                            state = parts[1] if len(parts) > 1 else "Unknown"
                            lab_name_parts = parts[2:mc_index]
                            lab_name = ' '.join(lab_name_parts).strip(',')
                            
                            # Extract certificate number
                            cert_number = parts[mc_index]
                            
                            # Extract test categories (after cert number)
                            test_categories = []
                            for j in range(mc_index + 1, len(parts)):
                                if re.match(r'\d{2}-\d{2}-\d{4}', parts[j]):  # Date pattern
                                    break
                                test_categories.append(parts[j])
                            
                            # Extract dates
                            date_parts = []
                            for j in range(mc_index + 1, len(parts)):
                                if re.match(r'\d{2}-\d{2}-\d{4}', parts[j]):
                                    date_parts.append(parts[j])
                                    if len(date_parts) == 2:
                                        break
                            
                            issue_date = date_parts[0] if len(date_parts) > 0 else None
                            expiry_date = date_parts[1] if len(date_parts) > 1 else None
                            
                            # Get address from next line if available
                            address = ""
                            if i + 1 < len(lines):
                                next_line = lines[i + 1].strip()
                                if not next_line.startswith('---') and 'MC-' not in next_line:
                                    address = next_line
                            
                            # Create lab entry
                            lab = {
                                'lab_name': lab_name,
                                'state': state,
                                'address': address,
                                'nabl_certificate_number': cert_number,
                                'test_categories': ' '.join(test_categories),
                                'issue_date': issue_date,
                                'expiry_date': expiry_date,
                                'status': 'Active' if self.is_certificate_valid(expiry_date) else 'Expired'
                            }
                            
                            labs.append(lab)
                            self.stats['nabl_labs_processed'] += 1
                            
                        except Exception as e:
                            self.logger.warning(f"Error parsing line: {line[:100]}... - {e}")
                            continue
            
            self.logger.info(f"Extracted {len(labs)} NABL laboratories")
            return labs
            
        except Exception as e:
            self.logger.error(f"Error reading NABL text file: {e}")
            return []
    
    def is_certificate_valid(self, expiry_date_str: str) -> bool:
        """Check if certificate is still valid"""
        if not expiry_date_str:
            return False
        
        try:
            expiry_date = datetime.strptime(expiry_date_str, '%d-%m-%Y')
            return expiry_date > datetime.now()
        except:
            return False
    
    def load_unified_database(self) -> list:
        """Load the unified healthcare organizations database"""
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list and dict structures
            if isinstance(data, dict):
                organizations = data.get('organizations', [])
            else:
                organizations = data
            
            self.stats['total_organizations'] = len(organizations)
            self.logger.info(f"Loaded {len(organizations)} organizations from unified database")
            return organizations
            
        except Exception as e:
            self.logger.error(f"Error loading unified database: {e}")
            return []
    
    def create_backup(self):
        """Create backup of unified database"""
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = f.read()
            
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                f.write(data)
            
            self.logger.info(f"Database backup created: {self.backup_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
    
    def find_matching_organization(self, lab: dict, organizations: list) -> dict:
        """Find matching organization in the database"""
        lab_name_lower = lab['lab_name'].lower()
        
        for org in organizations:
            if not isinstance(org, dict):
                continue
            
            org_name_lower = org.get('name', '').lower()
            
            # Check for exact match or partial match
            if (lab_name_lower in org_name_lower or 
                org_name_lower in lab_name_lower or
                any(word in org_name_lower for word in lab_name_lower.split() if len(word) > 3)):
                
                # Additional check for location match
                org_city = org.get('city', '').lower()
                org_state = org.get('state', '').lower()
                lab_state = lab['state'].lower()
                
                if lab_state in org_state or org_state in lab_state:
                    return org
        
        return None
    
    def add_nabl_certification(self, organization: dict, lab: dict):
        """Add NABL certification to organization"""
        if 'certifications' not in organization:
            organization['certifications'] = []
        
        # Ensure certifications is a list
        if not isinstance(organization['certifications'], list):
            organization['certifications'] = []
        
        # Check if NABL certification already exists
        has_nabl = False
        for cert in organization['certifications']:
            if isinstance(cert, dict) and cert.get('type') == 'NABL Accreditation':
                has_nabl = True
                break
        
        if not has_nabl:
            nabl_cert = {
                'name': 'National Accreditation Board for Testing and Calibration Laboratories (NABL)',
                'type': 'NABL Accreditation',
                'status': lab['status'],
                'certificate_number': lab['nabl_certificate_number'],
                'test_categories': lab['test_categories'],
                'issue_date': lab['issue_date'],
                'expiry_date': lab['expiry_date'],
                'score_impact': 15.0 if lab['status'] == 'Active' else 0.0,
                'source': 'NABL PDF Document'
            }
            
            organization['certifications'].append(nabl_cert)
            
            # Update quality indicators
            if 'quality_indicators' not in organization:
                organization['quality_indicators'] = {}
            
            organization['quality_indicators']['nabl_accredited'] = True
            organization['quality_indicators']['accreditation_valid'] = lab['status'] == 'Active'
            
            # Update data source
            current_source = organization.get('data_source', '')
            if 'NABL' not in current_source:
                if current_source:
                    organization['data_source'] = f"{current_source}+NABL"
                else:
                    organization['data_source'] = 'NABL'
            
            self.stats['nabl_certifications_added'] += 1
            self.stats['organizations_updated'] += 1
            
            return True
        
        return False
    
    def integrate_nabl_data(self):
        """Main integration process"""
        self.logger.info("Starting NABL integration process...")
        
        # Create backup
        self.create_backup()
        
        # Extract NABL labs
        nabl_labs = self.extract_nabl_labs_from_text()
        if not nabl_labs:
            self.logger.error("No NABL labs extracted. Aborting integration.")
            return
        
        # Load unified database
        organizations = self.load_unified_database()
        if not organizations:
            self.logger.error("No organizations loaded. Aborting integration.")
            return
        
        # Process each NABL lab
        matched_count = 0
        for lab in nabl_labs:
            matching_org = self.find_matching_organization(lab, organizations)
            
            if matching_org:
                if self.add_nabl_certification(matching_org, lab):
                    matched_count += 1
                    self.logger.info(f"Added NABL certification to: {matching_org.get('name')}")
        
        # Save updated database
        try:
            with open(self.unified_db_file, 'w', encoding='utf-8') as f:
                json.dump(organizations, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Updated database saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving updated database: {e}")
            return
        
        # Generate report
        self.generate_report(matched_count)
    
    def generate_report(self, matched_count: int):
        """Generate integration report"""
        report = {
            'integration_timestamp': datetime.now().isoformat(),
            'nabl_labs_processed': self.stats['nabl_labs_processed'],
            'organizations_matched': matched_count,
            'nabl_certifications_added': self.stats['nabl_certifications_added'],
            'organizations_updated': self.stats['organizations_updated'],
            'total_organizations': self.stats['total_organizations'],
            'success_rate': f"{(matched_count / self.stats['nabl_labs_processed'] * 100):.1f}%" if self.stats['nabl_labs_processed'] > 0 else "0%"
        }
        
        report_file = f"nabl_simple_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Integration report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
        
        # Print summary
        print("\n=== NABL Integration Summary ===")
        print(f"NABL labs processed: {report['nabl_labs_processed']}")
        print(f"Organizations matched: {report['organizations_matched']}")
        print(f"NABL certifications added: {report['nabl_certifications_added']}")
        print(f"Organizations updated: {report['organizations_updated']}")
        print(f"Success rate: {report['success_rate']}")
        print(f"Total organizations in database: {report['total_organizations']}")
        print("================================")

if __name__ == "__main__":
    integrator = SimpleNABLIntegrator()
    integrator.integrate_nabl_data()