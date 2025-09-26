import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

analyzer = HealthcareOrgAnalyzer()

print("=== MAYO CLINIC ===")
mayo = analyzer.search_organization_info("Mayo Clinic")
if mayo:
    print(f"Total Score: {mayo.get('total_score', 0)}")
    print(f"Score Breakdown: {mayo.get('score_breakdown', {})}")
    
    # Get ranking
    mayo_rank = analyzer.calculate_organization_rankings("Mayo Clinic", mayo.get('total_score', 0))
    if mayo_rank:
        print(f"Overall Rank: {mayo_rank.get('overall_rank', 'N/A')}")
        print(f"Percentile: {mayo_rank.get('percentile', 'N/A')}")

print("\n=== FORTIS MEMORIAL RESEARCH INSTITUTE ===")
fortis = analyzer.search_organization_info("Fortis Memorial Research Institute")
if fortis:
    print(f"Total Score: {fortis.get('total_score', 0)}")
    print(f"Score Breakdown: {fortis.get('score_breakdown', {})}")
    
    # Get ranking
    fortis_rank = analyzer.calculate_organization_rankings("Fortis Memorial Research Institute", fortis.get('total_score', 0))
    if fortis_rank:
        print(f"Overall Rank: {fortis_rank.get('overall_rank', 'N/A')}")
        print(f"Percentile: {fortis_rank.get('percentile', 'N/A')}")

print("\n=== COMPARISON ===")
if mayo and fortis:
    mayo_score = mayo.get('total_score', 0)
    fortis_score = fortis.get('total_score', 0)
    print(f"Mayo Score: {mayo_score}")
    print(f"Fortis Score: {fortis_score}")
    print(f"Same Score: {mayo_score == fortis_score}")