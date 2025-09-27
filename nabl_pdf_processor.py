#!/usr/bin/env python3
"""
NABL PDF Processor
Extracts organization data from NABL PDF documents and integrates with healthcare database
"""

import PyPDF2
import pdfplumber
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

class NABLPDFProcessor:
    def __init__(self, pdf_path: str = None):
        self.pdf_path = pdf_path or "C:/Users/MANIKUMAR/Downloads/202402170534-NABL-600-doc-1.pdf"
        self.project_root = Path.cwd()
        self.extracted_data = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for NABL data extraction
        self.patterns = {
            'organization_name': r'^[A-Z][A-Za-z\s&.,()-]+(?:Ltd|Limited|Pvt|Private|Hospital|Clinic|Laboratory|Labs?|Centre|Center|Institute|Corporation|Company)?\.?$',
            'location': r'[A-Za-z\s,.-]+(?:Delhi|Mumbai|Bangalore|Chennai|Kolkata|Hyderabad|Pune|Ahmedabad|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Thane|Bhopal|Visakhapatnam|Pimpri|Patna|Vadodara|Ghaziabad|Ludhiana|Agra|Nashik|Faridabad|Meerut|Rajkot|Kalyan|Vasai|Varanasi|Srinagar|Aurangabad|Dhanbad|Amritsar|Navi Mumbai|Allahabad|Ranchi|Howrah|Coimbatore|Jabalpur|Gwalior|Vijayawada|Jodhpur|Madurai|Raipur|Kota|Guwahati|Chandigarh|Solapur|Hubli|Tiruchirappalli|Bareilly|Mysore|Tiruppur|Gurgaon|Aligarh|Jalandhar|Bhubaneswar|Salem|Mira-Bhayandar|Warangal|Guntur|Bhiwandi|Saharanpur|Gorakhpur|Bikaner|Amravati|Noida|Jamshedpur|Bhilai|Cuttack|Firozabad|Kochi|Nellore|Bhavnagar|Dehradun|Durgapur|Asansol|Rourkela|Nanded|Kolhapur|Ajmer|Akola|Gulbarga|Jamnagar|Ujjain|Loni|Siliguri|Jhansi|Ulhasnagar|Jammu|Sangli-Miraj|Mangalore|Erode|Belgaum|Ambattur|Tirunelveli|Malegaon|Gaya|Jalgaon|Udaipur|Maheshtala)',
            'accreditation_number': r'NABL-\d+|TC-\d+|MC-\d+|\d{4,6}',
            'iso_standard': r'ISO\s*\d{4,5}(?:-\d+)?',
            'validity_date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}',
            'scope': r'(?:Medical|Clinical|Testing|Calibration|Chemical|Biological|Microbiological|Pathology|Radiology|Laboratory|Diagnostic)'
        }
    
    def extract_text_from_pdf(self) -> str:
        """Extract text from PDF using multiple methods for better accuracy"""
        text_content = ""
        
        try:
            # Method 1: Using pdfplumber (better for tables and structured data)
            with pdfplumber.open(self.pdf_path) as pdf:
                self.logger.info(f"PDF has {len(pdf.pages)} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.info(f"Processing page {page_num}")
                    
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_content += f"\n--- PAGE {page_num} ---\n"
                        text_content += page_text
                    
                    # Extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        self.logger.info(f"Found {len(tables)} tables on page {page_num}")
                        for table_num, table in enumerate(tables, 1):
                            text_content += f"\n--- TABLE {page_num}-{table_num} ---\n"
                            for row in table:
                                if row and any(cell for cell in row if cell):
                                    text_content += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}")
            
            # Fallback: Using PyPDF2
            try:
                with open(self.pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    self.logger.info(f"Fallback: PDF has {len(pdf_reader.pages)} pages")
                    
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- PAGE {page_num} (PyPDF2) ---\n"
                            text_content += page_text
                            
            except Exception as e2:
                self.logger.error(f"Both PDF extraction methods failed: {e2}")
                return ""
        
        return text_content
    
    def parse_organization_data(self, text_content: str) -> List[Dict[str, Any]]:
        """Parse organization data from extracted text"""
        organizations = []
        lines = text_content.split('\n')
        
        current_org = {}
        in_table = False
        table_headers = []
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect table headers
            if 'S.No' in line or 'Organization' in line or 'Laboratory' in line:
                in_table = True
                table_headers = [col.strip() for col in line.split('|') if col.strip()]
                self.logger.info(f"Found table headers: {table_headers}")
                continue
            
            # Process table rows
            if in_table and '|' in line:
                row_data = [col.strip() for col in line.split('|') if col.strip()]
                
                if len(row_data) >= 2:  # At least organization name and some data
                    org_data = self.extract_organization_info(row_data, table_headers)
                    if org_data:
                        organizations.append(org_data)
                continue
            
            # Process non-table format
            org_info = self.extract_organization_from_line(line)
            if org_info:
                organizations.append(org_info)
        
        self.logger.info(f"Extracted {len(organizations)} organizations from PDF")
        return organizations
    
    def extract_organization_info(self, row_data: List[str], headers: List[str]) -> Optional[Dict[str, Any]]:
        """Extract organization information from table row"""
        if not row_data or len(row_data) < 2:
            return None
        
        org_data = {
            'organization_name': '',
            'nabl_accredited': True,
            'accreditation_type': 'Medical Laboratory',
            'iso_standard': 'ISO 15189',
            'locations': [],
            'services': [],
            'accreditation_status': 'Active',
            'accreditation_number': '',
            'validity_date': '',
            'scope': '',
            'last_verified': datetime.now().strftime("%Y-%m-%d"),
            'source': 'NABL PDF Document',
            'extraction_method': 'PDF Table Parsing'
        }
        
        # Map data based on position or headers
        for i, data in enumerate(row_data):
            if i == 0 and data.isdigit():
                continue  # Skip serial number
            
            # Organization name (usually first non-numeric field)
            if not org_data['organization_name'] and not data.isdigit():
                org_data['organization_name'] = self.clean_organization_name(data)
            
            # Location detection
            elif re.search(self.patterns['location'], data, re.IGNORECASE):
                locations = self.extract_locations(data)
                org_data['locations'].extend(locations)
            
            # Accreditation number
            elif re.search(self.patterns['accreditation_number'], data):
                org_data['accreditation_number'] = data
            
            # ISO standard
            elif re.search(self.patterns['iso_standard'], data, re.IGNORECASE):
                org_data['iso_standard'] = data
            
            # Validity date
            elif re.search(self.patterns['validity_date'], data):
                org_data['validity_date'] = data
            
            # Scope
            elif re.search(self.patterns['scope'], data, re.IGNORECASE):
                org_data['scope'] = data
                org_data['services'].append(data)
        
        # Validate organization data
        if org_data['organization_name'] and len(org_data['organization_name']) > 3:
            return org_data
        
        return None
    
    def extract_organization_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract organization information from a single line"""
        # Skip headers, page numbers, etc.
        if any(skip in line.lower() for skip in ['page', 'nabl', 'accredited', 'laboratory', 'list', 'document']):
            return None
        
        # Look for organization name pattern
        org_match = re.search(self.patterns['organization_name'], line)
        if not org_match:
            return None
        
        org_name = self.clean_organization_name(org_match.group())
        if len(org_name) < 4:
            return None
        
        org_data = {
            'organization_name': org_name,
            'nabl_accredited': True,
            'accreditation_type': 'Medical Laboratory',
            'iso_standard': 'ISO 15189',
            'locations': self.extract_locations(line),
            'services': ['Clinical Laboratory'],
            'accreditation_status': 'Active',
            'accreditation_number': '',
            'validity_date': '',
            'scope': '',
            'last_verified': datetime.now().strftime("%Y-%m-%d"),
            'source': 'NABL PDF Document',
            'extraction_method': 'Line Parsing'
        }
        
        # Extract additional information from the same line
        acc_num_match = re.search(self.patterns['accreditation_number'], line)
        if acc_num_match:
            org_data['accreditation_number'] = acc_num_match.group()
        
        iso_match = re.search(self.patterns['iso_standard'], line, re.IGNORECASE)
        if iso_match:
            org_data['iso_standard'] = iso_match.group()
        
        date_match = re.search(self.patterns['validity_date'], line)
        if date_match:
            org_data['validity_date'] = date_match.group()
        
        scope_match = re.search(self.patterns['scope'], line, re.IGNORECASE)
        if scope_match:
            org_data['scope'] = scope_match.group()
            org_data['services'] = [scope_match.group()]
        
        return org_data
    
    def clean_organization_name(self, name: str) -> str:
        """Clean and standardize organization name"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Remove common prefixes/suffixes that might interfere
        name = re.sub(r'^(Dr\.?|Mr\.?|Ms\.?|Mrs\.?)\s+', '', name, flags=re.IGNORECASE)
        
        # Standardize common abbreviations
        replacements = {
            r'\bPvt\.?\s*Ltd\.?': 'Private Limited',
            r'\bLtd\.?': 'Limited',
            r'\bHosp\.?': 'Hospital',
            r'\bLab\.?': 'Laboratory',
            r'\bMed\.?': 'Medical',
            r'\bClin\.?': 'Clinic'
        }
        
        for pattern, replacement in replacements.items():
            name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        
        return name.strip()
    
    def extract_locations(self, text: str) -> List[str]:
        """Extract location information from text"""
        locations = []
        
        # Find all location matches
        location_matches = re.findall(self.patterns['location'], text, re.IGNORECASE)
        
        for match in location_matches:
            # Clean and standardize location
            location = match.strip().title()
            if location and location not in locations:
                locations.append(location)
        
        return locations
    
    def process_pdf(self) -> List[Dict[str, Any]]:
        """Main method to process the PDF and extract organization data"""
        self.logger.info(f"Processing NABL PDF: {self.pdf_path}")
        
        # Check if file exists
        if not Path(self.pdf_path).exists():
            self.logger.error(f"PDF file not found: {self.pdf_path}")
            return []
        
        # Extract text from PDF
        text_content = self.extract_text_from_pdf()
        if not text_content:
            self.logger.error("No text content extracted from PDF")
            return []
        
        # Save extracted text for debugging
        text_file = self.project_root / "nabl_pdf_extracted_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        self.logger.info(f"Extracted text saved to: {text_file}")
        
        # Parse organization data
        organizations = self.parse_organization_data(text_content)
        
        # Remove duplicates
        unique_organizations = self.remove_duplicates(organizations)
        
        self.extracted_data = unique_organizations
        return unique_organizations
    
    def remove_duplicates(self, organizations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate organizations based on name similarity"""
        unique_orgs = []
        seen_names = set()
        
        for org in organizations:
            org_name = org['organization_name'].lower().strip()
            
            # Simple duplicate check
            if org_name not in seen_names:
                seen_names.add(org_name)
                unique_orgs.append(org)
            else:
                self.logger.debug(f"Duplicate organization skipped: {org['organization_name']}")
        
        self.logger.info(f"Removed {len(organizations) - len(unique_orgs)} duplicates")
        return unique_orgs
    
    def save_extracted_data(self, filename: str = None) -> str:
        """Save extracted data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nabl_pdf_extracted_data_{timestamp}.json"
        
        filepath = self.project_root / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Extracted data saved to: {filepath}")
        return str(filepath)
    
    def generate_extraction_report(self) -> Dict[str, Any]:
        """Generate a report of the extraction process"""
        report = {
            'extraction_timestamp': datetime.now().isoformat(),
            'pdf_source': self.pdf_path,
            'total_organizations_extracted': len(self.extracted_data),
            'extraction_summary': {
                'organizations_with_locations': len([org for org in self.extracted_data if org['locations']]),
                'organizations_with_accreditation_numbers': len([org for org in self.extracted_data if org['accreditation_number']]),
                'organizations_with_validity_dates': len([org for org in self.extracted_data if org['validity_date']]),
                'organizations_with_scope': len([org for org in self.extracted_data if org['scope']])
            },
            'sample_organizations': self.extracted_data[:5] if self.extracted_data else [],
            'extraction_statistics': {
                'avg_name_length': sum(len(org['organization_name']) for org in self.extracted_data) / len(self.extracted_data) if self.extracted_data else 0,
                'total_locations_found': sum(len(org['locations']) for org in self.extracted_data),
                'unique_iso_standards': list(set(org['iso_standard'] for org in self.extracted_data if org['iso_standard']))
            }
        }
        
        # Save report
        report_file = self.project_root / f"nabl_pdf_extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Extraction report saved to: {report_file}")
        return report

def main():
    import sys
    
    # Get PDF path from command line or use default
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    processor = NABLPDFProcessor(pdf_path)
    
    print("🔍 NABL PDF Processing Started")
    print("=" * 50)
    
    # Process the PDF
    organizations = processor.process_pdf()
    
    if organizations:
        print(f"✅ Successfully extracted {len(organizations)} organizations")
        
        # Save extracted data
        data_file = processor.save_extracted_data()
        
        # Generate report
        report = processor.generate_extraction_report()
        
        print(f"\n📊 Extraction Summary:")
        print(f"   • Total Organizations: {report['total_organizations_extracted']}")
        print(f"   • With Locations: {report['extraction_summary']['organizations_with_locations']}")
        print(f"   • With Accreditation Numbers: {report['extraction_summary']['organizations_with_accreditation_numbers']}")
        print(f"   • With Validity Dates: {report['extraction_summary']['organizations_with_validity_dates']}")
        
        print(f"\n📄 Files Generated:")
        print(f"   • Extracted Data: {data_file}")
        print(f"   • Extraction Report: nabl_pdf_extraction_report_*.json")
        print(f"   • Raw Text: nabl_pdf_extracted_text.txt")
        
        # Show sample organizations
        if organizations:
            print(f"\n🏥 Sample Organizations:")
            for i, org in enumerate(organizations[:3], 1):
                print(f"   {i}. {org['organization_name']}")
                if org['locations']:
                    print(f"      📍 Location: {', '.join(org['locations'])}")
                if org['accreditation_number']:
                    print(f"      🏆 Accreditation: {org['accreditation_number']}")
        
    else:
        print("❌ No organizations extracted from PDF")
        print("Please check the PDF file format and content")
    
    print("\n" + "=" * 50)
    print("🎉 NABL PDF Processing Complete!")

if __name__ == "__main__":
    main()