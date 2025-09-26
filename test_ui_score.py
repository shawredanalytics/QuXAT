import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

analyzer = HealthcareOrgAnalyzer()
result = analyzer.search_organization_info('Apollo Hospitals Chennai')

if result:
    print(f'Organization: {result["name"]}')
    print(f'Total Score: {result["total_score"]}')
    print(f'Score Breakdown: {result["score_breakdown"]}')
    print(f'Number of certifications: {len(result["certifications"])}')
    for cert in result['certifications']:
        print(f'  - {cert.get("name", "Unknown")}: {cert.get("score_impact", 0)}')
else:
    print('No result found')