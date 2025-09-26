import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

analyzer = HealthcareOrgAnalyzer()

print("=== APOLLO HOSPITALS CHENNAI ===")
apollo = analyzer.search_organization_info("Apollo Hospitals Chennai")
if apollo:
    print(f"Total Score: {apollo.get('total_score', 0)}")
    print(f"Score Breakdown: {apollo.get('score_breakdown', {})}")
    
    # Get ranking
    apollo_rank = analyzer.calculate_organization_rankings("Apollo Hospitals Chennai", apollo.get('total_score', 0))
    if apollo_rank:
        print(f"Overall Rank: {apollo_rank.get('overall_rank', 'N/A')}")
        print(f"Percentile: {apollo_rank.get('percentile', 'N/A')}")
else:
    print("Apollo Hospitals Chennai not found")

print("\n=== MAYO CLINIC HOSPITAL ===")
mayo = analyzer.search_organization_info("Mayo Clinic Hospital")
if mayo:
    print(f"Total Score: {mayo.get('total_score', 0)}")
    print(f"Score Breakdown: {mayo.get('score_breakdown', {})}")
    
    # Get ranking
    mayo_rank = analyzer.calculate_organization_rankings("Mayo Clinic Hospital", mayo.get('total_score', 0))
    if mayo_rank:
        print(f"Overall Rank: {mayo_rank.get('overall_rank', 'N/A')}")
        print(f"Percentile: {mayo_rank.get('percentile', 'N/A')}")
else:
    print("Mayo Clinic Hospital not found")

print("\n=== COMPARISON ===")
if apollo and mayo:
    apollo_score = apollo.get('total_score', 0)
    mayo_score = mayo.get('total_score', 0)
    print(f"Apollo Hospitals Chennai Score: {apollo_score}")
    print(f"Mayo Clinic Hospital Score: {mayo_score}")
    print(f"Same Score: {apollo_score == mayo_score}")
    
    # Check if both have rank 1
    apollo_rank_val = apollo_rank.get('overall_rank', 0) if apollo_rank else 0
    mayo_rank_val = mayo_rank.get('overall_rank', 0) if mayo_rank else 0
    print(f"Apollo Rank: {apollo_rank_val}")
    print(f"Mayo Rank: {mayo_rank_val}")
    print(f"Both Rank 1: {apollo_rank_val == 1 and mayo_rank_val == 1}")