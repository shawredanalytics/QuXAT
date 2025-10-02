#!/usr/bin/env python3
"""
Test script for verifying the equivalency logic between CAP, NABL, and ISO 15189 accreditations.
This test ensures that organizations with CAP or NABL accreditations receive the same scoring
benefits as those with ISO 15189 accreditation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from international_scoring_algorithm import InternationalHealthcareScorer

def test_equivalency_logic():
    """Test the equivalency logic for CAP, NABL, and ISO 15189 accreditations."""
    
    print("Testing Accreditation Equivalency Logic")
    print("=" * 50)
    
    # Test organization with ISO 15189 accreditation
    iso_org = {
        'name': 'ISO 15189 Hospital',
        'country': 'USA',
        'certifications': [
            {
                'name': 'ISO 15189 Medical Laboratory Accreditation',
                'type': 'ISO',
                'standard': '15189',
                'status': 'Active',
                'valid_until': '2025-12-31'
            }
        ]
    }
    
    # Test organization with CAP accreditation
    cap_org = {
        'name': 'CAP Accredited Hospital',
        'country': 'USA',
        'certifications': [
            {
                'name': 'College of American Pathologists Laboratory Accreditation',
                'type': 'CAP',
                'standard': 'Laboratory',
                'status': 'Active',
                'valid_until': '2025-12-31'
            }
        ]
    }
    
    # Test organization with NABL accreditation
    nabl_org = {
        'name': 'NABL Accredited Hospital',
        'country': 'India',
        'certifications': [
            {
                'name': 'National Accreditation Board for Testing and Calibration Laboratories',
                'type': 'NABL',
                'standard': 'Laboratory',
                'status': 'Active',
                'valid_until': '2025-12-31'
            }
        ]
    }
    
    # Test organization with multiple equivalent accreditations
    multi_org = {
        'name': 'Multi-Accredited Hospital',
        'country': 'USA',
        'certifications': [
            {
                'name': 'College of American Pathologists Laboratory Accreditation',
                'type': 'CAP',
                'standard': 'Laboratory',
                'status': 'Active',
                'valid_until': '2025-12-31'
            },
            {
                'name': 'ISO 15189 Medical Laboratory Accreditation',
                'type': 'ISO',
                'standard': '15189',
                'status': 'Active',
                'valid_until': '2025-12-31'
            }
        ]
    }
    
    # Test organization with no equivalent accreditations
    no_equiv_org = {
        'name': 'Non-Equivalent Hospital',
        'country': 'USA',
        'certifications': [
            {
                'name': 'ISO 9001 Quality Management',
                'type': 'ISO',
                'standard': '9001',
                'status': 'Active',
                'valid_until': '2025-12-31'
            }
        ]
    }
    
    # Initialize scoring algorithm
    scorer = InternationalHealthcareScorer()
    
    # Test each organization
    test_cases = [
        ("ISO 15189 Organization", iso_org),
        ("CAP Organization", cap_org),
        ("NABL Organization", nabl_org),
        ("Multi-Accredited Organization", multi_org),
        ("Non-Equivalent Organization", no_equiv_org)
    ]
    
    results = []
    
    for test_name, org_data in test_cases:
        print(f"\nTesting: {test_name}")
        print("-" * 30)
        
        result = scorer.calculate_international_quality_score(org_data['certifications'])
        
        print(f"Organization: {org_data['name']}")
        print(f"Total Score: {result['total_score']:.2f}")
        print(f"Certification Score: {result['certification_score']:.2f}")
        print(f"Total Penalty: {result.get('total_penalty', 0):.2f}")
        
        # Display certification details
        if 'certification_details' in result:
            print("Certification Details:")
            for cert_name, details in result['certification_details'].items():
                print(f"  - {cert_name}: Score {details.get('score', 0):.2f}")
        
        # Display mandatory compliance
        if 'mandatory_compliance' in result:
            print("Mandatory Compliance:")
            for req, status in result['mandatory_compliance'].items():
                print(f"  - {req}: {'✓' if status else '✗'}")
        
        results.append((test_name, result))
    
    # Verify equivalency
    print("\n" + "=" * 50)
    print("EQUIVALENCY VERIFICATION")
    print("=" * 50)
    
    iso_score = results[0][1]['certification_score']
    cap_score = results[1][1]['certification_score']
    nabl_score = results[2][1]['certification_score']
    
    print(f"ISO 15189 Certification Score: {iso_score:.2f}")
    print(f"CAP Certification Score: {cap_score:.2f}")
    print(f"NABL Certification Score: {nabl_score:.2f}")
    
    # Check if scores are equivalent (within tolerance)
    tolerance = 0.1
    cap_equivalent = abs(iso_score - cap_score) <= tolerance
    nabl_equivalent = abs(iso_score - nabl_score) <= tolerance
    
    print(f"\nEquivalency Check:")
    print(f"CAP ≈ ISO 15189: {'✓ PASS' if cap_equivalent else '✗ FAIL'}")
    print(f"NABL ≈ ISO 15189: {'✓ PASS' if nabl_equivalent else '✗ FAIL'}")
    
    # Check mandatory compliance equivalency
    iso_mandatory = results[0][1].get('mandatory_compliance', {})
    cap_mandatory = results[1][1].get('mandatory_compliance', {})
    nabl_mandatory = results[2][1].get('mandatory_compliance', {})
    
    print(f"\nMandatory Compliance Check:")
    print(f"ISO 15189 Group Compliance:")
    print(f"  - ISO org: {iso_mandatory.get('ISO_15189_GROUP', False)}")
    print(f"  - CAP org: {cap_mandatory.get('ISO_15189_GROUP', False)}")
    print(f"  - NABL org: {nabl_mandatory.get('ISO_15189_GROUP', False)}")
    
    # Overall test result
    overall_pass = cap_equivalent and nabl_equivalent
    print(f"\nOVERALL TEST RESULT: {'✓ PASS' if overall_pass else '✗ FAIL'}")
    
    if overall_pass:
        print("✓ Equivalency logic is working correctly!")
        print("✓ CAP and NABL accreditations are properly treated as equivalent to ISO 15189")
    else:
        print("✗ Equivalency logic needs adjustment")
        print("✗ Score differences detected between equivalent accreditations")
    
    return overall_pass

if __name__ == "__main__":
    test_equivalency_logic()