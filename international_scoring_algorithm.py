"""
International Healthcare Quality Scoring Algorithm
Removes regional bias and implements global healthcare quality standards
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

class InternationalHealthcareScorer:
    """
    International Healthcare Quality Scoring System
    Designed to be fair and unbiased across all regions and countries
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_international_standards()
    
    def setup_international_standards(self):
        """Setup international healthcare quality standards and weights"""
        
        # Accreditation Equivalency Groups - Define which accreditations are equivalent
        self.accreditation_equivalencies = {
            'ISO_15189_GROUP': {
                'name': 'Medical Laboratory Quality Standards',
                'description': 'Equivalent accreditations for medical laboratory quality and competence',
                'equivalent_types': ['ISO_15189', 'CAP', 'NABL'],
                'penalty': 8.0,
                'primary_standard': 'ISO_15189'
            },
            'GLOBAL_HOSPITAL_ACCRED_GROUP': {
                'name': 'Global or National Hospital Accreditation',
                'description': 'Equivalent hospital accreditation standards across regions (JCI or national bodies)',
                'equivalent_types': [
                    'JCI',
                    'JOINT_COMMISSION_US',
                    'DNV_HEALTHCARE',
                    'ACCREDITATION_CANADA',
                    'CQC_UK',
                    'HAS_FRANCE',
                    'G_BA_GERMANY',
                    'ACHS_AUSTRALIA',
                    'JCQHC_JAPAN',
                    'TJCHA_TAIWAN'
                ],
                'penalty': 20.0,
                'primary_standard': 'JCI'
            }
        }
        
        # Mandatory Accreditation Requirements for All Healthcare Organizations
        self.mandatory_accreditations = {
            'JCI': {
                'name': 'Joint Commission International',
                'penalty': 20.0,
                'description': 'Global healthcare quality and patient safety standards',
                'equivalency_group': 'GLOBAL_HOSPITAL_ACCRED_GROUP'
            },
            'ISO_9001': {
                'name': 'ISO 9001',
                'penalty': 12.0,
                'description': 'Quality Management Systems',
                'equivalency_group': None
            },
            'ISO_15189_GROUP': {
                'name': 'Medical Laboratory Quality Standards',
                'penalty': 8.0,
                'description': 'Medical laboratory quality and competence (ISO 15189, CAP, or NABL)',
                'equivalency_group': 'ISO_15189_GROUP'
            }
        }
        
        # Global Healthcare Quality Standards (No Regional Bias)
        self.certification_weights = {
            # TIER 1: Global Gold Standards (Highest Weight)
            'JCI': {
                'weight': 4.0, 
                'base_score': 35, 
                'description': 'Joint Commission International - Global Gold Standard',
                'region': 'Global',
                'tier': 1
            },
            'WHO_CERTIFICATION': {
                'weight': 3.8, 
                'base_score': 32, 
                'description': 'WHO Global Health Standards Certification',
                'region': 'Global',
                'tier': 1
            },
            
            # TIER 2: International ISO Standards (High Weight)
            'ISO_9001': {
                'weight': 3.2, 
                'base_score': 25, 
                'description': 'ISO 9001 - Quality Management Systems',
                'region': 'Global',
                'tier': 2
            },
            'ISO_13485': {
                'weight': 3.2, 
                'base_score': 25, 
                'description': 'ISO 13485 - Medical Devices Quality Management',
                'region': 'Global',
                'tier': 2
            },
            'ISO_15189': {
                'weight': 3.0, 
                'base_score': 22, 
                'description': 'ISO 15189 - Medical Laboratories Quality and Competence',
                'region': 'Global',
                'tier': 2
            },
            'ISO_27001': {
                'weight': 2.8, 
                'base_score': 20, 
                'description': 'ISO 27001 - Information Security Management',
                'region': 'Global',
                'tier': 2
            },
            'ISO_45001': {
                'weight': 2.6, 
                'base_score': 18, 
                'description': 'ISO 45001 - Occupational Health and Safety Management',
                'region': 'Global',
                'tier': 2
            },
            'ISO_14001': {
                'weight': 2.4, 
                'base_score': 16, 
                'description': 'ISO 14001 - Environmental Management Systems',
                'region': 'Global',
                'tier': 2
            },
            
            # TIER 3: Regional Excellence Standards (Medium-High Weight)
            # North America
            'JOINT_COMMISSION_US': {
                'weight': 3.5, 
                'base_score': 30, 
                'description': 'Joint Commission (US) - National Healthcare Accreditation',
                'region': 'North America',
                'tier': 3
            },
            'MAGNET_RECOGNITION': {
                'weight': 3.6, 
                'base_score': 28, 
                'description': 'Magnet Recognition Program - Nursing Excellence',
                'region': 'North America',
                'tier': 3
            },
            'DNV_HEALTHCARE': {
                'weight': 3.0, 
                'base_score': 24, 
                'description': 'DNV Healthcare Accreditation',
                'region': 'North America',
                'tier': 3
            },
            'ACCREDITATION_CANADA': {
                'weight': 3.0, 
                'base_score': 24, 
                'description': 'Accreditation Canada',
                'region': 'North America',
                'tier': 3
            },
            
            # Europe
            'CQC_UK': {
                'weight': 3.5, 
                'base_score': 30, 
                'description': 'Care Quality Commission (UK)',
                'region': 'Europe',
                'tier': 3
            },
            'HAS_FRANCE': {
                'weight': 3.0, 
                'base_score': 25, 
                'description': 'Haute Autorité de Santé (France)',
                'region': 'Europe',
                'tier': 3
            },
            'G_BA_GERMANY': {
                'weight': 3.0, 
                'base_score': 25, 
                'description': 'G-BA (Germany) Healthcare Quality',
                'region': 'Europe',
                'tier': 3
            },
            
            # Asia-Pacific
            'ACHS_AUSTRALIA': {
                'weight': 3.0, 
                'base_score': 25, 
                'description': 'Australian Council on Healthcare Standards',
                'region': 'Asia-Pacific',
                'tier': 3
            },
            'JCQHC_JAPAN': {
                'weight': 3.0, 
                'base_score': 25, 
                'description': 'Japan Council for Quality Health Care',
                'region': 'Asia-Pacific',
                'tier': 3
            },
            'TJCHA_TAIWAN': {
                'weight': 3.0, 
                'base_score': 25, 
                'description': 'Taiwan Joint Commission on Hospital Accreditation',
                'region': 'Asia-Pacific',
                'tier': 3
            },
            
            # TIER 4: National/Regional Standards (Medium Weight - Bonus, Not Required)
            'NABH_INDIA': {
                'weight': 2.5, 
                'base_score': 20, 
                'description': 'National Accreditation Board for Hospitals (India)',
                'region': 'India',
                'tier': 4
            },
            'NABL_INDIA': {
                'weight': 2.0, 
                'base_score': 15, 
                'description': 'National Accreditation Board for Testing and Calibration Laboratories (India)',
                'region': 'India',
                'tier': 4
            },
            'CBAHI_SAUDI': {
                'weight': 2.5, 
                'base_score': 20, 
                'description': 'Central Board for Accreditation of Healthcare Institutions (Saudi Arabia)',
                'region': 'Middle East',
                'tier': 4
            },
            'HAAD_UAE': {
                'weight': 2.5, 
                'base_score': 20, 
                'description': 'Health Authority Abu Dhabi (UAE)',
                'region': 'Middle East',
                'tier': 4
            },
            'COHSASA_AFRICA': {
                'weight': 2.5, 
                'base_score': 20, 
                'description': 'Council for Health Service Accreditation of Southern Africa',
                'region': 'Africa',
                'tier': 4
            },
            
            # TIER 5: Specialty Certifications (Medium Weight)
            'CAP': {
                'weight': 3.0,
                'base_score': 22,
                'description': 'College of American Pathologists - Laboratory Accreditation (Equivalent to ISO 15189)',
                'region': 'Global',
                'tier': 2,
                'equivalent_to': 'ISO_15189'
            },
            'NABL': {
                'weight': 3.0,
                'base_score': 22,
                'description': 'National Accreditation Board for Testing and Calibration Laboratories (Equivalent to ISO 15189)',
                'region': 'India',
                'tier': 2,
                'equivalent_to': 'ISO_15189'
            },
            'CLIA_LABORATORY': {
                'weight': 2.5, 
                'base_score': 18, 
                'description': 'Clinical Laboratory Improvement Amendments (US)',
                'region': 'North America',
                'tier': 5
            },
            'EA_LABORATORY': {
                'weight': 2.5, 
                'base_score': 18, 
                'description': 'European Accreditation for Laboratories',
                'region': 'Europe',
                'tier': 5
            }
        }
        
        # International Quality Metrics Weights
        self.quality_metrics_weights = {
            'clinical_outcomes': 0.30,      # 30% - Patient mortality, readmission rates, infection rates
            'patient_experience': 0.25,     # 25% - Patient satisfaction, PROMs, PREMs
            'operational_excellence': 0.25, # 25% - Efficiency, wait times, staff ratios
            'innovation_technology': 0.10,  # 10% - Digital health, AI/ML, research
            'sustainability_social': 0.10   # 10% - Environmental, community health, diversity
        }
        
        # Regional Adaptation Framework (No Penalties, Only Context)
        self.regional_contexts = {
            'developed': {
                'innovation_weight_multiplier': 1.2,
                'technology_expectation': 'high',
                'description': 'Higher expectations for innovation and technology adoption'
            },
            'developing': {
                'accessibility_weight_multiplier': 1.2,
                'basic_care_focus': True,
                'description': 'Higher weight on accessibility and basic care quality'
            },
            'rural': {
                'specialization_adjustment': 0.8,
                'technology_adjustment': 0.9,
                'description': 'Adjusted expectations for specialization and technology'
            },
            'urban': {
                'comprehensive_services_expectation': 1.1,
                'description': 'Higher expectations for comprehensive services'
            }
        }
    
    def calculate_international_quality_score(self, 
                                            certifications: List[Dict], 
                                            quality_metrics: Dict = None,
                                            hospital_context: Dict = None) -> Dict:
        """
        Calculate international healthcare quality score without regional bias
        
        Args:
            certifications: List of hospital certifications
            quality_metrics: Dictionary of quality metrics (clinical outcomes, patient experience, etc.)
            hospital_context: Hospital context (region, type, size, etc.)
        
        Returns:
            Comprehensive score breakdown
        """
        
        score_breakdown = {
            'certification_score': 0,
            'quality_metrics_score': 0,
            'total_score': 0,
            'certification_breakdown': {},
            'quality_metrics_breakdown': {},
            'international_recognition': {},
            'regional_context': {},
            'recommendations': []
        }
        
        # 1. Calculate Certification Score (60% of total score)
        cert_result = self._calculate_certification_score(certifications, hospital_context)
        score_breakdown['certification_score'] = cert_result['score']
        score_breakdown['certification_breakdown'] = cert_result['breakdown']
        score_breakdown['international_recognition'] = cert_result['international_recognition']
        
        # 2. Calculate Quality Metrics Score (40% of total score)
        if quality_metrics:
            metrics_result = self._calculate_quality_metrics_score(quality_metrics, hospital_context)
            score_breakdown['quality_metrics_score'] = metrics_result['score']
            score_breakdown['quality_metrics_breakdown'] = metrics_result['breakdown']
        
        # 3. Calculate Total Score
        score_breakdown['total_score'] = (
            score_breakdown['certification_score'] * 0.6 + 
            score_breakdown['quality_metrics_score'] * 0.4
        )
        
        # 4. Apply Regional Context (No Penalties, Only Adjustments)
        if hospital_context:
            context_result = self._apply_regional_context(score_breakdown, hospital_context)
            score_breakdown['regional_context'] = context_result
        
        # 5. Generate International Recommendations
        score_breakdown['recommendations'] = self._generate_international_recommendations(
            score_breakdown, certifications, hospital_context
        )
        
        return score_breakdown
    
    def _calculate_certification_score(self, certifications: List[Dict], context: Dict = None) -> Dict:
        """Calculate certification score based on international standards with mandatory requirements"""
        
        result = {
            'score': 0,
            'breakdown': {},
            'mandatory_compliance': {},
            'mandatory_penalties': {},
            'international_recognition': {
                'global_standards': 0,
                'regional_excellence': 0,
                'specialty_certifications': 0,
                'total_certifications': 0
            }
        }
        
        if not certifications:
            # Apply all mandatory penalties if no certifications
            total_penalty = 0
            for mandatory_key, mandatory_info in self.mandatory_accreditations.items():
                result['mandatory_compliance'][mandatory_key] = False
                result['mandatory_penalties'][mandatory_key] = mandatory_info['penalty']
                total_penalty += mandatory_info['penalty']
            
            result['score'] = max(0, -total_penalty)  # Negative score for missing mandatory
            return result
        
        # Check mandatory compliance first
        mandatory_found = {}
        for mandatory_key in self.mandatory_accreditations.keys():
            mandatory_found[mandatory_key] = False
        
        total_weighted_score = 0
        certification_count = 0
        
        # Process each certification
        for cert in certifications:
            if cert.get('status') not in ['Active', 'Valid', 'Current']:
                continue
            
            cert_type = self._identify_certification_type(cert.get('name', '') + ' ' + cert.get('type', '') + ' ' + cert.get('standard', ''))
            
            # Check if this certification fulfills a mandatory requirement
            for mandatory_key, mandatory_info in self.mandatory_accreditations.items():
                # Check direct match
                if cert_type == mandatory_key:
                    mandatory_found[mandatory_key] = True
                # Check equivalency group match
                elif mandatory_info.get('equivalency_group'):
                    equivalency_group = self.accreditation_equivalencies.get(mandatory_info['equivalency_group'])
                    if equivalency_group and cert_type in equivalency_group['equivalent_types']:
                        mandatory_found[mandatory_key] = True
                # Special handling for ISO_15189_GROUP which is both key and equivalency group
                elif mandatory_key == 'ISO_15189_GROUP':
                    equivalency_group = self.accreditation_equivalencies.get('ISO_15189_GROUP')
                    if equivalency_group and cert_type in equivalency_group['equivalent_types']:
                        mandatory_found[mandatory_key] = True
            
            if cert_type and cert_type in self.certification_weights:
                weight_info = self.certification_weights[cert_type]
                base_score = cert.get('score_impact', weight_info['base_score'])
                weight = weight_info['weight']
                tier = weight_info['tier']
                
                # Calculate weighted score
                weighted_score = base_score * weight
                total_weighted_score += weighted_score
                certification_count += 1
                
                # Track by tier for international recognition
                if tier == 1:
                    result['international_recognition']['global_standards'] += 1
                elif tier in [2, 3]:
                    result['international_recognition']['regional_excellence'] += 1
                elif tier in [4, 5]:
                    result['international_recognition']['specialty_certifications'] += 1
                
                # Track certification breakdown
                if cert_type not in result['breakdown']:
                    result['breakdown'][cert_type] = {
                        'count': 0,
                        'total_score': 0,
                        'weight': weight,
                        'description': weight_info['description'],
                        'tier': tier,
                        'region': weight_info['region']
                    }
                result['breakdown'][cert_type]['count'] += 1
                result['breakdown'][cert_type]['total_score'] += weighted_score

        # Detect presence of US Joint Commission (for penalty softening)
        has_joint_commission_us = False
        for key in result['breakdown'].keys():
            if key == 'JOINT_COMMISSION_US':
                has_joint_commission_us = True
                break
        
        # Apply mandatory compliance penalties
        total_penalty = 0
        for mandatory_key, mandatory_info in self.mandatory_accreditations.items():
            is_compliant = mandatory_found[mandatory_key]
            result['mandatory_compliance'][mandatory_key] = is_compliant
            
            if not is_compliant:
                penalty = mandatory_info['penalty']
                # Soften ISO 9001 penalty when JOINT_COMMISSION_US is present
                if has_joint_commission_us and mandatory_key == 'ISO_9001':
                    penalty = penalty * 0.5  # 50% reduction recognizing US-equivalent QMS oversight
                result['mandatory_penalties'][mandatory_key] = penalty
                total_penalty += penalty
            else:
                result['mandatory_penalties'][mandatory_key] = 0
        
        result['international_recognition']['total_certifications'] = certification_count
        
        # Apply diversity bonus for multiple certification types
        if certification_count > 1:
            diversity_bonus = min(certification_count * 2, 15)  # Up to 15 points
            total_weighted_score += diversity_bonus
            result['diversity_bonus'] = diversity_bonus
        
        # Apply international excellence bonus
        global_certs = result['international_recognition']['global_standards']
        if global_certs > 0:
            international_bonus = min(global_certs * 5, 20)  # Up to 20 points
            total_weighted_score += international_bonus
            result['international_bonus'] = international_bonus
        
        # Apply mandatory penalties to final score
        final_score = total_weighted_score - total_penalty
        
        # Cap certification score at 60 (60% of total possible score), but allow negative for penalties
        result['score'] = min(final_score, 60) if final_score > 0 else final_score
        result['total_penalty'] = total_penalty
        
        return result
    
    def _calculate_quality_metrics_score(self, quality_metrics: Dict, context: Dict = None) -> Dict:
        """Calculate quality metrics score based on international standards"""
        
        result = {
            'score': 0,
            'breakdown': {}
        }
        
        total_score = 0
        
        # Clinical Outcomes (30% weight)
        clinical_score = self._calculate_clinical_outcomes_score(
            quality_metrics.get('clinical_outcomes', {})
        )
        clinical_weighted = clinical_score * self.quality_metrics_weights['clinical_outcomes']
        total_score += clinical_weighted
        result['breakdown']['clinical_outcomes'] = {
            'raw_score': clinical_score,
            'weighted_score': clinical_weighted,
            'weight': self.quality_metrics_weights['clinical_outcomes']
        }
        
        # Patient Experience (25% weight)
        patient_score = self._calculate_patient_experience_score(
            quality_metrics.get('patient_experience', {})
        )
        patient_weighted = patient_score * self.quality_metrics_weights['patient_experience']
        total_score += patient_weighted
        result['breakdown']['patient_experience'] = {
            'raw_score': patient_score,
            'weighted_score': patient_weighted,
            'weight': self.quality_metrics_weights['patient_experience']
        }
        
        # Operational Excellence (25% weight)
        operational_score = self._calculate_operational_excellence_score(
            quality_metrics.get('operational_excellence', {})
        )
        operational_weighted = operational_score * self.quality_metrics_weights['operational_excellence']
        total_score += operational_weighted
        result['breakdown']['operational_excellence'] = {
            'raw_score': operational_score,
            'weighted_score': operational_weighted,
            'weight': self.quality_metrics_weights['operational_excellence']
        }
        
        # Innovation & Technology (10% weight)
        innovation_score = self._calculate_innovation_score(
            quality_metrics.get('innovation_technology', {})
        )
        innovation_weighted = innovation_score * self.quality_metrics_weights['innovation_technology']
        total_score += innovation_weighted
        result['breakdown']['innovation_technology'] = {
            'raw_score': innovation_score,
            'weighted_score': innovation_weighted,
            'weight': self.quality_metrics_weights['innovation_technology']
        }
        
        # Sustainability & Social Responsibility (10% weight)
        sustainability_score = self._calculate_sustainability_score(
            quality_metrics.get('sustainability_social', {})
        )
        sustainability_weighted = sustainability_score * self.quality_metrics_weights['sustainability_social']
        total_score += sustainability_weighted
        result['breakdown']['sustainability_social'] = {
            'raw_score': sustainability_score,
            'weighted_score': sustainability_weighted,
            'weight': self.quality_metrics_weights['sustainability_social']
        }
        
        # Cap quality metrics score at 40 (40% of total possible score)
        result['score'] = min(total_score, 40)
        
        return result
    
    def _identify_certification_type(self, cert_name: str) -> Optional[str]:
        """Identify certification type from name with comprehensive international recognition"""
        
        if not cert_name:
            return None
        
        cert_name = cert_name.upper()
        
        # Global Standards
        if 'JCI' in cert_name or 'JOINT COMMISSION INTERNATIONAL' in cert_name:
            return 'JCI'
        if 'WHO' in cert_name and ('CERTIFICATION' in cert_name or 'STANDARD' in cert_name):
            return 'WHO_CERTIFICATION'
        
        # ISO Standards
        iso_mappings = {
            'ISO 9001': 'ISO_9001',
            'ISO9001': 'ISO_9001',
            'ISO 13485': 'ISO_13485',
            'ISO13485': 'ISO_13485',
            'ISO 15189': 'ISO_15189',
            'ISO15189': 'ISO_15189',
            'ISO 27001': 'ISO_27001',
            'ISO27001': 'ISO_27001',
            'ISO 45001': 'ISO_45001',
            'ISO45001': 'ISO_45001',
            'ISO 14001': 'ISO_14001',
            'ISO14001': 'ISO_14001'
        }
        
        for iso_pattern, iso_type in iso_mappings.items():
            if iso_pattern in cert_name:
                return iso_type
        
        # Regional Excellence Standards
        regional_mappings = {
            'JOINT COMMISSION': 'JOINT_COMMISSION_US',
            'MAGNET': 'MAGNET_RECOGNITION',
            'DNV': 'DNV_HEALTHCARE',
            'ACCREDITATION CANADA': 'ACCREDITATION_CANADA',
            'CQC': 'CQC_UK',
            'CARE QUALITY COMMISSION': 'CQC_UK',
            'HAS': 'HAS_FRANCE',
            'HAUTE AUTORITÉ': 'HAS_FRANCE',
            'G-BA': 'G_BA_GERMANY',
            'ACHS': 'ACHS_AUSTRALIA',
            'JCQHC': 'JCQHC_JAPAN',
            'TJCHA': 'TJCHA_TAIWAN',
            'NABH': 'NABH_INDIA',
            'NABL': 'NABL',
            'CBAHI': 'CBAHI_SAUDI',
            'HAAD': 'HAAD_UAE',
            'COHSASA': 'COHSASA_AFRICA'
        }
        
        for pattern, cert_type in regional_mappings.items():
            if pattern in cert_name:
                return cert_type
        
        # Specialty Certifications
        if 'CAP' in cert_name or 'COLLEGE OF AMERICAN PATHOLOGISTS' in cert_name:
            return 'CAP'
        if 'CLIA' in cert_name:
            return 'CLIA_LABORATORY'
        if 'EA' in cert_name and 'LABORATORY' in cert_name:
            return 'EA_LABORATORY'
        
        return None
    
    def _calculate_clinical_outcomes_score(self, clinical_data: Dict) -> float:
        """Calculate clinical outcomes score (0-100)"""
        if not clinical_data:
            return 50  # Neutral score if no data
        
        # Implement clinical outcomes scoring logic
        # This would integrate with actual clinical data
        return min(clinical_data.get('composite_score', 50), 100)
    
    def _calculate_patient_experience_score(self, patient_data: Dict) -> float:
        """Calculate patient experience score (0-100)"""
        if not patient_data:
            return 50  # Neutral score if no data
        
        # Implement patient experience scoring logic
        return min(patient_data.get('composite_score', 50), 100)
    
    def _calculate_operational_excellence_score(self, operational_data: Dict) -> float:
        """Calculate operational excellence score (0-100)"""
        if not operational_data:
            return 50  # Neutral score if no data
        
        # Implement operational excellence scoring logic
        return min(operational_data.get('composite_score', 50), 100)
    
    def _calculate_innovation_score(self, innovation_data: Dict) -> float:
        """Calculate innovation and technology score (0-100)"""
        if not innovation_data:
            return 30  # Lower baseline for innovation
        
        # Implement innovation scoring logic
        return min(innovation_data.get('composite_score', 30), 100)
    
    def _calculate_sustainability_score(self, sustainability_data: Dict) -> float:
        """Calculate sustainability and social responsibility score (0-100)"""
        if not sustainability_data:
            return 40  # Moderate baseline
        
        # Implement sustainability scoring logic
        return min(sustainability_data.get('composite_score', 40), 100)
    
    def _apply_regional_context(self, score_breakdown: Dict, context: Dict) -> Dict:
        """Apply regional context without penalties - only positive adjustments"""
        
        regional_adjustments = {
            'context_applied': context.get('region_type', 'unknown'),
            'adjustments_made': [],
            'original_score': score_breakdown['total_score'],
            'adjusted_score': score_breakdown['total_score']
        }
        
        # No negative adjustments - only positive context-based bonuses
        region_type = context.get('region_type', 'developed')
        
        if region_type in self.regional_contexts:
            context_info = self.regional_contexts[region_type]
            
            # Apply positive adjustments only
            if 'innovation_weight_multiplier' in context_info:
                innovation_bonus = score_breakdown.get('quality_metrics_breakdown', {}).get(
                    'innovation_technology', {}).get('weighted_score', 0) * 0.2
                regional_adjustments['adjusted_score'] += innovation_bonus
                regional_adjustments['adjustments_made'].append(
                    f"Innovation bonus: +{innovation_bonus:.1f} points"
                )
            
            if 'accessibility_weight_multiplier' in context_info:
                accessibility_bonus = 2.0  # Bonus for serving developing regions
                regional_adjustments['adjusted_score'] += accessibility_bonus
                regional_adjustments['adjustments_made'].append(
                    f"Accessibility bonus: +{accessibility_bonus:.1f} points"
                )
        
        return regional_adjustments
    
    def _generate_international_recommendations(self, 
                                             score_breakdown: Dict, 
                                             certifications: List[Dict], 
                                             context: Dict = None) -> List[Dict]:
        """Generate international improvement recommendations"""
        
        recommendations = []
        current_score = score_breakdown['total_score']
        
        # Global certification recommendations
        if score_breakdown['international_recognition']['global_standards'] == 0:
            recommendations.append({
                'category': 'Global Certification',
                'priority': 'High',
                'recommendation': 'Pursue JCI Accreditation',
                'impact': 'High (15-25 points)',
                'timeline': '12-18 months',
                'description': 'Joint Commission International provides global recognition and significant score improvement',
                'region_applicability': 'Global'
            })
        
        # ISO certification recommendations
        iso_certs = [cert for cert in certifications if 'ISO' in cert.get('name', '').upper()]
        if len(iso_certs) < 3:
            recommendations.append({
                'category': 'International Standards',
                'priority': 'Medium',
                'recommendation': 'Implement ISO Quality Management Systems',
                'impact': 'Medium (10-20 points)',
                'timeline': '6-12 months',
                'description': 'ISO 9001, ISO 13485, and ISO 15189 provide strong international foundation',
                'region_applicability': 'Global'
            })
        
        # Regional excellence recommendations
        if context and context.get('region'):
            region = context['region']
            if region == 'North America' and not any('JOINT_COMMISSION' in str(cert) for cert in certifications):
                recommendations.append({
                    'category': 'Regional Excellence',
                    'priority': 'High',
                    'recommendation': 'Pursue Joint Commission Accreditation',
                    'impact': 'High (20-30 points)',
                    'timeline': '12-18 months',
                    'description': 'Joint Commission is the gold standard for US healthcare',
                    'region_applicability': 'North America'
                })
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize the international scorer
    scorer = InternationalHealthcareScorer()
    
    # Example: Mayo Clinic scoring
    mayo_certifications = [
        {
            'name': 'Joint Commission International',
            'status': 'Active',
            'score_impact': 30
        },
        {
            'name': 'ISO 9001:2015',
            'status': 'Active',
            'score_impact': 25
        }
    ]
    
    mayo_quality_metrics = {
        'clinical_outcomes': {'composite_score': 85},
        'patient_experience': {'composite_score': 90},
        'operational_excellence': {'composite_score': 88},
        'innovation_technology': {'composite_score': 95},
        'sustainability_social': {'composite_score': 75}
    }
    
    mayo_context = {
        'region': 'North America',
        'region_type': 'developed',
        'hospital_type': 'Academic Medical Center',
        'size': 'Large'
    }
    
    # Calculate score
    mayo_score = scorer.calculate_international_quality_score(
        mayo_certifications, 
        mayo_quality_metrics, 
        mayo_context
    )
    
    print("Mayo Clinic International Score:")
    print(f"Total Score: {mayo_score['total_score']:.1f}/100")
    print(f"Certification Score: {mayo_score['certification_score']:.1f}/60")
    print(f"Quality Metrics Score: {mayo_score['quality_metrics_score']:.1f}/40")
    print("\nCertification Breakdown:")
    for cert_type, details in mayo_score['certification_breakdown'].items():
        print(f"  {cert_type}: {details['total_score']:.1f} points ({details['description']})")