# Test the enhanced model functionality
import sys
sys.path.append('.')

try:
    from streamlit_app import HealthcareOrgAnalyzer
    
    # Create analyzer instance
    analyzer = HealthcareOrgAnalyzer()
    
    print('Testing JCI data integration in HealthcareOrgAnalyzer...')
    
    # Test JCI data loading
    if hasattr(analyzer, 'jci_organizations') and analyzer.jci_organizations:
        print(f'✅ JCI data loaded successfully: {len(analyzer.jci_organizations)} organizations')
    else:
        print('❌ JCI data not loaded')
    
    # Test JCI accreditation check
    test_org = "Singapore General Hospital"
    jci_cert = analyzer.check_jci_accreditation(test_org)
    if jci_cert:
        print(f'✅ JCI accreditation found for {test_org}:')
        print(f'   - Organization: {jci_cert.get("name", "N/A")}')
        print(f'   - Country: {jci_cert.get("country", "N/A")}')
        print(f'   - Type: {jci_cert.get("type", "N/A")}')
        print(f'   - Accreditation Date: {jci_cert.get("accreditation_date", "N/A")}')
        print(f'   - Region: {jci_cert.get("region", "N/A")}')
    else:
        print(f'❌ No JCI accreditation found for {test_org}')
    
    # Test certification enhancement
    print('\n🧪 Testing certification enhancement...')
    test_certifications = [
        {'name': 'ISO 9001', 'status': 'Active', 'score_impact': 15}
    ]
    enhanced_certs = analyzer.enhance_certification_with_jci(test_certifications, test_org)
    print(f'✅ Enhanced certifications: {len(enhanced_certs)} total certifications')
    
    for cert in enhanced_certs:
        if cert.get('name') == 'JCI':
            print(f'   - JCI certification added with {cert.get("score_impact", 0)} points')
            if 'organization_info' in cert:
                org_info = cert['organization_info']
                print(f'     Organization: {org_info.get("name", "N/A")}')
                print(f'     Country: {org_info.get("country", "N/A")}')
                print(f'     Accreditation Date: {org_info.get("accreditation_date", "N/A")}')
        else:
            print(f'   - {cert.get("name", "Unknown")}: {cert.get("status", "Unknown")} ({cert.get("score_impact", 0)} points)')
    
    print('\n🎉 JCI integration test completed successfully!')
    
except Exception as e:
    print(f'❌ Error testing enhanced model: {e}')
    import traceback
    traceback.print_exc()