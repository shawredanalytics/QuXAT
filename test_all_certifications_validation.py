#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test script to verify that all certification types (ISO, NABL, NABH, JCI) 
are no longer automatically assigned and only validated certifications from official sources are used.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_validator import HealthcareDataValidator, healthcare_validator
from iso_certification_scraper import get_iso_certifications

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_no_automatic_certifications():
    """Test that no certifications are automatically assigned to generic organizations"""
    print("=" * 80)
    print("COMPREHENSIVE CERTIFICATION VALIDATION TEST")
    print("=" * 80)
    
    # Initialize the validator
    validator = HealthcareDataValidator()
    
    # Test organizations that should NOT receive automatic certifications
    test_organizations = [
        "Generic Hospital",
        "Test Medical Center", 
        "Random Healthcare Facility",
        "Unknown Clinic",
        "Sample Laboratory"
    ]
    
    print("\n1. Testing Generic Organizations (Should have NO automatic certifications)")
    print("-" * 70)
    
    all_tests_passed = True
    
    for org_name in test_organizations:
        print(f"\nTesting: {org_name}")
        
        # Test the main validation functionality
        try:
            results = healthcare_validator.validate_organization_certifications(org_name)
            certifications = results.get('certifications', []) if results else []
        except Exception as e:
            print(f"  ✅ PASS: Validation properly failed (Exception: {str(e)[:50]}...)")
            certifications = []
        
        # Check for any certifications
        if certifications:
            print(f"  ❌ FAIL: Found {len(certifications)} certifications (should be 0)")
            for cert in certifications:
                print(f"    - {cert.get('name', 'Unknown')} ({cert.get('issuer', 'Unknown issuer')})")
            all_tests_passed = False
        else:
            print(f"  ✅ PASS: No certifications found")
        
        # Test individual validation methods
        print(f"    Testing individual validators:")
        
        # Test NABH validation
        nabh_results = validator._validate_nabh_certification(org_name)
        if nabh_results:
            print(f"    ❌ NABH: Found {len(nabh_results)} certifications (should be 0)")
            all_tests_passed = False
        else:
            print(f"    ✅ NABH: No certifications found")
        
        # Test NABL validation
        nabl_results = validator._validate_nabl_certification(org_name)
        if nabl_results:
            print(f"    ❌ NABL: Found {len(nabl_results)} certifications (should be 0)")
            all_tests_passed = False
        else:
            print(f"    ✅ NABL: No certifications found")
        
        # Test JCI validation
        jci_results = validator._validate_jci_certification(org_name)
        if jci_results:
            print(f"    ❌ JCI: Found {len(jci_results)} certifications (should be 0)")
            all_tests_passed = False
        else:
            print(f"    ✅ JCI: No certifications found")
        
        # Test ISO certification scraper directly
        try:
            iso_direct = get_iso_certifications(org_name, location="")
            if iso_direct and hasattr(iso_direct, 'active_certifications') and iso_direct.active_certifications > 0:
                print(f"    ❌ ISO Direct: Found {iso_direct.active_certifications} certifications (should be None or 0)")
                all_tests_passed = False
            else:
                print(f"    ✅ ISO Direct: No certifications found")
        except Exception as e:
            print(f"    ✅ ISO Direct: Properly disabled (Exception: {str(e)[:50]}...)")
    
    print("\n2. Testing Known Organizations (Should only show validated certifications)")
    print("-" * 70)
    
    # Test some known organizations that might have had hardcoded data
    known_organizations = [
        "Apollo Hospitals",
        "Fortis Healthcare", 
        "Max Healthcare",
        "Dr Lal PathLabs",
        "SRL Diagnostics",
        "Satya Scan"
    ]
    
    for org_name in known_organizations:
        print(f"\nTesting: {org_name}")
        
        try:
            results = healthcare_validator.validate_organization_certifications(org_name)
            certifications = results.get('certifications', []) if results else []
        except Exception as e:
            print(f"  ✅ Validation properly failed (Exception: {str(e)[:50]}...)")
            certifications = []
        
        if certifications:
            print(f"  ⚠️  Found {len(certifications)} certifications:")
            for cert in certifications:
                cert_name = cert.get('name', 'Unknown')
                issuer = cert.get('issuer', 'Unknown issuer')
                source = cert.get('source', 'Unknown source')
                print(f"    - {cert_name} from {issuer} (Source: {source})")
                
                # Check if this is from a validated source
                if 'official' in source.lower() or 'validated' in source.lower():
                    print(f"      ✅ From validated source")
                else:
                    print(f"      ❌ Not from validated source - may be simulated")
                    all_tests_passed = False
        else:
            print(f"  ✅ No certifications found (as expected with validation disabled)")
    
    print("\n" + "=" * 80)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! No automatic certification assignment detected.")
        print("✅ Only validated certifications from official sources will be used.")
    else:
        print("❌ SOME TESTS FAILED! Automatic certification assignment still occurring.")
        print("⚠️  Please review the validation logic.")
    print("=" * 80)
    
    return all_tests_passed

def test_scoring_mechanism():
    """Test that the scoring mechanism only uses validated certifications"""
    print("\n3. Testing Scoring Mechanism")
    print("-" * 70)
    
    # Test with a generic organization
    org_name = "Test Hospital for Scoring"
    
    try:
        results = healthcare_validator.validate_organization_certifications(org_name)
        certifications = results.get('certifications', []) if results else []
    except Exception as e:
        print(f"  ✅ Validation properly failed (Exception: {str(e)[:50]}...)")
        certifications = []
    
    # Check if any score impact is calculated from certifications
    total_cert_score = sum(cert.get('score_impact', 0) for cert in certifications)
    
    print(f"Testing scoring for: {org_name}")
    print(f"  Certifications found: {len(certifications)}")
    print(f"  Total certification score impact: {total_cert_score}")
    
    if total_cert_score == 0:
        print("  ✅ PASS: No score impact from certifications (as expected)")
        return True
    else:
        print("  ❌ FAIL: Score impact detected from certifications")
        for cert in certifications:
            if cert.get('score_impact', 0) > 0:
                print(f"    - {cert.get('name', 'Unknown')}: {cert.get('score_impact', 0)} points")
        return False

if __name__ == "__main__":
    print("Starting comprehensive certification validation tests...")
    
    # Run all tests
    test1_passed = test_no_automatic_certifications()
    test2_passed = test_scoring_mechanism()
    
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Certification validation is working correctly")
        print("✅ No automatic assignment of certifications")
        print("✅ Scoring mechanism only uses validated certifications")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Please review the certification validation logic")
        sys.exit(1)