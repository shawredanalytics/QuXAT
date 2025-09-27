"""
Excel Data Processor for QuXAT Healthcare Quality Grid
This module handles Excel file uploads, data validation, and integration with the QuXAT scoring system.
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import re
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelDataProcessor:
    """
    Processes Excel files containing healthcare organization data for QuXAT system integration
    """
    
    def __init__(self):
        self.required_columns = {
            'name': ['name', 'organization_name', 'hospital_name', 'facility_name'],
            'country': ['country', 'nation', 'location_country'],
            'city': ['city', 'location_city', 'location'],
            'state': ['state', 'province', 'region', 'location_state'],
            'hospital_type': ['hospital_type', 'facility_type', 'type', 'category']
        }
        
        self.optional_columns = {
            'certifications': ['certifications', 'accreditations', 'quality_certifications'],
            'website': ['website', 'url', 'web_address'],
            'phone': ['phone', 'telephone', 'contact_number'],
            'email': ['email', 'contact_email', 'email_address'],
            'established_year': ['established_year', 'founded_year', 'year_established'],
            'bed_count': ['bed_count', 'beds', 'number_of_beds'],
            'specialties': ['specialties', 'medical_specialties', 'departments']
        }
        
        # Certification mapping for standardization
        self.certification_mapping = {
            'jci': 'Joint Commission International (JCI)',
            'joint commission international': 'Joint Commission International (JCI)',
            'nabh': 'National Accreditation Board for Hospitals & Healthcare Providers (NABH)',
            'nabl': 'National Accreditation Board for Testing and Calibration Laboratories (NABL)',
            'iso 9001': 'ISO 9001',
            'iso 14001': 'ISO 14001',
            'iso 45001': 'ISO 45001',
            'iso 15189': 'ISO 15189',
            'iso 13485': 'ISO 13485',
            'cap': 'College of American Pathologists (CAP)',
            'clia': 'Clinical Laboratory Improvement Amendments (CLIA)',
            'magnet': 'Magnet Recognition Program'
        }
        
        # Hospital type standardization
        self.hospital_type_mapping = {
            'general': 'General Hospital',
            'specialty': 'Specialty Hospital',
            'teaching': 'Academic Medical Center',
            'academic': 'Academic Medical Center',
            'private': 'Private Hospital',
            'public': 'Public Hospital',
            'government': 'Government Hospital',
            'multi-specialty': 'Multi-Specialty Hospital',
            'super specialty': 'Super Specialty Hospital',
            'clinic': 'Medical Clinic',
            'medical center': 'Medical Center',
            'hospital network': 'Hospital Network'
        }
    
    def validate_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate Excel file structure and content
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'file_info': {},
            'column_mapping': {},
            'preview_data': None
        }
        
        try:
            # Check file existence and extension
            if not os.path.exists(file_path):
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            if not file_path.lower().endswith(('.xlsx', '.xls', '.csv')):
                validation_result['errors'].append("File must be Excel (.xlsx, .xls) or CSV format")
                return validation_result
            
            # Read file
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Basic file info
            validation_result['file_info'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
            }
            
            # Check minimum requirements
            if len(df) == 0:
                validation_result['errors'].append("File is empty")
                return validation_result
            
            if len(df.columns) < 2:
                validation_result['errors'].append("File must have at least 2 columns")
                return validation_result
            
            # Map columns to required fields
            column_mapping = self._map_columns(df.columns)
            validation_result['column_mapping'] = column_mapping
            
            # Check for required columns
            missing_required = []
            for required_field, possible_names in self.required_columns.items():
                if required_field not in column_mapping:
                    missing_required.append(f"{required_field} (looking for: {', '.join(possible_names)})")
            
            if missing_required:
                validation_result['errors'].append(f"Missing required columns: {', '.join(missing_required)}")
            
            # Data quality checks
            if 'name' in column_mapping:
                name_col = column_mapping['name']
                empty_names = df[name_col].isna().sum()
                if empty_names > 0:
                    validation_result['warnings'].append(f"{empty_names} rows have empty organization names")
                
                duplicate_names = df[name_col].duplicated().sum()
                if duplicate_names > 0:
                    validation_result['warnings'].append(f"{duplicate_names} duplicate organization names found")
            
            # Preview data (first 5 rows)
            validation_result['preview_data'] = df.head().to_dict('records')
            
            # Mark as valid if no errors
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Error reading file: {str(e)}")
            logger.error(f"File validation error: {e}")
        
        return validation_result
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Map Excel columns to required fields
        
        Args:
            columns: List of column names from Excel file
            
        Returns:
            Dictionary mapping field names to column names
        """
        column_mapping = {}
        columns_lower = [col.lower().strip() for col in columns]
        
        # Map required columns
        for field, possible_names in self.required_columns.items():
            for possible_name in possible_names:
                if possible_name.lower() in columns_lower:
                    original_col = columns[columns_lower.index(possible_name.lower())]
                    column_mapping[field] = original_col
                    break
        
        # Map optional columns
        for field, possible_names in self.optional_columns.items():
            for possible_name in possible_names:
                if possible_name.lower() in columns_lower:
                    original_col = columns[columns_lower.index(possible_name.lower())]
                    column_mapping[field] = original_col
                    break
        
        return column_mapping
    
    def process_excel_data(self, file_path: str, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Excel data and convert to QuXAT format
        
        Args:
            file_path: Path to Excel file
            validation_result: Result from validate_excel_file
            
        Returns:
            Dictionary with processed data and statistics
        """
        processing_result = {
            'success': False,
            'organizations': [],
            'statistics': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            if not validation_result['is_valid']:
                processing_result['errors'].append("Cannot process invalid file")
                return processing_result
            
            # Read file
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            column_mapping = validation_result['column_mapping']
            organizations = []
            
            for index, row in df.iterrows():
                try:
                    org_data = self._process_organization_row(row, column_mapping, index)
                    if org_data:
                        organizations.append(org_data)
                except Exception as e:
                    processing_result['warnings'].append(f"Error processing row {index + 1}: {str(e)}")
                    continue
            
            processing_result['organizations'] = organizations
            processing_result['statistics'] = {
                'total_rows_processed': len(df),
                'organizations_created': len(organizations),
                'success_rate': round((len(organizations) / len(df)) * 100, 2) if len(df) > 0 else 0,
                'countries': list(set([org.get('country', 'Unknown') for org in organizations])),
                'hospital_types': list(set([org.get('hospital_type', 'Unknown') for org in organizations])),
                'with_certifications': len([org for org in organizations if org.get('certifications', [])]),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            processing_result['success'] = True
            
        except Exception as e:
            processing_result['errors'].append(f"Processing error: {str(e)}")
            logger.error(f"Data processing error: {e}")
        
        return processing_result
    
    def _process_organization_row(self, row: pd.Series, column_mapping: Dict[str, str], row_index: int) -> Optional[Dict[str, Any]]:
        """
        Process a single organization row
        
        Args:
            row: Pandas Series representing a row
            column_mapping: Column mapping dictionary
            row_index: Row index for error reporting
            
        Returns:
            Organization dictionary or None if invalid
        """
        # Check if name is present and valid
        if 'name' not in column_mapping:
            return None
        
        name = str(row[column_mapping['name']]).strip()
        if pd.isna(row[column_mapping['name']]) or not name or name.lower() == 'nan':
            return None
        
        # Build organization data
        org_data = {
            'name': name,
            'original_name': name,
            'data_source': 'Excel Upload',
            'last_updated': datetime.now().isoformat(),
            'quality_indicators': {
                'excel_imported': True,
                'data_verified': False
            }
        }
        
        # Add required fields
        for field in ['country', 'city', 'state', 'hospital_type']:
            if field in column_mapping:
                value = row[column_mapping[field]]
                if pd.notna(value):
                    if field == 'hospital_type':
                        org_data[field] = self._standardize_hospital_type(str(value))
                    else:
                        org_data[field] = str(value).strip()
                else:
                    org_data[field] = ''
            else:
                org_data[field] = ''
        
        # Add optional fields
        for field in ['website', 'phone', 'email', 'established_year', 'bed_count', 'specialties']:
            if field in column_mapping:
                value = row[column_mapping[field]]
                if pd.notna(value):
                    if field == 'established_year':
                        try:
                            org_data[field] = int(float(str(value)))
                        except:
                            org_data[field] = None
                    elif field == 'bed_count':
                        try:
                            org_data[field] = int(float(str(value)))
                        except:
                            org_data[field] = None
                    elif field == 'specialties':
                        org_data[field] = [s.strip() for s in str(value).split(',') if s.strip()]
                    else:
                        org_data[field] = str(value).strip()
        
        # Process certifications
        org_data['certifications'] = self._process_certifications(row, column_mapping)
        
        return org_data
    
    def _process_certifications(self, row: pd.Series, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Process certification data from row
        
        Args:
            row: Pandas Series representing a row
            column_mapping: Column mapping dictionary
            
        Returns:
            List of certification dictionaries
        """
        certifications = []
        
        if 'certifications' in column_mapping:
            cert_value = row[column_mapping['certifications']]
            if pd.notna(cert_value):
                cert_text = str(cert_value).strip()
                if cert_text:
                    # Split by common delimiters
                    cert_names = re.split(r'[,;|]', cert_text)
                    
                    for cert_name in cert_names:
                        cert_name = cert_name.strip()
                        if cert_name:
                            standardized_name = self._standardize_certification_name(cert_name)
                            if standardized_name:
                                certification = {
                                    'name': standardized_name,
                                    'type': self._get_certification_type(standardized_name),
                                    'status': 'Active',  # Default to Active
                                    'source': 'Excel Upload',
                                    'accreditation_date': '',
                                    'expiry_date': '',
                                    'remarks': f'Imported from Excel: {cert_name}',
                                    'score_impact': self._get_certification_score_impact(standardized_name)
                                }
                                certifications.append(certification)
        
        return certifications
    
    def _standardize_certification_name(self, cert_name: str) -> Optional[str]:
        """
        Standardize certification name
        
        Args:
            cert_name: Raw certification name
            
        Returns:
            Standardized certification name or None
        """
        cert_lower = cert_name.lower().strip()
        
        # Direct mapping
        if cert_lower in self.certification_mapping:
            return self.certification_mapping[cert_lower]
        
        # Partial matching
        for key, value in self.certification_mapping.items():
            if key in cert_lower or cert_lower in key:
                return value
        
        # Return original if no mapping found
        return cert_name.strip()
    
    def _get_certification_type(self, cert_name: str) -> str:
        """
        Get certification type based on name
        
        Args:
            cert_name: Certification name
            
        Returns:
            Certification type
        """
        cert_lower = cert_name.lower()
        
        if 'jci' in cert_lower or 'joint commission' in cert_lower:
            return 'JCI Accreditation'
        elif 'nabh' in cert_lower:
            return 'NABH Accreditation'
        elif 'nabl' in cert_lower:
            return 'NABL Accreditation'
        elif 'iso' in cert_lower:
            return 'ISO Certification'
        elif 'cap' in cert_lower:
            return 'CAP Accreditation'
        elif 'magnet' in cert_lower:
            return 'Magnet Recognition'
        else:
            return 'Healthcare Accreditation'
    
    def _get_certification_score_impact(self, cert_name: str) -> float:
        """
        Get score impact for certification
        
        Args:
            cert_name: Certification name
            
        Returns:
            Score impact value
        """
        # Import certification weights from the main analyzer
        try:
            from streamlit_app import HealthcareOrgAnalyzer
            analyzer = HealthcareOrgAnalyzer()
            
            cert_lower = cert_name.lower()
            for key, score in analyzer.certification_weights.items():
                if key.lower() in cert_lower or cert_lower in key.lower():
                    return float(score)
        except:
            pass
        
        # Default scoring based on certification type
        cert_lower = cert_name.lower()
        if 'jci' in cert_lower:
            return 35.0
        elif 'nabh' in cert_lower:
            return 18.0
        elif 'nabl' in cert_lower:
            return 15.0
        elif 'iso 9001' in cert_lower:
            return 15.0
        elif 'iso' in cert_lower:
            return 10.0
        else:
            return 5.0
    
    def _standardize_hospital_type(self, hospital_type: str) -> str:
        """
        Standardize hospital type
        
        Args:
            hospital_type: Raw hospital type
            
        Returns:
            Standardized hospital type
        """
        type_lower = hospital_type.lower().strip()
        
        for key, value in self.hospital_type_mapping.items():
            if key in type_lower:
                return value
        
        return hospital_type.strip()
    
    def integrate_with_database(self, organizations: List[Dict[str, Any]], database_path: str = 'unified_healthcare_organizations.json') -> Dict[str, Any]:
        """
        Integrate processed organizations with existing database
        
        Args:
            organizations: List of processed organizations
            database_path: Path to existing database file
            
        Returns:
            Integration result dictionary
        """
        integration_result = {
            'success': False,
            'statistics': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load existing database
            existing_data = {'organizations': []}
            if os.path.exists(database_path):
                with open(database_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            existing_orgs = existing_data.get('organizations', [])
            
            # Track integration statistics
            new_orgs_added = 0
            existing_orgs_updated = 0
            duplicates_skipped = 0
            
            # Create name index for faster lookup
            existing_names = {org['name'].lower(): i for i, org in enumerate(existing_orgs)}
            
            for new_org in organizations:
                org_name_lower = new_org['name'].lower()
                
                if org_name_lower in existing_names:
                    # Update existing organization
                    existing_index = existing_names[org_name_lower]
                    existing_org = existing_orgs[existing_index]
                    
                    # Merge certifications
                    existing_certs = existing_org.get('certifications', [])
                    new_certs = new_org.get('certifications', [])
                    
                    # Add new certifications that don't exist
                    for new_cert in new_certs:
                        cert_exists = any(
                            existing_cert['name'].lower() == new_cert['name'].lower()
                            for existing_cert in existing_certs
                        )
                        if not cert_exists:
                            existing_certs.append(new_cert)
                    
                    existing_org['certifications'] = existing_certs
                    existing_org['last_updated'] = datetime.now().isoformat()
                    existing_org['quality_indicators']['excel_updated'] = True
                    
                    existing_orgs_updated += 1
                else:
                    # Add new organization
                    existing_orgs.append(new_org)
                    existing_names[org_name_lower] = len(existing_orgs) - 1
                    new_orgs_added += 1
            
            # Update metadata
            metadata = existing_data.get('metadata', {})
            metadata.update({
                'excel_integration_timestamp': datetime.now().isoformat(),
                'excel_integration_statistics': {
                    'new_organizations_added': new_orgs_added,
                    'existing_organizations_updated': existing_orgs_updated,
                    'duplicates_skipped': duplicates_skipped,
                    'total_organizations_processed': len(organizations)
                },
                'total_organizations': len(existing_orgs),
                'version': metadata.get('version', '1.0') + '_excel_updated'
            })
            
            # Add data source if not present
            data_sources = metadata.get('data_sources', [])
            if 'Excel Upload' not in data_sources:
                data_sources.append('Excel Upload')
            metadata['data_sources'] = data_sources
            
            # Save updated database
            updated_data = {
                'metadata': metadata,
                'organizations': existing_orgs
            }
            
            with open(database_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
            
            integration_result['statistics'] = {
                'new_organizations_added': new_orgs_added,
                'existing_organizations_updated': existing_orgs_updated,
                'duplicates_skipped': duplicates_skipped,
                'total_organizations_final': len(existing_orgs),
                'integration_timestamp': datetime.now().isoformat()
            }
            
            integration_result['success'] = True
            
        except Exception as e:
            integration_result['errors'].append(f"Integration error: {str(e)}")
            logger.error(f"Database integration error: {e}")
        
        return integration_result
    
    def generate_sample_template(self, output_path: str = 'healthcare_organizations_template.xlsx') -> bool:
        """
        Generate a sample Excel template for users
        
        Args:
            output_path: Path for the template file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sample data
            sample_data = {
                'name': [
                    'Apollo Hospital Delhi',
                    'Fortis Memorial Research Institute',
                    'Max Super Speciality Hospital'
                ],
                'country': ['India', 'India', 'India'],
                'city': ['Delhi', 'Gurgaon', 'Delhi'],
                'state': ['Delhi', 'Haryana', 'Delhi'],
                'hospital_type': ['Multi-Specialty Hospital', 'Academic Medical Center', 'Super Specialty Hospital'],
                'certifications': [
                    'JCI, NABH, ISO 9001',
                    'JCI, NABH, ISO 9001, ISO 14001',
                    'NABH, ISO 9001'
                ],
                'website': [
                    'https://www.apollohospitals.com',
                    'https://www.fortishealthcare.com',
                    'https://www.maxhealthcare.in'
                ],
                'bed_count': [500, 400, 350],
                'established_year': [1983, 1996, 2001],
                'specialties': [
                    'Cardiology, Oncology, Neurology',
                    'Cardiology, Orthopedics, Gastroenterology',
                    'Cardiology, Neurology, Oncology'
                ]
            }
            
            df = pd.DataFrame(sample_data)
            df.to_excel(output_path, index=False)
            
            logger.info(f"Sample template created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return False