"""
Website Scraper Module for QuXAT Healthcare Quality Assessment
Extracts organization data from healthcare websites for QuXAT scoring
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareWebsiteScraper:
    """Scrapes healthcare organization websites to extract relevant data for QuXAT scoring"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Common certification patterns
        self.certification_patterns = {
            'JCI': [r'joint commission international', r'jci accredited', r'jci certification'],
            'NABH': [r'nabh accredited', r'national accreditation board', r'nabh certification'],
            'NABL': [r'nabl accredited', r'nabl certification', r'testing.*calibration'],
            'ISO': [r'iso\s*\d+', r'iso certified', r'iso accreditation'],
            'CAP': [r'cap accredited', r'college.*american.*pathologists'],
            'AAAHC': [r'aaahc accredited', r'ambulatory.*accreditation'],
            'DNV': [r'dnv.*accredited', r'det norske veritas'],
            'Magnet': [r'magnet.*status', r'magnet.*recognition', r'magnet.*hospital']
        }
        
        # Quality initiative keywords
        self.quality_keywords = [
            'patient safety', 'quality improvement', 'clinical excellence',
            'infection control', 'medication safety', 'fall prevention',
            'hand hygiene', 'patient satisfaction', 'quality assurance',
            'continuous improvement', 'best practices', 'evidence-based'
        ]
        
    def scrape_organization_data(self, url: str) -> Dict[str, Any]:
        """
        Main method to scrape organization data from a website
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing extracted organization data
        """
        try:
            # Validate and normalize URL
            normalized_url = self._normalize_url(url)
            if not normalized_url:
                raise ValueError("Invalid URL provided")
            
            logger.info(f"Starting to scrape: {normalized_url}")
            
            # Get main page content
            main_content = self._fetch_page_content(normalized_url)
            if not main_content:
                raise Exception("Failed to fetch main page content")
            
            # Extract basic organization information
            org_data = self._extract_basic_info(main_content, normalized_url)
            
            # Extract certifications and accreditations
            org_data['certifications'] = self._extract_certifications(main_content)
            
            # Extract quality initiatives
            org_data['quality_initiatives'] = self._extract_quality_initiatives(main_content)
            
            # Extract contact information
            contact_info = self._extract_contact_info(main_content)
            org_data.update(contact_info)
            
            # Extract services offered
            org_data['services'] = self._extract_services(main_content)
            
            # Try to get additional pages (about, quality, accreditation pages)
            additional_data = self._scrape_additional_pages(normalized_url, main_content)
            
            # Merge additional data
            for key, value in additional_data.items():
                if key == 'certifications':
                    org_data['certifications'].extend(value)
                elif key == 'quality_initiatives':
                    org_data['quality_initiatives'].extend(value)
                else:
                    org_data[key] = value
            
            # Remove duplicates and clean data
            org_data = self._clean_extracted_data(org_data)
            
            # Add metadata
            org_data['data_source'] = 'Website_Scraper'
            org_data['scraped_url'] = normalized_url
            org_data['scrape_timestamp'] = datetime.now().isoformat()
            org_data['scraper_confidence'] = self._calculate_confidence_score(org_data)
            
            logger.info(f"Successfully scraped data for: {org_data.get('name', 'Unknown')}")
            return org_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'error': str(e),
                'url': url,
                'scrape_timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _normalize_url(self, url: str) -> Optional[str]:
        """Normalize and validate URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
                
            return url
        except Exception:
            return None
    
    def _fetch_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse page content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def _extract_basic_info(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract basic organization information"""
        org_data = {
            'name': '',
            'original_name': '',
            'website': url,
            'description': '',
            'hospital_type': 'Healthcare Organization'
        }
        
        # Extract organization name
        name_selectors = [
            'h1', 'title', '.site-title', '.logo-text', 
            '.hospital-name', '.org-name', '.brand-name'
        ]
        
        for selector in name_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) > 3 and len(text) < 100:
                    org_data['name'] = text
                    org_data['original_name'] = text
                    break
            if org_data['name']:
                break
        
        # If no name found, try meta tags
        if not org_data['name']:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                org_data['name'] = meta_title.get('content', '').strip()
                org_data['original_name'] = org_data['name']
        
        # Extract description
        desc_selectors = [
            'meta[name="description"]', 'meta[property="og:description"]',
            '.about-text', '.description', '.intro-text'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    desc = element.get('content', '').strip()
                else:
                    desc = element.get_text().strip()
                
                if desc and len(desc) > 20:
                    org_data['description'] = desc[:500]  # Limit description length
                    break
        
        # Determine hospital type based on content
        content_text = soup.get_text().lower()
        
        type_keywords = {
            'Academic Medical Center': ['university', 'medical school', 'teaching hospital', 'academic'],
            'General Hospital': ['general hospital', 'multi-specialty', 'full service'],
            'Specialty Hospital': ['specialty', 'specialized', 'cardiac', 'cancer', 'orthopedic'],
            'Clinic': ['clinic', 'medical center', 'outpatient'],
            'Laboratory': ['laboratory', 'lab', 'diagnostic', 'pathology'],
            'Dental Facility': ['dental', 'dentist', 'orthodontic', 'oral health']
        }
        
        for hospital_type, keywords in type_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                org_data['hospital_type'] = hospital_type
                break
        
        return org_data
    
    def _extract_certifications(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract certifications and accreditations"""
        certifications = []
        content_text = soup.get_text().lower()
        
        for cert_type, patterns in self.certification_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_text, re.IGNORECASE)
                for match in matches:
                    # Get surrounding context
                    start = max(0, match.start() - 100)
                    end = min(len(content_text), match.end() + 100)
                    context = content_text[start:end]
                    
                    certification = {
                        'name': cert_type,
                        'type': f'{cert_type} Accreditation',
                        'status': 'Active',
                        'source': 'Website',
                        'context': context.strip(),
                        'confidence': 'medium'
                    }
                    
                    # Try to extract dates if present
                    date_pattern = r'\b(19|20)\d{2}\b'
                    dates = re.findall(date_pattern, context)
                    if dates:
                        certification['year'] = dates[-1]  # Use most recent year
                    
                    certifications.append(certification)
                    break  # Only add one instance per certification type
        
        # Look for certification logos/images
        cert_images = soup.find_all('img', alt=re.compile(r'(accredited|certified|jci|nabh|iso)', re.I))
        for img in cert_images:
            alt_text = img.get('alt', '').lower()
            for cert_type in self.certification_patterns.keys():
                if cert_type.lower() in alt_text:
                    certification = {
                        'name': cert_type,
                        'type': f'{cert_type} Accreditation',
                        'status': 'Active',
                        'source': 'Website_Logo',
                        'confidence': 'high'
                    }
                    certifications.append(certification)
        
        return certifications
    
    def _extract_quality_initiatives(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract quality initiatives and programs"""
        initiatives = []
        content_text = soup.get_text().lower()
        
        for keyword in self.quality_keywords:
            if keyword in content_text:
                # Find the context around the keyword
                pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                matches = re.finditer(pattern, content_text, re.IGNORECASE)
                
                for match in matches:
                    context = match.group().strip()
                    
                    initiative = {
                        'name': keyword.title(),
                        'type': 'Quality Initiative',
                        'status': 'Active',
                        'description': context,
                        'source': 'Website'
                    }
                    initiatives.append(initiative)
                    break  # Only add one instance per keyword
        
        return initiatives
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {
            'phone': '',
            'email': '',
            'address': '',
            'city': '',
            'state': '',
            'country': '',
            'postal_code': ''
        }
        
        content_text = soup.get_text()
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, content_text)
        if phone_matches:
            contact_info['phone'] = phone_matches[0] if isinstance(phone_matches[0], str) else ''.join(phone_matches[0])
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, content_text)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract address information
        address_selectors = [
            '.address', '.contact-address', '.location',
            '[itemtype*="PostalAddress"]', '.postal-address'
        ]
        
        for selector in address_selectors:
            address_elem = soup.select_one(selector)
            if address_elem:
                address_text = address_elem.get_text().strip()
                if address_text:
                    contact_info['address'] = address_text
                    
                    # Try to parse city, state, country
                    address_parts = address_text.split(',')
                    if len(address_parts) >= 2:
                        contact_info['city'] = address_parts[-2].strip()
                        contact_info['state'] = address_parts[-1].strip()
                    break
        
        return contact_info
    
    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Extract healthcare services offered"""
        services = []
        
        # Common service keywords
        service_keywords = [
            'cardiology', 'oncology', 'neurology', 'orthopedics', 'pediatrics',
            'emergency', 'surgery', 'radiology', 'laboratory', 'pharmacy',
            'intensive care', 'maternity', 'rehabilitation', 'dialysis'
        ]
        
        content_text = soup.get_text().lower()
        
        for service in service_keywords:
            if service in content_text:
                services.append(service.title())
        
        # Look for services in navigation or dedicated sections
        service_sections = soup.find_all(['nav', 'ul', 'div'], class_=re.compile(r'(service|department|specialty)', re.I))
        for section in service_sections:
            links = section.find_all('a')
            for link in links:
                service_text = link.get_text().strip()
                if service_text and len(service_text) < 50:
                    services.append(service_text)
        
        return list(set(services))  # Remove duplicates
    
    def _scrape_additional_pages(self, base_url: str, main_soup: BeautifulSoup) -> Dict[str, Any]:
        """Scrape additional relevant pages"""
        additional_data = {
            'certifications': [],
            'quality_initiatives': []
        }
        
        # Look for links to relevant pages
        relevant_links = []
        link_patterns = [
            r'about', r'quality', r'accreditation', r'certification',
            r'awards', r'recognition', r'excellence'
        ]
        
        all_links = main_soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            link_text = link.get_text().lower()
            
            for pattern in link_patterns:
                if re.search(pattern, link_text) or re.search(pattern, href.lower()):
                    full_url = urljoin(base_url, href)
                    relevant_links.append(full_url)
                    break
        
        # Limit to first 3 additional pages to avoid overloading
        for url in relevant_links[:3]:
            try:
                time.sleep(1)  # Be respectful to the server
                page_soup = self._fetch_page_content(url)
                if page_soup:
                    page_certs = self._extract_certifications(page_soup)
                    page_initiatives = self._extract_quality_initiatives(page_soup)
                    
                    additional_data['certifications'].extend(page_certs)
                    additional_data['quality_initiatives'].extend(page_initiatives)
                    
            except Exception as e:
                logger.warning(f"Failed to scrape additional page {url}: {str(e)}")
                continue
        
        return additional_data
    
    def _clean_extracted_data(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and deduplicate extracted data"""
        
        # Remove duplicate certifications
        if 'certifications' in org_data:
            seen_certs = set()
            unique_certs = []
            for cert in org_data['certifications']:
                cert_key = (cert.get('name', ''), cert.get('type', ''))
                if cert_key not in seen_certs:
                    seen_certs.add(cert_key)
                    unique_certs.append(cert)
            org_data['certifications'] = unique_certs
        
        # Remove duplicate quality initiatives
        if 'quality_initiatives' in org_data:
            seen_initiatives = set()
            unique_initiatives = []
            for initiative in org_data['quality_initiatives']:
                init_key = initiative.get('name', '')
                if init_key not in seen_initiatives:
                    seen_initiatives.add(init_key)
                    unique_initiatives.append(initiative)
            org_data['quality_initiatives'] = unique_initiatives
        
        # Clean services list
        if 'services' in org_data:
            org_data['services'] = list(set(org_data['services']))
        
        return org_data
    
    def _calculate_confidence_score(self, org_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extracted data"""
        score = 0.0
        
        # Basic info completeness
        if org_data.get('name'):
            score += 0.2
        if org_data.get('description'):
            score += 0.1
        if org_data.get('phone') or org_data.get('email'):
            score += 0.1
        if org_data.get('address'):
            score += 0.1
        
        # Certifications found
        cert_count = len(org_data.get('certifications', []))
        score += min(0.3, cert_count * 0.1)
        
        # Quality initiatives found
        init_count = len(org_data.get('quality_initiatives', []))
        score += min(0.2, init_count * 0.05)
        
        return min(1.0, score)