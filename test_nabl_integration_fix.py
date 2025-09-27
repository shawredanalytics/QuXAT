#!/usr/bin/env python3
"""
Test NABL Integration Fix
Verifies that NABL accreditation is now properly integrated and scored for organizations.
"""

import json
from datetime import datetime

def test_nabl_integration():
    """Test the NABL integration fix"""
    
    print("=== Testing NABL Integration Fix ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load unified database
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            organizations = json.load(f)
        
        print(f"Total organizations loaded: {len(organizations)}")
        print()
        
    except Exception as e:
        print(f"Error loading database: {e}")
        return
    
    # Test statistics
    nabl_accredited_count = 0
    nabl_active_count = 0
    total_nabl_score = 0
    
    # Test specific organizations
    test_organizations = [
        "Apex Hospitals",
        "Max Super Speciality Hospital",
        "Fortis Memorial Research Institute",
        "Manipal Hospital",
        "Delhi Heart and Lung Institute"
    ]
    
    print("1. Testing Specific Organizations:")
    print("-" * 50)
    
    for test_org in test_organizations:
        found = False
        for org in organizations:
            if not isinstance(org, dict):
                continue
                
            org_name = org.get('name', '')
            if test_org.lower() in org_name.lower():
                found = True
                print(f"Organization: {org_name}")
                print(f"City: {org.get('city', 'N/A')}")
                print(f"Data Source: {org.get('data_source', 'N/A')}")
                
                # Check certifications
                certifications = org.get('certifications', [])
                nabl_cert = None
                total_score = 0
                
                for cert in certifications:
                    if isinstance(cert, dict):
                        cert_type = cert.get('type', '')
                        score_impact = cert.get('score_impact', 0)
                        total_score += score_impact
                        
                        if 'NABL' in cert_type:
                            nabl_cert = cert
                
                print(f"Total Certifications: {len(certifications)}")
                print(f"Total Score Impact: {total_score}")
                
                if nabl_cert:
                    print(f"✓ NABL Certification Found:")
                    print(f"  - Status: {nabl_cert.get('status', 'N/A')}")
                    print(f"  - Certificate Number: {nabl_cert.get('certificate_number', 'N/A')}")
                    print(f"  - Score Impact: {nabl_cert.get('score_impact', 0)}")
                    print(f"  - Test Categories: {nabl_cert.get('test_categories', 'N/A')}")
                    print(f"  - Expiry Date: {nabl_cert.get('expiry_date', 'N/A')}")
                else:
                    print("✗ No NABL Certification Found")
                
                print()
                break
        
        if not found:
            print(f"Organization '{test_org}' not found in database")
            print()
    
    # Overall statistics
    print("2. Overall NABL Statistics:")
    print("-" * 30)
    
    for org in organizations:
        if not isinstance(org, dict):
            continue
        
        certifications = org.get('certifications', [])
        has_nabl = False
        
        for cert in certifications:
            if isinstance(cert, dict) and 'NABL' in cert.get('type', ''):
                has_nabl = True
                nabl_accredited_count += 1
                
                if cert.get('status') == 'Active':
                    nabl_active_count += 1
                
                score_impact = cert.get('score_impact', 0)
                total_nabl_score += score_impact
                break
    
    print(f"Organizations with NABL accreditation: {nabl_accredited_count}")
    print(f"Organizations with active NABL: {nabl_active_count}")
    print(f"Total NABL score impact: {total_nabl_score}")
    print(f"Average NABL score per accredited org: {total_nabl_score/nabl_accredited_count:.1f}" if nabl_accredited_count > 0 else "N/A")
    print()
    
    # Data source analysis
    print("3. Data Source Analysis:")
    print("-" * 25)
    
    data_sources = {}
    for org in organizations:
        if not isinstance(org, dict):
            continue
        
        source = org.get('data_source', 'Unknown')
        data_sources[source] = data_sources.get(source, 0) + 1
    
    for source, count in sorted(data_sources.items()):
        print(f"{source}: {count}")
    
    print()
    
    # Quality indicators check
    print("4. Quality Indicators Check:")
    print("-" * 30)
    
    nabl_quality_count = 0
    for org in organizations:
        if not isinstance(org, dict):
            continue
        
        quality_indicators = org.get('quality_indicators', {})
        if isinstance(quality_indicators, dict) and quality_indicators.get('nabl_accredited'):
            nabl_quality_count += 1
    
    print(f"Organizations with nabl_accredited=True: {nabl_quality_count}")
    print()
    
    # Test results summary
    print("=== Test Results Summary ===")
    if nabl_accredited_count > 0:
        print("✓ NABL integration successful!")
        print(f"✓ {nabl_accredited_count} organizations now have NABL accreditation")
        print(f"✓ {nabl_active_count} organizations have active NABL certificates")
        print(f"✓ Total NABL score impact: {total_nabl_score} points")
        
        if nabl_accredited_count == nabl_quality_count:
            print("✓ Quality indicators properly updated")
        else:
            print(f"⚠ Quality indicators mismatch: {nabl_quality_count} vs {nabl_accredited_count}")
    else:
        print("✗ NABL integration failed - no organizations found with NABL accreditation")
    
    print("============================")

if __name__ == "__main__":
    test_nabl_integration()