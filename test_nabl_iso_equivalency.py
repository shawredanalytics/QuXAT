#!/usr/bin/env python3
"""
Test script to verify NABL-ISO 15189 equivalency logic in the scoring methodology.
This script tests that when a healthcare organization has NABL accreditation,
it automatically implies ISO 15189 accreditation for scoring purposes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_nabl_iso_equivalency():
    """Test the NABL-ISO 15189 equivalency logic"""
    analyzer = HealthcareOrgAnalyzer()
    
    print("🧪 Testing NABL-ISO 15189 Equivalency Logic")
    print("=" * 60)
    
    # Test Case 1: Organization with NABL but no ISO 15189
    print("\n📋 Test Case 1: Organization with NABL accreditation only")
    test_certifications_1 = [
        {
            'name': 'NABL Accreditation',
            'status': 'Active',
            'score_impact': 18,
            'description': 'National Accreditation Board for Testing and Calibration Laboratories',
            'validity': 'Valid until 2025',
            'issuer': 'NABL',
            'certificate_number': 'NABL-12345'
        }
    ]
    
    # Apply equivalency logic
    enhanced_certs_1 = analyzer._apply_nabl_iso_equivalency(test_certifications_1.copy())
    
    print(f"Original certifications: {len(test_certifications_1)}")
    print(f"Enhanced certifications: {len(enhanced_certs_1)}")
    
    # Check if ISO 15189 was added
    iso_found = False
    for cert in enhanced_certs_1:
        if 'ISO 15189' in cert.get('name', ''):
            iso_found = True
            print(f"✅ ISO 15189 automatically added: {cert['name']}")
            print(f"   Status: {cert['status']}")
            print(f"   Score Impact: {cert['score_impact']}")
            print(f"   Equivalency Note: {cert.get('equivalency_note', 'N/A')}")
            break
    
    if not iso_found:
        print("❌ ISO 15189 was NOT automatically added")
    
    # Test Case 2: Organization with both NABL and existing ISO 15189
    print("\n📋 Test Case 2: Organization with both NABL and existing ISO 15189")
    test_certifications_2 = [
        {
            'name': 'NABL Accreditation',
            'status': 'Active',
            'score_impact': 18,
            'description': 'National Accreditation Board for Testing and Calibration Laboratories',
            'validity': 'Valid until 2025',
            'issuer': 'NABL',
            'certificate_number': 'NABL-12345'
        },
        {
            'name': 'ISO 15189',
            'status': 'Active',
            'score_impact': 22,
            'description': 'Medical Laboratories Quality and Competence',
            'validity': 'Valid until 2024',
            'issuer': 'ISO',
            'certificate_number': 'ISO-67890'
        }
    ]
    
    # Apply equivalency logic
    enhanced_certs_2 = analyzer._apply_nabl_iso_equivalency(test_certifications_2.copy())
    
    print(f"Original certifications: {len(test_certifications_2)}")
    print(f"Enhanced certifications: {len(enhanced_certs_2)}")
    
    # Should not add duplicate ISO 15189
    iso_count = sum(1 for cert in enhanced_certs_2 if 'ISO 15189' in cert.get('name', ''))
    if iso_count == 1:
        print("✅ No duplicate ISO 15189 added (existing one preserved)")
    else:
        print(f"❌ Unexpected ISO 15189 count: {iso_count}")
    
    # Test Case 3: Organization without NABL
    print("\n📋 Test Case 3: Organization without NABL accreditation")
    test_certifications_3 = [
        {
            'name': 'ISO 9001',
            'status': 'Active',
            'score_impact': 25,
            'description': 'Quality Management Systems',
            'validity': 'Valid until 2025',
            'issuer': 'ISO',
            'certificate_number': 'ISO-11111'
        }
    ]
    
    # Apply equivalency logic
    enhanced_certs_3 = analyzer._apply_nabl_iso_equivalency(test_certifications_3.copy())
    
    print(f"Original certifications: {len(test_certifications_3)}")
    print(f"Enhanced certifications: {len(enhanced_certs_3)}")
    
    # Should not add ISO 15189
    iso_found_3 = any('ISO 15189' in cert.get('name', '') for cert in enhanced_certs_3)
    if not iso_found_3:
        print("✅ No ISO 15189 added (no NABL present)")
    else:
        print("❌ ISO 15189 was incorrectly added without NABL")
    
    # Test Case 4: Scoring impact test
    print("\n📋 Test Case 4: Scoring impact with NABL equivalency")
    
    # Calculate score with NABL only
    score_breakdown_1 = analyzer.calculate_quality_score(
        enhanced_certs_1, [], "Test Hospital with NABL"
    )
    
    # Calculate score without NABL
    score_breakdown_3 = analyzer.calculate_quality_score(
        enhanced_certs_3, [], "Test Hospital without NABL"
    )
    
    print(f"Score with NABL (+ implied ISO 15189): {score_breakdown_1['total_score']:.2f}")
    print(f"Score without NABL: {score_breakdown_3['total_score']:.2f}")
    print(f"Score difference: {score_breakdown_1['total_score'] - score_breakdown_3['total_score']:.2f}")
    
    # Display certification breakdown
    if 'certification_breakdown' in score_breakdown_1:
        print("\nCertification breakdown with NABL:")
        for cert_type, details in score_breakdown_1['certification_breakdown'].items():
            print(f"  {cert_type}: {details['count']} cert(s), {details['total_score']:.2f} points")
    
    print("\n" + "=" * 60)
    print("🎯 NABL-ISO 15189 Equivalency Test Complete!")
    
    return enhanced_certs_1, enhanced_certs_2, enhanced_certs_3

if __name__ == "__main__":
    test_nabl_iso_equivalency()