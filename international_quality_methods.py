"""
International Quality Assessment Methods for QuXAT
Supporting methods for the international healthcare quality scoring system
"""

def _calculate_international_quality_initiatives_score(self, initiatives):
    """Calculate score for quality initiatives with international focus"""
    if not initiatives or initiatives == 'no_official_data_available':
        return 0
    
    total_score = 0
    initiative_count = 0
    
    # International quality initiative categories with global relevance
    category_weights = {
        'Patient Safety': 1.0,
        'Clinical Excellence': 0.95,
        'Quality Improvement': 0.9,
        'Patient Experience': 0.85,
        'Technology Innovation': 0.8,
        'Research & Development': 0.75,
        'Sustainability': 0.7,
        'Community Health': 0.65,
        'Staff Development': 0.6,
        'Operational Excellence': 0.55
    }
    
    # Global impact multipliers
    impact_multipliers = {
        'International': 1.2,
        'National': 1.0,
        'Regional': 0.8,
        'Local': 0.6
    }
    
    for initiative in initiatives:
        if isinstance(initiative, dict):
            category = initiative.get('category', 'Quality Improvement')
            impact = initiative.get('impact', 'National')
            status = initiative.get('status', 'Active')
            
            # Base score calculation
            base_score = 3.0
            category_weight = category_weights.get(category, 0.5)
            impact_multiplier = impact_multipliers.get(impact, 1.0)
            status_multiplier = 1.0 if status == 'Active' else 0.7
            
            initiative_score = base_score * category_weight * impact_multiplier * status_multiplier
            total_score += initiative_score
            initiative_count += 1
    
    # Apply diversity bonus for multiple initiative types
    if initiative_count > 3:
        diversity_bonus = min((initiative_count - 3) * 1.5, 8)
        total_score += diversity_bonus
    
    # Cap at 25 points to leave room for other scoring components
    return min(total_score, 25)

def _calculate_international_quality_metrics(self, org_name, branch_info=None):
    """Calculate score based on international quality metrics"""
    # Placeholder for international quality metrics
    # This would integrate with global healthcare databases and rankings
    
    metrics_score = 0
    
    # International recognition indicators
    international_indicators = [
        'world health organization',
        'global health',
        'international hospital',
        'world renowned',
        'global leader',
        'international medical center'
    ]
    
    org_name_lower = org_name.lower()
    for indicator in international_indicators:
        if indicator in org_name_lower:
            metrics_score += 2
    
    # Cap at 10 points for basic implementation
    return min(metrics_score, 10)

def _calculate_regional_adaptation_bonus(self, org_name, certifications):
    """Calculate positive regional adaptation bonus (no penalties)"""
    bonus = 0
    
    # Bonus for serving underserved regions
    underserved_indicators = [
        'rural', 'community', 'public', 'government', 
        'district', 'municipal', 'county', 'regional'
    ]
    
    org_name_lower = org_name.lower()
    for indicator in underserved_indicators:
        if indicator in org_name_lower:
            bonus += 1
    
    # Bonus for multi-regional presence
    if certifications:
        regional_certs = sum(1 for cert in certifications 
                           if any(region in cert.get('name', '').lower() 
                                 for region in ['state', 'provincial', 'national', 'federal']))
        if regional_certs > 0:
            bonus += min(regional_certs, 3)
    
    # Cap at 5 points
    return min(bonus, 5)

def generate_international_improvement_recommendations(self, score_breakdown, org_name):
    """Generate improvement recommendations based on international standards"""
    recommendations = {
        'priority_actions': [],
        'certification_opportunities': [],
        'quality_initiatives': [],
        'international_expansion': []
    }
    
    total_score = score_breakdown.get('total_score', 0)
    cert_score = score_breakdown.get('certification_score', 0)
    
    # Priority actions based on score ranges
    if total_score < 30:
        recommendations['priority_actions'].extend([
            "Pursue JCI (Joint Commission International) accreditation for global recognition",
            "Implement ISO 9001 Quality Management System as foundation",
            "Establish patient safety initiatives aligned with WHO guidelines",
            "Develop quality improvement programs with measurable outcomes"
        ])
    elif total_score < 60:
        recommendations['priority_actions'].extend([
            "Expand ISO certification portfolio (ISO 13485, 15189, 27001)",
            "Implement advanced patient experience programs",
            "Pursue regional excellence accreditation (Joint Commission, CQC, etc.)",
            "Develop international collaboration partnerships"
        ])
    else:
        recommendations['priority_actions'].extend([
            "Pursue Magnet Recognition for nursing excellence",
            "Implement Planetree patient-centered care model",
            "Establish WHO Collaborating Centre status",
            "Lead international healthcare quality initiatives"
        ])
    
    # Certification opportunities
    cert_breakdown = score_breakdown.get('certification_breakdown', {})
    
    if 'GLOBAL_GOLD' not in cert_breakdown:
        recommendations['certification_opportunities'].append({
            'certification': 'Joint Commission International (JCI)',
            'impact': '40 points',
            'description': 'Global gold standard for healthcare quality',
            'timeline': '12-18 months'
        })
    
    if 'ISO_STANDARDS' not in cert_breakdown:
        recommendations['certification_opportunities'].extend([
            {
                'certification': 'ISO 9001 Quality Management',
                'impact': '28 points',
                'description': 'Foundation for quality management systems',
                'timeline': '6-12 months'
            },
            {
                'certification': 'ISO 13485 Medical Devices',
                'impact': '30 points',
                'description': 'Quality management for medical devices',
                'timeline': '8-12 months'
            }
        ])
    
    # Quality initiatives
    recommendations['quality_initiatives'].extend([
        "Implement WHO Patient Safety Solutions",
        "Establish clinical outcome measurement programs",
        "Develop patient experience improvement initiatives",
        "Create sustainability and environmental health programs",
        "Implement technology innovation projects"
    ])
    
    # International expansion opportunities
    recommendations['international_expansion'].extend([
        "Participate in global healthcare quality networks",
        "Establish international patient referral programs",
        "Develop telemedicine capabilities for global reach",
        "Create international medical tourism programs",
        "Participate in global health research collaborations"
    ])
    
    return recommendations