import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer
from data_validator import HealthcareDataValidator

# Initialize the analyzer
analyzer = HealthcareOrgAnalyzer()
validator = HealthcareDataValidator()

# Test Apollo Hospitals
org_name = 'Apollo Hospitals Chennai'
print(f'Testing: {org_name}')

# Check unified database
unified_result = analyzer.search_unified_database(org_name)
print(f'Unified DB result: {unified_result is not None}')
if unified_result:
    print(f'  Name: {unified_result.get("name", "N/A")}')
    print(f'  Certifications: {len(unified_result.get("certifications", []))}')
    for cert in unified_result.get("certifications", []):
        print(f'    - {cert.get("name", "N/A")}: {cert.get("status", "N/A")} (Score: {cert.get("score_impact", 0)})')

# Check validation result
validation_result = validator.validate_organization_certifications(org_name)
print(f'\nValidation result:')
print(f'  Status: {validation_result.get("validation_status", "N/A")}')
print(f'  Certifications count: {len(validation_result.get("certifications", []))}')
for cert in validation_result.get("certifications", []):
    print(f'    - {cert.get("name", "N/A")}: {cert.get("status", "N/A")} (Score: {cert.get("score_impact", 0)})')

# Check certifications specifically
certifications = analyzer.search_certifications(org_name)
print(f'\nSearch certifications count: {len(certifications)}')
for cert in certifications:
    print(f'  - {cert.get("name", "N/A")}: {cert.get("status", "N/A")} (Score: {cert.get("score_impact", 0)})')

# Test the full search process
print(f'\n--- Full Search Process ---')
results = analyzer.search_organization_info(org_name)
if results:
    print(f'Total score: {results.get("total_score", 0)}')
    print(f'Score breakdown: {results.get("score_breakdown", {})}')
else:
    print('No results found')

# Test scoring calculation directly
print(f'\n--- Direct Scoring Test ---')
certifications = analyzer.search_certifications(org_name)
initiatives = []  # Empty for now
score_data = analyzer.calculate_quality_score(certifications, initiatives, org_name)
print(f'Direct score calculation: {score_data}')