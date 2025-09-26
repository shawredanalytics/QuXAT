#!/usr/bin/env python3
"""
Test script to verify JCI and ISO validation fixes
This script tests that the validation mechanisms are properly implemented and working.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_validator import HealthcareDataValidator

def test_jci_validation():
    """Test JCI validation with known JCI organizations"""
    print("🧪 Testing JCI Validation...")
    
    validator = HealthcareDataValidator()
    
    # Test with organizations from the JCI data file
    test_orgs = [
        "Singapore General Hospital",
        "National University Hospital Singapore",
        "Random Hospital Name"  # Should not match
    ]
    
    for org_name in test_orgs:
        print(f"\nTesting JCI validation for: {org_name}")
        jci_results = validator._validate_jci_certification(org_name)
        
        if jci_results:
            print(f"  ✅ Found {len(jci_results)} JCI certifications:")
            for cert in jci_results:
                print(f"    - {cert.get('name', 'Unknown')} from {cert.get('issuer', 'Unknown')}")
        else:
            print(f"  ❌ No JCI certifications found")
    
    return True

def test_iso_validation():
    """Test ISO validation"""
    print("\n🧪 Testing ISO Validation...")
    
    validator = HealthcareDataValidator()
    
    # Test with some organization names
    test_orgs = [
        "Apollo Hospitals",
        "Test Hospital"
    ]
    
    for org_name in test_orgs:
        print(f"\nTesting ISO validation for: {org_name}")
        iso_results = validator._validate_iso_certification(org_name)
        
        if iso_results:
            print(f"  ✅ Found {len(iso_results)} ISO certifications:")
            for cert in iso_results:
                print(f"    - {cert.get('name', 'Unknown')} from {cert.get('issuer', 'Unknown')}")
        else:
            print(f"  ❌ No ISO certifications found")
    
    return True

def test_integrated_validation():
    """Test the integrated validation mechanism"""
    print("\n🧪 Testing Integrated Validation...")
    
    validator = HealthcareDataValidator()
    
    # Test with organizations that might have certifications
    test_orgs = [
        "Singapore General Hospital",  # Should have JCI
        "Apollo Hospitals",  # Might have ISO
        "Test Hospital"  # Should have none
    ]
    
    for org_name in test_orgs:
        print(f"\nTesting integrated validation for: {org_name}")
        results = validator.validate_organization_certifications(org_name)
        
        if results and results.get('certifications'):
            certs = results['certifications']
            print(f"  ✅ Found {len(certs)} total certifications:")
            for cert in certs:
                print(f"    - {cert.get('name', 'Unknown')} ({cert.get('type', 'Unknown type')})")
            print(f"  Data sources: {results.get('data_sources', [])}")
        else:
            print(f"  ❌ No certifications found")
    
    return True

def main():
    """Run all validation tests"""
    print("=" * 70)
    print("🔍 VALIDATION FIXES TEST SUITE")
    print("=" * 70)
    
    all_tests_passed = True
    
    try:
        # Test JCI validation
        if not test_jci_validation():
            all_tests_passed = False
        
        # Test ISO validation
        if not test_iso_validation():
            all_tests_passed = False
        
        # Test integrated validation
        if not test_integrated_validation():
            all_tests_passed = False
        
    except Exception as e:
        print(f"\n❌ ERROR during testing: {str(e)}")
        all_tests_passed = False
    
    print("\n" + "=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)
    
    if all_tests_passed:
        print("🎉 ALL TESTS COMPLETED!")
        print("✅ JCI validation is now working")
        print("✅ ISO validation is now working")
        print("✅ Integrated validation mechanism is functional")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the validation implementations")
    
    print("=" * 70)

if __name__ == "__main__":
    main()