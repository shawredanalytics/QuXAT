#!/usr/bin/env python3
"""
Test script to analyze the ranking system and understand duplicate Rank 1 assignments
"""

import sys
import json
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

def test_organization_scoring(org_name):
    """Test scoring for a specific organization"""
    analyzer = HealthcareOrgAnalyzer()
    
    print(f"\n=== {org_name.upper()} ANALYSIS ===")
    
    # Search for organization in database
    org_info = analyzer.search_organization_info(org_name)
    if not org_info:
        print(f"{org_name} not found in database")
        return None
    
    print(f"Organization found: {org_info.get('name', 'Unknown')}")
    print(f"Country: {org_info.get('country', 'Unknown')}")
    print(f"Hospital Type: {org_info.get('hospital_type', 'Unknown')}")
    
    # Get certifications
    certifications = org_info.get('certifications', [])
    print(f"Number of certifications: {len(certifications)}")
    
    # Get quality initiatives
    initiatives = []
    quality_indicators = org_info.get('quality_indicators', {})
    if quality_indicators.get('jci_accredited'):
        initiatives.append({'name': 'JCI Quality Standards', 'score_impact': 5})
    if quality_indicators.get('nabh_accredited'):
        initiatives.append({'name': 'NABH Quality Standards', 'score_impact': 3})
    
    print(f"Quality initiatives: {len(initiatives)}")
    
    # Calculate score
    try:
        score_data = analyzer.calculate_quality_score(certifications, initiatives, org_name, None, [])
        print(f"Total Score: {score_data['total_score']:.2f}")
        print(f"Certification Score: {score_data['certification_score']:.2f}")
        print(f"Base Score: {score_data.get('base_score', 0):.2f}")
        
        # Print detailed score breakdown
        print(f"Score breakdown: {score_data}")
        
        # Check reputation components
        reputation_bonus = analyzer.calculate_reputation_bonus(org_name)
        reputation_multiplier = analyzer.get_reputation_multiplier(org_name)
        print(f"Reputation Bonus: {reputation_bonus}")
        print(f"Reputation Multiplier: {reputation_multiplier}")
        
        # Check if organization is in global rankings
        org_name_lower = org_name.lower().strip()
        for hospital_key, data in analyzer.global_hospital_rankings.items():
            if hospital_key in org_name_lower:
                print(f"Found in global rankings as: {hospital_key}")
                print(f"Ranking data: {data}")
                break
        else:
            print("Not found in global hospital rankings")
        
        return score_data
        
    except Exception as e:
        print(f"Error calculating score: {e}")
        return None

def test_ranking_calculation():
    """Test the ranking calculation system"""
    analyzer = HealthcareOrgAnalyzer()
    
    print("\n=== RANKING SYSTEM ANALYSIS ===")
    
    # Test with Mayo Clinic
    mayo_score_data = test_organization_scoring("Mayo Clinic")
    
    # Test with Fortis Memorial Research Institute
    fortis_score_data = test_organization_scoring("Fortis Memorial Research Institute")
    
    if mayo_score_data and fortis_score_data:
        print(f"\n=== SCORE COMPARISON ===")
        print(f"Mayo Clinic Total Score: {mayo_score_data['total_score']:.2f}")
        print(f"Fortis Memorial Total Score: {fortis_score_data['total_score']:.2f}")
        
        # Test ranking calculation for both
        print(f"\n=== RANKING CALCULATION TEST ===")
        
        # Calculate rankings for Mayo Clinic
        mayo_rankings = analyzer.calculate_organization_rankings("Mayo Clinic", mayo_score_data['total_score'])
        if mayo_rankings:
            print(f"Mayo Clinic Rank: {mayo_rankings['overall_rank']}")
            print(f"Mayo Clinic Percentile: {mayo_rankings['percentile']:.1f}%")
        
        # Calculate rankings for Fortis
        fortis_rankings = analyzer.calculate_organization_rankings("Fortis Memorial Research Institute", fortis_score_data['total_score'])
        if fortis_rankings:
            print(f"Fortis Memorial Rank: {fortis_rankings['overall_rank']}")
            print(f"Fortis Memorial Percentile: {fortis_rankings['percentile']:.1f}%")
        
        # Analyze the ranking logic issue
        print(f"\n=== RANKING LOGIC ANALYSIS ===")
        if mayo_score_data['total_score'] == fortis_score_data['total_score']:
            print("ISSUE: Both organizations have identical scores - this causes duplicate rankings")
        elif mayo_score_data['total_score'] > fortis_score_data['total_score']:
            print("Mayo Clinic should rank higher than Fortis Memorial")
        else:
            print("Fortis Memorial should rank higher than Mayo Clinic")

if __name__ == "__main__":
    test_ranking_calculation()