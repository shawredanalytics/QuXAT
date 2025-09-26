import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def debug_ranking():
    analyzer = HealthcareOrgAnalyzer()
    
    # Test Mayo Clinic
    print("=== MAYO CLINIC ANALYSIS ===")
    mayo_info = analyzer.search_organization_info("Mayo Clinic")
    print(f"Mayo Clinic Info: {mayo_info}")
    
    # Test Fortis Memorial Research Institute
    print("\n=== FORTIS MEMORIAL ANALYSIS ===")
    fortis_info = analyzer.search_organization_info("Fortis Memorial Research Institute")
    print(f"Fortis Info: {fortis_info}")
    
    # Compare scores
    if mayo_info and fortis_info:
        print("\n=== SCORE COMPARISON ===")
        mayo_total = mayo_info.get('total_score', 0)
        fortis_total = fortis_info.get('total_score', 0)
        
        print(f"Mayo Clinic Total Score: {mayo_total}")
        print(f"Fortis Memorial Total Score: {fortis_total}")
        print(f"Scores are identical: {mayo_total == fortis_total}")
        
        # Test ranking calculation
        print("\n=== RANKING CALCULATION TEST ===")
        mayo_rankings = analyzer.calculate_organization_rankings("Mayo Clinic", mayo_total)
        print(f"Mayo Clinic Rankings: {mayo_rankings}")
        
        fortis_rankings = analyzer.calculate_organization_rankings("Fortis Memorial Research Institute", fortis_total)
        print(f"Fortis Memorial Rankings: {fortis_rankings}")
    else:
        print("Could not retrieve organization information")

if __name__ == "__main__":
    debug_ranking()