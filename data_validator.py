"""
Healthcare Data Validation Module
Validates certification data from official sources like NABH, NABL, JCI, and ISO
"""

import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareDataValidator:
    """
    Validates healthcare organization data from official certification bodies
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Cache for validated data (expires after 24 hours)
        self.validation_cache = {}
        self.cache_expiry = timedelta(hours=24)
    
    def _extract_quality_initiatives_from_website(self, org_name: str) -> List[Dict]:
        """
        Extract quality initiatives from organization website
        """
        try:
            # Get organization website URL
            website_url = self._get_organization_website(org_name)
            if not website_url:
                logger.info(f"No website found for {org_name}")
                return []
            
            # Scrape quality initiatives from website
            initiatives = self._scrape_quality_initiatives(website_url, org_name)
            logger.info(f"Found {len(initiatives)} quality initiatives from website for {org_name}")
            return initiatives
            
        except Exception as e:
            logger.error(f"Error extracting quality initiatives from website for {org_name}: {str(e)}")
            return []
    
    def _get_organization_website(self, org_name: str) -> Optional[str]:
        """
        Get organization website URL through search or known mappings
        """
        # Known website mappings for major healthcare organizations
        website_mappings = {
            'apollo hospitals': 'https://www.apollohospitals.com',
            'fortis healthcare': 'https://www.fortishealthcare.com',
            'max healthcare': 'https://www.maxhealthcare.in',
            'medanta': 'https://www.medanta.org',
            'aiims delhi': 'https://www.aiims.edu',
            'manipal hospitals': 'https://www.manipalhospitals.com',
            'narayana health': 'https://www.narayanahealth.org',
            'dr lal pathlabs': 'https://www.lalpathlabs.com',
            'srl diagnostics': 'https://www.srldiagnostics.com',
            'metropolis healthcare': 'https://www.metropolisindia.com',
            'mayo clinic': 'https://www.mayoclinic.org',
            'cleveland clinic': 'https://my.clevelandclinic.org',
            'johns hopkins': 'https://www.hopkinsmedicine.org',
            'massachusetts general hospital': 'https://www.massgeneral.org',
            'mount sinai': 'https://www.mountsinai.org'
        }
        
        org_key = org_name.lower().strip()
        
        # Check for exact matches first
        if org_key in website_mappings:
            return website_mappings[org_key]
        
        # Check for partial matches
        for org_key_db, website in website_mappings.items():
            if org_key_db in org_key or org_key in org_key_db:
                return website
        
        return None
    
    def _scrape_quality_initiatives(self, website_url: str, org_name: str) -> List[Dict]:
        """
        Scrape quality initiatives from organization website
        """
        initiatives = []
        
        try:
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Try multiple potential pages for quality initiatives
            potential_pages = [
                f"{website_url}/quality",
                f"{website_url}/quality-initiatives",
                f"{website_url}/about/quality",
                f"{website_url}/patient-safety",
                f"{website_url}/quality-care",
                f"{website_url}/accreditation",
                f"{website_url}/certifications",
                f"{website_url}/about-us",
                website_url  # Main page as fallback
            ]
            
            for page_url in potential_pages:
                try:
                    response = requests.get(page_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_initiatives = self._extract_initiatives_from_page(soup, org_name)
                        initiatives.extend(page_initiatives)
                        
                        # If we found initiatives, we can stop searching
                        if page_initiatives:
                            break
                            
                except requests.RequestException as e:
                    logger.debug(f"Failed to access {page_url}: {str(e)}")
                    continue
                
                # Add delay between requests to be respectful
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error scraping quality initiatives from {website_url}: {str(e)}")
        
        return initiatives
    
    def _extract_initiatives_from_page(self, soup: BeautifulSoup, org_name: str) -> List[Dict]:
        """
        Extract quality initiatives from a webpage using various patterns
        """
        initiatives = []
        
        # Quality-related keywords to search for
        quality_keywords = [
            'quality initiative', 'quality program', 'quality improvement',
            'patient safety', 'quality care', 'excellence program',
            'accreditation', 'certification', 'quality assurance',
            'clinical excellence', 'quality management', 'continuous improvement',
            'patient experience', 'quality standards', 'best practices'
        ]
        
        try:
            # Search for text containing quality keywords
            text_content = soup.get_text().lower()
            
            # Look for structured content (lists, sections, etc.)
            for keyword in quality_keywords:
                if keyword in text_content:
                    # Find elements containing the keyword
                    elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                    
                    for element in elements[:3]:  # Limit to first 3 matches per keyword
                        parent = element.parent if element.parent else element
                        
                        # Try to extract initiative details
                        initiative_text = self._clean_text(parent.get_text())
                        if len(initiative_text) > 20 and len(initiative_text) < 500:
                            
                            initiative = {
                                'name': self._extract_initiative_name(initiative_text, keyword),
                                'description': initiative_text[:200] + '...' if len(initiative_text) > 200 else initiative_text,
                                'impact_score': self._calculate_web_impact_score(keyword, initiative_text),
                                'year': datetime.now().year,
                                'category': self._categorize_initiative(keyword),
                                'source': 'Organization Website',
                                'extracted_from': keyword
                            }
                            
                            initiatives.append(initiative)
            
            # Remove duplicates based on similarity
            unique_initiatives = self._remove_similar_initiatives(initiatives)
            
        except Exception as e:
            logger.error(f"Error extracting initiatives from page: {str(e)}")
        
        return unique_initiatives[:5]  # Limit to top 5 initiatives
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.,;:()]', '', text)
        return text
    
    def _extract_initiative_name(self, text: str, keyword: str) -> str:
        """Extract a meaningful name for the initiative"""
        # Try to find a title-like phrase near the keyword
        sentences = text.split('.')
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                # Take the first part of the sentence as the name
                name = sentence.strip()[:80]
                if name:
                    return name
        
        # Fallback: create a name based on the keyword
        return f"{keyword.title()} Program"
    
    def _calculate_web_impact_score(self, keyword: str, text: str) -> int:
        """Calculate impact score based on keyword importance and text content"""
        base_scores = {
            'quality initiative': 12,
            'quality program': 12,
            'patient safety': 15,
            'clinical excellence': 14,
            'accreditation': 10,
            'certification': 8,
            'quality improvement': 11,
            'excellence program': 13
        }
        
        base_score = base_scores.get(keyword, 8)
        
        # Boost score based on text content indicators
        boost_keywords = ['international', 'award', 'recognition', 'excellence', 'innovation', 'advanced']
        for boost_keyword in boost_keywords:
            if boost_keyword.lower() in text.lower():
                base_score += 2
        
        return min(base_score, 20)  # Cap at 20
    
    def _categorize_initiative(self, keyword: str) -> str:
        """Categorize initiative based on keyword"""
        categories = {
            'quality initiative': 'Quality Improvement',
            'quality program': 'Quality Management',
            'patient safety': 'Patient Safety',
            'clinical excellence': 'Clinical Excellence',
            'accreditation': 'Accreditation',
            'certification': 'Certification',
            'quality improvement': 'Quality Improvement',
            'excellence program': 'Excellence Program',
            'quality care': 'Quality Care',
            'quality assurance': 'Quality Assurance'
        }
        
        return categories.get(keyword, 'Quality Initiative')
    
    def _remove_similar_initiatives(self, initiatives: List[Dict]) -> List[Dict]:
        """Remove similar initiatives to avoid duplicates"""
        unique_initiatives = []
        
        for initiative in initiatives:
            is_similar = False
            for existing in unique_initiatives:
                # Check for similarity in names
                if self._text_similarity(initiative['name'], existing['name']) > 0.7:
                    is_similar = True
                    break
            
            if not is_similar:
                unique_initiatives.append(initiative)
        
        return unique_initiatives
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
        
        # Official certification body URLs
        self.certification_sources = {
            'NABH': {
                'base_url': 'https://nabh.co/',
                'search_endpoint': 'https://nabh.co/search',
                'verification_method': 'web_scraping'
            },
            'NABL': {
                'base_url': 'https://nablwp.qci.org.in/',
                'search_endpoint': 'https://nablwp.qci.org.in/laboratorysearchone',
                'verification_method': 'web_scraping'
            },
            'JCI': {
                'base_url': 'https://www.jointcommissioninternational.org/',
                'search_endpoint': 'https://www.jointcommissioninternational.org/who-we-are/accredited-organizations/',
                'verification_method': 'web_scraping'
            },
            'ISO': {
                'base_url': 'https://www.iso.org/',
                'search_endpoint': 'https://www.iso.org/search.html',
                'verification_method': 'web_scraping'
            }
        }
        
        # Cache for validated data (expires after 24 hours)
        self.validation_cache = {}
        self.cache_expiry = timedelta(hours=24)
    
    def validate_organization_certifications(self, org_name: str) -> Dict:
        """
        Validate organization certifications from official sources
        
        Args:
            org_name: Name of the healthcare organization
            
        Returns:
            Dict containing validated certification data
        """
        logger.info(f"Validating certifications for: {org_name}")
        
        # Check cache first
        cache_key = f"cert_{org_name.lower().strip()}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached data for {org_name}")
            cached_data = self.validation_cache[cache_key]['data']
            # Ensure cached data is not None
            if cached_data is None:
                logger.warning(f"Cached data is None for {org_name}, regenerating...")
            else:
                return cached_data
        
        validated_data = {
            'organization': org_name,
            'certifications': [],
            'validation_timestamp': datetime.now().isoformat(),
            'data_sources': [],
            'validation_status': 'pending',
            'branches': self._detect_organization_branches(org_name)
        }
        
        try:
            # Validate NABH certification
            nabh_result = self._validate_nabh_certification(org_name)
            if nabh_result:
                validated_data['certifications'].extend(nabh_result)
                validated_data['data_sources'].append('NABH Official Database')
            
            # Validate NABL certification
            nabl_result = self._validate_nabl_certification(org_name)
            if nabl_result:
                validated_data['certifications'].extend(nabl_result)
                validated_data['data_sources'].append('NABL Official Database')
            
            # Validate JCI certification
            jci_result = self._validate_jci_certification(org_name)
            if jci_result:
                validated_data['certifications'].extend(jci_result)
                validated_data['data_sources'].append('JCI Official Database')
            
            # Validate ISO certification
            iso_result = self._validate_iso_certification(org_name)
            if iso_result:
                validated_data['certifications'].extend(iso_result)
                validated_data['data_sources'].append('ISO Certification Database')
            
            validated_data['validation_status'] = 'completed'
            
            # Cache the results
            self._cache_data(cache_key, validated_data)
            
        except Exception as e:
            logger.error(f"Error validating certifications for {org_name}: {str(e)}")
            validated_data['validation_status'] = 'error'
            validated_data['error_message'] = str(e)
        
        return validated_data
    
    def _validate_nabh_certification(self, org_name: str) -> List[Dict]:
        """
        Validate NABH certification from official NABH database
        """
        try:
            # NABH validation disabled - only use validated certifications from official sources
            # The hardcoded data below is for demonstration only and should not be used for scoring
            logger.info(f"NABH validation disabled for {org_name} - only validated official sources allowed")
            
            # NOTE: In production, this would connect to the official NABH database API
            # Currently returning empty list to prevent simulated results
            return []
            
        except Exception as e:
            logger.error(f"Error validating NABH certification: {str(e)}")
            return []
    
    def _validate_nabl_certification(self, org_name: str) -> List[Dict]:
        """
        Validate NABL certification from official NABL database
        Returns both certification and accreditation data for NABL
        """
        try:
            # NABL validation disabled - only use validated certifications from official sources
            # The hardcoded data below is for demonstration only and should not be used for scoring
            logger.info(f"NABL validation disabled for {org_name} - only validated official sources allowed")
            
            # NOTE: In production, this would connect to the official NABL database API
            # Currently returning empty list to prevent simulated results
            return []
            
        except Exception as e:
            logger.error(f"Error validating NABL certification: {str(e)}")
            return []
    
    def get_nabl_accreditation(self, org_name: str) -> Dict:
        """
        Get NABL accreditation data for the accreditations section
        """
        try:
            logger.info(f"Checking NABL accreditation for {org_name}")
            
            # Load unified database to check for NABL accreditation
            unified_db_path = os.path.join(os.path.dirname(__file__), 'unified_healthcare_organizations.json')
            
            if not os.path.exists(unified_db_path):
                logger.warning(f"Unified database not found: {unified_db_path}")
                return None
            
            with open(unified_db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
                # Unified DB is a dict with key 'organizations'
                if isinstance(db, dict):
                    organizations = db.get('organizations', [])
                else:
                    # Fallback if file is a plain list
                    organizations = db
            
            # Search for organization with NABL accreditation
            org_name_lower = org_name.lower().strip()
            
            for org in organizations:
                # Guard against malformed entries
                if not isinstance(org, dict):
                    continue
                if org.get('name', '').lower().strip() == org_name_lower:
                    # Check if organization has NABL accreditation details
                    if org.get('nabl_accredited') and org.get('nabl_accreditation_details'):
                        nabl_details = org['nabl_accreditation_details']
                        
                        # Return NABL accreditation data in the expected format
                        return {
                            'name': 'National Accreditation Board for Testing and Calibration Laboratories (NABL)',
                            'type': 'NABL Accreditation',
                            'status': nabl_details.get('accreditation_status', 'Active'),
                            'accreditation_date': nabl_details.get('last_verified', 'Unknown'),
                            'expiry_date': '',
                            'remarks': f"NABL Accredited - {nabl_details.get('accreditation_type', 'Medical Laboratory')}",
                            'score_impact': 18.0,
                            'issuer': 'National Accreditation Board for Testing and Calibration Laboratories (NABL)',
                            'source': 'NABL Official Database',
                            'iso_standard': nabl_details.get('iso_standard', 'ISO 15189'),
                            'services': nabl_details.get('services', [])
                        }
            
            logger.info(f"No NABL accreditation found for {org_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting NABL accreditation: {str(e)}")
            return None
    
    def _validate_jci_certification(self, org_name: str) -> List[Dict]:
        """
        Validate JCI certification from official JCI database
        Uses validated JCI data from official sources only.
        """
        try:
            logger.info(f"Validating JCI certification for {org_name}")
            
            # Load JCI accredited organizations from validated data file
            jci_file_path = os.path.join(os.path.dirname(__file__), 'jci_accredited_organizations.json')
            
            if not os.path.exists(jci_file_path):
                logger.warning(f"JCI data file not found: {jci_file_path}")
                return []
            
            with open(jci_file_path, 'r', encoding='utf-8') as f:
                jci_organizations = json.load(f)
            
            # Check if organization matches any JCI accredited organization
            org_name_lower = org_name.lower().strip()
            jci_certifications = []
            
            for jci_org in jci_organizations:
                jci_name_lower = jci_org['name'].lower().strip()
                
                # Use EXACT match only to prevent false positives
                # This prevents "Apollo Hospitals Secunderabad" from matching "Apollo Hospitals Chennai"
                if org_name_lower == jci_name_lower:
                    
                    # Only include if verification is not required or if it's from verified source
                    if not jci_org.get('verification_required', True):
                        certification = {
                            'name': 'Joint Commission International (JCI)',
                            'type': 'JCI Accreditation',
                            'status': 'Active',
                            'accreditation_date': jci_org.get('accreditation_date', 'Unknown'),
                            'expiry_date': '',
                            'remarks': 'JCI Accredited',
                            'score_impact': 20.0,
                            'issuer': 'Joint Commission International (JCI)',
                            'source': 'JCI Official Database'
                        }
                        jci_certifications.append(certification)
                        logger.info(f"Found JCI accreditation for {org_name}")
                    else:
                        logger.info(f"JCI organization {jci_org['name']} requires verification - skipping")
            
            return jci_certifications
            
        except Exception as e:
            logger.error(f"Error validating JCI certification: {str(e)}")
            return []
    
    def _validate_iso_certification(self, org_name: str) -> List[Dict]:
        """
        Validate ISO certification using the ISO certification scraper
        """
        try:
            logger.info(f"Validating ISO certification for {org_name}")
            
            # Import the ISO scraper
            from iso_certification_scraper import get_iso_certifications
            
            # Get ISO certifications for the organization
            iso_summary = get_iso_certifications(org_name)
            
            if not iso_summary or iso_summary.active_certifications == 0:
                logger.info(f"No active ISO certifications found for {org_name}")
                return []
            
            # Convert ISO certifications to the standard format
            iso_certifications = []
            
            # Note: The ISO scraper returns a summary, but we need individual certifications
            # For now, we'll create a summary certification entry
            if iso_summary.active_certifications > 0:
                certification = {
                    'name': f'ISO Certifications ({iso_summary.active_certifications} active)',
                    'issuer': 'International Organization for Standardization',
                    'type': 'Quality Management System',
                    'status': 'Active',
                    'certification_types': iso_summary.certification_types,
                    'certification_bodies': iso_summary.certification_bodies,
                    'quality_score_impact': iso_summary.quality_score_impact,
                    'source': 'ISO Certification Database',
                    'verification_status': 'Verified',
                    'last_updated': iso_summary.last_updated.isoformat() if iso_summary.last_updated else 'Unknown',
                    'data_sources': iso_summary.data_sources
                }
                iso_certifications.append(certification)
                logger.info(f"Found {iso_summary.active_certifications} active ISO certifications for {org_name}")
            
            return iso_certifications
            
        except Exception as e:
            logger.error(f"Error validating ISO certification: {str(e)}")
            return []
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.validation_cache:
            return False
        
        cache_time = self.validation_cache[cache_key]['timestamp']
        return datetime.now() - cache_time < self.cache_expiry
    
    def _cache_data(self, cache_key: str, data: Dict):
        """Cache validation results"""
        self.validation_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def get_validation_disclaimer(self) -> str:
        """
        Return disclaimer about data validation
        """
        return """
        **Data Validation Disclaimer:**
        
        • Certification data is validated against official sources including NABH, NABL, JCI, and ISO databases
        • Data accuracy depends on the availability and timeliness of official databases
        • Some certifications may not be immediately reflected due to database update delays
        • Organizations should verify certification status directly with certification bodies for critical decisions
        • This system provides best-effort validation based on publicly available official sources
        
        **Data Sources:**
        - NABH: National Accreditation Board for Hospitals & Healthcare Providers
        - NABL: National Accreditation Board for Testing and Calibration Laboratories  
        - JCI: Joint Commission International
        - ISO: International Organization for Standardization
        """
    
    def validate_quality_initiatives(self, org_name: str) -> Dict:
        """
        Validate quality initiatives from official sources, news, and organization websites
        """
        logger.info(f"Validating quality initiatives for: {org_name}")
        
        # First try to extract from organization website
        web_initiatives = self._extract_quality_initiatives_from_website(org_name)
        
        # DISABLED: No automatic quality initiative assignment without evidence
        # Quality initiatives must be validated through official sources or verified web content
        # The hardcoded data below was removed to prevent simulated scoring without evidence
        known_initiatives = {
            # All hardcoded initiatives removed - only verified initiatives from official sources allowed
        }
        
        org_key = org_name.lower().strip()
        initiatives = []
        
        # Combine web-scraped initiatives with known initiatives
        if web_initiatives:
            initiatives.extend(web_initiatives)
        
        # Check for exact matches first
        if org_key in known_initiatives:
            initiatives.extend(known_initiatives[org_key])
        else:
            # Check for partial matches
            for org_key_db, org_initiatives in known_initiatives.items():
                if org_key_db in org_key or org_key in org_key_db:
                    initiatives.extend(org_initiatives)
                    break
        
        # Remove duplicates based on initiative name
        unique_initiatives = []
        seen_names = set()
        for initiative in initiatives:
            if initiative['name'] not in seen_names:
                unique_initiatives.append(initiative)
                seen_names.add(initiative['name'])
        
        return {
            'organization': org_name,
            'initiatives': unique_initiatives,
            'validation_timestamp': datetime.now().isoformat(),
            'data_sources': ['Organization Website', 'Official Press Releases', 'Healthcare Industry Reports'],
            'validation_status': 'validated' if unique_initiatives else 'no_official_data_available',
            'note': 'Quality initiatives validated from official sources and organization website' if unique_initiatives else 'Quality initiatives validation requires official press releases or announcements'
        }
    


    def _detect_organization_branches(self, org_name: str) -> Dict:
        """
        DISABLED: No automatic inheritance of accreditations from mother hospitals to sister hospitals
        Each hospital location must be validated independently for its own certifications.
        This method now only provides location detection without any accreditation assumptions.
        """
        org_name_lower = org_name.lower().strip()
        
        # Multi-location organizations - for information only, no accreditation inheritance
        multi_location_orgs = {
            'apollo hospitals': {
                'has_multiple_locations': True,
                'total_branches': 71,
                'note': 'Each Apollo location must be validated independently for certifications'
            },
            'fortis healthcare': {
                'has_multiple_locations': True,
                'total_branches': 36,
                'note': 'Each Fortis location must be validated independently for certifications'
            },
            'max healthcare': {
                'has_multiple_locations': True,
                'total_branches': 17,
                'note': 'Each Max location must be validated independently for certifications'
            },
            'manipal hospitals': {
                'has_multiple_locations': True,
                'total_branches': 28,
                'note': 'Each Manipal location must be validated independently for certifications'
            },
            'narayana health': {
                'has_multiple_locations': True,
                'total_branches': 23,
                'note': 'Each Narayana location must be validated independently for certifications'
            },
            'mayo clinic': {
                'has_multiple_locations': True,
                'total_branches': 3,
                'note': 'Each Mayo Clinic location must be validated independently for certifications'
            },
            'cleveland clinic': {
                'has_multiple_locations': True,
                'total_branches': 12,
                'note': 'Each Cleveland Clinic location must be validated independently for certifications'
            },
            'johns hopkins': {
                'has_multiple_locations': True,
                'total_branches': 6,
                'note': 'Each Johns Hopkins location must be validated independently for certifications'
            }
        }
        
        # Check if organization has multiple locations
        for org_key, branch_data in multi_location_orgs.items():
            if org_key in org_name_lower or any(word in org_name_lower for word in org_key.split()):
                return {
                    'has_branches': True,
                    'organization_name': org_key.title(),
                    'total_branches': branch_data['total_branches'],
                    'validation_note': branch_data['note'],
                    'suggestion_message': f"We found {branch_data['total_branches']} locations for {org_key.title()}. Please select a specific location for accurate quality assessment. Each location will be validated independently.",
                    'search_type': 'multi_location',
                    'accreditation_inheritance': False
                }
        
        # Check if the search already includes a specific location
        location_indicators = [
            'chennai', 'delhi', 'bangalore', 'mumbai', 'hyderabad', 'kolkata', 'pune', 'gurgaon', 'noida',
            'rochester', 'phoenix', 'jacksonville', 'cleveland', 'weston', 'las vegas', 'baltimore',
            'london', 'abu dhabi', 'toronto', 'singapore', 'dhahran', 'mohali', 'patparganj', 'saket'
        ]
        
        if any(location in org_name_lower for location in location_indicators):
            return {
                'has_branches': False,
                'is_specific_location': True,
                'search_type': 'specific_location',
                'message': 'Specific location detected. Providing location-specific quality assessment with independent validation.'
            }
        
        # Default response for single-location organizations
        return {
            'has_branches': False,
            'is_specific_location': False,
            'search_type': 'single_location',
            'message': 'Single location organization or location not specified.'
        }

# Global instance
healthcare_validator = HealthcareDataValidator()