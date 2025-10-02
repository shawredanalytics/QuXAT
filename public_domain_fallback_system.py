#!/usr/bin/env python3
"""
Public Domain Fallback System for QuXAT Healthcare Scoring
Provides QuXAT scores and rankings for organizations not in the main database
using publicly available information from web sources.
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PublicDomainOrganization:
    """Data structure for organizations found through public domain sources"""
    name: str
    location: str = ""
    country: str = ""
    organization_type: str = "Healthcare Organization"
    certifications: List[Dict] = None
    accreditations: List[Dict] = None
    quality_indicators: Dict = None
    web_presence: Dict = None
    confidence_score: float = 0.5
    data_sources: List[str] = None
    quality_score: float = 0.0
    total_score: float = 0.0
    data_source: str = "public_domain"
    confidence_level: str = "medium"
    last_updated: str = ""
    
    def __post_init__(self):
        if self.certifications is None:
            self.certifications = []
        if self.accreditations is None:
            self.accreditations = []
        if self.quality_indicators is None:
            self.quality_indicators = {}
        if self.web_presence is None:
            self.web_presence = {}
        if self.data_sources is None:
            self.data_sources = []
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

class PublicDomainFallbackSystem:
    """
    Fallback system that searches public domain sources for healthcare organizations
    and generates QuXAT scores based on publicly available information.
    """
    
    def __init__(self):
        self.web_search_available = True
        self.accreditation_patterns = self._load_accreditation_patterns()
        self.quality_indicators = self._load_quality_indicators()
        self.scoring_weights = self._load_scoring_weights()
        
    def _load_accreditation_patterns(self) -> Dict[str, List[str]]:
        """Load patterns to identify accreditations from web content"""
        return {
            'jci': [
                'joint commission international',
                'jci accredited',
                'jci accreditation',
                'joint commission accredited'
            ],
            'nabh': [
                'nabh accredited',
                'nabh accreditation',
                'national accreditation board',
                'nabh certified'
            ],
            'nabl': [
                'nabl accredited',
                'nabl accreditation',
                'national accreditation board for testing and calibration laboratories',
                'nabl certified'
            ],
            'iso': [
                'iso 9001',
                'iso 14001',
                'iso 45001',
                'iso certified',
                'iso accredited'
            ],
            # ENHANCED CAP DETECTION - MANDATORY FOR ALL HEALTHCARE ORGANIZATIONS
            'cap': [
                'cap accredited',
                'cap accreditation',
                'college of american pathologists',
                'cap laboratory',
                'cap 15189',
                'cap certified',
                'cap approved',
                'pathologists accreditation',
                'laboratory accreditation program',
                'cap lab accreditation',
                'cap quality assurance',
                'cap proficiency testing',
                'american pathologists accreditation'
            ],
            'magnet': [
                'magnet hospital',
                'magnet recognition',
                'magnet status'
            ]
        }
    
    def _load_quality_indicators(self) -> Dict[str, List[str]]:
        """Load patterns to identify quality indicators from web content"""
        return {
            'awards': [
                'best hospital',
                'top hospital',
                'award winning',
                'excellence award',
                'quality award',
                'patient safety award'
            ],
            'rankings': [
                'ranked #',
                'top 10',
                'top 100',
                'best in',
                'leading hospital'
            ],
            'specialties': [
                'center of excellence',
                'specialty care',
                'tertiary care',
                'quaternary care',
                'super specialty'
            ],
            'technology': [
                'robotic surgery',
                'advanced imaging',
                'telemedicine',
                'electronic health records',
                'digital health'
            ]
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights for different quality indicators"""
        return {
            # MANDATORY ACCREDITATIONS - INCREASED WEIGHTS TO REFLECT MANDATORY STATUS
            'jci_accreditation': 30.0,  # Increased from 25.0 - MANDATORY
            'cap_accreditation': 30.0,  # Increased from 15.0 - MANDATORY
            'iso_9001_certification': 25.0,  # NEW - MANDATORY
            'iso_15189_certification': 25.0,  # NEW - MANDATORY
            
            # OTHER ACCREDITATIONS
            'nabh_accreditation': 20.0,
            'nabl_accreditation': 15.0,
            'iso_certification': 10.0,  # General ISO certifications (non-mandatory)
            'magnet_status': 20.0,
            'awards_recognition': 15.0,
            'specialty_services': 10.0,
            'technology_adoption': 8.0,
            'web_presence': 5.0,
            'patient_reviews': 12.0,
            'base_healthcare_score': 10.0  # Minimum score for healthcare organizations
        }
    
    def search_public_domain(self, organization_name: str) -> Optional[PublicDomainOrganization]:
        """
        Search public domain sources for organization information
        """
        try:
            logger.info(f"Searching public domain for: {organization_name}")
            
            # Simulate web search results (in production, this would use actual web search APIs)
            web_data = self._simulate_web_search(organization_name)
            
            if not web_data:
                return None
            
            # Extract organization information
            org_info = self._extract_organization_info(organization_name, web_data)
            
            if org_info:
                logger.info(f"Found public domain information for: {organization_name}")
                return org_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching public domain for {organization_name}: {e}")
            return None
    
    def _simulate_web_search(self, organization_name: str) -> Dict[str, Any]:
        """
        DISABLED: No automatic certificate allocation without evidence
        This method previously assigned certificates based on patterns without verification.
        All certifications must now be validated through official sources only.
        """
        # IMPORTANT: No automatic accreditation assignment without verified evidence
        # All certifications must come from official validation sources
        
        org_name_lower = organization_name.lower()
        
        # Only provide basic organizational information without any accreditations
        if any(keyword in org_name_lower for keyword in ['hospital', 'medical', 'clinic', 'healthcare']):
            return {
                'organization_name': organization_name,
                'found_data': {
                    'accreditations': [],  # NO automatic accreditations
                    'awards': [],  # NO automatic awards without evidence
                    'specialties': ['healthcare services'],
                    'location': 'Location to be verified',
                    'type': 'Healthcare Organization'
                },
                'confidence': 0.2,  # Lower confidence due to lack of verified data
                'source': 'basic_pattern_only',
                'note': 'No certifications assigned - requires official validation'
            }
        
        return None
    
    def _extract_organization_info(self, org_name: str, web_data: Dict[str, Any]) -> Optional[PublicDomainOrganization]:
        """Extract and structure organization information from web data"""
        try:
            found_data = web_data.get('found_data', {})
            
            # Extract accreditations
            accreditations = []
            for acc_type in found_data.get('accreditations', []):
                accreditations.append({
                    'type': acc_type.upper(),
                    'status': 'Active',
                    'source': 'Public Domain',
                    'confidence': web_data.get('confidence', 0.5)
                })
            
            # Extract quality indicators
            quality_indicators = {
                'awards': found_data.get('awards', []),
                'specialties': found_data.get('specialties', []),
                'recognition': len(found_data.get('awards', [])) > 0
            }
            
            # Web presence indicators
            web_presence = {
                'has_website': True,
                'online_presence': 'Active',
                'information_availability': 'Good' if web_data.get('confidence', 0) > 0.6 else 'Limited'
            }
            
            return PublicDomainOrganization(
                name=org_name,
                location=found_data.get('location', 'Location to be verified'),
                country=self._extract_country(found_data.get('location', '')),
                organization_type=found_data.get('type', 'Healthcare Organization'),
                accreditations=accreditations,
                quality_indicators=quality_indicators,
                web_presence=web_presence,
                confidence_score=web_data.get('confidence', 0.5),
                data_sources=[web_data.get('source', 'public_domain')],
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error extracting organization info: {e}")
            return None
    
    def _extract_country(self, location: str) -> str:
        """Extract country from location string"""
        location_lower = location.lower()
        
        country_patterns = {
            'usa': ['usa', 'united states', 'america', 'minnesota', 'ohio', 'california', 'texas'],
            'india': ['india', 'mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad'],
            'uk': ['uk', 'united kingdom', 'london', 'england'],
            'canada': ['canada', 'toronto', 'vancouver'],
            'australia': ['australia', 'sydney', 'melbourne']
        }
        
        for country, patterns in country_patterns.items():
            if any(pattern in location_lower for pattern in patterns):
                return country.upper()
        
        return 'Unknown'
    
    def calculate_public_domain_score(self, org_data: PublicDomainOrganization) -> Dict[str, Any]:
        """
        Calculate QuXAT score based on public domain information
        """
        try:
            score_breakdown = {}
            total_score = 0.0
            
            # Accreditation scoring
            accreditation_score = 0.0
            for acc in org_data.accreditations:
                acc_type = acc['type'].lower()
                if acc_type in ['jci']:
                    accreditation_score += self.scoring_weights['jci_accreditation']
                elif acc_type in ['nabh']:
                    accreditation_score += self.scoring_weights['nabh_accreditation']
                elif acc_type in ['nabl']:
                    accreditation_score += self.scoring_weights['nabl_accreditation']
                elif acc_type in ['iso']:
                    accreditation_score += self.scoring_weights['iso_certification']
                elif acc_type in ['cap']:
                    accreditation_score += self.scoring_weights['cap_accreditation']
                elif acc_type in ['magnet']:
                    accreditation_score += self.scoring_weights['magnet_status']
            
            score_breakdown['Accreditation Score'] = accreditation_score
            total_score += accreditation_score
            
            # Quality indicators scoring
            quality_score = 0.0
            if org_data.quality_indicators.get('awards'):
                quality_score += self.scoring_weights['awards_recognition']
            if org_data.quality_indicators.get('specialties'):
                quality_score += self.scoring_weights['specialty_services']
            
            score_breakdown['Quality Indicators Score'] = quality_score
            total_score += quality_score
            
            # Web presence scoring
            web_score = 0.0
            if org_data.web_presence.get('has_website'):
                web_score += self.scoring_weights['web_presence']
            
            score_breakdown['Web Presence Score'] = web_score
            total_score += web_score
            
            # Confidence adjustment
            confidence_multiplier = org_data.confidence_score
            adjusted_total_score = total_score * confidence_multiplier
            
            # MANDATORY ACCREDITATION PENALTY ENFORCEMENT
            # Check for all mandatory accreditations: CAP, JCI, ISO 9001, ISO 15189, Magnet Recognition
            mandatory_accreditations = {
                'cap': {'compliant': False, 'penalty': 40.0, 'name': 'CAP'},
                'jci': {'compliant': False, 'penalty': 30.0, 'name': 'JCI'},
                'iso_9001': {'compliant': False, 'penalty': 25.0, 'name': 'ISO 9001'},
                'iso_15189': {'compliant': False, 'penalty': 25.0, 'name': 'ISO 15189'},
                'magnet': {'compliant': False, 'penalty': 25.0, 'name': 'Magnet Recognition'}
            }
            
            # Check compliance for each mandatory accreditation
            for acc in org_data.accreditations:
                acc_type = acc['type'].lower()
                acc_name = acc.get('name', '')
                acc_standard = acc.get('standard', '')
                if acc_type == 'cap':
                    mandatory_accreditations['cap']['compliant'] = True
                elif acc_type == 'jci':
                    mandatory_accreditations['jci']['compliant'] = True
                elif acc_type == 'iso' and 'iso 9001' in acc_standard.lower():
                    mandatory_accreditations['iso_9001']['compliant'] = True
                elif acc_type == 'iso' and 'iso 15189' in acc_standard.lower():
                    mandatory_accreditations['iso_15189']['compliant'] = True
                elif acc_type == 'magnet' or 'magnet' in acc_name.lower():
                    mandatory_accreditations['magnet']['compliant'] = True
            
            # Apply penalties for missing mandatory accreditations
            total_mandatory_penalty = 0.0
            missing_accreditations = []
            
            for acc_key, acc_info in mandatory_accreditations.items():
                if not acc_info['compliant']:
                    total_mandatory_penalty += acc_info['penalty']
                    missing_accreditations.append(acc_info['name'])
                
                # Add compliance status to score breakdown
                score_breakdown[f"{acc_info['name']} Compliance"] = "✅ Compliant" if acc_info['compliant'] else "❌ Non-Compliant (Penalty Applied)"
                if not acc_info['compliant']:
                    score_breakdown[f"{acc_info['name']} Penalty"] = acc_info['penalty']
            
            # Apply total penalty
            if total_mandatory_penalty > 0:
                adjusted_total_score = max(0, adjusted_total_score - total_mandatory_penalty)
                score_breakdown['Total Mandatory Penalties'] = total_mandatory_penalty
            
            # Generate warning message
            mandatory_warning = ""
            if missing_accreditations:
                if len(missing_accreditations) == 1:
                    mandatory_warning = f"⚠️ CRITICAL: {missing_accreditations[0]} accreditation is mandatory for all healthcare organizations. Score significantly reduced."
                else:
                    mandatory_warning = f"⚠️ CRITICAL: Multiple mandatory accreditations missing ({', '.join(missing_accreditations)}). Score significantly reduced."
            
            score_breakdown['Confidence Adjustment'] = f"{confidence_multiplier:.2f}"
            score_breakdown['Raw Total Score'] = total_score
            score_breakdown['Adjusted Total Score'] = adjusted_total_score
            
            result = {
                'total_score': adjusted_total_score,
                'certification_score': accreditation_score * confidence_multiplier,
                'quality_score': quality_score * confidence_multiplier,
                'score_breakdown': score_breakdown,
                'confidence_level': 'High' if confidence_multiplier > 0.7 else 'Medium' if confidence_multiplier > 0.4 else 'Low',
                'data_source': 'Public Domain Analysis',
                'last_updated': datetime.now().isoformat(),
                'mandatory_compliance': {
                    'cap_compliant': mandatory_accreditations['cap']['compliant'],
                    'jci_compliant': mandatory_accreditations['jci']['compliant'],
                    'iso_9001_compliant': mandatory_accreditations['iso_9001']['compliant'],
                    'iso_15189_compliant': mandatory_accreditations['iso_15189']['compliant'],
                    'magnet_compliant': mandatory_accreditations['magnet']['compliant']
                },
                'mandatory_penalties': total_mandatory_penalty
            }
            
            if mandatory_warning:
                result['mandatory_warning'] = mandatory_warning
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating public domain score: {e}")
            return {
                'total_score': 0.0,
                'certification_score': 0.0,
                'quality_score': 0.0,
                'score_breakdown': {},
                'confidence_level': 'Low',
                'data_source': 'Public Domain Analysis (Error)',
                'last_updated': datetime.now().isoformat()
            }
    
    def generate_fallback_organization_data(self, organization_name: str) -> Optional[Dict[str, Any]]:
        """
        Generate complete organization data with QuXAT scoring for organizations not in database
        """
        try:
            # Search public domain
            org_data = self.search_public_domain(organization_name)
            
            if not org_data:
                # Create minimal fallback data
                org_data = PublicDomainOrganization(
                    name=organization_name,
                    location='Location to be verified',
                    country='Unknown',
                    organization_type='Healthcare Organization',
                    accreditations=[],
                    quality_indicators={},
                    web_presence={'has_website': False},
                    confidence_score=0.2,
                    data_sources=['minimal_fallback'],
                    last_updated=datetime.now()
                )
            
            # Calculate scores
            scoring_data = self.calculate_public_domain_score(org_data)
            
            # Create complete organization record
            fallback_org = {
                'name': org_data.name,
                'original_name': org_data.name,
                'country': org_data.country,
                'state': org_data.location,
                'city': org_data.location,
                'hospital_type': org_data.organization_type,
                'data_source': 'Public Domain Fallback',
                'certifications': [
                    {
                        'type': acc['type'],
                        'status': acc['status'],
                        'source': acc['source'],
                        'found': True
                    } for acc in org_data.accreditations
                ],
                'total_score': scoring_data['total_score'],
                'certification_score': scoring_data['certification_score'],
                'quality_score': scoring_data['quality_score'],
                'score_breakdown': scoring_data['score_breakdown'],
                'confidence_level': scoring_data['confidence_level'],
                'public_domain_source': True,
                'last_updated': scoring_data['last_updated'],
                'fallback_notice': f"This organization was not found in our primary database. Information and scoring are based on publicly available data with {scoring_data['confidence_level'].lower()} confidence."
            }
            
            logger.info(f"Generated fallback data for {organization_name} with score: {scoring_data['total_score']:.2f}")
            return fallback_org
            
        except Exception as e:
            logger.error(f"Error generating fallback organization data: {e}")
            return None

def test_fallback_system():
    """Test the public domain fallback system"""
    fallback_system = PublicDomainFallbackSystem()
    
    test_organizations = [
        "Mayo Clinic",
        "Cleveland Clinic", 
        "Apollo Hospital",
        "Fortis Healthcare",
        "Unknown Hospital XYZ"
    ]
    
    print("🧪 Testing Public Domain Fallback System")
    print("=" * 50)
    
    for org_name in test_organizations:
        print(f"\n🏥 Testing: {org_name}")
        
        fallback_data = fallback_system.generate_fallback_organization_data(org_name)
        
        if fallback_data:
            print(f"✅ Generated fallback data:")
            print(f"   📍 Location: {fallback_data['state']}")
            print(f"   🏆 Total Score: {fallback_data['total_score']:.2f}")
            print(f"   🎯 Confidence: {fallback_data['confidence_level']}")
            print(f"   📜 Certifications: {len(fallback_data['certifications'])}")
        else:
            print(f"❌ Failed to generate fallback data")

if __name__ == "__main__":
    test_fallback_system()