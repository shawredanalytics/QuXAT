#!/usr/bin/env python3
"""
Test script to verify tie-handling in the ranking system
"""

import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

def test_tie_handling():
    """Test that organizations with identical scores receive the same rank"""
    analyzer = HealthcareOrgAnalyzer()
    
    print("=== TESTING TIE HANDLING ===")
    
    # Test with organizations that should have identical scores
    test_orgs = [
        "Fortis Memorial Research Institute",
        "Max Super Speciality Hospital"
    ]
    
    scores_and_ranks = []
    
    for org_name in test_orgs:
        print(f"\n--- {org_name} ---")
        
        # Get organization info
        org_info = analyzer.search_organization_info(org_name)
        if not org_info:
            print(f"{org_name} not found")
            continue
            
        # Calculate score
        certifications = org_info.get('certifications', [])
        initiatives = []
        quality_indicators = org_info.get('quality_indicators', {})
        if quality_indicators.get('jci_accredited'):
            initiatives.append({'name': 'JCI Quality Standards', 'score_impact': 5})
        if quality_indicators.get('nabh_accredited'):
            initiatives.append({'name': 'NABH Quality Standards', 'score_impact': 3})
        
        score_data = analyzer.calculate_quality_score(certifications, initiatives, org_name, None, [])
        total_score = score_data['total_score']
        
        # Calculate ranking
        rankings = analyzer.calculate_organization_rankings(org_name, total_score)
        
        print(f"Total Score: {total_score}")
        print(f"Overall Rank: {rankings['overall_rank']}")
        print(f"Percentile: {rankings['percentile']:.2f}%")
        
        scores_and_ranks.append({
            'name': org_name,
            'score': total_score,
            'rank': rankings['overall_rank'],
            'percentile': rankings['percentile']
        })
    
    # Check for ties
    print("\n=== TIE ANALYSIS ===")
    for i, org1 in enumerate(scores_and_ranks):
        for j, org2 in enumerate(scores_and_ranks):
            if i < j:  # Avoid duplicate comparisons
                if org1['score'] == org2['score']:
                    print(f"\n🔍 IDENTICAL SCORES FOUND:")
                    print(f"{org1['name']}: Score={org1['score']}, Rank={org1['rank']}")
                    print(f"{org2['name']}: Score={org2['score']}, Rank={org2['rank']}")
                    
                    if org1['rank'] == org2['rank']:
                        print("✅ CORRECT: Same rank assigned to organizations with identical scores")
                    else:
                        print("❌ ERROR: Different ranks assigned to organizations with identical scores")
                        print(f"   Rank difference: {abs(org1['rank'] - org2['rank'])}")

if __name__ == "__main__":
    test_tie_handling()