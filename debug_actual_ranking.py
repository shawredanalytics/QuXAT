import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

analyzer = HealthcareOrgAnalyzer()

def debug_ranking_calculation(org_name, expected_score):
    """Debug the ranking calculation for a specific organization"""
    print(f"\n=== DEBUGGING RANKING FOR {org_name} ===")
    
    # Get all organizations from unified database
    all_orgs = []
    
    # Calculate scores for all organizations in the database
    for org in analyzer.unified_database:
        org_name_db = org['name']
        
        # Skip if it's the current organization
        if org_name_db.lower() == org_name.lower():
            continue
        
        # Get certifications from unified database
        certifications = []
        for cert in org.get('certifications', []):
            certifications.append({
                'name': cert.get('name', ''),
                'status': cert.get('status', 'Active'),
                'score_impact': cert.get('score_impact', 0)
            })
        
        # Calculate basic quality initiatives (simplified for ranking)
        initiatives = []
        if org.get('quality_indicators', {}).get('jci_accredited'):
            initiatives.append({'name': 'JCI Quality Standards', 'score_impact': 5})
        if org.get('quality_indicators', {}).get('nabh_accredited'):
            initiatives.append({'name': 'NABH Quality Standards', 'score_impact': 3})
        
        # Calculate score for this organization
        score_data = analyzer.calculate_quality_score(certifications, initiatives, org_name_db, None, [])
        
        all_orgs.append({
            'name': org_name_db,
            'total_score': score_data['total_score']
        })
    
    # Sort organizations by total score (descending)
    all_orgs.sort(key=lambda x: x['total_score'], reverse=True)
    
    print(f"Total organizations in database: {len(all_orgs)}")
    print(f"Current organization score: {expected_score}")
    
    # Show top 10 organizations
    print("\nTop 10 organizations:")
    for i, org in enumerate(all_orgs[:10]):
        print(f"  {i+1}. {org['name']}: {org['total_score']}")
    
    # Count organizations with higher scores
    organizations_with_higher_scores = 0
    organizations_with_same_score = 0
    
    for org in all_orgs:
        if org['total_score'] > expected_score:
            organizations_with_higher_scores += 1
        elif org['total_score'] == expected_score:
            organizations_with_same_score += 1
    
    print(f"\nOrganizations with higher scores: {organizations_with_higher_scores}")
    print(f"Organizations with same score: {organizations_with_same_score}")
    
    # Current ranking logic
    rank = organizations_with_higher_scores + 1
    print(f"Calculated rank: {rank}")
    
    # Show organizations with scores around the current score
    print(f"\nOrganizations with scores around {expected_score}:")
    for org in all_orgs:
        if abs(org['total_score'] - expected_score) <= 5:
            print(f"  {org['name']}: {org['total_score']}")

# Debug both organizations
debug_ranking_calculation("Apollo Hospitals Chennai", 88.75)
debug_ranking_calculation("Mayo Clinic Hospital", 74.0)