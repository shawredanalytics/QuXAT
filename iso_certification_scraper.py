"""
ISO Certification Scraper for QuXAT Healthcare Quality Grid
This module scrapes ISO certification data from various sources including IAF CertSearch,
certification body databases, and official ISO registries for healthcare organizations.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from urllib.parse import quote_plus, urljoin
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ISOCertification:
    """Represents an ISO certification for a healthcare organization"""
    organization_name: str
    iso_standard: str  # e.g., 'ISO 9001:2015', 'ISO 14001:2015'
    standard_name: str  # e.g., 'Quality Management System'
    certification_body: str  # Name of the certification body
    certificate_number: str
    issue_date: datetime
    expiry_date: datetime
    scope: str  # Scope of certification
    status: str  # 'Valid', 'Expired', 'Suspended', 'Withdrawn'
    accreditation_body: str  # e.g., 'UKAS', 'ANAB', 'DAkkS'
    verification_source: str  # Source where data was verified
    last_verified: datetime
    confidence_score: float  # 0-1 based on source reliability

@dataclass
class ISOCertificationSummary:
    """Summary of all ISO certifications for an organization"""
    organization_name: str
    total_certifications: int
    active_certifications: int
    certification_types: List[str]
    certification_bodies: List[str]
    earliest_certification: Optional[datetime]
    latest_expiry: Optional[datetime]
    quality_score_impact: float  # Impact on overall quality score
    last_updated: datetime
    data_sources: List[str]

class ISOCertificationScraper:
    """Main class for scraping ISO certification data from multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Healthcare-relevant ISO standards
        self.healthcare_iso_standards = {
            'ISO 9001': 'Quality Management System',
            'ISO 14001': 'Environmental Management System',
            'ISO 45001': 'Occupational Health and Safety Management System',
            'ISO 27001': 'Information Security Management System',
            'ISO 13485': 'Medical Devices Quality Management System',
            'ISO 15189': 'Medical Laboratories Requirements',
            'ISO 22000': 'Food Safety Management System',
            'ISO 50001': 'Energy Management System',
            'ISO 27799': 'Health Informatics Security Management',
            'ISO 14155': 'Clinical Investigation of Medical Devices'
        }
        
        # Data sources for ISO certification verification
        self.data_sources = {
            'iaf_certsearch': {
                'name': 'IAF CertSearch',
                'url': 'https://www.iafcertsearch.org/',
                'reliability': 0.95,
                'method': 'api_simulation'  # Would be API in production
            },
            'certification_bodies': {
                'name': 'Certification Body Databases',
                'url': 'various',
                'reliability': 0.85,
                'method': 'web_scraping'
            },
            'iso_survey': {
                'name': 'ISO Survey Database',
                'url': 'https://www.iso.org/the-iso-survey.html',
                'reliability': 0.80,
                'method': 'data_extraction'
            }
        }
        
        # Cache for certification data
        self.certification_cache = {}
        self.cache_expiry = timedelta(hours=12)  # Shorter cache for certification data
    
    def get_organization_iso_certifications(self, org_name: str, location: str = "") -> ISOCertificationSummary:
        """
        Get all ISO certifications for a healthcare organization
        
        Args:
            org_name: Name of the healthcare organization
            location: Location to help with search accuracy
            
        Returns:
            ISOCertificationSummary with all found certifications
        """
        logger.info(f"Searching ISO certifications for: {org_name}")
        
        # Check cache first
        cache_key = f"iso_{org_name.lower().strip()}_{location.lower().strip()}"
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached ISO data for {org_name}")
            cached_data = self.certification_cache[cache_key]['data']
            # Ensure cached data is not None
            if cached_data is None:
                logger.warning(f"Cached ISO data is None for {org_name}, regenerating...")
            else:
                return cached_data
        
        all_certifications = []
        data_sources_used = []
        
        try:
            # Search IAF CertSearch database
            iaf_certs = self._search_iaf_certsearch(org_name, location)
            if iaf_certs:
                all_certifications.extend(iaf_certs)
                data_sources_used.append('IAF CertSearch')
            
            # Search certification body databases
            cb_certs = self._search_certification_bodies(org_name, location)
            if cb_certs:
                all_certifications.extend(cb_certs)
                data_sources_used.append('Certification Body Databases')
            
            # Search ISO survey data
            iso_survey_certs = self._search_iso_survey_data(org_name, location)
            if iso_survey_certs:
                all_certifications.extend(iso_survey_certs)
                data_sources_used.append('ISO Survey Database')
            
            # Remove duplicates and create summary
            unique_certifications = self._deduplicate_certifications(all_certifications)
            summary = self._create_certification_summary(org_name, unique_certifications, data_sources_used)
            
            # Cache the results
            self._cache_data(cache_key, summary)
            
            logger.info(f"Found {len(unique_certifications)} ISO certifications for {org_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Error searching ISO certifications for {org_name}: {str(e)}")
            return self._create_empty_summary(org_name)
    
    def _search_iaf_certsearch(self, org_name: str, location: str) -> List[ISOCertification]:
        """
        Search IAF CertSearch database for ISO certifications
        Note: In production, this would use the actual IAF CertSearch API
        """
        certifications = []
        
        try:
            logger.info(f"Searching IAF CertSearch for {org_name}")
            
            # Simulate IAF CertSearch API response
            # In production, this would make actual API calls to https://www.iafcertsearch.org/
            simulated_data = self._simulate_iaf_certsearch_data(org_name)
            
            for cert_data in simulated_data:
                certification = ISOCertification(
                    organization_name=org_name,
                    iso_standard=cert_data['standard'],
                    standard_name=self.healthcare_iso_standards.get(cert_data['standard'].split(':')[0], 'Unknown Standard'),
                    certification_body=cert_data['certification_body'],
                    certificate_number=cert_data['certificate_number'],
                    issue_date=cert_data['issue_date'],
                    expiry_date=cert_data['expiry_date'],
                    scope=cert_data['scope'],
                    status=cert_data['status'],
                    accreditation_body=cert_data['accreditation_body'],
                    verification_source='IAF CertSearch',
                    last_verified=datetime.now(),
                    confidence_score=0.95
                )
                certifications.append(certification)
            
        except Exception as e:
            logger.error(f"Error searching IAF CertSearch: {str(e)}")
        
        return certifications
    
    def _search_certification_bodies(self, org_name: str, location: str) -> List[ISOCertification]:
        """
        Search various certification body databases
        """
        certifications = []
        
        try:
            logger.info(f"Searching certification body databases for {org_name}")
            
            # Simulate certification body database searches
            # In production, this would scrape actual certification body websites
            simulated_data = self._simulate_certification_body_data(org_name)
            
            for cert_data in simulated_data:
                certification = ISOCertification(
                    organization_name=org_name,
                    iso_standard=cert_data['standard'],
                    standard_name=self.healthcare_iso_standards.get(cert_data['standard'].split(':')[0], 'Unknown Standard'),
                    certification_body=cert_data['certification_body'],
                    certificate_number=cert_data['certificate_number'],
                    issue_date=cert_data['issue_date'],
                    expiry_date=cert_data['expiry_date'],
                    scope=cert_data['scope'],
                    status=cert_data['status'],
                    accreditation_body=cert_data['accreditation_body'],
                    verification_source='Certification Body Database',
                    last_verified=datetime.now(),
                    confidence_score=0.85
                )
                certifications.append(certification)
            
        except Exception as e:
            logger.error(f"Error searching certification body databases: {str(e)}")
        
        return certifications
    
    def _search_iso_survey_data(self, org_name: str, location: str) -> List[ISOCertification]:
        """
        Search ISO survey data for organization certifications
        """
        certifications = []
        
        try:
            logger.info(f"Searching ISO survey data for {org_name}")
            
            # Simulate ISO survey data
            # In production, this would access actual ISO survey databases
            simulated_data = self._simulate_iso_survey_data(org_name)
            
            for cert_data in simulated_data:
                certification = ISOCertification(
                    organization_name=org_name,
                    iso_standard=cert_data['standard'],
                    standard_name=self.healthcare_iso_standards.get(cert_data['standard'].split(':')[0], 'Unknown Standard'),
                    certification_body=cert_data['certification_body'],
                    certificate_number=cert_data['certificate_number'],
                    issue_date=cert_data['issue_date'],
                    expiry_date=cert_data['expiry_date'],
                    scope=cert_data['scope'],
                    status=cert_data['status'],
                    accreditation_body=cert_data['accreditation_body'],
                    verification_source='ISO Survey Database',
                    last_verified=datetime.now(),
                    confidence_score=0.80
                )
                certifications.append(certification)
            
        except Exception as e:
            logger.error(f"Error searching ISO survey data: {str(e)}")
        
        return certifications
    
    def _simulate_iaf_certsearch_data(self, org_name: str) -> List[Dict]:
        """
        Simulate IAF CertSearch API response
        In production, this would be replaced with actual API calls
        """
        # DISABLED: Hardcoded ISO data that was causing automatic assignment
        # The hardcoded data below is for demonstration only and should not be used for scoring
        # Only validated certifications from official sources should be used
        
        # known_orgs = {
        #     'apollo hospitals': [...],
        #     'fortis healthcare': [...],
        #     'max healthcare': [...]
        # }
        
        # org_key = org_name.lower().strip()
        
        # Check for exact matches
        # if org_key in known_orgs:
        #     return known_orgs[org_key]
        
        # Check for partial matches
        # for hospital_key, certs in known_orgs.items():
        #     if hospital_key in org_key or org_key in hospital_key:
        #         return certs
        
        # Generate random certifications for demonstration
        # if random.random() < 0.3:  # 30% chance of having certifications
        #     return self._generate_random_certifications(org_name)
        
        return []
    
    def _simulate_certification_body_data(self, org_name: str) -> List[Dict]:
        """
        Simulate certification body database response
        """
        # DISABLED: Random certification generation that was causing automatic assignment
        # This would be replaced with actual web scraping in production
        # if random.random() < 0.2:  # 20% chance of additional certifications
        #     return self._generate_random_certifications(org_name, max_certs=2)
        return []
    
    def _simulate_iso_survey_data(self, org_name: str) -> List[Dict]:
        """
        Simulate ISO survey database response
        """
        # DISABLED: Random certification generation that was causing automatic assignment
        # This would be replaced with actual data extraction in production
        # if random.random() < 0.15:  # 15% chance of survey data
        #     return self._generate_random_certifications(org_name, max_certs=1)
        return []
    
    def _generate_random_certifications(self, org_name: str, max_certs: int = 3) -> List[Dict]:
        """
        Generate random ISO certifications for demonstration
        """
        standards = ['ISO 9001:2015', 'ISO 14001:2015', 'ISO 45001:2018', 'ISO 27001:2013']
        cert_bodies = ['Bureau Veritas', 'TUV SUD', 'DNV GL', 'BSI Group', 'SGS', 'Intertek']
        accred_bodies = ['NABCB', 'UKAS', 'ANAB', 'DAkkS']
        
        certifications = []
        num_certs = random.randint(1, max_certs)
        
        for i in range(num_certs):
            standard = random.choice(standards)
            cert_body = random.choice(cert_bodies)
            
            issue_date = datetime.now() - timedelta(days=random.randint(30, 1095))
            expiry_date = issue_date + timedelta(days=1095)  # 3 years validity
            
            certification = {
                'standard': standard,
                'certification_body': cert_body,
                'certificate_number': f'CERT-{random.randint(100000, 999999)}',
                'issue_date': issue_date,
                'expiry_date': expiry_date,
                'scope': f'Healthcare Services - {org_name}',
                'status': 'Valid' if expiry_date > datetime.now() else 'Expired',
                'accreditation_body': random.choice(accred_bodies)
            }
            certifications.append(certification)
        
        return certifications
    
    def _deduplicate_certifications(self, certifications: List[ISOCertification]) -> List[ISOCertification]:
        """
        Remove duplicate certifications based on standard and certificate number
        """
        seen = set()
        unique_certs = []
        
        for cert in certifications:
            key = (cert.iso_standard, cert.certificate_number)
            if key not in seen:
                seen.add(key)
                unique_certs.append(cert)
        
        return unique_certs
    
    def _create_certification_summary(self, org_name: str, certifications: List[ISOCertification], 
                                    data_sources: List[str]) -> ISOCertificationSummary:
        """
        Create a summary of all certifications for an organization
        """
        active_certs = [cert for cert in certifications if cert.status == 'Valid']
        cert_types = list(set([cert.iso_standard for cert in certifications]))
        cert_bodies = list(set([cert.certification_body for cert in certifications]))
        
        earliest_cert = min([cert.issue_date for cert in certifications]) if certifications else None
        latest_expiry = max([cert.expiry_date for cert in active_certs]) if active_certs else None
        
        # Calculate quality score impact based on certifications
        quality_impact = self._calculate_quality_score_impact(active_certs)
        
        return ISOCertificationSummary(
            organization_name=org_name,
            total_certifications=len(certifications),
            active_certifications=len(active_certs),
            certification_types=cert_types,
            certification_bodies=cert_bodies,
            earliest_certification=earliest_cert,
            latest_expiry=latest_expiry,
            quality_score_impact=quality_impact,
            last_updated=datetime.now(),
            data_sources=data_sources
        )
    
    def _calculate_quality_score_impact(self, active_certifications: List[ISOCertification]) -> float:
        """
        Calculate the impact of ISO certifications on quality score
        """
        if not active_certifications:
            return 0.0
        
        # Score weights for different ISO standards
        standard_weights = {
            'ISO 9001': 15.0,  # Quality Management - highest impact
            'ISO 13485': 12.0,  # Medical Devices - high impact for healthcare
            'ISO 27001': 10.0,  # Information Security - important for healthcare
            'ISO 45001': 8.0,   # Occupational Health & Safety
            'ISO 14001': 6.0,   # Environmental Management
            'ISO 15189': 10.0,  # Medical Laboratories
            'ISO 22000': 5.0,   # Food Safety
            'ISO 50001': 4.0,   # Energy Management
            'ISO 27799': 8.0,   # Health Informatics Security
            'ISO 14155': 7.0    # Clinical Investigation
        }
        
        total_impact = 0.0
        for cert in active_certifications:
            standard_base = cert.iso_standard.split(':')[0]
            weight = standard_weights.get(standard_base, 3.0)  # Default weight for unknown standards
            
            # Adjust based on confidence score
            adjusted_weight = weight * cert.confidence_score
            total_impact += adjusted_weight
        
        # Cap the maximum impact at 25 points
        return min(total_impact, 25.0)
    
    def _create_empty_summary(self, org_name: str) -> ISOCertificationSummary:
        """
        Create an empty summary when no certifications are found
        """
        return ISOCertificationSummary(
            organization_name=org_name,
            total_certifications=0,
            active_certifications=0,
            certification_types=[],
            certification_bodies=[],
            earliest_certification=None,
            latest_expiry=None,
            quality_score_impact=0.0,
            last_updated=datetime.now(),
            data_sources=[]
        )
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid
        """
        if cache_key not in self.certification_cache:
            return False
        
        cache_time = self.certification_cache[cache_key]['timestamp']
        return datetime.now() - cache_time < self.cache_expiry
    
    def _cache_data(self, cache_key: str, data: ISOCertificationSummary):
        """
        Cache certification data
        """
        self.certification_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }

# Global instance for use in other modules
iso_scraper = ISOCertificationScraper()

def get_iso_certifications(org_name: str, location: str = "") -> ISOCertificationSummary:
    """
    Convenience function to get ISO certifications for an organization
    
    Args:
        org_name: Name of the healthcare organization
        location: Location to help with search accuracy
        
    Returns:
        ISOCertificationSummary with all found certifications
    """
    return iso_scraper.get_organization_iso_certifications(org_name, location)

if __name__ == "__main__":
    # Test the scraper
    test_orgs = ["Apollo Hospitals", "Fortis Healthcare", "Max Healthcare"]
    
    for org in test_orgs:
        print(f"\n=== Testing {org} ===")
        summary = get_iso_certifications(org)
        print(f"Total certifications: {summary.total_certifications}")
        print(f"Active certifications: {summary.active_certifications}")
        print(f"Quality score impact: {summary.quality_score_impact}")
        print(f"Certification types: {summary.certification_types}")